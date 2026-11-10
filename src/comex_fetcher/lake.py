"""Convert raw COMEX Stat trade data and reference tables into the Hive lake.

Datasets in the Lake:
- ``exp``, ``imp``, ``exp-mun``, ``imp-mun``, ``exp-nbm``, ``imp-nbm``:
  Trade microdata partitioned by ``ano=<ano>`` (integer).
- ``auxiliary-tables``, ``repetro``, ``validacao``, ``ncm-vigente``:
  Unpartitioned reference tables. XLSX files become one Parquet per sheet (composite
  key ``<arquivo>__<aba>``); ZIPs become one Parquet per CSV/XLSX member.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import tempfile
import unicodedata
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    import duckdb
    import polars as pl
    from quantilica.analytics.lake import LakeError, LakeWriter
    from quantilica.core.lake import (
        DatasetDescriptor,
        composite_file_key,
        partition_types_for,
        select_current,
    )
except ImportError as exc:
    raise ImportError(
        "comex_fetcher.lake requer o extra 'analysis': "
        "uv add 'comex-fetcher[analysis]' "
        "--index https://index.quantilica.com/simple/"
    ) from exc

from comex_fetcher import __version__
from comex_fetcher.payload import SoftErrorPayloadError, check_file

if TYPE_CHECKING:
    from quantilica.core.lake import Planned

logger = logging.getLogger(__name__)

SOURCE_ID = "comex"

TRADE_DATASETS = frozenset({"exp", "imp", "exp-mun", "imp-mun", "exp-nbm", "imp-nbm"})
STATIC_DATASETS = frozenset({"auxiliary-tables", "repetro", "validacao", "ncm-vigente"})
ALL_DATASETS = sorted(TRADE_DATASETS | STATIC_DATASETS)

DATASET_ALIASES: dict[str, str] = {
    "exp": "trade_exp_ncm",
    "imp": "trade_imp_ncm",
    "exp-nbm": "trade_exp_nbm",
    "imp-nbm": "trade_imp_nbm",
    "exp-mun": "trade_exp_mun",
    "imp-mun": "trade_imp_mun",
    "auxiliary-tables": "tabelas_auxiliares_ncm_sh",
    "repetro": "repetro",
    "validacao": "totais_validacao",
    "ncm-vigente": "ncm_vigente",
}

REVERSE_ALIASES: dict[str, str] = {
    v.replace("_", "-"): k for k, v in DATASET_ALIASES.items()
}
REVERSE_ALIASES.update({v: k for k, v in DATASET_ALIASES.items()})

#: colunas de código: sempre texto (``CO_NCM`` com zero à esquerda não vira inteiro).
CODE_COLUMNS = frozenset(
    {"co_ncm", "co_nbm", "co_sh2", "co_sh4", "co_sh6", "co_urf", "co_pais", "co_mun"}
    | {"co_unid", "co_via", "co_cuci_item", "co_cgce_3", "co_isic_classe", "co_ppi"}
    | {"co_ppe", "co_fat_agreg", "co_uf", "sg_uf", "sg_uf_ncm", "sg_uf_nbm"}
    # tabelas auxiliares: o CSV lê tudo como texto, então as abas do XLSX também
    # (antes viravam inteiro e a mesma coluna mudava de tipo entre as fontes).
    | {"co_cgce_n1", "co_cgce_n2", "co_cgce_n3", "co_bloco", "co_mun_geo"}
    | {"co_cuci_sec", "co_cuci_divisao", "co_cuci_grupo", "co_cuci_sub"}
    | {"co_isic_secao", "co_isic_divisao", "co_isic_grupo", "co_siit"}
    | {"co_pais_isoa3", "co_pais_ison3", "co_ncm_secrom"}
    | {"co_exp_set", "co_exp_subset"}
)
#: dialeto fixo dos CSV do Comex: campos entre aspas duplas, aspa dentro do texto
#: escrita ``""``. Sem isso o DuckDB deduz o dialeto e, em arquivos com ``;`` ou
#: aspas no texto (``sh``), deixa as aspas literais e racha as linhas.
CSV_DIALECT: dict[str, str] = {"quote": '"', "escape": '"'}
_TABULAR_MEMBERS = (".csv", ".xlsx")

_YEAR = re.compile(r"[-_](?P<ano>(?:19|20)\d{2})(?:@|\.|$|\b)")


@dataclass
class ConvertResult:
    """Counts of a conversion run; ``errors`` holds one message per failure."""

    converted: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def resolve_dataset(path: Path) -> str | None:
    """Infer dataset id from parent directory or filename."""
    parent_name = path.parent.name.lower()
    if parent_name in ALL_DATASETS:
        return parent_name
    if parent_name in REVERSE_ALIASES:
        return REVERSE_ALIASES[parent_name]
    if path.parent.parent.name.lower() in ALL_DATASETS:
        return path.parent.parent.name.lower()
    if path.parent.parent.name.lower() in REVERSE_ALIASES:
        return REVERSE_ALIASES[path.parent.parent.name.lower()]
    for ds in ALL_DATASETS:
        if path.name.lower().startswith(ds):
            return ds
    for alias, ds in REVERSE_ALIASES.items():
        if path.name.lower().startswith(alias):
            return ds
    return None


def resolve_year(path: Path) -> int | None:
    """Extract integer 4-digit year from filename or folder."""
    match = _YEAR.search(path.name)
    if match:
        return int(match["ano"])
    if path.parent.name.isdigit() and len(path.parent.name) == 4:
        return int(path.parent.name)
    return None


def _snake(name: str) -> str:
    """Nome de coluna em snake_case ASCII (igual ao do caminho CSV/DuckDB)."""
    ascii_ = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore")
    return re.sub(r"[^a-z0-9]+", "_", ascii_.decode().lower()).strip("_")


def _retype_sheet(df: pl.DataFrame) -> pl.DataFrame:
    """Normaliza nomes e tipa uma aba lida como texto.

    Colunas de código ficam texto; as demais viram inteiro, ou decimal, só quando
    **todo** valor converte (nada de perder dado em silêncio).
    """
    df = df.rename({c: _snake(c) or f"col_{i}" for i, c in enumerate(df.columns)})
    out = []
    for col in df.columns:
        series = df[col]
        if col in CODE_COLUMNS or series.dtype != pl.String:
            out.append(series)
            continue
        for dtype in (pl.Int64, pl.Float64):
            cast = series.cast(dtype, strict=False)
            if cast.null_count() == series.null_count():
                out.append(cast)
                break
        else:
            out.append(series)
    return pl.DataFrame(out)


def _repair_quotes_line(line: str, sep: str = ";") -> str:
    """Corrige as aspas de **uma** linha de CSV, sem alterar o número de campos.

    Critério: um campo é entre aspas só se começa com ``"``; dentro dele, ``""`` é
    aspa escapada e um ``"`` só fecha o campo quando é seguido do separador ou do
    fim da linha. Qualquer outra ``"`` é texto e vira ``""``; campo que chega ao fim
    da linha sem fechar é fechado. Campo sem aspas no início fica como está.
    """
    out: list[str] = []
    i, n = 0, len(line)
    while i <= n:
        if i < n and line[i] == '"':
            out.append('"')
            i += 1
            while True:
                if i >= n:  # campo aberto até o fim da linha: fecha
                    out.append('"')
                    break
                ch = line[i]
                if ch == '"':
                    if i + 1 < n and line[i + 1] == '"':
                        out.append('""')
                        i += 2
                        continue
                    if i + 1 >= n or line[i + 1] == sep:
                        out.append('"')
                        i += 1
                        break
                    out.append('""')  # aspa no meio do texto
                    i += 1
                    continue
                out.append(ch)
                i += 1
        else:
            j = line.find(sep, i)
            j = n if j < 0 else j
            out.append(line[i:j])
            i = j
        if i < n and line[i] == sep:
            out.append(sep)
            i += 1
            if i == n:  # separador final: campo vazio
                break
            continue
        break
    return "".join(out)


def repair_csv_quotes(src: Path, dst: Path, *, encoding: str = "latin-1") -> int:
    """Copia ``src`` para ``dst`` com as aspas de cada linha reparadas.

    Uma linha física continua sendo um registro (nenhuma linha é descartada ou
    unida). Devolve quantas linhas foram alteradas.
    """
    changed = 0
    with (
        open(src, encoding=encoding, newline="") as reader,
        open(dst, "w", encoding=encoding, newline="") as writer,
    ):
        for raw in reader:
            body = raw.rstrip("\r\n")
            fixed = _repair_quotes_line(body) if '"' in body else body
            if fixed != body:
                changed += 1
            writer.write(fixed + raw[len(body) :])
    return changed


def _is_csv_error(exc: BaseException) -> bool:
    return "CSV Error" in str(exc) or "csv" in type(exc).__name__.lower()


def _write_csv(
    writer: LakeWriter,
    src: Path,
    *,
    scratch_dir: Path,
    **kwargs: Any,
) -> Any:
    """``write_duckdb`` com repetição tolerante se o CSV tiver aspas irregulares.

    A leitura normal vem primeiro. Se o DuckDB recusar o arquivo com ``CSV Error``
    (aspa que abre e nunca fecha engole as linhas seguintes), o arquivo é copiado
    com as aspas reparadas por :func:`repair_csv_quotes` e a escrita é refeita;
    chave, ``sha256`` e origem continuam os do arquivo original.
    """
    try:
        return writer.write_duckdb(src, **kwargs)
    except (duckdb.Error, LakeError) as exc:
        if not _is_csv_error(exc):
            raise
        first = _first_line(exc)
    fixed = scratch_dir / f"reparado-{src.name}"
    changed = repair_csv_quotes(src, fixed, encoding=kwargs.get("encoding", "latin-1"))
    logger.warning(
        "comex: %s: %s; reescrito com aspas reparadas em %d linha(s)",
        src.name,
        first,
        changed,
    )
    kwargs.setdefault("src_origin", src)
    return writer.write_duckdb(fixed, **kwargs)


def read_excel_sheets(path: Path) -> dict[str, pl.DataFrame]:
    """Todas as abas de um XLSX, como texto e depois tipadas por :func:`_retype_sheet`.

    Abas vazias ficam de fora.
    """
    sheets = pl.read_excel(
        path, sheet_id=0, infer_schema_length=0, raise_if_empty=False
    )
    if isinstance(sheets, pl.DataFrame):  # versões que devolvem só a 1ª aba
        sheets = {"sheet1": sheets}
    return {
        name: _retype_sheet(frame)
        for name, frame in sheets.items()
        if frame.width > 0 and frame.height > 0
    }


def read_ncm_vigente(path: Path) -> pl.DataFrame:
    """Lê o JSON de nomenclatura do Siscomex (``Nomenclaturas``) em tabela longa.

    Raises:
        ValueError: Se o JSON não tiver a lista ``Nomenclaturas``.
    """
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("Nomenclaturas") if isinstance(payload, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError("JSON do Siscomex sem 'Nomenclaturas'")
    df = pl.DataFrame(rows, infer_schema_length=None).select(
        pl.col("Codigo").cast(pl.String).alias("codigo"),
        pl.col("Codigo").cast(pl.String).str.replace_all(r"\D", "").alias("codigo_ncm"),
        pl.col("Descricao").cast(pl.String).alias("descricao"),
        pl.col("Data_Inicio")
        .cast(pl.String)
        .str.to_date("%d/%m/%Y", strict=True)
        .alias("data_inicio"),
        pl.col("Data_Fim")
        .cast(pl.String)
        .str.to_date("%d/%m/%Y", strict=True)
        .alias("data_fim"),
        pl.col("Tipo_Ato_Ini").cast(pl.String).alias("tipo_ato_ini"),
        pl.col("Numero_Ato_Ini").cast(pl.String).alias("numero_ato_ini"),
        pl.col("Ano_Ato_Ini").cast(pl.String).alias("ano_ato_ini"),
    )
    return df.with_columns(
        pl.col("codigo_ncm").str.len_chars().cast(pl.Int32).alias("nivel_digitos"),
        pl.lit(payload.get("Data_Ultima_Atualizacao_NCM")).alias("vigente_em"),
        pl.lit(payload.get("Ato")).alias("ato"),
    )


def _first_line(exc: BaseException) -> str:
    message = str(exc).strip()
    return message.splitlines()[0] if message else repr(exc)


class LakeConverter:
    """Converter registered under the ``quantilica.lake`` entry point."""

    source_id = SOURCE_ID

    def datasets(self) -> list[str]:
        """Dataset ids this converter writes to the lake."""
        return list(ALL_DATASETS)

    def convert(
        self,
        input_dir: Path,
        lake_dir: Path,
        *,
        datasets: list[str] | None = None,
        force: bool = False,
    ) -> ConvertResult:
        """Convert raw COMEX files into ``lake_dir``.

        Args:
            input_dir: Root directory containing raw files.
            lake_dir: Root of the lake.
            datasets: Optional list of dataset ids to convert; None converts all.
            force: Reconvert even if sha256 already matches in the lake.

        Returns:
            ConvertResult: Files converted, skipped, and error messages.
        """
        input_dir = Path(input_dir)
        lake_dir = Path(lake_dir)
        result = ConvertResult()
        if not input_dir.is_dir():
            result.errors.append(f"diretório '{input_dir}' não existe")
            return result

        allowed: set[str] = set()
        if datasets:
            unknown: set[str] = set()
            for d in datasets:
                resolved = REVERSE_ALIASES.get(d, d)
                if resolved in ALL_DATASETS:
                    allowed.add(resolved)
                else:
                    unknown.add(d)
            if unknown:
                for u in sorted(unknown):
                    result.errors.append(f"dataset desconhecido: {u}")
                return result
        else:
            allowed = set(ALL_DATASETS)

        candidates = sorted(
            p
            for p in input_dir.rglob("*")
            if p.is_file()
            and p.suffix.lower() in {".csv", ".xlsx", ".zip", ".json"}
            and not p.name.endswith(".manifest.json")
        )

        current = set(
            select_current(p.relative_to(input_dir).as_posix() for p in candidates)
        )
        files = []
        for path in candidates:
            if path.relative_to(input_dir).as_posix() in current:
                files.append(path)
                continue
            ds = resolve_dataset(path)
            if ds and ds in allowed:
                result.skipped += 1

        writers: dict[str, LakeWriter] = {}

        for path in files:
            dataset_id = resolve_dataset(path)
            if not dataset_id or dataset_id not in allowed:
                continue

            is_trade = dataset_id in TRADE_DATASETS
            part_keys: list[str] = ["ano"] if is_trade else []
            part_vals: dict[str, Any] = {}

            if is_trade:
                year = resolve_year(path)
                if year is None:
                    result.errors.append(
                        f"{path.name}: não foi possível inferir ano da partição"
                    )
                    continue
                part_vals["ano"] = year

            writer_key = f"{dataset_id}:" + ",".join(part_keys)
            if writer_key not in writers:
                alias = DATASET_ALIASES.get(dataset_id, dataset_id.replace("-", "_"))
                writers[writer_key] = LakeWriter(
                    lake_dir / SOURCE_ID / dataset_id,
                    DatasetDescriptor(
                        source_id=SOURCE_ID,
                        dataset_id=dataset_id,
                        alias=alias,
                        partition_keys=part_keys,
                        partition_types=partition_types_for(part_keys),
                    ),
                    force=force,
                )
            writer = writers[writer_key]

            try:
                tag = f"comex-fetcher {__version__}"
                suffix = path.suffix.lower()
                if dataset_id == "ncm-vigente":
                    check_file(path)
                    written = writer.write_polars(
                        read_ncm_vigente(path),
                        path,
                        partitions=part_vals,
                        converter=tag,
                    )
                    statuses = [written.status]
                elif suffix == ".csv":
                    check_file(path)
                    with tempfile.TemporaryDirectory(
                        dir=os.environ.get("QUANTILICA_LAKE_SCRATCH") or None
                    ) as tmp:
                        written = _write_csv(
                            writer,
                            path,
                            scratch_dir=Path(tmp),
                            partitions=part_vals,
                            separator=";",
                            encoding="latin-1",
                            converter=tag,
                            **CSV_DIALECT,
                        )
                    statuses = [written.status]
                elif suffix == ".xlsx":
                    statuses = self._write_sheets(writer, path, part_vals, tag)
                elif suffix == ".zip":
                    statuses = self._write_zip(writer, path, part_vals, tag)
                else:
                    result.errors.append(f"{path.name}: formato não suportado")
                    continue
            except (SoftErrorPayloadError, LakeError, OSError, duckdb.Error) as exc:
                result.errors.append(f"{path.name}: {_first_line(exc)}")
                continue
            except Exception as exc:  # noqa: BLE001 - erro contado por arquivo
                result.errors.append(f"{path.name}: {_first_line(exc)}")
                continue

            for status in statuses:
                if status == "skipped":
                    result.skipped += 1
                else:
                    result.converted += 1

        return result

    @staticmethod
    def _write_sheets(
        writer: LakeWriter, path: Path, part_vals: dict[str, Any], tag: str
    ) -> list[str]:
        """Uma escrita por aba, com chave composta ``<arquivo>__<aba>``."""
        sheets = read_excel_sheets(path)
        if not sheets:
            raise LakeError(f"{path.name}: planilha sem abas com dados")
        return [
            writer.write_polars(
                frame,
                path,
                partitions=part_vals,
                file_key_name=composite_file_key(path, name),
                converter=tag,
            ).status
            for name, frame in sheets.items()
        ]

    @staticmethod
    def _write_zip(
        writer: LakeWriter, path: Path, part_vals: dict[str, Any], tag: str
    ) -> list[str]:
        """Converte cada membro CSV/XLSX do ZIP, em streaming para disco.

        Chave composta ``<zip>__<membro>``; membro de outro tipo é erro contado
        (nunca ignorado em silêncio) e ZIP sem membro tabular também.
        """
        statuses: list[str] = []
        with zipfile.ZipFile(path) as zf:
            members = [i for i in zf.infolist() if not i.is_dir()]
            bad = [
                i.filename
                for i in members
                if not i.filename.lower().endswith(_TABULAR_MEMBERS)
            ]
            tabular = [i for i in members if i.filename not in bad]
            if not tabular:
                raise LakeError(f"{path.name}: ZIP sem membro CSV/XLSX")
            for info in tabular:
                key = composite_file_key(path, info.filename)
                ext = Path(info.filename).suffix.lower()
                with tempfile.TemporaryDirectory(
                    dir=os.environ.get("QUANTILICA_LAKE_SCRATCH") or None
                ) as tmp:
                    dest = Path(tmp) / f"membro{ext}"
                    with zf.open(info) as src, open(dest, "wb") as out:
                        shutil.copyfileobj(src, out, 1 << 20)
                    if ext == ".csv":
                        check_file(dest, info.filename)
                        written = _write_csv(
                            writer,
                            dest,
                            scratch_dir=Path(tmp),
                            partitions=part_vals,
                            file_key_name=key,
                            src_origin=path,
                            separator=";",
                            encoding="latin-1",
                            converter=tag,
                            **CSV_DIALECT,
                        )
                        statuses.append(written.status)
                    else:
                        for sheet, frame in read_excel_sheets(dest).items():
                            statuses.append(
                                writer.write_polars(
                                    frame,
                                    path,
                                    partitions=part_vals,
                                    file_key_name=composite_file_key(
                                        path, f"{info.filename}__{sheet}"
                                    ),
                                    converter=tag,
                                ).status
                            )
        if bad:
            raise LakeError(
                f"{path.name}: membros não tabulares ignorados: {', '.join(bad)}"
            )
        return statuses

    def inventory(self, input_dir: Path) -> list[Planned]:
        """Return planned datasets for each raw file."""
        from quantilica.core.lake import Planned

        input_dir = Path(input_dir)
        if not input_dir.is_dir():
            return []

        planned: list[Planned] = []
        for path in sorted(input_dir.rglob("*")):
            if not path.is_file() or path.name.endswith((".manifest.json", ".tmp")):
                continue
            if path.suffix.lower() not in {".csv", ".xlsx", ".zip", ".json"}:
                planned.append(Planned(path, skip_reason="nao_tabular"))
                continue
            dataset_id = resolve_dataset(path)
            if dataset_id is not None:
                planned.append(Planned(path, dataset=dataset_id))
            else:
                planned.append(Planned(path, skip_reason="nao_tabular"))
        return planned


converter = LakeConverter()

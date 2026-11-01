"""Convert raw COMEX Stat trade data and reference tables into the Hive lake.

Datasets in the Lake:
- ``exp``, ``imp``, ``exp-mun``, ``imp-mun``, ``exp-nbm``, ``imp-nbm``:
  Trade microdata partitioned by ``ano=<ano>`` (integer).
- ``auxiliary-tables``, ``repetro``, ``validacao``:
  Unpartitioned reference tables.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    import duckdb
    import polars as pl
    from quantilica.analytics.lake import LakeError, LakeWriter
    from quantilica.core.lake import (
        DatasetDescriptor,
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

if TYPE_CHECKING:
    from quantilica.core.lake import Planned

SOURCE_ID = "comex"

TRADE_DATASETS = frozenset({"exp", "imp", "exp-mun", "imp-mun", "exp-nbm", "imp-nbm"})
STATIC_DATASETS = frozenset({"auxiliary-tables", "repetro", "validacao"})
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
}

REVERSE_ALIASES: dict[str, str] = {
    v.replace("_", "-"): k for k, v in DATASET_ALIASES.items()
}
REVERSE_ALIASES.update({v: k for k, v in DATASET_ALIASES.items()})

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
            if p.is_file() and p.suffix.lower() in {".csv", ".xlsx", ".zip"}
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
                suffix = path.suffix.lower()
                if suffix == ".csv":
                    with open(path, "rb") as f:
                        head = f.read(512).lstrip(b"\xef\xbb\xbf \r\n\t")
                        is_bad = (
                            head.startswith(b"<?php")
                            or b"<!doctype html" in head.lower()
                            or b"<html" in head.lower()
                        )
                        if is_bad:
                            raise LakeError(
                                f"{path.name}: payload inválido (soft-206 PHP/HTML)"
                            )
                    written = writer.write_duckdb(
                        path,
                        partitions=part_vals,
                        separator=";",
                        encoding="latin-1",
                        converter=f"comex-fetcher {__version__}",
                    )
                elif suffix == ".xlsx":
                    df = pl.read_excel(path)
                    written = writer.write_polars(
                        df,
                        path,
                        partitions=part_vals,
                        converter=f"comex-fetcher {__version__}",
                    )
                else:
                    continue

                if written.status == "skipped":
                    result.skipped += 1
                else:
                    result.converted += 1
            except (LakeError, OSError, duckdb.Error, Exception) as exc:
                message = str(exc).strip()
                first_line = message.splitlines()[0] if message else repr(exc)
                result.errors.append(f"{path.name}: {first_line}")
                continue

        return result

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
            if path.suffix.lower() not in {".csv", ".xlsx", ".zip"}:
                planned.append(Planned(path, skip_reason="nao_tabular"))
                continue
            dataset_id = resolve_dataset(path)
            if dataset_id is not None:
                planned.append(Planned(path, dataset=dataset_id))
            else:
                planned.append(Planned(path, skip_reason="nao_tabular"))
        return planned


converter = LakeConverter()

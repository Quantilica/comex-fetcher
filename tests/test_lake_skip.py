"""O build do lake pula, sem ler o bruto, o que já está em dia."""

from __future__ import annotations

import builtins
import hashlib
import io
import json
import zipfile
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")

import polars as pl
import xlsxwriter

import comex_fetcher.lake as lake_mod
from comex_fetcher.lake import converter

FIXTURES = Path(__file__).parent / "fixtures"
_EXP_CSV = (
    "CO_ANO;CO_MES;CO_NCM;CO_UNID;CO_PAIS;SG_UF_NCM;CO_VIA;CO_URF;QT_ESTAT;"
    "KG_LIQUIDO;VL_FOB\n2023;01;01012100;10;105;SP;01;0817600;100;500;12000\n"
)


def _sidecar(path: Path) -> None:
    """Sidecar de manifesto confiável: o sha256 vem dele, sem ler o bruto."""
    data = path.read_bytes()
    path.with_name(path.name + ".manifest.json").write_text(
        json.dumps(
            {"sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data)}
        ),
        encoding="utf-8",
    )


def _xlsx(path: Path, abas: tuple[str, ...] = ("SIIT",)) -> None:
    wb = xlsxwriter.Workbook(str(path))
    for nome in abas:
        ws = wb.add_worksheet(nome)
        ws.write_row(0, 0, ["CO_SIIT", "NO_SIIT"])
        ws.write_row(1, 0, [1, "Alimentos"])
    wb.close()


def _bruto(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    for pasta in ("exp", "auxiliary-tables", "repetro", "ncm-vigente"):
        (raw / pasta).mkdir(parents=True)

    csv = raw / "exp" / "exp_2023@20240315.csv"
    csv.write_text(_EXP_CSV, encoding="latin-1")
    _sidecar(csv)

    xlsx = raw / "auxiliary-tables" / "tabelas-auxiliares@20261006.xlsx"
    _xlsx(xlsx, ("SIIT", "CGCE"))
    _sidecar(xlsx)

    z = raw / "repetro" / "repetro@20261006.zip"
    membro = tmp_path / "m.xlsx"
    _xlsx(membro)
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("a.csv", '"CO_X";"NO_X"\n"1";"um"\n')
        zf.writestr("b.csv", '"CO_X";"NO_X"\n"2";"dois"\n')
        zf.write(membro, "c.xlsx")
    _sidecar(z)

    js = raw / "ncm-vigente" / "ncm-vigente@20261104.json"
    js.write_bytes((FIXTURES / "siscomex_nomenclatura_sample.json").read_bytes())
    _sidecar(js)
    return raw


#: dataset -> (converted na 1ª rodada)
_DATASETS = {"exp": 1, "auxiliary-tables": 2, "repetro": 3, "ncm-vigente": 1}


@pytest.fixture
def acessos(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Registra todo acesso ao bruto: ZIP, leitores, ``check_file`` e ``open``."""
    vistos: list[str] = []

    def espia(nome: str, original: Any) -> Any:
        def _f(*args: Any, **kwargs: Any) -> Any:
            vistos.append(nome)
            return original(*args, **kwargs)

        return _f

    monkeypatch.setattr(zipfile, "ZipFile", espia("ZipFile", zipfile.ZipFile))
    monkeypatch.setattr(pl, "read_excel", espia("read_excel", pl.read_excel))
    for nome in ("check_file", "read_excel_sheets", "read_ncm_vigente"):
        monkeypatch.setattr(lake_mod, nome, espia(nome, getattr(lake_mod, nome)))

    original_open = builtins.open

    def aberto(file: Any, *args: Any, **kwargs: Any) -> Any:
        if "raw" in Path(str(file)).parts and not str(file).endswith(".manifest.json"):
            vistos.append(f"open:{file}")
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", aberto)
    monkeypatch.setattr(io, "open", aberto)
    return vistos


@pytest.mark.parametrize("dataset", sorted(_DATASETS))
def test_segunda_rodada_por_dataset_nao_le_o_bruto(
    tmp_path: Path, acessos: list[str], dataset: str
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    res = converter.convert(raw, lake, datasets=[dataset])
    assert not res.errors, res.errors
    assert (res.converted, res.skipped) == (_DATASETS[dataset], 0)
    assert acessos  # a primeira rodada lê o bruto

    acessos.clear()
    res2 = converter.convert(raw, lake, datasets=[dataset])
    assert (res2.converted, res2.skipped, res2.errors) == (0, _DATASETS[dataset], [])
    assert acessos == []


def test_sem_datasets_continua_convertendo_e_pulando(
    tmp_path: Path, acessos: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    total = sum(_DATASETS.values())
    res = converter.convert(raw, lake)
    assert (res.converted, res.skipped, res.errors) == (total, 0, [])
    acessos.clear()
    res2 = converter.convert(raw, lake)
    assert (res2.converted, res2.skipped, res2.errors) == (0, total, [])
    assert acessos == []


@pytest.mark.parametrize("dataset", sorted(_DATASETS))
def test_force_le_o_bruto_e_reconverte(
    tmp_path: Path, acessos: list[str], dataset: str
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=[dataset])
    acessos.clear()
    res = converter.convert(raw, lake, datasets=[dataset], force=True)
    assert (res.converted, res.skipped) == (_DATASETS[dataset], 0)
    assert acessos


def test_bruto_novo_converte_e_o_antigo_nao_e_lido(
    tmp_path: Path, acessos: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["exp"])
    novo = raw / "exp" / "exp_2024@20250115.csv"
    novo.write_text(_EXP_CSV.replace("2023", "2024"), encoding="latin-1")
    _sidecar(novo)

    acessos.clear()
    res = converter.convert(raw, lake, datasets=["exp"])
    assert (res.converted, res.skipped, res.errors) == (1, 1, [])
    assert acessos
    assert all("exp_2023" not in a for a in acessos)


def test_zip_alterado_reconverte(tmp_path: Path, acessos: list[str]) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["repetro"])
    z = raw / "repetro" / "repetro@20261006.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("a.csv", '"CO_X";"NO_X"\n"1";"um"\n"9";"nove"\n')
    _sidecar(z)

    acessos.clear()
    res = converter.convert(raw, lake, datasets=["repetro"])
    assert res.converted == 1 and res.skipped == 0
    assert "ZipFile" in acessos


def test_zip_com_membro_nao_tabular_segue_dando_erro_na_primeira_rodada(
    tmp_path: Path,
) -> None:
    """Sem Parquet nenhum o ZIP nunca conta como em dia: o erro continua aparecendo."""
    raw = tmp_path / "raw" / "repetro"
    raw.mkdir(parents=True)
    with zipfile.ZipFile(raw / "repetro@20261006.zip", "w") as zf:
        zf.writestr("leia.txt", "oi")
    for _ in range(2):
        res = converter.convert(tmp_path / "raw", tmp_path / "lake")
        assert res.converted == 0 and "sem membro CSV/XLSX" in res.errors[0]

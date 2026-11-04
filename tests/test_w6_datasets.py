"""TC-06: ZIP, XLSX multi-aba, NCM vigente do Siscomex e guarda do soft-206 no sync."""

from __future__ import annotations

import datetime as dt
import json
import zipfile
from pathlib import Path

import httpx2
import polars as pl
import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")
xlsxwriter = pytest.importorskip("xlsxwriter")

from quantilica.analytics.lake import check_dataset, scan_dataset  # noqa: E402
from quantilica.core.http import HttpClient  # noqa: E402

from comex_fetcher.catalog import list_datasets  # noqa: E402
from comex_fetcher.lake import SOURCE_ID, converter  # noqa: E402
from comex_fetcher.payload import csv_header_ok, json_header_ok  # noqa: E402
from comex_fetcher.plugin import ComexFetcherApp, path_builder  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
CSV = (
    "CO_ANO;CO_MES;CO_NCM;CO_PAIS;VL_FOB\n"
    "1994;07;01010101;105;8500\n"
    "1994;08;00010101;249;100\n"
)


def _xlsx(path: Path, sheets: dict[str, list[list[str]]]) -> None:
    wb = xlsxwriter.Workbook(path)
    for name, rows in sheets.items():
        ws = wb.add_worksheet(name)
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                ws.write_string(r, c, value)
    wb.close()


def test_xlsx_all_sheets_become_datasets(tmp_path: Path) -> None:
    raw = tmp_path / "raw" / "auxiliary-tables"
    raw.mkdir(parents=True)
    _xlsx(
        raw / "tabelas-auxiliares@20261104.xlsx",
        {
            "NCM": [["CO_NCM", "NO_NCM_POR"], ["01012100", "Cavalos"]],
            "PAIS": [["CO_PAIS", "NO_PAIS"], ["105", "Brasil"], ["249", "EUA"]],
            "Vazia": [],
        },
    )
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert (res.converted, res.errors) == (2, [])
    dataset = tmp_path / "lake" / SOURCE_ID / "auxiliary-tables"
    assert check_dataset(dataset) == []
    assert sorted(p.stem for p in dataset.glob("*.parquet")) == [
        "tabelas-auxiliares__ncm",
        "tabelas-auxiliares__pais",
    ]
    ncm = pl.read_parquet(dataset / "tabelas-auxiliares__ncm.parquet")
    assert ncm["co_ncm"][0] == "01012100"  # zero à esquerda preservado
    again = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert (again.converted, again.skipped) == (0, 2)


def test_zip_members_are_converted_not_ignored(tmp_path: Path) -> None:
    raw = tmp_path / "raw" / "exp-nbm"
    raw.mkdir(parents=True)
    with zipfile.ZipFile(raw / "exp-nbm_1994@19950201.zip", "w") as zf:
        zf.writestr("EXP_1994_NBM.csv", CSV.encode("latin-1"))
        zf.writestr("EXP_1994_NBM_B.csv", CSV.encode("latin-1"))
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert (res.converted, res.errors) == (2, [])
    dataset = tmp_path / "lake" / SOURCE_ID / "exp-nbm"
    assert check_dataset(dataset) == []
    df = scan_dataset(dataset).collect()
    assert df.height == 4 and df["ano"].unique().to_list() == [1994]
    assert df.schema["co_ncm"] == pl.String and "00010101" in df["co_ncm"].to_list()


def test_zip_without_tabular_member_is_counted_error(tmp_path: Path) -> None:
    raw = tmp_path / "raw" / "exp"
    raw.mkdir(parents=True)
    with zipfile.ZipFile(raw / "exp_2020@20210101.zip", "w") as zf:
        zf.writestr("LEIAME.pdf", b"%PDF-1.4")
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert res.converted == 0 and len(res.errors) == 1
    assert "sem membro CSV/XLSX" in res.errors[0]


def test_zip_with_php_member_is_rejected(tmp_path: Path) -> None:
    raw = tmp_path / "raw" / "exp"
    raw.mkdir(parents=True)
    with zipfile.ZipFile(raw / "exp_2020@20210101.zip", "w") as zf:
        zf.writestr("EXP_2020.csv", b"<?php\n/** Joomla CMS Error Page */\n")
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert res.converted == 0 and "soft-206" in res.errors[0]


def test_ncm_vigente_from_real_siscomex_sample(tmp_path: Path) -> None:
    raw = tmp_path / "raw" / "ncm-vigente"
    raw.mkdir(parents=True)
    (raw / "ncm-vigente@20261104.json").write_bytes(
        (FIXTURES / "siscomex_nomenclatura_sample.json").read_bytes()
    )
    (raw / "ncm-vigente@20261104.json.manifest.json").write_text("{}")
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert (res.converted, res.errors) == (1, [])
    dataset = tmp_path / "lake" / SOURCE_ID / "ncm-vigente"
    assert check_dataset(dataset) == []
    df = pl.read_parquet(next(dataset.rglob("*.parquet")))
    row = df.filter(pl.col("codigo") == "0101.21.00").row(0, named=True)
    assert row["codigo_ncm"] == "01012100" and row["nivel_digitos"] == 8
    assert row["data_inicio"] == dt.date(2022, 4, 1)
    assert row["data_fim"] == dt.date(9999, 12, 31)
    assert df["vigente_em"][0].startswith("Vigente em")
    assert df.schema["codigo_ncm"] == pl.String


def test_ncm_vigente_is_in_the_catalog(tmp_path: Path) -> None:
    entry = next(e for e in list_datasets("other") if e["id"] == "ncm-vigente")
    assert entry["url"].startswith("https://portalunico.siscomex.gov.br/")
    assert entry["ext"] == "json"
    assert path_builder(tmp_path, entry, None).parent.name == "ncm-vigente"


def test_header_guards() -> None:
    assert csv_header_ok(b'"CO_ANO";"CO_MES"\n')
    assert csv_header_ok(b"\xef\xbb\xbfCO_ANO;CO_MES\n")
    assert not csv_header_ok(b"<?php\n")
    assert not csv_header_ok(b"<!DOCTYPE html>\n")
    assert not csv_header_ok(b"Not Found\n")
    assert json_header_ok(b'{"Nomenclaturas":[]}')
    assert not json_header_ok(b"<?php")


def _app(body: bytes, status: int = 206) -> ComexFetcherApp:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            status, content=body, headers={"content-type": "text/plain"}
        )

    client = HttpClient(
        transport=httpx2.MockTransport(handler), attempts=1, retry_base_delay=0
    )
    return ComexFetcherApp(
        name="comex-fetcher",
        groups_dict={},
        aliases_dict={},
        list_datasets=list_datasets,
        path_builder=path_builder,
        client=client,
    )


PHP = b"<?php\n/** Joomla CMS Error Page */\necho 'Not Found';\n"


def test_sync_rejects_soft_206_php(tmp_path: Path) -> None:
    entry = next(e for e in list_datasets("trade-exp") if e["year"] == 2024)
    app = _app(PHP)
    with pytest.raises(Exception, match="(?i)payload|cabe|header|invál"):
        app.download_entry(entry, tmp_path)
    assert not list(tmp_path.rglob("*.csv"))


def test_sync_accepts_real_csv_header(tmp_path: Path) -> None:
    entry = next(e for e in list_datasets("trade-exp") if e["year"] == 2024)
    out = _app(CSV.encode("latin-1"), status=200).download_entry(entry, tmp_path)
    assert out.read_text(encoding="latin-1").startswith("CO_ANO;")


def test_sync_rejects_json_php_for_ncm(tmp_path: Path) -> None:
    entry = next(e for e in list_datasets("other") if e["id"] == "ncm-vigente")
    with pytest.raises(Exception, match="(?i)payload|cabe|header|invál"):
        _app(PHP).download_entry(entry, tmp_path)
    ok = _app(
        (FIXTURES / "siscomex_nomenclatura_sample.json").read_bytes(), status=200
    ).download_entry(entry, tmp_path)
    assert json.loads(ok.read_text(encoding="utf-8"))["Nomenclaturas"]


def test_lake_rows_equal_sum_of_all_sheets_and_versions_do_not_duplicate(
    tmp_path: Path,
) -> None:
    """O Lake pode ter mais linhas que a 1ª aba, mas nunca linhas duplicadas.

    A contagem do lake é a soma de **todas** as abas da versão vigente de cada
    arquivo; uma versão nova do mesmo arquivo substitui a anterior.
    """
    raw = tmp_path / "raw" / "repetro"
    raw.mkdir(parents=True)

    def rows(n: int) -> list[list[str]]:
        return [["CO_NCM", "V"]] + [[f"{i:08d}", str(i)] for i in range(n)]

    _xlsx(
        raw / "exp-repetro@20261001.xlsx",
        {"Leia-me": rows(3), "Dados": rows(300)},
    )
    _xlsx(
        raw / "exp-repetro@20261030.xlsx",  # versão mais nova do mesmo arquivo
        {"Leia-me": rows(3), "Dados": rows(300)},
    )
    _xlsx(raw / "imp-repetro@20261030.xlsx", {"Dados": rows(50)})
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert (res.converted, res.skipped, res.errors) == (3, 1, [])
    dataset = tmp_path / "lake" / SOURCE_ID / "repetro"
    assert check_dataset(dataset) == []
    assert scan_dataset(dataset).collect().height == 3 + 300 + 50

    _xlsx(
        raw / "exp-repetro@20261104.xlsx",
        {"Leia-me": rows(3), "Dados": rows(320)},
    )
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert res.errors == []
    assert scan_dataset(dataset).collect().height == 3 + 320 + 50

# Copyright (c) 2026 Komesu, D.K.
# Licensed under the MIT License.

"""Tests for the Hive lake conversion of COMEX Stat data."""

from __future__ import annotations

from importlib.metadata import entry_points
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")

from quantilica.analytics.lake import check_dataset, scan_dataset
from typer.testing import CliRunner

from comex_fetcher.lake import (
    ALL_DATASETS,
    SOURCE_ID,
    converter,
    resolve_dataset,
    resolve_year,
)
from comex_fetcher.plugin import app


def test_entry_point_registered() -> None:
    eps = entry_points(group="quantilica.lake")
    matches = [ep for ep in eps if ep.name == "comex"]
    assert len(matches) == 1
    loaded = matches[0].load()
    assert loaded is converter
    assert loaded.source_id == SOURCE_ID


def test_resolve_dataset() -> None:
    assert resolve_dataset(Path("exp/exp_2023@20240315.csv")) == "exp"
    assert resolve_dataset(Path("imp-mun/imp-mun_2020@20240315.csv")) == "imp-mun"
    assert (
        resolve_dataset(Path("auxiliary-tables/ncm@20240315.csv")) == "auxiliary-tables"
    )
    assert resolve_dataset(Path("repetro/exp-repetro@20240315.xlsx")) == "repetro"
    assert resolve_dataset(Path("unknown/file.csv")) is None


def test_resolve_year() -> None:
    assert resolve_year(Path("exp/exp_2023@20240315.csv")) == 2023
    assert resolve_year(Path("imp-nbm/imp-nbm_1994@20240315.csv")) == 1994
    assert resolve_year(Path("auxiliary-tables/ncm@20240315.csv")) is None


def test_converter_datasets() -> None:
    assert converter.datasets() == ALL_DATASETS


def test_convert_end_to_end(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    lake_dir = tmp_path / "lake"

    # 1. Trade dataset (partitioned by ano)
    exp_dir = raw_dir / "exp"
    exp_dir.mkdir(parents=True)
    exp_csv = exp_dir / "exp_2023@20240315.csv"
    exp_csv.write_text(
        "CO_ANO;CO_MES;CO_NCM;CO_UNID;CO_PAIS;SG_UF_NCM;CO_VIA;CO_URF;QT_ESTAT;KG_LIQUIDO;VL_FOB\n"
        "2023;01;01012100;10;105;SP;01;0817600;100;500;12000\n"
        "2023;02;01012100;10;105;SP;01;0817600;200;1000;24000\n",
        encoding="latin-1",
    )

    # 2. Auxiliary table (unpartitioned)
    aux_dir = raw_dir / "auxiliary-tables"
    aux_dir.mkdir(parents=True)
    aux_csv = aux_dir / "ncm@20240315.csv"
    aux_csv.write_text(
        "CO_NCM;NO_NCM_POR\n01012100;Cavalos reprodutores de raca pura\n",
        encoding="latin-1",
    )

    res = converter.convert(raw_dir, lake_dir)
    assert not res.errors, res.errors
    assert res.converted == 2
    assert res.skipped == 0

    # Verify exp dataset in lake
    exp_lake = lake_dir / SOURCE_ID / "exp"
    assert check_dataset(exp_lake) == []
    df_exp = scan_dataset(exp_lake).collect()
    assert df_exp.height == 2
    assert "ano" in df_exp.columns
    assert df_exp["ano"][0] == 2023
    assert "vl_fob" in df_exp.columns

    # Verify auxiliary table in lake
    aux_lake = lake_dir / SOURCE_ID / "auxiliary-tables"
    assert check_dataset(aux_lake) == []
    df_aux = scan_dataset(aux_lake).collect()
    assert df_aux.height == 1
    assert "co_ncm" in df_aux.columns

    # Second pass skips
    res2 = converter.convert(raw_dir, lake_dir)
    assert not res2.errors
    assert res2.converted == 0
    assert res2.skipped == 2


def test_cli_convert(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    lake_dir = tmp_path / "lake"

    exp_dir = raw_dir / "exp"
    exp_dir.mkdir(parents=True)
    exp_csv = exp_dir / "exp_2024@20240501.csv"
    exp_csv.write_text(
        "CO_ANO;CO_MES;CO_NCM;VL_FOB\n2024;05;01012100;5000\n",
        encoding="latin-1",
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["convert", "-i", str(raw_dir), "--lake", str(lake_dir), "--dataset", "exp"],
    )
    assert result.exit_code == 0
    assert (lake_dir / SOURCE_ID / "exp").exists()


def test_convert_nbm_and_code_columns(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    lake_dir = tmp_path / "lake"

    nbm_dir = raw_dir / "exp-nbm"
    nbm_dir.mkdir(parents=True)
    nbm_csv = nbm_dir / "exp-nbm_1994@19950201.csv"
    nbm_csv.write_text(
        "CO_ANO;CO_MES;CO_NBM;CO_PAIS;SG_UF_NBM;VL_FOB\n1994;07;01010101;105;SP;8500\n",
        encoding="latin-1",
    )

    res = converter.convert(raw_dir, lake_dir, datasets=["exp-nbm"])
    assert not res.errors, res.errors
    assert res.converted == 1

    nbm_lake = lake_dir / SOURCE_ID / "exp-nbm"
    assert check_dataset(nbm_lake) == []
    df = scan_dataset(nbm_lake).collect()
    assert df.height == 1
    assert df["ano"][0] == 1994
    assert df["co_nbm"][0] == "01010101"


def test_reject_soft_206_php(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    lake_dir = tmp_path / "lake"

    exp_dir = raw_dir / "exp"
    exp_dir.mkdir(parents=True)
    bad_csv = exp_dir / "exp_1999@20200101.csv"
    bad_csv.write_text(
        "<?php\n/** Joomla CMS Error Page */\necho 'Not Found';\n",
        encoding="latin-1",
    )

    res = converter.convert(raw_dir, lake_dir, datasets=["exp"])
    assert len(res.errors) == 1
    assert "soft-206" in res.errors[0]
    assert res.converted == 0


def test_convert_canonical_alias(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    lake_dir = tmp_path / "lake"

    exp_dir = raw_dir / "exp"
    exp_dir.mkdir(parents=True)
    exp_csv = exp_dir / "exp_2022@20230101.csv"
    exp_csv.write_text(
        "CO_ANO;CO_MES;CO_NCM;VL_FOB\n2022;03;01012100;1000\n",
        encoding="latin-1",
    )

    res = converter.convert(raw_dir, lake_dir, datasets=["trade_exp_ncm"])
    assert not res.errors, res.errors
    assert res.converted == 1


def test_convert_unknown_dataset_comex(tmp_path: Path) -> None:
    res = converter.convert(tmp_path, tmp_path, datasets=["nao_existe_xyz"])
    assert len(res.errors) == 1
    assert "dataset desconhecido: nao_existe_xyz" in res.errors[0]


def test_inventory_comex(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    exp_dir = raw_dir / "exp"
    exp_dir.mkdir()
    (exp_dir / "exp_2023@20240101.csv").write_text("a;b\n")
    (raw_dir / "doc.pdf").write_text("dummy")

    planned = converter.inventory(raw_dir)
    assert len(planned) == 2
    datasets = {p.path.name: (p.dataset, p.skip_reason) for p in planned}
    assert datasets["exp_2023@20240101.csv"] == ("exp", None)
    assert datasets["doc.pdf"] == (None, "nao_tabular")


_NCM_HEAD = '"CO_NCM";"CO_UNID";"NO_NCM_POR"\n'
_NCM_GOOD = "".join(f'"{i:08d}";"10";"Desc {i}"\n' for i in range(3000))


def test_csv_with_unclosed_quote_keeps_every_line(tmp_path: Path) -> None:
    """Aspa que abre e não fecha (ncm@20261006.csv) não pode derrubar o arquivo."""
    aux = tmp_path / "raw" / "auxiliary-tables"
    aux.mkdir(parents=True)
    bad = (
        _NCM_HEAD
        + _NCM_GOOD
        + '"99999999";"10";"Cavalo\n'  # aspa aberta, nunca fechada
        + '"99999998";"10";"Cavalo "puro" sangue"\n'  # aspas no meio do texto
        + '"99999997";"10";"Tubo de 5" de diametro"\n'
        + '"99999996";"10";"Normal"\n'
    )
    (aux / "ncm@20261006.csv").write_bytes(bad.encode("latin-1"))
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert (res.converted, res.errors) == (1, [])
    dataset = tmp_path / "lake" / SOURCE_ID / "auxiliary-tables"
    assert check_dataset(dataset) == []
    df = scan_dataset(dataset).collect()
    assert df.height == 3004  # nenhuma linha perdida nem unida
    by_code = dict(zip(df["co_ncm"], df["no_ncm_por"], strict=True))
    assert by_code["99999999"] == "Cavalo"
    assert by_code["99999998"] == 'Cavalo "puro" sangue'
    assert by_code["99999997"] == 'Tubo de 5" de diametro'
    assert by_code["99999996"] == "Normal"


def test_repair_csv_quotes_line() -> None:
    from comex_fetcher.lake import _repair_quotes_line as fix

    assert fix('"a";"b"') == '"a";"b"'
    assert fix('"a";"b') == '"a";"b"'
    assert fix('"a";"x"y"z";"c"') == '"a";"x""y""z";"c"'
    assert fix('"a";"q""r";"c"') == '"a";"q""r";"c"'
    assert fix('1;"a;b";') == '1;"a;b";'
    assert fix('x"y;z') == 'x"y;z'

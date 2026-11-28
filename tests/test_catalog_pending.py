"""Ano corrente do catálogo e a marca ``pending_publication`` (virada de ano)."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import httpx2
from quantilica.cli.sdk import EXIT_SYNC_PARTIAL
from quantilica.core.http import HttpClient
from typer.testing import CliRunner

from comex_fetcher.catalog import (
    GROUP_ALIASES,
    GROUPS,
    PENDING_GRACE_DAYS,
    list_datasets,
)
from comex_fetcher.plugin import ComexFetcherApp, path_builder

runner = CliRunner(env={"COLUMNS": "200"})

NEW_YEAR = dt.date(2027, 1, 1)
PHP = b"<?php\n/** Joomla CMS Error Page */\necho 'Not Found';\n"
CSV = b"CO_ANO;CO_MES;VL_FOB\n2026;1;10\n"


def _pending(today: dt.date) -> list[tuple[str, int]]:
    return [
        (e["group"], e["year"])
        for e in list_datasets(today=today)
        if e.get("pending_publication")
    ]


def test_o_ano_e_calculado_na_listagem_nao_na_importacao() -> None:
    last = {
        today: max(e["year"] for e in list_datasets("trade-exp", today=today))
        for today in (dt.date(2026, 12, 31), NEW_YEAR)
    }
    assert last == {dt.date(2026, 12, 31): 2026, NEW_YEAR: 2027}
    exp_2027 = [
        e for e in list_datasets("trade-exp", today=NEW_YEAR) if e["year"] == 2027
    ]
    assert exp_2027[0]["url"].endswith("EXP_2027.csv")


def test_so_o_ano_corrente_do_comercio_ncm_e_municipal_leva_a_marca() -> None:
    assert sorted(_pending(NEW_YEAR)) == [
        ("trade-exp", 2027),
        ("trade-exp-mun", 2027),
        ("trade-imp", 2027),
        ("trade-imp-mun", 2027),
    ]
    # tabelas e NBM (série histórica fechada) nunca
    marked = {
        e["group"] for e in list_datasets(today=NEW_YEAR) if "pending_publication" in e
    }
    assert not marked & {"auxiliary", "repetro", "validation", "other"}
    assert not marked & {"trade-exp-nbm", "trade-imp-nbm"}


def test_a_marca_acaba_depois_da_folga() -> None:
    last = NEW_YEAR + dt.timedelta(days=PENDING_GRACE_DAYS)
    assert len(_pending(last)) == 4
    assert _pending(last + dt.timedelta(days=1)) == []
    assert _pending(dt.date(2026, 11, 28)) == []


def test_agrupamentos_e_grupo_invalido_seguem_iguais() -> None:
    trade = list_datasets("trade", today=NEW_YEAR)
    assert {e["group"] for e in trade} == set(GROUP_ALIASES["trade"])
    assert len(list_datasets(today=NEW_YEAR)) == len(trade) + len(
        list_datasets("tables", today=NEW_YEAR)
    )
    try:
        list_datasets("nao-existe")
    except ValueError as exc:
        assert "nao-existe" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("esperava ValueError")


# ---------------------------------------------------- host: sync de ponta a ponta


def _app(today: dt.date, mode: str) -> ComexFetcherApp:
    """``mode``: ``"404"`` ou ``"php"`` (soft-206) para o ano 2027; 2026 existe."""

    def handler(request: httpx2.Request) -> httpx2.Response:
        if "2027" in str(request.url):
            if mode == "404":
                return httpx2.Response(404)
            return httpx2.Response(
                206, content=PHP, headers={"content-type": "text/plain"}
            )
        return httpx2.Response(200, content=CSV)

    def listing(group: str) -> list[dict[str, Any]]:
        return [e for e in list_datasets(group, today=today) if e["year"] >= 2026]

    return ComexFetcherApp(
        name="comex-fetcher",
        groups_dict={"trade-exp": GROUPS["trade-exp"]},
        aliases_dict={},
        list_datasets=listing,
        path_builder=path_builder,
        client=HttpClient(
            transport=httpx2.MockTransport(handler), attempts=1, retry_base_delay=0
        ),
    )


def _sync(app: ComexFetcherApp, tmp_path: Path) -> tuple[int, dict[str, Any]]:
    out = tmp_path / "r.json"
    result = runner.invoke(
        app.app,
        ["sync", "trade-exp", "-o", str(tmp_path / "raw"), "--summary-json", str(out)],
    )
    return result.exit_code, json.loads(out.read_text())


def test_soft_206_de_entrada_pendente_vira_ainda_nao_publicado(tmp_path: Path) -> None:
    code, data = _sync(_app(NEW_YEAR, "php"), tmp_path)
    assert code == 0, data
    assert data["errors"] == []
    assert data["skipped_items"] == [
        {"id": "exp-2027", "reason": "pending-publication"}
    ]
    assert data["total"] == 2 and data["skipped"] == 1 and data["failed"] == 0


def test_404_de_entrada_pendente_tambem_e_perdoado(tmp_path: Path) -> None:
    code, data = _sync(_app(NEW_YEAR, "404"), tmp_path)
    assert code == 0, data
    assert [i["id"] for i in data["skipped_items"]] == ["exp-2027"]


def test_passada_a_folga_o_soft_206_volta_a_ser_erro_do_arquivo(tmp_path: Path) -> None:
    late = NEW_YEAR + dt.timedelta(days=PENDING_GRACE_DAYS + 1)
    code, data = _sync(_app(late, "php"), tmp_path)
    assert code == EXIT_SYNC_PARTIAL
    assert [e["id"] for e in data["errors"]] == ["exp-2027"]
    assert "soft-206" in data["errors"][0]["message"]
    assert data["skipped_items"] == []


def test_soft_206_de_ano_fechado_nunca_e_perdoado(tmp_path: Path) -> None:
    """Sem a marca (ano 2026 em 2027-01-01 não é pendente), segue erro como hoje."""

    def handler(request: httpx2.Request) -> httpx2.Response:
        if "2026" in str(request.url):
            return httpx2.Response(206, content=PHP)
        return httpx2.Response(200, content=CSV)

    app = _app(NEW_YEAR, "php")
    app.client = HttpClient(
        transport=httpx2.MockTransport(handler), attempts=1, retry_base_delay=0
    )
    code, data = _sync(app, tmp_path)
    assert code == EXIT_SYNC_PARTIAL
    assert [e["id"] for e in data["errors"]] == ["exp-2026"]


def test_looks_like_php_so_aceita_php() -> None:
    from comex_fetcher.payload import looks_like_error_page, looks_like_php

    assert looks_like_php(b"<?php\n/** Joomla */")
    assert looks_like_php(b"\xef\xbb\xbf  <?PHP echo 1;")
    for other in (b"<?xml version='1.0'?>", b"<?", b"<!DOCTYPE html>", b"<html>"):
        assert not looks_like_php(other), other
    # a guarda de cabeçalho segue barrando todas essas aberturas
    assert looks_like_error_page(b"<?xml version='1.0'?>")


def test_pagina_xhtml_de_manutencao_nao_vira_ainda_nao_publicado(
    tmp_path: Path,
) -> None:
    """``<?xml`` em entrada pendente segue erro do arquivo (não prova que sumiu)."""
    xhtml = b"<?xml version='1.0'?>\n<html><body>Em manutencao</body></html>\n"

    def handler(request: httpx2.Request) -> httpx2.Response:
        if "2027" in str(request.url):
            return httpx2.Response(206, content=xhtml)
        return httpx2.Response(200, content=CSV)

    app = _app(NEW_YEAR, "php")
    app.client = HttpClient(
        transport=httpx2.MockTransport(handler), attempts=1, retry_base_delay=0
    )
    code, data = _sync(app, tmp_path)
    assert code == EXIT_SYNC_PARTIAL
    assert [e["id"] for e in data["errors"]] == ["exp-2027"]
    assert data["skipped_items"] == []
    assert "soft-206" not in data["errors"][0]["message"]

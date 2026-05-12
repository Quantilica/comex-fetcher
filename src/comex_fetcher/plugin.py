# Copyright (c) 2026 Komesu, D.K.
# Licensed under the MIT License.

"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from comex_fetcher import download_all, get_complete, get_table, get_year, get_year_nbm
from comex_fetcher.constants import AUX_TABLES

app = typer.Typer(help="Dados de comércio exterior (SECEX/COMEX).")

_DEFAULT_OUTPUT = Path("/data/secex-comex")
console = Console()


def _expand_years(years: list[str]) -> list[int]:
    result = []
    for arg in years:
        if ":" in arg:
            try:
                start, end = map(int, arg.split(":"))
                step = 1 if start <= end else -1
                result.extend(range(start, end + step, step))
            except ValueError:
                console.print(f"[yellow]Aviso:[/yellow] intervalo inválido '{arg}'")
        else:
            try:
                result.append(int(arg))
            except ValueError:
                console.print(f"[yellow]Aviso:[/yellow] ano inválido '{arg}'")
    return result


@app.command("trade")
def trade(
    years: Annotated[
        list[str],
        typer.Argument(help="Anos (ex: 2020), intervalos (2018:2020) ou 'complete'"),
    ],
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de saída")
    ] = _DEFAULT_OUTPUT,
    exports: Annotated[
        bool, typer.Option("-exp/-no-exp", "--exports/--no-exports", help="Apenas exportações")
    ] = False,
    imports: Annotated[
        bool, typer.Option("-imp/-no-imp", "--imports/--no-imports", help="Apenas importações")
    ] = False,
    municipality: Annotated[
        bool, typer.Option("-mun/-no-mun", "--municipality/--no-municipality", help="Dados municipais (1997+)")
    ] = False,
) -> None:
    """Baixar dados de transações comerciais (NCM/NBM)."""
    exp = imp = True
    if exports or imports:
        exp, imp = exports, imports

    if years == ["complete"]:
        get_complete(data_dir=output, exp=exp, imp=imp, mun=municipality, show_progress=True)
        return

    for year in _expand_years(years):
        if year < 1989:
            console.print(f"[yellow]Pulando {year}:[/yellow] dados não disponíveis antes de 1989.")
            continue
        if year < 1997:
            get_year_nbm(data_dir=output, year=year, exp=exp, imp=imp, show_progress=True)
        else:
            get_year(data_dir=output, year=year, exp=exp, imp=imp, mun=municipality, show_progress=True)


@app.command("table")
def table(
    tables: Annotated[
        Optional[list[str]],
        typer.Argument(help="Nomes das tabelas ou 'all'. Omitir para listar disponíveis."),
    ] = None,
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de saída")
    ] = _DEFAULT_OUTPUT,
) -> None:
    """Baixar tabelas auxiliares de códigos."""
    if not tables:
        t = Table(title="Tabelas auxiliares disponíveis", show_header=True)
        t.add_column("Nome", style="cyan")
        for name in AUX_TABLES:
            t.add_row(name)
        console.print(t)
        return

    to_download = list(AUX_TABLES.keys()) if "all" in tables else [t for t in tables if t in AUX_TABLES]
    for t in tables:
        if t not in AUX_TABLES and t != "all":
            console.print(f"[yellow]Aviso:[/yellow] tabela '{t}' não encontrada.")

    for t in to_download:
        get_table(data_dir=output, table=t, show_progress=True)


@app.command("all")
def all_datasets(
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de saída")
    ] = _DEFAULT_OUTPUT,
    yes: Annotated[
        bool, typer.Option("-y", "--yes", help="Confirmar sem prompt")
    ] = False,
) -> None:
    """Baixar TUDO (todos os anos, todas as tabelas)."""
    if not yes:
        typer.confirm(
            "Isso pode demorar muito e usar vários GBs. Continuar?",
            abort=True,
        )
    download_all(data_dir=output, show_progress=True)

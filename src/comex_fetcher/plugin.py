"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from comex_fetcher import (
    download_all,
    get_table,
    get_year,
    get_year_nbm,
)
from comex_fetcher.constants import AUX_TABLES

app = typer.Typer(help="Dados de comércio exterior (SECEX/COMEX).")
console = Console()

_DEFAULT_OUTPUT = Path("/data/secex-comex")


def _setup_logging(verbose: bool) -> None:
    """Configura logging via RichHandler para não quebrar barras de progresso.

    verbose=False → WARNING apenas; verbose=True → DEBUG via Rich console.
    """
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, show_path=False)],
        force=True,
    )


def _make_progress() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    )


def _expand_years(years: list[str]) -> list[int]:
    result = []
    for arg in years:
        if ":" in arg:
            try:
                start, end = map(int, arg.split(":"))
                step = 1 if start <= end else -1
                result.extend(range(start, end + step, step))
            except ValueError:
                console.print(
                    f"[yellow]Aviso:[/yellow] intervalo inválido '{arg}'"
                )
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
        typer.Argument(
            help="Anos (ex: 2020) ou intervalos (2018:2020)"
        ),
    ],
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de saída")
    ] = _DEFAULT_OUTPUT,
    exports: Annotated[
        bool,
        typer.Option(
            "-exp/-no-exp",
            "--exports/--no-exports",
            help="Apenas exportações",
        ),
    ] = False,
    imports: Annotated[
        bool,
        typer.Option(
            "-imp/-no-imp",
            "--imports/--no-imports",
            help="Apenas importações",
        ),
    ] = False,
    municipality: Annotated[
        bool,
        typer.Option(
            "-mun/-no-mun",
            "--municipality/--no-municipality",
            help="Dados municipais (1997+)",
        ),
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", help="Logs detalhados")
    ] = False,
) -> None:
    """Baixar dados de transações comerciais (NCM/NBM)."""
    _setup_logging(verbose)
    exp = imp = True
    if exports or imports:
        exp, imp = exports, imports

    years_list = _expand_years(years)
    if not years_list:
        console.print("[yellow]Nenhum ano válido informado.[/yellow]")
        raise typer.Exit(code=1)

    with _make_progress() as progress:
        task = progress.add_task(
            "[cyan]Iniciando...[/cyan]", total=len(years_list)
        )
        ok = skipped = 0
        for year in years_list:
            if year < 1989:
                console.print(
                    f"[yellow]Pulando {year}:[/yellow]"
                    " dados não disponíveis antes de 1989."
                )
                skipped += 1
                progress.update(
                    task,
                    advance=1,
                    description=f"[dim]{skipped} pulado(s)[/dim]",
                )
                continue
            progress.update(task, description=f"[cyan]{year}[/cyan]")
            if year < 1997:
                get_year_nbm(
                    data_dir=output,
                    year=year,
                    exp=exp,
                    imp=imp,
                    show_progress=False,
                )
            else:
                get_year(
                    data_dir=output,
                    year=year,
                    exp=exp,
                    imp=imp,
                    mun=municipality,
                    show_progress=False,
                )
            ok += 1
            progress.update(
                task,
                advance=1,
                description=(
                    f"[green]{ok}✓[/green]  [dim]{skipped} skip[/dim]"
                ),
            )

    console.print(
        f"[green]✓[/green] [bold]{ok}[/bold]"
        f" ano(s) baixados em [dim]{output}[/dim]"
    )


@app.command("table")
def table_cmd(
    tables: Annotated[
        list[str] | None,
        typer.Argument(help="Nomes das tabelas ou 'all'. Omitir para listar."),
    ] = None,
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de saída")
    ] = _DEFAULT_OUTPUT,
    verbose: Annotated[
        bool, typer.Option("--verbose", help="Logs detalhados")
    ] = False,
) -> None:
    """Baixar tabelas auxiliares de códigos."""
    _setup_logging(verbose)
    if not tables:
        rich_table = Table(
            title="Tabelas auxiliares disponíveis", show_header=True
        )
        rich_table.add_column("Nome", style="cyan")
        for name in AUX_TABLES:
            rich_table.add_row(name)
        console.print(rich_table)
        return

    to_download = (
        list(AUX_TABLES.keys())
        if "all" in tables
        else [t for t in tables if t in AUX_TABLES]
    )
    for name in tables:
        if name not in AUX_TABLES and name != "all":
            console.print(
                f"[yellow]Aviso:[/yellow] tabela '{name}' não encontrada."
            )

    if not to_download:
        console.print("[yellow]Nenhuma tabela válida informada.[/yellow]")
        return

    with _make_progress() as progress:
        task = progress.add_task(
            "[cyan]Baixando tabelas...[/cyan]", total=len(to_download)
        )
        for name in to_download:
            progress.update(task, description=f"[cyan]{name}[/cyan]")
            get_table(data_dir=output, table=name, show_progress=False)
            progress.update(task, advance=1)

    n = len(to_download)
    console.print(
        f"[green]✓[/green] [bold]{n}[/bold]"
        f" tabela(s) baixadas em [dim]{output}[/dim]"
    )


@app.command("all")
def all_datasets(
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de saída")
    ] = _DEFAULT_OUTPUT,
    yes: Annotated[
        bool, typer.Option("-y", "--yes", help="Confirmar sem prompt")
    ] = False,
    verbose: Annotated[
        bool, typer.Option("--verbose", help="Logs detalhados")
    ] = False,
) -> None:
    """Baixar TUDO (todos os anos, todas as tabelas)."""
    _setup_logging(verbose)
    if not yes:
        typer.confirm(
            "Isso pode demorar muito e usar vários GBs. Continuar?",
            abort=True,
        )

    with _make_progress() as progress:
        task = progress.add_task("[cyan]Baixando tudo...[/cyan]", total=None)

        def on_progress(done: int, total: int) -> None:
            progress.update(
                task,
                completed=done,
                total=total,
                description=(f"[cyan]Baixando[/cyan]  [green]{done}✓[/green]"),
            )

        download_all(
            data_dir=output,
            show_progress=False,
            on_progress=on_progress,
        )

    console.print(
        f"[green]✓[/green] Todos os datasets baixados em [dim]{output}[/dim]"
    )

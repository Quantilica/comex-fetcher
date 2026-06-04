"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Annotated

import typer
from quantilica.core.cli import (
    expand_years_cli,
    get_console,
    make_batch_progress,
    make_download_progress,
    setup_rich_logging,
)
from quantilica.core.http import ProgressCallback
from rich.console import Group
from rich.live import Live
from rich.progress import Progress, TaskID
from rich.table import Table

from comex_fetcher import (
    get_table,
    get_year,
    get_year_nbm,
)
from comex_fetcher.constants import AUX_TABLES

app = typer.Typer(help="Dados de comércio exterior (SECEX/COMEX).")
console = get_console()

_DEFAULT_OUTPUT = Path("/data/secex-comex")
_MIN_YEAR = 1989


def _file_callback(
    file_progress: Progress,
    task_id: TaskID,
    description: str,
) -> ProgressCallback:
    """Return a ProgressCallback that feeds into a Rich file progress task."""

    def callback(downloaded: int, total_bytes: int) -> None:
        # (0, 0) fires at the start of each download attempt (incl. retries)
        if downloaded == 0 and total_bytes == 0:
            file_progress.reset(task_id)
            file_progress.update(task_id, description=description, visible=True)
            return
        if total_bytes:
            file_progress.update(task_id, total=total_bytes)
        file_progress.update(task_id, completed=downloaded)

    return callback


@app.command("sync")
def sync(
    years: Annotated[
        list[str] | None,
        typer.Argument(
            help=(
                "Anos (ex: 2020) ou intervalos (2018:2020)."
                f" Padrão: todos desde {_MIN_YEAR}."
            ),
        ),
    ] = None,
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de saída")
    ] = _DEFAULT_OUTPUT,
    exports: Annotated[
        bool,
        typer.Option("--exports/--no-exports", help="Apenas exportações"),
    ] = False,
    imports: Annotated[
        bool,
        typer.Option("--imports/--no-imports", help="Apenas importações"),
    ] = False,
    municipality: Annotated[
        bool,
        typer.Option(
            "--municipality/--no-municipality",
            help="Dados municipais (1997+)",
        ),
    ] = False,
    no_tables: Annotated[
        bool,
        typer.Option("--no-tables", help="Não baixar as tabelas auxiliares de códigos"),
    ] = False,
    tables_only: Annotated[
        bool,
        typer.Option("--tables-only", help="Baixar apenas as tabelas auxiliares"),
    ] = False,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Listar sem baixar")
    ] = False,
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Sincronizar dados de comércio exterior (transações + tabelas)."""
    setup_rich_logging(verbose, console=console)
    exp = imp = True
    if exports or imports:
        exp, imp = exports, imports

    current_year = dt.datetime.now().year
    if years:
        years_list = [
            y for y in expand_years_cli(years, console=console) if y >= _MIN_YEAR
        ]
    else:
        years_list = list(range(_MIN_YEAR, current_year + 1))

    if not tables_only and not years_list:
        console.print("[yellow]Nenhum ano válido informado.[/yellow]")
        raise typer.Exit(code=1)

    do_trade = not tables_only
    do_tables = not no_tables
    table_names = list(AUX_TABLES.keys())

    if dry_run:
        t = Table(show_header=True, header_style="bold")
        t.add_column("Tipo", style="cyan")
        t.add_column("Item")
        if do_trade:
            for year in years_list:
                t.add_row("transações", str(year))
        if do_tables:
            for name in table_names:
                t.add_row("tabela", name)
        console.print(t)
        n = (len(years_list) if do_trade else 0) + (
            len(table_names) if do_tables else 0
        )
        console.print(f"[bold]Total:[/bold] {n} item(ns)")
        return

    try:
        total = (len(years_list) if do_trade else 0) + (
            len(table_names) if do_tables else 0
        )
        overall = make_batch_progress(console)
        file_prog = make_download_progress(console)
        overall_task = overall.add_task("[cyan]Iniciando...[/cyan]", total=total)
        file_task = file_prog.add_task("", total=None, visible=False)

        ok = 0
        with Live(Group(overall, file_prog), console=console, refresh_per_second=10):
            if do_trade:
                for year in years_list:
                    overall.update(overall_task, description=f"[cyan]{year}[/cyan]")
                    cb = _file_callback(file_prog, file_task, str(year))
                    if year < 1997:
                        get_year_nbm(
                            data_dir=output,
                            year=year,
                            exp=exp,
                            imp=imp,
                            progress=cb,
                        )
                    else:
                        get_year(
                            data_dir=output,
                            year=year,
                            exp=exp,
                            imp=imp,
                            mun=municipality,
                            progress=cb,
                        )
                    file_prog.update(file_task, visible=False)
                    ok += 1
                    overall.update(
                        overall_task,
                        advance=1,
                        description=f"[green]{ok}✓[/green]",
                    )

            if do_tables:
                for name in table_names:
                    overall.update(overall_task, description=f"[cyan]{name}[/cyan]")
                    cb = _file_callback(file_prog, file_task, name)
                    get_table(data_dir=output, table=name, progress=cb)
                    file_prog.update(file_task, visible=False)
                    ok += 1
                    overall.update(
                        overall_task,
                        advance=1,
                        description=f"[green]{ok}✓[/green]",
                    )

        console.print(
            f"[green]✓[/green] [bold]{ok}[/bold]"
            f" item(ns) sincronizados em [dim]{output}[/dim]"
        )
    except KeyboardInterrupt:
        console.print("[yellow]Download cancelado pelo usuário.[/yellow]")
        raise typer.Exit(code=130)


@app.command("list")
def list_cmd(
    verbose: Annotated[bool, typer.Option("--verbose", help="Logs detalhados")] = False,
) -> None:
    """Listar as tabelas auxiliares de códigos disponíveis."""
    setup_rich_logging(verbose, console=console)
    rich_table = Table(title="Tabelas auxiliares disponíveis", show_header=True)
    rich_table.add_column("Nome", style="cyan")
    for name in AUX_TABLES:
        rich_table.add_row(name)
    console.print(rich_table)

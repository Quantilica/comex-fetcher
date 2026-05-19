#!/usr/bin/env python3

"""Command-line interface for downloading Brazil's foreign trade data.

This tool provides access to trade transaction data and auxiliary code tables
from Brazil's Ministry of Economy (SECEX/COMEX).
"""

import argparse
import logging
import sys
from pathlib import Path

from quantilica_core.logging import configure_cli_logging

from comex_fetcher import (
    __version__,
    download_all,
    get_table,
    get_year,
    get_year_nbm,
    logger,
)
from comex_fetcher.constants import AUX_TABLES, TABLES


def expand_years(args_years: list[str]) -> list[int]:
    """Expand year arguments into a list of individual years."""
    years = []
    for arg in args_years:
        if ":" in arg:
            try:
                start, end = map(int, arg.split(":"))
                step = 1 if start <= end else -1
                years.extend(range(start, end + step, step))
            except ValueError:
                print(f"Error: Invalid year range '{arg}'")
                continue
        else:
            try:
                years.append(int(arg))
            except ValueError:
                print(f"Error: Invalid year '{arg}'")
                continue
    return years


def handle_trade(args: argparse.Namespace):
    """Handle the 'trade' subcommand."""
    show_progress = not args.verbose
    if not args.exp and not args.imp:
        exp = imp = True
    else:
        exp, imp = args.exp, args.imp

    years = expand_years(args.years)
    for year in years:
        if year < 1989:
            logger.warning(
                f"Skipping year {year}: Data not available before 1989."
            )
            continue

        if year < 1997:
            if args.mun:
                logger.warning(
                    f"Note: Municipality data not available for {year}. Downloading national data."
                )
            get_year_nbm(
                data_dir=args.output,
                year=year,
                exp=exp,
                imp=imp,
                show_progress=show_progress,
            )
        else:
            get_year(
                data_dir=args.output,
                year=year,
                exp=exp,
                imp=imp,
                mun=args.mun,
                show_progress=show_progress,
            )


def handle_table(args: argparse.Namespace):
    """Handle the 'table' subcommand."""
    if not args.tables:
        print_code_tables()
        return

    tables_to_download = []
    if "all" in args.tables:
        tables_to_download = list(AUX_TABLES.keys())
    else:
        for t in args.tables:
            if t in AUX_TABLES:
                tables_to_download.append(t)
            else:
                logger.warning(
                    f"Table '{t}' not found. Use 'comex-fetcher table' without arguments to see available tables."
                )

    if not tables_to_download:
        return

    logger.info(
        f"Downloading {len(tables_to_download)} tables to {args.output}..."
    )
    for table in tables_to_download:
        try:
            get_table(
                data_dir=args.output,
                table=table,
                show_progress=not args.verbose,
            )
        except Exception as e:
            logger.error(f"Error downloading table '{table}': {e}")


def handle_all(args: argparse.Namespace):
    """Handle the 'all' subcommand."""
    logger.info(
        f"Downloading ALL available datasets to {args.output}. This may take a long time and use several GBs of space."
    )
    confirm = (
        input("Continue? [y/N]: ") if not getattr(args, "yes", False) else "y"
    )
    if confirm.lower() == "y":
        download_all(data_dir=args.output, show_progress=not args.verbose)
    else:
        print("Aborted.")


def print_code_tables():
    """Print available auxiliary code tables."""
    print("\nAvailable code tables:")
    for table, info in TABLES.items():
        print(f"\n  {table: <11} {info['name']}")
        desc = info["description"]
        # Simple word wrap
        words = desc.split()
        line = " " * 13
        for word in words:
            if len(line) + len(word) > 80:
                print(line)
                line = " " * 13 + word
            else:
                line += " " + word
        print(line)
    print()


def get_parser() -> argparse.ArgumentParser:
    """Create and configure the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="comex-fetcher",
        description="Download Brazil's foreign trade data (SECEX/COMEX).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Exibir logs detalhados em vez de barra de progresso",
    )
    parser.set_defaults(func=lambda _: parser.print_help())

    subparsers = parser.add_subparsers(title="commands", dest="command")

    # Trade command
    trade_parser = subparsers.add_parser(
        "trade", help="Download trade transaction data (NCM/NBM)"
    )
    trade_parser.add_argument(
        "years",
        nargs="+",
        help="Years (e.g. 2020) or ranges (2018:2020)",
    )
    trade_parser.add_argument(
        "-exp", "--exports", action="store_true", help="Download exports only"
    )
    trade_parser.add_argument(
        "-imp", "--imports", action="store_true", help="Download imports only"
    )
    trade_parser.add_argument(
        "-mun",
        "--municipality",
        action="store_true",
        help="Download municipality-level data (1997+)",
    )
    trade_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("/data/secex-comex"),
        help="Output directory",
    )
    trade_parser.set_defaults(func=handle_trade)

    # Table command
    table_parser = subparsers.add_parser(
        "table", help="Download auxiliary code tables"
    )
    table_parser.add_argument(
        "tables",
        nargs="*",
        help="Table names or 'all'. Leave empty to list available tables.",
    )
    table_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("/data/secex-comex"),
        help="Output directory",
    )
    table_parser.set_defaults(func=handle_table)

    # All command
    all_parser = subparsers.add_parser(
        "all", help="Download EVERYTHING (all years, all tables, all datasets)"
    )
    all_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("/data/secex-comex"),
        help="Output directory",
    )
    all_parser.add_argument(
        "-y", "--yes", action="store_true", help="Skip confirmation prompt"
    )
    all_parser.set_defaults(func=handle_all)

    return parser


def main():
    """Main entry point."""
    parser = get_parser()
    args = parser.parse_args()
    configure_cli_logging(verbose=args.verbose)
    if not args.verbose:
        logging.getLogger().setLevel(logging.WARNING)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

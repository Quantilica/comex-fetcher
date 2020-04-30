#!/usr/bin/env python3


import argparse
import os

from . import download


def expand_years(args_years):
    years = []
    for arg in args_years:
        if ":" in arg:
            start, end = arg.split(":")
            start, end = int(start), int(end)
            if start > end:
                years += list(range(start, end-1, -1))
            else:
                years += list(range(start, end+1))
        else:
            years.append(int(arg))
    return years


# ==============================================================================
# ----------------------------TRANSACTION TRADE DATA----------------------------
# ==============================================================================
def download_trade(args):
    for y in expand_years(args.years):
        if args.mun:
            download.exp_mun(y, args.o)
            download.imp_mun(y, args.o)
        elif args.nbm:
            download.exp_nbm(y, args.o)
            download.imp_nbm(y, args.o)
        else:
            download.exp(y, args.o)
            download.imp(y, args.o)


# ==============================================================================
# ----------------------------AUXILIARY CODE TABLES-----------------------------
# ==============================================================================
def download_code(args):
    if "all" in args.tables:
        for table in download.CODE_TABLES:
            download.code(table, args.o)
    else:
        for table in args.tables:
            download.code(table, args.o)


def download_ncm(args):
    if "all" in args.tables:
        for table in download.NCM_TABLES:
            download.ncm(table, args.o)
    else:
        for table in args.tables:
            download.ncm(table, args.o)


def download_nbm(args):
    if "all" in args.tables:
        for table in download.NBM_TABLES:
            download.nbm(table, args.o)
    else:
        for table in args.tables:
            download.nbm(table, args.o)


# ==============================================================================
# ------------------------------------PARSERS-----------------------------------
# ==============================================================================
def set_download_trader_subparser(download_subs, default_output):
    # !!! DOWNLOAD TRADE TRANSACTIONS DATA
    download_trade_parser = download_subs.add_parser(
        "trade", description="Download Exports & Imports data")
    download_trade_parser.add_argument(
        "years",
        action="store",
        nargs="+",
        help="Year (or year range) or list of years (year ranges) to download",
    )
    download_trade_parser.add_argument("-mun", action="store_true")
    download_trade_parser.add_argument("-nbm", action="store_true")
    download_trade_parser.add_argument(
        "-o",
        action="store",
        default=default_output,
        help="Output path directory where files will be saved",
    )
    download_trade_parser.set_defaults(func=download_trade)


def set_download_code_subparser(download_subs, default_output):
    # !!! DOWNLOAD CODE TABLES
    download_code_parser = download_subs.add_parser(
        "code", description="Download code tables for Brazil's foreign data")
    download_code_parser.add_argument(
        "tables",
        action="store",
        nargs="+",
        help="Name (or list of names) of table to download ('all' to download all tables)",
    )
    download_code_parser.add_argument(
        "-o",
        action="store",
        default=default_output,
        help="Output path directory where files will be saved",
    )
    download_code_parser.set_defaults(func=download_code)


def set_download_ncm(download_subs, default_output):
    # !!! DOWNLOAD NCM TABLES
    download_ncm_parser = download_subs.add_parser(
        "ncm", description="Download NCM tables for Brazil's foreign trade data")
    download_ncm_parser.add_argument(
        "tables",
        action="store",
        nargs="+",
        help="Name (or list of names) of table to download ('all' to download all tables)",
    )
    download_ncm_parser.add_argument(
        "-o",
        action="store",
        default=default_output,
        help="Output path directory where files will be saved",
    )
    download_ncm_parser.set_defaults(func=download_ncm)


def set_download_nbm(download_subs, default_output):
    # !!! DOWNLOAD NBM TABLES
    download_nbm_parser = download_subs.add_parser(
        "nbm", description="Download NBM tables for Brazil's foreign trade data")
    download_nbm_parser.add_argument(
        "tables",
        action="store",
        nargs="+",
        help="Name (or list of names) of table to download ('all' to download all tables)",
    )
    download_nbm_parser.add_argument(
        "-o",
        action="store",
        default=default_output,
        help="Output path directory where files will be saved",
    )
    download_nbm_parser.set_defaults(func=download_nbm)


def set_parser():
    default_output = os.path.join(".", "DATA", "MDIC")

    parser = argparse.ArgumentParser(
        description="Easy access to Brazil's foreign trade data")
    command_subparsers = parser.add_subparsers(dest="command", required=True)

    # * DOWNLOAD DATA
    download_subparser = command_subparsers.add_parser(
        "download", description="Download Brazil's foreign trade data")
    download_subs = download_subparser.add_subparsers()

    set_download_trader_subparser(download_subs, default_output)
    set_download_code_subparser(download_subs, default_output)
    set_download_ncm(download_subs, default_output)
    set_download_nbm(download_subs, default_output)

    return parser


def main():
    parser = set_parser()
    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as ki:
        print(f"\n\n{ki}\n\n")
        print("\n\n\nEXITING...\n\n\n")

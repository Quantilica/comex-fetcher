import argparse
import datetime
import os

import download


def download_bc(args):
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
            download.code(table, args.o)
    else:
        for table in args.tables:
            download.nbm(table, args.o)


def set_parser():
    parser = argparse.ArgumentParser(description="Manage MDIC data.")
    command_subparsers = parser.add_subparsers(dest="command", required=True)

    # * DOWNLOAD MDIC DATA
    download_subparser = command_subparsers.add_parser(
        "download", description="Download MDIC data.")
    download_subs = download_subparser.add_subparsers()

    # DOWNLOAD BC DATA
    download_bc_parser = download_subs.add_parser(
        "bc", description="Export & Import data.")
    # years : list or range of years to download data
    download_bc_parser.add_argument("years", action="store", nargs="+")
    # -mun : download municipalities data
    download_bc_parser.add_argument("-mun", action="store_true")
    download_bc_parser.add_argument("-nbm", action="store_true")
    # -o : output path
    download_bc_parser.add_argument(
        "-o", action="store", default=os.path.join("\\", "DATA", "MDIC"))
    download_bc_parser.set_defaults(func=download_bc)

    # DOWNLOAD CODE DATA
    download_code_parser = download_subs.add_parser(
        "code", description="Code data.")
    download_code_parser.add_argument("tables", action="store", nargs="+")
    download_code_parser.add_argument(
        "-o", action="store", default=os.path.join("\\", "DATA", "MDIC"))
    download_code_parser.set_defaults(func=download_code)

    # DOWNLOAD NCM DATA
    download_ncm_parser = download_subs.add_parser(
        "ncm", description="NCM data.")
    download_ncm_parser.add_argument("tables", action="store", nargs="+")
    download_ncm_parser.add_argument(
        "-o", action="store", default=os.path.join("\\", "DATA", "MDIC"))
    download_ncm_parser.set_defaults(func=download_ncm)

    # DOWNLOAD NBM DATA
    download_nbm_parser = download_subs.add_parser(
        "nbm", description="NBM data.")
    download_nbm_parser.add_argument("tables", action="store", nargs="+")
    download_nbm_parser.add_argument(
        "-o", action="store", default=os.path.join("\\", "DATA", "MDIC"))
    download_nbm_parser.set_defaults(func=download_nbm)

    return parser


def expand_years(args):
    years = []
    for arg in args:
        if ":" in arg:
            start, end = arg.split(":")
            start, end = int(start), int(end)
            years += list(range(start, end + 1))
        else:
            years.append(int(arg))

    return years


def main():
    parser = set_parser()
    args = parser.parse_args()

    args.func(args)


if __name__ == '__main__':
    main()

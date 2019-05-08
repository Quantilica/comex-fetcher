import argparse
import os

from . import download


def download_bc(args):
    for y in expand_years(args.years):
        if args.mun:
            download.exp_mun(y, args.o)
            download.imp_mun(y, args.o)
        else:
            download.exp(y, args.o)
            download.imp(y, args.o)


def download_code(args):
    for table in args.tables:
        download.code(table, args.o)


def download_ncm(args):
    for table in args.tables:
        download.ncm(table, args.o)


def set_parser():
    parser = argparse.ArgumentParser(description="Download MDIC data.")

    subparsers = parser.add_subparsers()

    # * DOWNLOAD BC DATA
    parser_bc = subparsers.add_parser("bc", description="Export & Import data.")
    # years : list or range of years to download data
    parser_bc.add_argument("years", action="store", nargs="+")
    # -mun : download municipalities data
    parser_bc.add_argument("-mun", action="store_true")
    # -o : output path
    parser_bc.add_argument(
        "-o", action="store", default=os.path.join("\\", "DATA", "MDIC"))
    parser_bc.set_defaults(func=download_bc)

    # * DOWNLOAD CODE DATA
    parser_code = subparsers.add_parser("code", description="Code data.")
    parser_code.add_argument("tables", action="store", nargs="+")
    parser_code.add_argument(
        "-o", action="store", default=os.path.join("\\", "DATA", "MDIC"))
    parser_code.set_defaults(func=download_code)

    # * DOWNLOAD NCM DATA
    parser_ncm = subparsers.add_parser("ncm", description="NCM data.")
    parser_ncm.add_argument("tables", action="store", nargs="+")
    parser_ncm.add_argument(
        "-o", action="store", default=os.path.join("\\", "DATA", "MDIC"))
    parser_code.set_defaults(func=download_ncm)

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

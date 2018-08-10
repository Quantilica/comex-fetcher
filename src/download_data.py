import argparse
import os

import download


def set_parser():
    parser = argparse.ArgumentParser()
    # years : list or range of years to download data
    parser.add_argument("years", action="store", nargs="+")
    # -mun : download municipalities data
    parser.add_argument("-mun", action="store_true")
    # -o : output path
    parser.add_argument(
        "-o", action="store_true", default=os.path.join("\\", "DATA", "MDIC"))

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
    years = expand_years(args.years)

    output = args.o

    for y in years:
        if args.mun:
            download.exp_mun(y, output)
            download.imp_mun(y, output)
        else:
            download.exp(y, output)
            download.imp(y, output)


if __name__ == '__main__':
    main()

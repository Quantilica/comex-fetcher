import argparse
import datetime
import os
import pandas as pd

import bc
import ncm
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


def expand_codes(list_codes: list, ncm_data):
    codes = []
    for arg in list_codes:
        if ":" in arg:
            start, end = arg.split(":")
            codes += list(ncm.range_codes(ncm_data, start, end))
        else:
            codes.append(arg)

    return codes


def get_data(years, codes, path):
    files = [os.path.join(path, f) for f in os.listdir(path)]
    files = [f for f in files if os.path.isfile(f)]
    files = [f for f in files for y in years if str(y) in f]
    data = bc.open_files(files)
    data = data.loc[data["Date"].dt.year.isin(years)]
    data = data.loc[data["CO_NCM"].isin(codes), :]

    return data


def save_data(data, path):
    if path.lower().endswith(".xlsx"):
        data.to_excel(path, index=False)
    elif path.lower().endswith(".csv"):
        data.to_csv(path, sep=";", decimal=",", index=False)
    elif path.lower().endswith(".h5"):
        data.to_hdf(path, key="data")


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


    # * EXPORT MDIC DATA
    export_parser = command_subparsers.add_parser(
        "export", description="Export MDIC data.")
    # -ncm : list of codes or range of codes
    export_parser.add_argument("-ncm", action="store", nargs="+", required=True)
    # -t : year period
    export_parser.add_argument("-t", action="store", nargs="+")
    # -s : balance side (x for exports and m for imports)
    export_parser.add_argument("-s", action="store", choices=["x", "m"])
    # -i : input path/filename
    export_parser.add_argument(
        "-i", action="store", default=os.path.join("\\", "DATA", "MDIC"))
    # -o : output path/filename
    export_parser.add_argument("-o", action="store", default="data.csv")
    export_parser.set_defaults(func=export)

    return parser


def export(args):
    PATH_EXP = os.path.join(args.i, "exp")
    PATH_IMP = os.path.join(args.i, "imp")
    NCM = ncm.open_file(os.path.join(args.i, "ncm", "NCM.csv"))

    years = expand_years(args.t)
    if years is None:
        years = [datetime.datetime.today().year]

    codes = expand_codes(args.ncm, NCM)

    if args.s is None:
        x = get_data(years, codes, PATH_EXP)
        x = x.assign(BALACE_SIDE="EXPORT")
        m = get_data(years, codes, PATH_IMP)
        m = m.assign(BALACE_SIDE="IMPORT")
        data = pd.concat([x, m], axis=0, ignore_index=True)
    elif args.s == "x":
        x = get_data(years, codes, PATH_EXP)
        data = x.assign(BALACE_SIDE="EXPORT")
    elif args.s == "m":
        m = get_data(years, codes, PATH_IMP)
        data = m.assign(BALACE_SIDE="IMPORT")

    if len(data) > 0:
        save_data(data, args.o)
    else:
        print("No data for this query!")
    print("DONE!")


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

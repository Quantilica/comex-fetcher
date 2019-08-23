import argparse
import datetime
import os
import pandas as pd

from . import bc
from . import ncm


def set_parser():
    parser = argparse.ArgumentParser()
    # -ncm : list of codes or range of codes
    parser.add_argument("-ncm", action="store", nargs="+", required=True)
    # -t : year period
    parser.add_argument("-t", action="store", nargs="+")
    # -s : balance side (x for exports and m for imports)
    parser.add_argument("-s", action="store", choices=["x", "m"])
    # -i : input path/filename
    parser.add_argument(
        "-i", action="store", default=os.path.join("\\", "DATA", "MDIC"))
    # -o : output path/filename
    parser.add_argument("-o", action="store", default="data.xlsx")

    return parser


def expand_years(list_years: list):
    years = []
    for arg in list_years:
        if ":" in arg:
            start, end = arg.split(":")
            start, end = int(start), int(end)
            years += list(range(start, end + 1))
        else:
            years.append(int(arg))

    return years


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


def main():
    parser = set_parser()
    args = parser.parse_args()

    PATH_DATA = args.i
    PATH_EXP = os.path.join(PATH_DATA, "exp")
    PATH_IMP = os.path.join(PATH_DATA, "imp")
    NCM = ncm.open_file(os.path.join(PATH_DATA, "ncm", "NCM.csv"))

    years = expand_years(args.t)
    if years is None:
        years = [datetime.datetime.today().year]

    codes = expand_codes(args.ncm, NCM)

    output_path = args.o

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
        save_data(data, output_path)
    else:
        print("No data for this query!")

    print("DONE!")


if __name__ == '__main__':
    main()

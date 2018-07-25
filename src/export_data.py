import argparse
import os

import bc
import ncm


PATH_DATA = os.path.join("..", "DATA")
PATH_EXP = os.path.join(PATH_DATA, "exp")
PATH_IMP = os.path.join(PATH_DATA, "imp")
PATH_NCM = os.path.join(PATH_DATA, "ncm", "NCM.csv")
NCM = ncm.open_file(PATH_NCM)


def set_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ncm", action="store", nargs="+", required=True)
    parser.add_argument("-t", action="store", nargs="+")
    parser.add_argument("-s", action="store", choices=["x", "m"])

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


def expand_codes(list_codes: list):
    codes = []
    for arg in list_codes:
        if ":" in arg:
            start, end = arg.split(":")
            codes += list(ncm.range_codes(NCM, start, end))
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

    years = expand_years(args.t)
    codes = expand_codes(args.ncm)

    if args.s is None:
        x = get_data(years, codes, PATH_EXP)
        save_data(x, "x.xlsx")
        m = get_data(years, codes, PATH_IMP)
        save_data(m, "m.xlsx")
    elif args.s == "x":
        x = get_data(years, codes, PATH_EXP)
        save_data(x, "x.xlsx")
    elif args.s == "m":
        m = get_data(years, codes, PATH_IMP)
        save_data(m, "m.xlsx")

    print("DONE!")


if __name__ == '__main__':
    main()

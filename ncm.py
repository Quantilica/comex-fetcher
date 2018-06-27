import pandas as pd
import os


DATA_DIR = "DATA"


def open_ncm_file(filename):
    d = pd.read_csv(
        filename,
        sep=";",
        decimal=",",
        header=0,
        encoding="latin1",
        dtype=str
    )

    return d


def merge_ncm(ncm, path_folder):
    files = [f for f in os.listdir(path_folder) if f.startswith("NCM_")]
    for f in files:
        d = open_ncm_file(os.path.join(path_folder, f))
        ncm = pd.merge(ncm, d, how="left")

    return ncm


def main():
    ncm = open_ncm_file(os.path.join(DATA_DIR, "NCM.csv"))
    ncm = merge_ncm(ncm, "DATA")
    ncm = ncm[[c for c in ncm
               if (not c.endswith("_ESP")) and (not c.endswith("_ING"))
               ]]
    ncm_out = os.path.join(DATA_DIR, "ncm_complete.xlsx")
    print("Salvando arquivo:", ncm_out)
    ncm.to_excel(ncm_out, index=False)


if __name__ == '__main__':
    main()

import pandas as pd
import numpy as np
import zipfile
import os


DATA_DIR = os.path.join("..", "DATA")


def open_historical_data(filename):
    print("Abrindo arquivo:", filename)
    with zipfile.ZipFile(filename) as zf:
        with zf.open(zf.namelist()[0]) as zfc:
            d = pd.read_csv(
                zfc, sep=";", decimal=",", header=0, encoding="latin1",
                dtype={
                    "CO_NCM": str,
                    "CO_UNID": str,
                    "CO_SH6": str,
                    "CO_PAIS": str,
                    "CO_UF": str,
                    "CO_PORTO": str,
                    "CO_VIA": str,
                    "CO_ANO": str,
                    "CO_MES": str,
                    "QT_ESTAT": np.float64,
                    "KG_LIQUIDO": np.float64,
                    "VL_FOB": np.float64,
                }
            )

    return d


def groupby_year_ncm(path_exp, path_imp):
    exp = open_historical_data(path_exp)
    exp = exp.loc[:, ["CO_NCM", "CO_ANO", "CO_PAIS",
                      "QT_ESTAT", "KG_LIQUIDO", "VL_FOB"]]
    exp = exp.groupby(["CO_NCM", "CO_ANO", "CO_PAIS"]).sum()
    exp.columns = ["QT_ESTAT_EXP", "KG_LIQUIDO_EXP", "VL_FOB_EXP"]

    imp = open_historical_data(path_imp)
    imp = imp.loc[:, ["CO_NCM", "CO_ANO", "CO_PAIS",
                      "QT_ESTAT", "KG_LIQUIDO", "VL_FOB"]]
    imp = imp.groupby(["CO_NCM", "CO_ANO", "CO_PAIS"]).sum()
    imp.columns = ["QT_ESTAT_IMP", "KG_LIQUIDO_IMP", "VL_FOB_IMP"]

    agrupado = pd.merge(
        right=exp,
        left=imp,
        left_index=True,
        right_index=True,
        how="outer"
    )
    agrupado["NX"] = agrupado["VL_FOB_EXP"].sub(
        agrupado["VL_FOB_IMP"], fill_value=0)
    del exp, imp
    agrupado = agrupado[["QT_ESTAT_EXP", "QT_ESTAT_IMP",
                         "KG_LIQUIDO_EXP", "KG_LIQUIDO_IMP",
                         "VL_FOB_EXP", "VL_FOB_IMP",
                         "NX"]].reset_index()

    return agrupado


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
    path_exp = os.path.join(DATA_DIR, "ncm", "EXP_COMPLETA.zip")
    path_imp = os.path.join(DATA_DIR, "ncm", "IMP_COMPLETA.zip")
    path_out = os.path.join(DATA_DIR, "serie_historica_bc.csv")
    agrupado = groupby_year_ncm(path_exp, path_imp)

    print("Salvando arquivo:", path_out)
    agrupado.to_csv(path_out, index=False, encoding="utf-8")

    ncm = open_ncm_file(os.path.join(DATA_DIR, "ncm", "NCM.csv"))
    ncm = merge_ncm(ncm, "DATA")
    ncm = ncm[[c for c in ncm
               if (not c.endswith("_ESP")) and (not c.endswith("_ING"))
               ]]
    ncm_out = os.path.join(DATA_DIR, "ncm", "ncm_complete.csv")
    print("Salvando arquivo:", ncm_out)
    ncm.to_csv(ncm_out, index=False, encoding="utf-8")


if __name__ == '__main__':
    main()

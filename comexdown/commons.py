import pandas as pd
import numpy as np
import os
import zipfile


def open_ncm_file(filename):
    d = pd.read_csv(
        filename,
        sep=";",
        decimal=",",
        header=0,
        encoding="latin-1",
        dtype=str
    )

    return d


def open_mdic_file(filename):
    d = pd.read_csv(
        filename, sep=";", decimal=",", header=0, encoding="latin-1",
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

    d = d.sort_values(by=["CO_NCM", "CO_MES", "CO_ANO"], ascending=True)

    return d


def select(df, column, value):
    if type(value) is list:
        df = df.loc[df[column].isin(value)]
    else:
        df = df.loc[df[column] == value]

    return df

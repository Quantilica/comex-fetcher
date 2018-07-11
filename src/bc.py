import pandas as pd
import numpy as np


def open_file(filename):
    d = pd.read_csv(
        filename,
        sep=";",
        decimal=",",
        header=0,
        encoding="latin-1",
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
        },
    )

    d = d.rename(columns={"CO_ANO": "year", "CO_MES": "month"})
    d = d.assign(day=1)
    d.loc[:, "Date"] = pd.to_datetime(d[["year", "month", "day"]])
    d = d.drop(labels=["year", "month", "day"], axis=1)

    return d


def open_files(paths):
    df = pd.DataFrame()
    for f in paths:
        d = open_file(f)
        df = pd.concat([df, d], axis=0, ignore_index=True)

    return df

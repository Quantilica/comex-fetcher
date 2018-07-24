import pandas as pd
import numpy as np


def open_file(filename):
    d = pd.read_csv(
        filename,
        sep=";",
        decimal=",",
        header=0,
        encoding="latin-1",
        dtype=str,
    )
    d.loc[:, "QT_ESTAT"] = d["QT_ESTAT"].apply(lambda x: np.float64(x))
    d.loc[:, "KG_LIQUIDO"] = d["KG_LIQUIDO"].apply(lambda x: np.float64(x))
    d.loc[:, "VL_FOB"] = d["VL_FOB"].apply(lambda x: np.float64(x))

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

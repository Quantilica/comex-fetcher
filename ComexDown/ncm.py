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

    return d


def range_codes(ncm, code_start: str, code_end: str) -> np.ndarray:
    if len(code_start) < 2:
        raise
    elif len(code_start) < 8:
        code_start += "0" * (8 - len(code_start))
    if len(code_end) < 2:
        raise
    elif len(code_end) < 8:
        code_end += "9" * (8 - len(code_end))
    codes = ncm.loc[
        (ncm["CO_NCM"] >= code_start) & (ncm["CO_NCM"] <= code_end), "CO_NCM"
    ]

    return codes.values

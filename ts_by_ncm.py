import pandas as pd
import os


import commons


if not os.path.exists("by_ncm"):
    os.makedirs(os.path.join("by_ncm", "imp"))
    os.makedirs(os.path.join("by_ncm", "exp"))


def main():
    ncm = commons.open_ncm_file(
        os.path.join("DATA", "ncm", "NCM.csv"))

    data_imp = commons.open_zip_mdic_data(
        os.path.join("DATA", "imp", "IMP_COMPLETA.zip"))
    n = len(data_imp["CO_NCM"].unique())
    i = 1
    for cod in data_imp["CO_NCM"].unique():
        no_ncm = ncm[ncm["CO_NCM"] == cod].iloc[0]["NO_NCM_POR"]
        print(f"IMP {i: >6} de {n: >6} {cod} {no_ncm}")
        data_imp_cod = data_imp[data_imp["CO_NCM"] == cod]
        data_imp_cod.to_csv(
            os.path.join("by_ncm", "imp", f"{cod}.csv"),
            sep=";", decimal=",", encoding="latin-1", index=False)
        del data_imp_cod
        i += 1
    del data_imp

    data_exp = commons.open_zip_mdic_data(
        os.path.join("DATA", "exp", "EXP_COMPLETA.zip"))
    n = len(data_exp["CO_NCM"].unique())
    i = 1
    for cod in data_exp["CO_NCM"].unique():
        no_ncm = ncm[ncm["CO_NCM"] == cod].iloc[0]["NO_NCM_POR"]
        print(f"EXP {i: >6} de {n: >6} {cod} {no_ncm}")
        data_exp_cod = data_exp[data_exp["CO_NCM"] == cod]
        data_exp_cod.to_csv(
            os.path.join("by_ncm", "exp", f"{cod}.csv"),
            sep=";", decimal=",", encoding="latin-1", index=False)
        del data_exp_cod
        i += 1
    del data_exp


if __name__ == '__main__':
    main()

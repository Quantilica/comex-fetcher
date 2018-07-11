import os
import pandas as pd
import commons


PATH_DATA = os.path.join("..", "DATA")
PATH_DATA_EXP = os.path.join(PATH_DATA, "exp")
PATH_DATA_IMP = os.path.join(PATH_DATA, "imp")
PATH_NCM_FILE = os.path.join(PATH_DATA, "ncm", "NCM.csv")
PATH_PLOTS = os.path.join("..", "plots")
PATH_PLOTS_EXP = os.path.join(PATH_PLOTS, "ncm_exp")
PATH_PLOTS_IMP = os.path.join(PATH_PLOTS, "ncm_imp")


if not os.path.exists(PATH_PLOTS_EXP):
    os.makedirs(PATH_PLOTS_EXP)
if not os.path.exists(PATH_PLOTS_IMP):
    os.makedirs(PATH_PLOTS_IMP)

files_exp = [os.path.join(PATH_DATA_EXP, f) for f in os.listdir(PATH_DATA_EXP)]
files_imp = [os.path.join(PATH_DATA_IMP, f) for f in os.listdir(PATH_DATA_IMP)]

ncm_data = commons.open_ncm_file(PATH_NCM_FILE)


def ncm_ts(directory, ncm_cod):
    files = [os.path.join(directory, f) for f in os.listdir(directory)
             if os.path.isfile(os.path.join(directory, f))]
    df = pd.DataFrame()
    for f in files:
        print("File", f, "NCM", ncm_cod)
        d = commons.open_mdic_file(f)
        l0 = len(d)
        d = d.loc[d["CO_NCM"] == ncm_cod, :]
        d = d.rename(columns={"CO_ANO": "year", "CO_MES": "month"})
        d = d.assign(day=1)
        d.loc[:, "date"] = pd.to_datetime(d[["year", "month", "day"]])
        d = d.drop(labels=["year", "month", "day"], axis=1)
        d = d.set_index("date")
        l1 = len(d)
        print("  len", l0, l1)
        df = pd.concat([df, d], axis=0)

    return df


PATH_DATA_EXP_BY_NCM = os.path.join(PATH_DATA_EXP, "by_ncm")
if not os.path.exists(PATH_DATA_EXP_BY_NCM):
    os.makedirs(PATH_DATA_EXP_BY_NCM)

for ncm_cod in ncm_data["CO_NCM"].unique():
    print(ncm_cod)
    d = ncm_ts(PATH_DATA_EXP, ncm_cod)
    print("  LEN", len(d))
    d.to_csv(
        os.path.join(PATH_DATA_EXP_BY_NCM, f"{ncm_cod}.csv"),
        sep=";",
        decimal=",",
        encoding="latin-1",
    )


PATH_DATA_IMP_BY_NCM = os.path.join(PATH_DATA_EXP, "by_ncm")
if not os.path.exists(PATH_DATA_IMP_BY_NCM):
    os.makedirs(PATH_DATA_IMP_BY_NCM)

for ncm_cod in ncm_data["CO_NCM"].unique():
    print(ncm_cod)
    d = ncm_ts(PATH_DATA_IMP, ncm_cod)
    print("  LEN", len(d))
    d.to_csv(
        os.path.join(PATH_DATA_IMP_BY_NCM, f"{ncm_cod}.csv"),
        sep=";",
        decimal=",",
        encoding="latin-1",
    )

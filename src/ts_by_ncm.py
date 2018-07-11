import os
import pandas as pd
import commons


PATH_DATA = os.path.join("..", "DATA")
PATH_DATA_EXP = os.path.join(PATH_DATA, "exp")
PATH_DATA_IMP = os.path.join(PATH_DATA, "imp")
PATH_NCM_FILE = os.path.join(PATH_DATA, "ncm", "ncm_names.csv")
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
        d = commons.open_mdic_file(f)
        d = d.loc[d["CO_NCM"].isin(ncm_cod), :]
        d = d.rename(columns={"CO_ANO": "year", "CO_MES": "month"})
        d = d.assign(day=1)
        d.loc[:, "Date"] = pd.to_datetime(d[["year", "month", "day"]])
        d = d.drop(labels=["year", "month", "day"], axis=1)
        d = d.set_index("Date")
        l1 = len(d)
        print(f"    File {f}, Lines: {l1}")
        df = pd.concat([df, d], axis=0)

    return df


PATH_DATA_EXP_BY_NCM = os.path.join(PATH_DATA_EXP, "by_ncm")
if not os.path.exists(PATH_DATA_EXP_BY_NCM):
    os.makedirs(PATH_DATA_EXP_BY_NCM)

for n0 in ncm_data["N0"].unique():
    c_n0 = ncm_data.loc[ncm_data["N0"] == n0, :]
    for n1 in c_n0["N1"].unique():
        print(n0, n1)
        c_n1 = c_n0.loc[c_n0["N1"] == n1, :]
        d = ncm_ts(PATH_DATA_EXP, c_n1["CO_NCM"])
        print("  LEN", len(d))
        d.to_csv(
            os.path.join(PATH_DATA_EXP_BY_NCM, f"{n0}{n1}.csv"),
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

import pandas as pd
import os


PATH_SERIE_BC = os.path.join("DATA", "serie_historica_BC.csv")
PATH_NCM = os.path.join("DATA", "ncm_complete.csv")


def anualize_bc(nx, ncm, fields=[]):
    nx = pd.merge(nx, ncm[["CO_NCM"] + fields], on=["CO_NCM"], how="left")
    nx = nx.groupby(["CO_ANO"] + fields).sum()
    nx = nx.reset_index()
    nx = nx[["CO_ANO"] + fields + [
        "QT_ESTAT_EXP", "QT_ESTAT_IMP", "KG_LIQUIDO_EXP", "KG_LIQUIDO_IMP",
        "VL_FOB_EXP", "VL_FOB_IMP", "NX"]]

    return nx


def main():
    nx = pd.read_csv(
        PATH_SERIE_BC,
        header=0,
        encoding="utf-8",
        dtype={
            "CO_NCM": str,
            "CO_ANO": str,
            "CO_PAIS": str,
            "QT_ESTAT_EXP": pd.np.float64,
            "QT_ESTAT_IMP": pd.np.float64,
            "KG_LIQUIDO_EXP": pd.np.float64,
            "KG_LIQUIDO_IMP": pd.np.float64,
            "VL_FOB_EXP": pd.np.float64,
            "VL_FOB_IMP": pd.np.float64,
            "NX": pd.np.float64,
        }
    )

    ncm = pd.read_csv(
        PATH_NCM,
        header=0,
        encoding="utf-8",
        dtype=str
    )

    fields_list = {
        "isic": ["NO_ISIC4_SECAO", "NO_ISIC4_GRUPO", "NO_ISIC4"],
        "cuci": ["NO_CUCI_ITEM", "NO_CUCI_SUB", "NO_CUCI_POS",
                 "NO_CUCI_CAP", "NO_CUCI_SEC"],
        "siit": ["CO_SIIT"],
        "fat_agreg": ["NO_FAT_AGREG"],
        "ppe": ["NO_PPE"],
        "ppi": ["NO_PPI"],
        "sh": ["NO_SEC_POR", "NO_SH2_POR", "NO_SH4_POR", "NO_SH6_POR"],
    }

    for f in fields_list:
        print("Processando:", f)
        a = anualize_bc(nx, ncm, fields_list[f])
        a.to_excel(
            "{}.xlsx".format(f),
            index=False
        )


if __name__ == '__main__':
    main()

import commons
import os


PATH_DATA = os.path.join("..", "DATA")


def main():
    ncm = commons.open_ncm_file(os.path.join(PATH_DATA, "ncm", "NCM.csv"))

    ncm = ncm[["CO_NCM", "NO_NCM_POR"]]
    ncm["N0"] = ncm["CO_NCM"].apply(lambda s: s[0:2])
    ncm["N1"] = ncm["CO_NCM"].apply(lambda s: s[2:4])
    ncm["N2a"] = ncm["CO_NCM"].apply(lambda s: s[4])
    ncm["N2b"] = ncm["CO_NCM"].apply(lambda s: s[5])
    ncm["N3a"] = ncm["CO_NCM"].apply(lambda s: s[6])
    ncm["N3b"] = ncm["CO_NCM"].apply(lambda s: s[7])
    ncm["CO_NCM"] = ncm["CO_NCM"].apply(lambda s: s)
    ncm = ncm[["CO_NCM", "N0", "N1", "N2a", "N2b", "N3a", "N3b", "NO_NCM_POR"]]
    ncm.set_index("CO_NCM", inplace=True)

    ncm.to_csv(
        os.path.join(PATH_DATA, "ncm", "ncm_names.csv"),
        sep=";",
        encoding="latin-1",
    )


if __name__ == '__main__':
    main()

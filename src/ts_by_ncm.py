import os
import commons


if not os.path.exists(os.path.join("..", "DATA", "by_ncm")):
    os.makedirs(os.path.join("..", "DATA", "by_ncm", "IMP"))
    os.makedirs(os.path.join("..", "DATA", "by_ncm", "EXP"))


def separate_groups(data, t):
    data.loc[:, "CO_NCM_GROUP"] = data["CO_NCM"].apply(lambda x: x[:2])
    ncm_groups = data["CO_NCM_GROUP"].unique()
    len_ncm_groups = len(ncm_groups)
    i = 1
    for group in ncm_groups:
        print(f"{t} {i: >4} of {len_ncm_groups: >4} : {group}")
        data_group = data.loc[data["CO_NCM_GROUP"] == group]
        ncm_codes = data_group["CO_NCM"].unique()
        len_ncm_codes = len(ncm_codes)
        j = 1
        for code in ncm_codes:
            print(f"{t} {j: >4} of {len_ncm_codes: >4} : {code}")
            data_code = data_group.loc[data_group["CO_NCM"] == code]
            if not os.path.exists(os.path.join("by_ncm", t, group)):
                os.makedirs(os.path.join("by_ncm", t, group))
            data_code.to_csv(
                os.path.join("..", "DATA", "by_ncm", t, group, f"{code}.csv"),
                sep=";", decimal=",", encoding="latin-1", index=False)
            del data_code
            j += 1
        del data_group
        i += 1


def main():
    data_imp = commons.open_zip_mdic_data(
        os.path.join("..", "DATA", "imp", "IMP_COMPLETA.zip"))
    separate_groups(data_imp, "IMP")
    del data_imp

    data_exp = commons.open_zip_mdic_data(
        os.path.join("..", "DATA", "exp", "EXP_COMPLETA.zip"))
    separate_groups(data_exp, "EXP")
    del data_exp


if __name__ == '__main__':
    main()

import os
import commons


def main():
    data = commons.open_zip_mdic_data(
        os.path.join("..", "DATA", "imp", "IMP_COMPLETA.zip"))
    for year in data["CO_ANO"].unique():
        print("IMP", year)
        dy = data.loc[data["CO_ANO"] == year]
        dy.to_csv(
            os.path.join("..", "DATA", "imp", f"{year}.csv"),
            sep=";", decimal=",", encoding="latin-1", index=False)
    del data

    data = commons.open_zip_mdic_data(
        os.path.join("..", "DATA", "exp", "EXP_COMPLETA.zip"))
    for year in data["CO_ANO"].unique():
        print("EXP", year)
        dy = data.loc[data["CO_ANO"] == year]
        dy.to_csv(
            os.path.join("..", "DATA", "exp", f"{year}.csv"),
            sep=";", decimal=",", encoding="latin-1", index=False)
    del data


if __name__ == '__main__':
    main()

from urllib import request
import os
import argparse


PATH_DATA = os.path.join("..", "DATA")


if not os.path.exists(PATH_DATA):
    os.makedirs(os.path.join(PATH_DATA))
    os.makedirs(os.path.join(PATH_DATA, "code"))
    os.makedirs(os.path.join(PATH_DATA, "exp"))
    os.makedirs(os.path.join(PATH_DATA, "imp"))
    os.makedirs(os.path.join(PATH_DATA, "ncm"))


URL_NCM_TABLES = [
    # Tabelas de Correlações de Códigos e Classificações
    "http://www.mdic.gov.br/balanca/bd/tabelas/NCM.csv",  # Tabela NCM
    "http://www.mdic.gov.br/balanca/bd/tabelas/NCM_SH.csv",  # Tabela NCM-SH
    "http://www.mdic.gov.br/balanca/bd/tabelas/NCM_CUCI.csv",  # Tabela NCM-CUCI
    "http://www.mdic.gov.br/balanca/bd/tabelas/NCM_CGCE.csv",  # Tabela NCM-CGCE
    "http://www.mdic.gov.br/balanca/bd/tabelas/NCM_ISIC.csv",  # Tabela NCM-ISIC
    "http://www.mdic.gov.br/balanca/bd/tabelas/NCM_SIIT.csv",  # Tabela NCM-SIIT
    "http://www.mdic.gov.br/balanca/bd/tabelas/NCM_FAT_AGREG.csv",  # Tabela NCM-
    "http://www.mdic.gov.br/balanca/bd/tabelas/NCM_PPE.csv",  # Tabela NCM-FAT_AGREG
    "http://www.mdic.gov.br/balanca/bd/tabelas/NCM_PPI.csv",  # Tabela NCM-PPE
    "http://www.mdic.gov.br/balanca/bd/tabelas/NCM_UNIDADE.csv",  # Tabela NCM-UNIDADE
]
URL_CODE_TABLES = [
    "http://www.mdic.gov.br/balanca/bd/tabelas/PAIS.csv",  # Tabela NCM-PAIS
    "http://www.mdic.gov.br/balanca/bd/tabelas/PAIS_BLOCO.csv",  # Tabela NCM-PAIS_BLOCO
    "http://www.mdic.gov.br/balanca/bd/tabelas/UF_MUN.csv",  # Tabela NCM-UF_MUN
    "http://www.mdic.gov.br/balanca/bd/tabelas/UF.csv",  # Tabela NCM-UF
    "http://www.mdic.gov.br/balanca/bd/tabelas/PORTO.csv",  # Tabela NCM-PORTO
    "http://www.mdic.gov.br/balanca/bd/tabelas/VIA.csv",  # Tabela NCM-VIA
]
URL_COMPLETE_BC_TABLES = [
    # Dados de séries históricas de importações e exportações
    "http://www.mdic.gov.br/balanca/bd/ncm/EXP_COMPLETA.zip",  # Arquivo da série histórica de exportações
    "http://www.mdic.gov.br/balanca/bd/ncm/IMP_COMPLETA.zip",  # Arquivo da série histórica de importações
]
CANON_EXP = "http://www.mdic.gov.br/balanca/bd/ncm/EXP_{year}.csv"
CANON_IMP = "http://www.mdic.gov.br/balanca/bd/ncm/IMP_{year}.csv"
# Fonte: http://www.mdic.gov.br/index.php/comercio-exterior/estatisticas-de-
# comercio-exterior/base-de-dados-do-comercio-exterior-brasileiro-arquivos-para-download


def download_file(url, path):
    if not os.path.exists(path):
        os.makedirs(path)
    filename = os.path.join(path, url.rsplit("/", maxsplit=1)[1])
    print(f"Baixando arquivo: {url:<50} --> {filename}")
    data = request.urlopen(url)
    with open(filename, "wb") as f:
        f.write(data.read())


def download_ncm():
    for url in URL_NCM_TABLES:
        download_file(url, os.path.join(PATH_DATA, "ncm"))


def download_code():
    for url in URL_CODE_TABLES:
        download_file(url, os.path.join(PATH_DATA, "code"))


def download_exp(year):
    url = CANON_EXP.format(year=year)
    download_file(url, os.path.join(PATH_DATA, "exp"))


def download_imp(year):
    url = CANON_EXP.format(year=year)
    download_file(url, os.path.join(PATH_DATA, "exp"))


def main():
    parser = argparse.ArgumentParser(description="download data")
    parser.add_argument("-t", choices=["m", "x"],
                        help="download import/export data")
    parser.add_argument("years", type=int, nargs="+",
                        help="years to download")
    args = parser.parse_args()
    print(args.years)

    if args.t:
        if args.t == "m":
            for year in args.years:
                download_imp(year)
        else:
            for year in args.years:
                download_exp(year)
    else:
        for year in args.years:
            download_imp(year)
            download_exp(year)


if __name__ == "__main__":
    main()

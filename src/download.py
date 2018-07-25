from urllib import request
import os


CANON_URL_NCM_TABLES = "http://www.mdic.gov.br/balanca/bd/tabelas/NCM{}.csv"
NCM_TABLES = {
    "ncm": "",
    "sh": "_SH",
    "cuci": "_CUCI",
    "cgce": "_CGCE",
    "isic": "_ISIC",
    "siit": "_SIIT",
    "fat_agreg": "_FAT_AGREG",
    "ppe": "_PPE",
    "ppi": "_PPI",
    "unidade": "_UNIDADE",
}

CANON_URL_CODE_TABLES = "http://www.mdic.gov.br/balanca/bd/tabelas/{}.csv"

CODE_TABLES = {
    "pais": "PAIS",
    "pais_bloco": "PAIS_BLOCO",
    "uf_mun": "UF_MUN",
    "uf": "UF",
    "porto": "PORTO",
    "via": "VIA",
    "urf": "URF"
}

URL_COMPLETE_BC_TABLES = [
    # Dados de séries históricas de importações e exportações
    "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_COMPLETA.zip",  # Arquivo da série histórica de exportações
    "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_COMPLETA.zip",  # Arquivo da série histórica de importações
]

URL_COMPLETE_BC_MUN_TABLES = [
    "http://www.mdic.gov.br/balanca/bd/comexstat-bd/mun/EXP_COMPLETA_MUN.zip",
    "http://www.mdic.gov.br/balanca/bd/comexstat-bd/mun/IMP_COMPLETA_MUN.zip",
]

CANON_EXP = "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_{year}.csv"
CANON_IMP = "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_{year}.csv"
CANON_EXP_MUN = "http://www.mdic.gov.br/balanca/bd/comexstat-bd/mun/EXP_{year}_MUN.csv"
CANON_IMP_MUN = "http://www.mdic.gov.br/balanca/bd/comexstat-bd/mun/IMP_{year}_MUN.csv"
# Fonte: http://www.mdic.gov.br/index.php/comercio-exterior/estatisticas-de-
# comercio-exterior/base-de-dados-do-comercio-exterior-brasileiro-arquivos-para-download

PATH_DATA = os.path.join("..", "DATA")


def download(url, path):
    if not os.path.exists(path):
        os.makedirs(path)
    filename = os.path.join(path, url.rsplit("/", maxsplit=1)[1])
    while True:
        print(f"Baixando arquivo: {url:<50} --> {filename}")
        try:
            data = request.urlopen(url)
        except Exception:
            print("Erro. Tentando novamente...")
        else:
            break
    with open(filename, "wb") as f:
        f.write(data.read())


def ncm(table="ncm"):
    download(
        CANON_URL_NCM_TABLES.format(NCM_TABLES[table]),
        os.path.join(PATH_DATA, "ncm"),
    )


def code(table):
    download(
        CANON_URL_CODE_TABLES.format(table),
        os.path.join(PATH_DATA, "code"),
    )


def exp(year):
    url = CANON_EXP.format(year=year)
    download(url, os.path.join(PATH_DATA, "exp"))


def imp(year):
    url = CANON_IMP.format(year=year)
    download(url, os.path.join(PATH_DATA, "imp"))


def exp_mun(year):
    url = CANON_EXP_MUN.format(year=year)
    download(url, os.path.join(PATH_DATA, "exp_mun"))


def imp_mun(year):
    url = CANON_IMP_MUN.format(year=year)
    download(url, os.path.join(PATH_DATA, "imp_mun"))

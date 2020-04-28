from urllib import request
import os
import time
import sys


CANON_URL = "http://www.mdic.gov.br/balanca/bd/"

# TABLES
CANON_URL_TABLES = CANON_URL + "tabelas/"

CANON_URL_NCM_TABLES = CANON_URL_TABLES + "NCM{}.csv"
NCM_TABLES = {
    "ncm": "",
    "sh": "_SH",
    "cgce": "_CGCE",
    "isic": "_ISIC_CUCI",
    "fat_agreg": "_FAT_AGREG",
    "ppe": "_PPE",
    "ppi": "_PPI",
    "unidade": "_UNIDADE",
}

CANON_URL_NBM_TABLES = CANON_URL_TABLES + "NBM{}.csv"
NBM_TABLES = {
    "nbm": "",
    "ncm": "_NCM"
}

CANON_URL_CODE_TABLES = CANON_URL_TABLES + "{}.csv"
CODE_TABLES = {
    "pais": "PAIS",
    "pais_bloco": "PAIS_BLOCO",
    "uf_mun": "UF_MUN",
    "uf": "UF",
    "via": "VIA",
    "urf": "URF"
}


# DATA
CANON_URL_DATA = CANON_URL + "comexstat-bd/"

URL_COMPLETE_BC_TABLES = [
    # Dados de séries históricas de importações e exportações
    CANON_URL_DATA + "ncm/EXP_COMPLETA.zip",
    CANON_URL_DATA + "ncm/IMP_COMPLETA.zip",
]

URL_COMPLETE_BC_MUN_TABLES = [
    CANON_URL_DATA + "mun/EXP_COMPLETA_MUN.zip",
    CANON_URL_DATA + "mun/IMP_COMPLETA_MUN.zip",
]

CANON_EXP = CANON_URL_DATA + "ncm/EXP_{year}.csv"
CANON_IMP = CANON_URL_DATA + "ncm/IMP_{year}.csv"
CANON_EXP_MUN = CANON_URL_DATA + "mun/EXP_{year}_MUN.csv"
CANON_IMP_MUN = CANON_URL_DATA + "mun/IMP_{year}_MUN.csv"
CANON_EXP_NBM = CANON_URL_DATA + "nbm/EXP_{year}_NBM.csv"
CANON_IMP_NBM = CANON_URL_DATA + "nbm/IMP_{year}_NBM.csv"
# Fonte: 
# http://www.mdic.gov.br/index.php/comercio-exterior/estatisticas-de-comercio-exterior/base-de-dados-do-comercio-exterior-brasileiro-arquivos-para-download


def download(url, path, retry=3, blocksize=1024):
    """Downloads the file in `url` and saves it in `path`

    Parameters
    ----------
    url: str
        The resource's URL to download
    path: str
        The destination path of downloaded file
    retry: int [default=3]
        Number of retries until raising exception
    blocksize: int [default=1024]
        The block size of requests

    """
    if not os.path.exists(path):
        os.makedirs(path)

    filename = os.path.join(path, url.rsplit("/", maxsplit=1)[1])
    for x in range(retry):
        sys.stdout.write(f"Baixando arquivo: {url:<50} --> {filename}\n")
        sys.stdout.flush()
        try:
            resp = request.urlopen(url)
            length = resp.getheader("content-length")
            if length:
                length = int(length)

            size = 0
            with open(filename, "wb") as f:
                while True:
                    buf1 = resp.read(blocksize)
                    if not buf1:
                        break
                    f.write(buf1)
                    size += len(buf1)
                    p = size / length
                    bar = "[{:<70}]".format("=" * int(p * 70))
                    if size > 2**20:
                        size_txt = "{: >9.2f} MiB".format(size / 2**20)
                    else:
                        size_txt = "{: >9.2f} KiB".format(size / 2**10)
                    if length:
                        sys.stdout.write(
                            f"{bar} {p*100: >5.1f}% {size_txt}\r")
                        sys.stdout.flush()

        except Exception as e:
            sys.stdout.write(f"\nErro... {e}")
            sys.stdout.flush()
            time.sleep(3)
            if x == retry - 1:
                raise

        else:
            sys.stdout.write("\n")
            sys.stdout.flush()
            break


def ncm(table, path):
    """Downloads a NCM table

    Parameters
    ----------
    table: str
        NCM table name to download
    path: str
        Destination path directory to save file

    """
    download(
        CANON_URL_NCM_TABLES.format(NCM_TABLES[table]),
        os.path.join(path, "ncm"),
    )


def nbm(table, path):
    """Downloads a NBM file

    Parameters
    ----------
    table: str
        NBM table name to download
    path: str
        Destination path directory to save file

    """
    download(
        CANON_URL_NBM_TABLES.format(NBM_TABLES[table]),
        os.path.join(path, "nbm"),
    )


def code(table, path):
    """Downloads a code file

    Parameters
    ----------
    table: str
        code table name to download
    path: str
        Destination path directory to save file

    """
    download(
        CANON_URL_CODE_TABLES.format(CODE_TABLES[table]),
        os.path.join(path, "code"),
    )


def exp(year, path):
    """Downloads a exp file

    Parameters
    ----------
    year: int
        exp year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_EXP.format(year=year)
    download(url, os.path.join(path, "exp"))


def imp(year, path):
    """Downloads a imp file

    Parameters
    ----------
    year: int
        imp year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_IMP.format(year=year)
    download(url, os.path.join(path, "imp"))


def exp_mun(year, path):
    """Downloads a exp_mun file

    Parameters
    ----------
    year: int
        exp_mun year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_EXP_MUN.format(year=year)
    download(url, os.path.join(path, "exp_mun"))


def imp_mun(year, path):
    """Downloads a imp_mun file

    Parameters
    ----------
    year: int
        imp_mun year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_IMP_MUN.format(year=year)
    download(url, os.path.join(path, "imp_mun"))


def exp_nbm(year, path):
    """Downloads a exp_nbm file

    Parameters
    ----------
    year: int
        exp_nbm year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_EXP_NBM.format(year=year)
    download(url, os.path.join(path, "exp_nbm"))


def imp_nbm(year, path):
    """Downloads a imp_nbm file

    Parameters
    ----------
    year: int
        imp_nbm year to download
    path: str
        Destination path directory to save file

    """
    url = CANON_IMP_NBM.format(year=year)
    download(url, os.path.join(path, "imp_nbm"))

from urllib import request
import os
import time


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


def download(url, path, retry=3, blocksize=1024):
    if not os.path.exists(path):
        os.makedirs(path)

    filename = os.path.join(path, url.rsplit("/", maxsplit=1)[1])
    for x in range(retry):
        print(f"Baixando arquivo: {url:<50} --> {filename}")
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
                        print(f"{bar} {p*100: >5.1f}% {size_txt}\r", end="")

        except Exception as e:
            print("\nErro...", e)
            time.sleep(3)
            if x == retry - 1:
                raise

        else:
            print("\n")
            break


def ncm(table, path):
    download(
        CANON_URL_NCM_TABLES.format(NCM_TABLES[table]),
        os.path.join(path, "ncm"),
    )


def code(table, path):
    download(
        CANON_URL_CODE_TABLES.format(CODE_TABLES[table]),
        os.path.join(path, "code"),
    )


def exp(year, path):
    url = CANON_EXP.format(year=year)
    download(url, os.path.join(path, "exp"))


def imp(year, path):
    url = CANON_IMP.format(year=year)
    download(url, os.path.join(path, "imp"))


def exp_mun(year, path):
    url = CANON_EXP_MUN.format(year=year)
    download(url, os.path.join(path, "exp_mun"))


def imp_mun(year, path):
    url = CANON_IMP_MUN.format(year=year)
    download(url, os.path.join(path, "imp_mun"))

# comexdown: Brazil's foreign trade data downloader

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/dankkom/comexdown/tests?style=flat-square) ![Coveralls github](https://img.shields.io/coveralls/github/dankkom/comexdown?style=flat-square) ![GitHub](https://img.shields.io/github/license/dankkom/comexdown?style=flat-square) ![PyPI](https://img.shields.io/pypi/v/comexdown?style=flat-square)

This package contains functions to download brazilian foreign trade data
published by [Ministerio da Economia(ME)/Secretaria de Comercio Exterior (SCE)][1].

## Installation

`comexdown` package is available on PyPI, so just use `pip`!

```sh
pip install comexdown
```

## Usage

```python
import comexdown

# Download main NCM table in the directory ./DATA
comexdown.ncm(table="ncm", path="./DATA")

# Download 2019 exports data file in the directory ./DATA
comexdown.exp(year=2019, path="./DATA")
```

## Command line tool

Download data on Brazilian foreign trade transactions (Exports / Imports).

You can specify a range of years to download at once.

```
comexdown download trade 2008:2019 -o "./DATA"
```

Download code tables.

```shell
comexdown download code all  # Download all related code files
comexdown download code uf   # Download only the UF.csv file
comexdown download ncm_cgce  # Download only the NCM_CGCE.csv file
comexdown download nbm_ncm   # Download only the NBM_NCM.csv file
```

[1]: http://www.mdic.gov.br/index.php/comercio-exterior/estatisticas-de-comercio-exterior/base-de-dados-do-comercio-exterior-brasileiro-arquivos-para-download

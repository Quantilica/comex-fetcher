# comexdown: Brazil's foreign trade data downloader

![GitHub](https://img.shields.io/github/license/dankkom/comexdown?style=flat-square) ![PyPI](https://img.shields.io/pypi/v/comexdown?style=flat-square)

This package contains functions to download brazilian foreign trade data
published by [Ministerio da Economia(ME)/Secretaria de Comercio Exterior (SCE)][1].

## Installation

`comexdown` package is available on PyPI, so just use `pip`!

```shell
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
comexdown trade 2008:2019 -o "./DATA"
```

Download code tables.

```shell
comexdown tables  # Download all related code files
```

## Datasets

- Trade data:
  - exp
  - imp
  - exp-mun
  - imp-mun
  - exp-nbm
  - imp-nbm
- Unique trade data files:
  - exp-completa
  - imp-completa
  - exp-mun-completa
  - imp-mun-completa
- Trade validation data:
  - exp-validacao
  - imp-validacao
  - exp-mun-validacao
  - imp-mun-validacao
- Trade REPETRO:
  - exp-repetro
  - imp-repetro
- Auxiliary tables:
  - ncm
  - sh
  - cuci
  - cgce
  - isic
  - siit
  - fat-agreg
  - unidade
  - ppi
  - ppe
  - grupo
  - pais
  - pais-bloco
  - uf
  - uf-mun
  - via
  - urf
  - isic-cuci
  - nbm
  - ncm-nbm

Data source: [Ministério da Economia/Secretaria de Comércio Exterior](https://www.gov.br/produtividade-e-comercio-exterior/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta)

## Development

To setup a development environment clone this repository and install the required packages:

```shell
git clone https://github.com/dankkom/comexdown.git
cd comexdown
pip install -e .[dev]
```

### Run tests

To run the tests suite, use the following command:

```shell
 pip install -e .[dev]
 pytest tests/
```

[1]: https://www.gov.br/produtividade-e-comercio-exterior/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta

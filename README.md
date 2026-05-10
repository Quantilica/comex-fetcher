# comex-fetcher: Brazil's foreign trade data downloader

![GitHub](https://img.shields.io/github/license/Quantilica/comex-fetcher?style=flat-square) ![PyPI](https://img.shields.io/pypi/v/comex-fetcher?style=flat-square)

This package contains functions to download brazilian foreign trade data
published by [Ministerio da Economia(ME)/Secretaria de Comercio Exterior (SCE)][1].

> **Note:** This package was formerly known as `comexdown`. See [migration guide](#migration-from-comexdown) below.

## Installation

`comex-fetcher` package is available on PyPI:

```shell
pip install comex-fetcher
```

## Usage

```python
import comex_fetcher

# Download main NCM table in the directory ./DATA
comex_fetcher.ncm(table="ncm", path="./DATA")

# Download 2019 exports data file in the directory ./DATA
comex_fetcher.exp(year=2019, path="./DATA")
```

## Command line tool

Download data on Brazilian foreign trade transactions (Exports / Imports).

You can specify a range of years to download at once.

```
comex-fetcher trade 2008:2019 -o "./DATA"
```

Download code tables.

```shell
comex-fetcher tables  # Download all related code files
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

## Migration from comexdown

If you were using `comexdown`, update your install and imports:

```shell
pip uninstall comexdown
pip install comex-fetcher
```

```python
# Before
import comexdown
comexdown.exp(year=2019, path="./DATA")

# After
import comex_fetcher
comex_fetcher.exp(year=2019, path="./DATA")
```

The `comexdown` package on PyPI will redirect you automatically (with a deprecation warning), but updating your code is recommended.

## Development

To setup a development environment clone this repository and install the required packages:

```shell
git clone https://github.com/Quantilica/comex-fetcher.git
cd comex-fetcher
pip install -e .[dev]
```

### Run tests

```shell
pip install -e .[dev]
pytest tests/
```

[1]: https://www.gov.br/produtividade-e-comercio-exterior/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta

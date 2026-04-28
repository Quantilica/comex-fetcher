"""URL generation for Brazil's foreign trade data sources.

This module provides functions to generate URLs for downloading various
types of foreign trade data from the Brazilian Ministry of Economy servers.
"""

from .constants import (
    ARQUIVO_UNICO,
    AUX_TABLES,
    BASE_URL,
    OTHER_TABLES,
    REPETRO_TABLES,
    TOTAIS_PARA_VALIDACAO,
    TRADE,
)


def table(table_name: str) -> str:
    """Generate URL for an auxiliary code table."""
    return get_url(table_name)


def trade(
    direction: str,
    year: int,
    mun: bool = False,
    nbm: bool = False,
) -> str:
    """Generate URL for trade transaction data."""
    if nbm:
        return get_url(f"{direction.lower()}-nbm", year=year)
    if mun:
        return get_url(f"{direction.lower()}-mun", year=year)
    return get_url(direction.lower(), year=year)


def complete(direction: str, mun: bool = False) -> str:
    """Generate URL for complete historical trade dataset."""
    key = f"{direction.lower()}-completa"
    if mun:
        key = f"{direction.lower()}-mun-completa"
    return get_url(key)


def get_url(table_name: str, **kwargs) -> str:
    """Centralized URL generation logic."""
    year = kwargs.get("year")

    if table_name in TRADE:
        return TRADE[table_name]["server_dir"] + TRADE[table_name]["server_filename"].format(year=year)

    if table_name in ARQUIVO_UNICO:
        return ARQUIVO_UNICO[table_name]["url"]

    if table_name in TOTAIS_PARA_VALIDACAO:
        return TOTAIS_PARA_VALIDACAO[table_name]["url"]

    if table_name in REPETRO_TABLES:
        return REPETRO_TABLES[table_name]["url"]

    if table_name == "tabelas-auxiliares":
        return OTHER_TABLES[table_name]["url"]

    if table_name in AUX_TABLES:
        return f"{BASE_URL}tabelas/{AUX_TABLES[table_name]}"

    raise ValueError(f"Unknown table or dataset: {table_name}")

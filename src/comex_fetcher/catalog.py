"""COMEX unified dataset catalog."""

import datetime as dt
from collections.abc import Callable
from typing import Any

from .constants import (
    AUX_TABLES,
    OTHER_TABLES,
    REPETRO_TABLES,
    TABLES,
    TOTAIS_PARA_VALIDACAO,
)
from .urls import get_url

_FIRST_YEAR_NCM = 1997
_YEARS_NBM = list(range(1989, 1997))

# O arquivo do ano novo (``EXP_2027.csv``, ``IMP_2027_MUN.csv``) só passa a
# existir quando o MDIC publica o primeiro mês do ano (a divulgação mensal sai no
# começo do mês seguinte). Até lá o servidor responde 404, ou 206 com código PHP
# no lugar do arquivo (o "soft-206", ver ``payload.py``). A entrada do ano
# corrente leva ``pending_publication`` (esse "arquivo inexistente" vira "ainda
# não publicado", sem erro) por esta folga, contada desde 1º de janeiro: 1º de
# março, com margem sobre a divulgação de janeiro (começo de fevereiro). Passada
# a folga, o arquivo ausente volta a ser erro. Estimativa, não medida: ajuste se o
# MDIC publicar mais tarde. O ano é calculado a cada listagem, não na importação.
PENDING_GRACE_DAYS = 60


def _pending_year(today: dt.date) -> int | None:
    """Ano cuja entrada ainda pode não estar publicada em ``today``, se houver."""
    year = today.year
    limit = dt.date(year, 1, 1) + dt.timedelta(days=PENDING_GRACE_DAYS)
    return year if today <= limit else None


def _make_trade_entries(
    direction: str,
    years: list[int],
    mun: bool = False,
    nbm: bool = False,
    pending_year: int | None = None,
) -> list[dict[str, Any]]:
    entries = []
    group = f"trade-{direction}"
    if nbm:
        group += "-nbm"
        base_name = f"{direction}-nbm"
    elif mun:
        group += "-mun"
        base_name = f"{direction}-mun"
    else:
        base_name = direction

    for y in years:
        entry: dict[str, Any] = {
            "id": f"{base_name}-{y}",
            "group": group,
            "url": get_url(base_name, year=y),
            "ext": "csv",
            "year": y,
            "direction": direction,
            "mun": mun,
            "nbm": nbm,
            "is_trade": True,
        }
        if y == pending_year:
            entry["pending_publication"] = True
        entries.append(entry)
    return entries


def _make_table_entries(group: str, table_dict: dict) -> list[dict[str, Any]]:
    entries = []
    for name, info in table_dict.items():
        url = info.get("url")
        if not url and name in AUX_TABLES:
            url = get_url(name)
        elif not url:
            url = get_url(name)

        ext = "csv"
        if "server_filename" in info:
            ext = info["server_filename"].split(".")[-1]
        elif "file_ref" in info:
            ext = info["file_ref"].split(".")[-1]

        entries.append(
            {
                "id": name,
                "group": group,
                "url": url,
                "ext": ext,
                "is_table": True,
                "table_group": group,
            }
        )
    return entries


_ENTRIES_AUX = _make_table_entries("auxiliary", TABLES)
_ENTRIES_REPETRO = _make_table_entries("repetro", REPETRO_TABLES)
_ENTRIES_VALIDATION = _make_table_entries("validation", TOTAIS_PARA_VALIDACAO)
_ENTRIES_OTHER = _make_table_entries("other", OTHER_TABLES)

GROUPS = {
    "trade-exp": {"name": "Exportação"},
    "trade-imp": {"name": "Importação"},
    "trade-exp-mun": {"name": "Exportação Municipal"},
    "trade-imp-mun": {"name": "Importação Municipal"},
    "trade-exp-nbm": {"name": "Exportação NBM"},
    "trade-imp-nbm": {"name": "Importação NBM"},
    "auxiliary": {"name": "Tabelas Auxiliares"},
    "repetro": {"name": "Tabelas REPETRO"},
    "validation": {"name": "Totais para Validação"},
    "other": {"name": "Outras Tabelas"},
}

# Tabelas: não dependem do ano, geradas uma vez.
_TABLE_ENTRIES: dict[str, list[dict[str, Any]]] = {
    "auxiliary": _ENTRIES_AUX,
    "repetro": _ENTRIES_REPETRO,
    "validation": _ENTRIES_VALIDATION,
    "other": _ENTRIES_OTHER,
}


def _group_entries(group: str, today: dt.date) -> list[dict[str, Any]]:
    """Entradas de um grupo canônico; o ano corrente é o de ``today``."""
    if group in _TABLE_ENTRIES:
        return _TABLE_ENTRIES[group]
    years_ncm = list(range(_FIRST_YEAR_NCM, today.year + 1))
    pending = _pending_year(today)
    builders: dict[str, Callable[[], list[dict[str, Any]]]] = {
        "trade-exp": lambda: _make_trade_entries(
            "exp", years_ncm, pending_year=pending
        ),
        "trade-imp": lambda: _make_trade_entries(
            "imp", years_ncm, pending_year=pending
        ),
        "trade-exp-mun": lambda: _make_trade_entries(
            "exp", years_ncm, mun=True, pending_year=pending
        ),
        "trade-imp-mun": lambda: _make_trade_entries(
            "imp", years_ncm, mun=True, pending_year=pending
        ),
        "trade-exp-nbm": lambda: _make_trade_entries("exp", _YEARS_NBM, nbm=True),
        "trade-imp-nbm": lambda: _make_trade_entries("imp", _YEARS_NBM, nbm=True),
    }
    return builders[group]()


GROUP_ALIASES = {
    "trade": [
        "trade-exp",
        "trade-imp",
        "trade-exp-mun",
        "trade-imp-mun",
        "trade-exp-nbm",
        "trade-imp-nbm",
    ],
    "tables": ["auxiliary", "repetro", "validation", "other"],
}


def list_datasets(
    group: str | None = None, *, today: dt.date | None = None
) -> list[dict[str, Any]]:
    """Lists available datasets in the catalog.

    Args:
        group (str | None): The specific group to list datasets for. If None,
            returns all datasets across all groups.
        today (dt.date | None): Reference day (default: today). The current
            year of the trade files is computed from it at each call.

    Returns:
        list[dict[str, Any]]: A list of dataset entry dictionaries. The current
            year's trade entries carry ``pending_publication`` while the file may
            not be published yet (see ``PENDING_GRACE_DAYS``).

    Raises:
        ValueError: If an unknown group is provided.
    """
    today = today or dt.date.today()
    if group is not None:
        if group in GROUPS:
            return list(_group_entries(group, today))
        if group in GROUP_ALIASES:
            return [e for g in GROUP_ALIASES[group] for e in _group_entries(g, today)]
        raise ValueError(f"Unknown group: {group!r}")

    return [e for g in GROUPS for e in _group_entries(g, today)]

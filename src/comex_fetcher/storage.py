"""Functions to manage downloaded file locations and paths.

This module provides utilities for generating standardized file paths for
downloaded foreign trade data and auxiliary tables. It ensures consistent
organization of data files with proper directory structure and naming
conventions.
"""

from pathlib import Path

from quantilica_core.storage import BaseDataRepository
from comex_fetcher.constants import TABLES


class DataRepository(BaseDataRepository):
    """Class to manage data repository paths using BaseDataRepository."""

    def __init__(self, root: Path | str):
        super().__init__(root)

    def path_aux(self, name: str) -> Path:
        """Generate path for auxiliary table file."""
        file_info = TABLES.get(name)
        if not file_info:
            raise ValueError(f"Unknown auxiliary table name: {name}")

        filename = file_info.get("file_ref")
        if not filename:
            raise ValueError(f"Auxiliary table '{name}' has no file reference")

        return self.storage.path_for(f"auxiliary-tables/{filename}")

    def path_trade(self, direction: str, year: int, mun: bool = False) -> Path:
        """Generate path for trade data file (NCM classification)."""
        direction = direction.lower()
        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction}")

        prefix = f"{direction.upper()}_"
        suffix = "_MUN" if mun else ""
        dir_name = f"{direction}-mun" if mun else direction
        filename = f"{prefix}{year}{suffix}.csv"
        
        return self.storage.path_for(f"{dir_name}/{filename}")

    def path_trade_nbm(self, direction: str, year: int) -> Path:
        """Generate path for NBM trade data file."""
        direction = direction.lower()
        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction}")

        prefix = f"{direction.upper()}_"
        dir_name = f"{direction}-nbm"
        filename = f"{prefix}{year}_NBM.csv"
        
        return self.storage.path_for(f"{dir_name}/{filename}")

    def path_trade_completa(self, direction: str, mun: bool = False) -> Path:
        """Generate path for complete trade data file."""
        direction = direction.lower()
        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction}")

        prefix = f"{direction.upper()}_"
        suffix = "_MUN" if mun else ""
        dir_name = f"{direction}-mun" if mun else direction
        filename = f"{prefix}COMPLETA{suffix}.csv"
        
        return self.storage.path_for(f"{dir_name}/{filename}")


def path_aux(root: Path | str, name: str) -> Path:
    """Generate path for auxiliary table file."""
    return DataRepository(root).path_aux(name)


def path_trade(root: Path | str, direction: str, year: int, mun: bool = False) -> Path:
    """Generate path for trade data file (NCM classification)."""
    return DataRepository(root).path_trade(direction, year, mun)


def path_trade_nbm(root: Path | str, direction: str, year: int) -> Path:
    """Generate path for NBM trade data file."""
    return DataRepository(root).path_trade_nbm(direction, year)


def path_trade_completa(root: Path | str, direction: str, mun: bool = False) -> Path:
    """Generate path for complete trade data file."""
    return DataRepository(root).path_trade_completa(direction, mun)

"""Functions to manage downloaded file locations and paths.

This module provides utilities for generating standardized file paths for
downloaded foreign trade data and auxiliary tables. It ensures consistent
organization of data files with proper directory structure and naming
conventions.

File organization:
- Trade data: Organized by direction (exp/imp) and year
- Municipality data: Separate subdirectories (exp-mun, imp-mun)
- NBM data: Separate subdirectories (exp-nbm, imp-nbm)
- Auxiliary tables: Single 'auxiliary-tables' directory
"""

from pathlib import Path
from comexdown.constants import TABLES


class DataRepository:
    """Class to manage data repository paths.

    This class encapsulates the root directory for data storage and provides
    methods to generate standardized file paths for various datasets.
    """

    def __init__(self, root: Path | str):
        """Initialize DataRepository with a root directory.

        Parameters
        ----------
        root : Path | str
            Root directory for data storage.
        """
        self.root = ensure_path(root)

    def path_aux(self, name: str) -> Path:
        """Generate path for auxiliary table file.

        Creates the standardized file path for an auxiliary code table based on
        its name and the root data directory.

        Parameters
        ----------
        name : str
            Name of the auxiliary table (e.g., 'ncm', 'pais', 'uf').

        Returns
        -------
        Path
            Full path to the auxiliary table file.

        Notes
        -----
        All auxiliary tables are stored in a 'auxiliary-tables' subdirectory
        under the root directory.
        """
        file_info = TABLES.get(name)
        if not file_info:
            raise ValueError(f"Unknown auxiliary table name: {name}")

        filename = file_info.get("file_ref")
        if not filename:
            raise ValueError(f"Auxiliary table '{name}' has no file reference")

        return self.root / "auxiliary-tables" / filename

    def path_trade(self, direction: str, year: int, mun: bool = False) -> Path:
        """Generate path for trade data file (NCM classification).

        Creates the standardized file path for trade transaction data files
        using the modern NCM product classification system (1997+).

        Parameters
        ----------
        direction : str
            Trade direction, either 'exp' (exports) or 'imp' (imports).
            Case insensitive.
        year : int
            Year of the trade data.
        mun : bool, optional
            If True, generates path for municipality-level data, by default False.

        Returns
        -------
        Path
            Full path to the trade data file.

        Raises
        ------
        ValueError
            If direction is not 'exp' or 'imp'.

        Notes
        -----
        File naming conventions:
        - National data: EXP_2020.csv or IMP_2020.csv
        - Municipality data: EXP_2020_MUN.csv or IMP_2020_MUN.csv

        Directory structure:
        - National data: root/exp/ or root/imp/
        - Municipality data: root/exp-mun/ or root/imp-mun/
        """
        direction = direction.lower()

        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction}")

        prefix = f"{direction.upper()}_"
        suffix = "_MUN" if mun else ""
        dir_name = f"{direction}-mun" if mun else direction

        filename = f"{prefix}{year}{suffix}.csv"
        return self.root / dir_name / filename

    def path_trade_nbm(self, direction: str, year: int) -> Path:
        """Generate path for NBM trade data file.

        Creates the standardized file path for historical trade transaction data
        files using the older NBM (Nomenclatura Brasileira de Mercadorias)
        product classification system (1989-1996).

        Parameters
        ----------
        direction : str
            Trade direction, either 'exp' (exports) or 'imp' (imports).
            Case insensitive.
        year : int
            Year of the trade data (should be between 1989-1996).

        Returns
        -------
        Path
            Full path to the NBM trade data file.

        Raises
        ------
        ValueError
            If direction is not 'exp' or 'imp'.

        Notes
        -----
        File naming convention: EXP_1995_NBM.csv or IMP_1995_NBM.csv
        Directory structure: root/exp-nbm/ or root/imp-nbm/
        NBM data does not include municipality-level breakdowns.
        """
        direction = direction.lower()

        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction}")

        prefix = f"{direction.upper()}_"
        dir_name = f"{direction}-nbm"

        filename = f"{prefix}{year}_NBM.csv"
        return self.root / dir_name / filename

    def path_trade_completa(self, direction: str, mun: bool = False) -> Path:
        """Generate path for complete trade data file.

        Creates the standardized file path for the complete trade transaction
        dataset files, which include all years of data in a single file.

        Parameters
        ----------
        direction : str
            Trade direction, either 'exp' (exports) or 'imp' (imports).
            Case insensitive.
        mun : bool, optional
            If True, generates path for municipality-level data, by default False.

        Returns
        -------
        Path
            Full path to the complete trade data file.

        Raises
        ------
        ValueError
            If direction is not 'exp' or 'imp'.

        Notes
        -----
        File naming conventions:
        - National data: EXP_COMPLETA.csv or IMP_COMPLETA.csv
        - Municipality data: EXP_COMPLETA_MUN.csv or IMP_COMPLETA_MUN.csv

        Directory structure:
        - National data: root/exp/ or root/imp/
        - Municipality data: root/exp-mun/ or root/imp-mun/
        """
        direction = direction.lower()

        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction}")

        prefix = f"{direction.upper()}_"
        suffix = "_MUN" if mun else ""
        dir_name = f"{direction}-mun" if mun else direction

        filename = f"{prefix}COMPLETA{suffix}.csv"
        return self.root / dir_name / filename


def ensure_path(path: Path | str) -> Path:
    """Ensure the input is a Path object.

    Converts string paths to Path objects, or returns Path objects unchanged.

    Parameters
    ----------
    path : Path | str
        Input path as either a string or Path object.

    Returns
    -------
    Path
        Path object representation of the input.
    """
    return Path(path) if isinstance(path, str) else path


def get_creation_time(path: Path) -> float:
    """Get the creation time of a file.

    Parameters
    ----------
    path : Path
        Path to the file.

    Returns
    -------
    float
        File creation timestamp as seconds since epoch.

    Notes
    -----
    On Unix systems, this may return the time of the last metadata change
    rather than creation time, depending on the filesystem.
    """
    return path.stat().st_ctime

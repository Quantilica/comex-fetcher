"""Functions to manage downloaded file locations and paths.

Filenames follow the ecosystem convention:
    {dataset}_{partition}@{YYYYMMDD}.{ext}

where ``@YYYYMMDD`` is the server's Last-Modified date.  When the date is
unknown the ``@`` suffix is omitted and the legacy bare name is used.
"""

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica.core.storage import (
    BaseDataRepository,
    build_stamped_filename,
    stamp_filename,
)

from comex_fetcher.constants import TABLES


class DataRepository(BaseDataRepository):
    """Manages local storage for comex-fetcher files."""

    def __init__(self, root: Path | str):
        """Initializes DataRepository.

        Args:
            root (Path | str): The root directory for storage.
        """
        super().__init__(root)

    # ------------------------------------------------------------------
    # Auxiliary tables
    # ------------------------------------------------------------------

    def path_aux(
        self,
        name: str,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for an auxiliary code table file.

        Example: ``auxiliary-tables/ncm@20240315.csv``

        Args:
            name (str): The name of the auxiliary table.
            last_modified (dt.date | None): The last modified date to stamp.
                Defaults to None.

        Returns:
            Path: The generated path for the auxiliary table.

        Raises:
            ValueError: If the auxiliary table name is unknown.
        """
        timestamp = last_modified or dt.date.today()
        file_info = TABLES.get(name)
        if not file_info:
            raise ValueError(f"Unknown auxiliary table name: {name}")
        ext = file_info["file_ref"].rsplit(".", 1)[-1].lower()
        filename = stamp_filename(name, ext, timestamp)
        return self.storage.path_for(f"auxiliary-tables/{filename}")

    def path_other(
        self,
        name: str,
        ext: str,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for miscellaneous auxiliary files (e.g. tabelas-auxiliares).

        Example: ``auxiliary-tables/tabelas-auxiliares@20240315.xlsx``

        Args:
            name (str): The name of the miscellaneous file.
            ext (str): The file extension.
            last_modified (dt.date | None): The last modified date to stamp.
                Defaults to None.

        Returns:
            Path: The generated path for the miscellaneous file.
        """
        timestamp = last_modified or dt.date.today()
        filename = stamp_filename(name, ext, timestamp)
        return self.storage.path_for(f"auxiliary-tables/{filename}")

    # ------------------------------------------------------------------
    # Trade data (NCM)
    # ------------------------------------------------------------------

    def path_trade(
        self,
        direction: str,
        year: int,
        mun: bool = False,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for a trade data file (NCM classification).

        Examples:
            ``exp/exp_2023@20240315.csv``
            ``exp-mun/exp-mun_2023@20240315.csv``

        Args:
            direction (str): The direction of trade ('exp' or 'imp').
            year (int): The year of the data.
            mun (bool): Whether to get municipal-level data. Defaults to False.
            last_modified (dt.date | None): The last modified date to stamp.
                Defaults to None.

        Returns:
            Path: The generated path for the trade data file.

        Raises:
            ValueError: If the direction is invalid.
        """
        timestamp = last_modified or dt.date.today()
        direction = direction.lower()
        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction!r}")
        dataset = f"{direction}-mun" if mun else direction
        filename = build_stamped_filename(dataset, year, ext="csv", timestamp=timestamp)
        return self.storage.path_for(f"{dataset}/{filename}")

    def path_trade_nbm(
        self,
        direction: str,
        year: int,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for an NBM trade data file (1989–1996).

        Example: ``exp-nbm/exp-nbm_1994@20240315.csv``

        Args:
            direction (str): The direction of trade ('exp' or 'imp').
            year (int): The year of the data.
            last_modified (dt.date | None): The last modified date to stamp.
                Defaults to None.

        Returns:
            Path: The generated path for the NBM trade data file.

        Raises:
            ValueError: If the direction is invalid.
        """
        timestamp = last_modified or dt.date.today()
        direction = direction.lower()
        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction!r}")
        dataset = f"{direction}-nbm"
        filename = build_stamped_filename(dataset, year, ext="csv", timestamp=timestamp)
        return self.storage.path_for(f"{dataset}/{filename}")

    # ------------------------------------------------------------------
    # REPETRO and validation
    # ------------------------------------------------------------------

    def path_repetro(
        self,
        dataset: str,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for a REPETRO file.

        Example: ``repetro/exp-repetro@20240315.xlsx``

        Args:
            dataset (str): The name of the REPETRO dataset.
            last_modified (dt.date | None): The last modified date to stamp.
                Defaults to None.

        Returns:
            Path: The generated path for the REPETRO file.
        """
        timestamp = last_modified or dt.date.today()
        filename = stamp_filename(dataset, "xlsx", timestamp)
        return self.storage.path_for(f"repetro/{filename}")

    def path_validacao(
        self,
        dataset: str,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for a validation totals file.

        Example: ``validacao/exp-validacao@20240315.csv``

        Args:
            dataset (str): The name of the validation dataset.
            last_modified (dt.date | None): The last modified date to stamp.
                Defaults to None.

        Returns:
            Path: The generated path for the validation totals file.
        """
        timestamp = last_modified or dt.date.today()
        filename = stamp_filename(dataset, "csv", timestamp)
        return self.storage.path_for(f"validacao/{filename}")

    def path_for_entry(
        self,
        entry: dict[str, Any],
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Route entry to the correct path generator based on its properties.

        Args:
            entry (dict[str, Any]): The dataset entry dictionary.
            last_modified (dt.date | None): The last modified date to stamp.
                Defaults to None.

        Returns:
            Path: The generated path for the dataset entry.

        Raises:
            ValueError: If unable to build a path for the given entry.
        """
        timestamp = last_modified or dt.date.today()
        if entry.get("is_trade"):
            if entry.get("nbm"):
                return self.path_trade_nbm(
                    direction=entry["direction"],
                    year=entry["year"],
                    last_modified=timestamp,
                )
            return self.path_trade(
                direction=entry["direction"],
                year=entry["year"],
                mun=entry.get("mun", False),
                last_modified=timestamp,
            )

        if entry.get("is_table"):
            group = entry.get("table_group")
            if group == "auxiliary":
                return self.path_aux(entry["id"], last_modified=timestamp)
            elif group == "repetro":
                return self.path_repetro(entry["id"], last_modified=timestamp)
            elif group == "validation":
                return self.path_validacao(entry["id"], last_modified=timestamp)
            elif group == "other":
                return self.path_other(
                    entry["id"], entry["ext"], last_modified=timestamp
                )

        raise ValueError(f"Unable to build path for entry: {entry}")

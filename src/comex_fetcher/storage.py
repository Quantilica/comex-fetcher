"""Functions to manage downloaded file locations and paths.

Filenames follow the ecosystem convention:
    {dataset}_{partition}@{YYYYMMDD}.{ext}

where ``@YYYYMMDD`` is the server's Last-Modified date.  When the date is
unknown the ``@`` suffix is omitted and the legacy bare name is used.
"""

import datetime as dt
from pathlib import Path

from quantilica_core.storage import BaseDataRepository, stamp_filename

from comex_fetcher.constants import TABLES


class DataRepository(BaseDataRepository):
    """Manages local storage for comex-fetcher files."""

    def __init__(self, root: Path | str):
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
        """
        file_info = TABLES.get(name)
        if not file_info:
            raise ValueError(f"Unknown auxiliary table name: {name}")
        ext = file_info["file_ref"].rsplit(".", 1)[-1].lower()
        filename = stamp_filename(name, ext, last_modified)
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
        """
        filename = stamp_filename(name, ext, last_modified)
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
        """
        direction = direction.lower()
        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction!r}")
        dataset = f"{direction}-mun" if mun else direction
        filename = stamp_filename(f"{dataset}_{year}", "csv", last_modified)
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
        """
        direction = direction.lower()
        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction!r}")
        dataset = f"{direction}-nbm"
        filename = stamp_filename(f"{dataset}_{year}", "csv", last_modified)
        return self.storage.path_for(f"{dataset}/{filename}")

    def path_trade_completa(
        self,
        direction: str,
        mun: bool = False,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for a complete historical trade data archive.

        Examples:
            ``exp/exp_completa@20240315.zip``
            ``exp-mun/exp-mun_completa@20240315.zip``
        """
        direction = direction.lower()
        if direction not in ("exp", "imp"):
            raise ValueError(f"Invalid argument direction={direction!r}")
        dataset = f"{direction}-mun" if mun else direction
        filename = stamp_filename(f"{dataset}_completa", "zip", last_modified)
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
        """
        filename = stamp_filename(dataset, "xlsx", last_modified)
        return self.storage.path_for(f"repetro/{filename}")

    def path_validacao(
        self,
        dataset: str,
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Path for a validation totals file.

        Example: ``validacao/exp-validacao@20240315.csv``
        """
        filename = stamp_filename(dataset, "csv", last_modified)
        return self.storage.path_for(f"validacao/{filename}")

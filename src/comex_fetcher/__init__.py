from quantilica_core.logging import get_logger

"""Brazil's foreign trade data downloader"""

from pathlib import Path

__version__ = "1.5.2"

logger = get_logger(__name__)

from . import download, storage, urls


def get_year(data_dir: Path, year: int, exp=False, imp=False, mun=False):
    """Download trade data for a specific year."""
    if not exp and not imp:
        exp = imp = True
    directions = []
    if exp:
        directions.append("exp")
    if imp:
        directions.append("imp")

    repo = storage.DataRepository(root=data_dir)

    for direction in directions:
        url = urls.trade(direction=direction, year=year, mun=mun)
        file_path = repo.path_trade(direction=direction, year=year, mun=mun)
        download.download_file(url, file_path)


def get_year_nbm(data_dir: Path, year: int, exp=False, imp=False):
    """Download older trade data (NBM) for a specific year."""
    if not exp and not imp:
        exp = imp = True
    directions = []
    if exp:
        directions.append("exp")
    if imp:
        directions.append("imp")

    repo = storage.DataRepository(root=data_dir)

    for direction in directions:
        url = urls.trade(direction=direction, year=year, nbm=True)
        file_path = repo.path_trade_nbm(direction=direction, year=year)
        download.download_file(url, file_path)


def get_complete(data_dir: Path, exp=False, imp=False, mun=False):
    """Download complete historical trade data."""
    if not exp and not imp:
        exp = imp = True
    directions = []
    if exp:
        directions.append("exp")
    if imp:
        directions.append("imp")

    repo = storage.DataRepository(root=data_dir)

    for direction in directions:
        url = urls.complete(direction=direction, mun=mun)
        file_path = repo.path_trade_completa(direction=direction, mun=mun)
        download.download_file(url, file_path)


def get_table(data_dir: Path, table: str):
    """Download an auxiliary code table."""
    url = urls.table(table)
    repo = storage.DataRepository(root=data_dir)
    file_path = repo.path_aux(name=table)
    download.download_file(url, file_path)


def download_all(data_dir: Path):
    """Download all available datasets."""
    download.download_all(data_dir)

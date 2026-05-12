"""Brazil's foreign trade data downloader"""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from quantilica_core.logging import get_logger

try:
    __version__ = version("comex-fetcher")
except PackageNotFoundError:
    __version__ = "0.0.0"

logger = get_logger(__name__)

from . import download, storage, urls


def get_year(
    data_dir: Path,
    year: int,
    exp=False,
    imp=False,
    mun=False,
    show_progress: bool = False,
):
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
        date = download._safe_head_date(url)
        file_path = repo.path_trade(direction=direction, year=year, mun=mun, last_modified=date)
        download.download_file(url, file_path, show_progress=show_progress)


def get_year_nbm(
    data_dir: Path,
    year: int,
    exp=False,
    imp=False,
    show_progress: bool = False,
):
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
        date = download._safe_head_date(url)
        file_path = repo.path_trade_nbm(direction=direction, year=year, last_modified=date)
        download.download_file(url, file_path, show_progress=show_progress)


def get_complete(
    data_dir: Path,
    exp=False,
    imp=False,
    mun=False,
    show_progress: bool = False,
):
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
        date = download._safe_head_date(url)
        file_path = repo.path_trade_completa(direction=direction, mun=mun, last_modified=date)
        download.download_file(url, file_path, show_progress=show_progress)


def get_table(data_dir: Path, table: str, show_progress: bool = False):
    """Download an auxiliary code table."""
    url = urls.table(table)
    repo = storage.DataRepository(root=data_dir)
    date = download._safe_head_date(url)
    file_path = repo.path_aux(name=table, last_modified=date)
    download.download_file(url, file_path, show_progress=show_progress)


def download_all(data_dir: Path, show_progress: bool = True):
    """Download all available datasets."""
    download.download_all(data_dir, show_progress=show_progress)

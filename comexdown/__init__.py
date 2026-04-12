"""Brazil's foreign trade data downloader"""

from pathlib import Path

import requests

from . import download, storage, urls

__version__ = "1.5.2"


def get_year(data_dir: Path, year: int, exp=False, imp=False, mun=False):
    """Download trade data

    Parameters
    ----------
    data_dir : Path
        Destination path to save downloaded data.
    year : int
        Year to download
    exp : bool, optional
        If True, download exports data.
    imp : bool, optional
        If True, download imports data.
    mun : bool, optional
        If True, download municipality data.
    """
    directions = []
    if exp:
        directions.append("exp")
    if imp:
        directions.append("imp")

    repo = storage.DataRepository(root=data_dir)

    with requests.Session() as client:
        for direction in directions:
            url = urls.trade(direction=direction, year=year, mun=mun)
            file_path = repo.path_trade(direction=direction, year=year, mun=mun)
            download.download_file(url, file_path, client=client)


def get_year_nbm(data_dir: Path, year: int, exp=False, imp=False):
    """Download older trade data (NBM)

    Parameters
    ----------
    data_dir : Path
        Destination path to save downloaded data.
    year : int
        Year to download
    exp : bool, optional
        If True, download export data.
    imp : bool, optional
        If True, download import data.
    """
    directions = []
    if exp:
        directions.append("exp")
    if imp:
        directions.append("imp")

    repo = storage.DataRepository(root=data_dir)

    with requests.Session() as client:
        for direction in directions:
            url = urls.trade(direction=direction, year=year, nbm=True)
            file_path = repo.path_trade_nbm(direction=direction, year=year)
            download.download_file(url, file_path, client=client)


def get_complete(data_dir: Path, exp=False, imp=False, mun=False):
    """Download complete trade data

    Parameters
    ----------
    data_dir : Path
        Destination path to save downloaded data.
    exp : bool, optional
        If True, download complete export data.
    imp : bool, optional
        If True, download complete import data.
    mun : bool, optional
        If True, download complete municipality trade data.
    """
    directions = []
    if exp:
        directions.append("exp")
    if imp:
        directions.append("imp")

    repo = storage.DataRepository(root=data_dir)

    with requests.Session() as client:
        for direction in directions:
            url = urls.complete(direction=direction, mun=mun)
            file_path = repo.path_trade_completa(direction=direction, mun=mun)
            download.download_file(url, file_path, client=client)


def get_table(data_dir: Path, table: str):
    """Download auxiliary code tables

    Parameters
    ----------
    data_dir : Path
        Destination path to save downloaded code table directory.
    table : str
        Name of auxiliary code table to download
    """
    url = urls.table(table)
    repo = storage.DataRepository(root=data_dir)
    file_path = repo.path_aux(name=table)
    with requests.Session() as client:
        download.download_file(url, file_path, client=client)

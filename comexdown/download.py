"""Functions to download foreign trade data from remote servers.

This module provides functionality for downloading files from the Brazilian
government's foreign trade data servers. It includes features for:
- Progress tracking during downloads
- Automatic retry on failure
- File timestamp comparison to avoid redundant downloads
- Chunked streaming downloads for large files

The module disables SSL warnings for compatibility with government servers
that may have certificate issues.
"""

import datetime as dt
import sys
import time
from pathlib import Path
from typing import Any, Generator

import requests
import urllib3

from .constants import (
    AUX_TABLES,
    TRADE,
    TABLES,
    ARQUIVO_UNICO,
    REPETRO_TABLES,
    TOTAIS_PARA_VALIDACAO,
    OTHER_TABLES,
)
from .urls import get_url

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
CURRENT_DATE = dt.datetime.now()
CURRENT_YEAR = CURRENT_DATE.year


def remote_is_more_recent(headers: dict, dest: Path) -> bool:
    """Check if the remote file is more recent than the local file.

    Compares the Last-Modified header from a remote file with the modification
    time of a local file to determine if the remote version is newer.

    Parameters
    ----------
    headers : dict
        HTTP headers from the remote server response, should contain
        'Last-Modified' field in standard HTTP date format.
    dest : Path
        Path to the local file to compare against.

    Returns
    -------
    bool
        True if the remote file is more recent than the local file,
        False if the local file doesn't exist, the remote has no
        Last-Modified header, or the local file is up to date.

    Notes
    -----
    This function is used to avoid re-downloading files that haven't
    changed on the server, saving bandwidth and time.
    """
    if not dest.exists():
        return False

    last_modified = headers.get("Last-Modified")
    if last_modified:
        # Parse standard HTTP date format
        remote_mtime = time.mktime(
            time.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
        )
        if dest.stat().st_mtime < remote_mtime:
            return True

    return False


def _print_progress(
    downloaded: int,
    total: int,
    width: int = 50,
) -> None:
    """Print download progress bar to stdout.

    Displays a real-time progress bar showing download completion percentage
    and downloaded size in MiB.

    Parameters
    ----------
    downloaded : int
        Number of bytes downloaded so far.
    total : int
        Total file size in bytes. If 0 or None, progress bar is not shown.
    width : int, optional
        Width of the progress bar in characters, by default 50.

    Notes
    -----
    The progress bar is printed to stdout using carriage return to update
    in place. Format: [=====>-----] 45.2% (12.34 MiB)
    """
    if not total:
        return

    p = downloaded / total
    filled = int(p * width)
    bar = "=" * filled + "-" * (width - filled)
    size_mb = downloaded / (1024 * 1024)
    msg = f"\r[{bar}] {p:.1%} ({size_mb:.2f} MiB)"
    sys.stdout.write(msg)
    sys.stdout.flush()


def _download_stream(
    response: requests.Response,
    output: Path,
    blocksize: int,
) -> None:
    """Stream download content to file with progress tracking.

    Downloads a file in chunks, writing to disk incrementally while displaying
    progress information.

    Parameters
    ----------
    response : requests.Response
        Active HTTP response object with streaming enabled.
    output : Path
        Destination file path where content will be written.
    blocksize : int
        Size of chunks to download and write at a time, in bytes.

    Raises
    ------
    requests.HTTPError
        If the response status code indicates an error.

    Notes
    -----
    This function writes data to disk as it's downloaded rather than loading
    the entire file into memory, making it suitable for large files.
    """
    response.raise_for_status()
    total_length = int(response.headers.get("content-length", 0))

    downloaded_size = 0
    with open(output, "wb") as f:
        for chunk in response.iter_content(chunk_size=blocksize):
            if chunk:
                f.write(chunk)
                downloaded_size += len(chunk)
                _print_progress(downloaded_size, total_length)

    sys.stdout.write("\n")


def download_file(
    url: str,
    output: Path,
    client: requests.Session,
    retry: int = 3,
    blocksize: int = 8192,
    verify_ssl: bool = False,
) -> Path:
    """Download a file from a URL to a specific output path.

    Downloads a file with automatic retry on failure, progress tracking,
    and smart update detection. Creates parent directories as needed.
    Checks if local file is already up to date before downloading.

    Parameters
    ----------
    url : str
        Source URL of the file to download.
    output : Path
        Destination local path where the file will be saved.
    client : requests.Session
        HTTP session object for making requests.
    retry : int, optional
        Maximum number of download attempts, by default 3.
    blocksize : int, optional
        Size of chunks to download at a time in bytes, by default 8192.
    verify_ssl : bool, optional
        Whether to verify SSL certificates, by default False.
        Set to False for compatibility with some government servers.

    Returns
    -------
    Path
        The path to the downloaded file (same as output parameter).

    Raises
    ------
    requests.RequestException
        If all download attempts fail.

    Notes
    -----
    - Parent directories are created automatically if they don't exist
    - File is only downloaded if it doesn't exist locally or if the remote
      version is newer (based on Last-Modified header)
    - Uses a browser-like User-Agent header for compatibility
    - Retries with 2-second delay between attempts on failure
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
    }

    # Ensure parent directory exists
    output.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(retry):
        sys.stdout.write(f"Downloading: {url:<50} --> {output.name}\n")
        sys.stdout.flush()

        try:
            # Check for updates with HEAD request
            head_resp = client.head(url, headers=headers, timeout=10, verify=verify_ssl)

            # Check if local file is up to date (i.e. remote is NOT newer)
            cond = remote_is_more_recent(head_resp.headers, output)
            if output.exists() and not cond:
                sys.stdout.write(f"{output.name} is up to date.\n")
                sys.stdout.flush()
                return output

            # Perform the specific download
            with client.get(
                url,
                headers=headers,
                stream=True,
                timeout=30,
                verify=verify_ssl,
            ) as r:
                _download_stream(r, output, blocksize)

            return output

        except requests.RequestException as e:
            sys.stdout.write(f"\nError downloading {url}: {e}\n")
            if attempt < retry - 1:
                time.sleep(2)
            else:
                raise

    return output


def get_file_metadata(client: requests.Session, url: str) -> dict[str, Any]:
    """Returns the metadata of a file

    Parameters
    ----------
    url: str
        The file's URL
    """
    r = client.head(url, verify=False)
    file_size = int(r.headers.get("Content-Length", 0))
    default_last_modified_string = "Thu, 01 Jan 1970 00:00:00 GMT"
    last_modified = dt.datetime.strptime(
        r.headers.get("Last-Modified", default_last_modified_string),
        "%a, %d %b %Y %H:%M:%S %Z",
    )
    return {
        "size": file_size,
        "last_modified": last_modified,
    }


def get_links_metadata(
    client: requests.Session,
) -> Generator[dict[str, Any], None, None]:
    """Get metadata of all files to download"""

    for dataset in TRADE:
        start_year, end_year = TRADE[dataset]["year_range"]
        if not end_year:
            end_year = CURRENT_DATE.year
        for year in range(start_year, end_year + 1):
            url = get_url(dataset, year=year)
            link_metadata = get_file_metadata(client=client, url=url)
            link_metadata["partitions"] = [str(year)]
            yield link_metadata
    for dataset in TABLES.keys():
        url = get_url(dataset)
        link_metadata = get_file_metadata(client=client, url=url)
        link_metadata["dataset_grouping"] = ["tabelas"]
        yield link_metadata
    for dataset in REPETRO_TABLES.keys():
        url = get_url(dataset)
        link_metadata = get_file_metadata(client=client, url=url)
        link_metadata["dataset_grouping"] = ["repetro"]
        yield link_metadata
    for dataset in TOTAIS_PARA_VALIDACAO.keys():
        url = get_url(dataset)
        link_metadata = get_file_metadata(client=client, url=url)
        link_metadata["dataset_grouping"] = ["totais-para-validacao"]
        yield link_metadata
    for dataset in ARQUIVO_UNICO.keys():
        url = get_url(dataset)
        link_metadata = get_file_metadata(client=client, url=url)
        link_metadata["dataset_grouping"] = ["arquivo-unico"]
        yield link_metadata
    for dataset in OTHER_TABLES.keys():
        url = get_url(dataset)
        link_metadata = get_file_metadata(client=client, url=url)
        yield link_metadata


def fetch_table(table_name: str, data_dir: Path, client: requests.Session):
    """Downloads a table

    Parameters
    ----------
    table_name: str
        The name of the table to download
    data_dir: Path
        The data directory path of downloaded file
    """
    url = get_url(table_name)
    metadata = get_file_metadata(client=client, url=url)
    filepath = get_table_filepath(
        data_dir=data_dir,
        table_name=table_name,
        modified=metadata["last_modified"],
        file_extension="csv",
    )
    if filepath.exists():
        return
    download_file(url, filepath, client)


def fetch_tabelas_auxiliares(data_dir: Path, client: requests.Session):
    """Downloads tabelas-auxiliares file

    Parameters
    ----------
    data_dir: Path
        Destination path directory to save file
    """
    url = get_url("tabelas-auxiliares")
    metadata = get_file_metadata(client=client, url=url)
    filepath = get_table_filepath(
        data_dir=data_dir,
        table_name="tabelas-auxiliares",
        modified=metadata["last_modified"],
        file_extension="xlsx",
    )
    if filepath.exists():
        return
    download_file(url, filepath, client)


def fetch_trade(data_dir: Path, dataset: str, year: int, client: requests.Session):
    url = get_url(table=dataset, year=year)
    metadata = get_file_metadata(client=client, url=url)
    filepath = get_trade_filepath(
        data_dir=data_dir,
        dataset=dataset,
        year=year,
        modified=metadata["last_modified"],
    )
    if filepath.exists():
        return
    download_file(url, filepath, client)


def fetch_trade_unique(data_dir: Path, dataset: str, client: requests.Session):
    """Downloads the file with complete data

    Parameters
    ----------
    data_dir : Path
        Destination path directory to save file
    """
    url = get_url(dataset)
    metadata = get_file_metadata(client=client, url=url)
    if dataset in TOTAIS_PARA_VALIDACAO:
        file_extension = "csv"
    elif dataset in ARQUIVO_UNICO:
        file_extension = "zip"
    filepath = get_trade_unique_filepath(
        data_dir=data_dir,
        dataset=dataset,
        modified=metadata["last_modified"],
        file_extension=file_extension,
    )
    if filepath.exists():
        return
    download_file(url, filepath, client)


def fetch_repetro(data_dir: Path, dataset: str, client: requests.Session):
    """Downloads the file with complete data of repetro

    Parameters
    ----------
    data_dir : Path
        Destination path directory to save file
    """
    url = get_url(dataset)
    metadata = get_file_metadata(client=client, url=url)
    filepath = get_table_filepath(
        data_dir=data_dir,
        table_name=dataset,
        modified=metadata["last_modified"],
        file_extension="xlsx",
    )
    if filepath.exists():
        return
    download_file(url, filepath, client)


def download_tables(data_dir: Path, client: requests.Session):
    for table in AUX_TABLES:
        fetch_table(table, data_dir, client)
    fetch_tabelas_auxiliares(data_dir, client)


def download_trade(data_dir: Path, client: requests.Session):
    for dataset in TRADE:
        start_year, end_year = TRADE[dataset]["year_range"]
        if end_year is None:
            end_year = CURRENT_YEAR
        for year in range(start_year, end_year + 1):
            fetch_trade(
                data_dir=data_dir,
                dataset=dataset,
                year=year,
                client=client,
            )


def download_trade_completa(data_dir: Path, client: requests.Session):
    for dataset in ARQUIVO_UNICO:
        fetch_trade_unique(data_dir=data_dir, dataset=dataset, client=client)


def download_trade_validacao(data_dir: Path, client: requests.Session):
    for dataset in TOTAIS_PARA_VALIDACAO:
        fetch_trade_unique(data_dir=data_dir, dataset=dataset, client=client)


def download_repetro(data_dir: Path, client: requests.Session):
    for dataset in REPETRO_TABLES:
        fetch_repetro(data_dir=data_dir, dataset=dataset, client=client)


def download_all(data_dir: Path, client: requests.Session):
    download_tables(data_dir, client)
    download_trade(data_dir, client)
    download_repetro(data_dir, client)
    download_trade_validacao(data_dir, client)
    download_trade_completa(data_dir, client)

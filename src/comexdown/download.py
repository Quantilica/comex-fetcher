"""Functions to download foreign trade data from remote servers.

This module provides functionality for downloading files from the Brazilian
government's foreign trade data servers using only the standard library.
"""

import datetime as dt
import http.client
import os
import ssl
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

from .constants import (
    ARQUIVO_UNICO,
    OTHER_TABLES,
    REPETRO_TABLES,
    TABLES,
    TOTAIS_PARA_VALIDACAO,
    TRADE,
)
from .urls import get_url

# Create an unverified SSL context for government servers with certificate issues
SSL_CONTEXT = ssl._create_unverified_context()

CURRENT_DATE = dt.datetime.now()
CURRENT_YEAR = CURRENT_DATE.year


def remote_is_more_recent(headers: http.client.HTTPMessage, dest: Path) -> bool:
    """Check if the remote file is more recent than the local file."""
    if not dest.exists():
        return True

    last_modified = headers.get("Last-Modified")
    if last_modified:
        try:
            # Parse standard HTTP date format
            remote_mtime = time.mktime(
                time.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
            )
            if dest.stat().st_mtime < remote_mtime:
                return True
        except (ValueError, OSError):
            return False

    return False


def _print_progress(
    downloaded: int,
    total: int,
    width: int = 50,
) -> None:
    """Print download progress bar to stdout."""
    if not total:
        return

    p = downloaded / total
    filled = int(p * width)
    bar = "=" * filled + "-" * (width - filled)
    size_mb = downloaded / (1024 * 1024)
    msg = f"\r[{bar}] {p:.1%} ({size_mb:.2f} MiB)"
    sys.stdout.write(msg)
    sys.stdout.flush()


def download_file(
    url: str,
    output: Path,
    retry: int = 3,
    blocksize: int = 8192,
) -> Path:
    """Download a file from a URL to a specific output path using urllib."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output.with_suffix(output.suffix + ".tmp")

    for attempt in range(retry):
        sys.stdout.write(f"Downloading: {url:<50} --> {output.name}\n")
        sys.stdout.flush()

        try:
            # HEAD request to check if update is needed
            req_head = urllib.request.Request(url, headers=headers, method="HEAD")
            with urllib.request.urlopen(req_head, context=SSL_CONTEXT, timeout=10) as resp:
                if output.exists() and not remote_is_more_recent(resp.headers, output):
                    sys.stdout.write(f"{output.name} is up to date.\n")
                    return output
                total_length = int(resp.headers.get("Content-Length", 0))

            # GET request for actual download
            req_get = urllib.request.Request(url, headers=headers)
            downloaded_size = 0
            with urllib.request.urlopen(req_get, context=SSL_CONTEXT, timeout=30) as resp:
                with open(temp_output, "wb") as f:
                    while True:
                        chunk = resp.read(blocksize)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        _print_progress(downloaded_size, total_length)

            sys.stdout.write("\n")

            if total_length > 0 and downloaded_size != total_length:
                raise OSError(f"Incomplete download: {downloaded_size}/{total_length}")

            # Atomic replace
            if os.path.exists(output):
                os.remove(output)
            os.rename(temp_output, output)

            # Set mtime from Last-Modified if available
            last_modified = resp.headers.get("Last-Modified")
            if last_modified:
                remote_mtime = time.mktime(
                    time.strptime(last_modified, "%a, %d %b %Y %H:%M:%S %Z")
                )
                os.utime(output, (time.time(), remote_mtime))

            return output

        except Exception as e:
            sys.stdout.write(f"\nError downloading {url}: {e}\n")
            if temp_output.exists():
                temp_output.unlink()

            if attempt < retry - 1:
                sleep_time = 2 ** attempt
                sys.stdout.write(f"Retrying in {sleep_time} seconds...\n")
                time.sleep(sleep_time)
            else:
                raise

    return output


def get_file_metadata(url: str, timeout: int = 30) -> dict[str, Any]:
    """Returns metadata using HEAD request."""
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers, method="HEAD")
    try:
        with urllib.request.urlopen(req, context=SSL_CONTEXT, timeout=timeout) as resp:
            size = int(resp.headers.get("Content-Length", 0))
            last_modified_str = resp.headers.get("Last-Modified")
            if last_modified_str:
                last_modified = dt.datetime.strptime(
                    last_modified_str, "%a, %d %b %Y %H:%M:%S %Z"
                )
            else:
                last_modified = dt.datetime(1970, 1, 1)
            return {"size": size, "last_modified": last_modified}
    except Exception as e:
        sys.stdout.write(f"Warning: Could not fetch metadata for {url}: {e}\n")
        return {"size": 0, "last_modified": dt.datetime(1970, 1, 1)}


def download_all(data_dir: Path):
    """Download everything from all datasets."""
    from .storage import DataRepository

    repo = DataRepository(data_dir)

    # 1. Auxiliary Tables
    for table_name in TABLES:
        url = get_url(table_name)
        dest = repo.path_aux(table_name)
        download_file(url, dest)

    # 2. Trade Data
    for dataset in TRADE:
        start_year, end_year = TRADE[dataset]["year_range"]
        if end_year is None:
            end_year = CURRENT_YEAR
        for year in range(start_year, end_year + 1):
            url = get_url(dataset, year=year)
            # Use appropriate repo path method based on dataset type
            if "mun" in dataset:
                dest = repo.path_trade(dataset.split("-")[0], year, mun=True)
            elif "nbm" in dataset:
                dest = repo.path_trade_nbm(dataset.split("-")[0], year)
            else:
                dest = repo.path_trade(dataset, year)
            download_file(url, dest)

    # 3. Complete Files
    for dataset in ARQUIVO_UNICO:
        url = get_url(dataset)
        # We might need a path_trade_completa for mun too
        direction = dataset.split("-")[0]
        mun = "mun" in dataset
        dest = repo.path_trade_completa(direction, mun=mun)
        download_file(url, dest)

    # 4. REPETRO
    for dataset in REPETRO_TABLES:
        url = get_url(dataset)
        # Add path for REPETRO in storage.py if needed, for now use a default
        dest = data_dir / "repetro" / REPETRO_TABLES[dataset]["server_filename"]
        download_file(url, dest)

    # 5. Validation
    for dataset in TOTAIS_PARA_VALIDACAO:
        url = get_url(dataset)
        dest = data_dir / "validacao" / TOTAIS_PARA_VALIDACAO[dataset]["server_filename"]
        download_file(url, dest)

    # 6. Other
    url = get_url("tabelas-auxiliares")
    dest = data_dir / "auxiliary-tables" / OTHER_TABLES["tabelas-auxiliares"]["server_filename"]
    download_file(url, dest)

"""Functions to download foreign trade data from remote servers.

This module provides functionality for downloading files from the Brazilian
government's foreign trade data servers.
"""

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica_core.http import HttpClient
import quantilica_core.metadata as core_meta

from . import logger
from .constants import (
    ARQUIVO_UNICO,
    OTHER_TABLES,
    REPETRO_TABLES,
    TABLES,
    TOTAIS_PARA_VALIDACAO,
    TRADE,
)
from .urls import get_url

CURRENT_DATE = dt.datetime.now()
CURRENT_YEAR = CURRENT_DATE.year

# Global client for comexdown
client = HttpClient(
    timeout=60.0,
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
    }
)


def download_file(
    url: str,
    output: Path,
    retry: int = 3,
    blocksize: int = 8192,
) -> Path:
    """Download a file from a URL to a specific output path using HttpClient.
    
    Uses quantilica-core for freshness check, atomic write, and manifest.
    """
    # Note: blocksize is currently ignored by HttpClient.download_with_manifest
    # which uses a default chunk size for hashing and httpx for downloading.
    
    # Temporarily adjust client attempts if retry is different from default
    original_attempts = client.attempts
    if retry != original_attempts:
        client.attempts = retry
        
    try:
        dataset_id = output.parent.name
        return client.download_with_manifest(
            url,
            output,
            source_id="comexstat",
            dataset_id=dataset_id,
            producer="comexdown",
        )
    finally:
        client.attempts = original_attempts


def get_file_metadata(url: str, timeout: int = 30) -> dict[str, Any]:
    """Returns metadata using HEAD request."""
    try:
        resp = client.head(url)
        size = int(resp.headers.get("Content-Length", 0))
        last_modified_str = resp.headers.get("Last-Modified")
        if last_modified_str:
            import email.utils
            last_modified = email.utils.parsedate_to_datetime(last_modified_str)
        else:
            last_modified = dt.datetime(1970, 1, 1, tzinfo=dt.UTC)
        return {"size": size, "last_modified": last_modified}
    except Exception as e:
        logger.warning(f"Could not fetch metadata for {url}: {e}")
        return {"size": 0, "last_modified": dt.datetime(1970, 1, 1, tzinfo=dt.UTC)}


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
        direction = dataset.split("-")[0]
        mun = "mun" in dataset
        dest = repo.path_trade_completa(direction, mun=mun)
        download_file(url, dest)

    # 4. REPETRO
    for dataset in REPETRO_TABLES:
        url = get_url(dataset)
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


def generate_catalog(downloaded_files: list[Path]) -> core_meta.MetadataCatalog:
    """Generate a validated MetadataCatalog from a list of downloaded file paths."""
    source_id = "comexstat"
    source = core_meta.Source(
        id=source_id,
        name="Comex Stat - Ministério do Desenvolvimento, Indústria, Comércio e Serviços",
        homepage_url="http://comexstat.mdic.gov.br",
    )

    datasets_map = {}
    resources = []
    
    for file_path in downloaded_files:
        # Determine dataset from parent directory name
        dataset_id = file_path.parent.name
        if dataset_id not in datasets_map:
            datasets_map[dataset_id] = core_meta.Dataset(
                id=dataset_id,
                source_id=source_id,
                name=dataset_id.upper().replace("-", " "),
            )
            
        filename = file_path.name
        resource_id = filename.replace(".", "_")
        
        resources.append(
            core_meta.Resource(
                id=resource_id,
                dataset_id=dataset_id,
                name=filename,
                format="csv" if filename.endswith(".csv") else None,
                path=str(file_path.absolute()),
            )
        )
        
    catalog = core_meta.MetadataCatalog(
        sources=[source],
        datasets=list(datasets_map.values()),
        resources=resources,
    )
    catalog.validate_references()
    return catalog

"""Functions to download foreign trade data from remote servers.

This module provides functionality for downloading files from the Brazilian
government's foreign trade data servers.
"""

import contextlib
import datetime as dt
from pathlib import Path

from quantilica_core.http import HttpClient
import quantilica_core.metadata as core_meta
from quantilica_core.progress import batch_progress, file_progress

from . import logger
from .constants import (
    ARQUIVO_UNICO,
    REPETRO_TABLES,
    TABLES,
    TOTAIS_PARA_VALIDACAO,
    TRADE,
)
from .urls import get_url

CURRENT_DATE = dt.datetime.now()
CURRENT_YEAR = CURRENT_DATE.year

# Global client for comex-fetcher
client = HttpClient(
    timeout=60.0,
    verify=False,  # balanca.economia.gov.br has SSL certificate issues
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
    show_progress: bool = False,
) -> Path:
    """Download a file from a URL to a specific output path using HttpClient.

    Uses quantilica-core for freshness check, atomic write, and manifest.
    """
    original_attempts = client.attempts
    if retry != original_attempts:
        client.attempts = retry

    try:
        dataset_id = output.parent.name
        if show_progress:
            with file_progress(output.name) as progress_cb:
                return client.download_with_manifest(
                    url,
                    output,
                    source_id="comexstat",
                    dataset_id=dataset_id,
                    producer="comex-fetcher",
                    progress=progress_cb,
                )
        return client.download_with_manifest(
            url,
            output,
            source_id="comexstat",
            dataset_id=dataset_id,
            producer="comex-fetcher",
        )
    finally:
        client.attempts = original_attempts


def _safe_head_date(url: str) -> dt.date | None:
    """Return the Last-Modified date from a HEAD request, or None on failure."""
    try:
        meta = client.head_metadata(url)
        lm = meta.get("last_modified")
        return lm.date() if lm else None
    except Exception as e:
        logger.warning(f"Could not fetch metadata for {url}: {e}")
        return None


def _count_download_all_files() -> int:
    """Count total files that download_all() will attempt to download."""
    count = len(TABLES)
    for dataset in TRADE:
        start_year, end_year = TRADE[dataset]["year_range"]
        if end_year is None:
            end_year = CURRENT_YEAR
        count += end_year - start_year + 1
    count += len(ARQUIVO_UNICO)
    count += len(REPETRO_TABLES)
    count += len(TOTAIS_PARA_VALIDACAO)
    count += 1  # tabelas-auxiliares
    return count


def download_all(data_dir: Path, show_progress: bool = True):
    """Download everything from all datasets."""
    from .storage import DataRepository

    repo = DataRepository(data_dir)
    total = _count_download_all_files()
    outer = (
        batch_progress("comex-fetcher", total=total)
        if show_progress
        else contextlib.nullcontext()
    )

    with outer as batch_pbar:
        # 1. Auxiliary Tables
        for table_name in TABLES:
            url = get_url(table_name)
            date = _safe_head_date(url)
            dest = repo.path_aux(table_name, last_modified=date)
            download_file(url, dest, show_progress=show_progress)
            if show_progress:
                batch_pbar.update(1)

        # 2. Trade Data
        for dataset in TRADE:
            start_year, end_year = TRADE[dataset]["year_range"]
            if end_year is None:
                end_year = CURRENT_YEAR
            for year in range(start_year, end_year + 1):
                url = get_url(dataset, year=year)
                date = _safe_head_date(url)
                if "mun" in dataset:
                    dest = repo.path_trade(dataset.split("-")[0], year, mun=True, last_modified=date)
                elif "nbm" in dataset:
                    dest = repo.path_trade_nbm(dataset.split("-")[0], year, last_modified=date)
                else:
                    dest = repo.path_trade(dataset, year, last_modified=date)
                download_file(url, dest, show_progress=show_progress)
                if show_progress:
                    batch_pbar.update(1)

        # 3. Complete Files
        for dataset in ARQUIVO_UNICO:
            url = get_url(dataset)
            date = _safe_head_date(url)
            direction = dataset.split("-")[0]
            mun = "mun" in dataset
            dest = repo.path_trade_completa(direction, mun=mun, last_modified=date)
            download_file(url, dest, show_progress=show_progress)
            if show_progress:
                batch_pbar.update(1)

        # 4. REPETRO
        for dataset in REPETRO_TABLES:
            url = get_url(dataset)
            date = _safe_head_date(url)
            dest = repo.path_repetro(dataset, last_modified=date)
            download_file(url, dest, show_progress=show_progress)
            if show_progress:
                batch_pbar.update(1)

        # 5. Validation
        for dataset in TOTAIS_PARA_VALIDACAO:
            url = get_url(dataset)
            date = _safe_head_date(url)
            dest = repo.path_validacao(dataset, last_modified=date)
            download_file(url, dest, show_progress=show_progress)
            if show_progress:
                batch_pbar.update(1)

        # 6. Other
        url = get_url("tabelas-auxiliares")
        date = _safe_head_date(url)
        dest = repo.path_other("tabelas-auxiliares", "xlsx", last_modified=date)
        download_file(url, dest, show_progress=show_progress)
        if show_progress:
            batch_pbar.update(1)


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

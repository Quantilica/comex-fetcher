"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica.cli.sdk import FetcherApp
from quantilica.core.storage import expected_format_for_path
from quantilica.core.sync import FreshnessPolicy

from .catalog import GROUP_ALIASES, GROUPS, list_datasets
from .payload import guard_for
from .storage import DataRepository


def path_builder(
    output_dir: Path, entry: dict[str, Any], last_modified: dt.date | None
) -> Path:
    """Builds the file path for a downloaded dataset.

    Args:
        output_dir (Path): The root output directory.
        entry (dict[str, Any]): The dataset entry dictionary.
        last_modified (dt.date | None): The last modified date of the dataset.

    Returns:
        Path: The generated file path.
    """
    return DataRepository(output_dir).path_for_entry(entry, last_modified=last_modified)


class ComexFetcherApp(FetcherApp):
    """``FetcherApp`` que barra no ``sync`` o soft-206 do MDIC (PHP/HTML com 206).

    O download passa a validar a primeira linha útil do CSV/JSON (``expect_header``)
    antes do ``os.replace``; o NCM do Siscomex, sem Last-Modified/ETag, é
    deduplicado por sha256 para não gerar uma versão nova por dia.
    """

    def _download_file(  # type: ignore[override]
        self,
        url: str,
        output: Path,
        progress: Any = None,
        *,
        force: bool = False,
        dataset_id: str | None = None,
        expected_format: str | None = None,
    ) -> Path:
        extra: dict[str, Any] = {"force": True} if force else {}
        fmt = (
            expected_format
            if expected_format is not None
            else expected_format_for_path(output.name)
        )
        if fmt and self._client_accepts("expected_format"):
            extra["expected_format"] = fmt
        guard = guard_for(output.name)
        if guard is not None and self._client_accepts("expect_header"):
            extra["expect_header"] = guard
        if output.name.startswith("ncm-vigente@") and self._client_accepts(
            "deduplicate_by_sha256"
        ):
            extra["deduplicate_by_sha256"] = True
        return self.client.download_with_manifest(
            url,
            output,
            source_id=self.source_id,
            dataset_id=dataset_id or output.parent.name or self.source_id,
            producer=self.name,
            progress=progress,
            **extra,
        )


_DEFAULT_OUTPUT = Path("/data/comex")

fetcher = ComexFetcherApp(
    default_output=_DEFAULT_OUTPUT,
    name="comex-fetcher",
    help="Dados de comércio exterior (SECEX/COMEX).",
    groups_dict=GROUPS,
    aliases_dict=GROUP_ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
    freshness_policy=FreshnessPolicy.HEAD_OR_MANIFEST,
)


def convert(
    input_dir: Path,
    lake_dir: Path,
    *,
    dataset: list[str] | None = None,
    force: bool = False,
) -> Any:
    """Converte arquivos brutos do COMEX para o lake Hive (Parquet)."""
    try:
        from comex_fetcher import lake
    except ImportError as exc:
        raise ImportError(
            "Conversão para o lake requer o extra 'analysis'. "
            "Instale com: quantilica install comex --extra analysis"
        ) from exc

    return lake.converter.convert(input_dir, lake_dir, datasets=dataset, force=force)


fetcher.command_convert(convert)
fetcher.command_pipeline(convert)

app = fetcher.app

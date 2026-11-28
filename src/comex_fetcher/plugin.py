"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from collections.abc import Callable
from pathlib import Path
from typing import Any

from quantilica.cli.sdk import PENDING_PUBLICATION_KEY, FetcherApp
from quantilica.core.exceptions import CorruptPayloadError
from quantilica.core.http import HttpStatusError
from quantilica.core.registry import FetcherInfo
from quantilica.core.storage import expected_format_for_path
from quantilica.core.sync import FreshnessPolicy

from .catalog import GROUP_ALIASES, GROUPS, list_datasets
from .payload import ServerFileMissingError, guard_for, looks_like_php
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


def _recording(
    guard: Callable[[bytes], bool], seen: list[bytes]
) -> Callable[[bytes], bool]:
    """Envolve o validador de cabeçalho para guardar a primeira linha que ele viu."""

    def check(line: bytes) -> bool:
        seen.append(line)
        return guard(line)

    return check


class ComexFetcherApp(FetcherApp):
    """``FetcherApp`` que barra no ``sync`` o soft-206 do MDIC (PHP/HTML com 206).

    O download passa a validar a primeira linha útil do CSV/JSON (``expect_header``)
    antes do ``os.replace``; o NCM do Siscomex, sem Last-Modified/ETag, é
    deduplicado por sha256 para não gerar uma versão nova por dia.

    O soft-206 (PHP no lugar de um arquivo inexistente) é o 404 do MDIC. Para uma
    entrada marcada com ``pending_publication`` (arquivo do ano novo, ainda não
    publicado), vira um 404 e o host o conta como "ainda não publicado"; para as
    demais, segue sendo erro do arquivo (``ServerFileMissingError``, um
    ``CorruptPayloadError``).
    """

    def download_entry(  # type: ignore[override]
        self, entry: dict[str, Any], output_dir: Path, *args: Any, **kwargs: Any
    ) -> Path:
        try:
            return super().download_entry(entry, output_dir, *args, **kwargs)
        except ServerFileMissingError as exc:
            if entry.get(PENDING_PUBLICATION_KEY):
                raise HttpStatusError(str(entry["url"]), 404) from exc
            raise

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
        first_line: list[bytes] = []
        if guard is not None and self._client_accepts("expect_header"):
            extra["expect_header"] = _recording(guard, first_line)
        if output.name.startswith("ncm-vigente@") and self._client_accepts(
            "deduplicate_by_sha256"
        ):
            extra["deduplicate_by_sha256"] = True
        try:
            return self.client.download_with_manifest(
                url,
                output,
                source_id=self.source_id,
                dataset_id=dataset_id or output.parent.name or self.source_id,
                producer=self.name,
                progress=progress,
                **extra,
            )
        except CorruptPayloadError as exc:
            if first_line and looks_like_php(first_line[-1]):
                raise ServerFileMissingError(
                    f"{exc} (soft-206: o servidor devolveu código PHP no lugar do "
                    f"arquivo, que não existe no servidor)"
                ) from exc
            raise


_DEFAULT_OUTPUT = Path("/data/comex")

fetcher = ComexFetcherApp(
    default_output=_DEFAULT_OUTPUT,
    name="comex-fetcher",
    help="Dados de comércio exterior (SECEX/COMEX).",
    info=FetcherInfo(
        id="comex",
        nome="Comércio Exterior (Comex Stat)",
        aliases=("secex-comex",),
        orgao="Ministério do Desenvolvimento, Indústria, Comércio e Serviços (MDIC)",
        licenca="Creative Commons Atribuição-SemDerivações 3.0 (CC BY-ND 3.0)",
        homepage=(
            "https://www.gov.br/mdic/pt-br/assuntos/comercio-exterior/"
            "estatisticas/base-de-dados-bruta"
        ),
        cadencia="monthly",
        dominio="macroeconomia",
    ),
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

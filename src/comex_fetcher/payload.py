"""Guardas de conteúdo dos downloads do Comex Stat.

O servidor do MDIC responde ``206`` com o código-fonte PHP do Joomla (``<?php``,
``text/plain``) quando o arquivo não existe. ``validate_payload_signature`` só barra
HTML, então o ``sync`` e o ``convert`` conferem a primeira linha útil do dado.
"""

from __future__ import annotations

from collections.abc import Callable

_BOM = b"\xef\xbb\xbf"


class SoftErrorPayloadError(ValueError):
    """Corpo que não é o dado esperado (PHP/HTML no lugar do CSV/JSON)."""


def looks_like_error_page(head: bytes) -> bool:
    """Se os primeiros bytes são código PHP ou marcação HTML, não dado."""
    text = head.lstrip(_BOM).lstrip().lower()
    return text.startswith(
        (b"<?php", b"<?", b"<!doctype", b"<html", b"<head", b"<body")
    )


def csv_header_ok(first_line: bytes) -> bool:
    """Primeira linha de um CSV do Comex: texto com separador e sem marcação."""
    line = first_line.lstrip(_BOM).strip()
    if not line or looks_like_error_page(line) or line.startswith(b"<"):
        return False
    return b";" in line or b"," in line


def json_header_ok(first_line: bytes) -> bool:
    """Primeira linha de um JSON: objeto ou lista."""
    return first_line.lstrip(_BOM).strip().startswith((b"{", b"["))


def guard_for(filename: str) -> Callable[[bytes], bool] | None:
    """Validador de cabeçalho para ``expect_header`` pela extensão, ou ``None``."""
    name = filename.lower()
    if name.endswith(".csv"):
        return csv_header_ok
    if name.endswith(".json"):
        return json_header_ok
    return None  # zip/xlsx: o testzip do cliente já valida


def check_file(path, name: str | None = None) -> None:
    """Valida um arquivo já em disco com a mesma regra do ``sync``.

    Raises:
        SoftErrorPayloadError: Quando a primeira linha não é dado.
    """
    from pathlib import Path

    guard = guard_for(name or Path(path).name)
    if guard is None:
        return
    with open(path, "rb") as fh:
        for line in fh:
            if line.strip(_BOM + b" \r\n\t"):
                if not guard(line):
                    raise SoftErrorPayloadError(
                        f"{name or Path(path).name}: payload inválido "
                        f"(soft-206 PHP/HTML): {line[:60]!r}"
                    )
                return
    raise SoftErrorPayloadError(f"{name or Path(path).name}: arquivo vazio")

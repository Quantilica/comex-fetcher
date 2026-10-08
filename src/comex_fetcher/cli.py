#!/usr/bin/env python3

"""Command-line interface for downloading Brazil's foreign trade data.

This tool provides access to trade transaction data and auxiliary code tables
from Brazil's Ministry of Economy (SECEX/COMEX).
"""

import sys

_HOST_MODULES = {"typer", "rich", "quantilica"}

try:
    from .plugin import app
except ImportError as exc:  # host (typer/rich/quantilica-cli) ausente
    if (exc.name or "").split(".")[0] not in _HOST_MODULES:
        raise
    app = None
    _PLUGIN_ERROR = exc
else:
    _PLUGIN_ERROR = None


def main(argv: list[str] | None = None) -> None:
    """Main entry point.

    Args:
        argv (list[str] | None): Command-line arguments. Defaults to
            sys.argv[1:] if None.
    """
    if app is None:
        print(
            "Erro: CLI requer 'typer' e 'rich' (via quantilica-cli). "
            'Instale via "quantilica install comex". '
            f"Detalhe: {_PLUGIN_ERROR}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    if argv is None:
        argv = sys.argv[1:]
    app(argv)


if __name__ == "__main__":
    main()

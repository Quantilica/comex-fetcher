import warnings

warnings.warn(
    "comexdown has been renamed to comex-fetcher. "
    "Please update your install: pip install comex-fetcher\n"
    "And your imports: 'import comexdown' -> 'import comex_fetcher'",
    DeprecationWarning,
    stacklevel=2,
)

from comex_fetcher import *  # noqa: F401, F403
from comex_fetcher import download, storage, urls  # noqa: F401
from comex_fetcher import (  # noqa: F401
    get_year,
    get_year_nbm,
    get_complete,
    get_table,
    download_all,
)

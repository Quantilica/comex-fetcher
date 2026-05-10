# comexdown (deprecated)

> **This package has been renamed to [`comex-fetcher`](https://github.com/Quantilica/comex-fetcher).**

Installing `comexdown` will automatically install `comex-fetcher` and re-export its full API with a deprecation warning. No functionality is broken, but you should migrate as soon as possible.

## Migration

```shell
pip uninstall comexdown
pip install comex-fetcher
```

```python
# Before
import comexdown

# After
import comex_fetcher
```

See the [comex-fetcher documentation](https://github.com/Quantilica/comex-fetcher) for full usage.

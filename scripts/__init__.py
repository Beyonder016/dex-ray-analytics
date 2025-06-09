"""
scripts/__init__.py
~~~~~~~~~~~~~~~~~~~
Package initialiser that re-exports the key helpers so tests (and users)
can simply write:

    from scripts import fetch_data, analyzer, visualizer
"""

# ---- public re-exports -----------------------------------------------------
from . import fetch_data, analyzer, visualizer

__all__: list[str] = ["fetch_data", "analyzer", "visualizer"]
# ---------------------------------------------------------------------------

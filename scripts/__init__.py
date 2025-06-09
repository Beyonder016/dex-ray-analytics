"""
scripts/__init__.py
~~~~~~~~~~~~~~~~~~~
Package initialiser that re-exports the key helpers so tests (and users)
can simply write:

    from scripts import fetch_data, analyzer, visualizer
"""

# ---- public re-exports -----------------------------------------------------
from .fetch_data import fetch_data        # function (or class) in fetch_data.py
from .analyzer   import analyzer          # idem in analyzer.py
from .visualizer import visualizer        # idem in visualizer.py

__all__: list[str] = ["fetch_data", "analyzer", "visualizer"]
# ---------------------------------------------------------------------------

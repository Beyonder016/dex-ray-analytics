"""
analyzer.py

Part of the **DeX‑Ray** project.
Transforms raw DataFrames from `fetch_data.py` into meaningful, presentation‑ready insights.

Functions
---------
clean_numeric(df: DataFrame, cols: list[str]) -> DataFrame
    Converts string‑numeric columns (e.g. 'tvl_usd') to floats.

top_pools_by_volume(df: DataFrame, n: int = 10) -> DataFrame
    Returns top‑N pools ranked by 24‑hour volume.

volatility(df: DataFrame, price_column: str = 'token_price_usd', window: int = 24) -> Series
    Calculates rolling standard deviation (volatility) of price data.

liquidity_vs_volume(df: DataFrame) -> DataFrame
    Returns a subset with TVL and 24h volume for bubble plots.

Example CLI
-----------
Run a quick self‑test if executed directly:
$ python scripts/analyzer.py
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def clean_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Ensure columns are numeric (remove commas / None → NaN)."""
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def top_pools_by_volume(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return top‑N pools sorted by 24‑hour volume (descending)."""
    if "volume_usd_24h" not in df.columns:
        raise KeyError("DataFrame must contain 'volume_usd_24h' column")
    return (
        df.sort_values("volume_usd_24h", ascending=False)
          .head(n)
          .reset_index(drop=True)
    )


def liquidity_vs_volume(df: pd.DataFrame) -> pd.DataFrame:
    """Return DataFrame with pool, TVL and 24h volume for plotting."""
    required = ["pool_name", "tvl_usd", "volume_usd_24h", "price_change_pct_24h"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns: {', '.join(missing)}")
    return df[required].copy()


def volatility(price_series: pd.Series, window: int = 24) -> pd.Series:
    """Return rolling standard deviation (volatility) of price series."""
    if price_series.empty:
        return pd.Series(dtype=float)
    return price_series.astype(float).rolling(window=window).std()

# ---------------------------------------------------------------------------
# CLI quick‑test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Load sample DataFrame if exists
    sample_path = Path(__file__).resolve().parent.parent / "data" / "sample_eth_pool.json"
    if sample_path.exists():
        import json
        with sample_path.open() as fp:
            raw = json.load(fp)
        df_raw = pd.json_normalize(raw)
        df_raw = clean_numeric(df_raw, ["tvl_usd", "volume_usd_24h", "price_change_pct_24h"])
        top5 = top_pools_by_volume(df_raw, 5)
        print("Top 5 pools by 24h volume:\n", top5[["pool_name", "volume_usd_24h"]])
    else:
        print("[analyzer] sample_eth_pool.json not found — run fetch_data.py first to cache data.")

"""
visualizer.py

Plotting utilities for the **DeX‑Ray** project.
Builds interactive Plotly charts from the cleaned DataFrames created by
`scripts/analyzer.py`.

Functions
---------
bar_top_volume(df: pandas.DataFrame, n: int = 10) -> plotly.graph_objects.Figure
    Bar chart of the top‑N pools ranked by 24‑hour USD volume.

line_price_trend(price_df: pandas.DataFrame, token_symbol: str = "", title: str | None = None)
    Line chart of a token's USD price over time.

bubble_tvl_vs_volume(df: pandas.DataFrame, n: int = 25, title: str = "TVL vs 24H Volume")
    Bubble scatter where X = TVL, Y = 24H volume, bubble size & color = 24‑hour % price change.

CLI Test
--------
Run this module directly to perform a smoke test that fetches 100 Ethereum pools,
cleans them, and displays a bar chart of the top‑5 by 24‑hour volume.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys

# Expose the module object as ``visualizer`` for tests.
visualizer = sys.modules[__name__]

# -----------------------------------------------------------------------------
# Chart builders
# -----------------------------------------------------------------------------

def bar_top_volume(df: pd.DataFrame, n: int = 10):
    """Return a Plotly bar chart of the top‑N pools by 24‑hour volume."""
    top = (
        df.sort_values("volume_usd_24h", ascending=False)
        .head(n)
        .copy()
    )
    fig = px.bar(
        top,
        x="pair",
        y="volume_usd_24h",
        text="tvl_usd",
        labels={
            "pair": "Pool",
            "volume_usd_24h": "24‑Hour Volume (USD)",
            "tvl_usd": "TVL (USD)"
        },
        title=f"Top {n} Pools by 24‑Hour Volume",
    )
    fig.update_layout(xaxis_tickangle=-35, xaxis_title="Pool (Token0‑Token1)")
    return fig


def line_price_trend(
    price_df: pd.DataFrame,
    token_symbol: str = "",
    title: str | None = None,
):
    """Plot a line chart of *token_symbol* price over time."""
    if title is None:
        title = f"{token_symbol.upper()} Price Trend"

    fig = go.Figure(
        go.Scatter(
            x=price_df["timestamp"],
            y=price_df["price_usd"],
            mode="lines",
            name=token_symbol.upper(),
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        hovermode="x unified",
    )
    return fig


def bubble_tvl_vs_volume(
    df: pd.DataFrame,
    n: int = 25,
    title: str = "TVL vs 24‑Hour Volume",
):
    """Return a bubble chart: X = TVL, Y = 24‑H volume, bubble = % price change."""
    sel = (
        df.sort_values("tvl_usd", ascending=False)
        .head(n)
        .copy()
    )
    fig = px.scatter(
        sel,
        x="tvl_usd",
        y="volume_usd_24h",
        size="price_change_pct_24h",
        color="price_change_pct_24h",
        hover_name="pair",
        labels={
            "tvl_usd": "Total Value Locked (USD)",
            "volume_usd_24h": "24‑Hour Volume (USD)",
            "price_change_pct_24h": "% Price Δ 24H",
        },
        title=title,
        size_max=40,
    )
    fig.update_layout(xaxis_type="log", yaxis_type="log")
    return fig

# -----------------------------------------------------------------------------
# Smoke‑test entry‑point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    from fetch_data import get_pools, pools_to_dataframe  # noqa: WPS433 – local import OK for test
    import analyzer  # noqa: WPS433 – local import OK for test

    # 1️⃣ Fetch
    raw_pools = get_pools("ethereum", limit=100)

    # 2️⃣ Frame & Clean
    df_pools = pools_to_dataframe(raw_pools)
    df_pools = analyzer.clean_numeric(
        df_pools,
        [
            "tvl_usd",
            "volume_usd_24h",
            "price_change_pct_24h",
        ],
    )

    # 3️⃣ Plot
    figure = bar_top_volume(df_pools, n=5)
    figure.show()

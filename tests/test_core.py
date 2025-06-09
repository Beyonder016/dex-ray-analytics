"""tests/test_core.py

Unit‑test suite for **DeX‑Ray**
Run with:
    pytest -q

These tests mock network calls so they work fully offline.
"""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import plotly.graph_objects as go
import pytest

import scripts.fetch_data as fetch_data
import scripts.analyzer as analyzer
import scripts.visualizer as visualizer


# ---------------------------------------------------------------------------
# Helper fixtures & mocks
# ---------------------------------------------------------------------------

# Minimal pool payload that resembles GeckoTerminal response
sample_pool = {
    "id": "eth0x123",
    "attributes": {
        "address": "0x123...",
        "token0_symbol": "AAA",
        "token1_symbol": "BBB",
        "reserve_in_usd": "100000",
        "volume_usd_24h": "50000",
        "price_usd": "1.5",
        "price_change_percentage_24h": "2.3",
    },
}


def _fake_request(url: str, params: dict | None = None, timeout: int = 10):  # noqa: D401
    """Return deterministic fake payload – replaces fetch_data._request."""

    # GeckoTerminal pools endpoint normally returns {"data": [ ... ]}
    return {"data": [sample_pool]}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_get_pools_returns_list():
    """fetch_data.get_pools should return a list with mocked request."""

    with patch("scripts.fetch_data._request", side_effect=_fake_request):
        pools = fetch_data.get_pools("ethereum", limit=1)

    assert isinstance(pools, list)
    assert len(pools) == 1
    assert pools[0]["id"] == "eth0x123"


def test_pools_to_dataframe_columns():
    """DataFrame conversion keeps curated columns intact."""

    df = fetch_data.pools_to_dataframe([sample_pool])
    expected = {
        "pool_id",
        "pair",
        "tvl_usd",
        "volume_usd_24h",
        "price_usd",
        "price_change_pct_24h",
    }
    assert expected.issubset(df.columns)


def test_clean_numeric_converts_types():
    """analyzer.clean_numeric should convert object → float."""

    df = fetch_data.pools_to_dataframe([sample_pool])
    cleaned = analyzer.clean_numeric(
        df.copy(), [
            "tvl_usd",
            "volume_usd_24h",
            "price_usd",
            "price_change_pct_24h",
        ]
    )

    assert cleaned["tvl_usd"].dtype.kind in "fc"  # float or complex (rare)


def test_bar_chart_returns_figure():
    """visualizer.bar_top_volume should produce a Plotly Figure."""

    df = fetch_data.pools_to_dataframe([sample_pool])
    fig = visualizer.bar_top_volume(df, n=1)
    assert isinstance(fig, go.Figure)

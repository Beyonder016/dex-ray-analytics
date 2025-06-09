"""
fetch_data.py
Utility module for interacting with GeckoTerminal DEX API used by the DeX‑Ray project.

Functions
---------
get_pools(network: str, limit: int = 100, page: int = 1) -> list[dict]
    Fetch a page of pools on a specified EVM network.

get_pool(pool_id: str) -> dict
    Fetch detailed info for a single pool.

pools_to_dataframe(pools: list[dict]) -> pandas.DataFrame
    Convert list of pool dicts to a DataFrame with curated columns.

Example
-------
>>> from fetch_data import get_pools, pools_to_dataframe
>>> pools = get_pools("ethereum", limit=20)
>>> df = pools_to_dataframe(pools)
>>> print(df.head())
"""

from __future__ import annotations

import requests
from typing import Any, Dict, List
import pandas as pd

BASE_URL = "https://api.geckoterminal.com/api/v2"

HEADERS = {
    "User-Agent": "DeX-Ray/1.0 (+https://github.com/yourusername/dex-ray-analytics)"
}

def _request(endpoint: str, params: dict | None = None) -> Dict[str, Any]:
    """Internal helper to perform a GET request and return JSON.

    Raises
    ------
    RuntimeError
        If request fails or returns non‑200 status.
    """
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    try:
        response = requests.get(url, params=params or {}, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"API request failed: {exc}") from exc


def get_pools(network: str, limit: int = 100, page: int = 1) -> List[Dict[str, Any]]:
    """Fetch a list of pools for a given network.

    Parameters
    ----------
    network : str
        Network slug, e.g. 'ethereum', 'bsc', 'arbitrum'.
    limit : int, default 100
        Number of pools per page (max 500 according to docs).
    page : int, default 1
        Page number.

    Returns
    -------
    list[dict]
        Raw pool objects from API.
    """
    endpoint = f"networks/{network}/pools"
    params = {"page[number]": page, "page[size]": limit}
    data = _request(endpoint, params)
    return data.get("data", [])


def get_pool(pool_id: str) -> Dict[str, Any]:
    """Fetch detailed data for a single pool.

    Parameters
    ----------
    pool_id : str
        Pool ID, e.g. 'ethereum_0xabc...'

    Returns
    -------
    dict
        Raw pool data from API.
    """
    endpoint = f"pools/{pool_id}"
    data = _request(endpoint)
    return data.get("data", {})


def pools_to_dataframe(pools: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert a list of pool dicts to a pandas DataFrame.

    Extracts commonly used attributes for quick analysis.

    Parameters
    ----------
    pools : list[dict]
        Raw pool objects.

    Returns
    -------
    pandas.DataFrame
    """
    records = []
    for item in pools:
        attrs = item.get("attributes", {})
        token_a = attrs.get("token_a_symbol")
        token_b = attrs.get("token_b_symbol")
        records.append(
            {
                "pool_id": item.get("id"),
                "pair": f"{token_a}/{token_b}",
                "dex_name": attrs.get("dex_name"),
                "network": attrs.get("network"),
                "price_usd": _f(attrs.get("price_usd")),
                "volume_usd_24h": _f(attrs.get("volume_usd_24h")),
                "volume_usd_7d": _f(attrs.get("volume_usd_7d")),
                "tvl_usd": _f(attrs.get("reserve_usd")),
                "price_change_24h": _f(attrs.get("price_percent_change_24h")),
            }
        )
    return pd.DataFrame(records)


def _f(value: Any) -> float | None:
    """Safe float conversion."""
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    # Simple smoke test when running directly
    eth_pools = get_pools("ethereum", limit=10)
    df = pools_to_dataframe(eth_pools)
    print(df.head())

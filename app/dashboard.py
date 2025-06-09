"""
dashboard.py – Streamlit front‑end for **DeX‑Ray**
-------------------------------------------------
A minimal but slick interactive dashboard tying together:
  • scripts.fetch_data
  • scripts.analyzer
  • scripts.visualizer

Run locally:
    streamlit run app/dashboard.py
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
from scripts import fetch_data, analyzer, visualizer

st.set_page_config(
    page_title="DeX‑Ray – DEX Analytics",
    page_icon="🧬",
    layout="wide",
)

# ───────────────────────────────────────────────────────────────────────────────
# Sidebar – controls
# ───────────────────────────────────────────────────────────────────────────────
NETWORKS = {
    "Ethereum": "ethereum",
    "Arbitrum": "arbitrum",
    "BSC": "bsc",
    "Polygon": "polygon",
}

st.sidebar.title("🔧 Controls")
network_name = st.sidebar.selectbox("Select Network", list(NETWORKS.keys()))
network = NETWORKS[network_name]
limit = st.sidebar.slider("Number of Pools", min_value=10, max_value=200, step=10, value=50)

auto_refresh = st.sidebar.checkbox("Auto‑refresh every 60 s", value=False)
refresh_button = st.sidebar.button("🔄 Manual Refresh")

REFRESH_INTERVAL = 60  # seconds

# ───────────────────────────────────────────────────────────────────────────────
# Data fetching (cached)
# ───────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=REFRESH_INTERVAL, show_spinner="Fetching pools …")
def get_data(net: str, lim: int) -> pd.DataFrame:
    pools = fetch_data.get_pools(net, limit=lim)
    df_raw = fetch_data.pools_to_dataframe(pools)
    df_clean = analyzer.clean_numeric(df_raw, [
        "tvl_usd",
        "volume_usd_24h",
        "price_change_percentage_24h",
    ])
    return df_clean

# Trigger refresh logic
if refresh_button or (auto_refresh and st.session_state.get("auto_update", False)):
    st.cache_data.clear()

df = get_data(network, limit)

# ───────────────────────────────────────────────────────────────────────────────
# Main dashboard
# ───────────────────────────────────────────────────────────────────────────────
st.title(f"DeX‑Ray 📊 – {network_name} Pools")

# Top volume bar chart
st.subheader("Top Pools by 24‑Hour Volume (USD)")
fig_bar = visualizer.bar_top_volume(df, n=10)
st.plotly_chart(fig_bar, use_container_width=True)

# Bubble chart TVL vs volume
st.subheader("TVL vs 24‑Hour Volume (Bubble Size = Price % Change)")
fig_bubble = visualizer.bubble_tvl_vs_volume(df)
st.plotly_chart(fig_bubble, use_container_width=True)

# Raw data expander
with st.expander("Raw Data Table"):
    st.dataframe(df, use_container_width=True)

# Footer
st.caption("Built with ❤️ using GeckoTerminal DEX API · DeX‑Ray © 2025")

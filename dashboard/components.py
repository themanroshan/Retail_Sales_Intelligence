"""
RetailPulse — Dashboard Components
"""

import streamlit as st
import pandas as pd


def sidebar_filters(df: pd.DataFrame, page: str) -> pd.DataFrame:
    """
    Render sidebar: project name at top, page nav, then filters.
    Returns filtered DataFrame.
    """
    # ── Project name — top of sidebar ─────────────────────────────────────
    st.sidebar.markdown(
        "<h2 style='margin-bottom:0px'>📊 RetailPulse</h2>"
        "<p style='color:gray; margin-top:2px; font-size:13px'>Indian Retail Sales Intelligence</p>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # ── Filters — right below project name ────────────────────────────────
    st.sidebar.markdown("**Filters**")

    years = sorted(df["year"].dropna().unique().astype(int).tolist())
    selected_years = st.sidebar.multiselect(
        "Year", years, default=years, key="filter_year"
    )

    categories = sorted(df["category"].dropna().unique().tolist())
    selected_cats = st.sidebar.multiselect(
        "Category", categories, default=categories, key="filter_cat"
    )

    states = sorted(df["state"].dropna().unique().tolist())
    selected_states = st.sidebar.multiselect(
        "State", states, default=states, key="filter_state"
    )

    # Apply filters
    mask = (
        df["year"].isin(selected_years) &
        df["category"].isin(selected_cats) &
        df["state"].isin(selected_states)
    )
    filtered = df[mask].copy()

    # Row count right after filters
    st.sidebar.caption(f"Showing **{len(filtered):,}** of {len(df):,} rows")
    st.sidebar.markdown("---")

    return filtered


def download_csv(df: pd.DataFrame, filename: str = "retailpulse_data.csv") -> None:
    """Download button — placed at bottom of each page."""
    st.markdown("---")
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
    )

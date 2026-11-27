"""
RetailPulse — Dashboard Components
====================================
Reusable Streamlit UI components: KPI cards, section headers, data tables.
"""

import streamlit as st
import pandas as pd


def kpi_card(label: str, value: str, delta: str = None, help_text: str = None) -> None:
    """Render a single KPI metric card."""
    st.metric(label=label, value=value, delta=delta, help=help_text)


def kpi_row(kpis: dict) -> None:
    """
    Render headline KPI cards in a row.
    kpis: dict mapping label → {"value": str, "delta": str|None, "help": str|None}
    """
    cols = st.columns(len(kpis))
    for col, (label, meta) in zip(cols, kpis.items()):
        with col:
            kpi_card(
                label     = label,
                value     = meta.get("value", "—"),
                delta     = meta.get("delta"),
                help_text = meta.get("help"),
            )


def section_header(title: str, subtitle: str = None) -> None:
    """Styled section header."""
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)
    st.markdown("---")


def data_table(df: pd.DataFrame, title: str = None,
               height: int = 400, use_container_width: bool = True) -> None:
    """Display a DataFrame with optional title."""
    if title:
        st.markdown(f"**{title}**")
    st.dataframe(df, height=height, use_container_width=use_container_width)


def warning_synthetic() -> None:
    """Display a persistent notice that data is synthetic."""
    st.info(
        "📊 **Data Notice:** This dashboard uses a **SYNTHETIC** dataset generated "
        "for portfolio demonstration. All figures are simulated and do not represent "
        "real company performance or actual Indian retail market data.",
        icon="ℹ️",
    )


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render sidebar filters and return the filtered DataFrame.
    Filters: Year, Category, State.
    """
    st.sidebar.header("Filters")

    # Year filter
    years = sorted(df["year"].dropna().unique().astype(int).tolist())
    selected_years = st.sidebar.multiselect(
        "Year", years, default=years, key="filter_year"
    )

    # Category filter
    categories = sorted(df["category"].dropna().unique().tolist())
    selected_cats = st.sidebar.multiselect(
        "Category", categories, default=categories, key="filter_cat"
    )

    # State filter
    states = sorted(df["state"].dropna().unique().tolist())
    selected_states = st.sidebar.multiselect(
        "State", states, default=states, key="filter_state"
    )

    # Apply
    mask = (
        df["year"].isin(selected_years) &
        df["category"].isin(selected_cats) &
        df["state"].isin(selected_states)
    )
    filtered = df[mask].copy()

    st.sidebar.markdown("---")
    st.sidebar.metric("Filtered Rows", f"{len(filtered):,}")

    return filtered


def download_csv(df: pd.DataFrame, filename: str = "retailpulse_export.csv") -> None:
    """Add a CSV download button for the filtered data."""
    csv = df.to_csv(index=False)
    st.download_button(
        label     = "⬇ Download filtered data as CSV",
        data      = csv,
        file_name = filename,
        mime      = "text/csv",
    )

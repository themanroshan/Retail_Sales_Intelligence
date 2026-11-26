"""Streamlit dashboard — 4 pages (Overview, Products, Time, Forecast).

Run with:
    streamlit run app.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics import (
    daily_orders,
    demand_heatmap,
    kpi_summary,
    top_aisles,
    top_departments,
    top_products,
    top_reordered,
)
from src.config import DATA_PROCESSED
from src.forecasting import SarimaForecaster, compare_models, train_test_split

st.set_page_config(page_title="Quick-Commerce Analytics", page_icon="🛒", layout="wide")


@st.cache_data
def load_data():
    """Load processed Parquet files produced by the pipeline."""
    data = {}
    for name in ["aisles", "departments", "products", "orders", "order_products"]:
        path = DATA_PROCESSED / f"{name}.parquet"
        if not path.exists():
            st.error(f"Missing {path.name}. Run: `python src/pipeline.py`")
            st.stop()
        data[name] = pd.read_parquet(path)
    return data


def main():
    st.title("🛒 Quick-Commerce Analytics Dashboard")
    st.caption("Instacart Market Basket data — a retail sales intelligence project.")

    data = load_data()
    orders = data["orders"]
    op = data["order_products"]

    page = st.sidebar.radio(
        "Pages", ["Overview", "Products", "Time Patterns", "Forecast"]
    )

    if page == "Overview":
        show_overview(orders, op)
    elif page == "Products":
        show_products(op, data["products"], data["departments"], data["aisles"])
    elif page == "Time Patterns":
        show_time(orders)
    elif page == "Forecast":
        show_forecast(orders)


def show_overview(orders, op):
    st.header("Executive Overview")
    kpis = kpi_summary(orders, op)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Orders", f"{kpis['total_orders']:,}")
    c2.metric("Customers", f"{kpis['total_customers']:,}")
    c3.metric("Items Sold", f"{kpis['total_items_sold']:,}")
    c4.metric("Avg Basket", f"{kpis['avg_basket_size']}")
    c5.metric("Reorder Rate", f"{kpis['reorder_rate']*100:.1f}%")

    st.subheader("Daily Order Volume")
    daily = daily_orders(orders)
    fig = px.line(daily, x="order_date", y="order_count")
    st.plotly_chart(fig, use_container_width=True)


def show_products(op, products, departments, aisles):
    st.header("Product & Category Analysis")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Departments")
        td = top_departments(op, products, departments, n=10)
        fig = px.bar(td, x="order_lines", y="department", orientation="h")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 10 Aisles")
        ta = top_aisles(op, products, aisles, n=10)
        fig = px.bar(ta, x="order_lines", y="aisle", orientation="h")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 15 Products")
    st.dataframe(top_products(op, products, n=15), use_container_width=True)

    st.subheader("Top 15 Reordered Products")
    st.dataframe(top_reordered(op, products, n=15), use_container_width=True)


def show_time(orders):
    st.header("Time & Seasonality Patterns")

    daily = daily_orders(orders)
    daily["rolling_7d"] = daily["order_count"].rolling(7, min_periods=1).mean()
    fig = px.line(daily, x="order_date", y=["order_count", "rolling_7d"])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Demand Heatmap (Day of Week × Hour)")
    heat = demand_heatmap(orders)
    pivot = heat.pivot(index="order_dow", columns="order_hour_of_day", values="order_count")
    fig = px.imshow(
        pivot,
        aspect="auto",
        labels=dict(x="Hour of Day", y="Day of Week (0=Sun)", color="Orders"),
    )
    st.plotly_chart(fig, use_container_width=True)


def show_forecast(orders):
    st.header("Demand Forecast — Next 14 Days")

    daily = daily_orders(orders)
    daily["order_date"] = pd.to_datetime(daily["order_date"])
    series = daily.set_index("order_date")["order_count"].asfreq("D").fillna(0)

    if len(series) < 60:
        st.warning("Need at least 60 days of data for forecasting.")
        return

    st.subheader("Model Comparison")
    with st.spinner("Training models ..."):
        results = compare_models(series)
    st.dataframe(results, use_container_width=True)

    st.subheader("SARIMA 14-Day Forecast")
    train, _ = train_test_split(series)
    sarima = SarimaForecaster().fit(train)
    forecast = sarima.predict(14)

    fig = go.Figure()
    fig.add_scatter(x=series.index, y=series.values, name="Actual")
    fig.add_scatter(x=forecast.index, y=forecast.values, name="SARIMA Forecast")
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

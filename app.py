"""
RetailPulse — Streamlit Dashboard
===================================
Run with:
    streamlit run app.py

Data source priority:
  1. MySQL (if configured in .env and pipeline has been run)
  2. Processed CSV fallback (data/processed/retailpulse_clean.csv)

If neither is available, the app will offer to generate synthetic data.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
import plotly.express as px

from src.config import PROCESSED_FILE, DATA_SOURCE
from src.analytics import (
    kpi_summary, monthly_sales_trend, sales_by_category,
    sales_by_subcategory, top_products_by_sales, bottom_products_by_sales,
    sales_by_state, sales_by_city, quarterly_sales,
    sales_by_day_of_week, sales_by_payment_method, discount_impact
)
from dashboard.components import (
    warning_synthetic, sidebar_filters, download_csv, section_header
)
from dashboard.charts import (
    monthly_trend_chart, category_bar_chart, category_pie_chart,
    profit_margin_bar, top_products_chart, state_choropleth,
    quarterly_comparison, day_of_week_chart, discount_impact_chart,
    subcategory_treemap, monthly_heatmap
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "RetailPulse — Indian Retail Intelligence",
    page_icon  = "📊",
    layout     = "wide",
    initial_sidebar_state = "expanded",
)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data …")
def load_data() -> pd.DataFrame:
    """Load cleaned data from MySQL (preferred) or CSV fallback."""
    # Try MySQL first
    if DATA_SOURCE == "mysql":
        try:
            from src.database import query_to_df, test_connection
            if test_connection():
                sql = """
                    SELECT
                        f.order_id, f.order_date, f.product_id,
                        p.product_name, p.category, p.sub_category,
                        l.state, l.city,
                        f.quantity, f.unit_price, f.discount,
                        f.sales_amount, f.profit,
                        f.payment_method,
                        f.year, f.month, f.quarter, f.year_month
                    FROM fact_sales f
                    JOIN dim_product  p ON f.product_id  = p.product_id
                    JOIN dim_location l ON f.location_id = l.location_id
                """
                df = query_to_df(sql)
                df["order_date"] = pd.to_datetime(df["order_date"])
                return df
        except Exception as e:
            st.sidebar.warning(f"MySQL unavailable: {e}\nUsing CSV fallback.")

    # CSV fallback
    if PROCESSED_FILE.exists():
        from src.data_loader import load_processed
        return load_processed()

    # Offer to generate data
    return None


# ── App entry point ───────────────────────────────────────────────────────────
def main() -> None:
    # Sidebar title
    st.sidebar.markdown("## 📊 RetailPulse")
    st.sidebar.caption("Indian Retail Sales Intelligence")
    st.sidebar.markdown("---")

    # Load data
    df_full = load_data()

    if df_full is None:
        st.title("📊 RetailPulse — Indian Retail Sales Intelligence")
        st.warning("No data found. Run the pipeline first.")
        st.code("python -m src.pipeline --no-db", language="bash")
        if st.button("Generate synthetic data now"):
            with st.spinner("Generating data …"):
                from src.generate_data import generate_transactions, save_raw
                from src.data_cleaning import clean
                from src.transformations import add_date_parts
                from src.config import RAW_FILE_PATH, DATA_PROCESSED, PROCESSED_FILE
                DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
                raw = generate_transactions()
                save_raw(raw)
                clean_df, _ = clean(raw)
                enriched = add_date_parts(clean_df)
                enriched.to_csv(PROCESSED_FILE, index=False)
            st.success("Data generated! Reload the page.")
            st.cache_data.clear()
        return

    # Sidebar filters
    df = sidebar_filters(df_full)

    # Page navigation
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Executive Overview",
         "📦 Product & Category",
         "📅 Time Analysis",
         "🗺 Regional Analytics",
         "🔍 Data Quality"],
        key="nav"
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("RetailPulse v1.0 | Portfolio Project")

    # Render selected page
    if   page == "🏠 Executive Overview":     page_overview(df)
    elif page == "📦 Product & Category":    page_products(df)
    elif page == "📅 Time Analysis":         page_time(df)
    elif page == "🗺 Regional Analytics":    page_regional(df)
    elif page == "🔍 Data Quality":          page_data_quality(df, df_full)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_overview(df: pd.DataFrame) -> None:
    st.title("📊 RetailPulse — Indian Retail Sales Intelligence")
    warning_synthetic()

    kpis = kpi_summary(df)

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales",      f"₹{kpis['total_sales']:,.0f}")
    col2.metric("Total Orders",     f"{kpis['total_orders']:,}")
    col3.metric("Units Sold",       f"{kpis['total_units_sold']:,}")
    col4.metric("Avg Order Value",  f"₹{kpis['avg_order_value']:,.2f}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Total Profit",     f"₹{kpis['total_profit']:,.0f}")
    col6.metric("Profit Margin",    f"{kpis['profit_margin_pct']}%")
    col7.metric("Avg Selling Price",f"₹{kpis['avg_selling_price']:,.2f}")
    col8.metric("Avg Discount",     f"{kpis['avg_discount_pct']}%")

    st.markdown("---")

    # Monthly trend
    col_a, col_b = st.columns([2, 1])
    with col_a:
        monthly = monthly_sales_trend(df)
        fig = monthly_trend_chart(monthly)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        cat_df = sales_by_category(df)
        fig_pie = category_pie_chart(cat_df)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Category bar
    st.markdown("---")
    col_c, col_d = st.columns(2)
    with col_c:
        fig_bar = category_bar_chart(cat_df)
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_d:
        fig_margin = profit_margin_bar(cat_df)
        st.plotly_chart(fig_margin, use_container_width=True)

    # Business observations
    st.markdown("---")
    section_header("📝 Key Observations")
    top_cat = cat_df.iloc[0]
    top_state_df = sales_by_state(df)
    top_state = top_state_df.iloc[0] if not top_state_df.empty else None

    obs = [
        f"**Top category by sales:** {top_cat['category']} "
        f"(₹{top_cat['total_sales']:,.0f}, {top_cat['sales_share_pct']}% of total sales)",
        f"**Highest profit margin category:** "
        f"{cat_df.loc[cat_df['profit_margin_pct'].idxmax(), 'category']} "
        f"({cat_df['profit_margin_pct'].max():.1f}%)",
    ]
    if top_state is not None:
        obs.append(f"**Top state by revenue:** {top_state['state']} "
                   f"(₹{top_state['total_sales']:,.0f}, {top_state['sales_share_pct']}% share)")

    for o in obs:
        st.markdown(f"- {o}")

    download_csv(df, "retailpulse_filtered.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PRODUCT & CATEGORY
# ══════════════════════════════════════════════════════════════════════════════
def page_products(df: pd.DataFrame) -> None:
    st.title("📦 Product & Category Analytics")
    warning_synthetic()

    # Category performance
    section_header("Category Performance")
    cat_df = sales_by_category(df)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(category_bar_chart(cat_df), use_container_width=True)
    with col2:
        st.plotly_chart(profit_margin_bar(cat_df), use_container_width=True)
    st.dataframe(cat_df.style.format({
        "total_sales": "₹{:,.2f}", "total_profit": "₹{:,.2f}",
        "profit_margin_pct": "{:.2f}%", "sales_share_pct": "{:.2f}%",
    }), use_container_width=True)

    # Subcategory treemap
    st.markdown("---")
    section_header("Sub-Category Breakdown")
    subcat = sales_by_subcategory(df)
    st.plotly_chart(subcategory_treemap(subcat), use_container_width=True)

    # Top & bottom products
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        section_header("Top 15 Products by Sales")
        top_prods = top_products_by_sales(df, n=15)
        st.plotly_chart(top_products_chart(top_prods, n=15), use_container_width=True)
        st.dataframe(top_prods[["product_name","category","total_sales","total_units",
                                 "total_orders","profit_margin_pct"]].style.format({
            "total_sales": "₹{:,.2f}", "profit_margin_pct": "{:.2f}%"
        }), use_container_width=True)

    with col_b:
        section_header("Bottom 15 Products by Sales")
        bot_prods = bottom_products_by_sales(df, n=15)
        st.dataframe(bot_prods[["product_name","category","total_sales","total_orders"]].style.format({
            "total_sales": "₹{:,.2f}"
        }), use_container_width=True)
        st.caption("Products with ≥ 2 orders, ranked by lowest total sales.")

    # Discount impact
    st.markdown("---")
    section_header("Discount Impact Analysis")
    disc = discount_impact(df)
    st.plotly_chart(discount_impact_chart(disc), use_container_width=True)
    st.dataframe(disc.style.format({
        "total_sales": "₹{:,.2f}", "sales_share_pct": "{:.2f}%"
    }), use_container_width=True)

    download_csv(df, "products_filtered.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — TIME ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def page_time(df: pd.DataFrame) -> None:
    st.title("📅 Time Analysis")
    warning_synthetic()

    # Monthly trend
    section_header("Monthly Sales Trend")
    monthly = monthly_sales_trend(df)
    st.plotly_chart(monthly_trend_chart(monthly), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Monthly Detail**")
        st.dataframe(monthly.style.format({
            "total_sales": "₹{:,.2f}", "total_profit": "₹{:,.2f}",
            "mom_growth_pct": "{:.2f}%",
        }), use_container_width=True)
    with col2:
        # Monthly heatmap
        df2 = df.copy()
        df2["year"]  = df2["order_date"].dt.year
        df2["month"] = df2["order_date"].dt.month
        monthly_heat = df2.groupby(["year","month"])["sales_amount"].sum().reset_index()
        monthly_heat.columns = ["year","month","total_sales"]
        st.plotly_chart(monthly_heatmap(monthly_heat), use_container_width=True)

    # Quarterly
    st.markdown("---")
    section_header("Quarterly Sales")
    qtrly = quarterly_sales(df)
    st.plotly_chart(quarterly_comparison(qtrly), use_container_width=True)

    # Day of week
    st.markdown("---")
    section_header("Day-of-Week Patterns")
    dow = sales_by_day_of_week(df)
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(day_of_week_chart(dow), use_container_width=True)
    with col4:
        st.dataframe(dow.style.format({"total_sales": "₹{:,.2f}"}),
                     use_container_width=True)

    # Partial period warning
    st.markdown("---")
    min_yr = int(df["year"].min())
    max_yr = int(df["year"].max())
    if min_yr == max_yr:
        st.info(f"ℹ️ All data is from {min_yr}. Year-over-year comparisons are not applicable.")

    # Payment method
    st.markdown("---")
    section_header("Payment Method Trends")
    payments = sales_by_payment_method(df)
    fig_pay = px.bar(
        payments, x="payment_method", y="total_sales",
        color="payment_method",
        title="Sales by Payment Method",
        labels={"total_sales": "Sales (INR)", "payment_method": "Method"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_pay.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           yaxis_tickformat="₹,.0f", showlegend=False)
    st.plotly_chart(fig_pay, use_container_width=True)

    download_csv(df, "time_analysis_filtered.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — REGIONAL ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
def page_regional(df: pd.DataFrame) -> None:
    st.title("🗺 Regional & Location Analytics")
    warning_synthetic()

    # State performance
    section_header("Performance by State")
    states_df = sales_by_state(df)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(state_choropleth(states_df), use_container_width=True)
    with col2:
        st.dataframe(states_df[["state","total_sales","total_orders",
                                  "profit_margin_pct","sales_share_pct"]].style.format({
            "total_sales": "₹{:,.2f}", "profit_margin_pct": "{:.2f}%",
            "sales_share_pct": "{:.2f}%",
        }), use_container_width=True)

    # City performance
    st.markdown("---")
    section_header("Top 20 Cities by Sales")
    cities_df = sales_by_city(df, top_n=20)
    fig_city = px.bar(
        cities_df,
        x="total_sales",
        y="city",
        orientation="h",
        color="state",
        title="Top 20 Cities by Total Sales",
        labels={"total_sales": "Sales (INR)", "city": "City", "state": "State"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_city.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis_tickformat="₹,.0f",
        yaxis={"categoryorder": "total ascending"},
    )
    st.plotly_chart(fig_city, use_container_width=True)

    # Category × State heatmap
    st.markdown("---")
    section_header("Category Sales by State (Heatmap)")
    cat_state = (
        df.groupby(["state", "category"])["sales_amount"]
        .sum()
        .reset_index()
    )
    pivot = cat_state.pivot_table(
        index="state", columns="category", values="sales_amount", aggfunc="sum"
    ).fillna(0)
    fig_heat = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Sales (INR) by State × Category",
        labels=dict(color="Sales (INR)"),
    )
    fig_heat.update_layout(paper_bgcolor="white")
    st.plotly_chart(fig_heat, use_container_width=True)

    st.caption(
        "⚠️ Geographic data is SYNTHETIC. States and cities are randomly assigned "
        "and do not reflect real regional retail patterns."
    )
    download_csv(df, "regional_filtered.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════
def page_data_quality(df: pd.DataFrame, df_full: pd.DataFrame) -> None:
    st.title("🔍 Data Quality Report")
    warning_synthetic()

    from src.data_loader import inspect_schema
    schema = inspect_schema(df_full)

    section_header("Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Clean Rows",    f"{schema['rows']:,}")
    col2.metric("Columns",             f"{schema['columns']}")
    col3.metric("Duplicate Rows",      f"{schema['duplicate_rows']}")
    col4.metric("Date Range",          f"{schema['date_min'][:10]} → {schema['date_max'][:10]}")

    st.markdown("---")
    section_header("Null Values per Column")
    nulls_df = pd.DataFrame.from_dict(
        schema["null_counts"], orient="index", columns=["Null Count"]
    )
    nulls_df["Null %"] = (nulls_df["Null Count"] / schema["rows"] * 100).round(2)
    st.dataframe(nulls_df, use_container_width=True)

    st.markdown("---")
    section_header("Numeric Column Statistics")
    stats_df = pd.DataFrame(schema["numeric_stats"]).T
    st.dataframe(stats_df.style.format("{:.2f}"), use_container_width=True)

    st.markdown("---")
    section_header("Data Quality Notes")
    notes = [
        "All data in this project is **SYNTHETIC** (seed=42, 10,000 rows, 2022–2024).",
        "No real company names, prices, or business results are represented.",
        "Cleaning rules applied: date validation, quantity > 0, price > 0, "
        "discount ∈ [0,1], sales_amount > 0, duplicate removal.",
        "Sales amount consistency: verified against unit_price × quantity × (1 − discount) ± 1%.",
        "Payment method nulls: filled with 'Unknown'.",
        "Idempotency: pipeline uses INSERT IGNORE in MySQL; re-running does not create duplicates.",
    ]
    for note in notes:
        st.markdown(f"- {note}")

    # Schema table
    st.markdown("---")
    section_header("Column Descriptions")
    schema_table = pd.DataFrame([
        ("order_id",       "VARCHAR",  "Unique order identifier — RP-XXXXXX"),
        ("order_date",     "DATE",     "Transaction date (YYYY-MM-DD)"),
        ("product_id",     "VARCHAR",  "Product identifier — P-XXXXX"),
        ("product_name",   "VARCHAR",  "Product display name"),
        ("category",       "VARCHAR",  "Product category (8 categories)"),
        ("sub_category",   "VARCHAR",  "Product sub-category (5 per category)"),
        ("quantity",       "INT",      "Units purchased (1–6)"),
        ("unit_price",     "DECIMAL",  "List price in INR before discount"),
        ("discount",       "DECIMAL",  "Discount fraction (0.00 to 0.40)"),
        ("sales_amount",   "DECIMAL",  "Post-discount revenue = price × qty × (1−discount)"),
        ("profit",         "DECIMAL",  "Simulated profit (synthetic margin applied)"),
        ("state",          "VARCHAR",  "Indian state name"),
        ("city",           "VARCHAR",  "Indian city name"),
        ("payment_method", "VARCHAR",  "Payment channel used"),
        ("year",           "INT",      "Order year (derived)"),
        ("month",          "INT",      "Order month 1–12 (derived)"),
        ("quarter",        "INT",      "Order quarter 1–4 (derived)"),
        ("year_month",     "VARCHAR",  "YYYY-MM period label (derived)"),
    ], columns=["Column", "Type", "Description"])
    st.dataframe(schema_table, use_container_width=True, height=500)


if __name__ == "__main__":
    main()

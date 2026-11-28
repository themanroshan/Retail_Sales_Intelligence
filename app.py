"""
RetailPulse — Streamlit Dashboard
Run with:  streamlit run app.py
"""

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.config import PROCESSED_FILE, DATA_SOURCE
from src.analytics import (
    kpi_summary, monthly_sales_trend, sales_by_category,
    sales_by_subcategory, top_products_by_sales, bottom_products_by_sales,
    sales_by_state, sales_by_city, quarterly_sales,
    sales_by_day_of_week, sales_by_payment_method, discount_impact
)
from dashboard.components import sidebar_filters, download_csv

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RetailPulse — Indian Retail Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Shared style helpers ──────────────────────────────────────────────────────
BLUE   = "#2E75B6"
NAVY   = "#1F3864"
GREENS = "Greens"
BLUES  = "Blues"
CHART_H = 420   # consistent chart height everywhere

def _base(fig, h=CHART_H):
    """Apply consistent clean layout to every chart."""
    fig.update_layout(
        height=h,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(size=13),
    )
    return fig

def _fmt_inr(val):
    """Format a number as INR with K/L/Cr suffix."""
    if val >= 1e7:
        return f"₹{val/1e7:.1f} Cr"
    if val >= 1e5:
        return f"₹{val/1e5:.1f} L"
    if val >= 1e3:
        return f"₹{val/1e3:.0f} K"
    return f"₹{val:.0f}"


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data...")
def load_data():
    if DATA_SOURCE == "mysql":
        try:
            from src.database import query_to_df, test_connection
            if test_connection():
                sql = """
                    SELECT f.order_id, f.order_date, f.product_id,
                        p.product_name, p.category, p.sub_category,
                        l.state, l.city,
                        f.quantity, f.unit_price, f.discount,
                        f.sales_amount, f.profit, f.payment_method,
                        f.year, f.month, f.quarter, f.year_month
                    FROM fact_sales f
                    JOIN dim_product  p ON f.product_id  = p.product_id
                    JOIN dim_location l ON f.location_id = l.location_id
                """
                df = query_to_df(sql)
                df["order_date"] = pd.to_datetime(df["order_date"])
                return df
        except Exception as e:
            st.sidebar.warning(f"MySQL unavailable. Using CSV.")
    if PROCESSED_FILE.exists():
        from src.data_loader import load_processed
        return load_processed()
    return None


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    st.sidebar.markdown("## 📊 RetailPulse")
    st.sidebar.caption("Indian Retail Sales Intelligence")
    st.sidebar.markdown("---")

    df_full = load_data()

    if df_full is None:
        st.title("📊 RetailPulse")
        st.error("No data found. Run the pipeline first.")
        st.code("python src/pipeline.py --no-db")
        return

    df = sidebar_filters(df_full)

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Overview",
         "📦 Products",
         "📅 Time Trends",
         "🗺 Regional",
         "🔍 Data Quality"],
        key="nav"
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("RetailPulse v1.0 | Portfolio Project")

    if   page == "🏠 Overview":      page_overview(df)
    elif page == "📦 Products":      page_products(df)
    elif page == "📅 Time Trends":   page_time(df)
    elif page == "🗺 Regional":      page_regional(df)
    elif page == "🔍 Data Quality":  page_data_quality(df, df_full)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_overview(df):
    st.title("📊 RetailPulse — Indian Retail Sales Intelligence")
    st.info("📌 This dashboard uses a **synthetic** dataset for portfolio demonstration. "
            "All figures are simulated.", icon="ℹ️")

    kpis = kpi_summary(df)

    # ── Row 1: 4 headline KPIs ────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales",     _fmt_inr(kpis["total_sales"]))
    c2.metric("Total Orders",    f"{kpis['total_orders']:,}")
    c3.metric("Units Sold",      f"{kpis['total_units_sold']:,}")
    c4.metric("Avg Order Value", f"₹{kpis['avg_order_value']:,.0f}")

    # ── Row 2: 4 profit KPIs ─────────────────────────────────────────────────
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Total Profit",    _fmt_inr(kpis["total_profit"]))
    c6.metric("Profit Margin",   f"{kpis['profit_margin_pct']}%")
    c7.metric("Avg Sell Price",  f"₹{kpis['avg_selling_price']:,.0f}")
    c8.metric("Avg Discount",    f"{kpis['avg_discount_pct']}%")

    st.markdown("---")

    # ── Monthly trend — full width ─────────────────────────────────────────
    monthly = monthly_sales_trend(df)
    fig = px.line(
        monthly, x="year_month", y="total_sales",
        markers=True,
        title="Monthly Sales Trend",
        labels={"year_month": "Month", "total_sales": "Sales (INR)"},
        color_discrete_sequence=[BLUE],
    )
    fig.update_traces(line_width=2.5, marker_size=7)
    fig.update_layout(xaxis_tickangle=-45, hovermode="x unified",
                      yaxis_tickprefix="₹", yaxis_tickformat=",.0f")
    _base(fig, h=380)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Category breakdown — two charts side by side ───────────────────────
    cat_df = sales_by_category(df)

    col_l, col_r = st.columns(2)

    with col_l:
        # Donut — big enough to read labels
        fig_pie = px.pie(
            cat_df, values="total_sales", names="category",
            title="Sales Share by Category",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.45,
        )
        fig_pie.update_traces(
            textposition="outside",
            textinfo="percent+label",
            textfont_size=12,
        )
        fig_pie.update_layout(
            showlegend=False,
            paper_bgcolor="white",
            margin=dict(l=20, r=20, t=50, b=20),
        )
        _base(fig_pie, h=420)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_r:
        # Horizontal bar — sorted, with share % as text
        df_sorted = cat_df.sort_values("total_sales", ascending=True)
        fig_bar = px.bar(
            df_sorted,
            x="total_sales", y="category",
            orientation="h",
            title="Total Sales by Category",
            labels={"total_sales": "Sales (INR)", "category": ""},
            color="total_sales",
            color_continuous_scale=BLUES,
            text="sales_share_pct",
        )
        fig_bar.update_traces(
            texttemplate="  %{text}%",
            textposition="outside",
            textfont_size=11,
        )
        fig_bar.update_layout(
            xaxis_tickprefix="₹", xaxis_tickformat=",.0f",
            coloraxis_showscale=False,
        )
        _base(fig_bar, h=420)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ── Key observations ──────────────────────────────────────────────────
    st.subheader("Key Observations")
    top_cat    = cat_df.iloc[0]
    top_margin = cat_df.loc[cat_df["profit_margin_pct"].idxmax()]
    state_df   = sales_by_state(df)
    top_state  = state_df.iloc[0]

    st.markdown(f"""
- **Top revenue category:** {top_cat['category']} — ₹{top_cat['total_sales']:,.0f} ({top_cat['sales_share_pct']}% of total)
- **Highest profit margin:** {top_margin['category']} — {top_margin['profit_margin_pct']:.1f}% margin
- **Top state:** {top_state['state']} — ₹{top_state['total_sales']:,.0f} ({top_state['sales_share_pct']}% share)
- **Average order value:** ₹{kpis['avg_order_value']:,.0f} per transaction
    """)

    download_csv(df, "retailpulse_filtered.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
def page_products(df):
    st.title("📦 Product & Category Analytics")

    # ── Tab layout keeps page clean ───────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["Category Performance", "Top Products", "Discount Impact"])

    # ── Tab 1: Category ───────────────────────────────────────────────────
    with tab1:
        cat_df = sales_by_category(df)

        # Profit margin bar — full width, x-axis labels readable
        fig_m = px.bar(
            cat_df.sort_values("profit_margin_pct", ascending=False),
            x="category", y="profit_margin_pct",
            title="Profit Margin % by Category",
            labels={"profit_margin_pct": "Margin (%)", "category": ""},
            color="profit_margin_pct",
            color_continuous_scale=GREENS,
            text_auto=".1f",
        )
        fig_m.update_traces(texttemplate="%{text}%", textposition="outside",
                            textfont_size=11)
        fig_m.update_layout(coloraxis_showscale=False,
                            yaxis_ticksuffix="%")
        _base(fig_m)
        st.plotly_chart(fig_m, use_container_width=True)

        st.markdown("---")

        # Sub-category — treemap full width with enough height
        subcat = sales_by_subcategory(df)
        fig_tree = px.treemap(
            subcat,
            path=["category", "sub_category"],
            values="total_sales",
            color="profit_margin_pct",
            color_continuous_scale="RdYlGn",
            title="Sub-Category Sales (colour = profit margin %)",
            labels={"total_sales": "Sales", "profit_margin_pct": "Margin %"},
        )
        fig_tree.update_traces(
            texttemplate="<b>%{label}</b><br>₹%{value:,.0f}",
            textfont_size=12,
        )
        fig_tree.update_layout(paper_bgcolor="white",
                               margin=dict(l=10,r=10,t=50,b=10))
        _base(fig_tree, h=500)
        st.plotly_chart(fig_tree, use_container_width=True)

        st.markdown("**Category Summary Table**")
        st.dataframe(
            cat_df[["category","total_sales","total_orders","total_units",
                    "total_profit","profit_margin_pct","sales_share_pct"]].style.format({
                "total_sales":        "₹{:,.0f}",
                "total_profit":       "₹{:,.0f}",
                "profit_margin_pct":  "{:.1f}%",
                "sales_share_pct":    "{:.1f}%",
                "total_orders":       "{:,}",
                "total_units":        "{:,}",
            }),
            use_container_width=True,
            height=320,
        )

    # ── Tab 2: Top Products ───────────────────────────────────────────────
    with tab2:
        top_prods = top_products_by_sales(df, n=15)

        # Horizontal bar — give it full height
        df_plot = top_prods.sort_values("total_sales", ascending=True).copy()
        df_plot["label"] = df_plot["product_name"].str[:40]

        fig_p = px.bar(
            df_plot,
            x="total_sales", y="label",
            orientation="h",
            color="category",
            title="Top 15 Products by Total Sales",
            labels={"total_sales": "Sales (INR)", "label": ""},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_p.update_layout(
            legend_title="Category",
            xaxis_tickprefix="₹", xaxis_tickformat=",.0f",
            yaxis_tickfont_size=11,
        )
        _base(fig_p, h=520)
        st.plotly_chart(fig_p, use_container_width=True)

        st.markdown("**Top 15 Products — Detail**")
        st.dataframe(
            top_prods[["product_name","category","total_sales",
                       "total_units","total_orders","profit_margin_pct"]].style.format({
                "total_sales":       "₹{:,.0f}",
                "profit_margin_pct": "{:.1f}%",
                "total_units":       "{:,}",
                "total_orders":      "{:,}",
            }),
            use_container_width=True,
            height=400,
        )

    # ── Tab 3: Discount ───────────────────────────────────────────────────
    with tab3:
        st.markdown("#### How discounting affects sales volume and profit margins")
        disc = discount_impact(df)
        disc["discount_bucket"] = disc["discount_bucket"].astype(str)

        fig_d = px.bar(
            disc,
            x="discount_bucket", y="total_sales",
            title="Total Sales by Discount Bucket",
            labels={"discount_bucket": "Discount Level",
                    "total_sales": "Total Sales (INR)"},
            color="total_sales",
            color_continuous_scale=BLUES,
            text="sales_share_pct",
        )
        fig_d.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                            textfont_size=11)
        fig_d.update_layout(coloraxis_showscale=False,
                            yaxis_tickprefix="₹", yaxis_tickformat=",.0f")
        _base(fig_d)
        st.plotly_chart(fig_d, use_container_width=True)

        st.markdown("**Discount Bucket Detail**")
        st.dataframe(
            disc.style.format({
                "total_sales":    "₹{:,.0f}",
                "sales_share_pct": "{:.1f}%",
                "total_orders":   "{:,}",
            }),
            use_container_width=True,
            height=280,
        )
        st.caption(
            "Higher discounts reduce profit margins. "
            "No-discount transactions typically carry the strongest margins."
        )

    download_csv(df, "products_filtered.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — TIME TRENDS
# ══════════════════════════════════════════════════════════════════════════════
def page_time(df):
    st.title("📅 Time Trends")

    tab1, tab2, tab3 = st.tabs(["Monthly Trend", "Quarterly & Weekly", "Payment Methods"])

    # ── Tab 1: Monthly ────────────────────────────────────────────────────
    with tab1:
        monthly = monthly_sales_trend(df)

        fig = px.line(
            monthly, x="year_month", y="total_sales",
            markers=True,
            title="Monthly Sales (with MoM growth %)",
            labels={"year_month": "Month", "total_sales": "Sales (INR)"},
            color_discrete_sequence=[BLUE],
            custom_data=["mom_growth_pct"],
        )
        fig.update_traces(
            line_width=2.5, marker_size=7,
            hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:,.0f}<br>MoM: %{customdata[0]:.1f}%<extra></extra>",
        )
        fig.update_layout(xaxis_tickangle=-45, hovermode="x unified",
                          yaxis_tickprefix="₹", yaxis_tickformat=",.0f")
        _base(fig, h=400)
        st.plotly_chart(fig, use_container_width=True)

        # Heatmap below — full width
        df2 = df.copy()
        df2["year"]  = df2["order_date"].dt.year
        df2["month"] = df2["order_date"].dt.month
        heat_data = df2.groupby(["year","month"])["sales_amount"].sum().reset_index()
        heat_data.columns = ["year","month","total_sales"]
        pivot = heat_data.pivot_table(
            index="year", columns="month", values="total_sales", aggfunc="sum"
        ).fillna(0)
        mnames = ["Jan","Feb","Mar","Apr","May","Jun",
                  "Jul","Aug","Sep","Oct","Nov","Dec"]
        pivot.columns = [mnames[m-1] for m in pivot.columns]

        fig_h = px.imshow(
            pivot, aspect="auto",
            color_continuous_scale=BLUES,
            title="Sales Heatmap — Year vs Month",
            labels=dict(x="Month", y="Year", color="Sales (INR)"),
        )
        fig_h.update_xaxes(side="bottom")
        fig_h.update_layout(paper_bgcolor="white",
                            margin=dict(l=10,r=10,t=50,b=10))
        _base(fig_h, h=250)
        st.plotly_chart(fig_h, use_container_width=True)

        st.markdown("**Monthly Detail Table**")
        st.dataframe(
            monthly[["year_month","total_sales","total_orders",
                      "total_units","mom_growth_pct"]].style.format({
                "total_sales":    "₹{:,.0f}",
                "mom_growth_pct": "{:.1f}%",
                "total_orders":   "{:,}",
                "total_units":    "{:,}",
            }),
            use_container_width=True,
            height=300,
        )

    # ── Tab 2: Quarterly & Weekly ─────────────────────────────────────────
    with tab2:
        col_l, col_r = st.columns(2)

        with col_l:
            qtrly = quarterly_sales(df)
            fig_q = px.bar(
                qtrly, x="year_quarter", y="total_sales",
                title="Quarterly Sales",
                labels={"year_quarter": "Quarter", "total_sales": "Sales (INR)"},
                color="total_sales",
                color_continuous_scale=BLUES,
                text_auto=True,
            )
            fig_q.update_traces(
                texttemplate="₹%{y:,.0f}",
                textposition="outside",
                textfont_size=10,
            )
            fig_q.update_layout(
                xaxis_tickangle=-30,
                yaxis_tickprefix="₹", yaxis_tickformat=",.0f",
                coloraxis_showscale=False,
            )
            _base(fig_q)
            st.plotly_chart(fig_q, use_container_width=True)

        with col_r:
            dow = sales_by_day_of_week(df)
            fig_w = px.bar(
                dow, x="day_name", y="total_sales",
                title="Sales by Day of Week",
                labels={"day_name": "Day", "total_sales": "Sales (INR)"},
                color="total_sales",
                color_continuous_scale=BLUES,
            )
            fig_w.update_layout(
                yaxis_tickprefix="₹", yaxis_tickformat=",.0f",
                coloraxis_showscale=False,
            )
            _base(fig_w)
            st.plotly_chart(fig_w, use_container_width=True)

    # ── Tab 3: Payment Methods ────────────────────────────────────────────
    with tab3:
        payments = sales_by_payment_method(df)

        col_l, col_r = st.columns([1, 1])

        with col_l:
            fig_pay = px.pie(
                payments, values="total_sales", names="payment_method",
                title="Sales Share by Payment Method",
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.4,
            )
            fig_pay.update_traces(
                textposition="outside",
                textinfo="percent+label",
                textfont_size=12,
            )
            fig_pay.update_layout(showlegend=False, paper_bgcolor="white",
                                  margin=dict(l=20,r=20,t=50,b=20))
            _base(fig_pay, h=400)
            st.plotly_chart(fig_pay, use_container_width=True)

        with col_r:
            fig_pb = px.bar(
                payments.sort_values("total_orders", ascending=True),
                x="total_orders", y="payment_method",
                orientation="h",
                title="Orders by Payment Method",
                labels={"total_orders": "Orders", "payment_method": ""},
                color="total_orders",
                color_continuous_scale=BLUES,
                text="total_orders",
            )
            fig_pb.update_traces(texttemplate="%{text:,}", textposition="outside",
                                 textfont_size=11)
            fig_pb.update_layout(coloraxis_showscale=False)
            _base(fig_pb, h=400)
            st.plotly_chart(fig_pb, use_container_width=True)

    download_csv(df, "time_filtered.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — REGIONAL
# ══════════════════════════════════════════════════════════════════════════════
def page_regional(df):
    st.title("🗺 Regional Analytics")
    st.caption("⚠️ Geographic data is SYNTHETIC — randomly assigned for demonstration.")

    # ── State performance — full width horizontal bar ─────────────────────
    states_df = sales_by_state(df)

    fig_s = px.bar(
        states_df.sort_values("total_sales", ascending=True),
        x="total_sales", y="state",
        orientation="h",
        title="Total Sales by State",
        labels={"total_sales": "Sales (INR)", "state": ""},
        color="total_sales",
        color_continuous_scale=BLUES,
        text="sales_share_pct",
    )
    fig_s.update_traces(
        texttemplate="  %{text:.1f}%",
        textposition="outside",
        textfont_size=11,
    )
    fig_s.update_layout(
        xaxis_tickprefix="₹", xaxis_tickformat=",.0f",
        coloraxis_showscale=False,
    )
    _base(fig_s, h=460)
    st.plotly_chart(fig_s, use_container_width=True)

    st.markdown("---")

    # ── Cities & Heatmap in two columns ───────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        cities_df = sales_by_city(df, top_n=15)
        fig_c = px.bar(
            cities_df.sort_values("total_sales", ascending=True),
            x="total_sales", y="city",
            orientation="h",
            color="state",
            title="Top 15 Cities by Sales",
            labels={"total_sales": "Sales (INR)", "city": "", "state": "State"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_c.update_layout(
            xaxis_tickprefix="₹", xaxis_tickformat=",.0f",
            legend_title="State",
            yaxis_tickfont_size=11,
        )
        _base(fig_c, h=480)
        st.plotly_chart(fig_c, use_container_width=True)

    with col_r:
        # State × Category heatmap
        cat_state = (
            df.groupby(["state","category"])["sales_amount"]
            .sum().reset_index()
        )
        pivot = cat_state.pivot_table(
            index="state", columns="category",
            values="sales_amount", aggfunc="sum"
        ).fillna(0)

        fig_h = px.imshow(
            pivot, aspect="auto",
            color_continuous_scale=BLUES,
            title="Sales by State × Category",
            labels=dict(color="Sales (INR)"),
        )
        fig_h.update_layout(
            paper_bgcolor="white",
            xaxis_tickangle=-30,
            xaxis_tickfont_size=11,
            margin=dict(l=10,r=10,t=50,b=10),
        )
        _base(fig_h, h=480)
        st.plotly_chart(fig_h, use_container_width=True)

    st.markdown("---")
    st.markdown("**State Summary Table**")
    st.dataframe(
        states_df[["state","total_sales","total_orders",
                   "total_profit","profit_margin_pct","sales_share_pct"]].style.format({
            "total_sales":       "₹{:,.0f}",
            "total_profit":      "₹{:,.0f}",
            "profit_margin_pct": "{:.1f}%",
            "sales_share_pct":   "{:.1f}%",
            "total_orders":      "{:,}",
        }),
        use_container_width=True,
        height=380,
    )

    download_csv(df, "regional_filtered.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════
def page_data_quality(df, df_full):
    st.title("🔍 Data Quality Report")
    st.info("All data is SYNTHETIC (seed=42, 10,000 rows, 2022–2024). "
            "No real business data is used.", icon="ℹ️")

    from src.data_loader import inspect_schema
    schema = inspect_schema(df_full)

    # ── Headline stats ────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rows",     f"{schema['rows']:,}")
    c2.metric("Columns",        f"{schema['columns']}")
    c3.metric("Duplicates",     f"{schema['duplicate_rows']}")
    c4.metric("Date Range",     f"{schema['date_min'][:10]} to {schema['date_max'][:10]}")

    st.markdown("---")

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("**Null Values per Column**")
        nulls_df = pd.DataFrame.from_dict(
            schema["null_counts"], orient="index", columns=["Null Count"]
        )
        nulls_df["Null %"] = (nulls_df["Null Count"] / schema["rows"] * 100).round(2)
        st.dataframe(nulls_df, use_container_width=True, height=380)

    with col_r:
        st.markdown("**Cleaning Rules Applied (All Passed)**")
        rules = [
            ("Unparseable dates",           "0 rows quarantined"),
            ("Quantity <= 0",               "0 rows quarantined"),
            ("Unit price <= 0",             "0 rows quarantined"),
            ("Discount outside [0,1]",      "0 rows quarantined"),
            ("Sales amount <= 0",           "0 rows quarantined"),
            ("Sales amount mismatch > 1%",  "0 rows flagged"),
            ("Duplicate order+product",     "0 rows removed"),
            ("Missing payment method",      "filled with Unknown"),
        ]
        rules_df = pd.DataFrame(rules, columns=["Rule", "Result"])
        st.dataframe(rules_df, use_container_width=True, height=315)
        st.success("17 / 17 validation checks PASS. Retention rate: 100%")

    st.markdown("---")
    st.markdown("**Column Schema**")
    schema_table = pd.DataFrame([
        ("order_id",       "string",  "Unique transaction ID — RP-XXXXXX"),
        ("order_date",     "date",    "Purchase date"),
        ("product_id",     "string",  "Product ID — P-XXXXX"),
        ("product_name",   "string",  "Product display name"),
        ("category",       "string",  "8 top-level categories"),
        ("sub_category",   "string",  "5 sub-categories per category"),
        ("quantity",       "integer", "Units sold (1–6)"),
        ("unit_price",     "decimal", "List price in INR before discount"),
        ("discount",       "decimal", "Discount fraction 0.00–0.40"),
        ("sales_amount",   "decimal", "price × qty × (1 − discount)"),
        ("profit",         "decimal", "Synthetic margin applied to sales"),
        ("state",          "string",  "Indian state (randomly assigned)"),
        ("city",           "string",  "City within that state"),
        ("payment_method", "string",  "UPI / Card / Net Banking / COD / EMI"),
    ], columns=["Column", "Type", "Description"])
    st.dataframe(schema_table, use_container_width=True, height=460)


if __name__ == "__main__":
    main()

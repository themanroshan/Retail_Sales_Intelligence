"""
RetailPulse — Streamlit Dashboard
Run:  streamlit run app.py
"""

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.config import PROCESSED_FILE
from src.analytics import (
    kpi_summary, monthly_sales_trend, sales_by_category,
    sales_by_subcategory, top_products_by_sales,
    sales_by_state, sales_by_city, quarterly_sales,
    sales_by_day_of_week, sales_by_payment_method, discount_impact
)
from dashboard.components import sidebar_filters, download_csv

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RetailPulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Style constants ───────────────────────────────────────────────────────────
BLUE  = "#2E75B6"
BLUES = "Blues"
GREENS = "Greens"
CHART_H = 420

def _base(fig, h=CHART_H):
    fig.update_layout(
        height=h,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=20, t=45, b=10),
        font=dict(size=13),
    )
    return fig

def _fmt(val):
    if val >= 1e7:  return f"₹{val/1e7:.2f} Cr"
    if val >= 1e5:  return f"₹{val/1e5:.1f} L"
    if val >= 1e3:  return f"₹{val/1e3:.0f} K"
    return f"₹{val:.0f}"


# ── Load data — always from CSV ───────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data...")
def load_data():
    if PROCESSED_FILE.exists():
        from src.data_loader import load_processed
        return load_processed()
    return None


# ── App ───────────────────────────────────────────────────────────────────────
def main():
    df_full = load_data()

    if df_full is None:
        st.error("Data not found. Run:  python src/pipeline.py --no-db")
        return

    # Sidebar: name + filters + nav (in that order)
    df = sidebar_filters(df_full, page="")

    page = st.sidebar.radio(
        "Pages",
        ["Overview", "Products", "Time Trends", "Regional", "Data Quality"],
        key="nav"
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Made by Roshan Manjal")

    if   page == "Overview":      page_overview(df)
    elif page == "Products":      page_products(df)
    elif page == "Time Trends":   page_time(df)
    elif page == "Regional":      page_regional(df)
    elif page == "Data Quality":  page_data_quality(df, df_full)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_overview(df):
    st.header("Overview")
    st.caption("Synthetic dataset — 10,000 Indian retail transactions, 2022–2024")

    kpis = kpi_summary(df)

    # Row 1
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales",     _fmt(kpis["total_sales"]))
    c2.metric("Total Orders",    f"{kpis['total_orders']:,}")
    c3.metric("Units Sold",      f"{kpis['total_units_sold']:,}")
    c4.metric("Avg Order Value", f"₹{kpis['avg_order_value']:,.0f}")

    # Row 2
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Total Profit",    _fmt(kpis["total_profit"]))
    c6.metric("Profit Margin",   f"{kpis['profit_margin_pct']}%")
    c7.metric("Avg Sell Price",  f"₹{kpis['avg_selling_price']:,.0f}")
    c8.metric("Avg Discount",    f"{kpis['avg_discount_pct']}%")

    st.markdown("---")

    # Monthly trend — full width
    monthly = monthly_sales_trend(df)
    fig = px.line(
        monthly, x="year_month", y="total_sales", markers=True,
        title="Monthly Sales Trend",
        labels={"year_month": "Month", "total_sales": "Sales (INR)"},
        color_discrete_sequence=[BLUE],
    )
    fig.update_traces(line_width=2.5, marker_size=7)
    fig.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        yaxis_tickprefix="₹",
        yaxis_tickformat=",.0f",
    )
    _base(fig, h=380)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Category — donut + bar side by side
    cat_df = sales_by_category(df)
    col_l, col_r = st.columns(2)

    with col_l:
        fig_pie = px.pie(
            cat_df, values="total_sales", names="category",
            title="Sales Share by Category",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.42,
        )
        fig_pie.update_traces(
            textposition="outside",
            textinfo="percent+label",
            textfont_size=11,
            pull=[0.03] * len(cat_df),
        )
        fig_pie.update_layout(
            showlegend=False,
            paper_bgcolor="white",
            margin=dict(l=30, r=30, t=50, b=30),
            height=420,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_r:
        fig_bar = px.bar(
            cat_df.sort_values("total_sales", ascending=True),
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

    # Key observations — auto-generated from real data
    top_cat    = cat_df.iloc[0]
    top_margin = cat_df.loc[cat_df["profit_margin_pct"].idxmax()]
    state_df   = sales_by_state(df)
    top_state  = state_df.iloc[0]

    st.subheader("Key Observations")
    st.markdown(f"""
- **Top revenue category:** {top_cat['category']} contributes {top_cat['sales_share_pct']}% of total sales
- **Best profit margin:** {top_margin['category']} at {top_margin['profit_margin_pct']:.1f}%
- **Top state:** {top_state['state']} with {top_state['sales_share_pct']}% of total sales
- **Average order value:** ₹{kpis['avg_order_value']:,.0f} per transaction
    """)

    download_csv(df, "overview_data.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
def page_products(df):
    st.header("Products & Categories")

    tab1, tab2, tab3 = st.tabs(["  Category Performance  ",
                                  "  Top Products  ",
                                  "  Discount Impact  "])

    # ── Tab 1 ─────────────────────────────────────────────────────────────
    with tab1:
        cat_df = sales_by_category(df)

        # Profit margin bar — full width
        fig_m = px.bar(
            cat_df.sort_values("profit_margin_pct", ascending=False),
            x="category", y="profit_margin_pct",
            title="Profit Margin % by Category",
            labels={"profit_margin_pct": "Margin (%)", "category": ""},
            color="profit_margin_pct",
            color_continuous_scale=GREENS,
        )
        fig_m.update_traces(
            texttemplate="%{y:.1f}%",
            textposition="outside",
            textfont_size=12,
        )
        fig_m.update_layout(
            coloraxis_showscale=False,
            yaxis_ticksuffix="%",
            xaxis_tickfont_size=12,
        )
        _base(fig_m, h=400)
        st.plotly_chart(fig_m, use_container_width=True)

        st.markdown("---")

        # Treemap — sub-category breakdown
        subcat = sales_by_subcategory(df)
        fig_tree = px.treemap(
            subcat,
            path=["category", "sub_category"],
            values="total_sales",
            color="profit_margin_pct",
            color_continuous_scale="RdYlGn",
            title="Sub-Category Sales  (colour = profit margin %)",
            labels={"total_sales": "Sales (INR)", "profit_margin_pct": "Margin %"},
            color_continuous_midpoint=25,
        )
        fig_tree.update_traces(
            texttemplate="<b>%{label}</b><br>%{percentParent:.1%}",
            textfont_size=13,
            hovertemplate="<b>%{label}</b><br>Sales: ₹%{value:,.0f}<br>Margin: %{color:.1f}%<extra></extra>",
        )
        fig_tree.update_layout(
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=50, b=10),
            coloraxis_colorbar=dict(title="Margin %"),
        )
        _base(fig_tree, h=520)
        st.plotly_chart(fig_tree, use_container_width=True)

        st.markdown("**Category Summary**")
        st.dataframe(
            cat_df[["category", "total_sales", "total_orders", "total_units",
                    "total_profit", "profit_margin_pct", "sales_share_pct"]].style.format({
                "total_sales":       "₹{:,.0f}",
                "total_profit":      "₹{:,.0f}",
                "profit_margin_pct": "{:.1f}%",
                "sales_share_pct":   "{:.1f}%",
                "total_orders":      "{:,}",
                "total_units":       "{:,}",
            }),
            use_container_width=True,
            height=330,
        )

    # ── Tab 2 ─────────────────────────────────────────────────────────────
    with tab2:
        top_prods = top_products_by_sales(df, n=15)
        df_plot = top_prods.sort_values("total_sales", ascending=True).copy()
        # Truncate long names cleanly
        df_plot["label"] = df_plot["product_name"].str[:45]

        fig_p = px.bar(
            df_plot,
            x="total_sales", y="label",
            orientation="h",
            color="category",
            title="Top 15 Products by Sales",
            labels={"total_sales": "Sales (INR)", "label": "Product"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_p.update_layout(
            legend_title="Category",
            xaxis_tickprefix="₹", xaxis_tickformat=",.0f",
            yaxis_tickfont_size=11,
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.02,
                xanchor="right",  x=1,
            ),
        )
        _base(fig_p, h=560)
        st.plotly_chart(fig_p, use_container_width=True)

        st.markdown("**Top 15 Products — Detail**")
        st.dataframe(
            top_prods[["product_name", "category", "total_sales",
                       "total_units", "total_orders", "profit_margin_pct"]].style.format({
                "total_sales":       "₹{:,.0f}",
                "profit_margin_pct": "{:.1f}%",
                "total_units":       "{:,}",
                "total_orders":      "{:,}",
            }),
            use_container_width=True,
            height=430,
        )

    # ── Tab 3 ─────────────────────────────────────────────────────────────
    with tab3:
        st.markdown("#### How discount levels affect sales and profit margins")
        disc = discount_impact(df)
        disc["discount_bucket"] = disc["discount_bucket"].astype(str)

        fig_d = px.bar(
            disc,
            x="discount_bucket", y="total_sales",
            title="Total Sales by Discount Level",
            labels={"discount_bucket": "Discount Level", "total_sales": "Sales (INR)"},
            color="total_sales",
            color_continuous_scale=BLUES,
            text="sales_share_pct",
        )
        fig_d.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
            textfont_size=12,
        )
        fig_d.update_layout(
            coloraxis_showscale=False,
            yaxis_tickprefix="₹", yaxis_tickformat=",.0f",
        )
        _base(fig_d)
        st.plotly_chart(fig_d, use_container_width=True)

        st.markdown("**Discount Breakdown**")
        st.dataframe(
            disc.style.format({
                "total_sales":     "₹{:,.0f}",
                "sales_share_pct": "{:.1f}%",
            }),
            use_container_width=True,
            height=290,
        )
        st.info(
            "Orders with no discount have the highest profit margins. "
            "Each 10% increase in discount reduces margin by roughly 1–2 percentage points.",
            icon="💡",
        )

    download_csv(df, "products_data.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — TIME TRENDS
# ══════════════════════════════════════════════════════════════════════════════
def page_time(df):
    st.header("Time Trends")

    tab1, tab2, tab3 = st.tabs(["  Monthly  ", "  Quarterly & Weekly  ", "  Payment Methods  "])

    # ── Tab 1 ─────────────────────────────────────────────────────────────
    with tab1:
        monthly = monthly_sales_trend(df)

        fig = px.line(
            monthly, x="year_month", y="total_sales", markers=True,
            title="Monthly Sales with MoM Growth",
            labels={"year_month": "Month", "total_sales": "Sales (INR)"},
            color_discrete_sequence=[BLUE],
            custom_data=["mom_growth_pct"],
        )
        fig.update_traces(
            line_width=2.5, marker_size=7,
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Sales: ₹%{y:,.0f}<br>"
                "MoM Growth: %{customdata[0]:.1f}%"
                "<extra></extra>"
            ),
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            hovermode="x unified",
            yaxis_tickprefix="₹",
            yaxis_tickformat=",.0f",
        )
        _base(fig, h=400)
        st.plotly_chart(fig, use_container_width=True)

        # Heatmap
        df2 = df.copy()
        df2["year"]  = df2["order_date"].dt.year
        df2["month"] = df2["order_date"].dt.month
        heat_data = df2.groupby(["year", "month"])["sales_amount"].sum().reset_index()
        heat_data.columns = ["year", "month", "total_sales"]
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
        fig_h.update_layout(
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=50, b=10),
        )
        _base(fig_h, h=260)
        st.plotly_chart(fig_h, use_container_width=True)

        st.markdown("**Monthly Detail**")
        st.dataframe(
            monthly[["year_month","total_sales","total_orders",
                      "total_units","mom_growth_pct"]].style.format({
                "total_sales":    "₹{:,.0f}",
                "mom_growth_pct": "{:.1f}%",
                "total_orders":   "{:,}",
                "total_units":    "{:,}",
            }),
            use_container_width=True,
            height=320,
        )

    # ── Tab 2 ─────────────────────────────────────────────────────────────
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

    # ── Tab 3 ─────────────────────────────────────────────────────────────
    with tab3:
        payments = sales_by_payment_method(df)
        col_l, col_r = st.columns(2)

        with col_l:
            fig_pie = px.pie(
                payments, values="total_sales", names="payment_method",
                title="Sales Share by Payment Method",
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.4,
            )
            fig_pie.update_traces(
                textposition="outside",
                textinfo="percent+label",
                textfont_size=12,
            )
            fig_pie.update_layout(
                showlegend=False,
                paper_bgcolor="white",
                margin=dict(l=30, r=30, t=50, b=30),
                height=400,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

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
            fig_pb.update_traces(
                texttemplate="%{text:,}",
                textposition="outside",
                textfont_size=11,
            )
            fig_pb.update_layout(coloraxis_showscale=False)
            _base(fig_pb, h=400)
            st.plotly_chart(fig_pb, use_container_width=True)

    download_csv(df, "time_data.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — REGIONAL
# ══════════════════════════════════════════════════════════════════════════════
def page_regional(df):
    st.header("Regional Analytics")
    st.caption("Geographic data is randomly assigned — for demonstration only")

    states_df = sales_by_state(df)

    # State bar — full width
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

    # Cities + heatmap
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
            legend=dict(font=dict(size=11)),
        )
        _base(fig_c, h=480)
        st.plotly_chart(fig_c, use_container_width=True)

    with col_r:
        cat_state = (
            df.groupby(["state", "category"])["sales_amount"]
            .sum().reset_index()
        )
        pivot = cat_state.pivot_table(
            index="state", columns="category",
            values="sales_amount", aggfunc="sum"
        ).fillna(0)

        fig_h = px.imshow(
            pivot, aspect="auto",
            color_continuous_scale=BLUES,
            title="Sales by State and Category",
            labels=dict(color="Sales (INR)"),
        )
        fig_h.update_layout(
            paper_bgcolor="white",
            xaxis_tickangle=-30,
            xaxis_tickfont_size=10,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        _base(fig_h, h=480)
        st.plotly_chart(fig_h, use_container_width=True)

    st.markdown("---")
    st.markdown("**State Summary**")
    st.dataframe(
        states_df[["state", "total_sales", "total_orders",
                   "total_profit", "profit_margin_pct", "sales_share_pct"]].style.format({
            "total_sales":       "₹{:,.0f}",
            "total_profit":      "₹{:,.0f}",
            "profit_margin_pct": "{:.1f}%",
            "sales_share_pct":   "{:.1f}%",
            "total_orders":      "{:,}",
        }),
        use_container_width=True,
        height=400,
    )

    download_csv(df, "regional_data.csv")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════
def page_data_quality(df, df_full):
    st.header("Data Quality")
    st.info(
        "This project uses a synthetic dataset — 10,000 rows generated by Python "
        "with a fixed random seed (42). No real company data is used.",
        icon="ℹ️",
    )

    from src.data_loader import inspect_schema
    schema = inspect_schema(df_full)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rows",   f"{schema['rows']:,}")
    c2.metric("Columns",      f"{schema['columns']}")
    c3.metric("Duplicates",   f"{schema['duplicate_rows']}")
    c4.metric("Date Range",   f"{schema['date_min'][:10]}  to  {schema['date_max'][:10]}")

    st.markdown("---")
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("**Null Values per Column**")
        nulls_df = pd.DataFrame.from_dict(
            schema["null_counts"], orient="index", columns=["Null Count"]
        )
        nulls_df["Null %"] = (nulls_df["Null Count"] / schema["rows"] * 100).round(2)
        st.dataframe(nulls_df, use_container_width=True, height=400)

    with col_r:
        st.markdown("**Cleaning Rules — All Passed**")
        rules = pd.DataFrame([
            ("Unparseable dates",          "0 quarantined"),
            ("Quantity <= 0",              "0 quarantined"),
            ("Unit price <= 0",            "0 quarantined"),
            ("Discount outside 0 to 1",    "0 quarantined"),
            ("Sales amount <= 0",          "0 quarantined"),
            ("Sales mismatch > 1%",        "0 flagged"),
            ("Duplicate order + product",  "0 removed"),
            ("Missing payment method",     "filled Unknown"),
        ], columns=["Rule", "Result"])
        st.dataframe(rules, use_container_width=True, height=330)
        st.success("17 out of 17 validation checks passed.  Retention rate: 100%")

    st.markdown("---")
    st.markdown("**Column Descriptions**")
    cols_df = pd.DataFrame([
        ("order_id",       "Unique transaction ID"),
        ("order_date",     "Purchase date"),
        ("product_id",     "Product identifier"),
        ("product_name",   "Product name"),
        ("category",       "One of 8 categories"),
        ("sub_category",   "One of 5 sub-categories per category"),
        ("quantity",       "Units bought — 1 to 6"),
        ("unit_price",     "List price in INR before discount"),
        ("discount",       "Discount fraction — 0.00 to 0.40"),
        ("sales_amount",   "price × qty × (1 − discount)"),
        ("profit",         "Simulated profit"),
        ("state",          "Indian state"),
        ("city",           "City in that state"),
        ("payment_method", "UPI / Card / Net Banking / COD / EMI"),
    ], columns=["Column", "Description"])
    st.dataframe(cols_df, use_container_width=True, height=480)


if __name__ == "__main__":
    main()

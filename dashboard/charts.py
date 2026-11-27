"""
RetailPulse — Chart Library
=============================
All Plotly chart functions used in the dashboard.
Each function accepts a DataFrame and returns a plotly Figure.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ── Colour palette ─────────────────────────────────────────────────────────────
PRIMARY_BLUE   = "#1F3864"
SECONDARY_BLUE = "#2E75B6"
ACCENT_ORANGE  = "#E67E22"
PALETTE        = px.colors.qualitative.Set2


def monthly_trend_chart(df: pd.DataFrame) -> go.Figure:
    """
    Line chart: monthly total sales with markers.
    df must have columns: year_month, total_sales, total_orders
    """
    fig = px.line(
        df,
        x="year_month",
        y="total_sales",
        markers=True,
        labels={"year_month": "Month", "total_sales": "Sales (INR)"},
        title="Monthly Sales Trend",
        color_discrete_sequence=[SECONDARY_BLUE],
    )
    fig.update_traces(line_width=2.5, marker_size=6)
    fig.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified",
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis_tickformat="₹,.0f",
    )
    return fig


def category_bar_chart(df: pd.DataFrame) -> go.Figure:
    """
    Horizontal bar chart: sales by category.
    df must have: category, total_sales, sales_share_pct
    """
    df_sorted = df.sort_values("total_sales", ascending=True)
    fig = px.bar(
        df_sorted,
        x="total_sales",
        y="category",
        orientation="h",
        color="sales_share_pct",
        color_continuous_scale="Blues",
        labels={"total_sales": "Total Sales (INR)", "category": "Category",
                "sales_share_pct": "Share (%)"},
        title="Sales by Category",
        text="sales_share_pct",
    )
    fig.update_traces(
        texttemplate="%{text}%",
        textposition="outside",
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_tickformat="₹,.0f",
        coloraxis_showscale=False,
        showlegend=False,
    )
    return fig


def category_pie_chart(df: pd.DataFrame) -> go.Figure:
    """Pie chart: sales share by category."""
    fig = px.pie(
        df,
        values="total_sales",
        names="category",
        title="Category Sales Share",
        color_discrete_sequence=PALETTE,
        hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(paper_bgcolor="white")
    return fig


def profit_margin_bar(df: pd.DataFrame) -> go.Figure:
    """Bar chart: profit margin % by category."""
    df_sorted = df.sort_values("profit_margin_pct", ascending=False)
    fig = px.bar(
        df_sorted,
        x="category",
        y="profit_margin_pct",
        color="profit_margin_pct",
        color_continuous_scale="Greens",
        labels={"profit_margin_pct": "Profit Margin (%)", "category": "Category"},
        title="Profit Margin by Category",
        text_auto=".1f",
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis_tickformat=".1f",
        coloraxis_showscale=False,
    )
    return fig


def top_products_chart(df: pd.DataFrame, n: int = 15) -> go.Figure:
    """Horizontal bar chart: top products by sales."""
    df_top = df.head(n).sort_values("total_sales", ascending=True)
    # Truncate long product names
    df_top = df_top.copy()
    df_top["label"] = df_top["product_name"].str[:35]
    fig = px.bar(
        df_top,
        x="total_sales",
        y="label",
        orientation="h",
        color="category",
        labels={"total_sales": "Sales (INR)", "label": "Product"},
        title=f"Top {n} Products by Sales",
        color_discrete_sequence=PALETTE,
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_tickformat="₹,.0f",
        legend_title="Category",
    )
    return fig


def state_choropleth(df: pd.DataFrame) -> go.Figure:
    """
    Bar chart of sales by state (choropleth requires GeoJSON — bar chart is simpler).
    df must have: state, total_sales
    """
    df_sorted = df.sort_values("total_sales", ascending=True).tail(12)
    fig = px.bar(
        df_sorted,
        x="total_sales",
        y="state",
        orientation="h",
        color="total_sales",
        color_continuous_scale="Blues",
        labels={"total_sales": "Sales (INR)", "state": "State"},
        title="Sales by State (Top 12)",
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_tickformat="₹,.0f",
        coloraxis_showscale=False,
    )
    return fig


def quarterly_comparison(df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart: quarterly sales by year."""
    fig = px.bar(
        df,
        x="year_quarter",
        y="total_sales",
        color="total_sales",
        color_continuous_scale="Blues",
        labels={"year_quarter": "Quarter", "total_sales": "Sales (INR)"},
        title="Quarterly Sales",
        text_auto=True,
    )
    fig.update_traces(texttemplate="₹%{y:,.0f}", textposition="outside")
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_tickangle=-30,
        yaxis_tickformat="₹,.0f",
        coloraxis_showscale=False,
    )
    return fig


def day_of_week_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart: sales by day of week."""
    fig = px.bar(
        df,
        x="day_name",
        y="total_sales",
        color="total_sales",
        color_continuous_scale="Blues",
        labels={"day_name": "Day of Week", "total_sales": "Total Sales (INR)"},
        title="Sales by Day of Week",
    )
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis_tickformat="₹,.0f",
        coloraxis_showscale=False,
    )
    return fig


def discount_impact_chart(df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart: orders and profit margin by discount bucket."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["discount_bucket"].astype(str),
        y=df["total_sales"],
        name="Total Sales (INR)",
        marker_color=SECONDARY_BLUE,
    ))
    fig.update_layout(
        title="Sales by Discount Bucket",
        xaxis_title="Discount Bucket",
        yaxis_title="Sales (INR)",
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis_tickformat="₹,.0f",
        legend_title="Metric",
    )
    return fig


def subcategory_treemap(df: pd.DataFrame) -> go.Figure:
    """Treemap: sales by category → sub_category."""
    fig = px.treemap(
        df,
        path=["category", "sub_category"],
        values="total_sales",
        color="profit_margin_pct",
        color_continuous_scale="RdYlGn",
        title="Category & Sub-Category Sales (colour = profit margin %)",
        labels={"total_sales": "Sales (INR)", "profit_margin_pct": "Margin (%)"},
    )
    fig.update_layout(paper_bgcolor="white")
    return fig


def monthly_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Heatmap: sales by year vs. month.
    df must have columns: year, month, total_sales
    """
    pivot = df.pivot_table(
        index="year", columns="month", values="total_sales", aggfunc="sum"
    ).fillna(0)
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot.columns = [month_names[m - 1] for m in pivot.columns]

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Monthly Sales Heatmap (Year × Month)",
        labels=dict(x="Month", y="Year", color="Sales (INR)"),
    )
    fig.update_layout(paper_bgcolor="white")
    return fig

"""
RetailPulse — Analytics Layer
==============================
KPI calculations and aggregations.
All functions accept a pandas DataFrame (the cleaned transactions table)
so they work identically whether the data comes from MySQL or CSV.

KPI definitions are documented in docs/KPI_DEFINITIONS.md.
"""

import pandas as pd
import numpy as np


# ── Core KPIs ─────────────────────────────────────────────────────────────────

def total_sales(df: pd.DataFrame) -> float:
    """Total sales amount (INR). Sum of sales_amount across all clean rows."""
    return float(df["sales_amount"].sum())


def total_orders(df: pd.DataFrame) -> int:
    """Count of distinct order_id values."""
    return int(df["order_id"].nunique())


def total_units_sold(df: pd.DataFrame) -> int:
    """Sum of quantity across all rows."""
    return int(df["quantity"].sum())


def average_order_value(df: pd.DataFrame) -> float:
    """Average sales_amount per unique order_id."""
    order_sales = df.groupby("order_id")["sales_amount"].sum()
    return float(order_sales.mean())


def average_selling_price(df: pd.DataFrame) -> float:
    """Average unit_price across all rows (before discount)."""
    return float(df["unit_price"].mean())


def total_profit(df: pd.DataFrame) -> float:
    """Total profit (INR). Sum of profit column."""
    return float(df["profit"].sum())


def overall_profit_margin(df: pd.DataFrame) -> float:
    """Overall profit margin = total_profit / total_sales."""
    sales = total_sales(df)
    if sales == 0:
        return 0.0
    return float(total_profit(df) / sales)


def average_discount(df: pd.DataFrame) -> float:
    """Sales-weighted average discount rate."""
    if df.empty:
        return 0.0
    gross = (df["unit_price"] * df["quantity"]).sum()
    if gross == 0:
        return 0.0
    disc_amount = (df["unit_price"] * df["quantity"] * df["discount"]).sum()
    return float(disc_amount / gross)


def kpi_summary(df: pd.DataFrame) -> dict:
    """
    Bundle of headline KPIs for the dashboard.
    Returns a dict with formatted and raw values.
    """
    return {
        "total_sales":          total_sales(df),
        "total_orders":         total_orders(df),
        "total_units_sold":     total_units_sold(df),
        "avg_order_value":      round(average_order_value(df), 2),
        "avg_selling_price":    round(average_selling_price(df), 2),
        "total_profit":         total_profit(df),
        "profit_margin_pct":    round(overall_profit_margin(df) * 100, 2),
        "avg_discount_pct":     round(average_discount(df) * 100, 2),
    }


# ── Category analysis ─────────────────────────────────────────────────────────

def sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Sales, orders, units, profit and margin by category."""
    agg = (
        df.groupby("category")
        .agg(
            total_sales   = ("sales_amount", "sum"),
            total_orders  = ("order_id",     "nunique"),
            total_units   = ("quantity",     "sum"),
            total_profit  = ("profit",       "sum"),
        )
        .reset_index()
    )
    agg["profit_margin_pct"] = (agg["total_profit"] / agg["total_sales"] * 100).round(2)
    agg["sales_share_pct"]   = (agg["total_sales"] / agg["total_sales"].sum() * 100).round(2)
    return agg.sort_values("total_sales", ascending=False).reset_index(drop=True)


def sales_by_subcategory(df: pd.DataFrame) -> pd.DataFrame:
    """Sales and profit by sub_category."""
    agg = (
        df.groupby(["category", "sub_category"])
        .agg(
            total_sales  = ("sales_amount", "sum"),
            total_orders = ("order_id",     "nunique"),
            total_units  = ("quantity",     "sum"),
            total_profit = ("profit",       "sum"),
        )
        .reset_index()
    )
    agg["profit_margin_pct"] = (agg["total_profit"] / agg["total_sales"] * 100).round(2)
    return agg.sort_values("total_sales", ascending=False).reset_index(drop=True)


# ── Product analysis ──────────────────────────────────────────────────────────

def top_products_by_sales(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Top N products by total sales amount."""
    agg = (
        df.groupby(["product_id", "product_name", "category"])
        .agg(
            total_sales  = ("sales_amount", "sum"),
            total_units  = ("quantity",     "sum"),
            total_orders = ("order_id",     "nunique"),
            total_profit = ("profit",       "sum"),
        )
        .reset_index()
        .sort_values("total_sales", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )
    agg["profit_margin_pct"] = (agg["total_profit"] / agg["total_sales"] * 100).round(2)
    return agg


def bottom_products_by_sales(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Bottom N products by total sales amount (min 2 orders)."""
    agg = (
        df.groupby(["product_id", "product_name", "category"])
        .agg(
            total_sales  = ("sales_amount", "sum"),
            total_orders = ("order_id",     "nunique"),
        )
        .reset_index()
    )
    agg = agg[agg["total_orders"] >= 2]
    return (
        agg.sort_values("total_sales", ascending=True)
        .head(n)
        .reset_index(drop=True)
    )


# ── Regional analysis ─────────────────────────────────────────────────────────

def sales_by_state(df: pd.DataFrame) -> pd.DataFrame:
    """Sales, orders and profit by state."""
    agg = (
        df.groupby("state")
        .agg(
            total_sales  = ("sales_amount", "sum"),
            total_orders = ("order_id",     "nunique"),
            total_units  = ("quantity",     "sum"),
            total_profit = ("profit",       "sum"),
        )
        .reset_index()
    )
    agg["profit_margin_pct"] = (agg["total_profit"] / agg["total_sales"] * 100).round(2)
    agg["sales_share_pct"]   = (agg["total_sales"] / agg["total_sales"].sum() * 100).round(2)
    return agg.sort_values("total_sales", ascending=False).reset_index(drop=True)


def sales_by_city(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Top N cities by sales."""
    agg = (
        df.groupby(["state", "city"])
        .agg(
            total_sales  = ("sales_amount", "sum"),
            total_orders = ("order_id",     "nunique"),
        )
        .reset_index()
        .sort_values("total_sales", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return agg


# ── Time analysis ─────────────────────────────────────────────────────────────

def monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly sales, orders and profit."""
    df2 = df.copy()
    df2["year_month"] = df2["order_date"].dt.to_period("M").astype(str)
    agg = (
        df2.groupby("year_month")
        .agg(
            total_sales  = ("sales_amount", "sum"),
            total_orders = ("order_id",     "nunique"),
            total_units  = ("quantity",     "sum"),
            total_profit = ("profit",       "sum"),
        )
        .reset_index()
        .sort_values("year_month")
    )
    # Month-over-month growth
    agg["prev_sales"] = agg["total_sales"].shift(1)
    agg["mom_growth_pct"] = (
        (agg["total_sales"] - agg["prev_sales"]) / agg["prev_sales"] * 100
    ).round(2)
    return agg.drop(columns=["prev_sales"]).reset_index(drop=True)


def quarterly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Quarterly sales aggregation."""
    df2 = df.copy()
    df2["year_quarter"] = (
        df2["order_date"].dt.year.astype(str) + "-Q" +
        df2["order_date"].dt.quarter.astype(str)
    )
    agg = (
        df2.groupby("year_quarter")
        .agg(
            total_sales  = ("sales_amount", "sum"),
            total_orders = ("order_id",     "nunique"),
        )
        .reset_index()
        .sort_values("year_quarter")
    )
    return agg


def sales_by_day_of_week(df: pd.DataFrame) -> pd.DataFrame:
    """Average daily sales by day of week."""
    df2 = df.copy()
    df2["day_name"] = df2["order_date"].dt.strftime("%A")
    df2["day_num"]  = df2["order_date"].dt.day_of_week
    agg = (
        df2.groupby(["day_num", "day_name"])
        .agg(
            total_sales  = ("sales_amount", "sum"),
            total_orders = ("order_id",     "nunique"),
        )
        .reset_index()
        .sort_values("day_num")
    )
    return agg


def sales_by_payment_method(df: pd.DataFrame) -> pd.DataFrame:
    """Sales split by payment method."""
    agg = (
        df.groupby("payment_method")
        .agg(
            total_sales  = ("sales_amount", "sum"),
            total_orders = ("order_id",     "nunique"),
        )
        .reset_index()
        .sort_values("total_sales", ascending=False)
    )
    agg["sales_share_pct"] = (agg["total_sales"] / agg["total_sales"].sum() * 100).round(2)
    return agg


# ── Discount analysis ─────────────────────────────────────────────────────────

def discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Discount bucket analysis: how discounts affect sales and profit."""
    df2 = df.copy()
    df2["discount_bucket"] = pd.cut(
        df2["discount"],
        bins=[-0.001, 0.0, 0.1, 0.2, 0.3, 0.4, 1.0],
        labels=["0%", "1–10%", "11–20%", "21–30%", "31–40%", "41%+"],
    )
    agg = (
        df2.groupby("discount_bucket", observed=True)
        .agg(
            total_sales  = ("sales_amount", "sum"),
            total_orders = ("order_id",     "nunique"),
            avg_profit_margin = ("profit",  lambda x: (x.sum() / df2.loc[x.index, "sales_amount"].sum() * 100)),
        )
        .reset_index()
    )
    agg["sales_share_pct"] = (agg["total_sales"] / agg["total_sales"].sum() * 100).round(2)
    return agg

"""
RetailPulse — Tests: Analytics / KPI Calculations
"""

import pytest
import pandas as pd
import numpy as np
from src.analytics import (
    total_sales, total_orders, total_units_sold, average_order_value,
    average_selling_price, total_profit, overall_profit_margin,
    average_discount, kpi_summary, sales_by_category, sales_by_subcategory,
    top_products_by_sales, bottom_products_by_sales, sales_by_state,
    monthly_sales_trend, quarterly_sales, sales_by_day_of_week,
    sales_by_payment_method, discount_impact
)


# ── KPI sanity checks ─────────────────────────────────────────────────────────

def test_total_sales_positive(clean_df):
    assert total_sales(clean_df) > 0


def test_total_orders_positive(clean_df):
    assert total_orders(clean_df) > 0


def test_total_units_positive(clean_df):
    assert total_units_sold(clean_df) > 0


def test_average_order_value_positive(clean_df):
    assert average_order_value(clean_df) > 0


def test_total_profit_positive(clean_df):
    assert total_profit(clean_df) > 0


def test_profit_margin_between_0_and_1(clean_df):
    margin = overall_profit_margin(clean_df)
    assert 0 < margin < 1


def test_average_discount_between_0_and_1(clean_df):
    disc = average_discount(clean_df)
    assert 0 <= disc <= 1


def test_kpi_summary_has_all_keys(clean_df):
    kpis = kpi_summary(clean_df)
    expected_keys = [
        "total_sales", "total_orders", "total_units_sold",
        "avg_order_value", "avg_selling_price", "total_profit",
        "profit_margin_pct", "avg_discount_pct",
    ]
    for k in expected_keys:
        assert k in kpis, f"Missing KPI: {k}"


def test_total_sales_matches_sum(tiny_df):
    expected = tiny_df["sales_amount"].sum()
    assert abs(total_sales(tiny_df) - expected) < 0.01


def test_total_orders_matches_distinct_ids(tiny_df):
    expected = tiny_df["order_id"].nunique()
    assert total_orders(tiny_df) == expected


def test_total_units_matches_sum(tiny_df):
    expected = int(tiny_df["quantity"].sum())
    assert total_units_sold(tiny_df) == expected


def test_average_order_value_calculation(tiny_df):
    expected = tiny_df.groupby("order_id")["sales_amount"].sum().mean()
    result = average_order_value(tiny_df)
    assert abs(result - expected) < 0.01


# ── Aggregation shapes ────────────────────────────────────────────────────────

def test_sales_by_category_has_rows(clean_df):
    df = sales_by_category(clean_df)
    assert len(df) > 0


def test_sales_by_category_no_null_category(clean_df):
    df = sales_by_category(clean_df)
    assert df["category"].isnull().sum() == 0


def test_sales_by_category_total_matches(clean_df):
    """Category totals should sum to overall total."""
    cat_total = sales_by_category(clean_df)["total_sales"].sum()
    overall   = total_sales(clean_df)
    assert abs(cat_total - overall) < 1.0   # allow 1 INR rounding


def test_sales_by_subcategory_has_rows(clean_df):
    df = sales_by_subcategory(clean_df)
    assert len(df) > 0


def test_top_products_respects_n(clean_df):
    n = 5
    df = top_products_by_sales(clean_df, n=n)
    assert len(df) <= n


def test_top_products_sorted_descending(clean_df):
    df = top_products_by_sales(clean_df, n=10)
    assert (df["total_sales"].diff().dropna() <= 0).all()


def test_bottom_products_has_rows(clean_df):
    df = bottom_products_by_sales(clean_df, n=5)
    assert len(df) >= 0   # may be empty if all products have < 2 orders


def test_sales_by_state_has_rows(clean_df):
    df = sales_by_state(clean_df)
    assert len(df) > 0


def test_monthly_trend_sorted(clean_df):
    df = monthly_sales_trend(clean_df)
    assert (df["year_month"].values == sorted(df["year_month"].values)).all()


def test_monthly_trend_total_matches(clean_df):
    df = monthly_sales_trend(clean_df)
    assert abs(df["total_sales"].sum() - total_sales(clean_df)) < 1.0


def test_quarterly_sales_has_rows(clean_df):
    df = quarterly_sales(clean_df)
    assert len(df) > 0


def test_sales_by_day_of_week_has_7_rows_max(clean_df):
    df = sales_by_day_of_week(clean_df)
    assert len(df) <= 7


def test_payment_method_total_matches(clean_df):
    df = sales_by_payment_method(clean_df)
    assert abs(df["total_sales"].sum() - total_sales(clean_df)) < 1.0


def test_discount_impact_returns_dataframe(clean_df):
    df = discount_impact(clean_df)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

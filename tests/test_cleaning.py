"""Tests for cleaning functions in src/pipeline.py."""

import pandas as pd
from src.pipeline import clean_orders, clean_products, add_synthetic_dates


def test_clean_orders_fills_null_days():
    df = pd.DataFrame({
        "order_id":          [1, 2, 3],
        "user_id":           [10, 10, 11],
        "order_number":      [1, 2, 1],
        "order_dow":         [0, 1, 2],
        "order_hour_of_day": [10, 11, 12],
        "days_since_prior_order": [None, 5.0, None],
    })
    result = clean_orders(df)
    assert result["days_since_prior_order"].isna().sum() == 0
    assert result["days_since_prior_order"].iloc[0] == 0


def test_clean_products_strips_whitespace():
    df = pd.DataFrame({
        "product_id":   [1, 2],
        "product_name": [" Milk ", " Bread"],
        "aisle_id":     [1, 2],
        "department_id":[10, 20],
    })
    result = clean_products(df)
    assert result.iloc[0]["product_name"] == "Milk"
    assert result.iloc[1]["product_name"] == "Bread"


def test_clean_products_removes_duplicates():
    df = pd.DataFrame({
        "product_id":   [1, 1, 2],
        "product_name": ["Milk", "Milk", "Bread"],
        "aisle_id":     [1, 1, 2],
        "department_id":[10, 10, 20],
    })
    result = clean_products(df)
    assert len(result) == 2


def test_add_synthetic_dates_creates_order_date():
    orders = pd.DataFrame({
        "order_id":          [1, 2, 3],
        "user_id":           [10, 10, 11],
        "order_number":      [1, 2, 1],
        "order_dow":         [0, 1, 2],
        "order_hour_of_day": [10, 11, 12],
        "days_since_prior_order": [0, 5, 0],
    })
    result = add_synthetic_dates(orders)
    assert "order_date" in result.columns
    assert result["order_date"].notna().all()


def test_synthetic_dates_are_chronological_per_user():
    orders = pd.DataFrame({
        "order_id":          [1, 2, 3],
        "user_id":           [10, 10, 10],
        "order_number":      [1, 2, 3],
        "order_dow":         [0, 1, 2],
        "order_hour_of_day": [10, 11, 12],
        "days_since_prior_order": [0, 5, 3],
    })
    result = add_synthetic_dates(orders).sort_values("order_number")
    diffs = result["order_date"].diff().dropna()
    assert (diffs >= pd.Timedelta(0)).all()

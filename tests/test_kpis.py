"""Tests for KPI functions in src/analytics.py."""

import pandas as pd
import pytest

from src.analytics import (
    average_basket_size,
    kpi_summary,
    reorder_rate,
    top_departments,
    total_customers,
    total_items_sold,
    total_orders,
)


@pytest.fixture
def sample_data():
    orders = pd.DataFrame({
        "order_id":          [1, 2, 3],
        "user_id":           [100, 100, 101],
        "order_number":      [1, 2, 1],
        "order_dow":         [0, 1, 2],
        "order_hour_of_day": [10, 11, 12],
        "days_since_prior_order": [0, 5, 0],
    })
    order_products = pd.DataFrame({
        "order_id":          [1, 1, 2, 2, 3],
        "product_id":        [10, 11, 10, 12, 11],
        "add_to_cart_order": [1, 2, 1, 2, 1],
        "reordered":         [0, 0, 1, 0, 1],
    })
    products = pd.DataFrame({
        "product_id":   [10, 11, 12],
        "product_name": ["Milk", "Bread", "Eggs"],
        "aisle_id":     [1, 1, 2],
        "department_id":[100, 100, 101],
    })
    departments = pd.DataFrame({
        "department_id": [100, 101],
        "department":    ["Dairy", "Produce"],
    })
    return orders, order_products, products, departments


def test_total_orders(sample_data):
    orders, *_ = sample_data
    assert total_orders(orders) == 3


def test_total_customers(sample_data):
    orders, *_ = sample_data
    assert total_customers(orders) == 2


def test_total_items_sold(sample_data):
    _, op, *_ = sample_data
    assert total_items_sold(op) == 5


def test_average_basket_size(sample_data):
    _, op, *_ = sample_data
    # Baskets: order 1 has 2 items, order 2 has 2, order 3 has 1 → avg = 5/3
    assert average_basket_size(op) == pytest.approx(5 / 3)


def test_reorder_rate(sample_data):
    _, op, *_ = sample_data
    # 2 reorders out of 5 lines
    assert reorder_rate(op) == pytest.approx(2 / 5)


def test_top_departments_sorted(sample_data):
    _, op, products, departments = sample_data
    result = top_departments(op, products, departments)
    assert result.iloc[0]["department"] == "Dairy"
    assert result.iloc[0]["order_lines"] == 4


def test_kpi_summary_has_all_keys(sample_data):
    orders, op, *_ = sample_data
    summary = kpi_summary(orders, op)
    assert set(summary.keys()) == {
        "total_orders", "total_customers", "total_items_sold",
        "avg_basket_size", "reorder_rate"
    }

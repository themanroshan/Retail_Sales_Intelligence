"""
RetailPulse — Pytest conftest
==============================
Shared fixtures for all tests.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
import pandas as pd
import numpy as np
from src.generate_data import generate_transactions
from src.data_cleaning import clean
from src.transformations import add_date_parts


@pytest.fixture(scope="session")
def raw_df():
    """Generate a small synthetic dataset once per test session."""
    return generate_transactions(n_rows=500, seed=42)


@pytest.fixture(scope="session")
def clean_df(raw_df):
    """Return the cleaned version of the raw fixture."""
    df, _ = clean(raw_df)
    return df


@pytest.fixture(scope="session")
def enriched_df(clean_df):
    """Return the enriched (date parts added) version."""
    return add_date_parts(clean_df)


@pytest.fixture
def tiny_df():
    """A minimal hand-crafted DataFrame for unit tests."""
    return pd.DataFrame({
        "order_id":       ["RP-000001", "RP-000002", "RP-000003"],
        "order_date":     pd.to_datetime(["2023-01-15", "2023-02-20", "2023-03-10"]),
        "product_id":     ["P-10001",   "P-10002",   "P-10003"],
        "product_name":   ["Phone A",   "Shirt B",   "Book C"],
        "category":       ["Electronics","Clothing", "Books"],
        "sub_category":   ["Mobile Phones","Men's Wear","Fiction"],
        "quantity":       [1,              2,          3],
        "unit_price":     [5000.0,         800.0,      300.0],
        "discount":       [0.10,           0.20,       0.00],
        "sales_amount":   [4500.0,         1280.0,     900.0],
        "profit":         [450.0,          384.0,      180.0],
        "state":          ["Maharashtra",  "Delhi",    "Karnataka"],
        "city":           ["Mumbai",       "New Delhi","Bengaluru"],
        "payment_method": ["UPI",          "Credit Card","Debit Card"],
    })

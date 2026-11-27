"""
RetailPulse — Tests: Data Cleaning
"""

import pytest
import pandas as pd
import numpy as np
from src.data_cleaning import clean


def test_clean_returns_two_items(raw_df):
    result = clean(raw_df)
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_clean_returns_dataframe_and_dict(raw_df):
    clean_df, audit = clean(raw_df)
    assert isinstance(clean_df, pd.DataFrame)
    assert isinstance(audit, dict)


def test_audit_has_required_keys(raw_df):
    _, audit = clean(raw_df)
    required = ["original_rows", "clean_rows", "quarantine_rows",
                "duplicate_rows", "retention_rate_pct", "cleaning_rules_applied"]
    for key in required:
        assert key in audit, f"Missing audit key: {key}"


def test_original_rows_matches_input(raw_df):
    _, audit = clean(raw_df)
    assert audit["original_rows"] == len(raw_df)


def test_clean_rows_plus_quarantine_equals_original(raw_df):
    clean_df, audit = clean(raw_df)
    assert audit["clean_rows"] + audit["quarantine_rows"] == audit["original_rows"]


def test_no_negative_quantity_in_clean(raw_df):
    clean_df, _ = clean(raw_df)
    assert (clean_df["quantity"] <= 0).sum() == 0


def test_no_negative_unit_price_in_clean(raw_df):
    clean_df, _ = clean(raw_df)
    assert (clean_df["unit_price"] <= 0).sum() == 0


def test_no_invalid_discount_in_clean(raw_df):
    clean_df, _ = clean(raw_df)
    assert ((clean_df["discount"] < 0) | (clean_df["discount"] > 1)).sum() == 0


def test_no_null_sales_amount_in_clean(raw_df):
    clean_df, _ = clean(raw_df)
    assert clean_df["sales_amount"].isnull().sum() == 0


def test_no_null_order_date_in_clean(raw_df):
    clean_df, _ = clean(raw_df)
    assert clean_df["order_date"].isnull().sum() == 0


def test_text_whitespace_stripped(tiny_df):
    """Whitespace in text columns should be stripped after cleaning."""
    dirty = tiny_df.copy()
    dirty["product_name"] = "  Phone A  "
    dirty["category"] = "  Electronics  "
    clean_df, _ = clean(dirty)
    assert (clean_df["product_name"].str.startswith(" ")).sum() == 0
    assert (clean_df["category"].str.endswith(" ")).sum() == 0


def test_duplicate_rows_removed(tiny_df):
    """Duplicate order_id + product_id pairs should be quarantined."""
    with_dup = pd.concat([tiny_df, tiny_df.head(1)], ignore_index=True)
    clean_df, audit = clean(with_dup)
    assert audit["duplicate_rows"] == 1
    assert len(clean_df) == len(tiny_df)


def test_negative_quantity_quarantined():
    """Rows with quantity <= 0 must be quarantined."""
    df = pd.DataFrame({
        "order_id":       ["RP-000001"],
        "order_date":     pd.to_datetime(["2023-01-01"]),
        "product_id":     ["P-10001"],
        "product_name":   ["Test Product"],
        "category":       ["Electronics"],
        "sub_category":   ["Mobile Phones"],
        "quantity":       [-1],
        "unit_price":     [5000.0],
        "discount":       [0.0],
        "sales_amount":   [5000.0],
        "profit":         [500.0],
        "state":          ["Maharashtra"],
        "city":           ["Mumbai"],
        "payment_method": ["UPI"],
    })
    clean_df, audit = clean(df)
    assert len(clean_df) == 0
    assert audit["quarantine_rows"] == 1


def test_retention_rate_is_percentage(raw_df):
    _, audit = clean(raw_df)
    assert 0 <= audit["retention_rate_pct"] <= 100


def test_clean_idempotent(raw_df):
    """Running clean twice on the same data should produce the same result."""
    clean_df1, audit1 = clean(raw_df)
    clean_df2, audit2 = clean(raw_df)
    assert audit1["clean_rows"] == audit2["clean_rows"]
    assert audit1["quarantine_rows"] == audit2["quarantine_rows"]

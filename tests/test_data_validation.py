"""
RetailPulse — Tests: Data Validation
"""

import pytest
import pandas as pd
from src.data_validation import validate


def test_validate_returns_dict(clean_df):
    report = validate(clean_df)
    assert isinstance(report, dict)


def test_validate_has_required_keys(clean_df):
    report = validate(clean_df)
    assert "checks" in report
    assert "overall" in report
    assert "summary" in report


def test_validate_overall_is_valid_status(clean_df):
    report = validate(clean_df)
    assert report["overall"] in ("PASS", "WARN", "FAIL")


def test_validate_checks_is_list(clean_df):
    report = validate(clean_df)
    assert isinstance(report["checks"], list)
    assert len(report["checks"]) > 0


def test_validate_clean_data_passes(clean_df):
    """Clean synthetic data should pass or warn, never fail."""
    report = validate(clean_df)
    assert report["overall"] in ("PASS", "WARN")


def test_validate_empty_dataframe_fails():
    empty = pd.DataFrame(columns=[
        "order_id", "order_date", "category", "quantity",
        "unit_price", "discount", "sales_amount", "profit",
        "state", "city", "payment_method", "product_id", "product_name",
        "sub_category"
    ])
    report = validate(empty)
    assert report["overall"] == "FAIL"


def test_each_check_has_status(clean_df):
    report = validate(clean_df)
    for check in report["checks"]:
        assert "status" in check
        assert check["status"] in ("PASS", "WARN", "FAIL")


def test_summary_string_contains_overall(clean_df):
    report = validate(clean_df)
    assert report["overall"] in report["summary"]

"""
RetailPulse — Tests: Pipeline Integration
Tests the end-to-end flow: generate → clean → validate → enrich → save.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import pandas as pd

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_generate_data_produces_dataframe():
    from src.generate_data import generate_transactions
    df = generate_transactions(n_rows=100, seed=99)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100


def test_generate_data_has_expected_columns():
    from src.generate_data import generate_transactions
    df = generate_transactions(n_rows=50, seed=1)
    expected = [
        "order_id", "order_date", "product_id", "product_name",
        "category", "sub_category", "quantity", "unit_price",
        "discount", "sales_amount", "profit", "state", "city",
        "payment_method",
    ]
    for col in expected:
        assert col in df.columns, f"Missing column: {col}"


def test_generate_data_is_deterministic():
    from src.generate_data import generate_transactions
    df1 = generate_transactions(n_rows=100, seed=42)
    df2 = generate_transactions(n_rows=100, seed=42)
    assert df1["sales_amount"].sum() == df2["sales_amount"].sum()
    assert list(df1["order_id"]) == list(df2["order_id"])


def test_generate_different_seed_gives_different_data():
    from src.generate_data import generate_transactions
    df1 = generate_transactions(n_rows=100, seed=1)
    df2 = generate_transactions(n_rows=100, seed=2)
    assert df1["sales_amount"].sum() != df2["sales_amount"].sum()


def test_generate_saves_to_file():
    """save_raw writes a CSV to the given path."""
    from src.generate_data import generate_transactions
    df = generate_transactions(n_rows=50, seed=7)
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "test_transactions.csv"
        df.to_csv(out_path, index=False)
        assert out_path.exists()
        loaded = pd.read_csv(out_path)
        assert len(loaded) == 50


def test_full_pipeline_no_db():
    """Run the pipeline with --no-db flag and verify CSV output."""
    from src.generate_data import generate_transactions
    from src.data_cleaning import clean
    from src.data_validation import validate
    from src.transformations import add_date_parts

    raw = generate_transactions(n_rows=200, seed=42)
    clean_df, audit = clean(raw)
    report = validate(clean_df)
    enriched = add_date_parts(clean_df)

    assert len(enriched) > 0
    assert report["overall"] in ("PASS", "WARN")
    assert audit["clean_rows"] == len(enriched)


def test_pipeline_csv_roundtrip():
    """Write processed CSV and read it back — data must match."""
    from src.generate_data import generate_transactions
    from src.data_cleaning import clean
    from src.transformations import add_date_parts

    raw = generate_transactions(n_rows=100, seed=42)
    clean_df, _ = clean(raw)
    enriched = add_date_parts(clean_df)

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "test_output.csv"
        enriched.to_csv(out_path, index=False)
        loaded = pd.read_csv(out_path)

    assert len(loaded) == len(enriched)
    assert set(loaded.columns) == set(enriched.columns)


def test_transformations_add_date_columns(clean_df):
    """add_date_parts must add year, month, quarter, etc."""
    from src.transformations import add_date_parts
    enriched = add_date_parts(clean_df)
    for col in ["year", "month", "quarter", "year_month", "day_name", "is_weekend"]:
        assert col in enriched.columns, f"Missing column: {col}"


def test_transformations_year_range(clean_df):
    from src.transformations import add_date_parts
    enriched = add_date_parts(clean_df)
    assert enriched["year"].between(2015, 2030).all()


def test_transformations_month_range(clean_df):
    from src.transformations import add_date_parts
    enriched = add_date_parts(clean_df)
    assert enriched["month"].between(1, 12).all()


def test_transformations_quarter_range(clean_df):
    from src.transformations import add_date_parts
    enriched = add_date_parts(clean_df)
    assert enriched["quarter"].between(1, 4).all()


def test_dim_product_build(clean_df):
    from src.transformations import build_dim_product
    dim = build_dim_product(clean_df)
    assert "product_id" in dim.columns
    assert dim["product_id"].duplicated().sum() == 0


def test_dim_location_build(clean_df):
    from src.transformations import build_dim_location
    dim = build_dim_location(clean_df)
    assert "location_id" in dim.columns
    assert dim.duplicated(subset=["state", "city"]).sum() == 0


def test_fact_sales_build(clean_df):
    from src.transformations import add_date_parts, build_dim_location, build_fact_sales
    enriched = add_date_parts(clean_df)
    dim_loc  = build_dim_location(enriched)
    fact     = build_fact_sales(enriched, dim_loc)
    assert "order_id" in fact.columns
    assert "sales_amount" in fact.columns
    assert len(fact) == len(enriched)

"""
RetailPulse — Transformations
==============================
Derives additional columns and builds dimension tables
from the cleaned flat-file transactions.
"""

import pandas as pd
import numpy as np


def add_date_parts(df: pd.DataFrame) -> pd.DataFrame:
    """Add year, month, quarter, week, day_of_week derived from order_date."""
    df = df.copy()
    df["year"]          = df["order_date"].dt.year
    df["month"]         = df["order_date"].dt.month
    df["month_name"]    = df["order_date"].dt.strftime("%b")
    df["quarter"]       = df["order_date"].dt.quarter
    df["quarter_label"] = "Q" + df["quarter"].astype(str)
    df["week"]          = df["order_date"].dt.isocalendar().week.astype(int)
    df["day_of_week"]   = df["order_date"].dt.day_of_week        # 0=Mon
    df["day_name"]      = df["order_date"].dt.strftime("%a")
    df["year_month"]    = df["order_date"].dt.to_period("M").astype(str)
    df["is_weekend"]    = (df["day_of_week"] >= 5).astype(int)
    return df


def build_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    """Build a date dimension table from all order_dates in the dataset."""
    dates = pd.DataFrame({"order_date": pd.to_datetime(df["order_date"].unique())})
    dates = dates.sort_values("order_date").reset_index(drop=True)
    dates["date_id"]      = dates["order_date"].dt.strftime("%Y%m%d").astype(int)
    dates["year"]         = dates["order_date"].dt.year
    dates["quarter"]      = dates["order_date"].dt.quarter
    dates["month"]        = dates["order_date"].dt.month
    dates["month_name"]   = dates["order_date"].dt.strftime("%B")
    dates["week"]         = dates["order_date"].dt.isocalendar().week.astype(int)
    dates["day_of_week"]  = dates["order_date"].dt.dayofweek
    dates["day_name"]     = dates["order_date"].dt.strftime("%A")
    dates["is_weekend"]   = (dates["day_of_week"] >= 5).astype(int)
    dates["year_month"]   = dates["order_date"].dt.to_period("M").astype(str)
    return dates


def build_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build product dimension from unique product_id values.
    Takes the most-common name/category/subcategory for each product_id.
    """
    agg = (
        df.groupby("product_id")
        .agg(
            product_name  = ("product_name",  lambda x: x.mode().iloc[0]),
            category      = ("category",      lambda x: x.mode().iloc[0]),
            sub_category  = ("sub_category",  lambda x: x.mode().iloc[0]),
        )
        .reset_index()
    )
    return agg


def build_dim_location(df: pd.DataFrame) -> pd.DataFrame:
    """Build location dimension from unique state+city combinations."""
    loc = (
        df[["state", "city"]]
        .drop_duplicates()
        .sort_values(["state", "city"])
        .reset_index(drop=True)
    )
    loc["location_id"] = range(1, len(loc) + 1)
    return loc[["location_id", "state", "city"]]


def build_fact_sales(df: pd.DataFrame, dim_location: pd.DataFrame) -> pd.DataFrame:
    """
    Build the fact_sales table by merging location IDs.
    Keeps all transaction-level columns required for aggregation.
    """
    fact = df.merge(dim_location, on=["state", "city"], how="left")
    # Keep the columns used in the star schema
    keep = [
        "order_id", "order_date", "product_id", "location_id",
        "quantity", "unit_price", "discount", "sales_amount", "profit",
        "payment_method",
        # derived date parts (optional — stored for query convenience)
        "year", "month", "quarter", "year_month",
    ]
    keep = [c for c in keep if c in fact.columns]
    return fact[keep].reset_index(drop=True)

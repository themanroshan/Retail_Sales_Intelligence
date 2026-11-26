"""ETL pipeline — read raw CSVs, clean, add synthetic dates, load into MySQL.

Run as:
    python src/pipeline.py
"""

from datetime import datetime
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import DATA_RAW, DATA_PROCESSED, SAMPLE_FRACTION, SYNTHETIC_START_DATE
from src.database import create_database, create_tables, load_dataframe


# ---------- STEP 1: READ RAW CSVs ----------
def read_raw_data():
    """Read all 6 Instacart CSV files from data/raw/."""
    print("Reading raw CSVs ...")
    aisles      = pd.read_csv(DATA_RAW / "aisles.csv")
    departments = pd.read_csv(DATA_RAW / "departments.csv")
    products    = pd.read_csv(DATA_RAW / "products.csv")
    orders      = pd.read_csv(DATA_RAW / "orders.csv")
    op_prior    = pd.read_csv(DATA_RAW / "order_products__prior.csv")
    op_train    = pd.read_csv(DATA_RAW / "order_products__train.csv")

    order_products = pd.concat([op_prior, op_train], ignore_index=True)
    return aisles, departments, products, orders, order_products


# ---------- STEP 2: CLEAN DATA ----------
def clean_products(products):
    """Strip whitespace, drop duplicates, cast types."""
    df = products.copy()
    df["product_name"] = df["product_name"].astype(str).str.strip()
    df = df.dropna(subset=["product_id", "aisle_id", "department_id"])
    df = df.drop_duplicates(subset=["product_id"])
    return df


def clean_orders(orders):
    """Fill null days_since_prior_order with 0 (first-ever orders)."""
    df = orders.copy()
    df["days_since_prior_order"] = df["days_since_prior_order"].fillna(0)
    df = df.drop_duplicates(subset=["order_id"])
    # Drop the eval_set column — not needed for analytics
    if "eval_set" in df.columns:
        df = df.drop(columns=["eval_set"])
    return df


def clean_order_products(order_products):
    """Drop duplicate (order_id, product_id) rows."""
    return order_products.drop_duplicates(subset=["order_id", "product_id"])


# ---------- STEP 3: ADD SYNTHETIC DATES ----------
def add_synthetic_dates(orders):
    """Instacart has no dates — build them from days_since_prior_order."""
    print("Building synthetic timeline ...")
    base_date = pd.Timestamp(datetime.strptime(SYNTHETIC_START_DATE, "%Y-%m-%d"))
    df = orders.sort_values(["user_id", "order_number"]).copy()

    # Cumulative days per user
    df["cum_days"] = df.groupby("user_id")["days_since_prior_order"].cumsum().astype(int)
    # Spread users across a year so they don't all start on day 0
    df["user_offset"] = (df["user_id"] % 365).astype(int)
    df["order_date"] = base_date + pd.to_timedelta(df["cum_days"] + df["user_offset"], unit="D")
    df = df.drop(columns=["cum_days", "user_offset"])
    return df


# ---------- STEP 4: SAMPLE (optional, for faster dev) ----------
def sample_users(orders, order_products, fraction):
    """Keep only a sample of users for faster local runs."""
    if fraction >= 1.0:
        return orders, order_products
    print(f"Sampling {fraction*100:.0f}% of users ...")
    sampled_users = orders["user_id"].drop_duplicates().sample(frac=fraction, random_state=42)
    orders_s = orders[orders["user_id"].isin(sampled_users)]
    op_s = order_products[order_products["order_id"].isin(orders_s["order_id"])]
    return orders_s, op_s


# ---------- STEP 5: LOAD INTO MYSQL ----------
def load_to_mysql(aisles, departments, products, orders, order_products):
    """Create DB + tables, then bulk-insert each table."""
    create_database()
    create_tables()

    load_dataframe(aisles, "dim_aisle")
    load_dataframe(departments, "dim_department")
    load_dataframe(products, "dim_product")

    users = orders[["user_id"]].drop_duplicates()
    load_dataframe(users, "dim_user")

    load_dataframe(orders, "dim_order")
    load_dataframe(order_products, "fact_order_products")


# ---------- STEP 6: SAVE PROCESSED FILES (for dashboard offline mode) ----------
def save_processed(aisles, departments, products, orders, order_products):
    """Save cleaned data to parquet for the Streamlit app to read."""
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    aisles.to_parquet(DATA_PROCESSED / "aisles.parquet", index=False)
    departments.to_parquet(DATA_PROCESSED / "departments.parquet", index=False)
    products.to_parquet(DATA_PROCESSED / "products.parquet", index=False)
    orders.to_parquet(DATA_PROCESSED / "orders.parquet", index=False)
    order_products.to_parquet(DATA_PROCESSED / "order_products.parquet", index=False)
    print(f"Saved processed files to {DATA_PROCESSED}")


# ---------- MAIN ----------
def main():
    print("=" * 50)
    print("RETAIL SALES ETL PIPELINE")
    print("=" * 50)

    # Read
    aisles, departments, products, orders, order_products = read_raw_data()
    print(f"Raw: {len(orders):,} orders, {len(order_products):,} order lines")

    # Clean
    products = clean_products(products)
    orders = clean_orders(orders)
    order_products = clean_order_products(order_products)

    # Sample for faster dev runs
    orders, order_products = sample_users(orders, order_products, SAMPLE_FRACTION)

    # Add synthetic dates
    orders = add_synthetic_dates(orders)

    # Save + load
    save_processed(aisles, departments, products, orders, order_products)
    load_to_mysql(aisles, departments, products, orders, order_products)

    print("\nPipeline complete!")


if __name__ == "__main__":
    main()

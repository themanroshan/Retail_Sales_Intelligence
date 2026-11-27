"""
RetailPulse — Data Loader
Reads the raw CSV and returns a DataFrame with minimal type coercion.
"""

import pandas as pd
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import RAW_FILE_PATH, PROCESSED_FILE


EXPECTED_COLUMNS = [
    "order_id", "order_date", "product_id", "product_name",
    "category", "sub_category", "quantity", "unit_price",
    "discount", "sales_amount", "profit", "state", "city",
    "payment_method",
]

DTYPE_MAP = {
    "order_id":       str,
    "product_id":     str,
    "product_name":   str,
    "category":       str,
    "sub_category":   str,
    "payment_method": str,
    "state":          str,
    "city":           str,
}


def load_raw(path: Path = RAW_FILE_PATH) -> pd.DataFrame:
    """
    Load the raw transactions CSV.

    Parameters
    ----------
    path : Path
        Path to the raw CSV file.

    Returns
    -------
    pd.DataFrame
        Raw DataFrame with minimal coercion applied.

    Raises
    ------
    FileNotFoundError
        If the CSV does not exist at the given path.
    ValueError
        If required columns are missing.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Raw data file not found: {path}\n"
            "Run:  python -m src.generate_data\n"
            "Or place the downloaded CSV at the above path."
        )

    df = pd.read_csv(path, dtype=DTYPE_MAP, low_memory=False)

    # Validate columns
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Raw CSV is missing expected columns: {missing_cols}\n"
            f"Found columns: {list(df.columns)}"
        )

    # Basic type parsing
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    for col in ["quantity", "unit_price", "discount", "sales_amount", "profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def load_processed(path: Path = PROCESSED_FILE) -> pd.DataFrame:
    """Load the cleaned, processed CSV produced by the pipeline."""
    if not path.exists():
        raise FileNotFoundError(
            f"Processed data file not found: {path}\n"
            "Run:  python -m src.pipeline"
        )
    df = pd.read_csv(path, dtype=DTYPE_MAP, low_memory=False)
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    for col in ["quantity", "unit_price", "discount", "sales_amount", "profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def inspect_schema(df: pd.DataFrame) -> dict:
    """Return a schema summary dict for reporting."""
    return {
        "rows":           len(df),
        "columns":        len(df.columns),
        "column_names":   list(df.columns),
        "dtypes":         df.dtypes.astype(str).to_dict(),
        "null_counts":    df.isnull().sum().to_dict(),
        "null_pct":       (df.isnull().mean() * 100).round(2).to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "date_min":       str(df["order_date"].min()) if "order_date" in df else "N/A",
        "date_max":       str(df["order_date"].max()) if "order_date" in df else "N/A",
        "numeric_stats":  df.select_dtypes(include="number").describe().to_dict(),
    }

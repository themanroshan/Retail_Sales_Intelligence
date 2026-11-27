"""
RetailPulse — ETL Pipeline
===========================
Orchestrates the full pipeline:
  1. Generate synthetic data (or load existing raw CSV)
  2. Inspect schema
  3. Clean data
  4. Validate cleaned data
  5. Apply transformations (add date parts, build dim tables)
  6. Save processed CSV
  7. Load into MySQL (optional — skipped if MySQL not configured)
  8. Print audit summary

Usage:
    python -m src.pipeline

Flags:
    --generate   : Force regenerate synthetic data even if raw file exists
    --no-db      : Skip MySQL loading (useful for CSV-only mode)
"""

import sys
import json
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.config import (
    RAW_FILE_PATH, PROCESSED_FILE, DATA_PROCESSED, DATA_SAMPLE,
    MYSQL_DATABASE
)
from src.generate_data import generate_transactions, save_raw
from src.data_loader import load_raw, inspect_schema
from src.data_cleaning import clean
from src.data_validation import validate, print_validation_report
from src.transformations import (
    add_date_parts, build_dim_date, build_dim_product,
    build_dim_location, build_fact_sales
)


def _ensure_dirs() -> None:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    DATA_SAMPLE.mkdir(parents=True, exist_ok=True)


def _save_processed(clean_df: pd.DataFrame) -> None:
    clean_df.to_csv(PROCESSED_FILE, index=False)
    print(f"[pipeline] Saved processed CSV → {PROCESSED_FILE}")


def _save_sample(clean_df: pd.DataFrame, n: int = 500) -> None:
    sample = clean_df.sample(min(n, len(clean_df)), random_state=42)
    sample_path = DATA_SAMPLE / "retailpulse_sample.csv"
    sample.to_csv(sample_path, index=False)
    print(f"[pipeline] Saved sample ({len(sample)} rows) → {sample_path}")


def _load_to_mysql(clean_df: pd.DataFrame) -> None:
    """Attempt to load data into MySQL. Skip gracefully on failure."""
    try:
        from src.database import (
            create_database, create_tables, test_connection,
            load_dim_product, load_dim_location, load_dim_date, load_fact_sales
        )
        from src.transformations import (
            build_dim_product, build_dim_location,
            build_dim_date, build_fact_sales
        )
        from src.config import SQL_DIR

        if not test_connection():
            print("[pipeline] WARNING: MySQL not reachable. Skipping database load.")
            print("           Run with --no-db to suppress this warning.")
            return

        print("[pipeline] Loading into MySQL …")
        create_database()
        create_tables(sql_dir=SQL_DIR)

        df_with_dates = add_date_parts(clean_df)

        dim_product  = build_dim_product(df_with_dates)
        dim_location = build_dim_location(df_with_dates)
        dim_date     = build_dim_date(df_with_dates)
        fact         = build_fact_sales(df_with_dates, dim_location)

        load_dim_product(dim_product)
        load_dim_location(dim_location)
        load_dim_date(dim_date)
        load_fact_sales(fact)

        print(f"[pipeline] MySQL load complete. Database: {MYSQL_DATABASE}")

    except ImportError:
        print("[pipeline] mysql-connector-python not installed. Skipping DB load.")
    except Exception as e:
        print(f"[pipeline] WARNING: MySQL load failed — {e}")
        print("           Data was saved to CSV. Configure .env to enable MySQL.")


def print_audit(audit: dict) -> None:
    print("\n" + "=" * 60)
    print("CLEANING AUDIT SUMMARY")
    print("=" * 60)
    print(f"  Original rows    : {audit['original_rows']:,}")
    print(f"  Clean rows       : {audit['clean_rows']:,}")
    print(f"  Quarantined rows : {audit['quarantine_rows']:,}")
    print(f"  Duplicate rows   : {audit['duplicate_rows']:,}")
    print(f"  Sales mismatches : {audit['sales_mismatch_rows']:,}")
    print(f"  Retention rate   : {audit['retention_rate_pct']}%")
    print("\n  Cleaning rules applied:")
    for rule in audit["cleaning_rules_applied"]:
        flagged = rule.get("rows_flagged", rule.get("rows_affected", 0))
        note    = rule.get("note", rule.get("action", ""))
        print(f"    {rule['rule']:<45} → {flagged} rows  {note}")
    print("=" * 60 + "\n")


def main(force_generate: bool = False, skip_db: bool = False) -> None:
    print("\n" + "=" * 60)
    print("RETAILPULSE ETL PIPELINE")
    print("=" * 60)

    _ensure_dirs()

    # ── Step 1: Generate or load raw data ─────────────────────────────────────
    if force_generate or not RAW_FILE_PATH.exists():
        print("[pipeline] Generating synthetic dataset …")
        raw_df = generate_transactions()
        save_raw(raw_df)
    else:
        print(f"[pipeline] Raw file found: {RAW_FILE_PATH.name}")

    # ── Step 2: Load & inspect ─────────────────────────────────────────────────
    print("[pipeline] Loading raw data …")
    raw_df = load_raw(RAW_FILE_PATH)
    schema = inspect_schema(raw_df)
    print(f"[pipeline] Raw shape  : {schema['rows']:,} rows × {schema['columns']} columns")
    print(f"[pipeline] Date range : {schema['date_min'][:10]} → {schema['date_max'][:10]}")

    # ── Step 3: Clean ──────────────────────────────────────────────────────────
    print("[pipeline] Cleaning data …")
    clean_df, audit = clean(raw_df)
    print_audit(audit)

    # ── Step 4: Validate ───────────────────────────────────────────────────────
    print("[pipeline] Validating cleaned data …")
    report = validate(clean_df)
    print_validation_report(report)
    if report["overall"] == "FAIL":
        print("[pipeline] WARNING: Validation FAILED. Review the report above.")

    # ── Step 5: Enrich with date parts ────────────────────────────────────────
    print("[pipeline] Applying transformations …")
    enriched_df = add_date_parts(clean_df)

    # ── Step 6: Save processed CSV ────────────────────────────────────────────
    _save_processed(enriched_df)
    _save_sample(enriched_df)

    # ── Step 7: Load to MySQL ─────────────────────────────────────────────────
    if not skip_db:
        _load_to_mysql(enriched_df)
    else:
        print("[pipeline] Skipping MySQL load (--no-db flag set).")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print(f"  Clean rows available : {len(enriched_df):,}")
    print(f"  Processed CSV        : {PROCESSED_FILE}")
    print("  Next steps:")
    print("    streamlit run app.py")
    print("    python -m pytest -v")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RetailPulse ETL Pipeline")
    parser.add_argument("--generate", action="store_true",
                        help="Force regenerate synthetic data")
    parser.add_argument("--no-db",    action="store_true",
                        help="Skip MySQL loading")
    args = parser.parse_args()
    main(force_generate=args.generate, skip_db=args.no_db)

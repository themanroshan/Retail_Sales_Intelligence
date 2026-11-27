"""
RetailPulse — Data Cleaning
============================
Applies cleaning rules and returns:
  - clean_df  : rows that passed all checks
  - audit     : dict summarising every cleaning decision

Rules applied (in order):
  1. Strip whitespace from text columns.
  2. Standardise category and sub_category capitalisation.
  3. Standardise state and city names.
  4. Parse / validate order_date — quarantine unparseable dates.
  5. Quarantine rows with quantity <= 0.
  6. Quarantine rows with unit_price <= 0.
  7. Quarantine rows with discount < 0 or discount > 1.
  8. Quarantine rows with sales_amount <= 0.
  9. Flag rows where computed_sales differs from stored sales_amount by > 1%.
 10. Remove fully duplicated rows (keep first).
 11. Fill missing payment_method with "Unknown".
"""

import pandas as pd
import numpy as np
from pathlib import Path


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Clean the raw RetailPulse DataFrame.

    Returns
    -------
    clean_df : pd.DataFrame
        Rows that passed all validation rules.
    audit : dict
        Full audit trail of cleaning decisions.
    """
    original_rows = len(df)
    work = df.copy()

    quarantine_flags = pd.Series(False, index=work.index)
    reasons = pd.Series("", index=work.index)
    audit_log = []

    # ── 1. Strip whitespace ────────────────────────────────────────────────────
    text_cols = ["order_id", "product_id", "product_name", "category",
                 "sub_category", "state", "city", "payment_method"]
    for col in text_cols:
        if col in work.columns:
            work[col] = work[col].astype(str).str.strip()

    # ── 2. Standardise category casing ────────────────────────────────────────
    for col in ["category", "sub_category"]:
        if col in work.columns:
            work[col] = work[col].str.title()

    # ── 3. Standardise state/city casing ──────────────────────────────────────
    for col in ["state", "city"]:
        if col in work.columns:
            work[col] = work[col].str.title()

    # ── 4. Validate order_date ─────────────────────────────────────────────────
    bad_dates = work["order_date"].isnull()
    n_bad_dates = int(bad_dates.sum())
    if n_bad_dates:
        quarantine_flags |= bad_dates
        reasons[bad_dates] += "unparseable_date;"
    audit_log.append({"rule": "unparseable_date", "rows_flagged": n_bad_dates})

    # ── 5. Quantity > 0 ────────────────────────────────────────────────────────
    bad_qty = work["quantity"].isnull() | (work["quantity"] <= 0)
    n_bad_qty = int(bad_qty.sum())
    if n_bad_qty:
        quarantine_flags |= bad_qty
        reasons[bad_qty] += "invalid_quantity;"
    audit_log.append({"rule": "invalid_quantity", "rows_flagged": n_bad_qty})

    # ── 6. Unit price > 0 ─────────────────────────────────────────────────────
    bad_price = work["unit_price"].isnull() | (work["unit_price"] <= 0)
    n_bad_price = int(bad_price.sum())
    if n_bad_price:
        quarantine_flags |= bad_price
        reasons[bad_price] += "invalid_unit_price;"
    audit_log.append({"rule": "invalid_unit_price", "rows_flagged": n_bad_price})

    # ── 7. Discount 0 ≤ d ≤ 1 ─────────────────────────────────────────────────
    bad_disc = (
        work["discount"].isnull() |
        (work["discount"] < 0) |
        (work["discount"] > 1)
    )
    n_bad_disc = int(bad_disc.sum())
    if n_bad_disc:
        quarantine_flags |= bad_disc
        reasons[bad_disc] += "invalid_discount;"
    audit_log.append({"rule": "invalid_discount", "rows_flagged": n_bad_disc})

    # ── 8. Sales amount > 0 ───────────────────────────────────────────────────
    bad_sales = work["sales_amount"].isnull() | (work["sales_amount"] <= 0)
    n_bad_sales = int(bad_sales.sum())
    if n_bad_sales:
        quarantine_flags |= bad_sales
        reasons[bad_sales] += "invalid_sales_amount;"
    audit_log.append({"rule": "invalid_sales_amount", "rows_flagged": n_bad_sales})

    # ── 9. Sales amount consistency check (flag only, not quarantine) ─────────
    computed = (work["unit_price"] * work["quantity"] * (1 - work["discount"])).round(2)
    mismatch = (computed - work["sales_amount"]).abs() / work["sales_amount"].replace(0, np.nan)
    mismatch_flag = mismatch > 0.01     # > 1% discrepancy
    n_mismatch = int(mismatch_flag.sum())
    work["sales_mismatch_flag"] = mismatch_flag.astype(int)
    audit_log.append({"rule": "sales_amount_mismatch_gt1pct", "rows_flagged": n_mismatch,
                      "note": "Flagged but not quarantined - rounding differences retained"})

    # ── 10. Duplicate rows ─────────────────────────────────────────────────────
    dup_mask = work.duplicated(subset=["order_id", "product_id"], keep="first")
    n_dups = int(dup_mask.sum())
    if n_dups:
        quarantine_flags |= dup_mask
        reasons[dup_mask] += "duplicate_order_product;"
    audit_log.append({"rule": "duplicate_order_product", "rows_flagged": n_dups})

    # ── 11. Fill missing payment_method ───────────────────────────────────────
    missing_payment = work["payment_method"].isnull() | (work["payment_method"] == "nan")
    n_missing_payment = int(missing_payment.sum())
    work.loc[missing_payment, "payment_method"] = "Unknown"
    audit_log.append({"rule": "fill_missing_payment_method",
                      "rows_affected": n_missing_payment,
                      "action": "filled with 'Unknown'"})

    # ── Split clean / quarantine ───────────────────────────────────────────────
    quarantine_df = work[quarantine_flags].copy()
    quarantine_df["quarantine_reason"] = reasons[quarantine_flags].values
    clean_df = work[~quarantine_flags].copy()

    # Drop the internal flag column from clean output
    if "sales_mismatch_flag" in clean_df.columns:
        clean_df = clean_df.drop(columns=["sales_mismatch_flag"])

    # ── Build audit summary ───────────────────────────────────────────────────
    audit = {
        "original_rows":    original_rows,
        "clean_rows":       len(clean_df),
        "quarantine_rows":  len(quarantine_df),
        "duplicate_rows":   n_dups,
        "sales_mismatch_rows": n_mismatch,
        "missing_values_per_column": df.isnull().sum().to_dict(),
        "cleaning_rules_applied": audit_log,
        "retention_rate_pct": round(len(clean_df) / original_rows * 100, 2),
    }

    return clean_df, audit

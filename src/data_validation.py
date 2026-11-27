"""
RetailPulse — Data Validation
==============================
Post-cleaning validation checks that run after data_cleaning.clean().
Returns a validation_report dict. Any FAIL status should be investigated.
"""

import pandas as pd
import numpy as np


def validate(df: pd.DataFrame) -> dict:
    """
    Run validation checks on the cleaned DataFrame.

    Returns
    -------
    dict with keys:
        checks  : list of individual check results
        overall : "PASS" | "WARN" | "FAIL"
        summary : human-readable summary string
    """
    checks = []

    def check(name: str, condition: bool, level: str = "FAIL", note: str = "") -> None:
        status = "PASS" if condition else level
        checks.append({"check": name, "status": status, "note": note})

    # ── Row count ─────────────────────────────────────────────────────────────
    check("row_count_positive", len(df) > 0, note=f"{len(df):,} rows")

    # ── No null values in key columns ─────────────────────────────────────────
    key_cols = ["order_id", "order_date", "category", "quantity",
                "unit_price", "sales_amount"]
    for col in key_cols:
        if col in df.columns:
            nulls = int(df[col].isnull().sum())
            check(
                f"no_nulls_{col}",
                nulls == 0,
                note=f"{nulls} nulls"
            )

    # ── Quantity always positive ───────────────────────────────────────────────
    if "quantity" in df.columns:
        bad = int((df["quantity"] <= 0).sum())
        check("quantity_positive", bad == 0, note=f"{bad} invalid")

    # ── Unit price always positive ─────────────────────────────────────────────
    if "unit_price" in df.columns:
        bad = int((df["unit_price"] <= 0).sum())
        check("unit_price_positive", bad == 0, note=f"{bad} invalid")

    # ── Discount within [0, 1] ─────────────────────────────────────────────────
    if "discount" in df.columns:
        bad = int(((df["discount"] < 0) | (df["discount"] > 1)).sum())
        check("discount_valid_range", bad == 0, note=f"{bad} out of range")

    # ── Sales amount positive ─────────────────────────────────────────────────
    if "sales_amount" in df.columns:
        bad = int((df["sales_amount"] <= 0).sum())
        check("sales_amount_positive", bad == 0, note=f"{bad} invalid")

    # ── No duplicate order_id + product_id pairs ──────────────────────────────
    if {"order_id", "product_id"}.issubset(df.columns):
        dups = int(df.duplicated(subset=["order_id", "product_id"]).sum())
        check("no_duplicate_order_product", dups == 0, note=f"{dups} duplicates")

    # ── order_date is a valid datetime ────────────────────────────────────────
    if "order_date" in df.columns:
        bad = int(df["order_date"].isnull().sum())
        check("order_date_parseable", bad == 0, note=f"{bad} unparseable")

    # ── Date range sanity (2020-01-01 to today) ───────────────────────────────
    if "order_date" in df.columns and df["order_date"].notna().any():
        min_date = df["order_date"].min()
        max_date = df["order_date"].max()
        check(
            "order_date_reasonable_range",
            min_date >= pd.Timestamp("2015-01-01"),
            level="WARN",
            note=f"Min date: {min_date.date()}"
        )
        check(
            "order_date_not_future",
            max_date <= pd.Timestamp("today") + pd.Timedelta(days=365),
            level="WARN",
            note=f"Max date: {max_date.date()}"
        )

    # ── Sales amount approximately equals unit_price * qty * (1 - discount) ──
    if {"unit_price", "quantity", "discount", "sales_amount"}.issubset(df.columns):
        expected = (df["unit_price"] * df["quantity"] * (1 - df["discount"])).round(2)
        mismatch = ((df["sales_amount"] - expected).abs() / df["sales_amount"].replace(0, np.nan) > 0.01)
        n_mismatch = int(mismatch.sum())
        check(
            "sales_amount_consistent_with_formula",
            n_mismatch == 0,
            level="WARN",
            note=f"{n_mismatch} rows differ >1% from computed value"
        )

    # ── KPI sanity: total sales > 0 ───────────────────────────────────────────
    if "sales_amount" in df.columns:
        total = float(df["sales_amount"].sum())
        check("total_sales_positive", total > 0, note=f"₹{total:,.2f}")

    # ── Determine overall status ───────────────────────────────────────────────
    statuses = [c["status"] for c in checks]
    if "FAIL" in statuses:
        overall = "FAIL"
    elif "WARN" in statuses:
        overall = "WARN"
    else:
        overall = "PASS"

    fail_count = statuses.count("FAIL")
    warn_count = statuses.count("WARN")
    pass_count = statuses.count("PASS")
    summary = (
        f"Overall: {overall} | "
        f"PASS: {pass_count} | WARN: {warn_count} | FAIL: {fail_count} | "
        f"Total checks: {len(checks)}"
    )

    return {"checks": checks, "overall": overall, "summary": summary}


def print_validation_report(report: dict) -> None:
    """Pretty-print the validation report to stdout."""
    print("\n" + "=" * 60)
    print("DATA VALIDATION REPORT")
    print("=" * 60)
    for c in report["checks"]:
        icon = "✓" if c["status"] == "PASS" else ("⚠" if c["status"] == "WARN" else "✗")
        print(f"  {icon} [{c['status']:<4}] {c['check']:<45} {c['note']}")
    print("-" * 60)
    print(f"  {report['summary']}")
    print("=" * 60 + "\n")

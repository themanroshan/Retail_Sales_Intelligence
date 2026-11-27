"""
RetailPulse — Excel Export
===========================
Generates RetailPulse_Analysis.xlsx using openpyxl.
Run with:
    python -m src.excel_export
"""

import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows

from src.config import PROCESSED_FILE, EXCEL_DIR
from src.data_loader import load_processed
from src.analytics import (
    kpi_summary, monthly_sales_trend, sales_by_category,
    sales_by_subcategory, top_products_by_sales, sales_by_state,
    sales_by_payment_method, discount_impact
)


# ── Style constants ───────────────────────────────────────────────────────────
HEADER_FILL   = PatternFill("solid", fgColor="1F3864")   # Dark navy
HEADER_FONT   = Font(bold=True, color="FFFFFF", size=11)
SUBHEAD_FILL  = PatternFill("solid", fgColor="2E75B6")   # Medium blue
SUBHEAD_FONT  = Font(bold=True, color="FFFFFF", size=10)
ALT_FILL      = PatternFill("solid", fgColor="EBF3FB")   # Light blue alt row
BORDER_SIDE   = Side(style="thin", color="B8CCE4")
THIN_BORDER   = Border(
    left=BORDER_SIDE, right=BORDER_SIDE,
    top=BORDER_SIDE,  bottom=BORDER_SIDE
)
CURRENCY_FMT  = '₹#,##0.00'
PCT_FMT       = '0.00%'
NUM_FMT       = '#,##0'


def _style_header_row(ws, row_num: int, n_cols: int) -> None:
    for col in range(1, n_cols + 1):
        cell = ws.cell(row=row_num, column=col)
        cell.fill   = HEADER_FILL
        cell.font   = HEADER_FONT
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _auto_col_width(ws) -> None:
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                val = str(cell.value) if cell.value is not None else ""
                max_len = max(max_len, len(val))
            except Exception:
                pass
        ws.column_dimensions[col_letter].width = min(max_len + 4, 40)


def _write_df(ws, df: pd.DataFrame, start_row: int = 1, header: bool = True) -> int:
    """Write DataFrame to worksheet. Returns the last row written."""
    rows = list(dataframe_to_rows(df, index=False, header=header))
    for r_idx, row in enumerate(rows, start=start_row):
        for c_idx, value in enumerate(row, start=1):
            ws.cell(row=r_idx, column=c_idx, value=value)
    if header and rows:
        _style_header_row(ws, start_row, len(rows[0]))
    return start_row + len(rows) - 1


def build_excel(output_path: Path = None) -> Path:
    if output_path is None:
        EXCEL_DIR.mkdir(parents=True, exist_ok=True)
        output_path = EXCEL_DIR / "RetailPulse_Analysis.xlsx"

    # Load data
    df = load_processed()
    kpis = kpi_summary(df)
    monthly  = monthly_sales_trend(df)
    cat_df   = sales_by_category(df)
    subcat   = sales_by_subcategory(df)
    products = top_products_by_sales(df, n=20)
    states   = sales_by_state(df)
    payments = sales_by_payment_method(df)
    disc     = discount_impact(df)

    wb = openpyxl.Workbook()

    # ── Sheet 1: Executive Summary ────────────────────────────────────────────
    ws = wb.active
    ws.title = "Executive Summary"
    ws["A1"] = "RetailPulse — Indian Retail Sales Intelligence"
    ws["A1"].font = Font(bold=True, size=16, color="1F3864")
    ws["A2"] = f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}"
    ws["A2"].font = Font(italic=True, size=10, color="666666")
    ws["A3"] = "DATA NOTE: This dataset is SYNTHETIC — generated for portfolio demonstration."
    ws["A3"].font = Font(bold=True, color="CC0000", size=10)

    ws["A5"] = "KEY PERFORMANCE INDICATORS"
    ws["A5"].font = Font(bold=True, size=12, color="1F3864")

    kpi_rows = [
        ("Total Sales (INR)",         f"₹{kpis['total_sales']:,.2f}"),
        ("Total Orders",              f"{kpis['total_orders']:,}"),
        ("Total Units Sold",          f"{kpis['total_units_sold']:,}"),
        ("Average Order Value (INR)", f"₹{kpis['avg_order_value']:,.2f}"),
        ("Average Selling Price",     f"₹{kpis['avg_selling_price']:,.2f}"),
        ("Total Profit (INR)",        f"₹{kpis['total_profit']:,.2f}"),
        ("Overall Profit Margin",     f"{kpis['profit_margin_pct']}%"),
        ("Average Discount",          f"{kpis['avg_discount_pct']}%"),
    ]
    for i, (k, v) in enumerate(kpi_rows, start=6):
        ws[f"A{i}"] = k
        ws[f"B{i}"] = v
        ws[f"A{i}"].font = Font(bold=True)
        ws[f"B{i}"].alignment = Alignment(horizontal="right")

    ws["A15"] = "Top Categories by Sales"
    ws["A15"].font = Font(bold=True, size=11, color="2E75B6")
    _write_df(ws, cat_df[["category","total_sales","sales_share_pct","profit_margin_pct"]].head(8), start_row=16)

    _auto_col_width(ws)
    ws.freeze_panes = "A6"

    # ── Sheet 2: Cleaned Data ─────────────────────────────────────────────────
    ws2 = wb.create_sheet("Cleaned Data")
    _write_df(ws2, df.head(5000))   # Cap at 5000 rows for Excel usability
    _auto_col_width(ws2)
    ws2["A1"].comment = None

    # ── Sheet 3: Monthly Analysis ─────────────────────────────────────────────
    ws3 = wb.create_sheet("Monthly Analysis")
    ws3["A1"] = "Monthly Sales Trend"
    ws3["A1"].font = Font(bold=True, size=13, color="1F3864")
    _write_df(ws3, monthly, start_row=3)
    _auto_col_width(ws3)

    # ── Sheet 4: Category Analysis ────────────────────────────────────────────
    ws4 = wb.create_sheet("Category Analysis")
    ws4["A1"] = "Sales by Category"
    ws4["A1"].font = Font(bold=True, size=13, color="1F3864")
    _write_df(ws4, cat_df, start_row=3)
    ws4["A18"] = "Sales by Sub-Category"
    ws4["A18"].font = Font(bold=True, size=12, color="2E75B6")
    _write_df(ws4, subcat, start_row=19)
    _auto_col_width(ws4)

    # ── Sheet 5: Product Analysis ─────────────────────────────────────────────
    ws5 = wb.create_sheet("Product Analysis")
    ws5["A1"] = "Top 20 Products by Sales"
    ws5["A1"].font = Font(bold=True, size=13, color="1F3864")
    _write_df(ws5, products, start_row=3)
    _auto_col_width(ws5)

    # ── Sheet 6: Regional Analysis ────────────────────────────────────────────
    ws6 = wb.create_sheet("Regional Analysis")
    ws6["A1"] = "Sales by State"
    ws6["A1"].font = Font(bold=True, size=13, color="1F3864")
    _write_df(ws6, states, start_row=3)
    _auto_col_width(ws6)

    # ── Sheet 7: Payment Methods ──────────────────────────────────────────────
    ws7 = wb.create_sheet("Payment Methods")
    ws7["A1"] = "Sales by Payment Method"
    ws7["A1"].font = Font(bold=True, size=13, color="1F3864")
    _write_df(ws7, payments, start_row=3)
    _auto_col_width(ws7)

    # ── Sheet 8: Discount Analysis ────────────────────────────────────────────
    ws8 = wb.create_sheet("Discount Analysis")
    ws8["A1"] = "Impact of Discount Buckets on Sales"
    ws8["A1"].font = Font(bold=True, size=13, color="1F3864")
    _write_df(ws8, disc, start_row=3)
    _auto_col_width(ws8)

    # ── Sheet 9: KPI Definitions ──────────────────────────────────────────────
    ws9 = wb.create_sheet("KPI Definitions")
    kpi_def_rows = [
        ("KPI", "Formula", "Unit", "Limitation"),
        ("Total Sales", "SUM(sales_amount)", "INR", "Post-discount revenue; excludes returns"),
        ("Total Orders", "COUNT(DISTINCT order_id)", "Count", "One order may have multiple rows"),
        ("Total Units Sold", "SUM(quantity)", "Units", "Includes all categories"),
        ("Avg Order Value", "Total Sales / Total Orders", "INR", "Sales-weighted, not basket count"),
        ("Avg Selling Price", "AVG(unit_price)", "INR", "Pre-discount list price"),
        ("Total Profit", "SUM(profit)", "INR", "Synthetic margin; not real financial data"),
        ("Profit Margin %", "Total Profit / Total Sales × 100", "%", "Overall blended margin"),
        ("Avg Discount %", "Discount Amount / Gross Sales × 100", "%", "Sales-weighted average"),
        ("Sales Share %", "Category Sales / Total Sales × 100", "%", "Concentration measure"),
        ("MoM Growth %", "(Current Month − Prior Month) / Prior Month × 100", "%", "First month has no prior"),
    ]
    for i, row_data in enumerate(kpi_def_rows, start=1):
        for j, val in enumerate(row_data, start=1):
            ws9.cell(row=i, column=j, value=val)
    _style_header_row(ws9, 1, 4)
    _auto_col_width(ws9)

    # ── Sheet 10: Data Quality ────────────────────────────────────────────────
    ws10 = wb.create_sheet("Data Quality")
    from src.data_loader import inspect_schema
    schema = inspect_schema(df)
    dq_rows = [
        ("Metric", "Value"),
        ("Total clean rows", schema["rows"]),
        ("Total columns", schema["columns"]),
        ("Date range (min)", schema["date_min"][:10]),
        ("Date range (max)", schema["date_max"][:10]),
        ("Duplicate rows (clean)", schema["duplicate_rows"]),
    ]
    for col_name, null_ct in schema["null_counts"].items():
        dq_rows.append((f"Nulls: {col_name}", null_ct))
    for i, row_data in enumerate(dq_rows, start=1):
        ws10.cell(row=i, column=1, value=row_data[0])
        ws10.cell(row=i, column=2, value=row_data[1])
    _style_header_row(ws10, 1, 2)
    _auto_col_width(ws10)

    wb.save(output_path)
    print(f"[excel_export] Saved → {output_path}")
    return output_path


if __name__ == "__main__":
    path = build_excel()
    print(f"Excel workbook ready: {path}")

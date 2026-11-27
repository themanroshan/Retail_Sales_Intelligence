# RetailPulse — Data Quality Report

## Pipeline Run Details

| Field             | Value                              |
|-------------------|------------------------------------|
| Run date          | November 2026                      |
| Input file        | data/raw/retailpulse_transactions.csv |
| Input rows        | 10,000                             |
| Seed              | 42 (deterministic)                 |
| Python version    | 3.14.10                            |
| Pandas version    | 3.1.1                              |

---

## Cleaning Audit Summary

| Metric                | Value   |
|-----------------------|---------|
| Original rows         | 10,000  |
| Clean rows            | 10,000  |
| Quarantined rows      | 0       |
| Duplicate rows        | 0       |
| Sales mismatches      | 0       |
| **Retention rate**    | **100.0%** |

---

## Cleaning Rules Applied

| Rule                              | Rows Flagged | Action                              |
|-----------------------------------|--------------|-------------------------------------|
| Unparseable date                  | 0            | Quarantine                          |
| Invalid quantity (≤ 0)            | 0            | Quarantine                          |
| Invalid unit_price (≤ 0)          | 0            | Quarantine                          |
| Discount outside [0, 1]           | 0            | Quarantine                          |
| Invalid sales_amount (≤ 0)        | 0            | Quarantine                          |
| Sales amount mismatch > 1%        | 0            | Flag (not quarantine)               |
| Duplicate (order_id, product_id)  | 0            | Quarantine first duplicate          |
| Missing payment_method            | 0            | Fill with "Unknown"                 |
| Whitespace in text columns        | Treated      | Stripped (cosmetic, no rows removed)|
| Category casing                   | Treated      | Title-cased (cosmetic)              |
| State/city casing                 | Treated      | Title-cased (cosmetic)              |

**Note:** 100% retention rate is expected for synthetic data generated with seed=42. For real production data, expect 2–10% quarantine rates due to source quality issues.

---

## Validation Report

All 17 validation checks passed.

| Check                                     | Status | Detail               |
|-------------------------------------------|--------|----------------------|
| row_count_positive                        | ✅ PASS | 10,000 rows          |
| no_nulls_order_id                         | ✅ PASS | 0 nulls              |
| no_nulls_order_date                       | ✅ PASS | 0 nulls              |
| no_nulls_category                         | ✅ PASS | 0 nulls              |
| no_nulls_quantity                         | ✅ PASS | 0 nulls              |
| no_nulls_unit_price                       | ✅ PASS | 0 nulls              |
| no_nulls_sales_amount                     | ✅ PASS | 0 nulls              |
| quantity_positive                         | ✅ PASS | 0 invalid            |
| unit_price_positive                       | ✅ PASS | 0 invalid            |
| discount_valid_range                      | ✅ PASS | 0 out of range       |
| sales_amount_positive                     | ✅ PASS | 0 invalid            |
| no_duplicate_order_product                | ✅ PASS | 0 duplicates         |
| order_date_parseable                      | ✅ PASS | 0 unparseable        |
| order_date_reasonable_range               | ✅ PASS | Min: 2022-01-01      |
| order_date_not_future                     | ✅ PASS | Max: 2024-12-31      |
| sales_amount_consistent_with_formula      | ✅ PASS | 0 rows differ >1%    |
| total_sales_positive                      | ✅ PASS | ₹74,447,185.53       |

**Overall: PASS**

---

## MySQL Idempotency Check

The pipeline uses `INSERT IGNORE` with a composite primary key `(order_id, product_id)`.

Running `python src/pipeline.py` a second time inserts 0 additional rows.

| Run  | Rows Inserted | Rows Skipped |
|------|--------------|--------------|
| 1st  | 10,000       | 0            |
| 2nd  | 0            | 10,000       |

---

## Numeric Statistics (Clean Data)

| Column       | Min         | Median       | Mean         | Max          |
|--------------|-------------|--------------|--------------|--------------|
| quantity     | 1           | 1            | 2.27         | 6            |
| unit_price   | ₹50.00      | ₹2,142.72    | ₹5,891.08    | ₹84,962.14   |
| discount     | 0.00        | 0.10         | 0.11         | 0.40         |
| sales_amount | ₹50.00      | ₹2,145.56    | ₹7,444.72    | ₹204,432.00  |
| profit       | ₹4.00       | ₹577.27      | ₹2,290.65    | ₹102,216.00  |

---

## Category Distribution

| Category                  | Rows  | Share % |
|---------------------------|-------|---------|
| Electronics               | 2,004 | 20.04%  |
| Clothing                  | 1,793 | 17.93%  |
| Home & Kitchen            | 1,392 | 13.92%  |
| Beauty & Personal Care    | 1,192 | 11.92%  |
| Sports & Fitness          | 998   | 9.98%   |
| Grocery & Food            | 999   | 9.99%   |
| Books                     | 822   | 8.22%   |
| Toys & Games              | 800   | 8.00%   |

---

## Known Limitations of This Data Quality Report

1. This report reflects a synthetic dataset with no real quality issues by design.
2. For a real dataset, expect failed checks in categories like unparseable dates, duplicate orders, and missing products.
3. The 100% retention rate is a property of synthetic generation, not a goal to target for real data.

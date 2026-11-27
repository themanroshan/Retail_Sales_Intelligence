# RetailPulse — Methodology

## 1. Dataset Selection Methodology

### Research process
During Phase 2 of the project, I searched for Indian retail transaction datasets on Kaggle and evaluated three candidates using the following criteria:

| Criterion           | Minimum Requirement                                                 |
|---------------------|---------------------------------------------------------------------|
| Row count           | > 1,000 transactions                                               |
| Date fields         | Actual transaction dates (not just order numbers)                  |
| Licence             | Explicitly permits portfolio/educational use and redistribution     |
| Geographic coverage | India-specific (INR currency, Indian city/state names)             |
| Fields required     | At minimum: order_id, date, category, quantity, price or amount    |

### Candidates evaluated

1. **E-Commerce Data (benroshan, Kaggle)** — 500 rows, licence not clearly stated
2. **Indian E-Commerce Sales (various Kaggle uploads)** — licence varies, most unclear
3. **Sample Superstore** — US-based, USD, not India-specific

**Decision:** None of the candidates met all criteria within the two-day timeframe. Generated a deterministic synthetic dataset instead.

### Why synthetic data is acceptable for this portfolio
- The analytical methodology (cleaning, SQL, dashboard) is identical whether data is real or synthetic
- Synthetic data eliminates licence risk
- Fixed seed = fully reproducible (every reviewer gets identical results)
- Transparently labeled throughout — no deception

---

## 2. Data Cleaning Methodology

### Philosophy
- Do not silently drop data
- Record every cleaning decision in an audit trail
- Quarantine bad rows separately — never delete them
- Less destructive treatments preferred (fill missing values vs. drop rows)

### Rules hierarchy
1. **Structural checks first:** date parsing, data type coercion
2. **Value range checks:** quantity > 0, price > 0, discount ∈ [0,1], amount > 0
3. **Consistency checks:** sales ≈ price × qty × (1−disc) within 1% tolerance
4. **Deduplication:** remove rows with duplicate (order_id, product_id)
5. **Imputation:** fill missing payment_method with "Unknown"

### Decision log

| Decision                              | Alternative                | Reason                                              |
|---------------------------------------|----------------------------|-----------------------------------------------------|
| Quarantine bad rows (not delete)      | Delete bad rows            | Preserves audit trail; allows later review          |
| Fill missing payment_method           | Drop rows                  | Payment method is non-critical; don't lose sales data |
| 1% tolerance for sales mismatch       | 0% tolerance               | Rounding differences in source data are common      |
| Title-case categories and states      | Leave as-is                | Prevents duplicate groups from case differences      |

---

## 3. Database Design Methodology

### Schema choice: Star Schema
Chosen over flat table because:
- Shows BI/warehouse design knowledge expected at fresher DA level
- Demonstrates understanding of normalization
- Enables realistic SQL queries with JOINs
- Product category is stored once — not duplicated across 10,000 rows

### Grain definition
**fact_sales grain:** One row per unique (order_id, product_id) combination — one line in an order.

This means:
- One order with 2 products = 2 rows in fact_sales
- Total orders = COUNT(DISTINCT order_id)
- Total products sold = COUNT(*) or SUM(quantity)

### Surrogate key decision
dim_location uses an auto-increment `location_id` surrogate key rather than a natural key combination of (state, city). This is because:
- Natural keys can change (city name spelling)
- Surrogate keys are more stable and join-efficient

---

## 4. KPI Calculation Methodology

### Two-pass vs. one-pass calculations

Average Order Value (AOV) requires two passes:
1. Sum sales_amount per order_id
2. Average those order totals

A single-pass `AVG(sales_amount)` gives the average row-level sales, which is different and incorrect for AOV. All KPI formulas are documented in `docs/KPI_DEFINITIONS.md`.

### Consistency rule
All KPI functions in `src/analytics.py` accept the same DataFrame. When a filter is applied in the dashboard sidebar, the filtered DataFrame is passed to all functions simultaneously. This ensures KPI cards, charts, and tables always reflect the same data.

---

## 5. SQL Query Methodology

### Script organisation
SQL scripts are numbered and ordered for a first-time setup:
1. Database creation
2. Table creation
3. Data quality checks (run first, before analysis)
4. Exploratory queries (simple aggregations)
5. Business analysis (14 specific questions)
6. Advanced analysis (window functions, complex CTEs)

### Query documentation standard
Every SQL query includes:
- Business question comment
- Logic explanation
- Expected output format
- Analyst interpretation note

This makes the SQL readable for non-technical reviewers (interviewers, hiring managers).

---

## 6. Testing Methodology

### Test categories
1. **Unit tests** — test individual functions in isolation (e.g., `test_no_negative_quantity_in_clean`)
2. **Integration tests** — test the full pipeline flow (e.g., `test_full_pipeline_no_db`)
3. **Contract tests** — verify the DataFrame schema and column presence
4. **Conditional tests** — MySQL tests are conditionally skipped when MySQL is unavailable

### Test design principles
- Tests must run without MySQL (graceful skip)
- Tests must be deterministic (use seed=42)
- Tests verify both positive cases (clean data passes) and negative cases (bad data quarantined)
- No test relies on hardcoded values that might change — use relative assertions (> 0, between 0 and 1)

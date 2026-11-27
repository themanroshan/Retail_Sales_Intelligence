-- =============================================================================
-- RetailPulse — Script 03: Data Quality Checks
-- =============================================================================
-- Purpose  : Verify data integrity after ETL pipeline load.
--            Run these queries in MySQL Workbench and review every result.
-- Expected : Every check should return 0 problem rows.
-- =============================================================================

USE retailpulse;

-- ── CHECK 1: Row counts ───────────────────────────────────────────────────────
-- Business purpose: Confirm that the pipeline loaded the expected volume of data.
SELECT
    'dim_product'  AS table_name, COUNT(*) AS row_count FROM dim_product
UNION ALL
SELECT 'dim_location',            COUNT(*) FROM dim_location
UNION ALL
SELECT 'dim_date',                COUNT(*) FROM dim_date
UNION ALL
SELECT 'fact_sales',              COUNT(*) FROM fact_sales;


-- ── CHECK 2: Orphaned fact rows (FK violations would have been caught by InnoDB) ──
-- Business purpose: Every fact row must have a valid product and location.
SELECT
    'fact missing product'  AS check_name,
    COUNT(*) AS problem_rows
FROM fact_sales f
LEFT JOIN dim_product p ON f.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

SELECT
    'fact missing location',
    COUNT(*)
FROM fact_sales f
LEFT JOIN dim_location l ON f.location_id = l.location_id
WHERE l.location_id IS NULL;


-- ── CHECK 3: Negative or zero sales_amount ────────────────────────────────────
-- Business purpose: Every transaction must have a positive revenue figure.
SELECT
    'negative or zero sales_amount' AS check_name,
    COUNT(*) AS problem_rows
FROM fact_sales
WHERE sales_amount <= 0;


-- ── CHECK 4: Invalid quantity ─────────────────────────────────────────────────
SELECT
    'quantity <= 0' AS check_name,
    COUNT(*) AS problem_rows
FROM fact_sales
WHERE quantity <= 0;


-- ── CHECK 5: Discount out of range ───────────────────────────────────────────
SELECT
    'discount outside [0, 1]' AS check_name,
    COUNT(*) AS problem_rows
FROM fact_sales
WHERE discount < 0 OR discount > 1;


-- ── CHECK 6: Null values in critical columns ──────────────────────────────────
SELECT
    'nulls in fact_sales key columns' AS check_name,
    SUM(
        CASE WHEN order_id       IS NULL THEN 1 ELSE 0 END +
        CASE WHEN order_date     IS NULL THEN 1 ELSE 0 END +
        CASE WHEN product_id     IS NULL THEN 1 ELSE 0 END +
        CASE WHEN sales_amount   IS NULL THEN 1 ELSE 0 END
    ) AS problem_rows
FROM fact_sales;


-- ── CHECK 7: Date range sanity ────────────────────────────────────────────────
-- Business purpose: Confirm dates fall within the expected project window.
SELECT
    MIN(order_date) AS earliest_date,
    MAX(order_date) AS latest_date,
    COUNT(DISTINCT order_date) AS distinct_dates,
    DATEDIFF(MAX(order_date), MIN(order_date)) AS date_span_days
FROM fact_sales;


-- ── CHECK 8: Sales amount vs. computed value ──────────────────────────────────
-- Business purpose: Detect rounding or ETL errors in the sales_amount field.
-- Expected: 0 rows where the difference exceeds 1 INR.
SELECT
    COUNT(*) AS rows_with_mismatch,
    AVG(ABS(sales_amount - ROUND(unit_price * quantity * (1 - discount), 2))) AS avg_diff_inr
FROM fact_sales
WHERE ABS(sales_amount - ROUND(unit_price * quantity * (1 - discount), 2)) > 1.00;


-- ── CHECK 9: Duplicate order-product combinations ─────────────────────────────
-- Primary key constraint enforces this, but explicit check for peace of mind.
SELECT
    'duplicate order_id + product_id' AS check_name,
    COUNT(*) - COUNT(DISTINCT CONCAT(order_id, '|', product_id)) AS problem_rows
FROM fact_sales;


-- ── CHECK 10: Category distribution ─────────────────────────────────────────
-- Business purpose: Confirm all 8 categories loaded correctly.
SELECT
    p.category,
    COUNT(DISTINCT f.product_id) AS distinct_products,
    COUNT(*)                     AS transaction_rows,
    ROUND(SUM(f.sales_amount), 2) AS total_sales_inr
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY total_sales_inr DESC;

-- =============================================================================
-- RetailPulse — Script 05: Business Analysis
-- =============================================================================
-- Purpose  : Answer the 14 core business questions from the project brief.
--            Uses JOINs, CTEs, CASE, HAVING, subqueries, window functions.
-- =============================================================================

USE retailpulse;

-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-01: What is total recorded sales?
-- ══════════════════════════════════════════════════════════════════════════════
-- Logic : Simple aggregate on the fact table.
-- Output: One row — total sales in INR.
-- Analyst note: This is post-discount revenue, not gross list-price revenue.
SELECT
    ROUND(SUM(sales_amount), 2) AS total_sales_inr
FROM fact_sales;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-02: How many distinct transactions/orders exist?
-- ══════════════════════════════════════════════════════════════════════════════
SELECT
    COUNT(DISTINCT order_id) AS total_orders
FROM fact_sales;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-03: How many units were sold in total?
-- ══════════════════════════════════════════════════════════════════════════════
SELECT
    SUM(quantity) AS total_units_sold
FROM fact_sales;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-04: Which categories contribute most to sales? (Pareto view)
-- ══════════════════════════════════════════════════════════════════════════════
-- Logic : Use a CTE to calculate total, then compute running share.
-- Output: Category, sales, % share, cumulative % share.
-- Analyst note: Identify if 2–3 categories drive 80% of revenue (Pareto rule).
WITH cat_sales AS (
    SELECT
        p.category,
        ROUND(SUM(f.sales_amount), 2) AS total_sales
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    GROUP BY p.category
),
total AS (
    SELECT SUM(total_sales) AS grand_total FROM cat_sales
)
SELECT
    c.category,
    c.total_sales,
    ROUND(c.total_sales / t.grand_total * 100, 2)   AS sales_share_pct,
    ROUND(
        SUM(c.total_sales) OVER (ORDER BY c.total_sales DESC
                                  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        / t.grand_total * 100, 2
    ) AS cumulative_share_pct
FROM cat_sales c, total t
ORDER BY c.total_sales DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-05: Which products perform best? (Top 10 by sales)
-- ══════════════════════════════════════════════════════════════════════════════
SELECT
    p.product_name,
    p.category,
    COUNT(DISTINCT f.order_id)       AS orders,
    SUM(f.quantity)                  AS units_sold,
    ROUND(SUM(f.sales_amount), 2)    AS total_sales_inr,
    ROUND(SUM(f.profit) / SUM(f.sales_amount) * 100, 2) AS profit_margin_pct,
    DENSE_RANK() OVER (ORDER BY SUM(f.sales_amount) DESC) AS sales_rank
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY sales_rank
LIMIT 10;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-06: Which regions contribute most?
-- ══════════════════════════════════════════════════════════════════════════════
SELECT
    l.state,
    COUNT(DISTINCT f.order_id)      AS orders,
    ROUND(SUM(f.sales_amount), 2)   AS total_sales_inr,
    ROUND(SUM(f.sales_amount) / (SELECT SUM(sales_amount) FROM fact_sales) * 100, 2) AS sales_share_pct,
    ROUND(SUM(f.profit), 2)         AS total_profit_inr,
    RANK() OVER (ORDER BY SUM(f.sales_amount) DESC) AS state_rank
FROM fact_sales f
JOIN dim_location l ON f.location_id = l.location_id
GROUP BY l.state
ORDER BY state_rank;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-07: What is the monthly sales trend?
-- ══════════════════════════════════════════════════════════════════════════════
-- Logic : Group by year_month, use LAG to compute MoM growth.
-- Output: Month, sales, previous month sales, growth %.
-- Analyst note: First month will have NULL growth — that is expected.
WITH monthly AS (
    SELECT
        year_month,
        COUNT(DISTINCT order_id)     AS orders,
        ROUND(SUM(sales_amount), 2)  AS total_sales
    FROM fact_sales
    GROUP BY year_month
)
SELECT
    year_month,
    orders,
    total_sales,
    LAG(total_sales) OVER (ORDER BY year_month)             AS prev_month_sales,
    ROUND(
        (total_sales - LAG(total_sales) OVER (ORDER BY year_month))
        / LAG(total_sales) OVER (ORDER BY year_month) * 100, 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY year_month;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-08: What are the strongest and weakest sales months?
-- ══════════════════════════════════════════════════════════════════════════════
-- Logic : Rank months by average sales across all years.
-- Analyst note: Useful for seasonal planning and staffing.
WITH monthly_avg AS (
    SELECT
        month,
        MONTHNAME(MIN(order_date))       AS month_name,
        ROUND(AVG(monthly_total), 2)     AS avg_monthly_sales
    FROM (
        SELECT
            year, month,
            SUM(sales_amount) AS monthly_total
        FROM fact_sales
        GROUP BY year, month
    ) sub
    GROUP BY month
)
SELECT
    month,
    month_name,
    avg_monthly_sales,
    RANK() OVER (ORDER BY avg_monthly_sales DESC) AS peak_rank
FROM monthly_avg
ORDER BY peak_rank;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-09: What is the average order value (AOV)?
-- ══════════════════════════════════════════════════════════════════════════════
-- Logic : Sum sales per order first, then average across orders.
-- Output: One row — AOV in INR.
-- Analyst note: AOV is order-level, not row-level. Averaging row-level
--               sales_amount would give a different (incorrect) figure.
SELECT
    ROUND(AVG(order_total), 2) AS avg_order_value_inr
FROM (
    SELECT order_id, SUM(sales_amount) AS order_total
    FROM fact_sales
    GROUP BY order_id
) order_summary;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-10: What is the average quantity per transaction?
-- ══════════════════════════════════════════════════════════════════════════════
SELECT
    ROUND(AVG(order_qty), 2) AS avg_items_per_order
FROM (
    SELECT order_id, SUM(quantity) AS order_qty
    FROM fact_sales
    GROUP BY order_id
) order_items;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-11: Which products show growing vs. declining sales? (Year-over-year)
-- ══════════════════════════════════════════════════════════════════════════════
-- Logic : Compare product sales between first and last full year in dataset.
-- Output: Products with YoY growth flag.
-- Analyst note: Only valid when dataset spans multiple years.
WITH yearly AS (
    SELECT
        f.product_id,
        p.product_name,
        p.category,
        f.year,
        ROUND(SUM(f.sales_amount), 2) AS yearly_sales
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    GROUP BY f.product_id, p.product_name, p.category, f.year
),
pivoted AS (
    SELECT
        product_id,
        product_name,
        category,
        MAX(CASE WHEN year = (SELECT MIN(year) FROM fact_sales) THEN yearly_sales END) AS sales_year1,
        MAX(CASE WHEN year = (SELECT MAX(year) FROM fact_sales) THEN yearly_sales END) AS sales_last_year
    FROM yearly
    GROUP BY product_id, product_name, category
)
SELECT
    product_name,
    category,
    COALESCE(sales_year1, 0)      AS first_year_sales,
    COALESCE(sales_last_year, 0)  AS last_year_sales,
    CASE
        WHEN sales_last_year > sales_year1  THEN 'Growing'
        WHEN sales_last_year < sales_year1  THEN 'Declining'
        WHEN sales_last_year = sales_year1  THEN 'Stable'
        ELSE 'Insufficient data'
    END AS trend
FROM pivoted
WHERE sales_year1 IS NOT NULL AND sales_last_year IS NOT NULL
ORDER BY last_year_sales DESC
LIMIT 20;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-12: How concentrated is sales across categories? (HHI-style)
-- ══════════════════════════════════════════════════════════════════════════════
-- Logic : Share squared, summed — a simple concentration measure.
--         Score near 1 = highly concentrated; near 0 = evenly distributed.
-- Analyst note: Tells you if the business is over-dependent on one category.
WITH shares AS (
    SELECT
        p.category,
        SUM(f.sales_amount) / (SELECT SUM(sales_amount) FROM fact_sales) AS share
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    GROUP BY p.category
)
SELECT
    ROUND(SUM(share * share), 4)  AS hhi_index,
    CASE
        WHEN SUM(share * share) > 0.25 THEN 'Highly Concentrated'
        WHEN SUM(share * share) > 0.10 THEN 'Moderately Concentrated'
        ELSE 'Diversified'
    END AS concentration_label
FROM shares;


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-13: What is the discount impact on sales and profit?
-- ══════════════════════════════════════════════════════════════════════════════
-- Logic : Bucket discounts, compare average profit margins per bucket.
-- Analyst note: If high-discount transactions show low margins, discounting
--               strategy may need revisiting.
SELECT
    CASE
        WHEN discount = 0.00         THEN '0% (No Discount)'
        WHEN discount <= 0.10        THEN '1–10%'
        WHEN discount <= 0.20        THEN '11–20%'
        WHEN discount <= 0.30        THEN '21–30%'
        WHEN discount <= 0.40        THEN '31–40%'
        ELSE '41%+'
    END AS discount_bucket,
    COUNT(DISTINCT order_id)                           AS orders,
    ROUND(SUM(sales_amount), 2)                        AS total_sales_inr,
    ROUND(AVG(discount) * 100, 2)                      AS avg_discount_pct,
    ROUND(SUM(profit) / SUM(sales_amount) * 100, 2)   AS profit_margin_pct
FROM fact_sales
GROUP BY discount_bucket
ORDER BY MIN(discount);


-- ══════════════════════════════════════════════════════════════════════════════
-- BQ-14: What is the profit contribution by category?
-- ══════════════════════════════════════════════════════════════════════════════
-- Logic : Profit and margin by category, ranked.
-- Analyst note: High sales ≠ high profit. This reveals profitability mix.
SELECT
    p.category,
    ROUND(SUM(f.profit), 2)                            AS total_profit_inr,
    ROUND(SUM(f.profit) / SUM(f.sales_amount) * 100, 2) AS profit_margin_pct,
    ROUND(SUM(f.profit) / (SELECT SUM(profit) FROM fact_sales) * 100, 2) AS profit_share_pct,
    RANK() OVER (ORDER BY SUM(f.profit) DESC)          AS profit_rank
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY profit_rank;

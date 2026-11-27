-- =============================================================================
-- RetailPulse — Script 06: Advanced Analysis
-- =============================================================================
-- Purpose  : Advanced SQL using window functions, CTEs, and subqueries.
--            Demonstrates deeper analytical capability for portfolio.
-- =============================================================================

USE retailpulse;

-- ══════════════════════════════════════════════════════════════════════════════
-- A1: Running total of monthly sales (cumulative sales over time)
-- ══════════════════════════════════════════════════════════════════════════════
WITH monthly AS (
    SELECT
        year_month,
        ROUND(SUM(sales_amount), 2) AS monthly_sales
    FROM fact_sales
    GROUP BY year_month
)
SELECT
    year_month,
    monthly_sales,
    ROUND(SUM(monthly_sales) OVER (ORDER BY year_month
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS cumulative_sales
FROM monthly
ORDER BY year_month;


-- ══════════════════════════════════════════════════════════════════════════════
-- A2: 3-month rolling average sales
-- ══════════════════════════════════════════════════════════════════════════════
WITH monthly AS (
    SELECT
        year_month,
        ROUND(SUM(sales_amount), 2) AS monthly_sales
    FROM fact_sales
    GROUP BY year_month
)
SELECT
    year_month,
    monthly_sales,
    ROUND(AVG(monthly_sales) OVER (ORDER BY year_month
          ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3m_avg
FROM monthly
ORDER BY year_month;


-- ══════════════════════════════════════════════════════════════════════════════
-- A3: Rank products within each category by total sales
-- ══════════════════════════════════════════════════════════════════════════════
WITH product_sales AS (
    SELECT
        p.category,
        p.product_name,
        ROUND(SUM(f.sales_amount), 2) AS total_sales
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    GROUP BY p.category, p.product_name
)
SELECT
    category,
    product_name,
    total_sales,
    RANK() OVER (PARTITION BY category ORDER BY total_sales DESC) AS rank_in_category
FROM product_sales
ORDER BY category, rank_in_category
LIMIT 40;


-- ══════════════════════════════════════════════════════════════════════════════
-- A4: Identify the top 3 states per category by sales
-- ══════════════════════════════════════════════════════════════════════════════
WITH state_cat AS (
    SELECT
        p.category,
        l.state,
        ROUND(SUM(f.sales_amount), 2)  AS total_sales,
        ROW_NUMBER() OVER (
            PARTITION BY p.category
            ORDER BY SUM(f.sales_amount) DESC
        ) AS rn
    FROM fact_sales f
    JOIN dim_product  p ON f.product_id  = p.product_id
    JOIN dim_location l ON f.location_id = l.location_id
    GROUP BY p.category, l.state
)
SELECT category, state, total_sales
FROM state_cat
WHERE rn <= 3
ORDER BY category, rn;


-- ══════════════════════════════════════════════════════════════════════════════
-- A5: Day-of-week sales pattern
-- ══════════════════════════════════════════════════════════════════════════════
-- Business purpose: Identify if weekends or specific weekdays drive more sales.
SELECT
    d.day_name,
    d.day_of_week,
    COUNT(DISTINCT f.order_id)       AS orders,
    ROUND(SUM(f.sales_amount), 2)    AS total_sales_inr,
    ROUND(AVG(f.sales_amount), 2)    AS avg_line_sales
FROM fact_sales f
JOIN dim_date d ON f.order_date = d.order_date
GROUP BY d.day_name, d.day_of_week
ORDER BY d.day_of_week;


-- ══════════════════════════════════════════════════════════════════════════════
-- A6: Sub-category profitability matrix
-- ══════════════════════════════════════════════════════════════════════════════
SELECT
    p.category,
    p.sub_category,
    ROUND(SUM(f.sales_amount), 2)                        AS total_sales,
    ROUND(SUM(f.profit), 2)                              AS total_profit,
    ROUND(SUM(f.profit) / SUM(f.sales_amount) * 100, 2) AS margin_pct,
    CASE
        WHEN SUM(f.profit) / SUM(f.sales_amount) >= 0.35 THEN 'High Margin'
        WHEN SUM(f.profit) / SUM(f.sales_amount) >= 0.20 THEN 'Medium Margin'
        ELSE 'Low Margin'
    END AS margin_tier
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category, p.sub_category
ORDER BY p.category, margin_pct DESC;


-- ══════════════════════════════════════════════════════════════════════════════
-- A7: Year-over-year comparison (if multi-year data exists)
-- ══════════════════════════════════════════════════════════════════════════════
SELECT
    year,
    COUNT(DISTINCT order_id)     AS orders,
    SUM(quantity)                AS units_sold,
    ROUND(SUM(sales_amount), 2)  AS total_sales_inr,
    ROUND(SUM(profit), 2)        AS total_profit_inr
FROM fact_sales
GROUP BY year
ORDER BY year;


-- ══════════════════════════════════════════════════════════════════════════════
-- A8: Top cities within top 3 states
-- ══════════════════════════════════════════════════════════════════════════════
WITH top_states AS (
    SELECT l.state
    FROM fact_sales f
    JOIN dim_location l ON f.location_id = l.location_id
    GROUP BY l.state
    ORDER BY SUM(f.sales_amount) DESC
    LIMIT 3
)
SELECT
    l.state,
    l.city,
    COUNT(DISTINCT f.order_id)      AS orders,
    ROUND(SUM(f.sales_amount), 2)   AS total_sales_inr
FROM fact_sales f
JOIN dim_location l ON f.location_id = l.location_id
WHERE l.state IN (SELECT state FROM top_states)
GROUP BY l.state, l.city
ORDER BY l.state, total_sales_inr DESC;

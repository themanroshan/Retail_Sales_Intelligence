-- =============================================================================
-- RetailPulse — Script 04: Exploratory Analysis
-- =============================================================================
-- Purpose  : Initial data exploration queries.
--            Run after pipeline and data quality checks pass.
-- =============================================================================

USE retailpulse;

-- ── Q1: Headline KPIs ─────────────────────────────────────────────────────────
-- Business question: What is the overall scale of this retail dataset?
-- Logic: Count distinct orders, sum sales, sum profit, compute margin.
-- Interpretation: These are the first numbers an executive dashboard would show.
SELECT
    COUNT(DISTINCT order_id)              AS total_orders,
    SUM(quantity)                         AS total_units_sold,
    ROUND(SUM(sales_amount), 2)           AS total_sales_inr,
    ROUND(SUM(profit), 2)                 AS total_profit_inr,
    ROUND(SUM(profit) / SUM(sales_amount) * 100, 2) AS profit_margin_pct,
    ROUND(SUM(sales_amount) / COUNT(DISTINCT order_id), 2) AS avg_order_value_inr
FROM fact_sales;


-- ── Q2: Sales distribution by category ─────────────────────────��─────────────
-- Business question: Which product categories drive the most revenue?
-- Logic: Join fact_sales with dim_product, group by category.
-- Interpretation: Focus marketing and inventory investment on top categories.
SELECT
    p.category,
    COUNT(DISTINCT f.order_id)             AS orders,
    SUM(f.quantity)                        AS units_sold,
    ROUND(SUM(f.sales_amount), 2)          AS total_sales_inr,
    ROUND(SUM(f.sales_amount) / (SELECT SUM(sales_amount) FROM fact_sales) * 100, 2) AS sales_share_pct,
    ROUND(SUM(f.profit) / SUM(f.sales_amount) * 100, 2) AS profit_margin_pct
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY total_sales_inr DESC;


-- ── Q3: Monthly order volume ──────────────────────────────────────────────────
-- Business question: How does sales volume change month by month?
-- Logic: Group by year_month, order chronologically.
-- Interpretation: Identify seasonal peaks and dips.
SELECT
    year_month,
    COUNT(DISTINCT order_id)     AS orders,
    SUM(quantity)                AS units_sold,
    ROUND(SUM(sales_amount), 2)  AS total_sales_inr
FROM fact_sales
GROUP BY year_month
ORDER BY year_month;


-- ── Q4: Top 15 products by sales ─────────────────────────────────────────────
-- Business question: Which individual products contribute most to revenue?
-- Logic: Group by product_id, sort by total sales descending.
-- Interpretation: These are your most important SKUs for procurement and display.
SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(DISTINCT f.order_id)       AS orders,
    SUM(f.quantity)                  AS units_sold,
    ROUND(SUM(f.sales_amount), 2)    AS total_sales_inr,
    ROUND(SUM(f.profit), 2)          AS total_profit_inr
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_sales_inr DESC
LIMIT 15;


-- ── Q5: Regional performance by state ────────────────────────────────────────
-- Business question: Which states generate the most revenue?
-- Logic: Join with dim_location, group by state.
-- Interpretation: Prioritise expansion and marketing spend in top states.
SELECT
    l.state,
    COUNT(DISTINCT f.order_id)      AS orders,
    ROUND(SUM(f.sales_amount), 2)   AS total_sales_inr,
    ROUND(SUM(f.profit), 2)         AS total_profit_inr,
    ROUND(SUM(f.profit) / SUM(f.sales_amount) * 100, 2) AS profit_margin_pct
FROM fact_sales f
JOIN dim_location l ON f.location_id = l.location_id
GROUP BY l.state
ORDER BY total_sales_inr DESC;


-- ── Q6: Payment method distribution ──────────────────────────────────────────
-- Business question: Which payment methods are most popular?
-- Logic: Group fact_sales by payment_method.
-- Interpretation: Invest in UX improvements for the most-used payment channels.
SELECT
    payment_method,
    COUNT(DISTINCT order_id)      AS orders,
    ROUND(SUM(sales_amount), 2)   AS total_sales_inr,
    ROUND(COUNT(DISTINCT order_id) / (SELECT COUNT(DISTINCT order_id) FROM fact_sales) * 100, 2) AS order_share_pct
FROM fact_sales
GROUP BY payment_method
ORDER BY orders DESC;


-- ── Q7: Average selling price by category ────────────────────────────────────
-- Business question: What is the typical price point in each category?
-- Logic: Average unit_price grouped by category.
-- Interpretation: Higher ASP categories may need fewer units to hit revenue targets.
SELECT
    p.category,
    ROUND(AVG(f.unit_price), 2)       AS avg_unit_price_inr,
    ROUND(AVG(f.discount) * 100, 2)   AS avg_discount_pct,
    ROUND(AVG(f.sales_amount), 2)     AS avg_line_sales_inr
FROM fact_sales f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY avg_unit_price_inr DESC;

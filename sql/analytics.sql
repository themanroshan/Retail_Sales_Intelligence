-- 10 business questions answered using SQL.
-- Copy-paste into MySQL Workbench after running the pipeline.

USE retail_sales;

-- Q1. How many orders, customers, and items in total?
SELECT
    (SELECT COUNT(DISTINCT order_id) FROM dim_order)         AS total_orders,
    (SELECT COUNT(DISTINCT user_id)  FROM dim_order)         AS total_customers,
    (SELECT COUNT(*)                 FROM fact_order_products) AS total_items_sold;

-- Q2. What is the average basket size?
SELECT ROUND(AVG(items_per_order), 2) AS avg_basket_size
FROM (
    SELECT order_id, COUNT(*) AS items_per_order
    FROM fact_order_products
    GROUP BY order_id
) t;

-- Q3. What is the overall reorder rate?
SELECT ROUND(AVG(reordered), 4) AS reorder_rate
FROM fact_order_products;

-- Q4. Top 10 departments by order volume
SELECT d.department, COUNT(*) AS order_lines
FROM fact_order_products f
JOIN dim_product    p ON f.product_id    = p.product_id
JOIN dim_department d ON p.department_id = d.department_id
GROUP BY d.department
ORDER BY order_lines DESC
LIMIT 10;

-- Q5. Top 10 aisles with highest reorder rate (min 500 lines)
SELECT a.aisle,
       COUNT(*) AS order_lines,
       ROUND(AVG(f.reordered), 4) AS reorder_rate
FROM fact_order_products f
JOIN dim_product p ON f.product_id = p.product_id
JOIN dim_aisle   a ON p.aisle_id   = a.aisle_id
GROUP BY a.aisle
HAVING COUNT(*) >= 500
ORDER BY reorder_rate DESC
LIMIT 10;

-- Q6. Top 15 products by order volume
SELECT p.product_name, COUNT(*) AS order_lines
FROM fact_order_products f
JOIN dim_product p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY order_lines DESC
LIMIT 15;

-- Q7. Day-of-week × hour demand heatmap
SELECT order_dow, order_hour_of_day, COUNT(*) AS orders
FROM dim_order
GROUP BY order_dow, order_hour_of_day
ORDER BY order_dow, order_hour_of_day;

-- Q8. Month-over-month growth (uses LAG window function)
WITH monthly AS (
    SELECT DATE_FORMAT(order_date, '%Y-%m-01') AS month, COUNT(*) AS orders
    FROM dim_order
    GROUP BY DATE_FORMAT(order_date, '%Y-%m-01')
)
SELECT
    month,
    orders,
    LAG(orders) OVER (ORDER BY month) AS prev_month,
    ROUND(
        (orders - LAG(orders) OVER (ORDER BY month))
        / LAG(orders) OVER (ORDER BY month) * 100, 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;

-- Q9. 7-day rolling average of daily orders
WITH daily AS (
    SELECT order_date, COUNT(*) AS daily_orders
    FROM dim_order
    GROUP BY order_date
)
SELECT
    order_date,
    daily_orders,
    ROUND(AVG(daily_orders) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_7d_avg
FROM daily
ORDER BY order_date;

-- Q10. Customer segmentation by number of orders
WITH user_orders AS (
    SELECT user_id, COUNT(DISTINCT order_id) AS orders
    FROM dim_order
    GROUP BY user_id
)
SELECT
    CASE
        WHEN orders = 1              THEN '1. One-time'
        WHEN orders BETWEEN 2 AND 5  THEN '2. Light (2-5)'
        WHEN orders BETWEEN 6 AND 15 THEN '3. Regular (6-15)'
        ELSE '4. Loyal (16+)'
    END AS segment,
    COUNT(*) AS users
FROM user_orders
GROUP BY segment
ORDER BY segment

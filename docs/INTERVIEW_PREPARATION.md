# RetailPulse — Interview Preparation Guide

> This guide prepares you to discuss the RetailPulse project confidently in Data Analyst and Business Analyst interviews.

---

## ⏱ 60-Second Project Pitch

> "I built RetailPulse, an end-to-end retail sales intelligence system. I started with a 10,000-row Indian retail transactions dataset — synthetic, clearly disclosed — and built a Python ETL pipeline that cleaned, validated, and loaded the data into a MySQL star schema database. I wrote over 50 SQL queries using JOINs, CTEs, and window functions to answer 14 business questions about category performance, regional sales, and discount impact. I built a 5-page Streamlit dashboard with Plotly charts and KPI cards, automated an Excel report with 10 sheets, and wrote 67 Pytest tests — all passed. The whole project is on GitHub and demonstrates the full data analyst workflow from raw data to business insights."

---

## 🗣 2-Minute Detailed Explanation

> "RetailPulse is my end-to-end retail sales analytics portfolio project.
>
> **Business problem:** An Indian multi-category retail business wants to understand which categories and regions drive revenue, what seasonal patterns exist, and how discounting affects profitability.
>
> **Data:** I used a synthetic dataset — 10,000 transactions covering 8 product categories and 12 Indian states from 2022 to 2024, generated with a fixed random seed so results are fully reproducible. I label it synthetic throughout the project to be transparent.
>
> **ETL pipeline:** I built a Python pipeline that generates or loads the raw CSV, applies 11 cleaning rules — removing invalid quantities, prices, and discounts; detecting duplicates; filling missing payment methods — and runs 17 automated validation checks. 100% of records passed.
>
> **Database:** I designed a MySQL star schema with 4 tables — fact_sales, dim_product, dim_location, and dim_date. The pipeline loads data using mysql-connector-python with INSERT IGNORE to prevent duplicates on re-runs.
>
> **SQL analysis:** I wrote 50+ SQL queries across 6 scripts, answering 14 business questions. I used CTEs, window functions like LAG and RANK, subqueries, HAVING clauses, and date functions.
>
> **Dashboard:** The Streamlit dashboard has 5 pages — Executive Overview, Product & Category, Time Analysis, Regional Analytics, and Data Quality. All pages use Plotly charts, have sidebar filters, and include CSV export.
>
> **Testing:** 67 Pytest tests cover data cleaning, validation, analytics, pipeline integration, and database connection. 7 MySQL tests are marked BLOCKED and skip gracefully when MySQL isn't available.
>
> Key finding from the synthetic data: Electronics drives 20% of sales, Beauty & Personal Care has the highest profit margin at 42%, and the Oct–Dec festive period shows the highest transaction volume."

---

## ⭐ STAR-Format Stories

### STAR 1 — Data Quality Challenge

**Situation:** When designing the ETL pipeline, I needed to decide how to handle problematic records rather than silently dropping them.

**Task:** Build a cleaning system that quarantines bad data while preserving a complete audit trail of every decision made.

**Action:** I implemented 11 cleaning rules that quarantine rows with invalid quantities, prices, or discounts into a separate quarantine DataFrame. I built an audit dict that records original rows, clean rows, quarantine rows, and the specific reason each row was flagged. For missing payment methods, I fill with "Unknown" rather than dropping — a less destructive choice.

**Result:** The audit trail clearly shows what was removed and why, making the pipeline defensible and reproducible. In the synthetic data, all 10,000 rows passed — but the system is production-ready for real data with actual quality issues.

---

### STAR 2 — SQL Window Functions

**Situation:** I needed to calculate month-over-month sales growth for the time analysis.

**Task:** Compute MoM growth rate for every month in the dataset using SQL.

**Action:** I used a CTE to aggregate monthly sales first, then applied the LAG window function to compare each month against the prior month: `(total_sales - LAG(total_sales) OVER (ORDER BY year_month)) / LAG(total_sales) * 100`. I documented that the first month will always return NULL (expected behavior — no prior month exists).

**Result:** The query correctly calculates MoM growth for all 36 months (Jan 2022 – Dec 2024). The window function approach is more efficient than a self-JOIN and easier to extend with other window functions like RANK or running totals.

---

### STAR 3 — Dashboard Design

**Situation:** I needed to build a dashboard that non-technical stakeholders could use, while also demonstrating technical depth.

**Task:** Design a 5-page Streamlit dashboard with consistent KPI definitions, working filters, and professional charts.

**Action:** I created a reusable components layer (`dashboard/components.py`) and a charts layer (`dashboard/charts.py`) to separate concerns. All pages read from the same filtered DataFrame passed through sidebar_filters(), ensuring every KPI and chart stays consistent when filters are applied. I added a data notice banner on every page to disclose the synthetic nature of the data.

**Result:** The dashboard reads consistently from either MySQL or CSV fallback, all 8 KPI cards update when filters change, and the charts layer has 12 reusable functions that can be called from any page.

---

## 💻 25 Technical Questions

### SQL Questions

**Q1: What is a CTE and when would you use one?**
A: A Common Table Expression is a named temporary result set defined within a WITH clause. I use CTEs when a subquery would be needed in multiple places (avoids repetition), when query readability matters, or for recursive queries. In RetailPulse, I used a CTE in BQ-07 to calculate monthly totals before applying LAG() on those totals.

**Q2: Explain the difference between RANK(), DENSE_RANK(), and ROW_NUMBER().**
A: ROW_NUMBER() assigns unique sequential numbers regardless of ties. RANK() leaves gaps after ties (1, 2, 2, 4). DENSE_RANK() does not leave gaps (1, 2, 2, 3). In BQ-05, I used DENSE_RANK() to rank products so ties get the same rank without skipping.

**Q3: What is a window function? Give an example from your project.**
A: A window function performs calculations across a set of rows related to the current row without collapsing them into groups. In BQ-07 I used `LAG(total_sales) OVER (ORDER BY year_month)` to access the prior month's sales for MoM growth calculation.

**Q4: What is the difference between WHERE and HAVING?**
A: WHERE filters rows before grouping; HAVING filters groups after aggregation. In BQ-05 (top aisles with min 500 lines from the old project), HAVING COUNT(*) >= 500 filters out groups with fewer than 500 rows.

**Q5: What is a star schema?**
A: A star schema has a central fact table surrounded by dimension tables. The fact table stores measurable, transactional events (each order line in RetailPulse). Dimension tables store descriptive attributes (product, location, date). It optimizes for analytical queries with simple JOINs from fact to dimensions.

**Q6: What indexes did you create and why?**
A: In fact_sales, I created indexes on `order_date`, `year_month`, `product_id`, and `location_id` because those are the columns most used in GROUP BY, JOIN, and WHERE clauses. The PRIMARY KEY on (order_id, product_id) also serves as a unique constraint preventing duplicate loads.

**Q7: How does INSERT IGNORE work?**
A: INSERT IGNORE silently skips rows that would violate a PRIMARY KEY or UNIQUE constraint rather than throwing an error. This makes the pipeline idempotent — you can re-run it without creating duplicates. The trade-off is that you need to check row counts separately to confirm whether rows were inserted or skipped.

**Q8: Write a SQL query to find the top 3 products per category by sales.**
A: 
```sql
WITH ranked AS (
    SELECT
        p.category,
        p.product_name,
        SUM(f.sales_amount) AS total_sales,
        ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(f.sales_amount) DESC) AS rn
    FROM fact_sales f
    JOIN dim_product p ON f.product_id = p.product_id
    GROUP BY p.category, p.product_name
)
SELECT category, product_name, total_sales
FROM ranked WHERE rn <= 3;
```
This is query A4 in `sql/06_advanced_analysis.sql`.

**Q9: How did you calculate average order value (AOV)?**
A: I first summed sales_amount per order_id (since each order can have multiple product lines), then averaged those order totals:
```sql
SELECT AVG(order_total) FROM (
    SELECT order_id, SUM(sales_amount) AS order_total
    FROM fact_sales GROUP BY order_id
) sub;
```
Averaging `sales_amount` directly (without the subquery) gives a row-level average, not an order-level average — which is the wrong figure.

**Q10: What is the HHI index? How did you use it?**
A: The Herfindahl-Hirschman Index measures market concentration. Each category's sales share is squared and summed. A score near 1 means one category dominates; near 0 means even distribution. I used it in BQ-12 to show whether the retail business is over-dependent on any single category.

**Q11: Explain the LAG function used in the monthly growth query.**
A: `LAG(total_sales) OVER (ORDER BY year_month)` returns the total_sales from the previous row (ordered by year_month). Subtracting it from the current month's sales and dividing by it gives MoM growth %. The first month returns NULL because there's no prior row — this is expected and I documented it.

**Q12: What is a foreign key? Why did you use them?**
A: A foreign key enforces referential integrity by requiring that a value in one table exists in another table. In fact_sales, `product_id` references `dim_product(product_id)` and `location_id` references `dim_location(location_id)`. This prevents orphaned fact rows where a dimension record doesn't exist. MySQL's InnoDB engine enforces these at the database level.

**Q13: What is EXPLAIN and when would you use it?**
A: EXPLAIN shows MySQL's query execution plan — which indexes are used, how tables are joined, and estimated row counts. I would use it to diagnose slow queries. If EXPLAIN shows "type: ALL" (full table scan), adding an index on the filtered or joined column usually fixes it.

**Q14: What is the difference between INNER JOIN and LEFT JOIN?**
A: INNER JOIN returns only rows where there's a match in both tables. LEFT JOIN returns all rows from the left table, with NULLs for unmatched rows from the right. In data quality check Q2, I used LEFT JOIN to find fact rows with no matching product — if the join succeeds, we have no orphans.

**Q15: How did you prevent duplicate rows in the MySQL load?**
A: By defining `PRIMARY KEY (order_id, product_id)` on fact_sales and using INSERT IGNORE. Any row with an already-existing (order_id, product_id) combination is silently skipped. I also check row counts in my tests to verify this works correctly.

---

### Python / Pandas Questions

**Q16: What is the difference between `.loc[]` and `.iloc[]`?**
A: `.loc[]` selects by label (row index value or column name). `.iloc[]` selects by integer position. In cleaning, I used `df.loc[mask, "payment_method"] = "Unknown"` to safely fill values where a boolean mask is True.

**Q17: How did you handle missing values in this project?**
A: Missing values in critical columns (order_date, quantity, unit_price, sales_amount) cause the row to be quarantined. Missing payment_method is filled with "Unknown" — a less destructive treatment since it's a non-critical dimension. I never silently drop rows without recording the reason.

**Q18: What is the difference between `.copy()` and assignment?**
A: When you do `df2 = df`, both variables point to the same underlying data. Modifying `df2` modifies `df`. Using `df2 = df.copy()` creates an independent copy. I use `.copy()` at the start of every transformation function to avoid accidentally mutating the original DataFrame passed in.

**Q19: How does `pd.read_csv()` handle data types?**
A: Pandas infers dtypes by default, which can misread IDs (like order_id) as integers if they look numeric. I specify `dtype={"order_id": str, "product_id": str}` in DTYPE_MAP to ensure string columns stay as strings. Numeric columns like quantity and sales_amount are explicitly coerced with `pd.to_numeric(errors='coerce')` which turns unparseable values into NaN.

**Q20: What is `groupby` and how did you use it?**
A: `groupby` splits a DataFrame into groups based on column values, allowing aggregation on each group. I used it extensively in `src/analytics.py`. For example, `sales_by_category()` does `df.groupby("category").agg(total_sales=("sales_amount","sum"))` to get sales per category.

---

### Business Analyst Questions

**Q21: What is an average order value (AOV) and what can it tell a business?**
A: AOV is total revenue divided by number of orders. It tells you the typical spend per transaction. A business would want to increase AOV through upselling, bundling, or minimum order thresholds for free shipping. In RetailPulse, AOV is ₹7,444.72 — higher in Electronics (expensive items) and lower in Grocery.

**Q22: What would you tell a manager whose top category by sales isn't the most profitable?**
A: Sales volume and profitability are different things. Electronics may have high revenue but thin margins (8–15%) due to competitive pricing. Beauty & Personal Care has lower absolute sales but 42% margins — meaning every rupee of sales delivers much more profit. The recommendation would be to invest in growing the high-margin categories while protecting the high-volume categories from price erosion.

**Q23: What are the limitations of this project?**
A: First, the data is synthetic — findings demonstrate methodology but not real retail trends. Second, without customer IDs, I can't calculate retention, LTV, or cohort analysis. Third, without actual cost data, profit figures are simulated margins, not real financial data. Fourth, geographic assignments are random, so regional insights are illustrative only.

**Q24: How would you present this project's findings to a non-technical stakeholder?**
A: I would start with the Executive Overview page — show the 8 headline KPIs, the monthly trend chart, and the category pie chart. Then I would move to the most important business question for them. For a category manager, I'd show the sub-category treemap. For a finance manager, I'd show the discount impact on margins. I would avoid technical terms like "CTE" or "JOIN" and instead say "I grouped the data by category" and "I calculated the profit after discounts."

**Q25: What would you change if you had more time?**
A: I would replace the synthetic data with a real licensed dataset to make the insights more credible. I would add customer-level analysis if customer IDs were available — RFM segmentation, repeat purchase rate, and cohort retention. I would also add a demand forecasting page using Prophet or SARIMA, and potentially integrate Power BI for stakeholders who prefer Excel-based tools.

---

## 💡 Possible Interviewer Challenges

### "Your data is synthetic — how is that useful?"

> "Using synthetic data is a deliberate choice, not a workaround. Real Indian retail transaction datasets on Kaggle have unclear licences that may prohibit redistribution in a portfolio. By generating synthetic data with a fixed seed, I get full reproducibility, clear licence ownership, and no risk of exposing proprietary business data. The *methodology* demonstrated here — the cleaning logic, validation checks, star schema design, SQL window functions, and dashboard architecture — applies identically to real data. When I find a licensed dataset, I can plug it in and all the analysis runs without changing a single line of code."

### "Why not use Power BI instead of Streamlit?"

> "Streamlit is code-first, which lets me version-control the dashboard, write unit tests for the data functions it uses, and demonstrate Python skills alongside BI skills. It also runs for free on Streamlit Cloud without a license. I considered Power BI as well — it's faster for prototyping — but for a portfolio project, the ability to show code, tests, and architecture was more important than visual polish. In a real job, I would use Power BI or Tableau if that's what the team uses."

### "How would you handle 10 million rows instead of 10,000?"

> "Several changes: I would switch from pandas CSV loading to chunked processing or Dask. I would use MySQL query pushdown rather than loading the full dataset into Python. For the dashboard, I would materialize the aggregations in a summary table rather than computing them on every request. I would add a caching layer using Redis or Streamlit's @st.cache_data. For SQL, I would add partitioning on order_date to speed up time-based queries. I would also consider a columnar database like ClickHouse for analytical workloads."

### "Why star schema instead of a flat table?"

> "A flat (denormalized) table is simpler to load but wastes storage and creates update anomalies — if a product's category changes, you'd need to update thousands of rows. A star schema stores product attributes once in dim_product, reducing duplication. The JOINs are simple (fact to dimension on a single key), and analytical queries benefit from indexes on the dimension foreign keys. For a 10,000-row portfolio dataset it doesn't matter much, but demonstrating star schema design shows I understand data warehouse principles."

---

## 📄 Resume Bullets (Two Versions)

### Version 1 — Concise (2 bullets)

> - Built **RetailPulse**, an end-to-end retail analytics platform processing 10,000 synthetic transactions using **Python (Pandas, NumPy), MySQL 8.0, and Streamlit**; designed a MySQL star schema, wrote 50+ SQL queries (CTEs, window functions, JOINs) answering 14 business questions, and built a 5-page interactive dashboard with Plotly visualizations
> - Implemented **67 Pytest tests** (100% passed) covering data cleaning, validation, analytics, and pipeline integration; automated Excel report generation (10 sheets, 657KB) using OpenPyXL; achieved 17/17 data quality validation checks PASS with 100% record retention rate

### Version 2 — Detailed (3 bullets)

> - Developed **RetailPulse**, a complete retail sales intelligence system: Python ETL pipeline with 11 cleaning rules and 17 validation checks; MySQL star schema (4 tables: fact_sales, dim_product, dim_location, dim_date); 50+ SQL queries using window functions, CTEs, and subqueries answering 14 business questions
> - Built a **5-page Streamlit dashboard** (Plotly charts, KPI cards, sidebar filters, CSV export) displaying total sales (₹74.4M), top categories (Electronics 20%, Clothing 18%), profit margins (42% Beauty & Personal Care), and regional performance across 12 Indian states; dashboard reads from MySQL or CSV fallback
> - Implemented **67 Pytest tests** (100% passed, 7 skipped for MySQL dependency), automated Excel workbook (10 sheets, OpenPyXL), and full project documentation including data dictionary, KPI definitions, SQL comments, and Windows 11 setup guide — full project on GitHub with Streamlit Cloud deployment

---

## 🎯 Key Numbers to Remember

- **10,000** rows in the dataset
- **₹74,447,185** total sales
- **10,000** orders (1 order per row in this dataset)
- **22,682** total units sold
- **₹7,444** average order value
- **14** business questions answered
- **50+** SQL queries across 6 scripts
- **67** Pytest tests (100% passed)
- **17/17** validation checks PASS
- **100%** data retention rate
- **8** product categories
- **12** Indian states
- **36** cities
- **5** dashboard pages
- **10** Excel sheets
- **657 KB** Excel workbook size
- **4** database tables (star schema)

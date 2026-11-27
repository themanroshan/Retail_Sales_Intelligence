# RetailPulse — Business Requirements Document

## Project Overview

**Project name:** RetailPulse — Indian Retail Sales Intelligence  
**Type:** Portfolio data analytics project  
**Scenario:** An Indian multi-category retail business wants to understand sales performance, product and category contribution, regional patterns, and transaction trends.

---

## Business Objectives

1. Understand total revenue and order volume over the analysis period.
2. Identify which product categories and sub-categories contribute most to sales.
3. Determine which individual products drive the highest revenue and profit.
4. Understand geographic distribution of sales across Indian states and cities.
5. Identify monthly and seasonal sales patterns.
6. Assess the impact of discounting on sales volume and profit margins.
7. Provide an interactive dashboard for self-service exploration.

---

## Stakeholders (Assumed)

| Role                    | Interest                                                  |
|-------------------------|-----------------------------------------------------------|
| Category Manager        | Category and sub-category performance, top/bottom products|
| Regional Sales Manager  | State and city performance, geographic concentration       |
| Finance Team            | Revenue totals, profit margins, discount impact           |
| Operations Team         | Quantity patterns, peak sales periods                     |
| Executive Leadership    | Headline KPIs, monthly trends, overall business health    |

---

## Business Questions to Answer

| BQ# | Question                                              | Priority |
|-----|-------------------------------------------------------|----------|
| 1   | What is total recorded sales?                         | High     |
| 2   | How many transactions/orders exist?                   | High     |
| 3   | How many units were sold?                             | High     |
| 4   | Which categories contribute most to sales?            | High     |
| 5   | Which products perform best?                          | High     |
| 6   | Which regions/cities contribute most?                 | High     |
| 7   | What is the monthly sales trend?                      | High     |
| 8   | What are the strongest and weakest sales periods?     | Medium   |
| 9   | What is the average order value?                      | High     |
| 10  | What is the average quantity per transaction?         | Medium   |
| 11  | Which products show growing vs. declining sales?      | Medium   |
| 12  | How concentrated is sales across categories?          | Medium   |
| 13  | What is the discount impact on sales and profit?      | Medium   |
| 14  | What is the profit contribution by category?          | High     |

---

## Deliverables

| Deliverable               | Format              | Status    |
|---------------------------|---------------------|-----------|
| Synthetic dataset          | CSV (10,000 rows)   | COMPLETE  |
| ETL pipeline               | Python scripts      | COMPLETE  |
| Data quality report        | Markdown + dashboard| COMPLETE  |
| MySQL star schema          | SQL scripts         | COMPLETE  |
| SQL analysis queries       | SQL scripts (6)     | COMPLETE  |
| KPI definitions            | Markdown            | COMPLETE  |
| Streamlit dashboard (5 pg) | Python app          | COMPLETE  |
| Excel analysis workbook    | .xlsx (10 sheets)   | COMPLETE  |
| Business analysis report   | Markdown            | COMPLETE  |
| Test suite (Pytest)        | Python tests (74)   | COMPLETE  |
| Setup guide                | Markdown            | COMPLETE  |
| Interview preparation      | Markdown            | COMPLETE  |

---

## Data Requirements

- Minimum 5,000 transaction rows (synthetic: 10,000)
- Date range spanning at least 2 years (synthetic: Jan 2022 – Dec 2024)
- At least 5 product categories
- At least 5 Indian states
- Quantity, price, discount, and sales amount fields
- Profit field (synthetic margin applied)

---

## Constraints and Assumptions

1. Data is **SYNTHETIC** — clearly disclosed throughout.
2. No real customer PII is used or referenced.
3. Geography is randomly assigned and does not reflect real retail patterns.
4. Profit figures are simulated and cannot be used for financial inference.
5. The project uses Python 3.14, MySQL 8.0+, and Streamlit for the dashboard.
6. No ML models or forecasting are included in this version (out of scope for MVP).

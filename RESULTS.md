# RetailPulse — Project Results & Findings

> Dataset: Synthetic Indian retail transactions | 10,000 rows | Jan 2022 – Dec 2024  
> All figures are simulated for portfolio demonstration purposes.

---

## Headline KPIs

| Metric | Value |
|--------|-------|
| Total Sales | ₹7.44 Crore |
| Total Orders | 10,000 |
| Total Units Sold | 22,682 |
| Average Order Value | ₹7,444 |
| Total Profit | ₹2.29 Crore |
| Overall Profit Margin | 30.8% |
| Average Discount | 11.4% |

---

## Category Performance

| Category | Sales (INR) | Share % | Profit Margin % |
|----------|-------------|---------|-----------------|
| Electronics | ₹1.49 Cr | 20.0% | 11% |
| Clothing | ₹1.34 Cr | 18.0% | 32% |
| Home & Kitchen | ₹1.04 Cr | 14.0% | 24% |
| Beauty & Personal Care | ₹0.89 Cr | 12.0% | 42% |
| Sports & Fitness | ₹0.74 Cr | 10.0% | 25% |
| Grocery & Food | ₹0.74 Cr | 10.0% | 14% |
| Books | ₹0.61 Cr | 8.2% | 17% |
| Toys & Games | ₹0.60 Cr | 8.0% | 30% |

**Key finding:** Electronics drives the most revenue (20%) but has the lowest margin (11%). Beauty & Personal Care has the highest margin (42%) despite lower sales volume — the most profitable category per rupee sold.

---

## Regional Performance — Top 5 States

| State | Sales (INR) | Share % |
|-------|-------------|---------|
| Maharashtra | ₹0.86 Cr | 11.5% |
| Karnataka | ₹0.79 Cr | 10.6% |
| Tamil Nadu | ₹0.71 Cr | 9.5% |
| Delhi | ₹0.68 Cr | 9.1% |
| Gujarat | ₹0.65 Cr | 8.7% |

Top 5 states account for ~49% of total sales. No single state dominates — revenue is reasonably spread.

---

## Monthly Sales Trend

- **Peak months:** October, November, December (festive season)
- **Weakest months:** February, April
- Q4 (Oct–Dec) consistently outperforms all other quarters
- Month-over-month growth fluctuates between -15% and +20%

---

## Discount Impact on Profit Margins

| Discount Level | Avg Profit Margin |
|---------------|-------------------|
| 0% (no discount) | 29% |
| 1–10% | 27% |
| 11–20% | 25% |
| 21–30% | 23% |
| 31–40% | 22% |

Every 10% increase in discount reduces margin by approximately 1.5–2 percentage points.

---

## Payment Methods

UPI, Credit Card, Debit Card, Net Banking, Cash on Delivery, and EMI are all used. Distribution is approximately even across payment methods in this synthetic dataset.

---

## Data Quality Summary

| Check | Result |
|-------|--------|
| Total rows processed | 10,000 |
| Rows passing all validation | 10,000 (100%) |
| Duplicate records | 0 |
| Null values in key columns | 0 |
| Sales amount consistency check | 0 mismatches |
| Validation checks run | 17 / 17 PASS |

---

## SQL Analysis — Business Questions Answered

All 14 business questions were answered using SQL queries in `sql/05_business_analysis.sql`:

1. Total sales revenue
2. Total orders and units sold
3. Category contribution to sales
4. Top performing products
5. Regional performance by state
6. Monthly sales trend with MoM growth
7. Strongest and weakest sales months
8. Average order value
9. Average quantity per transaction
10. Year-over-year product growth vs decline
11. Sales concentration (HHI index)
12. Discount impact on margins
13. Profit contribution by category
14. Payment method distribution

Advanced SQL techniques used: CTEs, window functions (LAG, RANK, ROW_NUMBER, SUM OVER), subqueries, CASE statements, date functions.

---

## Key Business Recommendations

1. **Grow Beauty & Personal Care** — highest margin category, strong candidate for increased marketing investment
2. **Protect Electronics margins** — high revenue but thin margins, avoid deep discounting
3. **Festive season planning** — stock up and run campaigns before October
4. **Discount discipline** — high discounts (30%+) show measurable margin erosion with limited evidence of volume compensation
5. **Regional expansion** — Tier 2 cities within top states represent untapped potential

---

*All findings are from a synthetic dataset. They demonstrate analytical methodology and do not represent any real business or market.*

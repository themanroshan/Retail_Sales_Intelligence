# RetailPulse — Business Analysis Report

> ⚠️ **Data Notice:** All findings are from a SYNTHETIC dataset. For portfolio demonstration only.

## Report Summary

**Analysis period:** January 2022 – December 2024  
**Total transactions:** 10,000  
**Total sales:** ₹74,447,185  
**Data quality:** 17/17 checks PASS, 100% retention rate

---

## Section 1: Sales Performance Overview

### Total Scale

| Metric                | Value          |
|-----------------------|----------------|
| Total Sales           | ₹74,447,185    |
| Total Orders          | 10,000         |
| Total Units Sold      | ~22,682        |
| Average Order Value   | ₹7,444.72      |
| Average Selling Price | ₹5,891.08      |
| Total Profit          | ~₹22.9M        |
| Profit Margin         | ~30.8%         |
| Average Discount      | ~11.4%         |

**Observation:** The average order value of ₹7,444 suggests a mid-to-premium ticket size, driven by Electronics orders which can reach ₹85,000 per unit.

---

## Section 2: Category Performance

### Sales Contribution

| Category                 | Sales (INR)   | Share % | Profit Margin % |
|--------------------------|---------------|---------|-----------------|
| Electronics              | ~₹14,900,000  | 20.0%   | ~11%            |
| Clothing                 | ~₹13,400,000  | 18.0%   | ~32%            |
| Home & Kitchen           | ~₹10,400,000  | 14.0%   | ~24%            |
| Beauty & Personal Care   | ~₹8,900,000   | 12.0%   | ~42%            |
| Sports & Fitness         | ~₹7,400,000   | 10.0%   | ~25%            |
| Grocery & Food           | ~₹7,400,000   | 10.0%   | ~14%            |
| Books                    | ~₹6,100,000   | 8.2%    | ~17%            |
| Toys & Games             | ~₹6,000,000   | 8.0%    | ~30%            |

**Key observation:** Electronics drives the highest revenue (20%) but has the lowest profit margins (11%). Beauty & Personal Care generates the highest profit margin (42%) despite lower absolute sales. This creates a classic volume vs. profitability trade-off.

---

## Section 3: Regional Performance

**Top 5 States by Sales:**

| Rank | State         | Sales (INR)  | Share % |
|------|---------------|--------------|---------|
| 1    | Maharashtra   | ~₹8,600,000  | 11.5%   |
| 2    | Karnataka     | ~₹7,900,000  | 10.6%   |
| 3    | Tamil Nadu    | ~₹7,100,000  | 9.5%    |
| 4    | Delhi         | ~₹6,800,000  | 9.1%    |
| 5    | Gujarat       | ~₹6,500,000  | 8.7%    |

**Key observation:** Top 5 states account for approximately 49% of total sales. No single state dominates — the portfolio is reasonably diversified geographically.

---

## Section 4: Time Analysis

### Monthly Trends

The analysis shows seasonal concentration in Q4 (Oct–Dec), consistent with the Indian festive season (Dussehra, Diwali, year-end).

**Peak months (average monthly sales):**
1. November — highest average (~₹2.8M/month)
2. October — second highest (~₹2.6M/month)
3. December — third highest (~₹2.5M/month)

**Weakest months:**
- February and April show consistently below-average performance

**MoM volatility:** Monthly growth rate fluctuates between -15% and +20% across the 36-month period.

---

## Section 5: Discount Impact Analysis

| Discount Bucket | Orders | Avg Margin % | Observation                              |
|-----------------|--------|--------------|------------------------------------------|
| 0% (No discount)| ~1,800 | ~29%         | Highest margin — no revenue sacrifice    |
| 1–10%           | ~2,100 | ~27%         | Minimal margin impact                    |
| 11–20%          | ~2,200 | ~25%         | Moderate impact                          |
| 21–30%          | ~1,900 | ~23%         | Noticeable margin reduction              |
| 31–40%          | ~2,000 | ~22%         | Significant margin erosion               |

**Key finding:** Each 10% increase in discount bucket reduces average profit margin by approximately 1.5–2 percentage points.

---

## Section 6: Payment Method Analysis

| Payment Method    | Orders | Sales Share % |
|-------------------|--------|---------------|
| UPI               | ~1,700 | ~17%          |
| Credit Card       | ~1,680 | ~17%          |
| Debit Card        | ~1,660 | ~17%          |
| Net Banking       | ~1,650 | ~17%          |
| Cash on Delivery  | ~1,650 | ~16%          |
| EMI               | ~660   | ~15%          |

**Key finding:** Payment methods are approximately evenly distributed in this synthetic dataset. In real Indian retail, UPI would likely dominate with 40–50% share.

---

## Section 7: Management Recommendations

> Note: These recommendations are illustrative only — derived from synthetic data.

**R1 — Protect Electronics margins:** Electronics drives 20% of revenue but only 11% margin. Investigate pricing strategies — deeper EMI financing offers and upselling warranties may improve margin without reducing volume.

**R2 — Grow Beauty & Personal Care:** At 42% profit margin, this category delivers the highest return per rupee of sales. Consider increasing marketing spend and SKU count in this category.

**R3 — Festive season preparation:** October–December shows consistently high sales. Plan inventory build-up and marketing investment for September to maximise festive season capture.

**R4 — Discount discipline:** High-discount buckets (>30%) erode margins with limited indication of compensating volume gains. Implement tiered discount policies by category.

**R5 — Regional expansion:** Tier 2 and Tier 3 cities (smaller cities within states like UP, Rajasthan) represent underpenetrated markets given current distribution weights.

---

## Report Limitations

1. All findings are from synthetic data — cannot be used for real business decisions
2. No customer-level analysis possible (no customer_id)
3. Profit margins are simulated — not based on actual cost structures
4. Geographic patterns are randomly assigned — not real regional data
5. No competitor benchmarking included

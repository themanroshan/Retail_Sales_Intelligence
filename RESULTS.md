# RetailPulse — Results

This is what I found after analysing the dataset.

**Reminder:** The data is **synthetic**. I generated it myself in Python. These numbers are not from a real company — they are from my own fake data. I am showing them to explain what my analysis can do.

---

## Overall Numbers

| Metric | Value |
|--------|-------|
| Total Sales | ₹7.44 Crore |
| Total Orders | 10,000 |
| Units Sold | 16,517 |
| Average Order Value | ₹7,444 |
| Total Profit | ₹1.21 Crore |
| Profit Margin | 16.2% |
| Average Discount | 14.1% |

So the average customer spends around ₹7,400 per order, and the business keeps about ₹16 out of every ₹100 in sales as profit.

---

## Which Categories Do Best?

| Category | Share of Sales | Profit Margin |
|----------|---------------|---------------|
| Electronics | 64.9% | 10.2% |
| Home & Kitchen | 15.5% | 25.1% |
| Clothing | 6.6% | 32.8% |
| Sports & Fitness | 6.4% | 24.7% |
| Beauty & Personal Care | 2.7% | 38.4% |
| Toys & Games | 2.2% | 30.2% |
| Grocery & Food | 1.0% | 13.9% |
| Books | 0.7% | 17.6% |

**What this means:**
- **Electronics dominates sales** — almost 65% of all revenue comes from this one category. But the profit margin is only 10%.
- **Beauty & Personal Care has the highest margin at 38%** — even though it is only 2.7% of sales, every rupee sold here returns much more profit.
- **Clothing is a good balance** — 6.6% of sales with a healthy 32.8% margin.
- If this were a real business, growing the high-margin categories would be more profitable than just chasing Electronics volume.

---

## Which States Drive the Most Sales?

| State | Share of Sales |
|-------|---------------|
| Rajasthan | 9.8% |
| West Bengal | 9.3% |
| Tamil Nadu | 9.0% |
| Maharashtra | 8.8% |
| Telangana | 8.6% |

The top 5 states make up about 45% of total sales. No single state is too dominant — revenue is spread reasonably across the country.

---

## When Do People Buy?

- **Peak months:** November 2022, December 2022, October 2023 — festive season (Diwali, year-end sales)
- **Weakest months:** January 2024, April 2023, February 2024

If this were a real store, I would plan bigger inventory and marketing spend before October, and run clearance sales in the slow months.

---

## Does Discounting Help or Hurt?

I grouped orders by discount level and checked the profit margin.

| Discount Level | Profit Margin |
|---------------|---------------|
| 0% | ~18% |
| 1–10% | ~17% |
| 11–20% | ~16% |
| 21–30% | ~15% |
| 31–40% | ~14% |

Each extra 10% of discount reduces the profit margin by roughly 1 to 1.5 percentage points. Discounts bring in more orders, but they eat into profit. A business would need to decide if the extra volume is worth it.

---

## What I Learned From This Project

- Writing SQL queries using JOINs, CTEs, and window functions is enough to answer most real business questions.
- Cleaning data took longer than I expected — I had 11 cleaning rules and 17 validation checks before I could trust the numbers.
- Building a dashboard is only useful if the data behind it is clean. I kept going back to fix my pipeline whenever a chart looked wrong.
- Writing findings in plain English is a separate skill from writing code. Both matter.

---

## What This Project Does Not Do

- The data is fake, so no real business decision should be based on these numbers.
- I do not have real cost data, so profit figures are simulated in the generator.
- I did not build any forecasting or ML models — that is something I want to do next.

---

Made by **Roshan Manjal**

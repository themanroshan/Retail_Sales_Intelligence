# RetailPulse — Results

This is what I found after analysing the dataset.

**Reminder:** The data is **synthetic**. I generated it myself in Python. These numbers are not from a real company — they are from my own fake data. I am showing them to explain what my analysis can do.

---

## Overall numbers

- **Total sales:** ₹7.44 Crore
- **Total orders:** 10,000
- **Units sold:** 22,682
- **Average order value:** ₹7,444
- **Overall profit margin:** 30.8%

So the average customer in this data spends around ₹7,400 per order, and the business keeps about ₹30 out of every ₹100 in sales as profit.

---

## Which categories do best?

I compared the 8 product categories on sales and profit margin.

| Category | Share of sales | Profit margin |
|---|---|---|
| Electronics | 20% | 11% |
| Clothing | 18% | 32% |
| Home & Kitchen | 14% | 24% |
| Beauty & Personal Care | 12% | 42% |
| Sports & Fitness | 10% | 25% |
| Grocery & Food | 10% | 14% |
| Books | 8.2% | 17% |
| Toys & Games | 8% | 30% |

**What this means:**
- **Electronics sell the most but earn the least per rupee.** They bring in 20% of all sales but the profit margin is only 11%.
- **Beauty & Personal Care is the opposite.** It is only 12% of sales but has the highest profit margin at 42%.
- **Clothing is a good middle ground** — it sells a lot (18%) and still keeps a healthy 32% margin.
- If this were a real business, I would say pushing Beauty & Personal Care and Clothing would grow profit faster than pushing Electronics.

---

## Which states drive the most sales?

- **Maharashtra** is the top state at 11.5% of total sales.
- The **top 5 states** (Maharashtra, Karnataka, Tamil Nadu, Delhi, Gujarat) make up **49% of all sales**.

This is roughly in line with where India's bigger cities and consumer spending sit.

---

## When do people buy?

- **October, November, and December** are the peak months. This makes sense — it is the festive season in India (Dussehra, Diwali, Christmas, year-end sales).
- **February and April** are the weakest months.

If this were a real store, I would plan bigger inventory and marketing spend for October to December, and run clearance sales in February and April.

---

## Does discounting help or hurt?

I bucketed orders by discount level and compared profit margin.

- Orders with **no discount** have a **29% profit margin**.
- Orders with a **30-40% discount** have only **22% profit margin**.

So each extra 10% of discount costs roughly 1.5 to 2 percentage points of margin. Discounts bring in more volume, but they eat into profit. A business would need to decide whether the extra sales are worth the lower margin.

---

## What I learned from this project

- Even basic SQL (joins, group by, window functions) can answer most business questions.
- Cleaning and validating data takes longer than I expected. I had 11 cleaning rules and 17 validation checks before I could trust the dataset.
- A dashboard is only useful if the data behind it is clean. I kept going back to fix my pipeline whenever a chart looked wrong.
- Writing up findings in plain English is a separate skill from writing code.

---

## What this project does NOT do

- The data is fake, so no real company decision should be based on these numbers.
- I do not have real costs, so profit numbers are also made up in the generator.
- I did not build any forecasting or ML models — that is on my list for the next project.

---

Made by **Roshan Manjal**
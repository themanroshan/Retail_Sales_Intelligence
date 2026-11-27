# RetailPulse — Limitations and Trade-offs

## Critical Limitations

### 1. Synthetic Data
**What it means:** All data was computationally generated. No real transactions, real products, or real businesses are represented.

**Impact:** Findings cannot be used to infer anything about actual Indian retail performance, specific companies, or market trends.

**What I do:** Prominently label as SYNTHETIC in every document, the dashboard, the Excel workbook, and the README. Present insights as "methodology demonstrations" rather than "business findings."

**What I don't do:** Present simulated data as real, invent impressive-sounding business outcomes, or omit the synthetic label.

---

### 2. No Real Customer Identifiers
**What it means:** The dataset has no customer_id. Each order_id is a transaction, not a customer.

**Impact:** Cannot calculate:
- Customer retention rate
- Repeat purchase rate
- Customer lifetime value (CLV/LTV)
- Cohort analysis
- RFM segmentation (Recency, Frequency, Monetary)

**What I do:** Use "Total Orders" as the transaction count KPI. Explicitly document that "Total Orders ≠ Total Customers."

---

### 3. Simulated Profit Margins
**What it means:** Profit is derived by applying synthetic margin rates (8–50%) per category, not actual cost-of-goods data.

**Impact:** Profit and profit margin figures are not real financial data and should not be used for business decisions.

**What I do:** Document this in the data dictionary and KPI definitions. Add "SYNTHETIC" note next to profit KPIs in the dashboard.

---

### 4. Random Geographic Assignment
**What it means:** State and city are randomly assigned to each transaction using probability weights. They do not reflect real regional retail patterns, population distribution, or economic activity.

**Impact:** Regional insights (e.g., "Maharashtra has 11.5% of sales") are purely artefacts of random assignment with population-ish weights. They do not reflect actual regional retail performance.

---

### 5. No Returns, Cancellations, or Refunds
**What it means:** The dataset has no concept of post-sale events.

**Impact:** Revenue figures represent gross transaction value with no adjustments for returns. Net revenue may be significantly lower in reality.

---

### 6. Date Range Limitation
**What it means:** Data runs from Jan 2022 to Dec 2024 (3 years, synthetic).

**Impact:** Year-over-year comparisons are possible but limited to this window. No pre-pandemic baseline.

---

### 7. Single-Store / Single-Business Assumption
**What it means:** No store_id or business_id dimension. All transactions are treated as belonging to one business.

**Impact:** Cannot perform store-level comparisons or multi-location analysis.

---

## Project-Scope Trade-offs

| Decision                            | Alternative Considered              | Reason for Choice                           |
|-------------------------------------|-------------------------------------|---------------------------------------------|
| Synthetic data                      | Real Kaggle dataset                 | Licence ambiguity; reproducibility          |
| mysql-connector-python              | SQLAlchemy                          | Beginner-friendly; fewer abstractions       |
| Streamlit dashboard                 | Power BI / Tableau                  | Code-first; version-controllable; free hosting |
| Star schema (4 tables)              | Fully denormalized flat table       | Demonstrates warehouse design knowledge    |
| 10,000 rows                         | 1,000,000+ rows                     | Fast pipeline execution; MVP scope          |
| No ML/forecasting                   | SARIMA, Prophet                     | Out of scope for MVP; requires real data    |
| No customer segmentation            | RFM segmentation                    | No customer_id in dataset                   |
| OpenPyXL Excel generation           | Manual Excel creation               | Reproducible; versioned; automatable        |

---

## Comparison to Real-World Data Analysis

| Aspect                         | This Project (Synthetic)            | Real-World DA Project               |
|--------------------------------|-------------------------------------|--------------------------------------|
| Data trust                     | Complete (we generated it)          | Requires validation, source checks   |
| Data quality                   | 100% clean by design                | Typically 5–30% cleanup needed       |
| Insight validity               | Methodology demonstration only      | Actionable business insights         |
| Deployment environment         | Local / Streamlit Cloud             | Enterprise cloud, secure DB          |
| Data volume                    | 10,000 rows                         | Millions–billions of rows            |
| Refresh frequency              | Manual re-run                       | Scheduled ETL (Airflow, DBT, etc.)   |
| Stakeholder sensitivity        | Public portfolio                    | Confidential, access-controlled      |

---

## What to Tell an Interviewer

If asked about limitations, be direct and confident:

> "The main limitation is that the data is synthetic. This was a deliberate choice — real Indian retail datasets on Kaggle have unclear licences. The synthetic dataset demonstrates exactly the same ETL, SQL, and dashboard skills as a real dataset would. When I find a licensed dataset, I can plug it in and all 50+ SQL queries and the dashboard run identically without changing any code. I think being transparent about this is more credible than using someone else's pre-cleaned data without disclosure."

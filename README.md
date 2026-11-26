# Retail Sales Intelligence & Demand Forecasting System

A quick-commerce analytics project built on the Instacart Market Basket dataset.
Transforms raw order data into a MySQL warehouse, answers business questions
with SQL, forecasts daily order demand, and surfaces insights in a Streamlit
dashboard.


## What it does

- **ETL pipeline** — reads Instacart CSVs, cleans them, loads them into MySQL.
- **Star schema** in MySQL (facts + dimensions) with 6 tables.
- **SQL analytics** — 10 business questions answered using JOINs, CTEs, and window functions.
- **Forecasting** — compares Naive, Seasonal Naive, and SARIMA models on daily order volume.
- **Dashboard** — interactive Streamlit app with 4 pages (Overview / Products / Time / Forecast).

## Tech stack

Python 3.11 · Pandas · MySQL 8 · SQLAlchemy · Statsmodels (SARIMA) · Streamlit · Plotly · Pytest

## Project structure

```
retail-sales-intelligence/
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   ├── README.md          (dataset download instructions)
│   └── raw/               (Instacart CSVs go here)
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_forecasting.ipynb
├── sql/
│   ├── schema.sql         (create tables)
│   └── analytics.sql      (10 business queries)
├── src/
│   ├── config.py
│   ├── database.py
│   ├── pipeline.py        (ETL)
│   ├── analytics.py       (KPI functions)
│   └── forecasting.py     (models + metrics)
├── app.py                 (Streamlit dashboard)
└── tests/
    ├── test_cleaning.py
    ├── test_kpis.py
    └── test_forecasting.py
```

## Setup

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure MySQL credentials
copy .env.example .env         # Windows
# cp .env.example .env          # Mac/Linux
# then edit .env with your MySQL password

# 4. Download Instacart dataset
# See data/README.md for instructions. Place CSVs in data/raw/

# 5. Run the pipeline (creates DB, loads data)
python src/pipeline.py

# 6. Launch the dashboard
streamlit run app.py
```

## Running tests

```bash
pytest -v
```

## Dataset

**Instacart Market Basket Analysis** (Kaggle)
- Link: https://www.kaggle.com/competitions/instacart-market-basket-analysis/data
- 3.4M orders, 200K users, 50K products
- 6 CSV files

## Business questions answered

1. Which departments drive the most orders?
2. Which aisles have the highest reorder rate?
3. What are the top 15 products?
4. Which products get reordered most?
5. When does demand peak (day of week × hour)?
6. How does order volume grow month over month?
7. What is the 7-day rolling average of daily orders?
8. How are customers segmented by order frequency?
9. What is the average basket size?
10. What will order volume look like for the next 14 days?

## Limitations

- Instacart dataset has no real timestamps — we construct synthetic dates from `days_since_prior_order`.
- No price data, so revenue KPIs are not included.
- Dataset reflects US grocery behavior; India quick-commerce patterns may differ.

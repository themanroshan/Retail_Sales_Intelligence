# RetailPulse — System Architecture

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RetailPulse Architecture                          │
└─────────────────────────────────────────────────────────────────────────────┘

   ┌──────────────────┐
   │  src/generate_   │  ← seed=42, 10,000 rows, 2022–2024
   │  data.py         │
   └────────┬─────────┘
            │ data/raw/retailpulse_transactions.csv
            ▼
   ┌──────────────────┐
   │  src/data_loader │  ← Load CSV, coerce types, check columns
   │  .py             │
   └────────┬─────────┘
            │ raw DataFrame (10,000 rows × 14 cols)
            ▼
   ┌──────────────────┐    ┌────────────────────────────────────┐
   │  src/data_       │    │ Audit Summary                      │
   │  cleaning.py     │───►│ original_rows: 10,000              │
   │  (11 rules)      │    │ clean_rows: 10,000                 │
   └────────┬─────────┘    │ quarantine_rows: 0                 │
            │              │ retention_rate: 100%               │
            │              └────────────────────────────────────┘
            ▼
   ┌──────────────────┐    ┌────────────────────────────────────┐
   │  src/data_       │    │ Validation Report                  │
   │  validation.py   │───►│ 17/17 checks PASS                  │
   │  (17 checks)     │    │ Overall: PASS                      │
   └────────┬─────────┘    └────────────────────────────────────┘
            │
            ▼
   ┌──────────────────┐
   │  src/            │  ← Add year, month, quarter, year_month,
   │  transformations │    day_name, is_weekend derived cols
   │  .py             │
   └────────┬─────────┘
            │
      ┌─────┴──────┐
      │            │
      ▼            ▼
  ┌───────────┐  ┌──────────────────────────────────────────────┐
  │  CSV Path │  │  MySQL Path                                   │
  │           │  │                                               │
  │ data/     │  │  build_dim_product()                         │
  │ processed │  │  build_dim_location()                        │
  │ /retail   │  │  build_dim_date()                            │
  │ pulse_    │  │  build_fact_sales()                          │
  │ clean.csv │  │        │                                     │
  └────┬──────┘  │        ▼                                     │
       │         │  MySQL 8.0 (retailpulse database)            │
       │         │  ┌───────────┐  ┌──────────────┐            │
       │         │  │dim_product│  │ dim_location  │            │
       │         │  └───────────┘  └──────────────┘            │
       │         │  ┌───────────┐  ┌──────────────┐            │
       │         │  │ dim_date  │  │  fact_sales   │            │
       │         │  └───────────┘  └──────────────┘            │
       │         └──────────────────────────────────────────────┘
       │                   │
       └──────────┬─────────┘
                  │  (data reads from MySQL or CSV fallback)
                  ▼
   ┌──────────────────────────────────┐
   │      src/analytics.py           │
   │  20 KPI and aggregation funcs   │
   │  kpi_summary()                  │
   │  sales_by_category()            │
   │  monthly_sales_trend()          │
   │  top_products_by_sales()        │
   │  ... (17 more functions)        │
   └────────┬─────────────────────────┘
            │
      ┌─────┴──────────────────┐
      │                        │
      ▼                        ▼
 ┌────────────────┐    ┌───────────────────┐
 │   app.py       │    │  src/excel_       │
 │   (Streamlit)  │    │  export.py        │
 │   5 Pages      │    │  10 sheets        │
 └────────────────┘    └───────────────────┘
      │                        │
      ▼                        ▼
  Browser                 excel/
  :8501                   RetailPulse_
                          Analysis.xlsx
```

## Component Descriptions

| Component                 | File                      | Responsibility                           |
|---------------------------|---------------------------|------------------------------------------|
| Data Generator            | `src/generate_data.py`    | Creates deterministic synthetic dataset  |
| Data Loader               | `src/data_loader.py`      | Reads raw CSV, coerces types             |
| Data Cleaner              | `src/data_cleaning.py`    | 11 rules, quarantine, audit trail        |
| Data Validator            | `src/data_validation.py`  | 17 post-clean checks                     |
| Transformations           | `src/transformations.py`  | Date parts, dimension builders           |
| Database Layer            | `src/database.py`         | MySQL connection, INSERT IGNORE loading  |
| ETL Orchestrator          | `src/pipeline.py`         | Coordinates all pipeline steps           |
| Analytics                 | `src/analytics.py`        | 20 KPI and aggregation functions         |
| Excel Exporter            | `src/excel_export.py`     | 10-sheet workbook via OpenPyXL           |
| Config                    | `src/config.py`           | Paths, MySQL settings, dotenv loading    |
| Dashboard Components      | `dashboard/components.py` | Reusable Streamlit UI elements           |
| Dashboard Charts          | `dashboard/charts.py`     | 12 Plotly chart functions                |
| Main App                  | `app.py`                  | 5-page Streamlit dashboard               |

## Technology Decisions

| Decision              | Technology              | Why                                                    |
|-----------------------|-------------------------|--------------------------------------------------------|
| Database              | MySQL 8.0               | Specified requirement; enterprise standard              |
| DB connector          | mysql-connector-python  | Beginner-friendly; no ORM abstraction overhead         |
| Dashboard             | Streamlit + Plotly      | Code-first; version-controllable; free hosting         |
| Testing               | Pytest                  | Industry standard for Python projects                  |
| Excel generation      | OpenPyXL                | Pure Python; no Excel installation required            |
| Env management        | python-dotenv           | Standard secret management; prevents credential commits|
| Data generation       | NumPy default_rng       | Deterministic; reproducible; modern NumPy API          |

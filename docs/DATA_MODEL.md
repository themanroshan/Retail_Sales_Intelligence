# RetailPulse — Data Model

## Star Schema Design

The database uses a **star schema** with one fact table and three dimension tables.

```
                    ┌──────────────┐
                    │  dim_date    │
                    │──────────────│
                    │ date_id (PK) │
                    │ order_date   │
                    │ year         │
                    │ quarter      │
                    │ month        │
                    │ month_name   │
                    │ week         │
                    │ day_of_week  │
                    │ day_name     │
                    │ is_weekend   │
                    │ year_month   │
                    └──────┬───────┘
                           │ order_date
                           │
┌───────────────┐    ┌─────▼──────────────────────────────────────┐    ┌──────────────┐
│  dim_product  │    │                 fact_sales                   │    │ dim_location │
│───────────────│    │─────────────────────────────────────────────│    │──────────────│
│ product_id(PK)◄────┤ order_id       (PK, part)                   ├────► location_id  │
│ product_name  │    │ product_id     (FK → dim_product)           │    │ (PK)         │
│ category      │    │ order_date     (FK → dim_date)              │    │ state        │
│ sub_category  │    │ location_id    (FK → dim_location)          │    │ city         │
└───────────────┘    │ quantity                                     │    └──────────────┘
                     │ unit_price                                   │
                     │ discount                                     │
                     │ sales_amount                                 │
                     │ profit                                       │
                     │ payment_method                               │
                     │ year                                         │
                     │ month                                        │
                     │ quarter                                      │
                     │ year_month                                   │
                     └─────────────────────────────────────────────┘
```

## Table Descriptions

### fact_sales (Fact Table)
- **Grain:** One row per order line (one order_id + product_id pair)
- **Purpose:** Stores all measurable transaction events
- **Primary key:** Composite (order_id, product_id)
- **Row count:** 10,000 (synthetic dataset)

### dim_product (Product Dimension)
- **Grain:** One row per unique product
- **Purpose:** Stores product attributes for category/sub-category analysis
- **Primary key:** product_id
- **Row count:** ~2,345 unique products

### dim_location (Geographic Dimension)
- **Grain:** One row per unique state + city combination
- **Purpose:** Enables regional roll-up analysis
- **Primary key:** location_id (surrogate)
- **Row count:** 36 (12 states × 3 cities average)

### dim_date (Date Dimension)
- **Grain:** One row per calendar date in the dataset
- **Purpose:** Enables time-based analysis without recalculating date parts each time
- **Primary key:** date_id (YYYYMMDD integer)
- **Row count:** 1,096 (Jan 2022 – Dec 2024, 3 years)

## Why Star Schema?

| Factor              | Star Schema                              | Flat Table                               |
|---------------------|------------------------------------------|------------------------------------------|
| Query simplicity    | Simple JOINs from fact to dims           | No JOINs needed                          |
| Storage efficiency  | Product name stored once per product     | Repeated on every row                    |
| Update maintenance  | Category rename: update 1 row in dim     | Update thousands of rows                 |
| Analytical performance | Indexes on FK columns help GROUP BY   | Full table scans on text columns         |
| Demonstrates skills | Shows BI/warehouse design knowledge      | Does not differentiate candidate         |

## Indexing Strategy

| Table        | Index               | Columns          | Purpose                          |
|--------------|---------------------|------------------|----------------------------------|
| fact_sales   | PRIMARY KEY         | order_id, product_id | Prevents duplicates           |
| fact_sales   | idx_order_date      | order_date       | Date range queries               |
| fact_sales   | idx_year_month      | year_month       | Monthly GROUP BY                 |
| fact_sales   | idx_product_id      | product_id       | JOIN to dim_product              |
| fact_sales   | idx_location_id     | location_id      | JOIN to dim_location             |
| dim_location | uq_state_city       | state, city      | Unique location pairs            |
| dim_location | idx_state           | state            | State-level GROUP BY             |
| dim_date     | idx_order_date      | order_date       | Date lookups                     |
| dim_date     | idx_year_month      | year_month       | Month lookups                    |

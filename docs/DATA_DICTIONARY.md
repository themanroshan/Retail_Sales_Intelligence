# RetailPulse — Data Dictionary

## Fact Table: fact_sales

| Column         | Data Type      | Nullable | Description                                                  | Example Value         |
|----------------|----------------|----------|--------------------------------------------------------------|-----------------------|
| order_id       | VARCHAR(20)    | NO       | Unique transaction identifier. Format: RP-XXXXXX            | RP-000123             |
| order_date     | DATE           | NO       | Date of purchase (YYYY-MM-DD)                               | 2023-10-15            |
| product_id     | VARCHAR(20)    | NO       | Product identifier. Format: P-XXXXX                         | P-23456               |
| location_id    | INT            | NO       | FK to dim_location                                           | 7                     |
| quantity       | INT            | NO       | Units purchased in this line. Always ≥ 1                    | 2                     |
| unit_price     | DECIMAL(12,2)  | NO       | List price per unit in INR before discount                  | 5000.00               |
| discount       | DECIMAL(5,4)   | NO       | Discount as a fraction [0.0000, 1.0000]                     | 0.1500                |
| sales_amount   | DECIMAL(14,2)  | NO       | Post-discount revenue = unit_price × quantity × (1−discount)| 8500.00               |
| profit         | DECIMAL(14,2)  | NO       | Simulated profit (synthetic margin applied to sales_amount) | 1700.00               |
| payment_method | VARCHAR(50)    | NO       | Payment channel used                                         | UPI                   |
| year           | SMALLINT       | NO       | Calendar year of order_date (derived)                       | 2023                  |
| month          | TINYINT        | NO       | Month number 1–12 (derived)                                 | 10                    |
| quarter        | TINYINT        | NO       | Quarter 1–4 (derived)                                       | 4                     |
| year_month     | VARCHAR(10)    | NO       | Period label YYYY-MM (derived, used for grouping)           | 2023-10               |

**Primary key:** (order_id, product_id)

---

## Dimension: dim_product

| Column       | Data Type    | Description                        |
|--------------|--------------|------------------------------------|
| product_id   | VARCHAR(20)  | PK — matches fact_sales.product_id |
| product_name | VARCHAR(500) | Full product display name          |
| category     | VARCHAR(100) | One of 8 top-level categories      |
| sub_category | VARCHAR(100) | One of 5 subcategories per category|

**Categories:**
Electronics, Clothing, Home & Kitchen, Books, Sports & Fitness,
Beauty & Personal Care, Grocery & Food, Toys & Games

---

## Dimension: dim_location

| Column      | Data Type    | Description                      |
|-------------|--------------|----------------------------------|
| location_id | INT (AUTO)   | PK — surrogate key               |
| state       | VARCHAR(100) | Indian state name                |
| city        | VARCHAR(100) | City within that state           |

**States covered (synthetic):**
Maharashtra, Karnataka, Tamil Nadu, Delhi, Gujarat, Telangana,
West Bengal, Rajasthan, Uttar Pradesh, Madhya Pradesh, Kerala, Punjab

---

## Dimension: dim_date

| Column      | Data Type    | Description                      |
|-------------|--------------|----------------------------------|
| date_id     | INT          | PK — YYYYMMDD integer            |
| order_date  | DATE         | Calendar date                    |
| year        | SMALLINT     | Calendar year                    |
| quarter     | TINYINT      | Quarter (1–4)                    |
| month       | TINYINT      | Month number (1–12)              |
| month_name  | VARCHAR(15)  | Full month name (January, etc.)  |
| week        | TINYINT      | ISO week number                  |
| day_of_week | TINYINT      | 0=Monday … 6=Sunday              |
| day_name    | VARCHAR(10)  | Day name (Monday, etc.)          |
| is_weekend  | TINYINT      | 1 if Saturday or Sunday          |
| year_month  | VARCHAR(10)  | YYYY-MM period string            |

---

## Processed CSV: retailpulse_clean.csv

Same schema as fact_sales plus joined columns from dimension tables
(product_name, category, sub_category, state, city).
Used as the dashboard data fallback when MySQL is not configured.

---

## Field Derivations

| Derived Field | Formula                                              |
|---------------|------------------------------------------------------|
| sales_amount  | unit_price × quantity × (1 − discount)              |
| profit        | sales_amount × category_profit_margin_rate (synthetic)|
| year          | YEAR(order_date)                                     |
| month         | MONTH(order_date)                                    |
| quarter       | QUARTER(order_date)                                  |
| year_month    | DATE_FORMAT(order_date, '%Y-%m')                     |

---

## Notes on Synthetic Data

- **profit** is calculated using synthetic margin rates per category.
  It does **not** reflect real cost structures.
- **unit_price** is drawn from log-uniform distributions within
  category-specific ranges — it simulates realistic Indian retail price points
  but is not based on actual market prices.
- Geographic assignments (state, city) are random — they do not reflect
  real regional sales patterns.

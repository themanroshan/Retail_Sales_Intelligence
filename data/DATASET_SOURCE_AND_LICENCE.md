# RetailPulse — Dataset Source and Licence

## ⚠️ IMPORTANT: This project uses a SYNTHETIC dataset

This project was built using a **deterministically generated synthetic dataset**.
It does **not** represent real company performance, real sales figures, or actual
Indian retail market data.

---

## Synthetic Dataset Details

| Field              | Value                                                      |
|--------------------|-------------------------------------------------------------|
| Dataset name       | RetailPulse Synthetic Transactions                         |
| Type               | SYNTHETIC — computer-generated                             |
| Generator          | `src/generate_data.py`                                     |
| Random seed        | 42 (fully reproducible)                                    |
| Rows               | 10,000                                                     |
| Columns            | 14                                                         |
| Date range         | 2022-01-01 to 2024-12-31                                   |
| Currency           | INR (Indian Rupees) — simulated                            |
| Geography          | 12 Indian states, 36 cities — randomly assigned            |
| Licence            | Public Domain (self-generated for portfolio use)           |
| Redistribution     | Permitted — no real data or proprietary information used   |

## Why synthetic data was chosen

During dataset research, the following Indian retail/e-commerce datasets were
identified on Kaggle:

1. **E-Commerce Data (benroshan)** — `kaggle.com/datasets/benroshan/ecommerce-data`
   - Three CSV files: List of Orders, Order Details, Sales Target
   - Approximately 500 rows of order data for India
   - Licence: unspecified / unclear original source
   - **Issue:** Small row count (< 1,000 orders) and unclear licence provenance

2. **Indian E-Commerce Sales Analysis** — various Kaggle uploads
   - Licence: typically unspecified or restricted
   - **Issue:** Licence terms do not clearly permit redistribution in a portfolio

3. **Sample Superstore (global)** — widely used US-based dataset
   - Not India-specific; currency is USD

**Decision:** Given the two-day time constraint and the need for a clearly
documented, reproducible dataset with no licence ambiguity, a deterministic
synthetic dataset was generated. This is disclosed prominently throughout the
project.

## If you want to use a real dataset

The project is designed to accept any CSV that matches the schema below.
Place the CSV at `data/raw/retailpulse_transactions.csv` and run:

```bash
python src/pipeline.py
```

**Required columns:**
```
order_id, order_date, product_id, product_name, category, sub_category,
quantity, unit_price, discount, sales_amount, profit, state, city, payment_method
```

The best real candidate found is the Kaggle dataset by **benroshan**:
- URL: https://www.kaggle.com/datasets/benroshan/ecommerce-data
- Verify licence before use
- After downloading, rename/reshape to match the column schema above
- See `data/README.md` for placement instructions

## Generation assumptions

- 8 product categories matching Indian retail (Electronics, Clothing, Home & Kitchen,
  Books, Sports & Fitness, Beauty & Personal Care, Grocery & Food, Toys & Games)
- 5 sub-categories per category
- Prices drawn from log-uniform distributions within realistic INR ranges per category
- Discount rates rounded to nearest 5% step within category-specific ranges
- Profit margins derived from typical Indian retail margin estimates per category
- Geographic distribution: 12 states, weighted approximately by population
- Seasonal weighting: higher transaction volume in Oct–Dec (festive season)
- Payment methods: UPI, Credit Card, Debit Card, Net Banking, Cash on Delivery, EMI

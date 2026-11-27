"""
RetailPulse — Synthetic Dataset Generator
==========================================
Generates a deterministic synthetic Indian retail transactions dataset.

IMPORTANT:
  This data is SYNTHETIC. It is generated for portfolio demonstration purposes.
  It does NOT represent real company performance, real sales figures, or real
  Indian retail market data. All numbers are simulated.

  Fixed random seed = 42 ensures full reproducibility.

Usage:
    python -m src.generate_data
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import (
    DATA_RAW, RAW_FILENAME, SYNTHETIC_SEED,
    SYNTHETIC_N_ROWS, SYNTHETIC_START_DATE, SYNTHETIC_END_DATE
)

# ── Catalogue ─────────────────────────────────────────────────────────────────

CATEGORIES = {
    "Electronics": {
        "subcategories": ["Mobile Phones", "Laptops", "Tablets", "Accessories", "Audio"],
        "price_range": (500, 85000),
        "discount_range": (0.0, 0.25),
    },
    "Clothing": {
        "subcategories": ["Men's Wear", "Women's Wear", "Kids' Wear", "Footwear", "Accessories"],
        "price_range": (200, 8000),
        "discount_range": (0.05, 0.40),
    },
    "Home & Kitchen": {
        "subcategories": ["Cookware", "Furniture", "Decor", "Appliances", "Bedding"],
        "price_range": (300, 25000),
        "discount_range": (0.0, 0.30),
    },
    "Books": {
        "subcategories": ["Fiction", "Non-Fiction", "Academic", "Children", "Comics"],
        "price_range": (99, 1500),
        "discount_range": (0.0, 0.20),
    },
    "Sports & Fitness": {
        "subcategories": ["Gym Equipment", "Outdoor", "Sportswear", "Footwear", "Nutrition"],
        "price_range": (200, 15000),
        "discount_range": (0.05, 0.25),
    },
    "Beauty & Personal Care": {
        "subcategories": ["Skincare", "Haircare", "Fragrances", "Makeup", "Men's Grooming"],
        "price_range": (100, 5000),
        "discount_range": (0.05, 0.35),
    },
    "Grocery & Food": {
        "subcategories": ["Staples", "Snacks", "Beverages", "Dairy", "Organic"],
        "price_range": (50, 2000),
        "discount_range": (0.0, 0.15),
    },
    "Toys & Games": {
        "subcategories": ["Board Games", "Action Figures", "Puzzles", "Educational", "Outdoor Toys"],
        "price_range": (150, 5000),
        "discount_range": (0.05, 0.30),
    },
}

# Indian states and their representative cities
LOCATIONS = {
    "Maharashtra":    ["Mumbai", "Pune", "Nagpur", "Nashik"],
    "Karnataka":      ["Bengaluru", "Mysuru", "Hubli"],
    "Tamil Nadu":     ["Chennai", "Coimbatore", "Madurai"],
    "Delhi":          ["New Delhi", "Noida", "Gurgaon"],
    "Gujarat":        ["Ahmedabad", "Surat", "Vadodara"],
    "Telangana":      ["Hyderabad", "Warangal", "Karimnagar"],
    "West Bengal":    ["Kolkata", "Durgapur", "Howrah"],
    "Rajasthan":      ["Jaipur", "Jodhpur", "Udaipur"],
    "Uttar Pradesh":  ["Lucknow", "Kanpur", "Agra", "Varanasi"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur"],
    "Kerala":         ["Thiruvananthapuram", "Kochi", "Kozhikode"],
    "Punjab":         ["Chandigarh", "Amritsar", "Ludhiana"],
}

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery", "EMI"]

# Profit margin ranges per category (cost as fraction of sale price after discount)
PROFIT_MARGINS = {
    "Electronics":            (0.05, 0.15),
    "Clothing":               (0.20, 0.45),
    "Home & Kitchen":         (0.15, 0.35),
    "Books":                  (0.10, 0.25),
    "Sports & Fitness":       (0.15, 0.35),
    "Beauty & Personal Care": (0.25, 0.50),
    "Grocery & Food":         (0.08, 0.20),
    "Toys & Games":           (0.20, 0.40),
}


def _make_product_name(category: str, subcategory: str, rng: np.random.Generator) -> str:
    """Generate a plausible product name from category+subcategory."""
    adjectives = ["Premium", "Classic", "Standard", "Deluxe", "Pro", "Lite", "Essential", "Smart"]
    brands = {
        "Electronics":            ["Samsung", "OnePlus", "Boat", "Mi", "Realme", "Noise"],
        "Clothing":               ["FabIndia", "Manyavar", "Biba", "Levi's", "United Colors"],
        "Home & Kitchen":         ["Prestige", "Butterfly", "Havells", "Godrej", "Nilkamal"],
        "Books":                  ["Penguin", "Rupa", "Orient", "Disha", "S Chand"],
        "Sports & Fitness":       ["Nivia", "Cosco", "Yonex", "Decathlon", "Speedo"],
        "Beauty & Personal Care": ["Lakme", "Biotique", "Himalaya", "Forest Essentials", "Mamaearth"],
        "Grocery & Food":         ["Haldiram's", "MTR", "ITC", "Britannia", "Patanjali"],
        "Toys & Games":           ["Funskool", "Hasbro", "Lego", "Itsy Bitsy", "Mattel"],
    }
    brand = rng.choice(brands.get(category, ["GenericBrand"]))
    adj   = rng.choice(adjectives)
    return f"{brand} {adj} {subcategory}"


def generate_transactions(
    n_rows: int = SYNTHETIC_N_ROWS,
    seed: int   = SYNTHETIC_SEED,
    start: str  = SYNTHETIC_START_DATE,
    end: str    = SYNTHETIC_END_DATE,
) -> pd.DataFrame:
    """
    Generate n_rows synthetic retail transactions.
    Returns a DataFrame matching the RetailPulse schema.
    """
    rng = np.random.default_rng(seed)

    # Date range
    date_range = pd.date_range(start=start, end=end, freq="D")
    # Weight more transactions toward weekends and festive months (Oct-Nov-Dec)
    month_weights = {1:0.7, 2:0.65, 3:0.75, 4:0.7, 5:0.75, 6:0.7,
                     7:0.75, 8:0.8, 9:0.85, 10:1.2, 11:1.4, 12:1.3}
    day_weights = np.array([month_weights[d.month] * (1.3 if d.day_of_week >= 5 else 1.0)
                            for d in date_range])
    day_weights /= day_weights.sum()
    order_dates = rng.choice(date_range, size=n_rows, p=day_weights)

    # Category and subcategory
    categories = list(CATEGORIES.keys())
    cat_probs   = np.array([0.20, 0.18, 0.14, 0.08, 0.10, 0.12, 0.10, 0.08])
    cat_probs  /= cat_probs.sum()
    chosen_cats = rng.choice(categories, size=n_rows, p=cat_probs)

    rows = []
    for i in range(n_rows):
        cat_name   = chosen_cats[i]
        cat_info   = CATEGORIES[cat_name]
        subcat     = rng.choice(cat_info["subcategories"])
        product    = _make_product_name(cat_name, subcat, rng)

        # Price — log-uniform across the category range
        lo, hi   = cat_info["price_range"]
        unit_price = round(float(np.exp(rng.uniform(np.log(lo), np.log(hi)))), 2)

        # Quantity — most orders are 1 unit, rare bulk buys
        qty_probs = [0.60, 0.25, 0.08, 0.04, 0.02, 0.01]
        quantity  = rng.choice([1, 2, 3, 4, 5, 6], p=qty_probs)

        # Discount (rounded to nearest 5%)
        d_lo, d_hi = cat_info["discount_range"]
        raw_disc   = rng.uniform(d_lo, d_hi)
        discount   = round(round(raw_disc * 20) / 20, 2)   # 0.00, 0.05, 0.10, …

        # Sales amount = unit_price * qty * (1 - discount)
        sales_amount = round(unit_price * quantity * (1 - discount), 2)

        # Profit
        pm_lo, pm_hi = PROFIT_MARGINS[cat_name]
        margin = rng.uniform(pm_lo, pm_hi)
        profit = round(sales_amount * margin, 2)

        # Location
        state = rng.choice(list(LOCATIONS.keys()))
        city  = rng.choice(LOCATIONS[state])

        # Payment
        payment = rng.choice(PAYMENT_METHODS)

        rows.append({
            "order_id":       f"RP-{(i + 1):06d}",
            "order_date":     pd.Timestamp(order_dates[i]).strftime("%Y-%m-%d"),
            "product_id":     f"P-{(hash(product) % 50000 + 10000):05d}",
            "product_name":   product,
            "category":       cat_name,
            "sub_category":   subcat,
            "quantity":       int(quantity),
            "unit_price":     unit_price,
            "discount":       discount,
            "sales_amount":   sales_amount,
            "profit":         profit,
            "state":          state,
            "city":           city,
            "payment_method": payment,
        })

    df = pd.DataFrame(rows)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.sort_values("order_date").reset_index(drop=True)
    return df


def save_raw(df: pd.DataFrame) -> None:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    out_path = DATA_RAW / RAW_FILENAME
    df.to_csv(out_path, index=False)
    print(f"[generate_data] Saved {len(df):,} rows → {out_path}")


if __name__ == "__main__":
    print("[generate_data] Generating synthetic dataset …")
    print(f"  Rows       : {SYNTHETIC_N_ROWS:,}")
    print(f"  Seed       : {SYNTHETIC_SEED}")
    print(f"  Date range : {SYNTHETIC_START_DATE} → {SYNTHETIC_END_DATE}")
    print()
    df = generate_transactions()
    save_raw(df)
    print("\nSample rows:")
    print(df.head(3).to_string(index=False))
    print(f"\nColumns: {list(df.columns)}")
    print(f"Shape  : {df.shape}")

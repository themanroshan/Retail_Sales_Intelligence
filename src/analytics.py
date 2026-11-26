"""Analytics functions — KPIs and business queries using Pandas."""

import pandas as pd


def total_orders(orders):
    return int(orders["order_id"].nunique())


def total_customers(orders):
    return int(orders["user_id"].nunique())


def total_items_sold(order_products):
    return int(len(order_products))


def average_basket_size(order_products):
    """Average number of items per order."""
    items_per_order = order_products.groupby("order_id").size()
    return float(items_per_order.mean())


def reorder_rate(order_products):
    """Fraction of order lines that are reorders (0 to 1)."""
    return float(order_products["reordered"].mean())


def top_departments(order_products, products, departments, n=10):
    """Top N departments by order volume."""
    merged = order_products.merge(
        products[["product_id", "department_id"]], on="product_id"
    ).merge(departments, on="department_id")

    result = (
        merged.groupby("department")
        .size()
        .reset_index(name="order_lines")
        .sort_values("order_lines", ascending=False)
        .head(n)
    )
    return result.reset_index(drop=True)


def top_aisles(order_products, products, aisles, n=10):
    merged = order_products.merge(
        products[["product_id", "aisle_id"]], on="product_id"
    ).merge(aisles, on="aisle_id")

    result = (
        merged.groupby("aisle")
        .size()
        .reset_index(name="order_lines")
        .sort_values("order_lines", ascending=False)
        .head(n)
    )
    return result.reset_index(drop=True)


def top_products(order_products, products, n=15):
    merged = order_products.merge(
        products[["product_id", "product_name"]], on="product_id"
    )
    result = (
        merged.groupby(["product_id", "product_name"])
        .size()
        .reset_index(name="order_lines")
        .sort_values("order_lines", ascending=False)
        .head(n)
    )
    return result.reset_index(drop=True)


def top_reordered(order_products, products, n=15):
    """Products with the highest count of reorders."""
    reorders = order_products[order_products["reordered"] == 1]
    merged = reorders.merge(products[["product_id", "product_name"]], on="product_id")
    result = (
        merged.groupby("product_name")
        .size()
        .reset_index(name="reorder_count")
        .sort_values("reorder_count", ascending=False)
        .head(n)
    )
    return result.reset_index(drop=True)


def demand_heatmap(orders):
    """Day-of-week × hour-of-day order counts."""
    return (
        orders.groupby(["order_dow", "order_hour_of_day"])
        .size()
        .reset_index(name="order_count")
    )


def daily_orders(orders):
    """Daily order volume (for forecasting input)."""
    return (
        orders.groupby("order_date")
        .size()
        .reset_index(name="order_count")
        .sort_values("order_date")
    )


def kpi_summary(orders, order_products):
    """Bundle of headline KPIs for the dashboard."""
    return {
        "total_orders": total_orders(orders),
        "total_customers": total_customers(orders),
        "total_items_sold": total_items_sold(order_products),
        "avg_basket_size": round(average_basket_size(order_products), 2),
        "reorder_rate": round(reorder_rate(order_products), 4),
    }

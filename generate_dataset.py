"""
generate_dataset.py
--------------------
Generates a realistic SAMPLE sales dataset for the
"Sales Data Analysis and Interactive Data Visualization" project.

This is a synthetically generated dataset created for training/college
project purposes. It does NOT represent any real company or real sales
transactions.

Run this script once to create:
    data/sales_data.csv
    data/sales_data.xlsx

Usage:
    python scripts/generate_dataset.py
"""

import os
import random
import numpy as np
import pandas as pd

# ---------------------------------------------------------------
# Reproducibility: fixing the random seed so the dataset generated
# is the same every time this script is run.
# ---------------------------------------------------------------
random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------
# Reference data: products grouped by category, with a realistic
# base price range used to generate sales figures.
# ---------------------------------------------------------------
PRODUCTS_BY_CATEGORY = {
    "Electronics": {
        "Laptop": (35000, 75000),
        "Smartphone": (12000, 55000),
        "Tablet": (10000, 30000),
        "Headphones": (800, 6000),
        "Keyboard": (500, 3500),
        "Monitor": (7000, 22000),
    },
    "Furniture": {
        "Chair": (2000, 12000),
        "Table": (3500, 18000),
        "Desk": (4000, 20000),
        "Bookshelf": (2500, 9000),
    },
    "Office Supplies": {
        "Notebook": (40, 300),
        "Pen": (10, 100),
        "Printer": (4500, 16000),
        "File Folder": (30, 250),
    },
}

REGIONS = ["North", "South", "East", "West"]
CUSTOMER_TYPES = ["New", "Returning"]

# Rough per-unit profit margin range used to derive Profit from Sales.
MIN_MARGIN, MAX_MARGIN = 0.05, 0.35   # 5% to 35% profit margin

NUM_RECORDS = 250

# Flatten product list as (Product, Category, price_low, price_high)
FLAT_PRODUCTS = []
for category, products in PRODUCTS_BY_CATEGORY.items():
    for product, price_range in products.items():
        FLAT_PRODUCTS.append((product, category, price_range[0], price_range[1]))


def random_date_in_2025():
    """Return a random datetime.date between 1-Jan-2025 and 31-Dec-2025."""
    start = pd.Timestamp("2025-01-01")
    end = pd.Timestamp("2025-12-31")
    delta_days = (end - start).days
    random_offset = random.randint(0, delta_days)
    return start + pd.Timedelta(days=random_offset)


def generate_row(order_id):
    product, category, price_low, price_high = random.choice(FLAT_PRODUCTS)

    quantity = random.randint(1, 10)
    unit_price = round(random.uniform(price_low, price_high), 2)
    sales = round(unit_price * quantity, 2)

    margin = random.uniform(MIN_MARGIN, MAX_MARGIN)
    profit = round(sales * margin, 2)

    # A small percentage of rows are deliberately left with missing values
    # or duplicated later in the cleaning stage, to make the "Data Cleaning"
    # part of the project meaningful.
    region = random.choice(REGIONS)
    customer_type = random.choice(CUSTOMER_TYPES)
    order_date = random_date_in_2025()

    return {
        "Order_ID": f"ORD{order_id:05d}",
        "Date": order_date.strftime("%Y-%m-%d"),
        "Product": product,
        "Category": category,
        "Region": region,
        "Sales": sales,
        "Quantity": quantity,
        "Profit": profit,
        "Customer_Type": customer_type,
    }


def inject_data_quality_issues(df):
    """
    Intentionally introduces a small, controlled number of data quality
    issues (missing values + duplicate rows) so that the data-cleaning
    step of the project has real work to do. This mirrors what happens
    with real-world raw data.
    """
    df = df.copy()

    # 1. Introduce a few missing values in Sales, Profit and Region
    missing_idx_sales = np.random.choice(df.index, size=4, replace=False)
    df.loc[missing_idx_sales, "Sales"] = np.nan

    missing_idx_profit = np.random.choice(df.index, size=4, replace=False)
    df.loc[missing_idx_profit, "Profit"] = np.nan

    missing_idx_region = np.random.choice(df.index, size=3, replace=False)
    df.loc[missing_idx_region, "Region"] = None

    # 2. Duplicate a handful of rows (simulating accidental duplicate entries)
    duplicate_rows = df.sample(n=5, random_state=1)
    df = pd.concat([df, duplicate_rows], ignore_index=True)

    # 3. Introduce a couple of invalid (negative) numeric values
    invalid_idx = np.random.choice(df.index, size=2, replace=False)
    df.loc[invalid_idx, "Quantity"] = -df.loc[invalid_idx, "Quantity"]

    return df


def main():
    rows = [generate_row(i + 1) for i in range(NUM_RECORDS)]
    df = pd.DataFrame(rows)

    df = inject_data_quality_issues(df)

    # Shuffle rows so duplicated/injected rows aren't all at the bottom
    df = df.sample(frac=1, random_state=7).reset_index(drop=True)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, "sales_data.csv")
    xlsx_path = os.path.join(data_dir, "sales_data.xlsx")

    df.to_csv(csv_path, index=False)
    df.to_excel(xlsx_path, index=False, sheet_name="Sales_Data")

    print(f"Generated {len(df)} rows (including intentional data-quality issues).")
    print(f"Saved: {csv_path}")
    print(f"Saved: {xlsx_path}")


if __name__ == "__main__":
    main()

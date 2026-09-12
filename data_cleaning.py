"""
data_cleaning.py
-----------------
All data cleaning, preprocessing and derived-column logic for the project.

This module is imported by both:
  - app.py (the Streamlit dashboard)
  - scripts/run_cleaning.py (a standalone script to produce cleaned_sales_data.csv/.xlsx)

DOCUMENTED THRESHOLDS
======================
Sales_Category is assigned using the following thresholds, based on the
Sales column (in Rupees):

    Sales >= 20000            -> "High"
    5000 <= Sales < 20000     -> "Medium"
    Sales < 5000               -> "Low"

These thresholds were chosen because, in the generated dataset, big-ticket
items such as Laptops, Desks and Printers naturally produce higher order
values than small items such as Pens and Notebooks. The cut points roughly
split the dataset into three meaningful, explainable groups for a viva
demonstration.
"""

import numpy as np
import pandas as pd

HIGH_SALES_THRESHOLD = 20000
MEDIUM_SALES_THRESHOLD = 5000


def load_raw_data(path):
    """Load the raw sales dataset from a CSV file."""
    df = pd.read_csv(path)
    return df


def get_data_quality_report(df):
    """
    Returns a dictionary summarizing data quality issues found in the
    raw dataframe: missing values per column, duplicate row count, and
    any invalid (negative) numeric values.
    """
    report = {
        "missing_values": df.isnull().sum().to_dict(),
        "total_missing": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "negative_quantity_rows": int((df["Quantity"] < 0).sum()) if "Quantity" in df.columns else 0,
        "negative_sales_rows": int((df["Sales"] < 0).sum()) if "Sales" in df.columns else 0,
        "negative_profit_rows": int((df["Profit"] < 0).sum()) if "Profit" in df.columns else 0,
        "total_rows_before_cleaning": int(len(df)),
    }
    return report


def clean_data(df):
    """
    Cleans the raw sales dataframe and returns a fully cleaned dataframe
    with derived columns added.

    Cleaning steps (in order):
      1. Drop exact duplicate rows.
      2. Convert 'Date' to proper datetime.
      3. Fix invalid (negative) numeric values by converting them to their
         absolute value (a negative Quantity/Sales/Profit is treated as a
         data-entry sign error, not a return, for this simple project).
      4. Fill missing numeric values (Sales, Profit) using the median of
         their respective Category, since Category is the strongest
         predictor of order value in this dataset.
      5. Fill missing 'Region' values with the mode (most frequent region).
      6. Ensure correct data types for every column.
      7. Add derived columns: Month, Year, Total_Sales, Profit_Margin,
         Sales_Category.
    """
    df = df.copy()

    # --- 1. Remove duplicate rows -------------------------------------
    df = df.drop_duplicates().reset_index(drop=True)

    # --- 2. Convert Date to datetime -----------------------------------
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    # Drop any rows where the date genuinely could not be parsed
    df = df.dropna(subset=["Date"]).reset_index(drop=True)

    # --- 3. Fix invalid (negative) numeric values -----------------------
    for col in ["Sales", "Quantity", "Profit"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].abs()

    # --- 4. Fill missing Sales / Profit using category median -----------
    for col in ["Sales", "Profit"]:
        df[col] = df.groupby("Category")[col].transform(
            lambda s: s.fillna(s.median())
        )
        # Fallback: if a whole category was missing, use overall median
        df[col] = df[col].fillna(df[col].median())

    # --- 5. Fill missing Region with the mode ---------------------------
    if df["Region"].isnull().any():
        mode_region = df["Region"].mode().iloc[0]
        df["Region"] = df["Region"].fillna(mode_region)

    # --- 6. Ensure correct data types ------------------------------------
    df["Order_ID"] = df["Order_ID"].astype(str)
    df["Product"] = df["Product"].astype(str)
    df["Category"] = df["Category"].astype(str)
    df["Region"] = df["Region"].astype(str)
    df["Customer_Type"] = df["Customer_Type"].astype(str)
    df["Quantity"] = df["Quantity"].round().astype(int)
    df["Sales"] = df["Sales"].round(2)
    df["Profit"] = df["Profit"].round(2)

    # --- 7. Derived columns ------------------------------------------------
    df["Month"] = df["Date"].dt.month_name()
    df["Year"] = df["Date"].dt.year

    # Total_Sales here is defined as Sales (the line-item total already
    # represents unit_price * quantity from data generation). Kept as an
    # explicit column since dashboards / Power BI commonly expect it.
    df["Total_Sales"] = df["Sales"]

    # Profit_Margin = Profit / Sales * 100, guarding against division by zero
    df["Profit_Margin"] = np.where(
        df["Sales"] > 0,
        (df["Profit"] / df["Sales"]) * 100,
        0,
    ).round(2)

    df["Sales_Category"] = df["Sales"].apply(_categorize_sales)

    # Final column order for a clean, presentable dataset
    column_order = [
        "Order_ID", "Date", "Year", "Month", "Product", "Category", "Region",
        "Quantity", "Sales", "Profit", "Profit_Margin", "Total_Sales",
        "Sales_Category", "Customer_Type",
    ]
    df = df[column_order]

    return df


def _categorize_sales(sales_value):
    if sales_value >= HIGH_SALES_THRESHOLD:
        return "High"
    elif sales_value >= MEDIUM_SALES_THRESHOLD:
        return "Medium"
    else:
        return "Low"

"""
analysis.py
-----------
Reusable analysis functions that compute KPIs and aggregated tables from
the cleaned sales dataframe. Used by app.py (Streamlit dashboard) and by
scripts/generate_charts.py (static chart export for the report).
"""

import pandas as pd


def compute_kpis(df):
    """Return a dictionary of top-level KPIs for the given (filtered) dataframe."""
    if len(df) == 0:
        return {
            "total_sales": 0,
            "total_profit": 0,
            "total_quantity": 0,
            "total_orders": 0,
            "avg_order_value": 0,
            "avg_profit_margin": 0,
        }

    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_quantity = df["Quantity"].sum()
    total_orders = df["Order_ID"].nunique()
    avg_order_value = total_sales / total_orders if total_orders else 0
    avg_profit_margin = df["Profit_Margin"].mean()

    return {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "total_quantity": int(total_quantity),
        "total_orders": int(total_orders),
        "avg_order_value": round(avg_order_value, 2),
        "avg_profit_margin": round(avg_profit_margin, 2),
    }


def sales_by_category(df):
    return (
        df.groupby("Category", as_index=False)
        .agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"))
        .sort_values("Total_Sales", ascending=False)
    )


def sales_by_region(df):
    return (
        df.groupby("Region", as_index=False)
        .agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"))
        .sort_values("Total_Sales", ascending=False)
    )


def sales_trend_over_time(df):
    """Monthly sales trend, ordered chronologically."""
    trend = (
        df.groupby(pd.Grouper(key="Date", freq="MS"))
        .agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"))
        .reset_index()
        .sort_values("Date")
    )
    return trend


def top_products(df, n=10, by="Sales"):
    return (
        df.groupby("Product", as_index=False)
        .agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"), Total_Quantity=("Quantity", "sum"))
        .sort_values(by="Total_" + by if not by.startswith("Total_") else by, ascending=False)
        .head(n)
    )


def customer_type_summary(df):
    return (
        df.groupby("Customer_Type", as_index=False)
        .agg(Total_Sales=("Sales", "sum"), Total_Orders=("Order_ID", "nunique"))
    )


def sales_category_distribution(df):
    return df["Sales_Category"].value_counts().reset_index(name="Count").rename(columns={"index": "Sales_Category"})

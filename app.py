"""
app.py
------
Sales Data Analysis and Interactive Data Visualization
--------------------------------------------------------
A Streamlit dashboard for a Data Visualization training / college project.

Run with:
    streamlit run app.py

NOTE: The dataset used in this project (data/sales_data.csv) is a
SYNTHETICALLY GENERATED SAMPLE DATASET created for this project. It does
not represent any real company or real transactions.
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.data_cleaning import load_raw_data, clean_data, get_data_quality_report
from scripts.analysis import (
    compute_kpis,
    sales_by_category,
    sales_by_region,
    sales_trend_over_time,
    top_products,
    customer_type_summary,
    sales_category_distribution,
)

# ---------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Sales Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
)

sns.set_theme(style="whitegrid")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "sales_data.csv")


# ---------------------------------------------------------------------
# Cached data loading / cleaning
# ---------------------------------------------------------------------
@st.cache_data
def get_raw_data():
    if not os.path.exists(RAW_DATA_PATH):
        return None
    return load_raw_data(RAW_DATA_PATH)


@st.cache_data
def get_cleaned_data(raw_df):
    return clean_data(raw_df)


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
st.sidebar.title("📊 Sales Dashboard")
st.sidebar.markdown(
    "Sales Data Analysis and Interactive Data Visualization\n\n"
    "*Built with Python, Pandas, Matplotlib/Seaborn and Streamlit*"
)
st.sidebar.markdown("---")

raw_df = get_raw_data()

if raw_df is None:
    st.error(
        f"Dataset not found at `data/sales_data.csv`.\n\n"
        f"Please run `python scripts/generate_dataset.py` first to create the sample dataset."
    )
    st.stop()

cleaned_df = get_cleaned_data(raw_df)

# ---------------------------------------------------------------------
# Sidebar filters (applied to the cleaned dataset)
# ---------------------------------------------------------------------
st.sidebar.subheader("🔍 Filters")

min_date = cleaned_df["Date"].min().date()
max_date = cleaned_df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

regions = sorted(cleaned_df["Region"].unique().tolist())
selected_regions = st.sidebar.multiselect("Region", options=regions, default=regions)

categories = sorted(cleaned_df["Category"].unique().tolist())
selected_categories = st.sidebar.multiselect("Category", options=categories, default=categories)

customer_types = sorted(cleaned_df["Customer_Type"].unique().tolist())
selected_customer_types = st.sidebar.multiselect(
    "Customer Type", options=customer_types, default=customer_types
)

# Handle both a single date and a (start, end) tuple from date_input
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered_df = cleaned_df[
    (cleaned_df["Date"].dt.date >= start_date)
    & (cleaned_df["Date"].dt.date <= end_date)
    & (cleaned_df["Region"].isin(selected_regions))
    & (cleaned_df["Category"].isin(selected_categories))
    & (cleaned_df["Customer_Type"].isin(selected_customer_types))
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(filtered_df)}** of **{len(cleaned_df)}** cleaned records.")

# ---------------------------------------------------------------------
# Main title
# ---------------------------------------------------------------------
st.title("📊 Sales Data Analysis and Interactive Data Visualization")
st.caption(
    "College / Training Project — Python (Pandas, Matplotlib, Seaborn) + Streamlit + Power BI. "
    "Dataset is a generated sample dataset."
)

tabs = st.tabs(
    [
        "🏠 Overview & KPIs",
        "🧹 Raw Data & Cleaning",
        "💰 Sales & Profit",
        "📦 Product & Category",
        "🌍 Regional Analysis",
        "📈 Trends Over Time",
        "⬇️ Export"
    ]
)

# =======================================================================
# TAB 1: Overview & KPIs
# =======================================================================
with tabs[0]:
    st.subheader("Key Performance Indicators")

    kpis = compute_kpis(filtered_df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"₹{kpis['total_sales']:,.0f}")
    col2.metric("Total Profit", f"₹{kpis['total_profit']:,.0f}")
    col3.metric("Total Quantity Sold", f"{kpis['total_quantity']:,}")

    col4, col5, col6 = st.columns(3)
    col4.metric("Total Orders", f"{kpis['total_orders']:,}")
    col5.metric("Avg Order Value", f"₹{kpis['avg_order_value']:,.0f}")
    col6.metric("Avg Profit Margin", f"{kpis['avg_profit_margin']:.1f}%")

    st.markdown("---")
    st.subheader("Sales Category Distribution")
    st.caption("High / Medium / Low, based on documented Sales thresholds (see scripts/data_cleaning.py)")

    dist = filtered_df["Sales_Category"].value_counts().reindex(["High", "Medium", "Low"]).fillna(0)
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["#2e7d32", "#f9a825", "#c62828"]
    ax.bar(dist.index, dist.values, color=colors)
    ax.set_xlabel("Sales Category")
    ax.set_ylabel("Number of Orders")
    ax.set_title("Order Count by Sales Category")
    st.pyplot(fig)
    plt.close(fig)

# =======================================================================
# TAB 2: Raw Data & Cleaning
# =======================================================================
with tabs[1]:
    st.subheader("Raw Dataset (before cleaning)")
    st.write(f"Shape: {raw_df.shape[0]} rows × {raw_df.shape[1]} columns")
    st.dataframe(raw_df, use_container_width=True)

    st.markdown("---")
    st.subheader("Data Quality Report")

    report = get_data_quality_report(raw_df)

    qcol1, qcol2, qcol3 = st.columns(3)
    qcol1.metric("Total Missing Values", report["total_missing"])
    qcol2.metric("Duplicate Rows", report["duplicate_rows"])
    qcol3.metric("Negative Quantity Rows", report["negative_quantity_rows"])

    st.write("**Missing values per column:**")
    missing_df = pd.DataFrame(
        list(report["missing_values"].items()), columns=["Column", "Missing Count"]
    )
    st.dataframe(missing_df, use_container_width=True)

    st.markdown("---")
    st.subheader("Cleaned Dataset (after cleaning + derived columns)")
    st.caption(
        "Cleaning steps: remove duplicates → fix data types → convert Date → "
        "fix negative values → fill missing values → add derived columns "
        "(Month, Year, Total_Sales, Profit_Margin, Sales_Category)."
    )
    st.write(f"Shape: {cleaned_df.shape[0]} rows × {cleaned_df.shape[1]} columns")
    st.dataframe(cleaned_df, use_container_width=True)

# =======================================================================
# TAB 3: Sales & Profit Analysis
# =======================================================================
with tabs[2]:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Sales Distribution")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(filtered_df["Sales"], bins=20, kde=True, color="#1f77b4", ax=ax)
        ax.set_xlabel("Sales (₹)")
        ax.set_title("Distribution of Order Sales Value")
        st.pyplot(fig)
        plt.close(fig)

    with col_right:
        st.subheader("Profit Distribution")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(filtered_df["Profit"], bins=20, kde=True, color="#2ca02c", ax=ax)
        ax.set_xlabel("Profit (₹)")
        ax.set_title("Distribution of Order Profit")
        st.pyplot(fig)
        plt.close(fig)

    st.markdown("---")
    st.subheader("Sales vs Profit (by order)")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    sns.scatterplot(
        data=filtered_df, x="Sales", y="Profit", hue="Category", alpha=0.7, ax=ax
    )
    ax.set_title("Sales vs Profit, colored by Category")
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")
    st.subheader("Quantity Sold Analysis")
    qty_by_cat = filtered_df.groupby("Category", as_index=False)["Quantity"].sum().sort_values(
        "Quantity", ascending=False
    )
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=qty_by_cat, x="Category", y="Quantity", hue="Category", palette="viridis", legend=False, ax=ax)
    ax.set_title("Total Quantity Sold by Category")
    st.pyplot(fig)
    plt.close(fig)

# =======================================================================
# TAB 4: Product & Category Performance
# =======================================================================
with tabs[3]:
    st.subheader("Top Performing Products")

    n_products = st.slider("Number of top products to show", min_value=3, max_value=15, value=10)
    metric_choice = st.radio("Rank by", options=["Sales", "Profit", "Quantity"], horizontal=True)

    top_df = top_products(filtered_df, n=n_products, by=metric_choice)
    st.dataframe(top_df, use_container_width=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    sort_col = "Total_" + metric_choice
    sns.barplot(data=top_df, y="Product", x=sort_col, hue="Product", palette="mako", legend=False, ax=ax)
    ax.set_title(f"Top {n_products} Products by Total {metric_choice}")
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")
    st.subheader("Category Performance")

    cat_df = sales_by_category(filtered_df)
    st.dataframe(cat_df, use_container_width=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    sns.barplot(data=cat_df, x="Category", y="Total_Sales", hue="Category", palette="crest", legend=False, ax=axes[0])
    axes[0].set_title("Total Sales by Category")
    axes[0].tick_params(axis="x", rotation=15)

    axes[1].pie(
        cat_df["Total_Sales"],
        labels=cat_df["Category"],
        autopct="%1.1f%%",
        startangle=90,
    )
    axes[1].set_title("Sales Share by Category")
    st.pyplot(fig)
    plt.close(fig)

# =======================================================================
# TAB 5: Regional Analysis
# =======================================================================
with tabs[4]:
    st.subheader("Regional Performance")

    reg_df = sales_by_region(filtered_df)
    st.dataframe(reg_df, use_container_width=True)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    sns.barplot(data=reg_df, x="Region", y="Total_Sales", hue="Region", palette="flare", legend=False, ax=axes[0])
    axes[0].set_title("Total Sales by Region")

    sns.barplot(data=reg_df, x="Region", y="Total_Profit", hue="Region", palette="crest", legend=False, ax=axes[1])
    axes[1].set_title("Total Profit by Region")
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")
    st.subheader("Region vs Category Heatmap (Total Sales)")
    pivot = filtered_df.pivot_table(
        index="Region", columns="Category", values="Sales", aggfunc="sum", fill_value=0
    )
    fig, ax = plt.subplots(figsize=(9, 4.5))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax)
    ax.set_title("Total Sales: Region vs Category")
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")
    st.subheader("Customer Type Summary")
    cust_df = customer_type_summary(filtered_df)
    st.dataframe(cust_df, use_container_width=True)

# =======================================================================
# TAB 6: Trends Over Time
# =======================================================================
with tabs[5]:
    st.subheader("Monthly Sales & Profit Trend")

    trend_df = sales_trend_over_time(filtered_df)

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(trend_df["Date"], trend_df["Total_Sales"], marker="o", label="Total Sales", color="#1f77b4")
    ax.plot(trend_df["Date"], trend_df["Total_Profit"], marker="o", label="Total Profit", color="#2ca02c")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (₹)")
    ax.set_title("Sales & Profit Trend Over Time")
    ax.legend()
    fig.autofmt_xdate(rotation=45)
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")
    st.subheader("Monthly Trend Data")
    st.dataframe(trend_df, use_container_width=True)

# =======================================================================
# TAB 7: Export
# =======================================================================
with tabs[6]:
    st.subheader("Export Cleaned Dataset")
    st.write(
        "Download the cleaned dataset (with derived columns) as CSV or Excel. "
        "This is the same dataset used to power this dashboard and the Power BI report."
    )

    csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Cleaned Data (CSV)",
        data=csv_bytes,
        file_name="cleaned_sales_data.csv",
        mime="text/csv",
    )

    st.markdown("---")
    st.write(
        "A copy of the cleaned dataset is also saved automatically to "
        "`data/cleaned_sales_data.csv` and `data/cleaned_sales_data.xlsx` "
        "when you run `python scripts/run_cleaning.py`."
    )

st.markdown("---")
st.caption(
    "Sales Data Analysis and Interactive Data Visualization using Python and Power BI "
    "— Sample project, dataset generated synthetically."
)

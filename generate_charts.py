"""
generate_charts.py
-------------------
Generates a set of static PNG charts (Matplotlib / Seaborn) from the
cleaned dataset and saves them into the charts/ folder. Useful for
pasting into a project report or PPT, separate from the live Streamlit
dashboard.

Run AFTER run_cleaning.py:

    python scripts/generate_dataset.py
    python scripts/run_cleaning.py
    python scripts/generate_charts.py
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, safe for script execution
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.analysis import sales_by_category, sales_by_region, sales_trend_over_time, top_products

sns.set_theme(style="whitegrid")


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    charts_dir = os.path.join(project_root, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    cleaned_path = os.path.join(data_dir, "cleaned_sales_data.csv")
    if not os.path.exists(cleaned_path):
        raise FileNotFoundError(
            f"Could not find {cleaned_path}. Run scripts/run_cleaning.py first."
        )

    df = pd.read_csv(cleaned_path, parse_dates=["Date"])

    # 1. Sales by Category
    cat_df = sales_by_category(df)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.barplot(data=cat_df, x="Category", y="Total_Sales", hue="Category", palette="crest", legend=False, ax=ax)
    ax.set_title("Total Sales by Category")
    fig.tight_layout()
    fig.savefig(os.path.join(charts_dir, "sales_by_category.png"), dpi=150)
    plt.close(fig)

    # 2. Sales by Region
    reg_df = sales_by_region(df)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    sns.barplot(data=reg_df, x="Region", y="Total_Sales", hue="Region", palette="flare", legend=False, ax=ax)
    ax.set_title("Total Sales by Region")
    fig.tight_layout()
    fig.savefig(os.path.join(charts_dir, "sales_by_region.png"), dpi=150)
    plt.close(fig)

    # 3. Monthly sales trend
    trend_df = sales_trend_over_time(df)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(trend_df["Date"], trend_df["Total_Sales"], marker="o", color="#1f77b4")
    ax.set_title("Monthly Sales Trend (2025)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Sales (₹)")
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    fig.savefig(os.path.join(charts_dir, "monthly_sales_trend.png"), dpi=150)
    plt.close(fig)

    # 4. Top 10 products by sales
    top_df = top_products(df, n=10, by="Sales")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=top_df, y="Product", x="Total_Sales", hue="Product", palette="mako", legend=False, ax=ax)
    ax.set_title("Top 10 Products by Total Sales")
    fig.tight_layout()
    fig.savefig(os.path.join(charts_dir, "top_products.png"), dpi=150)
    plt.close(fig)

    # 5. Region vs Category heatmap
    pivot = df.pivot_table(index="Region", columns="Category", values="Sales", aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax)
    ax.set_title("Total Sales: Region vs Category")
    fig.tight_layout()
    fig.savefig(os.path.join(charts_dir, "region_vs_category_heatmap.png"), dpi=150)
    plt.close(fig)

    # 6. Sales Category distribution (High/Medium/Low)
    dist = df["Sales_Category"].value_counts().reindex(["High", "Medium", "Low"]).fillna(0)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(dist.index, dist.values, color=["#2e7d32", "#f9a825", "#c62828"])
    ax.set_title("Order Count by Sales Category")
    fig.tight_layout()
    fig.savefig(os.path.join(charts_dir, "sales_category_distribution.png"), dpi=150)
    plt.close(fig)

    print(f"Saved 6 charts to: {charts_dir}")


if __name__ == "__main__":
    main()

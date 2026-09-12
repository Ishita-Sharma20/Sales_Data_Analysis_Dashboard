"""
run_cleaning.py
----------------
Standalone script that loads the raw dataset, cleans it, and saves the
cleaned dataset as both CSV and Excel files.

Run this AFTER generate_dataset.py:

    python scripts/generate_dataset.py
    python scripts/run_cleaning.py
"""

import os
import sys

# Allow running this script directly (adds project root to path)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_cleaning import load_raw_data, clean_data, get_data_quality_report


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")

    raw_path = os.path.join(data_dir, "sales_data.csv")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(
            f"Could not find {raw_path}. Run scripts/generate_dataset.py first."
        )

    raw_df = load_raw_data(raw_path)

    report = get_data_quality_report(raw_df)
    print("Data Quality Report (before cleaning):")
    for key, value in report.items():
        print(f"  {key}: {value}")

    cleaned_df = clean_data(raw_df)

    cleaned_csv_path = os.path.join(data_dir, "cleaned_sales_data.csv")
    cleaned_xlsx_path = os.path.join(data_dir, "cleaned_sales_data.xlsx")

    cleaned_df.to_csv(cleaned_csv_path, index=False)
    cleaned_df.to_excel(cleaned_xlsx_path, index=False, sheet_name="Cleaned_Sales_Data")

    print(f"\nRows before cleaning: {len(raw_df)}")
    print(f"Rows after cleaning:  {len(cleaned_df)}")
    print(f"Saved: {cleaned_csv_path}")
    print(f"Saved: {cleaned_xlsx_path}")


if __name__ == "__main__":
    main()

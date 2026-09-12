# Sales Data Analysis and Interactive Data Visualization using Python and Power BI

A college / training project demonstrating an end-to-end data analytics
workflow: **generate → clean → analyze → visualize (Python + Streamlit)
→ visualize (Power BI)**.

> **Note on the dataset:** `data/sales_data.csv` is a **synthetically
> generated sample dataset** created specifically for this project
> (250 rows, Jan–Dec 2025). It does not represent any real company.

---

## 1. Project Structure

```
sales_project/
├── app.py                      # Streamlit dashboard (main application)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── data/
│   ├── sales_data.csv          # Raw generated dataset
│   ├── sales_data.xlsx         # Raw generated dataset (Excel)
│   ├── cleaned_sales_data.csv  # Cleaned dataset with derived columns
│   └── cleaned_sales_data.xlsx # Cleaned dataset (Excel)
├── scripts/
│   ├── generate_dataset.py     # Creates the sample dataset
│   ├── data_cleaning.py        # Cleaning + derived-column logic (importable module)
│   ├── run_cleaning.py         # Runs cleaning, saves cleaned_sales_data.csv/.xlsx
│   ├── analysis.py             # KPI / aggregation helper functions
│   └── generate_charts.py      # Exports static PNG charts to charts/
├── charts/                     # Static PNG charts (for report/PPT use)
└── powerbi/
    └── POWER_BI_GUIDE.md       # Step-by-step guide to build the Power BI report
```

## 2. Setup

Requires **Python 3.9+**.

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt
```

## 3. Run the project (in order)

```bash
# Step 1: Generate the sample raw dataset (data/sales_data.csv, .xlsx)
python scripts/generate_dataset.py

# Step 2: Clean the data and save the cleaned dataset
python scripts/run_cleaning.py

# Step 3 (optional): Export static charts to charts/ for your report/PPT
python scripts/generate_charts.py

# Step 4: Launch the interactive dashboard
streamlit run app.py
```

The dashboard opens automatically in your browser at `http://localhost:8501`.

> `app.py` also cleans the data itself at runtime (using
> `scripts/data_cleaning.py`), so steps 1–3 are only needed to produce the
> standalone `data/cleaned_sales_data.*` files and the `charts/` PNGs —
> the dashboard will still work with just Step 1 + Step 4.

## 4. Dashboard Features

The Streamlit dashboard (`app.py`) is organized into 7 tabs:

1. **Overview & KPIs** — Total Sales, Total Profit, Total Quantity, Total
   Orders, Average Order Value, Average Profit Margin, Sales Category
   distribution.
2. **Raw Data & Cleaning** — view the raw dataset, a full data-quality
   report (missing values, duplicates, invalid values), and the cleaned
   dataset with derived columns.
3. **Sales & Profit** — sales/profit distributions, sales-vs-profit
   scatter plot, quantity sold by category.
4. **Product & Category** — top N products (ranked by Sales, Profit, or
   Quantity — user selectable), category performance bar + pie chart.
5. **Regional Analysis** — sales/profit by region, region-vs-category
   heatmap, customer type summary.
6. **Trends Over Time** — monthly sales & profit trend line chart.
7. **Export** — download the cleaned dataset as CSV directly from the
   dashboard.

All charts respond live to the **sidebar filters**: date range, region,
category, and customer type.

## 5. Data Cleaning Logic (for your viva)

Implemented in `scripts/data_cleaning.py`, in this order:

1. Remove exact duplicate rows.
2. Convert `Date` to proper datetime; drop unparseable dates.
3. Fix invalid negative values in `Sales`, `Quantity`, `Profit` (treated as
   sign errors — converted to absolute value).
4. Fill missing `Sales`/`Profit` using the **median of their Category**
   (falls back to the overall median if a whole category is missing).
5. Fill missing `Region` with the **mode** (most frequent region).
6. Enforce correct data types on every column.
7. Add derived columns:
   - `Month`, `Year` — extracted from `Date`
   - `Total_Sales` — equal to `Sales` (kept as an explicit column since
     dashboards/Power BI commonly expect a `Total_Sales` field)
   - `Profit_Margin` = `Profit / Sales * 100`
   - `Sales_Category` — **High** (Sales ≥ ₹20,000), **Medium**
     (₹5,000 ≤ Sales < ₹20,000), **Low** (Sales < ₹5,000)

The raw dataset is deliberately generated with a few missing values,
duplicate rows, and invalid negative numbers (see
`scripts/generate_dataset.py → inject_data_quality_issues()`) so the
cleaning step has real, demonstrable work to do.

## 6. Power BI

See [`powerbi/POWER_BI_GUIDE.md`](powerbi/POWER_BI_GUIDE.md) for a full
step-by-step guide (data load, DAX measures, suggested pages/visuals,
slicers) to build `sales_dashboard.pbix` in Power BI Desktop using
`data/cleaned_sales_data.xlsx`.

A `.pbix` file itself isn't included because it can only be created and
saved from Power BI Desktop (Windows) — not generated by a script — but
every input file and measure you need is ready.

## 7. Technologies Used

| Purpose                     | Technology                  |
|------------------------------|-----------------------------|
| Data generation & cleaning   | Python, Pandas, NumPy       |
| Static charts                | Matplotlib, Seaborn         |
| Interactive dashboard        | Streamlit                   |
| Spreadsheet export           | OpenPyXL (via Pandas)       |
| BI report                    | Power BI                    |

## 8. Possible Viva Questions & Quick Answers

- **Why Category-median for filling missing Sales/Profit?** Category is
  the strongest predictor of an order's value in this dataset (a Laptop
  and a Pen have very different typical sales values), so it gives a more
  realistic fill than a single overall average.
- **Why convert negative values to absolute value instead of dropping
  them?** For this simple project they're treated as data-entry sign
  errors, not returns — dropping them would lose otherwise-good rows.
- **How is Profit_Margin calculated?** `Profit / Sales * 100`, guarded
  against division by zero.
- **How are Sales_Category thresholds decided?** Documented explicitly in
  `scripts/data_cleaning.py` — High ≥ ₹20,000, Medium ₹5,000–₹20,000,
  Low < ₹5,000 — chosen to roughly split the dataset into three
  explainable groups.

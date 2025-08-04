# index_calc/generate_excel_report.py

import pandas as pd
import numpy as np
import os

from openpyxl import load_workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
import matplotlib.pyplot as plt

INDEX_CSV = "reports/index_history.csv"
OUTPUT_EXCEL = "reports/index_report.xlsx"

# Load index history
df = pd.read_csv(INDEX_CSV, parse_dates=["Date"])
df["daily_return"] = df["index_level"].pct_change()
df.dropna(inplace=True)

# Summary metrics
cumulative_return = (df["index_level"].iloc[-1] / df["index_level"].iloc[0]) - 1
volatility = df["daily_return"].std() * np.sqrt(252)
max_drawdown = ((df["index_level"].cummax() - df["index_level"]) / df["index_level"].cummax()).max()

# Save Excel file with summary + full data
with pd.ExcelWriter(OUTPUT_EXCEL, engine="xlsxwriter") as writer:
    # Sheet 1: Summary
    summary_df = pd.DataFrame({
        "Metric": ["Cumulative Return", "Volatility", "Max Drawdown"],
        "Value": [f"{cumulative_return:.2%}", f"{volatility:.2%}", f"{max_drawdown:.2%}"]
    })
    summary_df.to_excel(writer, index=False, sheet_name="Summary")

    # Sheet 2: Full Index Data
    df.to_excel(writer, index=False, sheet_name="Index History")

    # Format columns
    workbook = writer.book
    worksheet = writer.sheets["Index History"]
    worksheet.set_column("A:A", 15)
    worksheet.set_column("B:C", 20)

    # Add line chart (plot separately and insert image)
    plt.figure(figsize=(8, 4))
    plt.plot(df["Date"], df["index_level"], label="Galactic AI Index", color="blue")
    plt.title("Galactic AI Index Over Time")
    plt.xlabel("Date")
    plt.ylabel("Index Level")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("reports/index_plot.png")
    plt.close()

# Insert chart image manually if needed
# Optional: use Excel to add image to the "Summary" sheet for presentation

print(f"Excel report saved to {OUTPUT_EXCEL}")

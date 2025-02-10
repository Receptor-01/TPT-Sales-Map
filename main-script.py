#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import logging
import os
import subprocess
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MultipleLocator

# ---- Configuration ----
LOG_FILE = "charts/main-script.log"
CSV_FILE_PATH = "sales-report.csv"
CHART_OUTPUT_PATH = "charts/sales_by_state_charts.pdf"

# ---- Logging Setup ----
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def notify(title, text):
    """Send a macOS notification."""
    subprocess.call(["osascript", "-e", f'display notification "{text}" with title "{title}"'])

def load_and_clean_data():
    """Load sales data, clean and return a Pandas DataFrame."""
    try:
        df = pd.read_csv(CSV_FILE_PATH)

        # Ensure required columns exist
        required_columns = ["State", "Order Id", "Your Earnings"]
        for col in required_columns:
            if col not in df.columns:
                logging.error(f"Missing column: {col}")
                raise ValueError(f"Missing column: {col}")

        # Convert currency to numeric values
        df["Your Earnings"] = df["Your Earnings"].replace(r"[\$,]", "", regex=True).astype(float)
        df.dropna(subset=["Your Earnings"], inplace=True)

        return df

    except Exception as e:
        logging.error(f"Error loading data: {e}")
        notify("Error", f"Failed to process data: {e}")
        raise

def generate_charts():
    """Generate and save bar charts for Top 10 States by Sales & Earnings."""
    df = load_and_clean_data()
    
    with PdfPages(CHART_OUTPUT_PATH) as pdf:
        # Chart 1: Top 10 States by Products Sold
        sales_by_units = df.groupby("State")["Order Id"].count().nlargest(10)

        if not sales_by_units.empty:
            fig, ax = plt.subplots(figsize=(11, 8.5))
            fig.patch.set_facecolor("black")
            ax.set_facecolor("black")

            sales_by_units.sort_values().plot(kind="barh", color="#39FF14", ax=ax)

            ax.set_title("Top 10 States by Products Sold", fontsize=16, color="white")
            ax.set_xlabel("Number of Products Sold", fontsize=14, color="#39FF14")
            ax.set_ylabel("State", fontsize=14, color="#39FF14")

            ax.tick_params(axis="both", colors="white")
            plt.xticks(color="white")
            plt.yticks(color="white")

            ax.xaxis.set_major_locator(MultipleLocator(5))
            ax.grid(True, axis="x", color="gray", linestyle="--", linewidth=0.5, alpha=0.5)

            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

        # Chart 2: Top 10 States by Sales Earnings
        sales_by_earnings = df.groupby("State")["Your Earnings"].sum().nlargest(10)

        if not sales_by_earnings.empty:
            fig, ax = plt.subplots(figsize=(11, 8.5))
            fig.patch.set_facecolor("black")
            ax.set_facecolor("black")

            sales_by_earnings.sort_values().plot(kind="barh", color="#39FF14", ax=ax)

            ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
            ax.set_title("Top 10 States by Sales Earnings", fontsize=16, color="white")
            ax.set_xlabel("Total Earnings ($)", fontsize=14, color="#39FF14")
            ax.set_ylabel("State", fontsize=14, color="#39FF14")

            ax.tick_params(axis="both", colors="white")
            plt.xticks(color="white")
            plt.yticks(color="white")

            ax.xaxis.set_major_locator(MultipleLocator(25))
            ax.grid(True, axis="x", color="gray", linestyle="--", linewidth=0.5, alpha=0.5)

            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    notify("Charts Generated", f"Sales charts saved at {CHART_OUTPUT_PATH}")

if __name__ == "__main__":
    generate_charts()

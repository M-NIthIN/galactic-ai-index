# index_calc/calculate_index.py

import pandas as pd
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rebalance.monthly_rebalancer import get_rebalancing_dates

# --- Config ---
DATA_DIR = "data"
OUTPUT_FILE = "reports/index_history.csv"
CONSTITUENTS_CSV = os.path.join(DATA_DIR, "constituents.csv")
BASE_INDEX_VALUE = 1000


def load_constituents():
    df = pd.read_csv(CONSTITUENTS_CSV)
    return df["ticker"].tolist(), dict(zip(df["ticker"], df["weight"]))


def load_price_data(tickers):
    price_frames = []

    for ticker in tickers:
        path = os.path.join(DATA_DIR, f"prices_{ticker}.csv")
        if not os.path.exists(path):
            print(f"Skipping {ticker} — file not found.")
            continue

        df = pd.read_csv(path, parse_dates=["Date"])[["Date", "close"]]
        df.rename(columns={"close": ticker}, inplace=True)

        # ✅ Convert prices to numeric (forcefully)
        df[ticker] = pd.to_numeric(df[ticker], errors="coerce")

        price_frames.append(df)

    if not price_frames:
        raise Exception("No price data available to calculate index.")

    df_prices = price_frames[0]
    for df in price_frames[1:]:
        df_prices = df_prices.merge(df, on="Date", how="inner")

    df_prices.sort_values("Date", inplace=True)
    df_prices.reset_index(drop=True, inplace=True)
    return df_prices


def calculate_returns(df_prices):
    df_returns = df_prices.copy()
    df_returns.iloc[:, 1:] = df_returns.iloc[:, 1:].pct_change(fill_method=None)
    df_returns.dropna(inplace=True)
    return df_returns


def generate_weight_schedule(df_returns, tickers):
    rebal_dates = get_rebalancing_dates(df_returns["Date"])
    equal_weight = 1 / len(tickers)

    weights_by_date = {}
    prev_date = None

    for date in df_returns["Date"]:
        if date in rebal_dates or not weights_by_date:
            weights_by_date[date] = {ticker: equal_weight for ticker in tickers}
        else:
            weights_by_date[date] = weights_by_date[prev_date]

        prev_date = date

    return weights_by_date


def calculate_index(df_returns, tickers, weights_by_date):
    index_returns = []

    for _, row in df_returns.iterrows():
        date = row["Date"]
        weights = weights_by_date[date]
        ret = sum(row[ticker] * weights[ticker] for ticker in tickers)
        index_returns.append(ret)

    index_levels = [BASE_INDEX_VALUE]
    for r in index_returns:
        index_levels.append(index_levels[-1] * (1 + r))

    df_index = df_returns[["Date"]].copy()
    df_index["index_return"] = index_returns
    df_index["index_level"] = index_levels[1:]  # drop initial base

    return df_index


def save_index(df_index):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df_index.to_csv(OUTPUT_FILE, index=False)
    print(f"Index with rebalancing saved to {OUTPUT_FILE}")


def main():
    print("Starting index calculation with monthly rebalancing...")

    tickers, weights = load_constituents()
    df_prices = load_price_data(tickers)
    df_returns = calculate_returns(df_prices)
    weights_by_date = generate_weight_schedule(df_returns, tickers)
    df_index = calculate_index(df_returns, tickers, weights_by_date)
    save_index(df_index)


if __name__ == "__main__":
    main()

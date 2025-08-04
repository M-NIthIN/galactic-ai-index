# index_calc/fetch_prices.py

import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta

# Paths
CONSTITUENTS_CSV = "data/constituents.csv"
DATA_DIR = "data"

# Setting Time
START_DATE = (datetime.today() - timedelta(days=180)).strftime('%Y-%m-%d')  # 6 months ago
END_DATE = datetime.today().strftime('%Y-%m-%d')

# Load constituents
df_constituents = pd.read_csv(CONSTITUENTS_CSV)
tickers = df_constituents["ticker"].tolist()

# Ensure output directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Fetch & save prices
for ticker in tickers:
    print(f"Fetching data for {ticker}...")

    try:
        data = yf.download(ticker, start=START_DATE, end=END_DATE)
        if data.empty:
            print(f"No data returned for {ticker}. Skipping.")
            continue

        data = data[["Close"]].rename(columns={"Close": "close"})
        data.reset_index(inplace=True)
        data.to_csv(f"{DATA_DIR}/prices_{ticker}.csv", index=False)

        print(f"Saved: prices_{ticker}.csv")

    except Exception as e:
        print(f"Error fetching {ticker}: {e}")

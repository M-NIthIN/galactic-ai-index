# index_calc/calculate_index.py

import pandas as pd
import os

DATA_DIR = "data"
OUTPUT_FILE = "reports/index_history.csv"
CONSTITUENTS_CSV = f"{DATA_DIR}/constituents.csv"
BASE_INDEX_VALUE = 1000

# Load constituent metadata
constituents = pd.read_csv(CONSTITUENTS_CSV)
tickers = constituents["ticker"].tolist()

# Load and merge all price data
price_frames = []

for ticker in tickers:
    price_path = f"{DATA_DIR}/prices_{ticker}.csv"
    if not os.path.exists(price_path):
        print(f"Missing data for {ticker}, skipping.")
        continue

    df = pd.read_csv(price_path, parse_dates=["Date"])


    # Keep only 'Date' and 'close', and coerce 'close' to numeric
    df = df[["Date", "close"]].copy()
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    
    # Drop any rows where close is NaN
    df.dropna(subset=["close"], inplace=True)
    
    df.rename(columns={"close": ticker}, inplace=True)

    price_frames.append(df)

# Merge all into one DataFrame on Date
df_prices = price_frames[0]
for df in price_frames[1:]:
    df_prices = df_prices.merge(df, on="Date", how="inner")

df_prices.sort_values("Date", inplace=True)
df_prices.reset_index(drop=True, inplace=True)

# Calculate daily returns
df_returns = df_prices.copy()
df_returns.iloc[:, 1:] = df_returns.iloc[:, 1:].pct_change()

# Apply weights
weights = dict(zip(constituents["ticker"], constituents["weight"]))
df_returns["index_return"] = sum(df_returns[ticker] * weights[ticker] for ticker in weights if ticker in df_returns)

# Drop first row (NaN returns)
df_returns.dropna(inplace=True)

# Calculate index level
index_levels = [BASE_INDEX_VALUE]
for r in df_returns["index_return"]:
    index_levels.append(index_levels[-1] * (1 + r))

# Create index DataFrame
df_index = df_returns[["Date"]].copy()
df_index["index_level"] = index_levels[1:]  # drop initial base value

# Save to CSV
os.makedirs("reports", exist_ok=True)
df_index.to_csv(OUTPUT_FILE, index=False)
print(f"Index saved to {OUTPUT_FILE}")

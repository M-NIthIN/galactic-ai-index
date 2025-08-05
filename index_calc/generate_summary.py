import pandas as pd
import matplotlib.pyplot as plt
import os

# Paths
input_path = "reports/index_history.csv"
output_chart = "reports/galactic_index_trend.png"

# Read index history
df = pd.read_csv(input_path, parse_dates=["Date"])
df.sort_values("Date", inplace=True)

# Calculate metrics
returns = df["index_level"].pct_change().dropna()
cumulative_return = (df["index_level"].iloc[-1] / df["index_level"].iloc[0]) - 1
volatility = returns.std() * (252 ** 0.5)
max_drawdown = ((df["index_level"].cummax() - df["index_level"]) / df["index_level"].cummax()).max()

# Save metrics as CSV
summary_df = pd.DataFrame({
    "Metric": ["Cumulative Return", "Volatility (Annual)", "Max Drawdown"],
    "Value": [
        f"{cumulative_return:.2%}",
        f"{volatility:.2%}",
        f"{max_drawdown:.2%}"
    ]
})
summary_df.to_csv("reports/index_summary.csv", index=False)

# Plot chart
plt.figure(figsize=(10, 4))
plt.plot(df["Date"], df["index_level"], color="blue")
plt.title("Galactic AI Index Over Time")
plt.xlabel("Date")
plt.ylabel("index_level")
plt.grid(True)
plt.tight_layout()
plt.savefig(output_chart)
print("Summary chart and metrics saved!")

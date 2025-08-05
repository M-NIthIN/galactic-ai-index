# rebalance/monthly_rebalancer.py

import pandas as pd

def get_rebalancing_dates(dates: pd.Series) -> list:
    """
    Returns a list of first trading days of each month from a list of dates.
    """
    df = pd.DataFrame({"Date": dates})
    df["Month"] = df["Date"].dt.to_period("M")
    return df.groupby("Month")["Date"].min().tolist()

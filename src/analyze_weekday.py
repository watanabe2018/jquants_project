import pandas as pd
import numpy as np

INPUT_PATH = "../data/toyota_7203_daily.csv"
OUTPUT_PATH = "../data/toyota_7203_weekday_anomaly.csv"

df = pd.read_csv(INPUT_PATH)

if df.empty:
    raise RuntimeError("入力CSVが空です")

required_cols = {"Date", "AdjO", "AdjC"}
missing = required_cols - set(df.columns)
if missing:
    raise RuntimeError(f"必要な列がありません: {missing}")

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")

df["ret_oc"] = df["AdjC"] / df["AdjO"] - 1
df["weekday"] = df["Date"].dt.day_name()

summary = (
    df.groupby("weekday")["ret_oc"]
    .agg(
        count="count",
        mean="mean",
        median="median",
        std="std",
        win_rate=lambda x: (x > 0).mean(),
    )
    .reset_index()
)

summary["mean_pct"] = summary["mean"] * 100
summary["median_pct"] = summary["median"] * 100
summary["win_rate_pct"] = summary["win_rate"] * 100

weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
summary["weekday"] = pd.Categorical(
    summary["weekday"],
    categories=weekday_order,
    ordered=True,
)
summary = summary.sort_values("weekday")

summary.to_csv(OUTPUT_PATH, index=False)

print(summary)
print(f"saved: {OUTPUT_PATH}")
from dotenv import load_dotenv
from jquantsapi import ClientV2
import pandas as pd
import os
import time

load_dotenv()

API_KEY = os.getenv("JQUANTS_API_KEY")
if not API_KEY:
    raise RuntimeError("JQUANTS_API_KEY が設定されていません")

cli = ClientV2(api_key=API_KEY)

print("requesting range...")

start = time.time()

df = cli.get_eq_bars_daily_range(
    start_dt="20240104",
    end_dt="20240110",
)

elapsed = time.time() - start

if df.empty:
    raise RuntimeError("取得データが空です")

required_cols = {"Date", "Code", "AdjO", "AdjH", "AdjL", "AdjC", "AdjVo"}
missing = required_cols - set(df.columns)
if missing:
    raise RuntimeError(f"必要な列がありません: {missing}")

print(df.head())
print(df.shape)
print(f"elapsed sec = {elapsed:.2f}")

os.makedirs("../data/raw/range", exist_ok=True)

out_path = "../data/raw/range/20240104_20240110.csv"
df.to_csv(out_path, index=False)

print(f"saved: {out_path}")
from dotenv import load_dotenv
from jquantsapi import ClientV2
import pandas as pd
import os
import time
from requests.exceptions import HTTPError, RetryError

load_dotenv()

API_KEY = os.getenv("JQUANTS_API_KEY")
if not API_KEY:
    raise RuntimeError("JQUANTS_API_KEY が .env に設定されていません")

CODE = "7203"
START_DATE = "20240213"
END_DATE = "20240229"

SLEEP_SEC = 30
MAX_RETRY = 2

OUT_DIR = "../data"
PARTIAL_PATH = f"{OUT_DIR}/toyota_7203_daily_partial.csv"
FINAL_PATH = f"{OUT_DIR}/toyota_7203_daily.csv"

os.makedirs(OUT_DIR, exist_ok=True)

cli = ClientV2(api_key=API_KEY)

dates = pd.bdate_range(START_DATE, END_DATE)
all_dfs = []

for dt in dates:
    date_str = dt.strftime("%Y%m%d")
    print(f"requesting {CODE} {date_str}...")

    success = False

    for attempt in range(1, MAX_RETRY + 1):
        try:
            df = cli.get_eq_bars_daily(
                code=CODE,
                date_yyyymmdd=date_str,
            )

            if df.empty:
                print(f"  no data: {date_str}")
            else:
                print(f"  received: {len(df)} rows")
                all_dfs.append(df)

                temp = pd.concat(all_dfs, ignore_index=True)
                temp = temp.sort_values("Date")
                temp.to_csv(PARTIAL_PATH, index=False)
                print(f"  partial saved: {PARTIAL_PATH}")

            success = True
            break

        except (HTTPError, RetryError) as e:
            wait_sec = 60 * attempt
            print(f"  error attempt {attempt}: {e}")
            print(f"  sleeping {wait_sec} sec...")
            time.sleep(wait_sec)

    if not success:
        print(f"  skipped after retries: {date_str}")

    print(f"sleeping {SLEEP_SEC} sec...")
    time.sleep(SLEEP_SEC)

if not all_dfs:
    raise RuntimeError("取得できたデータが0件です。CSV保存を中止します。")

result = pd.concat(all_dfs, ignore_index=True)
result = result.sort_values("Date")

required_cols = {"Date", "Code", "AdjO", "AdjH", "AdjL", "AdjC", "AdjVo"}
missing = required_cols - set(result.columns)
if missing:
    raise RuntimeError(f"必要な列がありません: {missing}")

if result.empty:
    raise RuntimeError("最終データが空です。CSV保存を中止します。")

result.to_csv(FINAL_PATH, index=False)

print("done")
print(result.head())
print(result.tail())
print(result.shape)
print(f"saved: {FINAL_PATH}")
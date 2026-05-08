from dotenv import load_dotenv
from jquantsapi import ClientV2
import os

load_dotenv()

API_KEY = os.getenv("JQUANTS_API_KEY")

cli = ClientV2(api_key=API_KEY)

print("requesting one day...")

df = cli.get_eq_bars_daily(
    code="7203",
    date_yyyymmdd="20240213",
)

print("data received")
print(df.head())

os.makedirs("../data", exist_ok=True)

df.to_csv("../data/toyota_7203_20240213.csv", index=False)

print("csv saved")
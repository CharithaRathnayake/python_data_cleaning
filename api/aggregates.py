import pandas as pd
from pathlib import Path

BASE = Path("./api")

# 1. Load cleaned parquet
df = pd.read_parquet(BASE / "cleaned.parquet")

# Daily avg close by ticker 
agg_daily_avg_close = (
    df.groupby(["trade_date", "ticker"], as_index=False)
      .agg(avg_close=("close_price", "mean"))
)

agg_daily_avg_close.to_parquet(BASE / "agg_daily_avg_close.parquet", index=False)


# Avg volume by sector

agg_avg_volume_sector = (
    df.groupby("sector", as_index=False)
        .agg(avg_volume=("volume", "mean"))
)

agg_avg_volume_sector.to_parquet(BASE / "agg_avg_volume_sector.parquet",
                                    index=False)


# Simple daily return by ticker 
df_sorted = df.sort_values(["ticker", "trade_date"])
df_sorted["daily_return"] = (
    df_sorted.groupby("ticker")["close_price"].pct_change(fill_method=None)
)

# Keep only rows where return is defined
agg_daily_return = (
    df_sorted[["trade_date", "ticker", "daily_return"]]
    .dropna(subset=["daily_return"])
)

agg_daily_return.to_parquet(BASE / "agg_daily_return.parquet", index=False)

print("Aggregates written:")
print(" - agg_daily_avg_close.parquet")
if "sector" in df.columns:
    print(" - agg_avg_volume_sector.parquet")
print(" - agg_daily_return.parquet")

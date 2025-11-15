import pandas as pd
import streamlit as st
from pathlib import Path

BASE = Path("./api")

@st.cache_data
def load_agg_daily_avg_close():
    df = pd.read_parquet(BASE / "agg_daily_avg_close.parquet")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df

@st.cache_data
def load_agg_daily_return():
    df = pd.read_parquet(BASE / "agg_daily_return.parquet")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df

@st.cache_data
def load_agg_avg_volume_sector():
    path = BASE / "agg_avg_volume_sector.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return None


st.title("Stock Aggregates Explorer 📈")

tab1, tab2, tab3 = st.tabs(["Daily Avg Close", "Daily Return", "Volume by Sector"])

# Daily Avg Close by Ticker 
with tab1:
    st.subheader("Daily Average Close by Ticker")

    df_close = load_agg_daily_avg_close()
    df_close["trade_date"] = pd.to_datetime(df_close["trade_date"])

    # Sidebar filters
    st.sidebar.header("Filters")

    min_date = df_close["trade_date"].min().date()
    max_date = df_close["trade_date"].max().date()

    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    all_tickers = sorted(df_close["ticker"].unique())
    selected_tickers = st.sidebar.multiselect(
        "Tickers",
        options=all_tickers,
        default=all_tickers[:5] if len(all_tickers) > 5 else all_tickers,
    )

    # Apply filters
    mask = (
        (df_close["trade_date"].dt.date >= date_range[0]) &
        (df_close["trade_date"].dt.date <= date_range[1])
    )
    if selected_tickers:
        mask &= df_close["ticker"].isin(selected_tickers)

    df_close_filtered = df_close[mask]

    # Pivot for bar chart (date as index, tickers as columns)
    pivot_close = df_close_filtered.pivot_table(
        index="trade_date",
        columns="ticker",
        values="avg_close"
    ).sort_index()

    st.bar_chart(pivot_close)

    st.dataframe(
        df_close_filtered.sort_values(["trade_date", "ticker"]).head(50)
    )



# Daily Return by Ticker 
with tab2:
    st.subheader("Daily Return by Ticker")

    df_ret = load_agg_daily_return()
    df_ret["trade_date"] = pd.to_datetime(df_ret["trade_date"])

    min_date = df_ret["trade_date"].min().date()
    max_date = df_ret["trade_date"].max().date()

    date_range_ret = st.sidebar.date_input(
        "Date range (returns)",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="returns_date",
    )

    all_tickers_ret = sorted(df_ret["ticker"].unique())
    selected_tickers_ret = st.sidebar.multiselect(
        "Tickers (returns)",
        options=all_tickers_ret,
        default=all_tickers_ret[:5] if len(all_tickers_ret) > 5 else all_tickers_ret,
        key="returns_tickers",
    )

    mask_ret = (
        (df_ret["trade_date"].dt.date >= date_range_ret[0]) &
        (df_ret["trade_date"].dt.date <= date_range_ret[1])
    )
    if selected_tickers_ret:
        mask_ret &= df_ret["ticker"].isin(selected_tickers_ret)

    df_ret_filtered = df_ret[mask_ret]

    pivot_ret = df_ret_filtered.pivot_table(
        index="trade_date",
        columns="ticker",
        values="daily_return"
    ).sort_index()

    st.bar_chart(pivot_ret)

    st.dataframe(
        df_ret_filtered.sort_values(["trade_date", "ticker"]).head(50)
    )

# Avg Volume by Sector 
with tab3:
    st.subheader("Average Volume by Sector")

    df_sector = load_agg_avg_volume_sector()
    if df_sector is None:
        st.info("No sector data found (agg_avg_volume_sector.parquet missing).")
    else:
        st.bar_chart(
            df_sector.set_index("sector")["avg_volume"]
        )
        st.dataframe(df_sector.sort_values("avg_volume", ascending=False))

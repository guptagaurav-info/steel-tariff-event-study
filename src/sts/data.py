"""Daily total returns (price + dividends) for the steel stocks, SPY and the base-metals fund."""
import pandas as pd
import pyarrow.parquet as pq

RAW = "data/raw/"


def total_return(sym):
    px = pq.read_table(RAW + "stock_prices.parquet", columns=["symbol", "report_date", "close"], filters=[("symbol", "=", sym)]).to_pandas()
    px.index = pd.to_datetime(px.pop("report_date")); px = px["close"].astype(float).sort_index()
    px = px[~px.index.duplicated()]
    dv = pq.read_table(RAW + "stock_dividend_events.parquet", filters=[("symbol", "=", sym)]).to_pandas()
    dv.index = pd.to_datetime(dv.pop("report_date"))
    dv = dv["amount"].astype(float).groupby(level=0).sum().reindex(px.index).fillna(0.0)
    return ((px + dv) / px.shift(1) - 1).iloc[1:]


def panel(cfg):
    syms = [cfg["market"], cfg["metals_proxy"]] + list(cfg["us_steel"]) + list(cfg["foreign_steel"])
    return pd.DataFrame({s: total_return(s) for s in syms}).sort_index()

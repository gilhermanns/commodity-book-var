from __future__ import annotations

import logging
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from .book import CONTRACTS

warnings.filterwarnings("ignore")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_prices(start: str = "2007-08-01", max_age_hours: float = 12) -> pd.DataFrame:
    DATA_DIR.mkdir(exist_ok=True)
    cache = DATA_DIR / "prices.csv"
    if cache.exists() and time.time() - cache.stat().st_mtime < max_age_hours * 3600:
        return pd.read_csv(cache, index_col=0, parse_dates=True)
    tick = {c.ticker: k for k, c in CONTRACTS.items()}
    raw = yf.download(list(tick), start=start, auto_adjust=True, progress=False, threads=False)["Close"]
    px = raw.rename(columns=tick)[list(CONTRACTS)]
    px.index = pd.to_datetime(px.index).tz_localize(None)
    px = px.ffill(limit=3).dropna()
    px.to_csv(cache)
    return px


def relative_returns(px: pd.DataFrame) -> pd.DataFrame:
    """Daily simple returns used to build scenarios.

    A relative return has no meaning when yesterday's price is zero or negative,
    and is absurd when it is a few dollars: WTI on 20 Apr 2020 is a -306% 'return'.
    Those days are zeroed for every contract, i.e. removed as scenarios. Zeroing
    only WTI would leave a crack or Brent-WTI spread with one leg missing and
    invent a loss that never happened. The dollar P&L of those days is untouched:
    it comes from price differences and stays in the backtest.
    """
    r = px.pct_change()
    bad = (px <= 0) | (px.shift(1) <= 0) | (r < -0.9)
    bad_day = bad.any(axis=1)
    bad_day = bad_day | bad_day.shift(1, fill_value=False)
    r.loc[bad_day] = 0.0
    return r.iloc[1:]


def dollar_pnl(px: pd.DataFrame, book: dict[str, float]) -> pd.Series:
    """Actual daily P&L of holding the book: price change x multiplier x contracts."""
    mult = pd.Series({k: CONTRACTS[k].dollar_per_point * q for k, q in book.items()})
    return (px[list(book)].diff() * mult).sum(axis=1).iloc[1:]


def exposures(px_row: pd.Series, book: dict[str, float]) -> pd.Series:
    """Signed notional per position in dollars at the given prices."""
    return pd.Series({k: px_row[k] * CONTRACTS[k].dollar_per_point * q for k, q in book.items()})

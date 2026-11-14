"""Rolling backtest: every day, compute VaR from data up to yesterday, then see
what the book actually made today. Count how often the loss was bigger than VaR."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2

from . import var as V
from .book import CONTRACTS


def rolling(px: pd.DataFrame, rets: pd.DataFrame, book: dict[str, float], level: float = 0.99,
            start: int = 750) -> pd.DataFrame:
    names = list(book)
    r = rets[names].to_numpy()
    p = px[names].to_numpy()[1:]                      # aligned with rets: p[t] is the close of day t
    mult = np.array([CONTRACTS[k].dollar_per_point * book[k] for k in names])
    sig = V.ewma_vol_path(r)
    actual = (np.diff(px[names].to_numpy(), axis=0) * mult).sum(axis=1)   # true dollar P&L per day
    cov = V.ewma_cov(r[:start])
    rows = []
    for t in range(start, len(r)):
        expo = p[t - 1] * mult                         # exposure at yesterday's close
        hist_v, _ = V.historical(r[:t], expo, level)
        par_v = V.norm.ppf(level) * np.sqrt(expo @ cov @ expo)
        fil_v, _ = V.filtered(r[:t], sig[:t], sig[t], expo, level)
        rows.append((rets.index[t], actual[t], hist_v, par_v, fil_v))
        cov = V.LAMBDA * cov + (1 - V.LAMBDA) * np.outer(r[t], r[t])
    return pd.DataFrame(rows, columns=["date", "pnl", "historical (500d)", "parametric EWMA", "filtered historical"]).set_index("date")


def kupiec(n: int, x: int, p: float) -> float:
    """p-value of the proportion-of-failures test. Small = exception rate is off."""
    if x == 0:
        lr = -2 * n * np.log(1 - p)
    else:
        phat = x / n
        lr = -2 * ((n - x) * np.log(1 - p) + x * np.log(p)) + 2 * ((n - x) * np.log(1 - phat) + x * np.log(phat))
    return float(chi2.sf(lr, 1))


def christoffersen(hits: np.ndarray) -> float:
    """p-value of the independence test. Small = exceptions come in clusters."""
    h = hits.astype(int)
    n00 = int(((h[:-1] == 0) & (h[1:] == 0)).sum()); n01 = int(((h[:-1] == 0) & (h[1:] == 1)).sum())
    n10 = int(((h[:-1] == 1) & (h[1:] == 0)).sum()); n11 = int(((h[:-1] == 1) & (h[1:] == 1)).sum())
    if n01 + n11 == 0 or n00 + n10 == 0:
        return float("nan")
    p01 = n01 / (n00 + n01); p11 = n11 / (n10 + n11) if (n10 + n11) else 0.0
    pi = (n01 + n11) / (n00 + n01 + n10 + n11)

    def ll(p, a, b):
        return (a * np.log(1 - p) if a else 0.0) + (b * np.log(p) if b else 0.0)
    lr = -2 * (ll(pi, n00 + n10, n01 + n11) - ll(p01, n00, n01) - ll(p11, n10, n11))
    return float(chi2.sf(lr, 1))


def scorecard(bt: pd.DataFrame, level: float = 0.99) -> pd.DataFrame:
    rows = []
    n = len(bt)
    for m in bt.columns[1:]:
        hits = (bt["pnl"] < -bt[m]).to_numpy()
        x = int(hits.sum())
        worst_ratio = (-bt["pnl"] / bt[m])[hits].max() if x else np.nan
        rows.append({"model": m, "days": n, "exceptions": x, "expected": n * (1 - level),
                     "rate %": x / n * 100, "Kupiec p": kupiec(n, x, 1 - level),
                     "independence p": christoffersen(hits),
                     "worst loss / VaR": worst_ratio, "avg VaR $": bt[m].mean()})
    return pd.DataFrame(rows)


def by_year(bt: pd.DataFrame) -> pd.DataFrame:
    hits = pd.DataFrame({m: bt["pnl"] < -bt[m] for m in bt.columns[1:]})
    out = hits.groupby(hits.index.year).sum()
    out.insert(0, "days", hits.groupby(hits.index.year).size())
    out.index.name = "year"
    return out

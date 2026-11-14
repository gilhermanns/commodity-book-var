"""Three one-day VaR models on the same book.

historical   replay the last 500 days of returns on today's exposures
parametric   normal quantile with an EWMA covariance matrix (RiskMetrics, lambda 0.94)
filtered     historical simulation on volatility-standardised returns, rescaled to
             today's volatility: keeps the fat tails of the data and reacts when
             volatility changes

All numbers are losses reported as positive dollars.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm

LAMBDA = 0.94
HS_WINDOW = 500


def ewma_cov(r: np.ndarray, lam: float = LAMBDA) -> np.ndarray:
    """EWMA covariance after the last row of r. r is (days, assets)."""
    n = len(r)
    w = (1 - lam) * lam ** np.arange(n - 1, -1, -1)
    w /= w.sum()
    return (r * w[:, None]).T @ r


def ewma_vol_path(r: np.ndarray, lam: float = LAMBDA, warmup: int = 60) -> np.ndarray:
    """sigma[t] = volatility forecast for day t made with returns before t."""
    var = np.empty_like(r)
    var[0] = r[:warmup].var(axis=0)
    for t in range(1, len(r)):
        var[t] = lam * var[t - 1] + (1 - lam) * r[t - 1] ** 2
    return np.sqrt(var)


def _var_es(pnl: np.ndarray, level: float) -> tuple[float, float]:
    q = np.quantile(pnl, 1 - level)
    tail = pnl[pnl <= q]
    return -q, -tail.mean()


def historical(r: np.ndarray, expo: np.ndarray, level: float = 0.99, window: int = HS_WINDOW):
    pnl = r[-window:] @ expo
    return _var_es(pnl, level)


def parametric(r: np.ndarray, expo: np.ndarray, level: float = 0.99):
    cov = ewma_cov(r)
    sd = float(np.sqrt(expo @ cov @ expo))
    z = norm.ppf(level)
    return z * sd, sd * norm.pdf(z) / (1 - level)


def filtered(r: np.ndarray, sig: np.ndarray, sig_next: np.ndarray, expo: np.ndarray,
             level: float = 0.99, window: int = HS_WINDOW):
    """r, sig are aligned (sig[t] forecast for r[t]); sig_next is the forecast for tomorrow."""
    z = r[-window:] / sig[-window:]
    pnl = (z * sig_next) @ expo
    return _var_es(pnl, level)


def component_var(r: np.ndarray, expo: np.ndarray, names, level: float = 0.99) -> pd.DataFrame:
    """Euler allocation of parametric VaR: how much each position adds to the total.
    Components sum to the total. A negative number is a position that hedges the book."""
    cov = ewma_cov(r)
    sd = float(np.sqrt(expo @ cov @ expo))
    z = norm.ppf(level)
    comp = z * expo * (cov @ expo) / sd
    alone = z * np.abs(expo) * np.sqrt(np.diag(cov))
    return pd.DataFrame({"exposure $": expo, "stand-alone VaR $": alone, "component VaR $": comp,
                         "share of book VaR %": comp / comp.sum() * 100}, index=list(names))


def snapshot(rets: pd.DataFrame, expo: pd.Series, levels=(0.95, 0.99)) -> pd.DataFrame:
    r = rets[expo.index].to_numpy()
    sig = ewma_vol_path(r)
    sig_next = np.sqrt(LAMBDA * sig[-1] ** 2 + (1 - LAMBDA) * r[-1] ** 2)
    e = expo.to_numpy()
    rows = []
    for lv in levels:
        for name, (v, es) in [("historical (500d)", historical(r, e, lv)),
                              ("parametric EWMA", parametric(r, e, lv)),
                              ("filtered historical", filtered(r, sig, sig_next, e, lv))]:
            rows.append({"confidence": f"{lv:.0%}", "model": name, "1-day VaR $": v, "expected shortfall $": es})
    return pd.DataFrame(rows)

import numpy as np
import pandas as pd
from scipy.stats import norm

from bookvar import backtest, data, var
from bookvar.book import CONTRACTS


def test_contract_multipliers():
    # one contract, price up by one quoted unit
    assert CONTRACTS["CL"].dollar_per_point == 1_000          # 1,000 bbl x $1
    assert CONTRACTS["HO"].dollar_per_point == 42_000         # 42,000 gal x $1
    assert CONTRACTS["ZC"].dollar_per_point == 50             # 5,000 bu x 1 cent
    assert CONTRACTS["KC"].dollar_per_point == 375            # 37,500 lb x 1 cent
    px = pd.DataFrame({"CL": [80.0, 81.5], "ZC": [450.0, 446.0]}, index=pd.bdate_range("2024-01-01", periods=2))
    pnl = data.dollar_pnl(px, {"CL": -10, "ZC": 20})
    assert np.isclose(pnl.iloc[0], -10 * 1.5 * 1000 + 20 * -4 * 50)


def test_parametric_var_matches_closed_form():
    rng = np.random.default_rng(0)
    r = rng.normal(0, 0.02, (4000, 1))
    v, es = var.parametric(r, np.array([1_000_000.0]), 0.99)
    assert abs(v / (norm.ppf(0.99) * 0.02 * 1e6) - 1) < 0.25   # EWMA is noisy but in the right place
    assert es > v


def test_components_sum_to_total_and_hedges_are_negative():
    rng = np.random.default_rng(1)
    common = rng.normal(0, 0.02, 3000)
    r = np.column_stack([common + rng.normal(0, 0.003, 3000), common + rng.normal(0, 0.003, 3000)])
    expo = np.array([1_000_000.0, -600_000.0])                 # long one, short a smaller amount of its twin
    comp = var.component_var(r, expo, ["A", "B"])
    total, _ = var.parametric(r, expo, 0.99)
    assert np.isclose(comp["component VaR $"].sum(), total)
    assert comp.loc["B", "component VaR $"] < 0


def test_negative_price_day_is_not_a_scenario_but_stays_in_pnl():
    idx = pd.bdate_range("2020-04-15", periods=6)
    px = pd.DataFrame({"CL": [20.0, 18.0, 18.3, -37.6, 10.0, 13.8]}, index=idx)
    r = data.relative_returns(px)
    assert r.loc[idx[3], "CL"] == 0 and r.loc[idx[4], "CL"] == 0
    pnl = data.dollar_pnl(px, {"CL": 1})
    assert np.isclose(pnl.loc[idx[3]], (-37.6 - 18.3) * 1000)


def test_kupiec_and_independence():
    assert backtest.kupiec(1000, 10, 0.01) > 0.9               # exactly the expected number
    assert backtest.kupiec(1000, 30, 0.01) < 0.001             # three times too many
    clustered = np.zeros(1000, dtype=bool); clustered[100:110] = True
    spread = np.zeros(1000, dtype=bool); spread[::100] = True
    assert backtest.christoffersen(clustered) < 0.001
    assert backtest.christoffersen(spread) > 0.05


def test_backtest_var_uses_only_past_data():
    rng = np.random.default_rng(2)
    idx = pd.bdate_range("2015-01-01", periods=900)
    px = pd.DataFrame({"CL": 60 * np.exp(np.cumsum(rng.normal(0, 0.02, 900))),
                       "NG": 3 * np.exp(np.cumsum(rng.normal(0, 0.03, 900)))}, index=idx)
    book = {"CL": 10, "NG": -5}
    a = backtest.rolling(px, data.relative_returns(px), book, start=600)
    px2 = px.copy(); px2.iloc[800:] *= 1.5
    b = backtest.rolling(px2, data.relative_returns(px2), book, start=600)
    cut = idx[798]
    pd.testing.assert_frame_equal(a.loc[:cut].drop(columns="pnl"), b.loc[:cut].drop(columns="pnl"))

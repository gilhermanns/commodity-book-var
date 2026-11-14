"""Historical stress: put today's book through past episodes.

Each scenario applies the relative price move of every contract over the
episode to today's exposure. VaR says what a bad day looks like in the current
regime; this says what happens if the regime changes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

EPISODES = {
    "Lehman / GFC (15 Sep - 24 Dec 2008)": ("2008-09-12", "2008-12-24"),
    "Oil price war (26 Nov 2014 - 28 Jan 2015)": ("2014-11-26", "2015-01-28"),
    "Covid demand collapse (20 Feb - 31 Mar 2020)": ("2020-02-20", "2020-03-31"),
    "Ukraine invasion (23 Feb - 8 Mar 2022)": ("2022-02-23", "2022-03-08"),
    "Ukraine unwind (8 Mar - 16 Mar 2022)": ("2022-03-08", "2022-03-16"),
}


def replay(px: pd.DataFrame, expo: pd.Series) -> pd.DataFrame:
    rows = []
    for name, (a, b) in EPISODES.items():
        w = px.loc[a:b, expo.index]
        if len(w) < 2:
            continue
        move = w.iloc[-1] / w.iloc[0] - 1
        pnl = move * expo
        rows.append({"scenario": name, "book P&L $": pnl.sum(),
                     "worst position": pnl.idxmin(), "worst P&L $": pnl.min(),
                     "best position": pnl.idxmax(), "best P&L $": pnl.max()})
    return pd.DataFrame(rows)


def worst_windows(rets: pd.DataFrame, expo: pd.Series, days=(1, 5, 10)) -> pd.DataFrame:
    """Worst h-day stretch in the whole history for today's exposures."""
    daily = pd.Series(rets[expo.index].to_numpy() @ expo.to_numpy(), index=rets.index)
    rows = []
    for h in days:
        roll = daily.rolling(h).sum()
        end = roll.idxmin()
        rows.append({"horizon (days)": h, "worst loss $": -roll.min(), "ending": end.strftime("%Y-%m-%d"),
                     "99% loss $": -np.nanquantile(roll, 0.01),
                     "sqrt-time from 1-day 99% $": -np.nanquantile(daily, 0.01) * np.sqrt(h)})
    return pd.DataFrame(rows)

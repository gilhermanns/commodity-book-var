from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

from . import style

FIG_DIR = Path(__file__).resolve().parents[1] / "figures"
MONEY = FuncFormatter(lambda v, _: "0" if v == 0 else f"{v / 1e3:+,.0f}k")
MONEY_ABS = FuncFormatter(lambda v, _: "0" if v == 0 else f"{v / 1e3:,.0f}k")
MONEY_M = FuncFormatter(lambda v, _: "0" if v == 0 else f"{v / 1e6:+.1f}m")


def _save(fig, name):
    FIG_DIR.mkdir(exist_ok=True)
    fig.savefig(FIG_DIR / name)
    plt.close(fig)


def backtest(bt: pd.DataFrame, model: str = "filtered historical"):
    style.apply()
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.vlines(bt.index, 0, bt["pnl"], color=style.MUTED, lw=0.5, alpha=0.7, label="Daily P&L")
    ax.plot(-bt[model], color=style.SERIES[0], lw=1.3, label=f"99% VaR, {model}")
    hits = bt[bt["pnl"] < -bt[model]]
    ax.scatter(hits.index, hits["pnl"], s=22, color=style.BAD, zorder=4, label=f"Loss beyond VaR ({len(hits)})")
    ax.axhline(0, color=style.AXIS, lw=0.8)
    lo = min(bt["pnl"].quantile(0.0005), -bt[model].max()) * 1.15
    ax.set_ylim(lo, bt["pnl"].quantile(0.9995) * 1.15)
    ax.yaxis.set_major_formatter(MONEY)
    ax.set_title("Daily P&L of the book against the VaR computed the evening before ($)")
    ax.legend(loc="lower left", ncol=3)
    _save(fig, "backtest.png")


def var_models(bt: pd.DataFrame, start: str = "2019-06-01", end: str = "2021-06-30"):
    style.apply()
    fig, ax = plt.subplots(figsize=(11, 4))
    d = bt.loc[start:end]
    for i, m in enumerate(bt.columns[1:]):
        ax.plot(d[m], color=style.SERIES[i], lw=1.6, label=m)
    ax.yaxis.set_major_formatter(MONEY_ABS)
    ax.set_title("How fast each model reacts: 99% one-day VaR through 2020 ($)")
    ax.legend(loc="upper left")
    _save(fig, "var_models_2020.png")


def components(comp: pd.DataFrame):
    style.apply()
    c = comp.sort_values("component VaR $")
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    y = range(len(c))
    ax.barh([i + 0.2 for i in y], c["stand-alone VaR $"], height=0.36, color=style.GRID, label="Stand-alone VaR of the position")
    ax.barh([i - 0.2 for i in y], c["component VaR $"], height=0.36, color=style.SERIES[0], label="Contribution to book VaR")
    ax.axvline(0, color=style.AXIS, lw=0.8)
    ax.set_yticks(list(y)); ax.set_yticklabels(c.index)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(MONEY)
    ax.set_title("Where the risk sits: stand-alone vs contribution (99%, 1 day)", pad=26)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2)
    _save(fig, "components.png")


def stress(st: pd.DataFrame):
    style.apply()
    s = st.iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.barh(s["scenario"], s["book P&L $"], color=style.SERIES[0], height=0.6)
    for y, v in enumerate(s["book P&L $"]):
        ax.text(v, y, f"  {v / 1e6:+.2f}m  ", va="center", ha="left" if v >= 0 else "right", fontsize=9, color=style.INK2)
    ax.axvline(0, color=style.AXIS, lw=0.8)
    ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(MONEY_M)
    ax.margins(x=0.18)
    ax.set_title("Today's book through past episodes ($)")
    _save(fig, "stress.png")

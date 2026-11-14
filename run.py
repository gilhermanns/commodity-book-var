"""python run.py [book.json]  -> figures/ and results/latest.md"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from bookvar import backtest, data, plots, stress, var
from bookvar.book import CONTRACTS, load_book

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def md_table(df: pd.DataFrame, index: bool = False, fmt: str = "{:,.0f}", fmts: dict | None = None) -> str:
    if index:
        df = df.reset_index()
    fmts = fmts or {}
    def cell(c, v):
        if isinstance(v, (float, np.floating)):
            return "" if pd.isna(v) else fmts.get(c, fmt).format(v)
        return str(v)
    head = "| " + " | ".join(str(c) for c in df.columns) + " |"
    sep = "|" + "|".join("---" for _ in df.columns) + "|"
    rows = ["| " + " | ".join(cell(c, v) for c, v in zip(df.columns, r)) + " |" for r in df.itertuples(index=False)]
    return "\n".join([head, sep, *rows])


def main():
    RESULTS.mkdir(exist_ok=True)
    book = load_book(sys.argv[1] if len(sys.argv) > 1 else ROOT / "book.json")
    px = data.load_prices()
    rets = data.relative_returns(px)
    expo = data.exposures(px.iloc[-1], book)
    asof = px.index[-1]

    pos = pd.DataFrame({"contract": [CONTRACTS[k].name for k in book], "lots": list(book.values()),
                        "price": [px[k].iloc[-1] for k in book], "exposure $": expo.to_numpy()}, index=list(book))
    snap = var.snapshot(rets, expo)
    comp = var.component_var(rets[list(book)].to_numpy(), expo.to_numpy(), list(book))
    undiversified = comp["stand-alone VaR $"].sum()

    print("rolling backtest ...")
    bt = backtest.rolling(px, rets, book)
    score = backtest.scorecard(bt)
    years = backtest.by_year(bt)
    st = stress.replay(px, expo)
    ww = stress.worst_windows(rets, expo)
    worst = bt.assign(**{"loss / VaR (filtered)": -bt["pnl"] / bt["filtered historical"]}).nsmallest(5, "pnl")
    worst = worst[["pnl", "filtered historical", "loss / VaR (filtered)"]].rename(columns={"pnl": "P&L $", "filtered historical": "VaR $"})
    worst.index = worst.index.strftime("%Y-%m-%d"); worst.index.name = "date"

    plots.backtest(bt)
    plots.var_models(bt)
    plots.components(comp)
    plots.stress(st)
    bt.to_csv(RESULTS / "backtest.csv", float_format="%.0f")

    f2 = {"price": "{:,.2f}", "rate %": "{:.2f}", "Kupiec p": "{:.3f}", "independence p": "{:.3f}", "worst loss / VaR": "{:.1f}",
          "share of book VaR %": "{:.1f}", "expected": "{:.1f}", "loss / VaR (filtered)": "{:.1f}"}
    lines = [f"# Book risk report, {asof:%d %b %Y}", "",
             "## Positions", "", md_table(pos, index=True, fmts=f2).replace("| index |", "| |"), "",
             f"Gross exposure ${expo.abs().sum():,.0f}, net ${expo.sum():,.0f}.", "",
             "## One-day VaR and expected shortfall", "", md_table(snap), "",
             "## Risk by position (parametric, 99%)", "", md_table(comp, index=True, fmts=f2).replace("| index |", "| |"), "",
             f"Sum of stand-alone VaRs ${undiversified:,.0f}, book VaR ${comp['component VaR $'].sum():,.0f}: "
             f"diversification and the spread legs take off {(1 - comp['component VaR $'].sum() / undiversified) * 100:.0f}%.", "",
             f"## Backtest, {bt.index[0]:%b %Y} to {bt.index[-1]:%b %Y} (99%, one day)", "", md_table(score, fmts=f2), "",
             "Exceptions per year:", "", md_table(years, index=True), "",
             "Five worst days:", "", md_table(worst, index=True, fmts=f2), "",
             "## Historical stress on today's book", "", md_table(st), "",
             "## Multi-day losses (today's exposures, full history)", "", md_table(ww), ""]
    (RESULTS / "latest.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

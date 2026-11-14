"""Contract specs and the book.

`dollar_per_point` is what one contract makes when the quoted price moves by 1.0.
It folds in the contract size and the quoting unit, which is where futures P&L
calculations usually go wrong (corn is 5,000 bushels quoted in cents, so 1.0 = $50).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Contract:
    name: str
    ticker: str
    dollar_per_point: float
    unit: str


CONTRACTS = {
    "CL": Contract("WTI crude", "CL=F", 1_000, "$/bbl, 1,000 bbl"),
    "BZ": Contract("Brent crude", "BZ=F", 1_000, "$/bbl, 1,000 bbl"),
    "RB": Contract("RBOB gasoline", "RB=F", 42_000, "$/gal, 42,000 gal"),
    "HO": Contract("ULSD", "HO=F", 42_000, "$/gal, 42,000 gal"),
    "NG": Contract("Henry Hub gas", "NG=F", 10_000, "$/MMBtu, 10,000 MMBtu"),
    "HG": Contract("Copper", "HG=F", 25_000, "$/lb, 25,000 lb"),
    "GC": Contract("Gold", "GC=F", 100, "$/oz, 100 oz"),
    "ZC": Contract("Corn", "ZC=F", 50, "cents/bu, 5,000 bu"),
    "ZS": Contract("Soybeans", "ZS=F", 50, "cents/bu, 5,000 bu"),
    "KC": Contract("Arabica coffee", "KC=F", 375, "cents/lb, 37,500 lb"),
}


def load_book(path: str | Path) -> dict[str, float]:
    """{'CL': -45, 'RB': 20, ...} in contracts, long positive."""
    book = json.loads(Path(path).read_text())["positions"]
    unknown = set(book) - set(CONTRACTS)
    if unknown:
        raise KeyError(f"no contract spec for {sorted(unknown)}")
    return {k: float(v) for k, v in book.items() if v != 0}

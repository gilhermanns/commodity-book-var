# Book risk report, 13 Nov 2026

## Positions

| | contract | lots | price | exposure $ |
|---|---|---|---|---|
| CL | WTI crude | -45 | 88.56 | -3,985,200 |
| RB | RBOB gasoline | 20 | 2.62 | 2,201,976 |
| HO | ULSD | 10 | 4.26 | 1,788,570 |
| BZ | Brent crude | 15 | 95.84 | 1,437,600 |
| NG | Henry Hub gas | -20 | 3.23 | -646,000 |
| HG | Copper | 12 | 6.08 | 1,823,850 |
| ZC | Corn | 40 | 445.50 | 891,000 |
| KC | Arabica coffee | 8 | 278.65 | 835,950 |

Gross exposure $13,610,146, net $4,347,746.

## One-day VaR and expected shortfall

| confidence | model | 1-day VaR $ | expected shortfall $ |
|---|---|---|---|
| 95% | historical (500d) | 114,783 | 188,344 |
| 95% | parametric EWMA | 143,287 | 179,688 |
| 95% | filtered historical | 140,899 | 234,665 |
| 99% | historical (500d) | 255,504 | 327,268 |
| 99% | parametric EWMA | 202,654 | 232,174 |
| 99% | filtered historical | 308,310 | 353,160 |

## Risk by position (parametric, 99%)

| | exposure $ | stand-alone VaR $ | component VaR $ | share of book VaR % |
|---|---|---|---|---|
| CL | -3,985,200 | 287,593 | -61,576 | -30.4 |
| RB | 2,201,976 | 173,796 | 114,190 | 56.3 |
| HO | 1,788,570 | 124,622 | 66,276 | 32.7 |
| BZ | 1,437,600 | 118,740 | 57,734 | 28.5 |
| NG | -646,000 | 49,345 | 16,732 | 8.3 |
| HG | 1,823,850 | 61,258 | 1,135 | 0.6 |
| ZC | 891,000 | 24,571 | 17 | 0.0 |
| KC | 835,950 | 40,160 | 8,146 | 4.0 |

Sum of stand-alone VaRs $880,084, book VaR $202,654: diversification and the spread legs take off 77%.

## Backtest, Aug 2010 to Nov 2026 (99%, one day)

| model | days | exceptions | expected | rate % | Kupiec p | independence p | worst loss / VaR | avg VaR $ |
|---|---|---|---|---|---|---|---|---|
| historical (500d) | 4095 | 55 | 41.0 | 1.34 | 0.036 | 0.218 | 9.5 | 171,166 |
| parametric EWMA | 4095 | 88 | 41.0 | 2.15 | 0.000 | 0.936 | 4.7 | 133,254 |
| filtered historical | 4095 | 47 | 41.0 | 1.15 | 0.353 | 0.120 | 2.9 | 162,891 |

Exceptions per year:

| year | days | historical (500d) | parametric EWMA | filtered historical |
|---|---|---|---|---|
| 2010 | 103 | 0 | 2 | 0 |
| 2011 | 252 | 3 | 3 | 4 |
| 2012 | 250 | 3 | 4 | 2 |
| 2013 | 252 | 1 | 7 | 4 |
| 2014 | 252 | 2 | 6 | 1 |
| 2015 | 252 | 11 | 7 | 4 |
| 2016 | 250 | 2 | 3 | 0 |
| 2017 | 251 | 1 | 3 | 2 |
| 2018 | 251 | 7 | 9 | 8 |
| 2019 | 252 | 3 | 5 | 1 |
| 2020 | 253 | 5 | 8 | 5 |
| 2021 | 252 | 0 | 4 | 3 |
| 2022 | 251 | 3 | 8 | 2 |
| 2023 | 251 | 0 | 3 | 2 |
| 2024 | 252 | 1 | 6 | 2 |
| 2025 | 252 | 3 | 3 | 2 |
| 2026 | 219 | 10 | 7 | 5 |

Five worst days:

| date | P&L $ | VaR $ | loss / VaR (filtered) |
|---|---|---|---|
| 2020-04-21 | -2,459,348 | 842,093 | 2.9 |
| 2022-08-01 | -476,924 | 370,813 | 1.3 |
| 2026-04-01 | -416,178 | 399,998 | 1.0 |
| 2022-01-27 | -405,486 | 193,014 | 2.1 |
| 2022-03-09 | -403,402 | 470,513 | 0.9 |

## Historical stress on today's book

| scenario | book P&L $ | worst position | worst P&L $ | best position | best P&L $ |
|---|---|---|---|---|---|
| Lehman / GFC (15 Sep - 24 Dec 2008) | -2,334,279 | RB | -1,571,738 | CL | 2,592,861 |
| Oil price war (26 Nov 2014 - 28 Jan 2015) | -450,029 | RB | -746,687 | CL | 1,581,317 |
| Covid demand collapse (20 Feb - 31 Mar 2020) | -702,561 | RB | -1,446,048 | CL | 2,467,593 |
| Ukraine invasion (23 Feb - 8 Mar 2022) | 1,030,831 | CL | -1,367,343 | HO | 1,016,612 |
| Ukraine unwind (8 Mar - 16 Mar 2022) | -527,137 | HO | -538,994 | CL | 923,329 |

## Multi-day losses (today's exposures, full history)

| horizon (days) | worst loss $ | ending | 99% loss $ | sqrt-time from 1-day 99% $ |
|---|---|---|---|---|
| 1 | 1,043,292 | 2008-12-22 | 234,529 | 234,529 |
| 5 | 1,298,770 | 2008-12-29 | 500,560 | 524,423 |
| 10 | 1,851,523 | 2020-03-23 | 668,660 | 741,646 |

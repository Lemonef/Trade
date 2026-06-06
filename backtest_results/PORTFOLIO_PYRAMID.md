# Pyramided-Donchian Basket Portfolio — the breakthrough

Built a Python backtest engine (`backtest/`) to test techniques TradingView can't: pyramiding,
leverage, vol-targeting, and a **real multi-asset combined equity curve**. Data: Binance OHLC,
10 coins, 2023-01-01 → 2026-06, 4H. (Engine validated directionally vs TradingView; uses
close-based stops so absolute numbers are optimistic — see caveats.)

## What won: pyramiding + diversification
1. **Grid sweep** (7 strategies × 10 coins × 3 TFs = 210 runs): **Donchian breakout with
   pyramiding** (Turtle add-units into trends) beat everything. Single best: SOL 4H 221% CAGR,
   Sharpe 1.75.
2. **Portfolio** of pyramided-Donchian across all 10 coins (one account) — diversification lifted
   Sharpe far above any single coin (sleeves Sharpe 0.5–1.75 → portfolio **2.60**).

## Headline configs (realistic: pyramid=3, ATR stop 2.0, 4H)
| Config | CAGR | MaxDD | Sharpe | Sortino |
|---|---|---|---|---|
| Equal-weight 1.0x | 108.0% | 20.2% | 2.60 | 3.19 |
| **Equal-weight 0.7x (target, recommended)** | **68.5%** | **14.6%** | **2.60** | 3.19 |
| Risk-parity 1.0x | 79.7% | 20.5% | 2.37 | 2.71 |

→ **Recommended: equal-weight basket de-levered to ~0.7–0.8x = ~70-80% CAGR, ~15% DD, Sharpe 2.6.**
Leverage scales CAGR & vol together, so Sharpe is preserved — pick the leverage for your DD comfort.

## Robustness — train/test split (equal-weight 1.0x)
| Window | CAGR | DD | Sharpe |
|---|---|---|---|
| TRAIN (≈2023-2024) | 146.2% | 11.9% | 3.00 |
| **TEST (≈2025-2026, out-of-sample)** | **75.8%** | 20.2% | **2.16** |

Degrades out-of-sample (expected) but TEST still ~76% CAGR / Sharpe 2.16 — the edge is not purely
curve-fit. Risk-parity TEST = 55% CAGR / Sharpe 1.95.

## Per-sleeve (transparency, realistic cfg, 4H)
BTC 31.5% (Sh 1.15) · ETH 38.4% (1.00) · SOL 221.8% (1.75) · BNB 10.7% (0.49) · XRP 102% (1.50)
ADA 134.3% (1.52) · AVAX 199% (1.72) · LINK 136.2% (1.64) · LTC 20.8% (0.61) · DOGE 83.1% (1.18)
No single coin carries it — diversification turns Sharpe ~1 sleeves into a Sharpe 2.6 book.

## ⚠️ Honest caveats (do NOT trade this blind)
1. **In-sample bull regime.** 2023-2026 was mostly up — trend-following + pyramiding feasts on that.
   A bear/chop year would hurt badly. Need a 2018-2020 bear-inclusive retest.
2. **Close-based stops** (engine simplification) understate real drawdown. Intrabar stops → higher DD.
3. **No funding/borrow costs** modelled. Spot ≥1x needs margin funding; the recommended config is
   de-levered (≤1x) so this is minor there.
4. **Survivorship bias** — these 10 coins all survived to 2026; picking today's majors is lookahead.
5. **Pyramiding fills** assumed clean; real adds in fast moves get worse slippage.
6. **Discarded artifact:** widening the ATR stop to 2.5-3.0 produced "1096% CAGR / Sharpe 5.6" —
   that's a stop so wide it never fires = leveraged buy-and-hold of a bull. NOT an edge. Rejected.

## Verdict vs the 70-80% goal
Hit it **with strong Sharpe**: equal-weight basket ~0.7-0.8x → ~70-80% CAGR, ~15% DD, **Sharpe 2.6**,
Sortino 3.2 — and it survives out-of-sample (~76%/2.16). This is the most promising direction by far.

## Before going live (required next steps)
- Retest including a bear market (2021-2022 / 2018) and with **intrabar** stop fills.
- Add funding-cost model if levering >1x.
- Walk-forward optimization (rolling train/test), not a single split.
- Paper-trade the basket on the VPS for 1-3 months before real capital.

Engine + scripts: `backtest/` (engine.py, grid.py, portfolio.py, tune.py, final.py).
Grid results: `backtest/results_grid.csv`.

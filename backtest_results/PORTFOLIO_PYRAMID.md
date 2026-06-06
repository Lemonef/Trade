# Pyramided-Donchian Basket — CORRECTED report (a bug was found)

> **Important honesty note.** An earlier version of this report claimed ~108% CAGR / Sharpe 2.6.
> **That was a bug.** The pyramiding code added units while deducting only fees, not the purchase
> cost — i.e. free leverage. After fixing it (`engine.py`, commit notes), the real numbers are far
> more modest and the strategy is **regime-dependent (bull-market beta), not a Sharpe-2.6 machine.**
> Keeping this writeup as the corrected record.

## What it actually is
Long-only Donchian breakout (20-high / 10-low, ADX filter, ATR stop 2.0, ATR risk sizing, optional
pyramiding) run as an equal-weight basket of 10 Binance coins, 4H. Built + tested in `backtest/`.

## Honest results (fixed engine)
### In-sample-ish 2023-01 → 2026-06
| Config | CAGR | MaxDD | Sharpe | Sortino |
|---|---|---|---|---|
| Equal-weight 1.0x | 5.56% | 33.8% | 0.35 | 0.31 |
| Risk-parity 1.0x | 6.48% | 31.7% | 0.40 | 0.35 |

Leverage does NOT help (Sharpe flat ~0.4; CAGR plateaus then DD-drag wins).

### Robustness — it decays out-of-sample
| Window | CAGR | DD | Sharpe |
|---|---|---|---|
| TRAIN 2023-2024 | 14.4% | 24.7% | 0.70 |
| **TEST 2025-2026 (OOS)** | **−2.6%** | 33.8% | **0.00** |

Worked in the 2023-24 recovery, **stopped working in 2025-26**. Regime decay / selection overfit
(the config was the best of a 210-run grid search — survivorship of the search, not a stable edge).

### Bear-market OOS — 2021-2022 (untouched period, params not fit here)
| Window | CAGR | DD | Sharpe |
|---|---|---|---|
| 2021 (bull top) | +147.9% | 18.4% | 2.57 |
| **2022 (the crash)** | **−19.1%** | 27.1% | **−0.90** |
| full 2021-2022 | +41.3% | 35.7% | 1.27 |

Verdict: it **feasts in bull markets, bleeds in bears.** 2022 every sleeve was negative except DOGE.

## Per-sleeve 2023-26 (only BTC/XRP have real signal)
BTC 22.4% (Sh 0.95) · XRP 24.9% (0.75) · AVAX 11.5% (0.46) · ETH 9.5% (0.46) · LINK 6.3% (0.35)
ADA 3.2% (0.28) · BNB 2.8% (0.23) · SOL −10.2% (−0.02) · DOGE −22.4% (−0.38) · LTC −25.3% (−0.63)

## Honest conclusion
- The 70-80% CAGR / Sharpe 2.6 "breakthrough" was a **software bug**, now fixed.
- The real strategy = **long-only crypto trend beta**: ~6% CAGR / Sharpe 0.4 over 2023-26, positive
  in bull regimes, negative in bear/chop. It does NOT hit the targets and is NOT robust as-is.
- The only consistently positive standalone sleeve is **BTC trend-following (Sharpe ~0.95)**.

## What would actually move the needle (honest next steps)
1. **Market/regime filter** — only trade when BTC is above its 200-day MA (skip bears). Should cut
   the 2022/2025 bleed. Test if it lifts full-period Sharpe.
2. **Add shorts** for bear regimes (we proved long-only = bull beta) — but shorts hurt in the
   earlier TradingView sweep, so test carefully.
3. **Concentrate on BTC** (the only stable sleeve) rather than diluting with weak alts.
4. **Walk-forward** (rolling re-fit) instead of one grid pick, to measure true OOS expectancy.
5. Re-introduce **intrabar stops** and **funding costs** for realism (current = close-based stops).

Lesson logged: always sanity-check a "too good" backtest (+1000% CAGR / Sharpe >3 in crypto = bug
until proven otherwise). Found here only because the 2022 bear retest showed +505% on a coin that
fell 90% — physically impossible, which exposed the accounting error.

# Donchian Breakout V1 — Backtest Report

**Strategy:** Donchian Breakout V1 (Long Only)
**Market:** BINANCE:SOLUSDT
**Timeframe:** 4H
**Period:** 2023-01-01 → 2026-06-06 (~3.43 yr)
**Engine:** TradingView Strategy Tester (Pine v5)
**Date run:** 2026-06-07
**Screenshot:** [donchian_v1_sol4h_2023.png](donchian_v1_sol4h_2023.png)

## Settings
| Param | Value |
|---|---|
| Entry Period (high breakout) | 20 |
| Exit Period (low breakdown) | 10 |
| ADX filter | on, threshold 20, len 14 |
| ATR expansion filter | on |
| Risk % per trade | 5.0 |
| ATR stop multiplier | 2.0 |
| Initial capital | 10,000 USDT |
| Commission | 0.1% | 
| Slippage | 2 ticks |

## Results
| Metric | Value | Target | Pass |
|---|---|---|---|
| CAGR | **7.45%** | 30%+ | ❌ |
| Win rate | 38.16% (29/76) | 55%+ | ❌ |
| Profit factor | **1.095** | 2.0+ | ❌ |
| Max drawdown (equity) | 45.35% | <20% | ❌ |
| Net P&L | +2,797.96 USDT (+27.98%) | — | — |
| Total trades | 76 | — | — |
| Max DD % of initial capital | 104.46% | — | ⚠ leverage |

## Verdict — ❌ FAIL all targets
- PF 1.095 = near breakeven after costs. Not tradeable.
- WR 38% + DD 45% = unacceptable risk profile.
- CAGR 7.45% vs **QB V1 SOL 4H = 23.63%** (PF 2.3, DD 20.7%). Donchian loses badly.
- Donchian default params (20/10, ADX 20, ATR 2.0) dead on SOL 4H.

## Bug fixed before test (was invalidating exits)
Original code: `longBreakdown = close < lowestLow` where `lowestLow` included current
bar → `lowestLow <= close` always → exit by breakdown could **never** fire (ATR stop
only). Fixed to `close < lowestLow[1]` (prior bar's channel). Same fix on short side
(`close > shortHighest[1]`). Without fix, "hold full trend, exit on M-low breakdown"
thesis was broken.

## Comparison vs current best
| Strategy | Market | CAGR | WR | PF | DD |
|---|---|---|---|---|---|
| QB V1 (best) | SOL 4H | 23.63% | 59.38% | 2.30 | 20.74% |
| Donchian V1 | SOL 4H | 7.45% | 38.16% | 1.095 | 45.35% |

## Next options
1. **Param sweep** Donchian: Entry 55/Exit 20 (Turtle slow), ADX off, ATR 2.5/3.0 — classic Donchian often needs wider channels. Low expectation it beats QB V1.
2. **Drop Donchian**, return to optimizing QB V1 (ceiling ~23% CAGR) — try different exit logic or add Donchian-style trailing to QB V1's trend leg.
3. Test Donchian on a stronger trender (BTC) before abandoning.

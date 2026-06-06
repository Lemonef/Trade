# Donchian Breakout V1

Strategy 4 — pure price breakout. Buy above N-period high, hold the trend, exit on prior
M-period low breakdown + ATR stop. Back to [[index]] · [[CLAUDE]]. Pine: `DONCHIAN_V1.pine`.

## Logic
- Entry: close > prior `entryPeriod`(20) high, gated by ADX>20 + ATR-expansion.
- Exit: close < **prior** `exitPeriod`(10) low (`lowestLow[1]`) OR ATR stop (2.0×).
- Bug fixed: original used current-bar `lowestLow` → exit could never fire. Now `[1]`.

## Sweep results (4H, 2023→2026) — see [[SWEEP_2023_4H]] and [[DONCHIAN_V1_SOL4H_2023]]
| Market | CAGR | WR | PF | DD |
|---|---|---|---|---|
| BTC | 24.77% | 33.80% | 1.48 | 26.09% |
| ETH | 23.26% | 32.76% | 1.552 | 21.63% |
| SOL | 7.45% | 38.16% | 1.095 | 45.35% |
| XAU | 1.01% | 37.29% | 1.09 | 9.62% |

## Verdict
Research claim (beats B&H on trending crypto) holds for **BTC/ETH** (CAGR ~24%, PF ~1.5) but
**fails on SOL/XAU**. Low WR (trend follower). PF still modest, DD high on crypto.
Trend camp with [[trend-meter]]; opposite of [[quant-blend]] / [[momentum-reversion]].
Next: try Turtle-slow params (Entry 55 / Exit 20) on BTC/ETH.

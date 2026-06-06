# Momentum Reversion (MR)

Strategy 2 — RSI pullback mean-reversion + momentum/volatility filters. Back to [[index]] · [[CLAUDE]].
Pine: `MR_V2.pine` ("UNLEASHED"). **V1 removed** — over-filtered (volume + RSI-70 exit gates →
~13-17 trades, near-flat). Its only lesson (removing those gates) is baked into V2.

## V2 design
Dropped RSI-70 exit + volume filter, wider pullback zones, 5% risk. More trades, real returns.
**Removing the RSI-70 exit + volume filter was the single biggest improvement in the whole project.**

## Sweep results (4H, 2023→2026) — see [[SWEEP_2023_4H]]
| Market | CAGR | WR | PF | DD |
|---|---|---|---|---|
| BTC | 11.12% | 58.33% | 1.99 | 18.17% |
| SOL | 10.86% | 50.00% | 1.866 | 15.49% |
| ETH | 8.20% | 40.74% | 1.519 | 19.31% |
| XAU | 1.70% | 58.33% | 2.464 | 3.33% |

## Verdict
Balanced ~8-11% CAGR, controlled DD. Mean-reversion camp with [[quant-blend]] (both like SOL/XAU).
Doesn't hit 30% target on defaults — candidate to fold into a regime router.

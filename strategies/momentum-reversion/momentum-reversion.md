# Momentum Reversion (MR)

Strategy 2 — RSI pullback mean-reversion + momentum/volatility filters. Back to [[index]] · [[CLAUDE]].
Pine: `MR_V1.pine` (over-filtered), `MR_V2.pine` ("UNLEASHED").

## V1 vs V2
- **V1**: bias + momentum + RSI pullback zone + RSI cross 50 + volatility + **volume** filter.
  Too many gates → ~13-17 trades, near-flat. Removed in V2.
- **V2**: dropped RSI-70 exit + volume filter, wider zones, 5% risk. More trades, real returns.

## Sweep results (4H, 2023→2026) — see [[SWEEP_2023_4H]]
| Ver | Market | CAGR | WR | PF | DD |
|---|---|---|---|---|---|
| V1 | BTC | 3.82% | 61.54% | 2.788 | 5.12% |
| V1 | SOL | 1.64% | 53.33% | 1.444 | 7.19% |
| V1 | ETH | 0.35% | 47.06% | 1.093 | 7.19% |
| V1 | XAU | — | 0 trades | — | — |
| V2 | BTC | 11.12% | 58.33% | 1.99 | 18.17% |
| V2 | SOL | 10.86% | 50.00% | 1.866 | 15.49% |
| V2 | ETH | 8.20% | 40.74% | 1.519 | 19.31% |
| V2 | XAU | 1.70% | 58.33% | 2.464 | 3.33% |

## Verdict
**Lesson confirmed: removing RSI70 exit + volume filter (V1→V2) is the biggest single win.**
V1 = excellent PF but too few trades → flat. V2 = balanced ~8-11% CAGR, controlled DD.
Mean-reversion camp with [[quant-blend]] (both like SOL/XAU). Neither hits 30% target on defaults.

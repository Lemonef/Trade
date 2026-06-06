# Quant Blend V1 (QB)

Strategy 3 — regime-aware. ADX decides trending vs ranging, then runs the right engine.
Prior "current best". Back to [[index]] · [[CLAUDE]]. Pine: `QB_V1.pine`.

## Logic
- **ADX > 25 → trending**: Supertrend + RSI momentum entries.
- **ADX < 20 → ranging**: Bollinger Band mean-reversion entries.
- Tuned "best" settings: Risk 5.0, ATR stop 2.5, ADX trend 25 / range 20.

## Sweep results (4H, 2023→2026, **file-default** sizing) — see [[SWEEP_2023_4H]]
| Market | CAGR | WR | PF | DD |
|---|---|---|---|---|
| SOL | 11.55% | 59.38% | 2.78 | 5.23% |
| XAU | 4.73% | 52.63% | 3.084 | 3.76% |
| BTC | −1.46% | 45.45% | 0.737 | 10.85% |
| ETH | −0.42% | 40.00% | 0.898 | 10.68% |

## Notes
- Default-sizing run is conservative (qty 10% equity). Tuned **Risk 5 / ATR 2.5** → SOL CAGR ~23.63%
  (same signals — WR 59.38% identical — bigger positions, DD rises to ~20%).
- **Best quality of the whole sweep**: SOL PF 2.78 / DD 5.2%, XAU PF 3.08 / DD 3.8%.
- Mean-reversion camp with [[momentum-reversion]]; opposite of trend camp [[trend-meter]] / [[donchian-breakout]].
- Ceiling ~23% CAGR (pyramid + daily TF didn't help). Next: graft trend-leg trailing or route by asset.

## V2 Hybrid (`QB_V2_hybrid.pine`) — Donchian trend leg
Swapped the weak Supertrend trend leg for a **Donchian breakout** (keeps Bollinger range leg).
Result: flipped the camp — now wins **BTC 4H (CAGR 27.81%, PF 1.59)** and ETH (+18.69%), but
**broke SOL** (−5.91%). 1D smooths it (BTC PF 2.50 / DD 9%, SOL +13.42%). Full report:
[[QB_V2_HYBRID]]. Best deployment: **Hybrid on BTC/ETH, V1 on SOL/XAU** (portfolio).

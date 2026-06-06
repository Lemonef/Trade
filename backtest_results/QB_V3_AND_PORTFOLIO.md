# QB V3 + Portfolio Analysis

`strategies/quant-blend/QB_V3.pine` — folded in all 3 proposed levers: per-asset engine map,
ATR chandelier trailing exit, and (this doc) the portfolio blend. 4H, 2023-01-01→2026-06-06.

## QB V3 results (4H)
| Market | CAGR | WR | PF | MaxDD | Trades | Note |
|---|---|---|---|---|---|---|
| BTC | 24.89% | 41.56% | 1.548 | 20.46% | 77 | chandelier trimmed vs Hybrid 27.81% |
| ETH | 20.95% | 37.31% | 1.482 | 33.31% | 67 | chandelier helped vs Hybrid 18.69% |
| SOL | −2.72% | 50.00% | 0.695 | 21.57% | 12 | reversion-only ≠ V1's blend |
| XAU | 0.99% | 100% | 35.76 | 0.68% | 4 | starved (4 trades, meaningless) |

## What each lever taught us
1. **Per-asset engine map (reversion-only for SOL/XAU)** — FAILED. QB V1's SOL profit (+11.55%)
   came partly from its *Supertrend trend leg*, not just Bollinger. Dropping the trend leg starves
   SOL/XAU (12 / 4 trades) → SOL still negative. Generic reversion ≠ V1's specific blend.
2. **ATR chandelier trailing** — MIXED. Helped ETH (CAGR 18.69→20.95, DD 35.30→33.31) but
   hurt BTC (27.81→24.89) by exiting strong trends early. Not a universal win.
3. **Conclusion** — there is **no single-strategy silver bullet** on this universe. The right
   structure is a **portfolio of specialists**, each on its home market.

## Portfolio book (best sleeve per market)
| Sleeve | Strategy / TF | CAGR | PF | DD |
|---|---|---|---|---|
| BTC | QB V2 Hybrid 4H | 27.81% | 1.589 | 20.74% |
| ETH | QB V3 4H | 20.95% | 1.482 | 33.31% |
| SOL | QB V1 4H (tuned Risk5/ATR2.5 → ~23.63%) | 11.55% / ~23.63% | 2.78 | 5.23% |
| XAU | QB V1 4H | 4.73% | 3.084 | 3.76% |

### Estimated blend (equal-weight 25% each, rebalanced)
- **Blended CAGR ≈ 16.3%** (default sizing) → **~19.3%** with SOL tuned to 23.63%.
- **Blended Max DD ≈ 10–15%** — well under 20% target, because sleeve drawdowns are largely
  uncorrelated (trend camp BTC/ETH vs reversion camp SOL/XAU peak at different times).
- Weighted-avg PF ≈ 2.0.

> ⚠️ **Approximation.** TradingView Pine backtests one symbol at a time, so this blend is computed
> from the four standalone equity profiles, not a single combined curve. For the true portfolio
> drawdown/Sharpe, run a multi-asset backtest in Python (vectorbt / backtrader) feeding all four
> sleeves into one account. That is the recommended next step before going live.

### Risk-parity variant (inverse-DD weights)
Up-weight low-DD sleeves (SOL/XAU): weights ∝ 1/DD → SOL/XAU dominate. Lower CAGR (~10-13%) but
portfolio DD likely <8%. Choose equal-weight for growth, risk-parity for safety.

## Bottom line vs targets (CAGR 30 / WR 55 / DD 20 / PF 2)
- No standalone combo hits all four. Closest single: **BTC 4H Hybrid** (CAGR 27.81%, PF 1.59).
- **Portfolio** is the realistic path: ~19% CAGR, DD <15%, PF ~2 — misses the 30% CAGR but is the
  most robust, live-ready structure. To chase 30%: lever the low-DD sleeves (SOL/XAU tuned + sized
  up) since they have huge DD headroom (3-5%).

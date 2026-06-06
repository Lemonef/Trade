# QB V2 Hybrid — Backtest Report

**Strategy:** Quant Blend V2 Hybrid (`strategies/quant-blend/QB_V2_hybrid.pine`)
**Idea:** keep QB's ADX regime switch, but swap the weak trend leg (Supertrend+RSI) for a
**Donchian breakout**. Ranging leg = Bollinger+RSI reversion. Long only. ATR risk 5% / stop 2.5×.
**Period:** 2023-01-01 → 2026-06-06. Engine: TradingView Strategy Tester (DEEP).
**Date run:** 2026-06-07.

## Results
| TF | Market | CAGR | WR | PF | MaxDD | Net | vs QB V1 |
|---|---|---|---|---|---|---|---|
| 4H | **BTC** | **27.81%** | 44.59% | 1.589 | 20.74% | +132.13% | −1.46% → +27.81% ✅✅ |
| 4H | ETH | 18.69% | 36.36% | 1.394 | 35.30% | +80.04% | −0.42% → +18.69% ✅ |
| 4H | SOL | −5.91% | 34.88% | 0.923 | 51.82% | −18.85% | +11.55% → −5.91% ❌ |
| 4H | XAU | 2.88% | 46.55% | 1.259 | 6.52% | +10.20% | +4.73% → +2.88% ↓ |
| 1D | BTC | 9.27% | 50.00% | **2.497** | 9.18% | +35.53% | (12 trades) |
| 1D | SOL | 13.42% | 33.33% | 2.138 | 22.14% | +54.02% | (9 trades) |
| 1D | ETH | 1.75% | 45.45% | 1.268 | 12.29% | +6.13% | (11 trades) |

Targets: CAGR 30%+ / WR 55%+ / DD <20% / PF 2.0+.

## Verdict — partial win, it FLIPPED the camp
- Donchian trend leg turned **BTC/ETH from losers into winners** (BTC 4H +27.81%, near target).
- But it **broke SOL** (−5.91%) — Donchian breakouts on SOL's choppy 4H trends are bad, and it
  cannibalised QB V1's good SOL Bollinger edge by routing high-ADX SOL bars to Donchian.
- Net effect: QB V2 Hybrid is now a **BTC/ETH** strategy, the mirror of QB V1 (SOL/XAU).

## Timeframe finding (you were right to check)
- **4H** = higher CAGR, higher DD (more trades, more compounding). Best for BTC CAGR.
- **1D** = much better quality (BTC PF 2.50 / DD 9.2%; SOL PF 2.14) but low CAGR (few trades).
- 1D *un-breaks* SOL (+13.42% vs −5.91%) — Daily removes the chop. But 9 trades = thin sample.

## No single (market, TF) hits all 4 targets
- Closest on CAGR: **BTC 4H** (27.81%) — misses WR (44.6) and PF (1.59).
- Closest on quality: **BTC 1D** (PF 2.50, DD 9.2%, WR 50) — CAGR only 9.27%.

## Recommended deployment (portfolio)
- **BTC (+ETH) → QB V2 Hybrid 4H** (trend camp, ~28% CAGR on BTC).
- **SOL / XAU → keep QB V1** (reversion camp, PF 2.8–3.1, tiny DD).
- Two uncorrelated camps → blended book, smoother equity, closer to the 30% goal via
  diversification rather than one heroic strategy. See [[index]] meta-strategy note.

## Next tuning ideas
- Per-asset engine map (don't route SOL's trend bars to Donchian — keep Bollinger on SOL).
- Donchian Turtle-slow (55/20) inside the trend leg for BTC/ETH.
- Add ATR trailing exit to the trend leg to cut BTC 4H DD below 20%.

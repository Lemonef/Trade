# Leverage choice — PyrDon (Donchian 55/20 + MA200) on BTC 4H, TradingView, 2023-2026

Tested live on TradingView via the `leverage` input (1/2/3×). Single-coin BTC (basket would smooth DD).

| Leverage | CAGR | Max DD | Profit Factor | Net P&L | Note |
|---|---|---|---|---|---|
| **1×** | 24.5% | 19.0% | **2.01** | +112% | best risk-adjusted; hits original targets (PF>2, DD<20) |
| **2×** | 46.0% | 35.7% | 1.64 | +266% | ≈ half-Kelly; aggressive but PF healthy — **recommended** |
| **3×** | 63.9% | 50.3% | 1.42 | +445% | near 70-80% goal but PF thinning, 50% DD |

## Key facts
- **Leverage is not free here:** PF degrades 2.01 → 1.64 → 1.42 as leverage rises (bigger positions
  hit the ATR stop harder; compounding path changes). DD scales ~linearly (19 → 36 → 50%).
- This is single-coin BTC. The **~20-coin basket** would cut DD meaningfully at each leverage (the
  Python basket OOS DD was ~18% at 1×).
- Sizing rule of thumb: for a Sharpe ~0.9 system, **half-Kelly ≈ 2×** is the disciplined aggressive
  level. Full-Kelly (~3×+) maximises growth but courts deep drawdowns / ruin risk.

## Recommendation
- **Safe:** 1× (24% CAGR, 19% DD, PF 2.0).
- **Aggressive sweet spot:** 2× (46% CAGR, 36% DD, PF 1.64).
- **Max-risk:** 3× (64% CAGR, 50% DD) — only with true tolerance for a halving of equity.

Pine: `strategies/donchian-breakout/PYRAMID_DONCHIAN.pine` — set the **Leverage** input (1/2/3×).
Screenshot (3×): `backtest_results/pyrdon_leverage_3x.png`.

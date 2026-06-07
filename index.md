# 🗿 Quant — Trading Bot Vault

Home / Map of Content. Owner: **Zen** (19, Thai uni). Capital ~$2,800. Goal: 20M Baht by early 30s.
Fully automated. See [[CLAUDE]] for full project spec + backtest workflow.

## Strategies
- [[trend-meter]] — EMA 13/21/34/55 + Stoch RSI trend follower (Long-only & Long+Short)
- [[momentum-reversion]] — RSI pullback mean-reversion (V1 over-filtered, V2 unleashed)
- [[quant-blend]] — ADX regime switch: Supertrend trend + Bollinger reversion ← prior best
- [[donchian-breakout]] — N-high breakout, hold trend, exit prior M-low

## Results
- [[SWEEP_2023_4H]] — full 5-strategy × 4-market sweep (4H, 2023→2026) **← main table**
- [[DONCHIAN_V1_SOL4H_2023]] — first Donchian deep-dive report

## TL;DR rankings (4H, 2023-26, default params)
| Rank | Combo | CAGR | PF | DD |
|---|---|---|---|---|
| Highest CAGR | [[trend-meter\|TM-LO]] / SOL | 48.84% | 1.45 | 36% |
| Best trend pick | [[donchian-breakout\|Donchian]] / BTC | 24.77% | 1.48 | 26% |
| Best quality | [[quant-blend\|QB V1]] / XAU | 4.73% | 3.08 | 3.8% |
| Best balance | [[quant-blend\|QB V1]] / SOL | 11.55% | 2.78 | 5.2% |

## Core insight
**Two camps, opposite markets:**
- Mean-reversion ([[quant-blend]], [[momentum-reversion]]) → win **SOL / XAU**, lose BTC/ETH.
- Trend-following ([[trend-meter]], [[donchian-breakout]]) → win **BTC / ETH**, lose SOL/XAU.

→ A market-aware meta-strategy (route by regime/asset) is the obvious next experiment.

## Infra
- TradingView (paper) · MT5 Exness demo · GitHub Actions (cloud bot)

# Quant — Trading Bot Project

Automated trading strategy R&D. Owner: Zen (19, Thai uni student). Capital ~$2,800
(100k Baht). Goal: 20M Baht by early 30s. Fully automated only. High risk tolerance.

## Infrastructure (live)
- **TradingView** paper trading: Gold 1D + SOL 1D (Trend Meter Long Only). Account: sudha_sutaschuto.
- **MT5 Demo**: Exness #413853078, XAUUSD D1, EA running.
- **Azure VPS**: 52.184.100.141, Win Server 2022, free ~Dec 2026 (GitHub Student credits).
- Languages: Pine Script v5 + MQL5.

## Files (folder per strategy; all Pine v5, mq5 removed)
| File | What |
|---|---|
| `strategies/trend-meter/TM_LongOnly.pine` | Strategy 1 — Trend Meter long-only (EMA 13/21/34/55 + Stoch RSI). |
| `strategies/trend-meter/TM_LongShort.pine` | Strategy 1 — Trend Meter long+short (exit on band flip). |
| `strategies/momentum-reversion/MR_V1.pine` | Strategy 2 V1 — RSI pullback + ROC + Volume + ATR (over-filtered). |
| `strategies/momentum-reversion/MR_V2.pine` | Strategy 2 V2 — no RSI70 exit, no volume filter, wider zones, 5% risk. |
| `strategies/quant-blend/QB_V1.pine` | Strategy 3 — ADX regime + Supertrend + RSI + Bollinger. |
| `strategies/donchian-breakout/DONCHIAN_V1.pine` | Strategy 4 — pure breakout, hold trend, exit on prior M-low. |
| `backtest_results/SWEEP_2023_4H.md` | Full 5-strategy × 4-market sweep (2023-26). |
| `backtest_results/` | Reports + (deleted) scratch screenshots. |

## Current best — QB V1 on SOL 4H
CAGR 23.63%, WR 59.38%, PF 2.3, DD 20.74%. Settings: Risk 5.0, ATR stop 2.5, ADX trend 25, ADX range 20.
Hitting ceiling ~23% CAGR (pyramid + daily TF didn't help).

## Target for any new strategy
CAGR 30%+, WR 55%+, DD <20%, PF 2.0+.

## Key lessons
- Removing RSI 70 exit = biggest single win (V1→V2 ETH).
- ADX regime detection fixed Gold DD (32% → 3.76%).
- Volume filter kills too many good trades — remove.
- ADX 25 is the sweet spot (lower = worse).
- Wider ATR stop (2.5x) > tighter.
- **Best market: SOL 4H** (momentum + clear trends).
- Dead markets: ETH, EURUSD, Nasdaq, Gold. EURUSD totally incompatible (7% WR).

## Backtest workflow (TradingView via agent-browser) — Account: sudha_sutaschuto
1. Browser **headed** (`--headed --profile "Profile 2"`) so Zen sees it. Google OAuth is blocked
   on automation Chrome → log in with TradingView **Email**, not "Continue with Google".
2. Pine Editor → paste code via clipboard (`Set-Clipboard` + click editor, Ctrl+A, Delete, Ctrl+V).
   The compile button is the **unlabeled icon button just left of "Publish script"**.
3. **Collapse multi-line boolean expressions to ONE line before pasting.** Pine implicit
   line-continuation (`x = a and \n  b and \n  c`) breaks in Monaco paste → "end of line without
   line continuation". Function-arg continuations inside `(...)` are safe. (MR V1, QB V1 needed this.)
4. Set symbol via symbol button → search `BINANCE:BTCUSDT` etc. (`OANDA:XAUUSD` for gold).
5. Date range: Strategy Tester date dropdown → "Custom date range" → start `2023-01-01`.
   **Date range RESETS to chart-start whenever you switch SCRIPT (Add to chart) — re-set it.**
   It PERSISTS across symbol changes and across "Update on chart" (same instance).

### MANDATORY pre-record checklist (every single read)
1. **Full report** read from DOM snapshot (returns all stats incl. CAGR; no scrolling needed).
2. **Date range** = `Jan 1, 2023 — Jun 6, 2026` (verify the button text).
3. **Refreshed** — if "The report is outdated" / Update report button shows, CLICK it; re-read.
4. **Right model** — active strategy name in report = the strategy being tested (not a leftover).
5. **Clean up** any scratch png created for diagnosis (read from DOM instead; delete pngs after).

Read: Total PnL %, Max drawdown %, Profitable trades (WR + n/N), Profit factor, CAGR.

## Full sweep — 4H, 2023-01-01 → 2026-06-06 (file-default params)
See `backtest_results/SWEEP_2023_4H.md` for the complete 20-cell table. Highlights:
| Strategy | Best market | CAGR | WR | PF | DD |
|---|---|---|---|---|---|
| TM Long Only | SOL | 48.84% | 33.82% | 1.452 | 36.20% |
| TM Long Only | BTC | 39.52% | 38.89% | 1.876 | 19.21% |
| TM Long Only | XAU | 13.62% | 46.30% | 2.174 | 8.42% |
| Donchian V1 | BTC | 24.77% | 33.80% | 1.48 | 26.09% |
| Donchian V1 | ETH | 23.26% | 32.76% | 1.552 | 21.63% |
| QB V1 (default) | SOL | 11.55% | 59.38% | 2.78 | 5.23% |
| QB V1 (default) | XAU | 4.73% | 52.63% | 3.084 | 3.76% |
| MR V2 | BTC | 11.12% | 58.33% | 1.99 | 18.17% |
| MR V1 | BTC | 3.82% | 61.54% | 2.788 | 5.12% |

**Cross-finding:** QB V1 wins mean-reversion markets (SOL/XAU), loses BTC/ETH. Donchian is the
opposite — wins trending BTC/ETH, loses SOL/XAU. TM-LO = highest CAGR but highest DD; shorts (L+S)
always hurt. QB V1 at file-default sizing is conservative; tuned (Risk 5/ATR 2.5) → SOL ~23.63%.

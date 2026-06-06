# Strategy Sweep — 4H, 2023-01-01 → 2026-06-06

All BINANCE crypto (BTCUSDT/ETHUSDT/SOLUSDT) + XAU. TradingView Strategy Tester (DEEP).
Re-set custom date range to 2023-01-01 on EVERY script switch (it resets to chart start).

| Strategy | Market | CAGR | WR | PF | MaxDD | Net | Verdict |
|---|---|---|---|---|---|---|---|
| TM Long Only | SOL | 48.84% | 33.82% (23/68) | 1.452 | 36.20% | +291.49% | high CAGR, high DD |
| TM Long Only | BTC | 39.52% | 38.89% (28/72) | 1.876 | 19.21% | +213.63% | 🟢 best TM-LO balance |
| TM Long Only | ETH | 12.52% | 25.00% (17/68) | 1.227 | 29.49% | +49.90% | weak |
| TM Long Only | XAU | 13.62% | 46.30% (25/54) | 2.174 | 8.42% | +54.85% | 🟢 low DD, high PF |
| TM Long+Short | SOL | 22.54% | 36.50% (50/137) | 1.09 | 53.93% | +155.05% | shorts add DD |
| TM Long+Short | BTC | 16.87% | 35.25% (49/139) | 1.198 | 31.15% | +104.15% | meh |
| TM Long+Short | ETH | −11.45% | 25.17% (37/147) | 0.888 | 54.56% | −17.26% | ❌ losing |
| TM Long+Short | XAU | 6.69% | 35.11% (33/94) | 1.287 | 15.02% | +28.03% | weak |
| MR V2 | SOL | 10.86% | 50.00% (9/18) | 1.866 | 15.49% | +42.46% | balanced |
| MR V2 | BTC | 11.12% | 58.33% (14/24) | 1.99 | 18.17% | +43.61% | 🟢 best MR V2 |
| MR V2 | ETH | 8.20% | 40.74% (11/27) | 1.519 | 19.31% | +31.07% | ok |
| MR V2 | XAU | 1.70% | 58.33% (7/12) | 2.464 | 3.33% | +5.96% | low freq, high PF |
| QB V1* | SOL | 11.55% | 59.38% (19/32) | 2.78 | 5.23% | +45.51% | 🟢 excellent quality |
| QB V1* | BTC | −1.46% | 45.45% (10/22) | 0.737 | 10.85% | −4.91% | ❌ losing |
| QB V1* | ETH | −0.42% | 40.00% (6/15) | 0.898 | 10.68% | −1.45% | ❌ losing |
| QB V1* | XAU | 4.73% | 52.63% (10/19) | 3.084 | 3.76% | +17.15% | 🟢 best PF, tiny DD |

\* QB V1 run at **file-default** sizing (qty 10% equity). Your tuned "best" (Risk 5.0 / ATR 2.5)
gave SOL CAGR ~23.63% historically — same signals (WR 59.38% identical), bigger positions →
higher CAGR + higher DD (~20%). To replicate, set Risk%=5.0, ATR stop=2.5 in inputs.

| Donchian V1 | SOL | 7.45% | 38.16% (29/76) | 1.095 | 45.35% | +27.98% | ❌ poor |
| Donchian V1 | BTC | 24.77% | 33.80% (24/71) | 1.48 | 26.09% | +113.73% | 🟢 best Donchian |
| Donchian V1 | ETH | 23.26% | 32.76% (19/58) | 1.552 | 21.63% | +105.00% | 🟢 strong |
| Donchian V1 | XAU | 1.01% | 37.29% (22/59) | 1.09 | 9.62% | +3.50% | ❌ flat |

## Key cross-findings
- **QB V1 ↔ Donchian are opposites**: QB wins SOL/XAU (mean-reversion regimes), loses BTC/ETH;
  Donchian wins BTC/ETH (clean trends), loses SOL/XAU.
- **TM Long Only** = highest raw CAGR (SOL 48.84%, BTC 39.52%) but high DD; shorts (L+S) always hurt.
- **MR V2** = balanced mid (~8-11% CAGR, controlled DD). (MR V1 removed — over-filtered, superseded.)
- No strategy hits the 30%+/PF2/DD<20 target on default params except TM-LO by CAGR (but DD too high).
- Best risk-adjusted: QB V1/XAU (PF 3.08, DD 3.76%), QB V1/SOL (PF 2.78, DD 5.23%), MR V2/XAU (PF 2.46, DD 3.33%).

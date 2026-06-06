# Trend Meter (TM)

Strategy 1 — the original "trend thingy". EMA stack 13/21/34/55 + Stochastic RSI cross.
Long when all 3 EMA bands green + Stoch K crosses up. Back to [[index]] · spec [[CLAUDE]].

Pine: `TM_LongOnly.pine`, `TM_LongShort.pine`. Live on VPS (long-only).

## Logic
- Bands: emaB>emaF (1), emaF>emaM (2), emaM>emaS (3). All green = uptrend.
- Entry long: all bands green + StochRSI K crossover D.
- Exit long: bands flip (not all green). L+S variant adds mirror short side.

## Sweep results (4H, 2023→2026) — see [[SWEEP_2023_4H]]
| Variant | Market | CAGR | WR | PF | DD |
|---|---|---|---|---|---|
| Long Only | SOL | 48.84% | 33.82% | 1.452 | 36.20% |
| Long Only | BTC | 39.52% | 38.89% | 1.876 | 19.21% |
| Long Only | ETH | 12.52% | 25.00% | 1.227 | 29.49% |
| Long Only | XAU | 13.62% | 46.30% | 2.174 | 8.42% |
| Long+Short | SOL | 22.54% | 36.50% | 1.09 | 53.93% |
| Long+Short | BTC | 16.87% | 35.25% | 1.198 | 31.15% |
| Long+Short | ETH | −11.45% | 25.17% | 0.888 | 54.56% |
| Long+Short | XAU | 6.69% | 35.11% | 1.287 | 15.02% |

## Verdict
Highest raw CAGR of all strategies (SOL/BTC) but **high drawdown** (trend follower, low WR).
**Shorts always hurt** — L+S worse than LO on every market; ETH L+S actually loses.
Best home: BTC (CAGR 39.5%, PF 1.88, DD 19%) or XAU (low DD, PF 2.17).
Trend-camp sibling: [[donchian-breakout]]. Opposite camp: [[quant-blend]].

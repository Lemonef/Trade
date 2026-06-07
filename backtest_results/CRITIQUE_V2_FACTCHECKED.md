# Re-critique, fact-checked against research (with sources)

Went back over every critique point and checked it against literature + our own extended tests.
Verdict: **several of my earlier criticisms were too harsh.** The approach is more robust than I claimed.

## The single most important source
Zarattini, Pagani, Barbon — **"Catching Crypto Trends"** (SSRN 5209907): classic trend-following on a
**survivorship-bias-FREE dataset of all crypto since 2015**, rotating the **top-20 liquid coins** —
essentially our strategy — achieved **Sharpe > 1.5, +10.8% annual alpha vs BTC, net of fees.**
This directly tests the things I worried about. Links at bottom.

## Each critique point, fact-checked
| # | My earlier claim | Verdict after research |
|---|---|---|
| 1 | Crowded/commodity edge | **TRUE but overstated.** Still Sharpe 1.25-1.5 net-of-fees in 2024-25 crypto. Crowded ≠ dead. |
| 2 | Trend-following decaying | **Overstated for crypto.** Recent studies still ~1.5 Sharpe. Decay real in legacy futures, less so crypto so far. |
| 3 | Regime-lucky / tiny sample | **Largely REFUTED.** Our extended test (8yr, survives 2018 −84% BTC) + SSRN (since 2015) show robustness across regimes. |
| 4 | Low 43% win rate | **TRUE & normal.** Sources confirm Donchian WR 30-40%, winners 3-5× losers. Inherent, not a flaw. |
| 5 | Fake diversification (correlated) | **TRUE,** now mitigated by the BTC master regime filter (halves bear loss). |
| 6 | Survivorship bias inflates it | **Overstated.** SSRN's bias-FREE study still got Sharpe 1.5 → survivorship isn't the main driver. Ours still has it, but it's not fatal. |
| 7 | Close-based stops understate DD | **TRUE** (backtest). Live bot uses intrabar low for stops — better. |
| 8 | Leverage liquidation + funding ignored | **TRUE & important.** Research: a correct-direction trend trade can still LOSE to adverse funding. Real concern for leveraged futures. |
| 9 | Mediocre Sharpe ~0.8 | **Fair for OUR build** (~0.86-0.91 OOS), but the concept's ceiling is ~1.5 (SSRN). Implementation gap, not a dead edge. |
| 10 | Pure leveraged beta | **Overstated.** SSRN shows +10.8% alpha *over* BTC → real alpha beyond beta, mostly from rotation + bear-avoidance. |
| 11 | Never traded live | TRUE. Still cash. Paper phase ongoing. |
| 12 | Tail risks (hack, depeg, delisting) | TRUE, unmodeled. Real crypto risk. |

## Improvements tested this round (evidence-backed)
| Idea | Source rationale | Result |
|---|---|---|
| **Volatility targeting** | Harvey et al.: improves Sharpe for risk assets | ❌ **Hurt** (OOS 0.86→0.4). Strategy is already vol-managed (ATR sizing + regime filters + cash); overlay double-counts and levers into re-entries. |
| Faster lookback (20/10 vs 55/20) | crypto responsiveness | Already tested earlier — **55/20 won** OOS. |
| Ensembles / carry / momentum / long-short | diversify alphas | Already tested — **all worse OOS** than trend core. |
| Universe expansion 10→20 | more independent bets | ✅ helped (OOS 0.61→0.91). Kept. |
| BTC master regime filter | cut correlated crashes | ✅ helped (halves 2022 loss). Kept. |

## Honest conclusion (revised)
- My first critique was **too pessimistic on robustness** (points 3, 6, 9, 10). Literature + our 8-year
  test show the approach is a **legitimate Sharpe ~1.0-1.5 edge**, not a mirage. The SSRN paper is near-proof
  the *concept* works survivorship-bias-free.
- The **valid, surviving criticisms**: low WR (inherent), funding/liquidation risk at leverage (real —
  keep leverage low), tail risks (unmodeled), and our implementation is cruder than the SSRN ceiling.
- **Improvement search is exhausted** — the evidence-backed lever (vol-targeting) didn't help because the
  strategy is already well-risk-managed. Adding more = overfitting. The honest next gains are:
  (a) a cleaner SSRN-style **rotational top-N** construction, (b) **funding-aware** sizing for the futures
  version — both real projects, not session knobs.

## Sources
- [Catching Crypto Trends — Zarattini/Pagani/Barbon (SSRN 5209907)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5209907)
- [Trend-following Strategies for Crypto Investors — Monash](https://www.monash.edu/__data/assets/pdf_file/0011/3744821/Trend-following-Strategies-for-Crypto-Investors.pdf)
- [The Impact of Volatility Targeting — Man Group (Harvey et al.)](https://www.man.com/insights/the-impact-of-volatility-targeting)
- [Volatility Targeting Improves Risk-Adjusted Returns — Alpha Architect](https://alphaarchitect.com/volatility-targeting-improves-risk-adjusted-returns/)
- [Position Sizing in Trend-Following — Concretum Group](https://concretumgroup.com/position-sizing-in-trend-following-comparing-volatility-targeting-volatility-parity-and-pyramiding/)
- [Volatility targeting impact — QuantPedia](https://quantpedia.com/Blog/Details/the-impact-of-volatility-targeting-on-equities-bonds-commodities-and-currencies)

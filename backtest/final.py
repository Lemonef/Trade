"""
Final, honest evaluation. Realistic config only (stop_mult=2.0 so the stop actually risk-controls).
Equal-weight & risk-parity basket portfolios, full period + train/test split for robustness.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from engine import load, backtest, BARS_PER_YEAR

DATA = Path(__file__).parent / "data"; IV = "4h"
BASKET = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","LTCUSDT","DOGEUSDT"]
CFG = dict(strat="donchian", entry=20, exit=10, risk=5, stop_mult=2.0, adx_filter=True, pyramid=3)

def sleeve(sym):
    eq,_ = backtest(load(sym, IV, DATA), CFG)
    return eq.pct_change().fillna(0.0).rename(sym)

def pm(pr):
    if len(pr) < 5 or pr.std() == 0: return (0,0,0,0)
    eq=(1+pr).cumprod(); yrs=len(eq)/BARS_PER_YEAR[IV]
    cagr=eq.iloc[-1]**(1/yrs)-1; dd=(eq/eq.cummax()-1).min()
    sh=pr.mean()/pr.std()*np.sqrt(BARS_PER_YEAR[IV])
    dn=pr[pr<0].std(); so=pr.mean()/dn*np.sqrt(BARS_PER_YEAR[IV]) if dn>0 else 0
    return (cagr*100, dd*100, sh, so)

rets = pd.concat([sleeve(s) for s in BASKET], axis=1).fillna(0.0)
vol = rets.std()*np.sqrt(BARS_PER_YEAR[IV])
w_eq = pd.Series(1/len(BASKET), index=rets.columns)
w_rp = (1/vol)/(1/vol).sum()
pr_eq = (rets*w_eq).sum(axis=1)
pr_rp = (rets*w_rp).sum(axis=1)

def line(tag, pr):
    c,d,s,so = pm(pr); print(f"  {tag:28s} CAGR {c:7.2f}%  DD {d:7.2f}%  Sharpe {s:.2f}  Sortino {so:.2f}")

print("=== FULL PERIOD 2023-01 -> 2026-06 (realistic cfg: pyr=3 stop=2.0) ===")
line("equal-weight 1.0x", pr_eq)
line("equal-weight 0.7x (target)", pr_eq*0.7)
line("risk-parity 1.0x (target)", pr_rp)

n = len(rets); half = n//2
print("\n=== TRAIN (1st half ~2023-2024) vs TEST (2nd half ~2025-2026) — equal-weight 1.0x ===")
line("TRAIN", pr_eq.iloc[:half])
line("TEST ", pr_eq.iloc[half:])
print("\n=== TRAIN vs TEST — risk-parity 1.0x ===")
line("TRAIN", pr_rp.iloc[:half])
line("TEST ", pr_rp.iloc[half:])

print("\n=== per-sleeve (realistic cfg), for transparency ===")
for s in BASKET:
    c,d,sh,so = pm(rets[s])
    print(f"  {s:9s} CAGR {c:7.2f}%  DD {d:7.2f}%  Sharpe {sh:.2f}")

# save equity curves for the report
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10,5))
    (1+pr_eq).cumprod().plot(ax=ax, label="Equal-weight 1.0x", color="tab:blue")
    (1+pr_rp).cumprod().plot(ax=ax, label="Risk-parity 1.0x", color="tab:green")
    (1+pr_eq*0.7).cumprod().plot(ax=ax, label="Equal-weight 0.7x (target)", color="tab:orange")
    ax.set_yscale("log"); ax.set_title("Pyramided-Donchian basket portfolio (in-sample, 4H 2023-26)")
    ax.legend(); ax.grid(True, alpha=0.3)
    out = Path(__file__).parent.parent / "backtest_results" / "portfolio_equity.png"
    fig.savefig(out, dpi=110, bbox_inches="tight")
    print(f"\nsaved equity curve -> {out}")
except Exception as e:
    print(f"\n(matplotlib unavailable, skipped chart: {e})")

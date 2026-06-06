"""Bear-market retest: run the basket portfolio on 2021-2022 (incl the 2022 crash)."""
import numpy as np, pandas as pd
from pathlib import Path
from engine import load, backtest, BARS_PER_YEAR

DATA = Path(__file__).parent / "data"; IV="4h"
BASKET = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","LTCUSDT","DOGEUSDT"]
CFG = dict(strat="donchian", entry=20, exit=10, risk=5, stop_mult=2.0, adx_filter=True, pyramid=3)

def sleeve(sym):
    eq,_ = backtest(load(f"{sym}_bear", IV, DATA), CFG)
    return eq.pct_change().fillna(0.0).rename(sym)

def pm(pr):
    if len(pr)<5 or pr.std()==0: return (0,0,0,0)
    eq=(1+pr).cumprod(); yrs=len(eq)/BARS_PER_YEAR[IV]
    cagr=eq.iloc[-1]**(1/yrs)-1; dd=(eq/eq.cummax()-1).min()
    sh=pr.mean()/pr.std()*np.sqrt(BARS_PER_YEAR[IV])
    dn=pr[pr<0].std(); so=pr.mean()/dn*np.sqrt(BARS_PER_YEAR[IV]) if dn>0 else 0
    return (cagr*100, dd*100, sh, so)

rets = pd.concat([sleeve(s) for s in BASKET], axis=1).fillna(0.0)
vol = rets.std()*np.sqrt(BARS_PER_YEAR[IV])
w_rp = (1/vol)/(1/vol).sum()
pr_eq = rets.mean(axis=1)
pr_rp = (rets*w_rp).sum(axis=1)

def line(tag, pr):
    c,d,s,so=pm(pr); print(f"  {tag:34s} CAGR {c:8.2f}%  DD {d:8.2f}%  Sharpe {s:6.2f}  Sortino {so:6.2f}")

cut = pd.Timestamp("2022-01-01", tz="UTC")
print("=== BEAR RETEST: full 2021-01 -> 2023-01 ===")
line("equal-weight 1.0x", pr_eq)
line("equal-weight 0.7x", pr_eq*0.7)
line("risk-parity 1.0x", pr_rp)
print("\n=== 2021 ONLY (bull top) ===")
line("equal-weight 1.0x", pr_eq[pr_eq.index < cut])
print("\n=== 2022 ONLY (the crash) — survival test ===")
line("equal-weight 1.0x", pr_eq[pr_eq.index >= cut])
line("equal-weight 0.7x", pr_eq[pr_eq.index >= cut]*0.7)
line("risk-parity 1.0x", pr_rp[pr_rp.index >= cut])

print("\n=== per-sleeve 2022-only (the crash) ===")
for s in BASKET:
    r = rets[s][rets.index >= cut]
    c,d,sh,so = pm(r)
    print(f"  {s:9s} CAGR {c:8.2f}%  DD {d:8.2f}%  Sharpe {sh:5.2f}")

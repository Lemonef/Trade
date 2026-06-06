"""Tune the basket portfolio for max Sharpe near the 70-80% CAGR target."""
import numpy as np
import pandas as pd
from pathlib import Path
from engine import load, backtest, BARS_PER_YEAR

DATA = Path(__file__).parent / "data"; IV = "4h"
BASKET = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","LTCUSDT","DOGEUSDT"]

def sleeve(sym, cfg):
    eq,_ = backtest(load(sym, IV, DATA), cfg)
    return eq.pct_change().fillna(0.0).rename(sym)

def pm(pr):
    eq=(1+pr).cumprod(); yrs=len(eq)/BARS_PER_YEAR[IV]
    cagr=eq.iloc[-1]**(1/yrs)-1; dd=(eq/eq.cummax()-1).min()
    sh=pr.mean()/pr.std()*np.sqrt(BARS_PER_YEAR[IV]) if pr.std()>0 else 0
    dn=pr[pr<0].std(); so=pr.mean()/dn*np.sqrt(BARS_PER_YEAR[IV]) if dn>0 else 0
    return cagr*100, dd*100, sh, so

print("=== param scan (equal-weight basket, 1.0x) ===")
best=None
for pyr in [2,3,4,5]:
    for sm in [1.5,2.0,2.5,3.0]:
        cfg=dict(strat="donchian",entry=20,exit=10,risk=5,stop_mult=sm,adx_filter=True,pyramid=pyr)
        rets=pd.concat([sleeve(s,cfg) for s in BASKET],axis=1).fillna(0.0)
        pr=rets.mean(axis=1)
        cagr,dd,sh,so=pm(pr)
        tag=f"pyr={pyr} stop={sm}"
        print(f"  {tag:16s} CAGR {cagr:7.2f}%  DD {dd:7.2f}%  Sharpe {sh:.2f}  Sortino {so:.2f}")
        if best is None or sh>best[0]: best=(sh,tag,cfg,cagr,dd,so)

print(f"\nBEST SHARPE: {best[1]} -> Sharpe {best[0]:.2f} CAGR {best[3]:.1f}% DD {best[4]:.1f}% Sortino {best[5]:.2f}")

# de-lever best to ~75% CAGR target
cfg=best[2]
rets=pd.concat([sleeve(s,cfg) for s in BASKET],axis=1).fillna(0.0)
pr=rets.mean(axis=1)
print("\n=== de-lever BEST to land in 70-80% CAGR ===")
for L in np.arange(0.4,1.55,0.1):
    cagr,dd,sh,so=pm(pr*L)
    mark=" <== target" if 70<=cagr<=80 else ""
    print(f"  {L:.1f}x : CAGR {cagr:7.2f}%  DD {dd:7.2f}%  Sharpe {sh:.2f}  Sortino {so:.2f}{mark}")

# ADX-filter on/off and adding a 200-EMA market filter idea: try requiring close>EMA200 (regime)
print("\n=== add long-term trend filter (only trade coin above its 200-bar EMA) ===")
def sleeve_f(sym,cfg):
    df=load(sym,IV,DATA)
    ema200=df.close.ewm(span=200,adjust=False).mean()
    eq,_=backtest(df,{**cfg,"ema_filter":ema200})  # engine ignores unknown; filter applied below instead
    return eq
# simpler: rebuild with manual filter by zeroing entries when below ema (approx via post-mask not exact) -> skip, note
print("  (skipped — needs engine support; noting as next step)")

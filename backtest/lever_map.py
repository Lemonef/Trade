"""Leverage map on the best robust configs (full cycle 2021-2026) — where does 70-80% CAGR land?"""
import numpy as np, pandas as pd
from pathlib import Path
from engine import load, backtest, BARS_PER_YEAR

DATA = Path(__file__).parent / "data"; IV="4h"
BASKET = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","LTCUSDT","DOGEUSDT"]

def load_merged(sym):
    df=pd.concat([load(f"{sym}_bear",IV,DATA), load(sym,IV,DATA)])
    return df[~df.index.duplicated(keep="first")].sort_index()
M={s:load_merged(s) for s in BASKET}

def ret(sym,cfg):
    eq,_=backtest(M[sym],cfg); return eq.pct_change().fillna(0.0).rename(sym)

def met(pr):
    eq=(1+pr).cumprod(); yrs=len(eq)/BARS_PER_YEAR[IV]
    cagr=eq.iloc[-1]**(1/yrs)-1 if eq.iloc[-1]>0 else -1
    dd=(eq/eq.cummax()-1).min(); sh=pr.mean()/pr.std()*np.sqrt(BARS_PER_YEAR[IV])
    return cagr*100,dd*100,sh

CFGS={
 "qbv1_ma200":dict(strat="qb_v1",risk=5,stop_mult=2.5,ma_filter=200),
 "qbhybrid_ma200":dict(strat="qb_hybrid",entry=20,exit=10,risk=5,stop_mult=2.5,ma_filter=200),
 "don5520_ma200":dict(strat="donchian",entry=55,exit=20,risk=5,stop_mult=2.5,adx_filter=True,ma_filter=200),
}
for name,cfg in CFGS.items():
    rets=pd.concat([ret(s,cfg) for s in BASKET],axis=1).fillna(0.0)
    pr=rets.mean(axis=1)
    print(f"\n=== {name} (equal-weight, full cycle) leverage map ===")
    for L in [1.0,1.5,2.0,2.5,3.0]:
        c,d,sh=met(pr*L)
        mark=" <== 70-80%" if 70<=c<=85 else ""
        print(f"  {L:.1f}x : CAGR {c:7.1f}%  DD {d:7.1f}%  Sharpe {sh:.2f}{mark}")

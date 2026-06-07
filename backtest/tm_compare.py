"""
Head-to-head, SAME data & method: TM Long Only vs the new Donchian55/20+MA200 basket.
TM-LO = long when the 4 EMAs (13>21>34>55) are stacked bullish, flat otherwise, full equity
(its native style). Merged 2021-2026, 4H, basket of 10 coins. Full / 2022 bear / OOS split.
"""
import numpy as np, pandas as pd
from pathlib import Path
from engine import load, backtest, BARS_PER_YEAR

DATA = Path(__file__).parent / "data"; IV="4h"
BASKET = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","LTCUSDT","DOGEUSDT"]
COMM=0.001+0.0005

def load_merged(sym):
    df=pd.concat([load(f"{sym}_bear",IV,DATA), load(sym,IV,DATA)])
    return df[~df.index.duplicated(keep="first")].sort_index()
M={s:load_merged(s) for s in BASKET}

def met(pr):
    pr=pr.dropna()
    eq=(1+pr).cumprod(); yrs=len(eq)/BARS_PER_YEAR[IV]
    cagr=eq.iloc[-1]**(1/yrs)-1 if eq.iloc[-1]>0 else -1
    dd=(eq/eq.cummax()-1).min(); sh=pr.mean()/pr.std()*np.sqrt(BARS_PER_YEAR[IV]) if pr.std()>0 else 0
    dn=pr[pr<0].std(); so=pr.mean()/dn*np.sqrt(BARS_PER_YEAR[IV]) if dn>0 else 0
    return cagr*100,dd*100,sh,so

# --- TM Long Only (4-EMA stack) ---
def tm_ret(sym):
    c=M[sym].close
    e1,e2,e3,e4=[c.ewm(span=n,adjust=False).mean() for n in (13,21,34,55)]
    green=((e1>e2)&(e2>e3)&(e3>e4)).astype(float)
    pos=green.shift(1).fillna(0.0)
    r=c.pct_change().fillna(0.0)
    trades=pos.diff().abs().fillna(0.0)        # entries/exits
    return (pos*r - trades*COMM).rename(sym)

tm = pd.concat([tm_ret(s) for s in BASKET],axis=1).fillna(0.0).mean(axis=1)

# --- New Donchian 55/20 + MA200 basket ---
CFG=dict(strat="donchian",entry=55,exit=20,risk=5,stop_mult=2.5,adx_filter=True,ma_filter=200)
def don_ret(sym):
    eq,_=backtest(M[sym],CFG); return eq.pct_change().fillna(0.0).rename(sym)
don = pd.concat([don_ret(s) for s in BASKET],axis=1).fillna(0.0).mean(axis=1)

y22a=pd.Timestamp("2022-01-01",tz="UTC"); y22b=pd.Timestamp("2023-01-01",tz="UTC")
def bear22(pr): return pr[(pr.index>=y22a)&(pr.index<y22b)]
n=len(don); oos=int(n*0.6)
def row(tag,pr):
    c,d,s,so=met(pr); print(f"  {tag:30s} CAGR {c:8.1f}%  DD {d:7.1f}%  Sharpe {s:5.2f}  Sortino {so:5.2f}")

print("=== TM Long Only (4-EMA stack), basket, same data ===")
row("FULL 2021-2026", tm)
row("2022 bear only", bear22(tm))
row("OOS last 40% (2024-26)", tm.iloc[oos:])
print("\n=== Donchian 55/20 + MA200 basket (the new model) ===")
row("FULL 2021-2026", don)
row("2022 bear only", bear22(don))
row("OOS last 40% (2024-26)", don.iloc[oos:])

# correlation
print(f"\ncorrelation TM vs Donchian (daily): {tm.corr(don):.2f}")

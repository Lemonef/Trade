"""
Evidence-backed test: VOLATILITY TARGETING (Harvey et al. - improves Sharpe for risk assets).
Scale the trend basket's exposure to a constant annual vol target (sane levels), capped leverage,
only when deployed. Compare base vs vol-targeted, OOS. Engine already does inverse-vol position
sizing (ATR); this is the portfolio-level overlay done correctly (earlier attempt used too-high target).
"""
import numpy as np, pandas as pd
from pathlib import Path
from engine import load, backtest

DATA=Path(__file__).parent/"data"; DPY=365
def have(s): return (DATA/f"{s}_bear_4h.csv").exists() and (DATA/f"{s}_4h.csv").exists()
coins=sorted({p.stem[:-3] for p in DATA.glob("*_4h.csv") if not p.stem.endswith("_bear") and have(p.stem[:-3])})
def merged(s):
    df=pd.concat([load(f"{s}_bear","4h",DATA), load(s,"4h",DATA)])
    return df[~df.index.duplicated(keep="first")].sort_index()
M={s:merged(s) for s in coins}
btc=M["BTCUSDT"].close; btc_reg=btc>btc.rolling(200).mean()
cfg=dict(strat="donchian",entry=55,exit=20,risk=5,stop_mult=2.5,adx_filter=True,ma_filter=200,btc_regime=btc_reg)
rs=[]
for s in coins:
    eq,_=backtest(M[s],cfg)
    rs.append(eq.resample("1D").last().ffill().pct_change().rename(s))
base=pd.concat(rs,axis=1).fillna(0.0).mean(axis=1)

def met(pr):
    pr=pr.dropna(); eq=(1+pr).cumprod(); yrs=len(eq)/DPY
    c=eq.iloc[-1]**(1/yrs)-1 if eq.iloc[-1]>0 else -1
    dd=(eq/eq.cummax()-1).min(); sh=pr.mean()/pr.std()*np.sqrt(DPY) if pr.std()>0 else 0
    return c*100,dd*100,sh

def voltarget(pr, target, maxlev=3.0, win=30):
    rv=pr.rolling(win).std()*np.sqrt(DPY)
    scale=(target/rv).clip(0,maxlev).shift(1).fillna(0.0)
    return pr*scale

n=len(base); oos=int(n*0.6)
def row(t,pr):
    f=met(pr); o=met(pr.iloc[oos:]); print(f"  {t:20s} FULL C{f[0]:6.1f}% DD{f[1]:6.1f}% Sh{f[2]:5.2f} | OOS C{o[0]:6.1f}% DD{o[1]:6.1f}% Sh{o[2]:5.2f}")

print(f"{len(coins)} coins\n=== base vs volatility-targeted (cap 3x) ===")
row("base (1x)", base)
for t in [0.15,0.20,0.25,0.30]:
    row(f"voltarget {int(t*100)}%", voltarget(base,t))

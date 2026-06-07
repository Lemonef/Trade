"""Last lever: risk-parity (inverse-vol) coin weighting vs equal-weight. OOS."""
import numpy as np, pandas as pd
from pathlib import Path
from engine import load, backtest
DATA=Path(__file__).parent/"data"; DPY=365
def have(s): return (DATA/f"{s}_bear_4h.csv").exists() and (DATA/f"{s}_4h.csv").exists()
coins=sorted({p.stem[:-3] for p in DATA.glob("*_4h.csv") if not p.stem.endswith("_bear") and have(p.stem[:-3])})
def merged(s):
    df=pd.concat([load(f"{s}_bear","4h",DATA), load(s,"4h",DATA)]); return df[~df.index.duplicated(keep="first")].sort_index()
M={s:merged(s) for s in coins}; btc=M["BTCUSDT"].close; reg=btc>btc.rolling(200).mean()
cfg=dict(strat="donchian",entry=55,exit=20,risk=5,stop_mult=2.5,adx_filter=True,ma_filter=200,btc_regime=reg)
R=pd.concat([backtest(M[s],cfg)[0].resample("1D").last().ffill().pct_change().rename(s) for s in coins],axis=1).fillna(0.0)
def met(pr):
    pr=pr.dropna(); eq=(1+pr).cumprod(); yrs=len(eq)/DPY
    c=eq.iloc[-1]**(1/yrs)-1 if eq.iloc[-1]>0 else -1; dd=(eq/eq.cummax()-1).min(); sh=pr.mean()/pr.std()*np.sqrt(DPY) if pr.std()>0 else 0
    return c*100,dd*100,sh
n=len(R); oos=int(n*0.6)
eqw=R.mean(axis=1)
vol=R.std(); w=(1/vol)/(1/vol).sum(); rpw=(R*w).sum(axis=1)
def row(t,pr):
    f=met(pr); o=met(pr.iloc[oos:]); print(f"  {t:16s} FULL Sh{f[2]:.2f} DD{f[1]:.1f}% | OOS C{o[0]:.1f}% DD{o[1]:.1f}% Sh{o[2]:.2f}")
print("equal-weight vs risk-parity:")
row("equal-weight", eqw); row("risk-parity", rpw)

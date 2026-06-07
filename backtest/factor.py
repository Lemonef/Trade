"""
Multi-factor cross-sectional sleeve (pro form): rank coins each day by a composite of
  + momentum (28d return)   + low-volatility (inverse 30d vol)   + carry (recent funding)
Long top-K, short bottom-K, dollar-neutral. Combine with trend+carry book.
"""
import numpy as np, pandas as pd
from pathlib import Path
from engine import load, backtest

DATA=Path(__file__).parent/"data"; DPY=365
def have_full(s): return (DATA/f"{s}_bear_4h.csv").exists() and (DATA/f"{s}_4h.csv").exists()
coins=sorted({p.stem[:-3] for p in DATA.glob("*_4h.csv") if not p.stem.endswith("_bear") and have_full(p.stem[:-3])})
carry_coins=[c for c in coins if (DATA/f"{c}_funding.csv").exists()]

def merged(s):
    df=pd.concat([load(f"{s}_bear","4h",DATA), load(s,"4h",DATA)])
    return df[~df.index.duplicated(keep="first")].sort_index()
PX=pd.DataFrame({s:merged(s).close.resample("1D").last() for s in coins}).dropna(how="all")
IDX=PX.index; RET=PX.pct_change().fillna(0.0)

def funding_daily(s):
    f=pd.read_csv(DATA/f"{s}_funding.csv"); f["dt"]=pd.to_datetime(f.fundingTime,unit="ms",utc=True)
    return f.set_index("dt").fundingRate.astype(float).resample("1D").sum()
FUND=pd.DataFrame({s:funding_daily(s) for s in carry_coins}).reindex(IDX).fillna(0.0)

def met(pr):
    pr=pr.dropna()
    if len(pr)<30 or pr.std()==0: return (0,0,0,0)
    eq=(1+pr).cumprod(); yrs=len(eq)/DPY
    cagr=eq.iloc[-1]**(1/yrs)-1 if eq.iloc[-1]>0 else -1
    dd=(eq/eq.cummax()-1).min(); sh=pr.mean()/pr.std()*np.sqrt(DPY)
    return (cagr*100,dd*100,sh)

# factors (z-scored cross-section each day)
mom=(PX/PX.shift(28)-1)
lowvol=-RET.rolling(30).std()
carry=FUND.reindex(columns=PX.columns).rolling(7).mean()
def z(df): return df.sub(df.mean(axis=1),axis=0).div(df.std(axis=1).replace(0,np.nan),axis=0)
score=(z(mom)+z(lowvol)+z(carry).fillna(0)).dropna(how="all")
K=4
rank=score.rank(axis=1,ascending=False)
nl=(rank<=K).astype(float); ns=(rank>=len(coins)-K+1).astype(float)
wl=nl.div(nl.sum(axis=1).replace(0,np.nan),axis=0).fillna(0.0)
ws=ns.div(ns.sum(axis=1).replace(0,np.nan),axis=0).fillna(0.0)
turn=(wl-ws).diff().abs().sum(axis=1).fillna(0.0)
factor=((wl-ws).shift(1).fillna(0.0)*RET).sum(axis=1) - turn*0.0005 - 0.15/DPY  # short cost

CFG=dict(strat="donchian",entry=55,exit=20,risk=5,stop_mult=2.5,adx_filter=True,ma_filter=200)
trend=pd.concat([backtest(merged(s),CFG)[0].resample("1D").last().ffill().pct_change().rename(s) for s in coins],axis=1).reindex(IDX).fillna(0.0).mean(axis=1)
carry_h=((FUND.clip(lower=0))-0.0003).mean(axis=1)

y22a=pd.Timestamp("2022-01-01",tz="UTC"); y22b=pd.Timestamp("2023-01-01",tz="UTC")
def bear(pr): return pr[(pr.index>=y22a)&(pr.index<y22b)]
n=len(IDX); oos=int(n*0.6)
def row(t,pr):
    f=met(pr); b=met(bear(pr)); o=met(pr.iloc[oos:])
    print(f"  {t:24s} FULL C{f[0]:7.1f}% DD{f[1]:6.1f}% Sh{f[2]:5.2f} | 2022 Sh{b[2]:5.2f} | OOS C{o[0]:6.1f}% Sh{o[2]:5.2f}")
def voltarget(pr,t=0.30,w=30):
    rv=pr.rolling(w).std()*np.sqrt(DPY); return pr*(t/rv).clip(upper=4.0).shift(1).fillna(0.0)
def ens(streams,t=0.30):
    df=pd.concat(streams,axis=1).fillna(0.0); vol=df.std()*np.sqrt(DPY); wt=(1/vol)/(1/vol).sum()
    return voltarget((df*wt).sum(axis=1),t)

print("=== sleeves ===")
row("trend",trend); row("carry harvest",carry_h); row("multi-factor L/S",factor)
print(f"\ncorr trend-carry {trend.corr(carry_h):.2f}  trend-factor {trend.corr(factor):.2f}  carry-factor {carry_h.corr(factor):.2f}")
print("\n=== ENSEMBLES (vol-target 30%) ===")
row("trend+carry",ens([trend,carry_h]))
row("trend+factor",ens([trend,factor]))
row("trend+carry+factor",ens([trend,carry_h,factor]))
best=ens([trend,carry_h,factor])
print("\n=== leverage on trend+carry+factor ===")
for L in [1.0,1.5,2.0,2.5,3.0]:
    f=met(best*L); print(f"  {L:.1f}x: CAGR {f[0]:7.1f}%  DD {f[1]:6.1f}%  Sharpe {f[2]:.2f}")

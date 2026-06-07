"""
Funding-rate CARRY sleeve (market-neutral: long spot / short perp, collect funding) +
ensemble with the trend basket. The pro move: stack uncorrelated edges.
Daily, merged 2021-2026. Carry modeled passively (collect signed funding) and harvest-positive-only,
with a cost haircut for spot-perp execution.
"""
import numpy as np, pandas as pd
from pathlib import Path
from engine import load, backtest

DATA=Path(__file__).parent/"data"; DPY=365
CARRY_COST=0.0003   # ~ daily spot-perp execution/spread drag

def have_full(sym): return (DATA/f"{sym}_bear_4h.csv").exists() and (DATA/f"{sym}_4h.csv").exists()
coins=sorted({p.stem[:-3] for p in DATA.glob("*_4h.csv") if not p.stem.endswith("_bear") and have_full(p.stem[:-3])})
carry_coins=[c for c in coins if (DATA/f"{c}_funding.csv").exists()]
print(f"price coins {len(coins)} | funding coins {len(carry_coins)}")

def merged(sym):
    df=pd.concat([load(f"{sym}_bear","4h",DATA), load(sym,"4h",DATA)])
    return df[~df.index.duplicated(keep="first")].sort_index()

# common daily index
PX=pd.DataFrame({s:merged(s).close.resample("1D").last() for s in coins}).dropna(how="all")
IDX=PX.index

def met(pr):
    pr=pr.dropna()
    if len(pr)<30 or pr.std()==0: return (0,0,0,0)
    eq=(1+pr).cumprod(); yrs=len(eq)/DPY
    cagr=eq.iloc[-1]**(1/yrs)-1 if eq.iloc[-1]>0 else -1
    dd=(eq/eq.cummax()-1).min(); sh=pr.mean()/pr.std()*np.sqrt(DPY)
    dn=pr[pr<0].std(); so=pr.mean()/dn*np.sqrt(DPY) if dn>0 else 0
    return (cagr*100,dd*100,sh,so)

# --- CARRY ---
def funding_daily(sym):
    f=pd.read_csv(DATA/f"{sym}_funding.csv")
    f["dt"]=pd.to_datetime(f.fundingTime,unit="ms",utc=True)
    s=f.set_index("dt").fundingRate.astype(float)
    return s.resample("1D").sum()   # ~3 per day summed

FUND=pd.DataFrame({s:funding_daily(s) for s in carry_coins}).reindex(IDX).fillna(0.0)
carry_passive=(FUND - CARRY_COST).mean(axis=1)                      # long spot/short perp, signed
carry_harvest=((FUND.clip(lower=0)) - CARRY_COST).mean(axis=1)      # collect only positive funding

# --- TREND (core) ---
CFG=dict(strat="donchian",entry=55,exit=20,risk=5,stop_mult=2.5,adx_filter=True,ma_filter=200)
def trend_daily(sym):
    eq,_=backtest(merged(sym),CFG); return eq.resample("1D").last().ffill().pct_change().rename(sym)
trend=pd.concat([trend_daily(s) for s in coins],axis=1).reindex(IDX).fillna(0.0).mean(axis=1)

y22a=pd.Timestamp("2022-01-01",tz="UTC"); y22b=pd.Timestamp("2023-01-01",tz="UTC")
def bear(pr): return pr[(pr.index>=y22a)&(pr.index<y22b)]
n=len(IDX); oos=int(n*0.6)
def row(tag,pr):
    f=met(pr); b=met(bear(pr)); o=met(pr.iloc[oos:])
    print(f"  {tag:26s} FULL C{f[0]:7.1f}% DD{f[1]:7.1f}% Sh{f[2]:5.2f} | 2022 Sh{b[2]:5.2f} | OOS C{o[0]:6.1f}% DD{o[1]:6.1f}% Sh{o[2]:5.2f}")

print("\n=== sleeves (daily, 1x) ===")
row("trend (core, ~20 coins)", trend)
row("carry passive", carry_passive)
row("carry harvest-positive", carry_harvest)
print(f"\ncorr trend vs carry_passive: {trend.corr(carry_passive):.2f}  vs harvest: {trend.corr(carry_harvest):.2f}")

def voltarget(pr,t=0.30,win=30):
    rv=pr.rolling(win).std()*np.sqrt(DPY); return pr*(t/rv).clip(upper=4.0).shift(1).fillna(0.0)
def ens(streams,t=0.30):
    df=pd.concat(streams,axis=1).fillna(0.0); vol=df.std()*np.sqrt(DPY); w=(1/vol)/(1/vol).sum()
    return voltarget((df*w).sum(axis=1),t)

print("\n=== ENSEMBLE trend + carry (inverse-vol, vol-target 30%) ===")
row("trend+carry_passive", ens([trend,carry_passive]))
row("trend+carry_harvest", ens([trend,carry_harvest]))

best=ens([trend,carry_harvest])
print("\n=== leverage on trend+carry_harvest ===")
for L in [1.0,1.5,2.0,2.5,3.0]:
    f=met(best*L); print(f"  {L:.1f}x: CAGR {f[0]:7.1f}%  DD {f[1]:7.1f}%  Sharpe {f[2]:.2f}")

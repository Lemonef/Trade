"""
Walk-forward validation (the honest overfit test).
Roll: train 12mo -> pick best-Sharpe param combo on train -> apply to next 3mo (out-of-sample) ->
step 3mo. Stitch all OOS test segments into one forward equity curve. Compare to fixed-param.
Basket of 10 coins, 4H, merged 2021-2026.
"""
import numpy as np, pandas as pd
from pathlib import Path
from engine import load, backtest, BARS_PER_YEAR

DATA = Path(__file__).parent / "data"; IV="4h"
BASKET = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","LTCUSDT","DOGEUSDT"]

def load_merged(sym):
    df=pd.concat([load(f"{sym}_bear",IV,DATA), load(sym,IV,DATA)])
    return df[~df.index.duplicated(keep="first")].sort_index()
M={s:load_merged(s) for s in BASKET}

# candidate param combos (kept simple to limit overfit DoF)
COMBOS={}
for entry,exit_ in [(20,10),(30,15),(40,20),(55,20)]:
    for sm in [2.0,2.5]:
        COMBOS[f"e{entry}_s{sm}"]=dict(strat="donchian",entry=entry,exit=exit_,risk=5,
                                       stop_mult=sm,adx_filter=True,ma_filter=200)

def basket_ret(cfg):
    rs=[]
    for s in BASKET:
        eq,_=backtest(M[s],cfg)
        rs.append(eq.pct_change().fillna(0.0).rename(s))
    return pd.concat(rs,axis=1).fillna(0.0).mean(axis=1)

# precompute basket returns per combo
R=pd.DataFrame({name:basket_ret(cfg) for name,cfg in COMBOS.items()}).fillna(0.0)

def sharpe(pr):
    return pr.mean()/pr.std()*np.sqrt(BARS_PER_YEAR[IV]) if len(pr)>20 and pr.std()>0 else -9

def met(pr):
    eq=(1+pr).cumprod(); yrs=len(eq)/BARS_PER_YEAR[IV]
    cagr=eq.iloc[-1]**(1/yrs)-1 if eq.iloc[-1]>0 else -1
    dd=(eq/eq.cummax()-1).min(); sh=sharpe(pr)
    dn=pr[pr<0].std(); so=pr.mean()/dn*np.sqrt(BARS_PER_YEAR[IV]) if dn>0 else 0
    return cagr*100,dd*100,sh,so

bpm=int(BARS_PER_YEAR[IV]/12)  # bars per month
train_n=12*bpm; test_n=3*bpm; step=3*bpm
idx=R.index; n=len(idx)
wf=[]; picks=[]
start=0
while start+train_n+test_n<=n:
    tr=R.iloc[start:start+train_n]
    te=R.iloc[start+train_n:start+train_n+test_n]
    best=max(COMBOS, key=lambda c: sharpe(tr[c]))
    picks.append(best)
    wf.append(te[best])
    start+=step
wf_oos=pd.concat(wf)

print(f"Walk-forward: train 12mo / test 3mo / step 3mo, {len(picks)} folds")
print(f"params picked per fold: {picks}")
print(f"\n=== WALK-FORWARD OUT-OF-SAMPLE (stitched, honest forward perf) ===")
c,d,sh,so=met(wf_oos); print(f"  CAGR {c:.1f}%  DD {d:.1f}%  Sharpe {sh:.2f}  Sortino {so:.2f}")

print("\n=== leverage on walk-forward OOS ===")
for L in [1.0,1.5,2.0,3.0]:
    c,d,sh,so=met(wf_oos*L); print(f"  {L:.1f}x: CAGR {c:7.1f}%  DD {d:7.1f}%  Sharpe {sh:.2f}")

print("\n=== benchmark: best FIXED combo over same OOS span (no reopt) ===")
span=R.loc[wf_oos.index[0]:wf_oos.index[-1]]
for name in COMBOS:
    c,d,sh,so=met(span[name]);
print("  fixed e20_s2.0:", "CAGR %.1f%% DD %.1f%% Sharpe %.2f"%met(span["e20_s2.0"])[:3])
print("  fixed e55_s2.5:", "CAGR %.1f%% DD %.1f%% Sharpe %.2f"%met(span["e55_s2.5"])[:3])

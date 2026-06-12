"""
RECONFIRM (2026-06-12): is range-bound mean-reversion (Bollinger + RSI oversold
dip-buy, the 'เหวี่ยงในกรอบ' swing) still DEAD on the live 25-coin 4h universe?
Long-only (crypto), equal-weight basket, net of fees, full + OOS, vs buy-hold.
Two variants: (A) Bollinger-only, (B) Bollinger + RSI filter.
"""
import numpy as np, pandas as pd
from pathlib import Path
DATA = Path(__file__).parent / "data"; DPY = 365; BARS_Y = DPY*6   # 4h
COST = 0.0008                                                      # 8 bps/side blended fee+slip

def have(s): return (DATA/f"{s}_bear_4h.csv").exists() and (DATA/f"{s}_4h.csv").exists()
coins = sorted({p.stem[:-3] for p in DATA.glob("*_4h.csv") if not p.stem.endswith("_bear") and have(p.stem[:-3])})
def load(s, tag):
    df = pd.read_csv(DATA/f"{s}{tag}_4h.csv")
    tcol = "open_time" if "open_time" in df.columns else df.columns[0]
    df["dt"] = pd.to_datetime(df[tcol], unit="ms", utc=True)
    return df.set_index("dt")[["open","high","low","close"]].astype(float)
def merged(s):
    df = pd.concat([load(s,"_bear"), load(s,"")]); return df[~df.index.duplicated(keep="first")].sort_index()
M = {s: merged(s) for s in coins}

def rsi(c, n=14):
    d = c.diff(); up = d.clip(lower=0); dn = -d.clip(upper=0)
    rs = up.ewm(alpha=1/n, adjust=False).mean() / dn.ewm(alpha=1/n, adjust=False).mean().replace(0, np.nan)
    return (100 - 100/(1+rs)).fillna(50)

def meanrev_ret(s, use_rsi, bb_n=20, bb_k=2.0, hold_max=10):
    c = M[s].close
    basis = c.rolling(bb_n).mean(); dev = bb_k*c.rolling(bb_n).std(ddof=0)
    lower = basis - dev; r = rsi(c)
    cv=c.values; lov=lower.values; bav=basis.values; rv=r.values
    pos=np.zeros(len(c)); held=0
    for i in range(1,len(c)):
        if held:
            pos[i]=1.0
            if cv[i]>=bav[i] or held>=hold_max: held=0; pos[i]=0.0
            else: held+=1
        else:
            entry = cv[i] < (lov[i] or -1e18)
            if use_rsi: entry = entry and rv[i] < 35
            if entry: held=1; pos[i]=1.0
    p=pd.Series(pos,index=c.index)
    return (p.shift(1).fillna(0)*c.pct_change() - p.diff().abs().fillna(0)*COST).rename(s)

def basket(use_rsi):
    cols=[meanrev_ret(s,use_rsi) for s in coins]
    return pd.concat(cols,axis=1).fillna(0.0).mean(axis=1).resample("1D").sum()
def buyhold():
    cols=[M[s].close.pct_change().rename(s) for s in coins]
    return pd.concat(cols,axis=1).fillna(0.0).mean(axis=1).resample("1D").sum()

def met(pr):
    pr=pr.dropna()
    if len(pr)<30 or pr.std()==0: return (0,0,0)
    eq=(1+pr).cumprod(); yrs=len(pr)/DPY
    cagr=(eq.iloc[-1]**(1/yrs)-1)*100 if eq.iloc[-1]>0 else -100
    dd=(eq/eq.cummax()-1).min()*100; sh=pr.mean()/pr.std()*np.sqrt(DPY)
    return (round(cagr,1),round(dd,1),round(sh,2))

bh=buyhold()
print(f"universe {len(coins)} coins, {bh.index.min().date()}..{bh.index.max().date()}, cost {COST*1e4:.0f}bps/side\n")
print(f"{'strategy':36s} {'FULL CAGR/DD/Sharpe':24s} {'OOS(last40%) CAGR/DD/Sharpe'}")
for lbl,pr in [("Bollinger-only reversion", basket(False)),
               ("Bollinger + RSI<35 reversion", basket(True)),
               ("equal-weight BUY-HOLD (bench)", bh)]:
    oo=int(len(pr)*0.6)
    f=met(pr); o=met(pr.iloc[oo:])
    print(f"{lbl:36s} {str(f):24s} {o}")
print("\nDead test: if reversion Sharpe < buy-hold AND/OR <0.3 net, range-oscillation edge = still dead.")

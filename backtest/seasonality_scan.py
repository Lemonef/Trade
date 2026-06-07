"""
Hunt a DIFFERENT family: seasonality. Avg 4h-bar return by day-of-week and by hour-of-day (UTC),
pooled across 25 coins 2021-2026. Persistent + sizeable = a seasonal edge (uncorrelated to
trend/reversion). Cheap expectancy check.
"""
import numpy as np, pandas as pd
from pathlib import Path
from engine import load
DATA=Path(__file__).parent/"data"
def have(s): return (DATA/f"{s}_bear_4h.csv").exists() and (DATA/f"{s}_4h.csv").exists()
coins=sorted({p.stem[:-3] for p in DATA.glob("*_4h.csv") if not p.stem.endswith("_bear") and have(p.stem[:-3])})
def merged(s):
    df=pd.concat([load(f"{s}_bear","4h",DATA), load(s,"4h",DATA)]); return df[~df.index.duplicated(keep="first")].sort_index()
rows=[]
for s in coins:
    c=merged(s).close; r=c.pct_change()
    df=pd.DataFrame({"r":r,"dow":r.index.dayofweek,"hr":r.index.hour}).dropna()
    rows.append(df)
A=pd.concat(rows)
base=A.r.mean()
print(f"baseline avg 4h return: {base*100:.4f}%\n")
print("=== by day-of-week (Mon=0) ===")
g=A.groupby("dow").r
for d in range(7):
    v=g.get_group(d); print(f"  {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][d]}: avg {v.mean()*100:7.4f}%  edge {(v.mean()-base)*100:7.4f}%  n={len(v)}")
print("\n=== by hour-of-day (UTC, 4h bars) ===")
g=A.groupby("hr").r
for h in sorted(A.hr.unique()):
    v=g.get_group(h); print(f"  {h:02d}:00 UTC: avg {v.mean()*100:7.4f}%  edge {(v.mean()-base)*100:7.4f}%  n={len(v)}")
# simple seasonal strategy: long only on the best day(s); corr to a buy&hold proxy
best_days=A.groupby("dow").r.mean().sort_values(ascending=False)
print("\nbest days:", [['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][d] for d in best_days.index[:2]])
print("NOTE: seasonality edges are usually tiny + fragile; need to be sizeable & persistent to trade.")

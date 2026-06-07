"""Fetch Binance perp funding-rate history 2021-2026 for all coins we have price data for."""
import time, csv
from pathlib import Path
import requests
OUT=Path(__file__).parent/"data"
BASE="https://fapi.binance.com/fapi/v1/fundingRate"
START=1609459200000; END=1780704000000

coins=sorted({p.stem[:-3] for p in OUT.glob("*_4h.csv") if not p.stem.endswith("_bear")})

def fetch(sym):
    rows=[]; start=START
    while start<END:
        try:
            r=requests.get(BASE,params={"symbol":sym,"startTime":start,"endTime":END,"limit":1000},timeout=20)
            if r.status_code!=200: return rows
            d=r.json()
        except Exception: return rows
        if not d: break
        rows.extend(d)
        if len(d)<1000: break
        start=d[-1]["fundingTime"]+1; time.sleep(0.1)
    return rows

for sym in coins:
    path=OUT/f"{sym}_funding.csv"
    if path.exists(): continue
    rows=fetch(sym)
    if not rows: print(f"{sym}: no funding"); continue
    with open(path,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["fundingTime","fundingRate"])
        for k in rows: w.writerow([k["fundingTime"],k["fundingRate"]])
    print(f"{sym}: {len(rows)} funding pts")
print("done")

"""Fetch 2021-01-01 -> 2023-01-01 (bull top 2021 + bear 2022) for the basket. 4H. Suffix _bear."""
import time, csv
from pathlib import Path
import requests

OUT = Path(__file__).parent / "data"; OUT.mkdir(exist_ok=True)
SYMBOLS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","LTCUSDT","DOGEUSDT"]
IV = "4h"
START_MS = 1609459200000   # 2021-01-01
END_MS   = 1672531200000   # 2023-01-01
BASE = "https://api.binance.com/api/v3/klines"

def fetch(sym):
    rows=[]; start=START_MS
    while start < END_MS:
        r=requests.get(BASE, params={"symbol":sym,"interval":IV,"startTime":start,"endTime":END_MS,"limit":1000}, timeout=20)
        r.raise_for_status(); d=r.json()
        if not d: break
        rows.extend(d)
        if len(d)<1000: break
        start=d[-1][0]+1; time.sleep(0.15)
    return rows

for sym in SYMBOLS:
    path=OUT/f"{sym}_bear_{IV}.csv"
    if path.exists(): print(f"skip {path.name}"); continue
    rows=fetch(sym)
    with open(path,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["open_time","open","high","low","close","volume"])
        for k in rows: w.writerow([k[0],k[1],k[2],k[3],k[4],k[5]])
    print(f"{sym}: {len(rows)} bars  ({path.name})")
print("done")

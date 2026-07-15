"""Fetch broader universe: 10 coins x [1h,4h,1d]. Skips files already cached."""
import time, csv
from pathlib import Path
import requests

OUT = Path(__file__).parent / "data"; OUT.mkdir(exist_ok=True)
# 22 pairs, all Binance-listed before 2023-01-01 (survivorship rule: see alpha_factory/config.py).
# PAXGUSDT (tokenized gold, listed 2020-08) and EURUSDT (fiat FX, listed 2020-01) extend the
# cross-section beyond crypto; newer gold/EUR tokens (XAUT/EURI/AEUR) fail the pre-2023 rule
# and GBP/AUD pairs are delisted (status BREAK).
SYMBOLS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","DOGEUSDT",
           "LINKUSDT","LTCUSDT","DOTUSDT","ATOMUSDT","UNIUSDT","ETCUSDT","XLMUSDT","FILUSDT",
           "NEARUSDT","SANDUSDT","TRXUSDT","EOSUSDT","PAXGUSDT","EURUSDT"]
INTERVALS = ["1h","4h","1d"]
START_MS=1672531200000; END_MS=1780704000000
BASE="https://api.binance.com/api/v3/klines"

def fetch(sym, iv):
    rows=[]; start=START_MS
    while start < END_MS:
        r=requests.get(BASE, params={"symbol":sym,"interval":iv,"startTime":start,"endTime":END_MS,"limit":1000}, timeout=20)
        r.raise_for_status(); d=r.json()
        if not d: break
        rows.extend(d)
        if len(d)<1000: break
        start=d[-1][0]+1; time.sleep(0.15)
    return rows

for sym in SYMBOLS:
    for iv in INTERVALS:
        path=OUT/f"{sym}_{iv}.csv"
        if path.exists():
            print(f"skip {path.name}"); continue
        rows=fetch(sym,iv)
        with open(path,"w",newline="") as f:
            w=csv.writer(f); w.writerow(["open_time","open","high","low","close","volume"])
            for k in rows: w.writerow([k[0],k[1],k[2],k[3],k[4],k[5]])
        print(f"{sym} {iv}: {len(rows)} bars")
print("done")

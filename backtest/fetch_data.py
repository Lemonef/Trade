"""Fetch Binance 4H + 1D klines for BTC/ETH/SOL, 2023-01-01 -> 2026-06-06. Cache to CSV."""
import time, csv
from pathlib import Path
import requests

OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVALS = ["4h", "1d"]
START_MS = 1672531200000   # 2023-01-01 00:00 UTC
END_MS   = 1780704000000   # 2026-06-07 00:00 UTC
BASE = "https://api.binance.com/api/v3/klines"


def fetch(symbol, interval):
    rows = []
    start = START_MS
    while start < END_MS:
        params = {"symbol": symbol, "interval": interval, "startTime": start,
                  "endTime": END_MS, "limit": 1000}
        r = requests.get(BASE, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        rows.extend(data)
        last_open = data[-1][0]
        if len(data) < 1000:
            break
        start = last_open + 1
        time.sleep(0.2)
    return rows


for sym in SYMBOLS:
    for iv in INTERVALS:
        rows = fetch(sym, iv)
        path = OUT / f"{sym}_{iv}.csv"
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["open_time", "open", "high", "low", "close", "volume"])
            for k in rows:
                w.writerow([k[0], k[1], k[2], k[3], k[4], k[5]])
        print(f"{sym} {iv}: {len(rows)} bars -> {path.name}")
print("done")

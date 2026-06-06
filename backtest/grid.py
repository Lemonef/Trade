"""Grid sweep: every cached symbol x TF x strategy-config. Rank by Sharpe and CAGR."""
import csv
from pathlib import Path
from engine import load, backtest, metrics

DATA = Path(__file__).parent / "data"

CONFIGS = {
    "donchian_20_10": dict(strat="donchian", entry=20, exit=10, risk=5, stop_mult=2.0, adx_filter=True),
    "donchian_55_20": dict(strat="donchian", entry=55, exit=20, risk=5, stop_mult=2.5, adx_filter=True),
    "donchian_pyr":   dict(strat="donchian", entry=20, exit=10, risk=5, stop_mult=2.0, adx_filter=True, pyramid=3),
    "qb_hybrid":      dict(strat="qb_hybrid", entry=20, exit=10, risk=5, stop_mult=2.5),
    "qb_hybrid_tr":   dict(strat="qb_hybrid", entry=20, exit=10, risk=5, stop_mult=2.5, trail=True, trail_mult=3.0),
    "meanrev":        dict(strat="meanrev", risk=5, stop_mult=2.5),
    "qb_v1":          dict(strat="qb_v1", risk=5, stop_mult=2.5),
}

files = sorted(DATA.glob("*.csv"))
pairs = []
for f in files:
    stem = f.stem
    sym, iv = stem.rsplit("_", 1)
    pairs.append((sym, iv))

rows = []
for sym, iv in pairs:
    df = load(sym, iv, DATA)
    for name, cfg in CONFIGS.items():
        try:
            eq, tr = backtest(df, cfg)
            m = metrics(eq, tr, iv)
        except Exception as e:
            print(f"ERR {sym} {iv} {name}: {e}"); continue
        rows.append(dict(sym=sym, iv=iv, strat=name, **m))

# write csv
out = Path(__file__).parent / "results_grid.csv"
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["sym","iv","strat","CAGR","MaxDD","Sharpe","WR","PF","n","final"])
    w.writeheader()
    for r in rows:
        w.writerow({k: (round(v,3) if isinstance(v,float) else v) for k,v in r.items()})

def fmt(r):
    return f"{r['sym']:9s} {r['iv']:3s} {r['strat']:14s} CAGR {r['CAGR']:7.2f}%  DD {r['MaxDD']:7.2f}%  Sharpe {r['Sharpe']:5.2f}  PF {r['PF']:5.2f}  WR {r['WR']:5.1f}  n={r['n']}"

valid = [r for r in rows if r["n"] >= 10 and r["final"] > 0]
print(f"\n=== TOP 15 by SHARPE (n>=10) ===")
for r in sorted(valid, key=lambda x: -x["Sharpe"])[:15]:
    print(fmt(r))
print(f"\n=== TOP 15 by CAGR (n>=10) ===")
for r in sorted(valid, key=lambda x: -x["CAGR"])[:15]:
    print(fmt(r))
print(f"\n{len(rows)} configs tested, results_grid.csv written")

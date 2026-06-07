"""
Full-cycle strategy search on merged 2021-2026 data (bull 2021 + bear 2022 + 2023-26).
Judged on OUT-OF-SAMPLE (last 40%) so we don't pick an overfit config.
Tests strategies x market-filter x params, basket + BTC-only.
"""
import numpy as np, pandas as pd
from pathlib import Path
from engine import load, backtest, BARS_PER_YEAR

DATA = Path(__file__).parent / "data"; IV="4h"
BASKET = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","LTCUSDT","DOGEUSDT"]

def load_merged(sym):
    a = load(f"{sym}_bear", IV, DATA)        # 2021-2022
    b = load(sym, IV, DATA)                   # 2023-2026
    df = pd.concat([a, b])
    df = df[~df.index.duplicated(keep="first")].sort_index()
    return df

MERGED = {s: load_merged(s) for s in BASKET}

def sleeve_ret(sym, cfg):
    eq,_ = backtest(MERGED[sym], cfg)
    return eq.pct_change().fillna(0.0).rename(sym)

def m(pr):
    if len(pr)<10 or pr.std()==0: return dict(CAGR=0,DD=0,Sharpe=0,Sortino=0)
    eq=(1+pr).cumprod(); yrs=len(eq)/BARS_PER_YEAR[IV]
    cagr=eq.iloc[-1]**(1/yrs)-1 if eq.iloc[-1]>0 else -1
    dd=(eq/eq.cummax()-1).min()
    sh=pr.mean()/pr.std()*np.sqrt(BARS_PER_YEAR[IV])
    dn=pr[pr<0].std(); so=pr.mean()/dn*np.sqrt(BARS_PER_YEAR[IV]) if dn>0 else 0
    return dict(CAGR=cagr*100, DD=dd*100, Sharpe=sh, Sortino=so)

CONFIGS = {
 "don2010":         dict(strat="donchian",entry=20,exit=10,risk=5,stop_mult=2.0,adx_filter=True),
 "don2010_ma200":   dict(strat="donchian",entry=20,exit=10,risk=5,stop_mult=2.0,adx_filter=True,ma_filter=200),
 "don2010_ma100":   dict(strat="donchian",entry=20,exit=10,risk=5,stop_mult=2.0,adx_filter=True,ma_filter=100),
 "don5520_ma200":   dict(strat="donchian",entry=55,exit=20,risk=5,stop_mult=2.5,adx_filter=True,ma_filter=200),
 "don2010_pyr_ma200":dict(strat="donchian",entry=20,exit=10,risk=5,stop_mult=2.0,adx_filter=True,ma_filter=200,pyramid=3),
 "qbhybrid_ma200":  dict(strat="qb_hybrid",entry=20,exit=10,risk=5,stop_mult=2.5,ma_filter=200),
 "qbv1_ma200":      dict(strat="qb_v1",risk=5,stop_mult=2.5,ma_filter=200),
 "meanrev":         dict(strat="meanrev",risk=5,stop_mult=2.5),
 "meanrev_ma200":   dict(strat="meanrev",risk=5,stop_mult=2.5,ma_filter=200),
}

# split index by fraction (full cycle ~2021-2026; test = last 40% ~2024-06 -> 2026)
sample_len = len(MERGED["BTCUSDT"])
print(f"Merged BTC bars: {sample_len} (~2021-01 -> 2026-06)\n")

rows=[]
for name,cfg in CONFIGS.items():
    rets = pd.concat([sleeve_ret(s,cfg) for s in BASKET], axis=1).fillna(0.0)
    pr = rets.mean(axis=1)
    n=len(pr); cut=int(n*0.6)
    full=m(pr); tr=m(pr.iloc[:cut]); te=m(pr.iloc[cut:])
    # BTC-only
    btc=m(rets["BTCUSDT"]); btc_te=m(rets["BTCUSDT"].iloc[cut:])
    rows.append((name,full,tr,te,btc,btc_te))

def fmt(d): return f"C{d['CAGR']:6.1f}% DD{d['DD']:6.1f}% Sh{d['Sharpe']:5.2f}"
print(f"{'config':20s} | BASKET full           | TRAIN(21-23)         | TEST OOS(24-26)      | BTC-only full        | BTC TEST")
for name,full,tr,te,btc,btc_te in rows:
    print(f"{name:20s} | {fmt(full)} | {fmt(tr)} | {fmt(te)} | {fmt(btc)} | {fmt(btc_te)}")

print("\n=== ranked by BASKET out-of-sample Sharpe ===")
for name,full,tr,te,btc,btc_te in sorted(rows,key=lambda x:-x[3]['Sharpe']):
    print(f"  {name:20s} OOS: {fmt(te)}  Sortino {te['Sortino']:.2f}")

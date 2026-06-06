"""
Portfolio backtest: pyramided Donchian across a crypto basket, combined into ONE account.
Tests equal-weight vs inverse-vol (risk-parity) weighting, then a leverage sweep to hit a
target CAGR while tracking Sharpe / MaxDD. This is the real combined equity curve.
"""
import numpy as np
import pandas as pd
from pathlib import Path
from engine import load, backtest, BARS_PER_YEAR

DATA = Path(__file__).parent / "data"
IV = "4h"
BASKET = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","LTCUSDT","DOGEUSDT"]
CFG = dict(strat="donchian", entry=20, exit=10, risk=5, stop_mult=2.0, adx_filter=True, pyramid=3)


def sleeve_returns(sym):
    df = load(sym, IV, DATA)
    eq, _ = backtest(df, CFG)
    r = eq.pct_change().fillna(0.0)
    r.name = sym
    return r


def port_metrics(port_ret):
    eq = (1 + port_ret).cumprod()
    years = len(eq) / BARS_PER_YEAR[IV]
    cagr = eq.iloc[-1] ** (1/years) - 1
    dd = (eq / eq.cummax() - 1).min()
    sharpe = port_ret.mean() / port_ret.std() * np.sqrt(BARS_PER_YEAR[IV]) if port_ret.std() > 0 else 0
    # Sortino
    downside = port_ret[port_ret < 0].std()
    sortino = port_ret.mean() / downside * np.sqrt(BARS_PER_YEAR[IV]) if downside > 0 else 0
    return dict(CAGR=cagr*100, MaxDD=dd*100, Sharpe=sharpe, Sortino=sortino, final=eq.iloc[-1])


# collect aligned sleeve returns
rets = pd.concat([sleeve_returns(s) for s in BASKET], axis=1).fillna(0.0)
print(f"Basket: {len(BASKET)} coins {IV}, {len(rets)} bars\n")

# per-sleeve annualised vol (for risk parity)
vol = rets.std() * np.sqrt(BARS_PER_YEAR[IV])

# weighting schemes
w_eq = pd.Series(1/len(BASKET), index=rets.columns)
w_rp = (1/vol) / (1/vol).sum()

for name, w in [("equal-weight", w_eq), ("risk-parity", w_rp)]:
    pr = (rets * w).sum(axis=1)
    m = port_metrics(pr)
    print(f"{name:12s} (1.0x): CAGR {m['CAGR']:7.2f}%  DD {m['MaxDD']:7.2f}%  Sharpe {m['Sharpe']:.2f}  Sortino {m['Sortino']:.2f}")

print("\n=== LEVERAGE SWEEP (risk-parity base) ===")
pr_base = (rets * w_rp).sum(axis=1)
for L in [1.0, 1.5, 2.0, 2.5, 3.0]:
    m = port_metrics(pr_base * L)
    print(f"  {L:.1f}x : CAGR {m['CAGR']:7.2f}%  DD {m['MaxDD']:7.2f}%  Sharpe {m['Sharpe']:.2f}  Sortino {m['Sortino']:.2f}")

print("\n=== LEVERAGE SWEEP (equal-weight base) ===")
pr_eq = (rets * w_eq).sum(axis=1)
for L in [1.0, 1.5, 2.0, 2.5, 3.0]:
    m = port_metrics(pr_eq * L)
    print(f"  {L:.1f}x : CAGR {m['CAGR']:7.2f}%  DD {m['MaxDD']:7.2f}%  Sharpe {m['Sharpe']:.2f}  Sortino {m['Sortino']:.2f}")

# find leverage that lands ~75% CAGR on risk-parity
print("\n=== TARGET ~70-80% CAGR (risk-parity) ===")
for L in np.arange(0.5, 3.05, 0.25):
    m = port_metrics(pr_base * L)
    if 68 <= m["CAGR"] <= 82:
        print(f"  {L:.2f}x : CAGR {m['CAGR']:6.2f}%  DD {m['MaxDD']:7.2f}%  Sharpe {m['Sharpe']:.2f}  Sortino {m['Sortino']:.2f}")
print("\nweights (risk-parity):")
print(w_rp.round(3).to_string())

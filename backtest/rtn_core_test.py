"""
RTN-Core test (Fable's one prescribed test).
Strategy: cross-sectional momentum ROTATION — each rebalance, rank the 25-coin
universe by trailing-return trend score, hold the TOP-8 equal-weight, gated by
BTC>MA regime (flat when off). Long-only, fees on turnover.

KEEP/KILL (Fable's rule):
  keep RTN-Core only if  standalone walk-forward OOS Sharpe > 0.86
                    AND  swapping it into the .55/.25/.20 blend lifts OOS > 1.28 (and > baseline blend).
Otherwise the rotational family is CLOSED.

Honest method: walk-forward picks the lookback param on TRAIN, applies OOS; blend
comparison is on the IDENTICAL OOS dates for trend-baseline vs RTN-Core (apples-to-apples).
Fees 0.1%+0.05% per side on rebalance turnover. Process on close (next-bar would be stricter;
kept consistent with the rest of the book so comparisons are valid).
"""
import numpy as np, pandas as pd
from pathlib import Path
from engine import load, backtest, BARS_PER_YEAR

DATA = Path(__file__).parent / "data"; IV = "4h"
COMM, SLIP = 0.001, 0.0005
COST = COMM + SLIP  # per side, applied to turnover

def have(s): return (DATA/f"{s}_bear_4h.csv").exists() and (DATA/f"{s}_4h.csv").exists()
UNIVERSE = [s for s in [
    "BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","LTCUSDT","DOGEUSDT",
    "DOTUSDT","ETCUSDT","FILUSDT","FTMUSDT","GALAUSDT","ICPUSDT","MANAUSDT","MATICUSDT","NEARUSDT","SANDUSDT",
    "UNIUSDT","XLMUSDT","AAVEUSDT","ALGOUSDT","ATOMUSDT"] if have(s)]

def merged(s):
    df = pd.concat([load(f"{s}_bear", IV, DATA), load(s, IV, DATA)])
    return df[~df.index.duplicated(keep="first")].sort_index()

print(f"Universe: {len(UNIVERSE)} coins")
M = {s: merged(s) for s in UNIVERSE}

# ---- daily close panel (resample 4h -> 1D last) ----
close = pd.DataFrame({s: M[s].close.resample("1D").last().ffill() for s in UNIVERSE}).dropna(how="all")
close = close.ffill()
ret1d = close.pct_change().fillna(0.0)
N = len(close)
bpy = 365  # daily

# ---- BTC regime: BTC close > its MA (gate) ----
def btc_regime(ma): return (close["BTCUSDT"] > close["BTCUSDT"].rolling(ma).mean())

def sharpe(pr):
    pr = pr.dropna()
    return pr.mean()/pr.std()*np.sqrt(bpy) if len(pr) > 20 and pr.std() > 0 else -9

def met(pr):
    pr = pr.fillna(0.0); eq = (1+pr).cumprod(); yrs = len(eq)/bpy
    cagr = eq.iloc[-1]**(1/yrs)-1 if eq.iloc[-1] > 0 else -1
    dd = (eq/eq.cummax()-1).min()
    return cagr*100, dd*100, sharpe(pr)

# ---- RTN-Core return stream for given (lookback, rebalance_days, regime_ma, top_k) ----
def rtn_stream(lb, reb, ma, top_k=8):
    score = close.pct_change(lb)               # trailing-return momentum score
    reg = btc_regime(ma)
    w = pd.DataFrame(0.0, index=close.index, columns=close.columns)
    last_w = pd.Series(0.0, index=close.columns)
    cur = pd.Series(0.0, index=close.columns)
    turn = pd.Series(0.0, index=close.index)
    for i, dt in enumerate(close.index):
        if i % reb == 0:  # rebalance day
            if reg.iloc[i] and i > lb:
                sc = score.iloc[i].dropna()
                top = sc.nlargest(top_k).index
                cur = pd.Series(0.0, index=close.columns)
                if len(top) > 0:
                    cur[top] = 1.0/len(top)
            else:
                cur = pd.Series(0.0, index=close.columns)  # regime off -> cash
            turn.iloc[i] = (cur - last_w).abs().sum()
            last_w = cur.copy()
        w.iloc[i] = cur.values
    # portfolio return: weights held from prior close earn today's return; minus turnover cost on reb days
    gross = (w.shift(1).fillna(0.0) * ret1d).sum(axis=1)
    fee = turn * COST
    return (gross - fee).rename(f"rtn_lb{lb}_rb{reb}_ma{ma}")

# ---- walk-forward the RTN lookback (honest OOS) ----
LB_GRID = [20, 30, 45, 60, 90]      # daily lookback candidates
REB, REG_MA, TOPK = 7, 50, 8        # weekly rebalance, BTC>50d MA regime, top-8
streams = {lb: rtn_stream(lb, REB, REG_MA, TOPK) for lb in LB_GRID}
S = pd.DataFrame(streams).fillna(0.0)

train_n, test_n, step = 365, 90, 90
idx = S.index; wf = []; picks = []
start = 0
while start + train_n + test_n <= N:
    tr = S.iloc[start:start+train_n]; te = S.iloc[start+train_n:start+train_n+test_n]
    best = max(LB_GRID, key=lambda lb: sharpe(tr[lb]))
    picks.append(best); wf.append(te[best])
    start += step
rtn_oos = pd.concat(wf)
oos_idx = rtn_oos.index

print(f"\nWalk-forward: train {train_n}d / test {test_n}d, {len(picks)} folds; lookbacks picked: {picks}")
c, d, sh = met(rtn_oos)
print(f"=== RTN-Core STANDALONE walk-forward OOS ===\n  CAGR {c:.1f}%  DD {d:.1f}%  Sharpe {sh:.2f}")
RTN_STANDALONE = sh

# ---- build the blend sleeves on the SAME daily grid (book_final method) ----
tcfg = dict(strat="donchian", entry=20, exit=10, risk=5, stop_mult=2.5, adx_filter=True, ma_filter=200)
trend = pd.concat([backtest(M[s], tcfg)[0].resample("1D").last().ffill().pct_change().rename(s)
                   for s in UNIVERSE], axis=1).fillna(0.0).mean(axis=1).reindex(close.index).fillna(0.0)

def flush_var(THR, TP, HOLD):
    def fc(s):
        df = M[s].resample("1D").last().ffill(); r = df.close.pct_change()
        sig = (r < THR); pos = pd.Series(0.0, index=df.index); h = 0
        for i in range(1, len(df)):
            if h > 0:
                pos.iloc[i] = 1.0; h -= 1
                if r.iloc[i] >= TP: h = 0
            if sig.iloc[i-1] and h == 0: h = HOLD; pos.iloc[i] = 1.0
        return (pos.shift(1).fillna(0)*r).fillna(0.0).rename(s)
    return pd.concat([fc(s) for s in UNIVERSE], axis=1).fillna(0.0).mean(axis=1).reindex(close.index).fillna(0.0)

def crash_var(THR, H2):
    def cc(s):
        df = M[s].resample("1D").last().ffill(); r = df.close.pct_change()
        sig = (r < THR); pos = pd.Series(0.0, index=df.index); h = 0
        for i in range(1, len(df)):
            if h > 0: pos.iloc[i] = 1.0; h -= 1
            if sig.iloc[i-1] and h == 0: h = H2; pos.iloc[i] = 1.0
        return (pos.shift(1).fillna(0)*r).fillna(0.0).rename(s)
    return pd.concat([cc(s) for s in UNIVERSE], axis=1).fillna(0.0).mean(axis=1).reindex(close.index).fillna(0.0)

flush2 = flush_var(-0.08, 0.05, 2)
crashreb = crash_var(-0.05, 3)

# ---- blend comparison on IDENTICAL OOS dates ----
base_blend = (0.55*trend + 0.25*flush2 + 0.20*crashreb)
rtn_blend  = (0.55*rtn_oos.reindex(close.index).fillna(0.0) + 0.25*flush2 + 0.20*crashreb)
bb_oos = base_blend.reindex(oos_idx).fillna(0.0)
rb_oos = rtn_blend.reindex(oos_idx).fillna(0.0)

cb, db, shb = met(bb_oos); cr, dr, shr = met(rb_oos)
print(f"\n=== BLEND on identical OOS dates (.55/.25/.20) ===")
print(f"  BASELINE (trend leg):   CAGR {cb:.1f}%  DD {db:.1f}%  Sharpe {shb:.2f}")
print(f"  RTN-Core swapped in:    CAGR {cr:.1f}%  DD {dr:.1f}%  Sharpe {shr:.2f}")

# correlation of RTN vs trend (Fable predicted high corr -> no diversification)
corr = pd.concat([rtn_oos, trend.reindex(oos_idx)], axis=1).fillna(0.0).corr().iloc[0,1]
print(f"  corr(RTN-Core, trend) on OOS: {corr:.2f}")

print("\n=== VERDICT (Fable keep/kill) ===")
k1 = RTN_STANDALONE > 0.86
k2 = (shr > 1.28) and (shr > shb)
print(f"  standalone OOS {RTN_STANDALONE:.2f} > 0.86 ?  {'PASS' if k1 else 'FAIL'}")
print(f"  blend lift {shr:.2f} > 1.28 and > baseline {shb:.2f} ?  {'PASS' if k2 else 'FAIL'}")
print(f"  --> {'KEEP + DEPLOY alongside' if (k1 and k2) else 'KILL — rotational family closed'}")

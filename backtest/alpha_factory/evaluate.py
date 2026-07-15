"""Per-factor evaluation: cross-sectional IC + decay, net quantile L/S, purged folds."""
import numpy as np
import pandas as pd


def daily_ic(factor, fwd):
    """Per-day cross-sectional Spearman IC (rank both sides, then row-wise Pearson)."""
    fr = factor.rank(axis=1)
    rr = fwd.rank(axis=1)
    return fr.corrwith(rr, axis=1)


def ic_stats(factor, close, horizons):
    out = {}
    for h in horizons:
        fwd = close.pct_change(h).shift(-h)          # forward h-day return
        ic = daily_ic(factor, fwd).dropna()
        out[f"ic_{h}"] = float(ic.mean())
        out[f"icir_{h}"] = float(ic.mean() / ic.std() * np.sqrt(len(ic))) if ic.std() > 0 else 0.0
        out["n_days"] = int(len(ic))
    return out


def ls_returns(factor, ret, k_frac, fee, slip, borrow_annual, dpy):
    """Dollar-neutral top-K/bottom-K L/S, executed next day, net of fee+slippage on
    turnover and borrow on the short leg."""
    n = factor.count(axis=1)
    k = np.maximum(2, (n * k_frac).astype(int))
    rk = factor.rank(axis=1, ascending=False)
    wl = rk.le(k, axis=0).astype(float)
    ws = rk.gt((n - k), axis=0).astype(float)
    wl = wl.div(wl.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    ws = ws.div(ws.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    w = wl - ws
    turn = w.diff().abs().sum(axis=1).fillna(0.0)
    gross = (w.shift(1).fillna(0.0) * ret).sum(axis=1)
    return gross - turn * (fee + slip) - ws.shift(1).fillna(0.0).sum(axis=1) * borrow_annual / dpy


def purged_folds(index, n_folds, embargo_days):
    """Contiguous OOS folds with an embargo gap dropped at each boundary."""
    blocks = np.array_split(np.arange(len(index)), n_folds)
    folds = []
    for i, b in enumerate(blocks):
        s = b[embargo_days:] if i > 0 else b        # drop embargo at the leading edge
        folds.append(index[s])
    return folds


def fold_sharpes(series, folds, dpy):
    out = []
    for f in folds:
        s = series.reindex(f).dropna()
        out.append(float(s.mean() / s.std() * np.sqrt(dpy)) if len(s) > 30 and s.std() > 0 else 0.0)
    return out

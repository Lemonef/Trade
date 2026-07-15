"""Incumbent book (the 5 alphas.py sleeves, panel-computable form) + improvement gate:
a survivor must make the WITH-ensemble beat the WITHOUT-ensemble out-of-sample."""
import numpy as np, pandas as pd
from . import ops
from .evaluate import ls_returns

def _flip_cost(pos, fee_slip):
    return pos.diff().abs().fillna(0.0) * fee_slip

def incumbent_sleeves(panel, cfg):
    px, ret = panel.close, panel.ret
    fee_slip = cfg.TAKER_FEE + cfg.SLIPPAGE
    ma200 = px.rolling(200).mean()
    # trend: long-only equal-weight when close > MA200 (panel form of the Donchian core's regime)
    pos = (px > ma200).astype(float)
    pos = pos.div(pos.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    trend = (pos.shift(1).fillna(0.0) * ret).sum(axis=1) - _flip_cost(pos, fee_slip).sum(axis=1)
    # xsmom 28d top/bottom 5 (alphas.py lines 44-48)
    m28 = px.pct_change(28); rk = m28.rank(axis=1, ascending=False); n = px.shape[1]
    wl = (rk <= 5).astype(float); ws = (rk >= n - 4).astype(float)
    wl = wl.div(wl.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    ws = ws.div(ws.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    turn = (wl - ws).diff().abs().sum(axis=1).fillna(0.0)
    xsmom = ((wl - ws).shift(1).fillna(0.0) * ret).sum(axis=1) - turn * cfg.TAKER_FEE - cfg.BORROW_ANNUAL / cfg.DPY
    # carry (alphas.py lines 53-56)
    fund = panel.funding.reindex(columns=px.columns).fillna(0.0)
    on = (fund.rolling(3).mean() > 0).astype(float)
    carry = (on.shift(1).fillna(0.0) * fund - on.diff().abs().fillna(0.0) * 0.0004).mean(axis=1)
    # rsi2 dip-in-trend (alphas.py lines 59-66)
    r2 = ops.rsi(px, 2); up = px > ma200
    p2 = pd.DataFrame(np.nan, index=px.index, columns=px.columns)
    p2[(up) & (r2 < 10)] = 1.0; p2[r2 > 50] = 0.0; p2 = p2.ffill().fillna(0.0)
    rsi2dip = (p2.shift(1).fillna(0.0) * ret - _flip_cost(p2, cfg.TAKER_FEE)).fillna(0.0).mean(axis=1)
    # tsmom (alphas.py lines 68-69)
    sig = (px.pct_change(28) > 0).astype(float).shift(1).fillna(0.0)
    sig = sig.div(sig.sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    tsmom = (sig * ret).sum(axis=1)
    return {"trend": trend, "xsmom": xsmom, "carry": carry, "rsi2dip": rsi2dip, "tsmom": tsmom}

def ensemble(sleeves):
    df = pd.DataFrame(sleeves).fillna(0.0)
    vol = df.std().replace(0, np.nan)
    w = (1 / vol) / (1 / vol).sum()
    return (df * w).sum(axis=1)

def _sharpe(s, dpy):
    s = s.dropna()
    return float(s.mean() / s.std() * np.sqrt(dpy)) if len(s) > 30 and s.std() > 0 else 0.0

def _maxdd(s):
    eq = (1 + s.fillna(0.0)).cumprod()
    return float((eq / eq.cummax() - 1).min())

def improvement(candidate_lsr, sleeves, cfg):
    df = pd.DataFrame(sleeves)
    corr = df.corrwith(candidate_lsr).abs()
    base = ensemble(sleeves)
    withc = ensemble({**sleeves, "candidate": candidate_lsr})
    cut = int(len(base) * cfg.OOS_SPLIT)
    b, w = base.iloc[cut:], withc.iloc[cut:]
    out = dict(max_corr=float(corr.max()), corr_by_sleeve=corr.round(2).to_dict(),
               base_oos_sharpe=_sharpe(b, cfg.DPY), with_oos_sharpe=_sharpe(w, cfg.DPY),
               base_maxdd=_maxdd(b), with_maxdd=_maxdd(w))
    out["delta_sharpe"] = out["with_oos_sharpe"] - out["base_oos_sharpe"]
    out["delta_maxdd"] = out["with_maxdd"] - out["base_maxdd"]
    out["redundant"] = out["max_corr"] > 0.9
    out["improves"] = out["delta_sharpe"] > 0 and not out["redundant"]
    return out

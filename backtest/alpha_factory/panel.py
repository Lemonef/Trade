"""Data panel: real CSVs (engine.load + alphas.py conventions) or synthetic GBM for tests."""
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from engine import load


@dataclass
class Panel:
    open: pd.DataFrame
    high: pd.DataFrame
    low: pd.DataFrame
    close: pd.DataFrame
    volume: pd.DataFrame
    funding: pd.DataFrame

    @property
    def ret(self):
        return self.close.pct_change().fillna(0.0)

    @property
    def coins(self):
        return list(self.close.columns)


def _merged(c, data_dir):
    df = pd.concat([load(f"{c}_bear", "4h", data_dir), load(c, "4h", data_dir)])
    return df[~df.index.duplicated(keep="first")].sort_index()


def build_panel(data_dir):
    data_dir = Path(data_dir)
    coins = sorted({p.stem[:-3] for p in data_dir.glob("*_4h.csv")
                    if not p.stem.endswith("_bear")
                    and (data_dir / f"{p.stem[:-3]}_bear_4h.csv").exists()})
    frames = {c: _merged(c, data_dir) for c in coins}
    agg = {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    daily = {k: pd.DataFrame({c: frames[c][k].resample("1D").agg(v) for c in coins}).dropna(how="all")
             for k, v in agg.items()}
    idx = daily["close"].index
    fund = {}
    for c in coins:
        fp = data_dir / f"{c}_funding.csv"
        if fp.exists():
            f = pd.read_csv(fp)
            f["dt"] = pd.to_datetime(f.fundingTime, unit="ms", utc=True)
            fund[c] = f.set_index("dt").fundingRate.astype(float).resample("1D").sum()
    funding = pd.DataFrame(fund).reindex(idx).fillna(0.0) if fund else pd.DataFrame(index=idx)
    return Panel(daily["open"], daily["high"], daily["low"], daily["close"], daily["volume"], funding)


def build_synth_panel(n_coins=8, n_days=800, seed=7, signal_strength=0.0):
    """GBM closes + derived OHLCV + funding noise. If signal_strength>0, a hidden score
    is mixed into NEXT-day returns and returned as the planted factor."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-01", periods=n_days, freq="D", tz="UTC")
    cols = [f"C{i:02d}USDT" for i in range(n_coins)]
    score = pd.DataFrame(rng.standard_normal((n_days, n_coins)), index=idx, columns=cols)
    noise = rng.standard_normal((n_days, n_coins)) * 0.02
    r = noise.copy()
    if signal_strength > 0:  # today's score moves TOMORROW's return
        r[1:] += signal_strength * 0.02 * score.values[:-1]
    close = pd.DataFrame(100 * np.exp(np.cumsum(r, axis=0)), index=idx, columns=cols)
    spread = np.abs(rng.standard_normal((n_days, n_coins))) * 0.005
    high = close * (1 + spread)
    low = close * (1 - spread)
    open_ = close.shift(1).fillna(close.iloc[0])
    volume = pd.DataFrame(1e6 * (1 + np.abs(rng.standard_normal((n_days, n_coins)))), index=idx, columns=cols)
    funding = pd.DataFrame(rng.standard_normal((n_days, n_coins)) * 1e-4, index=idx, columns=cols)
    return Panel(open_, high, low, close, volume, funding), score

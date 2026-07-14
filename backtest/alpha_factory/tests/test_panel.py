import numpy as np
import pandas as pd
from pathlib import Path


def _write_csv(p, start_ms, n, price0):
    rows = ["open_time,open,high,low,close,volume"]
    t, px = start_ms, price0
    for i in range(n):
        o = px
        c = px * (1 + 0.001 * ((i % 5) - 2))
        h = max(o, c) * 1.001
        l = min(o, c) * 0.999
        rows.append(f"{t},{o},{h},{l},{c},{100+i}")
        px = c
        t += 4 * 3600 * 1000
    p.write_text("\n".join(rows))


def test_build_panel_merges_and_resamples(tmp_path):
    from alpha_factory.panel import build_panel
    day0 = 1672531200000  # 2023-01-01
    bear0 = day0 - 60 * 24 * 3600 * 1000
    for c in ["AAAUSDT", "BBBUSDT"]:
        _write_csv(tmp_path / f"{c}_4h.csv", day0, 6 * 30, 100.0)
        _write_csv(tmp_path / f"{c}_bear_4h.csv", bear0, 6 * 70, 90.0)   # overlaps 10 days
    (tmp_path / "AAAUSDT_funding.csv").write_text(
        "fundingTime,fundingRate\n" + f"{day0},0.0001\n{day0 + 8*3600*1000},0.0002\n")
    p = build_panel(tmp_path)
    assert p.coins == ["AAAUSDT", "BBBUSDT"]
    assert not p.close.index.duplicated().any()
    assert p.close.index.tz is not None
    assert abs(p.funding["AAAUSDT"].loc["2023-01-01"] - 0.0003) < 1e-12  # same-day sum
    assert (p.high >= p.low).all().all()


def test_synth_panel_reproducible_and_planted():
    from alpha_factory.panel import build_synth_panel
    p1, f1 = build_synth_panel(seed=7, signal_strength=0.5)
    p2, f2 = build_synth_panel(seed=7, signal_strength=0.5)
    assert p1.close.equals(p2.close) and f1.equals(f2)
    # planted factor must predict next-day cross-sectional returns
    fwd = p1.close.pct_change().shift(-1)
    daily_corr = f1.rank(axis=1).corrwith(fwd.rank(axis=1), axis=1)
    assert daily_corr.mean() > 0.1
    p3, _ = build_synth_panel(seed=7, signal_strength=0.0)
    assert not p3.close.isna().all().any() and len(p3.close) == 800

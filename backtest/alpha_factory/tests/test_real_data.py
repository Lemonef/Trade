"""Validation #4 (spec): known-alpha anchors on REAL data. Auto-skips when data absent."""
import pytest
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"
pytestmark = pytest.mark.skipif(not (DATA / "BTCUSDT_4h.csv").exists(), reason="no real data")


def test_baseline_anchors():
    from alpha_factory.panel import build_panel
    from alpha_factory.bench import incumbent_sleeves, _sharpe
    from alpha_factory import config as cfg
    panel = build_panel(DATA)
    sleeves = incumbent_sleeves(panel, cfg)
    cut = int(len(panel.close) * cfg.OOS_SPLIT)
    oos = {k: _sharpe(v.iloc[cut:], cfg.DPY) for k, v in sleeves.items()}
    assert oos["carry"] > 0, f"carry must be positive OOS (documented finding), got {oos}"
    weak = sum(1 for k in ("xsmom", "rsi2dip", "tsmom") if oos[k] < 0.8)
    assert weak >= 2, f"most non-carry alphas are documented weak OOS, got {oos}"

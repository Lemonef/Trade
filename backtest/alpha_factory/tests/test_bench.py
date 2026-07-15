import numpy as np, pandas as pd
from alpha_factory.panel import build_synth_panel
from alpha_factory import config as cfg

def test_uncorrelated_edge_improves_book():
    from alpha_factory.bench import incumbent_sleeves, improvement
    from alpha_factory.evaluate import ls_returns
    panel, planted = build_synth_panel(seed=11, signal_strength=0.5)
    sleeves = incumbent_sleeves(panel, cfg)
    assert set(sleeves) == {"trend", "xsmom", "carry", "rsi2dip", "tsmom"}
    lsr = ls_returns(planted, panel.ret, cfg.K_FRAC, cfg.TAKER_FEE, cfg.SLIPPAGE, cfg.BORROW_ANNUAL, cfg.DPY)
    imp = improvement(lsr, sleeves, cfg)
    assert imp["improves"] and imp["delta_sharpe"] > 0 and not imp["redundant"]

def test_clone_of_incumbent_is_redundant():
    from alpha_factory.bench import incumbent_sleeves, improvement
    panel, _ = build_synth_panel(seed=11, signal_strength=0.5)
    sleeves = incumbent_sleeves(panel, cfg)
    clone = sleeves["xsmom"] * 1.0000001
    imp = improvement(clone, sleeves, cfg)
    assert imp["redundant"] and imp["max_corr"] > 0.99

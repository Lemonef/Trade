import numpy as np
import pandas as pd
from alpha_factory.panel import build_synth_panel
from alpha_factory import config as cfg


def test_planted_signal_has_positive_ic_and_noise_does_not():
    from alpha_factory.evaluate import ic_stats
    panel, planted = build_synth_panel(seed=11, signal_strength=0.5)
    s = ic_stats(planted, panel.close, (1, 5))
    assert s["ic_1"] > 0.10 and s["icir_1"] > 1.0
    rng = np.random.default_rng(0)
    noise = pd.DataFrame(rng.standard_normal(panel.close.shape),
                         index=panel.close.index, columns=panel.close.columns)
    sn = ic_stats(noise, panel.close, (1,))
    assert abs(sn["ic_1"]) < 0.05


def test_lookahead_factor_is_neutralized_by_shift():
    """A cheating factor (= same-day return) must show ~no NET edge once execution is shift(1)."""
    from alpha_factory.evaluate import ls_returns
    panel, _ = build_synth_panel(seed=5, signal_strength=0.0)
    cheat = panel.ret  # knows today's return "in advance"
    lsr = ls_returns(cheat, panel.ret, cfg.K_FRAC, cfg.TAKER_FEE, cfg.SLIPPAGE, cfg.BORROW_ANNUAL, cfg.DPY)
    sh = lsr.mean() / lsr.std() * np.sqrt(cfg.DPY)
    assert sh < 0.5  # no edge survives the one-day execution lag on iid noise


def test_planted_signal_makes_money_net_of_costs():
    from alpha_factory.evaluate import ls_returns
    panel, planted = build_synth_panel(seed=11, signal_strength=0.5)
    lsr = ls_returns(planted, panel.ret, cfg.K_FRAC, cfg.TAKER_FEE, cfg.SLIPPAGE, cfg.BORROW_ANNUAL, cfg.DPY)
    assert lsr.mean() / lsr.std() * np.sqrt(cfg.DPY) > 1.0


def test_purged_folds_disjoint_with_embargo():
    from alpha_factory.evaluate import purged_folds
    idx = pd.date_range("2023-01-01", periods=400, freq="D", tz="UTC")
    folds = purged_folds(idx, 4, 10)
    assert len(folds) == 4
    for a, b in zip(folds, folds[1:]):
        assert (b[0] - a[-1]).days > 10   # embargo gap
    assert sum(len(f) for f in folds) <= 400 - 3 * 10

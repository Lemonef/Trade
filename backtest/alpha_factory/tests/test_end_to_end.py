import pandas as pd
from alpha_factory import config as cfg

def test_factory_end_to_end_on_synthetic(tmp_path):
    from alpha_factory.panel import build_synth_panel
    from alpha_factory.zoo import build_zoo, Factor
    from alpha_factory.report import run_factory, render
    panel, planted = build_synth_panel(seed=11, signal_strength=0.6)
    zoo = build_zoo()[:20] + [Factor("planted", "test", "synthetic", lambda p: planted)]
    df = run_factory(panel, zoo, cfg)
    assert set(["name", "verdict", "reason", "dsr_prob"]).issubset(df.columns)
    row = df[df.name == "planted"].iloc[0]
    assert row.verdict == "SURVIVED" and row.improves_book in (True, False)
    md, csv = render(df, cfg, tmp_path, "TEST")
    text = md.read_text()
    assert "SURVIVED" in text and cfg.SURVIVORSHIP_CAVEAT[:40] in text
    assert csv.exists() and len(pd.read_csv(csv)) == len(df)

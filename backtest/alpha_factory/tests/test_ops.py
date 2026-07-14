def test_scaffold_imports():
    import alpha_factory.config as cfg
    assert cfg.FDR_Q == 0.10 and cfg.N_FOLDS == 4

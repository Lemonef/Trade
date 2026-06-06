"""Sanity-check engine against TradingView sweep numbers."""
from engine import load, backtest, metrics
from pathlib import Path

DATA = Path(__file__).parent / "data"

checks = [
    ("BTCUSDT", "4h", dict(strat="donchian", entry=20, exit=10, risk=5, stop_mult=2.0, adx_filter=True), "TV Donchian BTC 4H ~24.77%"),
    ("ETHUSDT", "4h", dict(strat="donchian", entry=20, exit=10, risk=5, stop_mult=2.0, adx_filter=True), "TV Donchian ETH 4H ~23.26%"),
    ("SOLUSDT", "4h", dict(strat="donchian", entry=20, exit=10, risk=5, stop_mult=2.0, adx_filter=True), "TV Donchian SOL 4H ~7.45%"),
    ("BTCUSDT", "4h", dict(strat="qb_hybrid", entry=20, exit=10, risk=5, stop_mult=2.5), "TV QB Hybrid BTC 4H ~27.81%"),
    ("SOLUSDT", "4h", dict(strat="meanrev", risk=5, stop_mult=2.5), "meanrev SOL (QB V1 range-ish)"),
]

for sym, iv, cfg, note in checks:
    df = load(sym, iv, DATA)
    eq, tr = backtest(df, cfg)
    m = metrics(eq, tr, iv)
    print(f"{sym} {iv} {cfg['strat']:9s} | CAGR {m['CAGR']:6.2f}%  DD {m['MaxDD']:6.2f}%  PF {m['PF']:.2f}  WR {m['WR']:.1f}%  n={m['n']:3d}  | {note}")

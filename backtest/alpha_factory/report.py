"""Orchestration + scoreboard rendering."""
from pathlib import Path
import numpy as np, pandas as pd
from . import config as _cfg
from .evaluate import ic_stats, ls_returns, purged_folds, fold_sharpes, daily_ic
from .stats import ic_pvalue, bh_fdr, deflated_sharpe_prob, verdict
from .bench import incumbent_sleeves, improvement

def run_factory(panel, zoo, cfg=_cfg, n_trials=None):
    n_trials = n_trials or len(zoo)
    folds = purged_folds(panel.close.index, cfg.N_FOLDS, cfg.EMBARGO_DAYS)
    rows = []
    for f in zoo:
        fac = f.fn(panel)
        s = ic_stats(fac, panel.close, cfg.HORIZONS)
        fwd1 = panel.close.pct_change().shift(-1)
        ic1 = daily_ic(fac, fwd1).dropna()
        lsr = ls_returns(fac, panel.ret, cfg.K_FRAC, cfg.TAKER_FEE, cfg.SLIPPAGE, cfg.BORROW_ANNUAL, cfg.DPY)
        fs = fold_sharpes(lsr, folds, cfg.DPY)
        sr = float(lsr.mean() / lsr.std() * np.sqrt(cfg.DPY)) if lsr.std() > 0 else 0.0
        rows.append(dict(name=f.name, family=f.family, provenance=f.provenance,
                         ic_1=s.get("ic_1", 0.0), icir_1=s.get("icir_1", 0.0),
                         ic_5=s.get("ic_5", 0.0), ic_20=s.get("ic_20", 0.0),
                         ic_decay=s.get(f"ic_{cfg.DECAY_CHECK_HORIZON}", 0.0),
                         n_days=s.get("n_days", 0), ls_sharpe=sr, fold_sharpes=fs,
                         pval=ic_pvalue(float(ic1.mean()), float(ic1.std()), len(ic1)),
                         dsr_prob=deflated_sharpe_prob(sr, len(lsr.dropna()), cfg.DPY,
                                                       float(lsr.skew() or 0), float(lsr.kurt() or 0), n_trials),
                         turnover=float(np.nan_to_num(lsr.abs().mean())), _lsr=lsr))
    keep = bh_fdr([r["pval"] for r in rows], cfg.FDR_Q)
    sleeves = incumbent_sleeves(panel, cfg)
    for r, k in zip(rows, keep):
        r["pval_pass"] = bool(k)
        r["verdict"], r["reason"] = verdict(r, cfg)
        if r["verdict"] == "SURVIVED":
            imp = improvement(r.pop("_lsr"), sleeves, cfg)
            r.update(max_corr=imp["max_corr"], delta_sharpe=round(imp["delta_sharpe"], 3),
                     delta_maxdd=round(imp["delta_maxdd"], 3), improves_book=imp["improves"])
            if imp["redundant"]:
                r["reason"] += " (REDUNDANT vs incumbent sleeve)"
        else:
            r.pop("_lsr"); r.update(max_corr=np.nan, delta_sharpe=np.nan,
                                    delta_maxdd=np.nan, improves_book=False)
    return pd.DataFrame(rows).sort_values(["verdict", "dsr_prob"], ascending=[False, False]).reset_index(drop=True)

def render(df, cfg, out_dir, stamp):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    md, csv = out_dir / f"ALPHA_FACTORY_{stamp}.md", out_dir / f"ALPHA_FACTORY_{stamp}.csv"
    df.drop(columns=[c for c in df.columns if c.startswith("_")], errors="ignore").to_csv(csv, index=False)
    surv = df[df.verdict == "SURVIVED"]
    cfg_dump = {k: getattr(cfg, k) for k in dir(cfg) if k.isupper() and k != "SURVIVORSHIP_CAVEAT"}
    lines = [f"# Alpha Factory scoreboard — {stamp}", "",
             f"> {cfg.SURVIVORSHIP_CAVEAT}", "", f"Config: `{cfg_dump}`",
             f"Factors tested: {len(df)} · SURVIVED: {len(surv)} · REJECTED: {len(df) - len(surv)}", "",
             "## SURVIVED (sorted by deflated-Sharpe probability)", "",
             "| factor | family | prov | IC1 | ICIR1 | LS Sharpe | folds | DSRp | maxCorr | ΔSharpe | ΔDD | IMPROVES BOOK |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in surv.iterrows():
        folds = "/".join(f"{x:.1f}" for x in r.fold_sharpes)
        lines.append(f"| {r['name']} | {r.family} | {r.provenance.split()[0]} | {r.ic_1:.3f} | {r.icir_1:.1f} | "
                     f"{r.ls_sharpe:.2f} | {folds} | {r.dsr_prob:.2f} | {r.max_corr:.2f} | "
                     f"{r.delta_sharpe:+.3f} | {r.delta_maxdd:+.3f} | {'YES' if r.improves_book else 'no'} |")
    lines += ["", "## REJECTED — count by reason", ""]
    for reason, n in df[df.verdict == "REJECTED"].reason.value_counts().items():
        lines.append(f"- {n:4d} × {reason}")
    lines += ["", f"Full per-factor table: `{csv.name}`", ""]
    md.write_text("\n".join(lines))
    return md, csv

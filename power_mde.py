#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post-hoc detectable effect size (MDE) and 95% CI for the primary M2 fit.

READS ONLY  results/04_deg_primary_M2.csv  (the pre-specified primary OLS M2).
WRITES ONLY results_power/ and tables/TableS13_*  -- results/ is never touched.

This answers statistical reviewer comment #6 of the second-round mock review:
"at least give a post-hoc detectable-effect interval so that non-significance
is not read as absence of effect".  It is a DESCRIPTIVE sensitivity analysis,
NOT an a-priori power calculation and NOT a test of equivalence.  The MDE is
derived from each probe's standard error and residual df, not from the
observed effect size, so it does not inherit the usual post-hoc-power fallacy.

Usage:  D:/anaconda3/python.exe power_mde.py
"""
import os
import numpy as np
import pandas as pd
from scipy.stats import t, nct
from scipy.optimize import brentq

ROOT = os.path.dirname(os.path.abspath(__file__))
PRIMARY = os.path.join(ROOT, "results", "04_deg_primary_M2.csv")
OUT = os.path.join(ROOT, "results_power")
TABD = os.path.join(ROOT, "tables")
SIX = ["FGFR1", "SMAD1", "STAT1", "TGFBR2", "CASP1", "CASP4"]
ALPHA = 0.05
TARGET_POWER = 0.80


def power_at(delta, se, df):
    """Two-sided t-test power for a true coefficient delta."""
    if se <= 0 or not np.isfinite(se) or df <= 0:
        return np.nan
    tc = t.ppf(1 - ALPHA / 2, df)
    ncp = delta / se
    return float(1 - nct.cdf(tc, df, ncp) + nct.cdf(-tc, df, ncp))


def mde_for(se, df):
    """Smallest |delta| detectable at TARGET_POWER, solved with the noncentral t."""
    if se <= 0 or not np.isfinite(se) or df <= 0:
        return np.nan
    hi = max(10.0 * se, 1e-3)
    while power_at(hi, se, df) < TARGET_POWER and hi < 1e4:
        hi *= 2
    return float(brentq(lambda d: power_at(d, se, df) - TARGET_POWER, 0.0, hi))


def se_crit_for(delta, df):
    """Largest se that still reaches TARGET_POWER for a given true effect."""
    lo, hi = 1e-5, 20.0
    if power_at(delta, lo, df) < TARGET_POWER:
        return np.nan
    return float(brentq(lambda s: power_at(delta, s, df) - TARGET_POWER, lo, hi))


def main():
    os.makedirs(OUT, exist_ok=True)
    d = pd.read_csv(PRIMARY, low_memory=False)
    d["se"] = pd.to_numeric(d["se"], errors="coerce")
    d["df_residual"] = pd.to_numeric(d["df_residual"], errors="coerce")
    d["log2FC"] = pd.to_numeric(d["log2FC"], errors="coerce")
    d["p"] = pd.to_numeric(d["p"], errors="coerce")

    # ---- platform-level: typical probe and fraction able to detect |log2FC|>=1 ----
    plat = []
    for name, g in d.groupby("platform_dataset", sort=True):
        se = g["se"].dropna()
        df = int(g["df_residual"].dropna().mode().iloc[0])
        se_med = float(se.median())
        crit = se_crit_for(1.0, df)
        plat.append({
            "platform_dataset": name,
            "n_probes": len(g),
            "df_residual": df,
            "se_median": round(se_med, 6),
            "mde_power80_typical_probe": round(mde_for(se_med, df), 6),
            "se_crit_for_absLFC1": round(crit, 6),
            "pct_probes_power80_at_absLFC1": round(100.0 * float((se <= crit).mean()), 2),
        })
    ptab = pd.DataFrame(plat)
    ptab.to_csv(os.path.join(OUT, "01_platform_mde.csv"), index=False)

    # ---- six genes: primary convention = probe with smallest nominal p ----
    s = d[d["gene"].isin(SIX)].copy()
    idx = s.groupby(["platform_dataset", "gene"])["p"].idxmin()
    sel = s.loc[idx].copy()
    rows = []
    for r in sel.itertuples(index=False):
        se, df, lfc = float(r.se), float(r.df_residual), float(r.log2FC)
        tc = t.ppf(0.975, df)
        mde = mde_for(se, df)
        rows.append({
            "platform_dataset": r.platform_dataset,
            "gene": r.gene,
            "probe": r.probe,
            "log2FC": round(lfc, 6),
            "se": round(se, 6),
            "df_residual": int(df),
            "p": float(r.p),
            "q_BH": float(r.q_BH),
            "ci95_low": round(lfc - tc * se, 6),
            "ci95_high": round(lfc + tc * se, 6),
            "mde_power80": round(mde, 6),
            "abs_log2FC_lt_mde": bool(abs(lfc) < mde),
            "interpretation": (
                "observed |log2FC| below MDE: non-significance cannot exclude a smaller effect"
                if abs(lfc) < mde else
                "observed |log2FC| above MDE: non-significance reflects multiplicity/variance, not lack of power"
            ),
        })
    gtab = pd.DataFrame(rows).sort_values(["platform_dataset", "gene"])
    gtab.to_csv(os.path.join(OUT, "02_six_genes_mde.csv"), index=False)

    # ---- manuscript-facing supplementary table ----
    gtab.to_csv(os.path.join(TABD, "TableS13_power_mde.tsv"), sep="\t", index=False)
    with open(os.path.join(TABD, "TableS13_power_mde.md"), "w", encoding="utf-8") as f:
        f.write("# Table S13. Post-hoc detectable effect size for the six transcripts (primary M2)\n\n")
        f.write("Descriptive sensitivity analysis derived from `results/04_deg_primary_M2.csv`; ")
        f.write("two-sided alpha = 0.05, target power = 0.80, noncentral-t solution using each probe's ")
        f.write("standard error and residual df. **Not** an a-priori power calculation and **not** a test ")
        f.write("of equivalence or absence of effect. Primary results are unchanged.\n\n")
        f.write("| Platform | Gene | log2FC | 95% CI | MDE (power 80%) | q_BH |\n|---|---|---:|---|---:|---:|\n")
        for r in gtab.itertuples(index=False):
            f.write("| %s | %s | %.3f | [%.3f, %.3f] | %.3f | %.3f |\n" % (
                r.platform_dataset, r.gene, r.log2FC, r.ci95_low, r.ci95_high,
                r.mde_power80, r.q_BH))
        f.write("\n## Platform-level summary\n\n")
        f.write("| Platform | Probes | Residual df | Median SE | Typical MDE | Probes with power>=80% at abs(log2FC)=1 |\n|---|---:|---:|---:|---:|---:|\n")
        for r in ptab.itertuples(index=False):
            f.write("| %s | %d | %d | %.4f | %.3f | %.2f%% |\n" % (
                r.platform_dataset, r.n_probes, r.df_residual, r.se_median,
                r.mde_power80_typical_probe, r.pct_probes_power80_at_absLFC1))

    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as f:
        f.write("# Post-hoc detectable effect size (MDE) - sensitivity only\n\n")
        f.write("- Input: `results/04_deg_primary_M2.csv` (69,513 probe-level primary M2 fits).\n")
        f.write("- Method: two-sided alpha=0.05, target power=0.80, solved with the noncentral t ")
        f.write("distribution from each probe's SE and residual df. MDE does **not** use the observed ")
        f.write("effect size, so it is not the classical post-hoc-power fallacy.\n")
        f.write("- Outputs: `01_platform_mde.csv`, `02_six_genes_mde.csv`, ")
        f.write("`tables/TableS13_power_mde.tsv|.md`.\n")
        f.write("- **Interpretation limit:** a non-significant BH q >= 0.05 in an underpowered, ")
        f.write("structurally imbalanced design is *not* evidence of no effect. If |log2FC| < MDE, ")
        f.write("the data cannot exclude a smaller true effect. Do not write 'no effect', 'equivalent' ")
        f.write("or 'confirmed negative' anywhere in the manuscript.\n")
        f.write("- `results/`, `results_m2b/`, `results_limma/` and all figures/tables 1-4 / S1-S12 ")
        f.write("are untouched. This is a NEW supplementary analysis, not a replacement of M2.\n")

    print("[PLATFORM]")
    print(ptab.to_string(index=False))
    print("\n[SIX GENES] %d rows; |log2FC| < MDE in %d / %d tests" % (
        len(gtab), int(gtab.abs_log2FC_lt_mde.sum()), len(gtab)))
    print(gtab[["platform_dataset", "gene", "log2FC", "ci95_low", "ci95_high",
                "mde_power80", "q_BH", "abs_log2FC_lt_mde"]].to_string(index=False))
    print("\n[OUTPUT] %s ; tables/TableS13_power_mde.{tsv,md}" % OUT)


if __name__ == "__main__":
    main()

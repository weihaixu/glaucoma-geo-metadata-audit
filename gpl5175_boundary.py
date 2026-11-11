#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Exploratory GSE45570 gene-level boundary check using the rebuilt GPL5175 map.

GEO has NO official GPL5175.annot.gz. This study rebuilt a probe -> gene symbol
map from the COMPLETE 316,919-row SOFT platform table (fetch_gpl5175_annot.py).
With that map, 17,634 / 22,011 (80.11%) GSE45570 transcript clusters can be
assigned to a gene, including 7 probes for the six prioritised transcripts.

WHAT THIS IS
  A boundary / sensitivity check written to results_gpl5175/. GSE45570 profiles
  WHOLE optic nerve head tissue, on a different platform, with a different case
  definition (an ocular-hypertension arm is excluded here). It CANNOT validate
  a finding about cultured ONH astrocytes and must never be called an
  independent replication. The primary results in results/, the 0/18 conclusion,
  Figures 1-2 and Tables 1-4 are untouched.

WHAT THIS IS NOT
  Not a negative result for unmapped probes, not a new primary model, not a
  meta-analysis, and not an input to the manuscript's abstract or conclusions.
"""
import gzip
import io
import json
import os

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "results_gpl5175")
MATRIX = os.path.join(ROOT, "GSE45570_series_matrix.txt.gz")
ANNOT = os.path.join(ROOT, "GPL5175.annot.gz")
SIX = ["FGFR1", "SMAD1", "STAT1", "TGFBR2", "CASP1", "CASP4"]
os.makedirs(OUT, exist_ok=True)


def read_series_matrix(path):
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    meta = {}
    for l in lines:
        if l.startswith("!Sample_"):
            p = l.split("\t")
            meta.setdefault(p[0], []).append([c.strip().strip('"') for c in p[1:]])
    i = next(k for k, l in enumerate(lines) if l.startswith("!series_matrix_table_begin"))
    j = next(k for k, l in enumerate(lines) if l.startswith("!series_matrix_table_end"))
    tbl = pd.read_csv(io.StringIO("\n".join(lines[i + 1:j])), sep="\t")
    tbl = tbl.rename(columns={tbl.columns[0]: "ID"})
    tbl["ID"] = tbl["ID"].astype(str).str.strip('"')
    return meta, tbl.set_index("ID")


def read_annot(path):
    mp = {}
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for l in f:
            if l.startswith("!") or l.startswith("ID\t"):
                continue
            c = l.rstrip("\r\n").split("\t")
            if len(c) >= 2 and c[0] and c[1]:
                mp[c[0]] = c[1]
    return mp


def ols_gene(y, X, df_resid):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    s2 = float(resid @ resid) / df_resid
    xtxi = np.linalg.inv(X.T @ X)
    se = np.sqrt(s2 * xtxi[1, 1])
    if se == 0 or not np.isfinite(se):
        return dict(log2FC=beta[1], se=np.nan, p=np.nan, ci_lo=np.nan, ci_hi=np.nan)
    t = beta[1] / se
    p = float(2 * stats.t.sf(abs(t), df_resid))
    crit = float(stats.t.ppf(0.975, df_resid))
    return dict(log2FC=float(beta[1]), se=float(se), p=p,
                ci_lo=float(beta[1] - crit * se), ci_hi=float(beta[1] + crit * se))


def main():
    meta, tbl = read_series_matrix(MATRIX)
    mp = read_annot(ANNOT)
    titles = meta["!Sample_title"][0]
    samples = [c for c in tbl.columns]
    assert len(titles) == len(samples), (len(titles), len(samples))

    def grp(t):
        tl = t.lower()
        if "oht" in tl or "ocular hypertension" in tl:
            return "excluded"
        if "poag" in tl or "glaucoma" in tl:
            return "glaucoma"
        if "control" in tl or "normal" in tl:
            return "control"
        return "unknown"

    groups = [grp(t) for t in titles]
    keep = [i for i, g in enumerate(groups) if g in ("glaucoma", "control")]
    used = [samples[i] for i in keep]
    y_glau = np.array([1.0 if groups[i] == "glaucoma" else 0.0 for i in keep])
    X = np.column_stack([np.ones(len(keep)), y_glau])
    df_resid = len(keep) - X.shape[1]

    E = tbl.loc[:, used].apply(pd.to_numeric, errors="coerce")
    sym = E.index.to_series().map(mp)
    mapped = E.assign(gene=sym.values).dropna(subset=["gene"])
    mapping = pd.DataFrame({"probe_id": E.index, "gene_symbol": sym.values,
                            "mapped": sym.notna().values})
    mapping.to_csv(os.path.join(OUT, "01_probe_mapping.csv"), index=False)

    # gene-level convention: per-sample median of all probes assigned to a gene
    G = mapped.groupby("gene").median(numeric_only=True)
    rows = []
    for g, vals in G.iterrows():
        r = ols_gene(vals.values.astype(float), X, df_resid)
        r.update({"gene": g, "n_probes": int((mapped["gene"] == g).sum())})
        rows.append(r)
    res = pd.DataFrame(rows)
    ok = res["p"].notna()
    res["q_BH"] = np.nan
    res.loc[ok, "q_BH"] = multipletests(res.loc[ok, "p"], method="fdr_bh")[1]
    res = res[["gene", "n_probes", "log2FC", "ci_lo", "ci_hi", "se", "p", "q_BH"]]
    res = res.sort_values("gene").reset_index(drop=True)
    res.to_csv(os.path.join(OUT, "02_gene_level_boundary.csv"), index=False,
               float_format="%.6g")

    six = res[res["gene"].isin(SIX)].copy()
    six["significant_q05"] = six["q_BH"] < 0.05
    six.to_csv(os.path.join(OUT, "03_six_gene_boundary.csv"), index=False,
               float_format="%.6g")

    # probe-level view for the seven six-gene probes that are present
    prows = []
    for pid, g in mp.items():
        if g in SIX and pid in E.index:
            r = ols_gene(E.loc[pid].values.astype(float), X, df_resid)
            r.update({"probe_id": pid, "gene": g})
            prows.append(r)
    pr = pd.DataFrame(prows)[["gene", "probe_id", "log2FC", "ci_lo", "ci_hi", "se", "p"]]
    pr = pr.sort_values(["gene", "probe_id"]).reset_index(drop=True)
    pr.to_csv(os.path.join(OUT, "04_six_gene_probes.csv"), index=False,
              float_format="%.6g")

    summary = {
        "purpose": "exploratory boundary check, NOT validation / replication",
        "annotation_source": "rebuilt from complete GPL5175 SOFT platform table; "
                             "GEO has no official GPL5175.annot.gz",
        "n_arrays_total": len(titles),
        "n_arrays_used": len(keep),
        "excluded_OHT_arrays": len(titles) - len(keep),
        "n_glaucoma": int((y_glau == 1).sum()), "n_control": int((y_glau == 0).sum()),
        "residual_df": df_resid,
        "n_matrix_probes": int(len(E)),
        "n_mapped_probes": int(sym.notna().sum()),
        "mapping_coverage_pct": round(100 * float(sym.notna().sum()) / len(E), 2),
        "n_genes_tested": int(len(res)),
        "n_six_gene_probes_in_matrix": int(len(pr)),
        "n_six_genes_significant_q05": int((six["q_BH"] < 0.05).sum()),
        "primary_results_modified": False,
        "interpretation": "whole ONH tissue, different platform and case definition; "
                          "cannot validate cultured ONH astrocyte findings; "
                          "unmapped probes are missing annotation, not negative results",
    }
    with open(os.path.join(OUT, "boundary_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write(
        "# GSE45570 gene-level boundary check (exploratory)\n\n"
        "Built from the **rebuilt** GPL5175 probe-to-gene map (complete SOFT "
        "platform table, 316,919 rows). GEO still has no official "
        "`GPL5175.annot.gz`.\n\n"
        "Files: `01_probe_mapping.csv`, `02_gene_level_boundary.csv` "
        "(gene = per-sample median of its probes; donor-level OLS "
        "`intercept + glaucoma`, BH across genes), `03_six_gene_boundary.csv`, "
        "`04_six_gene_probes.csv`, `boundary_summary.json`.\n\n"
        "**Boundary, not validation.** GSE45570 is whole ONH tissue on an exon "
        "array with a different case definition; the OHT arm is excluded. It "
        "cannot validate a finding about cultured ONH astrocytes, and it is not "
        "an independent replication. `results/`, the 0/18 conclusion, Figures "
        "1-2 and Tables 1-4 are untouched. Unmapped probes are missing "
        "annotation, never negative results.\n")
    print(json.dumps(summary, indent=2), flush=True)
    print("\nSix-gene gene-level results:", flush=True)
    print(six.to_string(index=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

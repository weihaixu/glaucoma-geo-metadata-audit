# -*- coding: utf-8 -*-
"""Round 9, task 2: gene-level sensitivity (removes "smallest-p probe" selection).

The primary M2 reports, for each of the six prioritised genes, the probe with
the smallest nominal p. That is a selection step and can inflate apparent
signal. Here three conventions are compared on the SAME real donor-level data
and the SAME design matrix:

  1. probe_min_p          - primary M2 convention (probe-level BH q)
  2. gene_median          - all probes of a gene collapsed to their per-donor
                            median log2 expression, then a fresh OLS + BH
                            across GENES (no probe selection at all)
  3. gene_simes            - Simes combination of the probe-level M2 p values
                            within a gene, then BH across genes

Outputs go to `results_genelevel/` and `tables/TableS11-S12`. The primary
`results/` directory is never written.
"""
import os
import sys

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import reanalysis as R  # noqa: E402
from run_limma_replication import load_primary_inputs, write_table  # noqa: E402

OUT = os.path.join(ROOT, "results_genelevel")
RESULTS = os.path.join(ROOT, "results")
SIX = R.SIX_GENES


def simes(p):
    """Simes combined p = min_i (m * p_(i) / i), p sorted ascending."""
    p = np.sort(np.asarray([x for x in p if np.isfinite(x)], dtype=float))
    if not len(p):
        return np.nan
    m = len(p)
    k = np.arange(1, m + 1)
    return float(np.min(m * p / k))


def bh(p):
    p = np.asarray(p, dtype=float)
    q = np.ones_like(p)
    ok = np.isfinite(p)
    q[ok] = multipletests(p[ok], method="fdr_bh")[1]
    return q


def main():
    os.makedirs(OUT, exist_ok=True)
    ds, prim = load_primary_inputs()
    prim["probe"] = prim["probe"].astype(str).str.strip()
    prim["gene"] = prim["gene"].astype(str).str.replace(r"^nan$", "", regex=True)
    gene_rows, summary, six_rows = [], [], []

    for name, d in sorted(ds.items()):
        de, X, ci, mapping = d["de"], d["X"], d["ci"], d["mapping"]
        psub = prim[prim.platform_dataset == name].copy()
        if mapping is None or not psub.gene.notna().any():
            for g in SIX:
                six_rows.append(dict(platform_dataset=name, gene=g,
                                     convention="probe_min_p", n_probes=0,
                                     log2FC=np.nan, p=np.nan, q_BH=np.nan,
                                     status="probe not mapped"))
                six_rows.append(dict(platform_dataset=name, gene=g,
                                     convention="gene_median", n_probes=0,
                                     log2FC=np.nan, p=np.nan, q_BH=np.nan,
                                     status="no gene annotation"))
                six_rows.append(dict(platform_dataset=name, gene=g,
                                     convention="gene_simes", n_probes=0,
                                     log2FC=np.nan, p=np.nan, q_BH=np.nan,
                                     status="no gene annotation"))
            summary.append(dict(platform_dataset=name, status="no gene annotation",
                                n_probes=len(psub), n_genes=0))
            print("%-22s SKIPPED (no gene annotation)" % name)
            continue

        # ---- convention 1: primary probe-level, smallest p per gene ----
        mapped = psub[psub.gene.ne("") & psub.gene.notna()]
        for g in SIX:
            s = mapped[mapped.gene == g]
            if not len(s):
                six_rows.append(dict(platform_dataset=name, gene=g,
                                     convention="probe_min_p", n_probes=0,
                                     log2FC=np.nan, p=np.nan, q_BH=np.nan,
                                     status="probe not mapped"))
                continue
            b = s.loc[s.p.idxmin()]
            six_rows.append(dict(platform_dataset=name, gene=g,
                                 convention="probe_min_p", n_probes=len(s),
                                 log2FC=b.log2FC, p=b.p, q_BH=b.q_BH, status="OK"))

        # ---- convention 2: median of all probes per gene, refit OLS ----
        gene_of_probe = dict(zip(mapped.probe, mapped.gene))
        keep = [p for p in de.index.astype(str) if p in gene_of_probe]
        E = de.loc[de.index.astype(str).isin(keep)].copy()
        E.index = [gene_of_probe[str(p)] for p in E.index]
        GE = E.groupby(level=0).median()      # genes x donors
        gt = R.ols_table(GE.values, X, ci, GE.index)
        gt.insert(0, "platform_dataset", name)
        gt = gt.rename(columns={"probe": "gene"})
        counts = E.groupby(level=0).size()
        gt["n_probes_aggregated"] = gt["gene"].map(counts).astype(int)
        gene_rows.append(gt)

        # ---- convention 3: Simes combination of probe-level M2 p values ----
        sp = mapped.groupby("gene")["p"].apply(simes).rename("p_simes")
        sq = pd.Series(bh(sp.values), index=sp.index, name="q_simes")
        npr = mapped.groupby("gene").size().rename("n_probes")
        simes_tab = pd.concat([sp, sq, npr], axis=1).reset_index()
        simes_tab.insert(0, "platform_dataset", name)
        simes_tab.to_csv(os.path.join(OUT, "simes_%s.csv" % name), index=False)

        for g in SIX:
            if g in GE.index:
                r = gt[gt.gene == g].iloc[0]
                six_rows.append(dict(platform_dataset=name, gene=g,
                                     convention="gene_median",
                                     n_probes=int(r.n_probes_aggregated),
                                     log2FC=r.log2FC, p=r.p, q_BH=r.q_BH, status="OK"))
            else:
                six_rows.append(dict(platform_dataset=name, gene=g,
                                     convention="gene_median", n_probes=0,
                                     log2FC=np.nan, p=np.nan, q_BH=np.nan,
                                     status="probe not mapped"))
            if g in sp.index:
                six_rows.append(dict(platform_dataset=name, gene=g,
                                     convention="gene_simes", n_probes=int(npr[g]),
                                     log2FC=np.nan, p=float(sp[g]), q_BH=float(sq[g]),
                                     status="OK"))
            else:
                six_rows.append(dict(platform_dataset=name, gene=g,
                                     convention="gene_simes", n_probes=0,
                                     log2FC=np.nan, p=np.nan, q_BH=np.nan,
                                     status="probe not mapped"))

        n_de_probe = int(((psub.q_BH < .05) & (psub.log2FC.abs() >= 1)).sum())
        n_de_gene = int(((gt.q_BH < .05) & (gt.log2FC.abs() >= 1)).sum())
        n_de_simes = int((simes_tab.q_simes < .05).sum())
        summary.append(dict(platform_dataset=name, status="OK",
                            n_probes=len(psub), n_genes=len(GE),
                            n_sig_genes_median=int(((gt.q_BH < .05) &
                                (gt.gene.isin(SIX))).sum()),
                            n_DE_probes_M2=n_de_probe,
                            n_DE_genes_median_M2=n_de_gene,
                            n_DE_genes_simes_p05=n_de_simes,
                            six_min_q_median=float(gt.loc[gt.gene.isin(SIX), "q_BH"].min()),
                            six_min_q_simes=float(simes_tab.loc[simes_tab.gene.isin(SIX), "q_simes"].min())))
        print("%-22s genes=%5d  DEG probes(M2)=%4d  DEG genes(median,M2)=%4d  "
              "six min q: median=%.4f simes=%.4f" %
              (name, len(GE), n_de_probe, n_de_gene,
               summary[-1]["six_min_q_median"], summary[-1]["six_min_q_simes"]))

    allg = pd.concat(gene_rows, ignore_index=True) if gene_rows else pd.DataFrame()
    allg.to_csv(os.path.join(OUT, "01_gene_level_deg.csv"), index=False)
    six = pd.DataFrame(six_rows)
    six["significant"] = np.where(six.q_BH.notna(), six.q_BH < .05, False)
    six.to_csv(os.path.join(OUT, "02_six_genes_three_conventions.csv"), index=False)
    summ = pd.DataFrame(summary)
    summ.to_csv(os.path.join(OUT, "03_dataset_summary.csv"), index=False)

    ok = six[six.status == "OK"]
    tab = ok.pivot_table(index=["platform_dataset", "gene"], columns="convention",
                         values="q_BH", aggfunc="first").reset_index()
    nsig = ok.groupby("convention").significant.sum().to_dict()
    allq = ok.q_BH.dropna()
    with open(os.path.join(OUT, "GENELEVEL_STATUS.md"), "w", encoding="utf-8") as fh:
        fh.write("# Gene-level sensitivity status\n\n")
        fh.write("- Same donor-level log2 matrices and design matrices as primary M2; "
                 "only the unit of testing changes (probe -> gene).\n")
        fh.write("- Three conventions: smallest-p probe (primary), per-donor median across "
                 "all probes of a gene with a fresh OLS + gene-level BH, and Simes "
                 "combination of probe-level p values with gene-level BH.\n")
        fh.write("- Six prioritised genes: significant results %s across conventions; "
                 "overall q range %.4f–%.4f.\n" % (nsig, allq.min(), allq.max()))
        fh.write("- Decision branch A is %s.\n" %
                 ("UNCHANGED" if sum(nsig.values()) == 0 else "CHANGED - REVIEW REQUIRED"))
        fh.write("- GSE45570 has no usable platform annotation (GPL5175 has no GEO "
                 "annot file), so gene-level testing is not possible there and it is "
                 "reported as `no gene annotation`, never as a negative result.\n")
        fh.write("- `results/`, `results_m2b/`, `results_diagnostics/`, "
                 "`results_limma/` were not written.\n")
    write_table(tab, "TableS11_genelevel_six_genes_q",
                "BH q for the six prioritised genes under three testing conventions. "
                "Blank = no probe mapped / no annotation. Significance threshold q<0.05.")
    write_table(summ, "TableS12_genelevel_DEG_counts",
                "Probe-level vs gene-level DEG counts at BH q<0.05 and |log2FC|>=1. "
                "Simes has no fold-change filter and is reported as a p-based check only.")

    print("\n=== BH q for six genes (three conventions) ===")
    print(tab.to_string(index=False, float_format=lambda x: "%.4f" % x))
    print("\nsignificant by convention:", nsig)
    print("BRANCH A:", "UNCHANGED" if sum(nsig.values()) == 0 else "CHANGED")
    print("wrote results_genelevel/ + TableS11/S12")


if __name__ == "__main__":
    main()

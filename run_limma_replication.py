# -*- coding: utf-8 -*-
"""Round 9, task 1: independent limma replication of the primary M2 model.

The primary M2 in `results/04_deg_primary_M2.csv` was fitted probe-wise with
ordinary least squares (Python). Here we export EXACTLY the same donor-level
log2 expression matrix and design matrix to R, run limma's lmFit + eBayes
(empirical-Bayes variance moderation), and reconcile every probe back against
the primary OLS result.

Strict guards:
  * A reconstructed Python OLS must reproduce the primary log2FC/se to 1e-8
    BEFORE anything is exported. If not, the script aborts.
  * limma logFC must match the reconstructed OLS beta to 1e-8.
  * Nothing is written into `results/`, `results_m2b/` or `results_diagnostics/`.

Outputs: `results_limma/` (inputs, per-probe reconciliation, six-gene table,
dataset summary, status note, R sessionInfo) and `tables/TableS9-S10`.
"""
import glob
import os
import subprocess
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import reanalysis as R  # noqa: E402

RESULTS = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "results_limma")
INDIR = os.path.join(OUT, "inputs")
TABLES = os.path.join(ROOT, "tables")
RSCRIPT = os.environ.get("RSCRIPT", r"C:\Program Files\R\R-4.2.0\bin\x64\Rscript.exe")
RLIB = os.path.join(ROOT, "Rlib")
SIX = R.SIX_GENES


def write_table(df, name, note=""):
    os.makedirs(TABLES, exist_ok=True)
    df.to_csv(os.path.join(TABLES, name + ".tsv"), sep="\t", index=False)
    with open(os.path.join(TABLES, name + ".md"), "w", encoding="utf-8") as fh:
        fh.write("**%s**\n\n" % name.replace("_", " "))
        if note:
            fh.write(note.strip() + "\n\n")
        fh.write(df.to_markdown(index=False) + "\n")


def load_primary_inputs():
    prim = pd.read_csv(os.path.join(RESULTS, "04_deg_primary_M2.csv"), low_memory=False)
    # Affymetrix exon probe IDs are numeric; pandas may infer int64. The GEO
    # matrix and the annot file both carry them as strings, so normalise once.
    prim["probe"] = prim["probe"].astype(str).str.strip()
    wanted = set(prim.platform_dataset.unique())
    qc = pd.read_csv(os.path.join(RESULTS, "02_qc_summary.csv"))
    scales = dict(zip(qc.platform_dataset, qc.scale_used.astype(str)))
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "*series_matrix*.txt.gz"))):
        name = os.path.basename(f).replace("_series_matrix.txt.gz", "")
        if name not in wanted:
            continue
        expr, meta = R.read_series_matrix(f)
        md_all = R.build_metadata(meta, expr, name)
        keep = md_all["group"].isin(["glaucoma", "control"]).values
        expr_a = expr.loc[:, keep] if keep.sum() < len(keep) else expr
        md_a = md_all.loc[keep].reset_index(drop=True) if keep.sum() < len(keep) else md_all
        sm = scales.get(name, "log2")
        el, _ = R.ensure_log2(expr_a, sm)
        de, dm = R.collapse_to_donor(el, md_a)
        adjusted_ok = (dm["race"] != "UNKNOWN").sum() >= len(dm) * 0.8
        X, ci, labs = R.make_design(dm, adjust=adjusted_ok)
        # map platform to its own annotation (identical to reanalysis.main)
        gpl = str(md_all["platform"].mode().iat[0]) if len(md_all) else "GPL_UNKNOWN"
        annot = os.path.join(ROOT, gpl + ".annot.gz")
        mapping = R.read_annot(annot) if os.path.exists(annot) else None
        out[name] = dict(de=de, dm=dm, X=X, ci=ci, labs=labs,
                         adjusted_ok=adjusted_ok, scale=sm, mapping=mapping,
                         annot=os.path.basename(annot) if mapping else "MISSING")
    missing = wanted - set(out)
    if missing:
        raise RuntimeError("primary datasets without a source matrix: %s" % sorted(missing))
    return out, prim


def main():
    os.makedirs(INDIR, exist_ok=True)
    ds, prim = load_primary_inputs()
    recon = []
    for name, d in sorted(ds.items()):
        de, dm, X, ci, labs = d["de"], d["dm"], d["X"], d["ci"], d["labs"]
        # Guard 1: reconstruct the primary OLS from the matrix we are about to export.
        chk = R.ols_table(de.values, X, ci, de.index)
        chk["probe"] = chk["probe"].astype(str).str.strip()
        ref = prim[prim.platform_dataset == name].set_index("probe")
        if set(chk.probe) != set(ref.index):
            print("  DEBUG prim n=%d recon n=%d example prim=%s recon=%s" %
                  (len(ref), len(chk), list(ref.index[:3]), list(chk.probe[:3])))
            raise RuntimeError("probe set mismatch for %s" % name)
        j = ref.loc[chk.probe.values]
        e1 = float(np.abs(chk.log2FC.values - j.log2FC.values).max())
        e2 = float(np.abs(chk.se.values - j.se.values).max())
        print("%-22s reconstructed OLS max|dlog2FC|=%.3g max|dse|=%.3g" % (name, e1, e2))
        if e1 > 1e-8 or e2 > 1e-8:
            raise RuntimeError("exported matrix does not reproduce primary M2 for %s" % name)
        chk.insert(0, "platform_dataset", name)
        recon.append(chk)
        # Export sample-safe identifiers so R never mangles donor keys.
        samples = ["S%04d" % (i + 1) for i in range(len(dm))]
        E = de.copy()
        E.index = E.index.astype(str).str.strip()
        E.columns = samples
        E.index.name = "probe"
        E.to_csv(os.path.join(INDIR, "expr_%s.tsv" % name), sep="\t")
        D = pd.DataFrame(X, columns=labs)
        D.insert(0, "sample", samples)
        D.to_csv(os.path.join(INDIR, "design_%s.tsv" % name), sep="\t", index=False)
        pd.DataFrame({"sample": samples, "donor_key": de.columns,
                      "group": dm["group"].values, "race": dm["race"].values}).to_csv(
            os.path.join(INDIR, "donormap_%s.tsv" % name), sep="\t", index=False)
        print("   exported %d probes x %d donors, design=%s" % (len(E), len(samples), ",".join(labs)))
    recon = pd.concat(recon, ignore_index=True)

    if not os.path.exists(RSCRIPT):
        raise RuntimeError("Rscript not found: %s" % RSCRIPT)
    if not os.path.isdir(RLIB):
        raise RuntimeError("project R library missing: run setup_rlib.R first")
    env = os.environ.copy()
    env["R_LIBS"] = RLIB
    env["LC_ALL"] = "C"
    cmd = [RSCRIPT, "--vanilla", os.path.join(ROOT, "limma_replication.R"), INDIR, OUT]
    print("\nrunning:", " ".join(cmd[1:]))
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=900)
    print(r.stdout[-4000:])
    if r.returncode != 0:
        print(r.stderr[-4000:])
        raise RuntimeError("limma replication failed (exit %d)" % r.returncode)

    lim = []
    for f in sorted(glob.glob(os.path.join(OUT, "limma_*.tsv"))):
        if os.path.basename(f) == "limma_fit_summary.tsv":
            continue  # R writes its own fit summary; not a probe table
        t = pd.read_csv(f, sep="\t")
        t["probe"] = t["probe"].astype(str).str.strip()
        name = os.path.basename(f).replace("limma_", "").replace(".tsv", "")
        t.insert(0, "platform_dataset", name)
        lim.append(t)
    lim = pd.concat(lim, ignore_index=True)
    # Gene symbols come from the primary table, which was annotated from each
    # platform's own annot file in reanalysis.main(); no re-annotation here.
    gmap = prim.set_index(["platform_dataset", "probe"])["gene"].to_dict()
    lim["gene"] = [gmap.get((d, p)) for d, p in zip(lim.platform_dataset, lim.probe)]

    # Guard 2: limma logFC == primary OLS beta.
    m = lim.merge(recon[["platform_dataset", "probe", "log2FC", "se", "t", "p", "q_BH"]],
                  on=["platform_dataset", "probe"], how="inner",
                  suffixes=("_limma", "_ols"))
    dmax = float(np.abs(m.logFC - m.log2FC).max())
    print("\nlimma vs primary OLS: %d probes, max|dlogFC|=%.3g" % (len(m), dmax))
    if dmax > 1e-8:
        raise RuntimeError("limma coefficients differ from primary OLS")

    full = m[["platform_dataset", "probe", "gene", "log2FC", "logFC", "se", "se_ols",
              "t", "t_mod", "p", "p_mod", "q_BH", "q_BH_mod",
              "df_residual", "df_prior", "df_total", "s2_prior", "s2_post", "sigma_ols"]]
    full.to_csv(os.path.join(OUT, "01_probe_reconciliation.csv"), index=False)

    # Six genes, primary "smallest nominal p probe" convention, both engines.
    rows = []
    for name, d in ds.items():
        if not d["mapping"]:
            for g in SIX:
                rows.append(dict(platform_dataset=name, gene=g, n_probes=0,
                                 status="probe not mapped", probe="", log2FC=np.nan,
                                 p_ols=np.nan, q_ols=np.nan, p_limma=np.nan,
                                 q_limma=np.nan, t_limma=np.nan))
            continue
        sub = full[(full.platform_dataset == name) & full.gene.isin(SIX)]
        for g in SIX:
            s = sub[sub.gene == g]
            if len(s) == 0:
                rows.append(dict(platform_dataset=name, gene=g, n_probes=0,
                                 status="probe not mapped", probe="", log2FC=np.nan,
                                 p_ols=np.nan, q_ols=np.nan, p_limma=np.nan,
                                 q_limma=np.nan, t_limma=np.nan))
                continue
            b = s.loc[s.p.idxmin()]       # same probe-selection rule as six_gene_rows()
            rows.append(dict(platform_dataset=name, gene=g, n_probes=len(s),
                             status="OK", probe=b.probe, log2FC=b.log2FC,
                             p_ols=b.p, q_ols=b.q_BH, p_limma=b.p_mod,
                             q_limma=b.q_BH_mod, t_limma=b.t_mod))
    six = pd.DataFrame(rows)
    six["sig_ols"] = np.where(six.q_ols.notna(), six.q_ols < .05, False)
    six["sig_limma"] = np.where(six.q_limma.notna(), six.q_limma < .05, False)
    six.to_csv(os.path.join(OUT, "02_six_genes_limma_vs_ols.csv"), index=False)

    # Dataset-level DEG counts under both engines, same thresholds as M2/M3.
    summ = []
    fit = pd.read_csv(os.path.join(OUT, "limma_fit_summary.tsv"), sep="\t")
    for name in sorted(ds):
        o = m[m.platform_dataset == name]
        r = dict(platform_dataset=name, n_probes=len(o),
                 n_donors=int(fit.loc[fit.dataset == name, "n_samples"].iat[0]),
                 df_residual=float(o.df_residual.iat[0]),
                 df_prior=float(o.df_prior.iat[0]),
                 df_total=float(o.df_total.iat[0]),
                 s2_prior=float(o.s2_prior.iat[0]),
                 median_sigma_ols=float(o.sigma_ols.median()),
                 max_abs_dlogFC=float(np.abs(o.logFC - o.log2FC).max()),
                 n_q05_lfc1_ols=int(((o.q_BH < .05) & (o.log2FC.abs() >= 1)).sum()),
                 n_q05_lfc1_limma=int(((o.q_BH_mod < .05) & (o.logFC.abs() >= 1)).sum()),
                 n_q05_lfc05_ols=int(((o.q_BH < .05) & (o.log2FC.abs() >= .5)).sum()),
                 n_q05_lfc05_limma=int(((o.q_BH_mod < .05) & (o.logFC.abs() >= .5)).sum()))
        summ.append(r)
    summ = pd.DataFrame(summ)
    summ.to_csv(os.path.join(OUT, "03_dataset_summary.csv"), index=False)

    ok = six[six.status == "OK"]
    n_sig_o, n_sig_l = int(ok.sig_ols.sum()), int(ok.sig_limma.sum())
    qrange = (float(ok.q_limma.min()), float(ok.q_limma.max()))
    with open(os.path.join(OUT, "LIMMA_STATUS.md"), "w", encoding="utf-8") as fh:
        fh.write("# limma replication status\n\n")
        fh.write("- R 4.2.0, limma 3.52.4 (Bioconductor 3.15 Windows binary), "
                 "statmod 1.5.0; installed into project-local `Rlib/`.\n")
        fh.write("- `lmFit(method=\"ls\") -> eBayes(trend=FALSE, robust=FALSE) -> "
                 "topTable(coef=\"glaucoma\", adjust.method=\"BH\")`.\n")
        fh.write("- Input matrices reproduce the primary M2 OLS exactly "
                 "(max |dlog2FC| = %.3g, max |dse| = 1e-8 tolerance); limma logFC "
                 "matches OLS beta to %.3g.\n" % (dmax, dmax))
        fh.write("- Six originally prioritised genes: **%d/%d** significant under primary "
                 "OLS and **%d/%d** under limma (BH q<0.05); limma q range %.3f–%.3f.\n"
                 % (n_sig_o, len(ok), n_sig_l, len(ok), qrange[0], qrange[1]))
        fh.write("- Decision branch A is %s.\n" %
                 ("UNCHANGED" if n_sig_l == 0 else "CHANGED - REVIEW REQUIRED"))
        fh.write("- `results/`, `results_m2b/` and `results_diagnostics/` were not written.\n")
    write_table(six[["platform_dataset", "gene", "n_probes", "probe", "log2FC",
                     "p_ols", "q_ols", "p_limma", "q_limma", "t_limma",
                     "sig_ols", "sig_limma", "status"]],
                "TableS9_limma_vs_OLS_six_genes",
                "Same probe-selection convention (smallest nominal p in the primary OLS) "
                "for both engines. BH across all probes on each platform.")
    write_table(summ, "TableS10_limma_DEG_counts",
                "M2 threshold: BH q<0.05 and |log2FC|>=1; M3 threshold: "
                "BH q<0.05 and |log2FC|>=0.5. Prior df/s2 from eBayes.")

    print("\n=== six genes ===")
    print(ok[["platform_dataset", "gene", "q_ols", "q_limma", "sig_ols", "sig_limma"]]
          .to_string(index=False, float_format=lambda x: "%.4f" % x))
    print("\n=== DEG counts ===")
    print(summ[["platform_dataset", "n_q05_lfc1_ols", "n_q05_lfc1_limma",
                "n_q05_lfc05_ols", "n_q05_lfc05_limma", "df_prior", "df_total"]]
          .to_string(index=False))
    print("\nBRANCH A:", "UNCHANGED" if n_sig_l == 0 else "CHANGED")
    print("wrote results_limma/ + TableS9/S10")


if __name__ == "__main__":
    main()

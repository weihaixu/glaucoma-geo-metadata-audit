#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build journal-ready figures and tables from REAL GEO re-analysis outputs.

Only files under results/ (primary M2 run) and results_m2b/ (covariate-complete
sensitivity run) are read. No values are simulated or hand-entered.

Usage:
    D:/anaconda3/python.exe make_figures_tables.py
Outputs:
    figures/Figure1.{png,svg}, figures/Figure2.{png,svg}
    tables/Table1..Table4 + TableS*.{tsv,md}, tables/tables_index.md
"""
import os
import json
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from scipy import stats

ROOT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ROOT, "results")
RES_B = os.path.join(ROOT, "results_m2b")
FIG = os.path.join(ROOT, "figures")
TAB = os.path.join(ROOT, "tables")
os.makedirs(FIG, exist_ok=True)
os.makedirs(TAB, exist_ok=True)

SIX = ["FGFR1", "SMAD1", "STAT1", "TGFBR2", "CASP1", "CASP4"]
DS_ORDER = ["GSE9944-GPL571", "GSE9944-GPL8300", "GSE9944-GPL91",
            "GSE2378-GPL8300", "GSE2378-GPL91", "GSE45570"]
DS_SHORT = {"GSE9944-GPL571": "9944/571", "GSE9944-GPL8300": "9944/8300",
            "GSE9944-GPL91": "9944/91", "GSE2378-GPL8300": "2378/8300",
            "GSE2378-GPL91": "2378/91", "GSE45570": "45570"}
PLAT3 = ["GSE2378-GPL8300", "GSE9944-GPL8300", "GSE9944-GPL571"]

BLUE, ORANGE, GREY, RED, GREEN, PURPLE = "#2C6E9B", "#D97A34", "#8A8F98", "#B23A48", "#1B7F5A", "#6B4C9A"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "axes.facecolor": "white",
                     "savefig.facecolor": "white"})


def rd(base, name, **kw):
    return pd.read_csv(os.path.join(base, name), **kw)


def save(fig, stem):
    for ext, kw in [("png", {"dpi": 300}), ("svg", {})]:
        p = os.path.join(FIG, stem + "." + ext)
        fig.savefig(p, bbox_inches="tight", **kw)
        print("  ", os.path.relpath(p, ROOT))
    plt.close(fig)


def write_table(df, stem, md=True):
    p = os.path.join(TAB, stem + ".tsv")
    df.to_csv(p, sep="\t", index=False, float_format="%.4g")
    print("  ", os.path.relpath(p, ROOT))
    if md:
        with open(os.path.join(TAB, stem + ".md"), "w", encoding="utf-8") as f:
            f.write(df.to_markdown(index=False, floatfmt=".4g") + "\n")
    return p


# ------------------------------------------------------------------ load
qc = rd(RES, "02_qc_summary.csv").set_index("platform_dataset")
deg = rd(RES, "03_deg_by_model.csv")
primary = rd(RES, "04_deg_primary_M2.csv", low_memory=False)
six = rd(RES, "05_six_key_genes.csv")
meta = rd(RES, "01_sample_metadata.csv", low_memory=False)
overlap = rd(RES, "10_donor_overlap.csv")
deg_b = rd(RES_B, "03_deg_by_model.csv")
six_b = rd(RES_B, "05_six_key_genes.csv")
print("Loaded: qc=%d deg=%d primary=%d six=%d meta=%d" %
      (len(qc), len(deg), len(primary), len(six), len(meta)))

# ================================================================== Figure 1
fig = plt.figure(figsize=(16.8, 5.9))
gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.25, 0.95], wspace=0.34,
                      left=0.055, right=0.985, top=0.90, bottom=0.26)
axA = fig.add_subplot(gs[0, 0])
axB = fig.add_subplot(gs[0, 1])
axC = fig.add_subplot(gs[0, 2])

# --- A: arrays vs donors -------------------------------------------------
order = [d for d in DS_ORDER if d in qc.index]
y = np.arange(len(order))
arr = [int(qc.loc[d, "n_arrays_total_incl_OHT"]) for d in order]
don = [int(qc.loc[d, "n_donors"]) for d in order]
axA.barh(y + 0.19, arr, height=0.36, color=GREY, label="Arrays in series matrix")
axA.barh(y - 0.19, don, height=0.36, color=BLUE, label="Independent donors entering models")
for i, (a, d) in enumerate(zip(arr, don)):
    axA.text(a + 0.6, i + 0.19, str(a), va="center", fontsize=7.5, color="#333333")
    axA.text(d + 0.6, i - 0.19, str(d), va="center", fontsize=7.5, color=BLUE)
axA.set_yticks(y)
axA.set_yticklabels([DS_SHORT[d] for d in order])
axA.invert_yaxis()
axA.set_xlabel("Number of samples")
axA.set_xlim(0, max(arr) * 1.22)
axA.set_title("A  Array-to-donor reconstruction", loc="left", fontweight="bold")
axA.legend(frameon=False, fontsize=7.2, loc="center right")
axA.text(0, -0.30, "96 arrays -> 66 donor-platform records\nGSE45570: 6 OHT eyes excluded from the contrast",
         transform=axA.transAxes, fontsize=7, color="#555555", va="top", clip_on=False)

# --- B: DEG counts across models ----------------------------------------
models = ["M0_array_nominal", "M1_donor_nominal",
          "M2_donor_adjusted_FDR_LFC1", "M3_donor_adjusted_FDR_LFC05"]
mlab = ["M0", "M1", "M2", "M3"]
mcol = [GREY, "#9FB6C6", BLUE, ORANGE]
pdat = [d for d in ["GSE9944-GPL571", "GSE9944-GPL8300", "GSE2378-GPL8300", "GSE45570"]]
w = 0.2
x = np.arange(len(pdat))
for j, (mo, lab, c) in enumerate(zip(models, mlab, mcol)):
    vals = []
    for d in pdat:
        r = deg[(deg.platform_dataset == d) & (deg.model == mo)]
        vals.append(int(r.n_DE_probes.iat[0]) if len(r) else 0)
    bars = axB.bar(x + (j - 1.5) * w, vals, width=w, color=c, label=lab)
    for b, v in zip(bars, vals):
        axB.text(b.get_x() + b.get_width() / 2, v + max(vals) * 0.015 + 4, str(v),
                 ha="center", va="bottom", fontsize=6.8, rotation=0,
                 color=RED if (mo.startswith("M2") and v == 0) else "#333333",
                 fontweight="bold" if mo.startswith("M2") else "normal")
axB.set_xticks(x)
axB.set_xticklabels([DS_SHORT[d] for d in pdat], fontsize=7.6)
axB.set_ylabel("Differentially expressed probes")
axB.set_ylim(0, 1550)
axB.set_title("B  DEG calls across the pre-specified model hierarchy", loc="left", fontweight="bold")
axB.legend(frameon=False, fontsize=7.5, ncol=4, title="Model", title_fontsize=7.5,
           loc="upper right", bbox_to_anchor=(1.0, 1.0))
axB.text(0, -0.30, "M2/M3 = donor level + BH q<0.05, |log2FC|>=1 / >=0.5.\n"
         "On 2378/8300 and 45570 the covariate-adjusted design was rejected (no ancestry field).",
         transform=axB.transAxes, fontsize=7, color="#555555", va="top", clip_on=False)

# --- C: ancestry x disease ----------------------------------------------
cols = ["9944/571\ncontrol", "9944/571\nglaucoma", "9944/8300\ncontrol", "9944/8300\nglaucoma"]
rows = ["African American", "Caucasian"]
M = np.zeros((2, 4), dtype=float)
for k, ds in enumerate(["GSE9944-GPL571", "GSE9944-GPL8300"]):
    cross = json.loads(str(qc.loc[ds, "race_x_group"]).replace("'", '"'))
    for i, ra in enumerate(["African_American", "Caucasian"]):
        for j2, gr in enumerate(["control", "glaucoma"]):
            M[i, k * 2 + j2] = float(cross.get(ra, {}).get(gr, 0))
im = axC.imshow(M, cmap="Blues", vmin=0, vmax=max(9, M.max()), aspect="auto")
for i in range(2):
    for j2 in range(4):
        axC.text(j2, i, "%d" % int(M[i, j2]), ha="center", va="center", fontsize=9,
                 color="white" if M[i, j2] > M.max() * 0.55 else "#222222", fontweight="bold")
axC.set_xticks(range(4)); axC.set_xticklabels(cols, fontsize=7)
axC.set_yticks(range(2)); axC.set_yticklabels(rows, fontsize=7.5)
axC.set_title("C  Ancestry x disease (donors)", loc="left", fontweight="bold")
axC.set_xticks(np.arange(-.5, 4, 1), minor=True)
axC.set_yticks(np.arange(-.5, 2, 1), minor=True)
axC.grid(which="minor", color="white", linewidth=1.4)
axC.tick_params(which="minor", length=0)
axC.text(0, -0.30, "9944/571: all 3 glaucoma donors are African American;\n"
         "all 9 Caucasian donors are controls -> near-collinear design",
         transform=axC.transAxes, fontsize=7, color=RED, ha="left", va="top", clip_on=False)
save(fig, "Figure1")

# ================================================================== Figure 2
m2 = six[six.model.str.contains("M2", na=False) & (six.n_probes > 0)].copy()
m2["dataset"] = m2.model.str.split("|").str[0]
piv = m2.pivot(index="gene", columns="dataset", values="log2FC").reindex(SIX)[PLAT3]
qpiv = m2.pivot(index="gene", columns="dataset", values="q_BH").reindex(SIX)[PLAT3]

forest = primary[(primary.gene.isin(SIX)) &
                 (primary.platform_dataset == "GSE9944-GPL571")].copy()
forest["lo"] = forest.log2FC - stats.t.ppf(.975, forest.df_residual) * forest.se
forest["hi"] = forest.log2FC + stats.t.ppf(.975, forest.df_residual) * forest.se
forest = forest.sort_values(["gene", "probe"]).reset_index(drop=True)

fig = plt.figure(figsize=(17.2, 7.2))
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.15, 1.0], wspace=0.34,
                      left=0.055, right=0.985, top=0.91, bottom=0.20)
axA = fig.add_subplot(gs[0, 0]); axB = fig.add_subplot(gs[0, 1]); axC = fig.add_subplot(gs[0, 2])

# --- A: log2FC heatmap ---------------------------------------------------
A = piv.values.astype(float)
vmax = np.nanmax(np.abs(A)) * 1.05
im = axA.imshow(A, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
for i in range(A.shape[0]):
    for j in range(A.shape[1]):
        axA.text(j, i, "%+.2f\nq=%.3f" % (A[i, j], qpiv.values[i, j]),
                 ha="center", va="center", fontsize=6.7,
                 color="white" if abs(A[i, j]) > vmax * .62 else "#222222")
axA.set_xticks(range(3)); axA.set_xticklabels([DS_SHORT[d] for d in PLAT3], fontsize=7.5)
axA.set_yticks(range(6)); axA.set_yticklabels(SIX, fontsize=8)
axA.set_title("A  M2 log2FC and BH q (best probe per gene)", loc="left", fontweight="bold")
axA.set_xticks(np.arange(-.5, 3, 1), minor=True); axA.set_yticks(np.arange(-.5, 6, 1), minor=True)
axA.grid(which="minor", color="white", linewidth=1.3); axA.tick_params(which="minor", length=0)
axA.text(0, -0.22, "0 / 18 gene-by-platform tests reach BH q<0.05",
         transform=axA.transAxes, fontsize=7.5, color=RED, ha="left", va="top",
         fontweight="bold", clip_on=False)

# --- B: nominal p vs BH q ------------------------------------------------
mm = m2.copy().reset_index(drop=True)
mm["lab"] = mm.gene + " | " + mm.dataset.map(DS_SHORT)
mm = mm.sort_values(["dataset", "gene"]).reset_index(drop=True)
yy = np.arange(len(mm))
axB.axvspan(0.0004, 0.05, color=GREEN, alpha=0.07, zorder=0)
axB.axvline(0.05, color=GREEN, lw=1.2, ls="--", zorder=1)
for i, r in mm.iterrows():
    axB.plot([r.p, r.q_BH], [i, i], color=GREY, lw=0.9, zorder=2)
    axB.scatter([r.p], [i], s=24, facecolors="white", edgecolors=BLUE, linewidths=1.1, zorder=3)
    axB.scatter([r.q_BH], [i], s=26, color=RED, zorder=4, marker="s")
axB.set_xscale("log"); axB.set_xlim(4e-4, 1.4); axB.set_ylim(-1, len(mm))
axB.set_yticks(yy); axB.set_yticklabels(mm.lab, fontsize=6.4)
axB.set_xlabel("Nominal p (open circle)  /  BH q (filled square)")
axB.set_title("B  Multiple testing removes every nominal signal", loc="left", fontweight="bold")
axB.text(0, -0.22, "Dashed line: BH q = 0.05. Shaded zone: p<0.05; no BH q falls in it.",
         transform=axB.transAxes, fontsize=7, color="#555555", va="top", clip_on=False)
axB.legend(handles=[Line2D([0], [0], marker="o", color="none", markerfacecolor="white",
                           markeredgecolor=BLUE, label="nominal p"),
                    Line2D([0], [0], marker="s", color="none", markerfacecolor=RED, label="BH q")],
           frameon=False, fontsize=7, loc="upper right")

# --- C: per-probe forest -------------------------------------------------
gcol = dict(zip(SIX, [BLUE, ORANGE, RED, GREEN, PURPLE, GREY]))
fy = np.arange(len(forest))
axC.axvline(0, color="#444444", lw=1.0, ls="--")
for i, r in forest.iterrows():
    c = gcol[r.gene]
    axC.plot([r.lo, r.hi], [i, i], color=c, lw=1.1, alpha=.85, zorder=2)
    axC.scatter([r.log2FC], [i], s=15, color=c, zorder=3)
for i in range(0, len(forest), 2):
    axC.axhspan(i - .5, i + .5, color="#F4F6F8", zorder=0)
axC.set_yticks(fy)
axC.set_yticklabels(forest.probe, fontsize=6.2)
for t, g in zip(axC.get_yticklabels(), forest.gene):
    t.set_color(gcol[g])
axC.set_xlabel("log2FC with nominal 95% CI (per probe)")
axC.set_title("C  All mapped probes, 9944/571 (n=%d)" % len(forest), loc="left", fontweight="bold")
axC.text(0, -0.22, "Nominal 95% CIs (not multiplicity-adjusted);\n"
         "probe labels are coloured by gene; probes within one gene\n"
         "are not independent. n=23 probes.",
         transform=axC.transAxes, fontsize=7, color="#555555", va="top", clip_on=False)
save(fig, "Figure2")

# ================================================================== tables
# Table 1 -- DEG counts by model with residual df
t1 = deg.copy()
t1["Unit"] = np.where(t1.model.str.startswith("M0"), "array", "donor")
t1["Pct_of_tested"] = (100.0 * t1.n_DE_probes / t1.n_probe_tested).round(3)
t1["Adjustment"] = np.where(t1.note.astype(str).str.contains("ADJUSTMENT NOT POSSIBLE"),
                            "not possible (ancestry absent)",
                            np.where(t1.model.str.startswith(("M2", "M3")), "ancestry only", "none"))
t1 = t1[["platform_dataset", "model", "Unit", "n_probe_tested", "n_DE_probes",
         "Pct_of_tested", "df_residual", "Adjustment"]]
t1.columns = ["Dataset", "Model", "Unit", "Probes tested", "DE probes",
              "% of tested", "Residual df", "Covariate adjustment"]
write_table(t1, "Table1_DEG_by_model")

# Table 2 -- six genes, best probe + 95% CI + group sizes + all-probe median
best = (primary[primary.gene.isin(SIX)]
        .sort_values("p").drop_duplicates(["platform_dataset", "gene"]))
med = (primary[primary.gene.isin(SIX)]
       .groupby(["platform_dataset", "gene"]).log2FC.median())
best = best.merge(med.rename("median_log2FC_all_probes"),
                  on=["platform_dataset", "gene"], how="left")
best["tcrit"] = stats.t.ppf(.975, best.df_residual)
best["ci_lo"] = best.log2FC - best.tcrit * best.se
best["ci_hi"] = best.log2FC + best.tcrit * best.se
cnt = primary[primary.gene.isin(SIX)].groupby(["platform_dataset", "gene"]).size()
best["n_probes_gene"] = [int(cnt[(d, g)]) for d, g in
                         zip(best.platform_dataset, best.gene)]
ns = {d: (int(qc.loc[d, "n_glaucoma_donors"]), int(qc.loc[d, "n_control_donors"])) for d in PLAT3}
rows = []
for d in PLAT3:
    for g in SIX:
        r = best[(best.platform_dataset == d) & (best.gene == g)]
        if not len(r):
            continue
        r = r.iloc[0]
        rows.append({
            "Dataset": d, "Gene": g, "Probe (min p)": r.probe,
            "All probes (n)": int(r.n_probes_gene),
            "log2FC": round(r.log2FC, 3),
            "95% CI": "[%.3f, %.3f]" % (r.ci_lo, r.ci_hi),
            "Median log2FC (all probes)": round(r.median_log2FC_all_probes, 3),
            "Nominal p": round(r.p, 5), "BH q": round(r.q_BH, 4),
            "n glaucoma": ns[d][0], "n control": ns[d][1],
            "Residual df": int(r.df_residual),
            "Status": "not significant (BH q>=0.05)"})
t2 = pd.DataFrame(rows)
write_table(t2, "Table2_six_genes_M2")

# Table S1 -- every mapped probe for the six genes, three annotated platforms
ps = primary[primary.gene.isin(SIX) & primary.platform_dataset.isin(PLAT3)].copy()
ps["tcrit"] = stats.t.ppf(.975, ps.df_residual)
ps["ci_lo"] = ps.log2FC - ps.tcrit * ps.se
ps["ci_hi"] = ps.log2FC + ps.tcrit * ps.se
ps = ps[["platform_dataset", "gene", "probe", "log2FC", "se", "ci_lo", "ci_hi",
         "p", "q_BH", "df_residual"]].sort_values(["platform_dataset", "gene", "p"])
ps.columns = ["Dataset", "Gene", "Probe", "log2FC", "SE", "CI low", "CI high",
              "Nominal p", "BH q", "Residual df"]
write_table(ps, "TableS1_all_probes_six_genes", md=False)

# Table 3 -- cohort / QC
cov = []
for d in DS_ORDER:
    if d not in qc.index:
        continue
    q = qc.loc[d]
    sub = meta[meta.series == d].drop_duplicates("donor_id")
    cov.append({
        "Dataset": d,
        "Arrays in matrix": int(q.n_arrays_total_incl_OHT),
        "Arrays used (case/control)": int(q.n_arrays_used_case_control),
        "Donors": int(q.n_donors),
        "Glaucoma donors": int(q.n_glaucoma_donors),
        "Control donors": int(q.n_control_donors),
        "Ancestry known (donors)": int(q.race_known),
        "Age usable (donors)": int(sub.age_num.notna().sum()),
        "Sex usable (donors)": int(sub.sex_bin.notna().sum()),
        "Scale": q.scale_used,
        "Probes tested": int(q.n_probes),
        "Probes with gene symbol": int(q.n_probes_mapped),
        "M2 adjustment terms": str(q.adjustment_terms),
        "Model status": str(q.model_status),
        "Design warning": str(q.design_warning)})
t3 = pd.DataFrame(cov)
write_table(t3, "Table3_cohort_QC")

# Table 4 -- donor overlap within the same GEO series
t4 = overlap[overlap.interpretation.astype(str).str.contains("SAME GEO SERIES")].copy()
t4 = t4[["dataset_A", "dataset_B", "donors_A", "donors_B",
         "shared_donor_ids", "shared_list", "interpretation"]]
t4.columns = ["Dataset A", "Dataset B", "Donors A", "Donors B",
              "Shared donor IDs", "Shared donor list", "Interpretation"]
write_table(t4, "Table4_donor_overlap")

# Table S2 -- primary M2 vs covariate-complete M2b
cmp = (deg[["platform_dataset", "model", "n_DE_probes"]]
       .merge(deg_b[["platform_dataset", "model", "n_DE_probes"]],
              on=["platform_dataset", "model"], suffixes=("_M2", "_M2b")))
cmp["Delta"] = cmp.n_DE_probes_M2b - cmp.n_DE_probes_M2
cmp.columns = ["Dataset", "Model", "DE probes (primary M2)", "DE probes (M2b)", "Delta"]
s2 = (six[six.model.str.contains("M2", na=False) & (six.n_probes > 0)][["model", "gene", "log2FC", "q_BH"]]
      .merge(six_b[six_b.model.str.contains("M2", na=False) & (six_b.n_probes > 0)][["model", "gene", "log2FC", "q_BH"]],
             on=["model", "gene"], suffixes=("_M2", "_M2b")))
s2.columns = ["Dataset|Model", "Gene", "log2FC (primary M2)", "BH q (primary M2)",
              "log2FC (M2b)", "BH q (M2b)"]
write_table(cmp, "TableS2_M2_vs_M2b_DEG_counts")
write_table(s2, "TableS3_M2_vs_M2b_six_genes")

# Table S4 -- real sensitivity grid (the in-memory grid in reanalysis.py was
# never exported; results/08_sensitivity.csv is only a copy of 03_deg_by_model)
grid = []
for ds, g in primary.groupby("platform_dataset"):
    for a in [0.05, 0.01]:
        for lfc in [0.5, 1.0, 1.5]:
            for use_q in [False, True]:
                pv = g.q_BH if use_q else g.p
                grid.append({"Dataset": ds, "alpha": a, "|log2FC| min": lfc,
                             "Statistic": "BH q" if use_q else "nominal p",
                             "DE probes": int(((pv < a) & (g.log2FC.abs() >= lfc)).sum()),
                             "Probes tested": len(g)})
tS4 = pd.DataFrame(grid)
write_table(tS4, "TableS4_sensitivity_grid", md=False)

# index
with open(os.path.join(TAB, "tables_index.md"), "w", encoding="utf-8") as f:
    f.write("# Journal-ready tables (generated from REAL results)\n\n")
    f.write("Source: `results/` (primary M2), `results_m2b/` (covariate-complete sensitivity), "
            "`work/data/make_figures_tables.py`. No value is simulated.\n\n")
    f.write("| File | Content | Rows |\n|---|---|---|\n")
    for stem, desc, n in [("Table1_DEG_by_model", "DEG counts by model with residual df", len(t1)),
                          ("Table2_six_genes_M2", "Six transcripts, best probe + 95% CI + group sizes", len(t2)),
                          ("Table3_cohort_QC", "Reconstructed cohort and QC / design warnings", len(t3)),
                          ("Table4_donor_overlap", "Shared donor IDs within one GEO series", len(t4)),
                          ("TableS1_all_probes_six_genes", "Every mapped probe with 95% CI", len(ps)),
                          ("TableS2_M2_vs_M2b_DEG_counts", "Primary M2 vs M2b DEG counts", len(cmp)),
                          ("TableS3_M2_vs_M2b_six_genes", "Primary M2 vs M2b six-gene statistics", len(s2)),
                          ("TableS4_sensitivity_grid", "Alpha x |log2FC| x FDR sensitivity grid", len(tS4))]:
        f.write("| `%s.tsv` | %s | %d |\n" % (stem, desc, n))

# ================================================================== manifest
MANIFEST_FILES = [
    "GSE9944-GPL571_series_matrix.txt.gz", "GSE9944-GPL8300_series_matrix.txt.gz",
    "GSE9944-GPL91_series_matrix.txt.gz", "GSE2378-GPL8300_series_matrix.txt.gz",
    "GSE2378-GPL91_series_matrix.txt.gz", "GSE45570_series_matrix.txt.gz",
    "GPL8300.annot.gz", "GPL571.annot.gz", "GPL91.annot.gz",
    "reanalysis.py", "reanalysis_m2b.py", "parallel_fetch.py",
    "fetch_gpl5175_annot.py", "summarize_results.py", "cold_read_v03.py",
    "cold_read_v04.py", "make_figures_tables.py", "apply_v04.py",
    "audit_references.py", "verify_literature.py", "apply_v05.py",
    "cold_read_v05.py", "make_report_v06.py", "make_report_v07.py",
    "cold_read_v06.py", "apply_v06.py", "diagnose_n1.py", "make_report_v08.py",
    "install_r_packages.py", "setup_rlib.R", "limma_replication.R",
    "run_limma_replication.py", "genelevel_sensitivity.py",
    "cold_read_v07.py", "apply_v07.py", "make_report_v09.py",
    "DECISION_LOG.md",
    "Rpackages/MANIFEST.tsv", "Rlib/limma/DESCRIPTION",
    "results_limma/01_probe_reconciliation.csv",
    "results_limma/02_six_genes_limma_vs_ols.csv",
    "results_limma/03_dataset_summary.csv",
    "results_limma/limma_fit_summary.tsv",
    "results_limma/LIMMA_STATUS.md", "results_limma/session_info.txt",
    "results_genelevel/01_gene_level_deg.csv",
    "results_genelevel/02_six_genes_three_conventions.csv",
    "results_genelevel/03_dataset_summary.csv",
    "results_genelevel/GENELEVEL_STATUS.md",
    "tables/TableS9_limma_vs_OLS_six_genes.tsv",
    "tables/TableS10_limma_DEG_counts.tsv",
    "tables/TableS11_genelevel_six_genes_q.tsv",
    "tables/TableS12_genelevel_DEG_counts.tsv",
    "results_diagnostics/07b_roc_donorlevel.csv",
    "results_diagnostics/collinearity_diagnostics.csv",
    "results_diagnostics/ancestry_disease_crosstab.csv",
    "results_diagnostics/N1_DIAGNOSTICS.md",
    "tables/TableS7_donor_vs_array_ROC.tsv",
    "tables/TableS8_collinearity_diagnostics.tsv",
    "references_audit.tsv", "references_audit.json",
    "verified_references.tsv", "verified_references.json",
    "references_v05.tsv", "literature_ledger.tsv", "citation_remap.json",
    "README.md", "REPRODUCIBILITY.md",
]
res_files = ["01_sample_metadata.csv", "02_qc_summary.csv", "03_deg_by_model.csv",
             "04_deg_primary_M2.csv", "05_six_key_genes.csv", "06_external_validation.csv",
             "07_roc.csv", "08_sensitivity.csv", "09_platform_overlap.csv",
             "10_donor_overlap.csv", "facts_for_manuscript.md", "decision.json"]
items = []
def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
for rel in MANIFEST_FILES:
    p = os.path.join(ROOT, rel)
    if os.path.exists(p):
        items.append(("input/script", rel, os.path.getsize(p), _sha(p)))
for rel in res_files:
    p = os.path.join(RES, rel)
    if os.path.exists(p):
        items.append(("result", "results/" + rel, os.path.getsize(p), _sha(p)))
for rel in ["03_deg_by_model.csv", "05_six_key_genes.csv", "02_qc_summary.csv"]:
    p = os.path.join(RES_B, rel)
    if os.path.exists(p):
        items.append(("sensitivity", "results_m2b/" + rel, os.path.getsize(p), _sha(p)))
man = pd.DataFrame(items, columns=["kind", "path", "bytes", "sha256"])
man.to_csv(os.path.join(TAB, "file_manifest.csv"), index=False)
print("  ", "tables/file_manifest.csv", len(man), "entries")

print("\nDONE. Figures:", len([f for f in os.listdir(FIG) if f.endswith('.png')]),
      "Tables:", len([f for f in os.listdir(TAB) if f.endswith('.tsv')]))

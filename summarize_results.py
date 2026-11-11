#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Turn results/*.csv into one auditable fact sheet for manuscript back-filling.

Every number written into the v0.3 manuscript must come from this file, never
from memory or from _selftest_results/.
"""
import json
import os
import sys
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
RES = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "results")
OUT = os.path.join(RES, "facts_for_manuscript.md")


def rd(name):
    p = os.path.join(RES, name)
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()


qc, deg, six, ev = rd("02_qc_summary.csv"), rd("03_deg_by_model.csv"), rd("05_six_key_genes.csv"), rd("06_external_validation.csv")
ov, meta, sens = rd("09_platform_overlap.csv"), rd("01_sample_metadata.csv"), rd("08_sensitivity.csv")
don = rd("10_donor_overlap.csv")

L = []
L.append("# Facts for manuscript back-filling (auto-generated)\n")
L.append("> Source: `results/*.csv` from `reanalysis.py` on REAL GEO series matrices. "
         "`_selftest_results/` is synthetic and must never be cited.\n")

L.append("\n## 1. Design / QC (02_qc_summary.csv)\n")
if len(qc):
    L.append("| dataset | arrays | donors | groups | ancestry x group | scale | annotation | design warning |")
    L.append("|---|---|---|---|---|---|---|---|")
    for _, r in qc.iterrows():
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r.get("platform_dataset"), r.get("n_arrays"), r.get("n_donors"),
            r.get("groups"), r.get("race_x_group"), r.get("scale_used"),
            r.get("annotation_file"), r.get("design_warning")))

L.append("\n## 2. DEG counts by model (03_deg_by_model.csv)\n")
if len(deg):
    L.append("| dataset | model | n DE probes | probes tested | residual df | note |")
    L.append("|---|---|---|---|---|---|")
    for _, r in deg.iterrows():
        L.append("| %s | %s | %s | %s | %s | %s |" % (
            r.get("platform_dataset"), r.get("model"), r.get("n_DE_probes"),
            r.get("n_probe_tested"), r.get("df_residual"), str(r.get("note", ""))[:70]))

L.append("\n## 3. Six originally prioritized genes, primary M2 model (05_six_key_genes.csv)\n")
m2 = six[six["model"].str.contains("M2", na=False)] if len(six) else pd.DataFrame()
if len(m2):
    L.append("| dataset | gene | probes | log2FC | nominal p | BH q | status |")
    L.append("|---|---|---|---|---|---|---|")
    for _, r in m2.iterrows():
        def f(x):
            try:
                return "%.4g" % float(x)
            except Exception:
                return "NA"
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r["model"].split("|")[0], r["gene"], r["n_probes"],
            f(r["log2FC"]), f(r["p"]), f(r["q_BH"]), r["status"]))
    mapped = m2[m2["n_probes"] > 0]
    nsig = int((mapped["q_BH"] < .05).sum())
    L.append("\n- Mapped gene x dataset tests: **%d**; with BH q<0.05: **%d**." % (len(mapped), nsig))

L.append("\n## 4. External comparison (06_external_validation.csv)\n")
if len(ev):
    L.append("| dataset | gene | probes | log2FC | p | BH q | AUC | 95% CI | perm p | status |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for _, r in ev.iterrows():
        def f(x):
            try:
                return "%.3g" % float(x)
            except Exception:
                return "NA"
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s-%s | %s | %s |" % (
            r.get("dataset"), r.get("gene"), r.get("n_probes"), f(r.get("log2FC")),
            f(r.get("p")), f(r.get("q_BH")), f(r.get("auc")), f(r.get("auc_ci_lo")),
            f(r.get("auc_ci_hi")), f(r.get("auc_perm_p")), r.get("status")))

L.append("\n## 5. Donor overlap across matrices (10_donor_overlap.csv)\n")
if len(don):
    L.append("| A | B | donors A | donors B | shared | interpretation |")
    L.append("|---|---|---|---|---|---|")
    for _, r in don.iterrows():
        L.append("| %s | %s | %s | %s | %s | %s |" % (
            r.get("dataset_A"), r.get("dataset_B"), r.get("donors_A"),
            r.get("donors_B"), r.get("shared_donor_ids"), str(r.get("interpretation"))[:90]))

L.append("\n## 6. Automatic decision-tree branch\n")
branch = "UNDETERMINED"
if len(m2):
    mapped = m2[m2["n_probes"] > 0]
    nsig = int((mapped["q_BH"] < .05).sum())
    m2deg = deg[deg["model"].str.contains("M2", na=False)] if len(deg) else pd.DataFrame()
    total_m2 = int(m2deg["n_DE_probes"].sum()) if len(m2deg) else -1
    if nsig == 0:
        branch = "A"
    elif nsig <= 2:
        branch = "B"
    elif nsig >= 3:
        branch = "C"
    if total_m2 >= 0 and total_m2 < 20:
        branch = "D (DEG counts collapsed)"
    L.append("- Six-gene tests with BH q<0.05: **%d** of %d mapped -> branch **%s**." %
             (nsig, len(mapped), branch))
    L.append("- Total M2 DEG probes across all platforms: **%d**." % total_m2)
L.append("- Rule: A = no gene survives -> stop calling them candidates; re-position as "
         "a methodological re-assessment. B/C = 1-2 / >=3 survive. D = whole DEG list collapses.\n")

open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("WROTE", OUT)
print("branch:", branch)
json.dump({"branch": branch}, open(os.path.join(RES, "decision.json"), "w"), indent=2)

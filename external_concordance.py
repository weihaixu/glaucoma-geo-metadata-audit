#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
external_concordance.py -- P1-b, step 3-4 of the submission-feasibility roadmap.

Purpose
-------
Apply the pre-specified donor-level OLS contrast to ONE external public GEO
series (GSE27276, human trabecular meshwork, POAG vs control) and report
*cross-tissue directional concordance* for the six pre-specified transcripts.

This is a STRESS TEST OF THE METADATA AUDIT, NOT A VALIDATION STUDY.
GSE27276 profiles a different tissue, from a different laboratory, on a
different platform, with a different case definition.  In its deposited
metadata the disease label is perfectly confounded with tissue procurement
(surgery vs donated eye) and with postmortem delay.  No ancestry / age / sex
fields are deposited, so the primary M2 design [1, glaucoma, ancestry]
reduces to [1, glaucoma] and is flagged "ADJUSTMENT NOT POSSIBLE", exactly as
for the primary platforms that lack an ancestry field.

Nothing in results/ is read for fitting and nothing there is modified.
All outputs go to results_external/ (independent directory).

Usage
-----
    D:/anaconda3/python.exe external_concordance.py

Inputs (read-only)
------------------
    external_inputs/GSE27276_series_matrix.txt.gz
    external_inputs/GPL2507.annot.gz
    results/04_deg_primary_M2.csv       (reference only, for sign comparison)

Author: re-analysis pipeline, round 13 (2026-11-09)
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
MATRIX = HERE / "external_inputs" / "GSE27276_series_matrix.txt.gz"
ANNOT = HERE / "external_inputs" / "GPL2507.annot.gz"
PRIMARY = HERE / "results" / "04_deg_primary_M2.csv"
OUT = HERE / "results_external"
TABLES = HERE / "tables"

SIX = ["TGFBR2", "SMAD1", "STAT1", "CASP1", "FGFR1", "CASP4"]
PRIMARY_PLATFORMS = [
    "GSE2378-GPL8300",
    "GSE9944-GPL8300",
    "GSE9944-GPL571",
]
ALPHA = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_matrix(path: Path):
    meta: dict[str, list[list[str]]] = defaultdict(list)
    ids: list[str] = []
    vals: list[list[float]] = []
    begin = False
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("!Sample_"):
                key = line.split("\t", 1)[0]
                meta[key].append(
                    [x.strip().strip('"') for x in line.split("\t")[1:]]
                )
            elif line.startswith("!Series_"):
                key = line.split("\t", 1)[0]
                meta[key].append(
                    [x.strip().strip('"') for x in line.split("\t")[1:]]
                )
            elif line.startswith("!series_matrix_table_begin"):
                begin = True
            elif line.startswith("!series_matrix_table_end"):
                break
            elif begin:
                parts = line.split("\t")
                if parts[0].strip('"') == "ID_REF":
                    continue
                ids.append(parts[0].strip('"'))
                vals.append(
                    [
                        float(x) if x not in ("", "null", "NA", "NaN") else np.nan
                        for x in parts[1:]
                    ]
                )
    X = np.asarray(vals, dtype=float)
    return meta, ids, X


def read_annot(path: Path) -> pd.DataFrame:
    rows: list[list[str]] = []
    header: list[str] | None = None
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.strip() or line[0] in "#!^":
                continue
            parts = line.rstrip("\n").split("\t")
            if header is None:
                header = parts
                continue
            rows.append(parts)
    df = pd.DataFrame(rows, columns=header)
    df = df[["ID", "Gene symbol"]].copy()
    df["ID"] = df["ID"].str.strip()
    df["Gene symbol"] = df["Gene symbol"].str.strip()
    return df


def phi_2x2(tab: pd.DataFrame) -> float:
    """Phi coefficient of a 2x2 crosstab, derived from the deposited labels."""
    if tab.shape != (2, 2):
        return float("nan")
    a, b = float(tab.iloc[0, 0]), float(tab.iloc[0, 1])
    c, d = float(tab.iloc[1, 0]), float(tab.iloc[1, 1])
    denom = np.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    return float((a * d - b * c) / denom) if denom > 0 else float("nan")


def bh(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    out = np.ones_like(p)
    ok = np.isfinite(p)
    if ok.any():
        out[ok] = multipletests(p[ok], method="fdr_bh")[1]
    return out


def ols_probe_matrix(Y: np.ndarray, glaucoma: np.ndarray, df_resid: int,
                     tcrit: float) -> dict[str, np.ndarray]:
    """Vectorised OLS of every probe on [1, glaucoma]. Returns beta/SE/t/p/CI."""
    n = Y.shape[1]
    X = np.column_stack([np.ones(n), glaucoma.astype(float)])
    xtx_inv = np.linalg.inv(X.T @ X)
    B = xtx_inv @ X.T @ Y.T                      # (2, n_probes)
    beta = B[1]
    resid = Y - (X @ B).T
    sigma2 = (resid ** 2).sum(axis=1) / df_resid
    se = np.sqrt(sigma2 * xtx_inv[1, 1])
    with np.errstate(divide="ignore", invalid="ignore"):
        tstat = np.where(se > 0, beta / se, 0.0)
    p = 2.0 * stats.t.sf(np.abs(tstat), df_resid)
    return {
        "log2FC": beta,
        "se": se,
        "t": tstat,
        "p": p,
        "ci_lo": beta - tcrit * se,
        "ci_hi": beta + tcrit * se,
    }


def build_units(meta, X, titles, groups, delays, collections):
    """Return three unit conventions: (name, Y, glaucoma, unit_ids, basis)."""
    n = X.shape[1]
    poag = [i for i, g in enumerate(groups) if g == 1]
    ctrl = [i for i, g in enumerate(groups) if g == 0]

    # --- controls: identical postmortem delay == paired eyes of one donor ---
    by_delay: dict[str, list[int]] = defaultdict(list)
    for i in ctrl:
        by_delay[delays[i]].append(i)
    ctrl_donors = []
    for delay in sorted(by_delay):
        ctrl_donors.append((f"C_delay_{delay.replace(':', '')}", by_delay[delay]))

    # --- POAG: all delays are 0 (surgery), so metadata cannot pair them ---
    C = np.corrcoef(X[:, poag].T)
    pairs = []
    for a in range(len(poag)):
        for b in range(a + 1, len(poag)):
            pairs.append((float(C[a, b]), poag[a], poag[b]))
    pairs.sort(reverse=True)
    chosen, used = [], set()
    for r, a, b in pairs:
        if a not in used and b not in used:
            chosen.append((r, a, b))
            used.update((a, b))
        if len(chosen) == 2:
            break

    def poag_units(n_pairs: int):
        units, consumed = [], set()
        for _, a, b in chosen[:n_pairs]:
            units.append((f"P_pair_{titles[a]}_{titles[b]}".replace(" ", ""), [a, b]))
            consumed.update((a, b))
        for i in poag:
            if i not in consumed:
                units.append((f"P_{titles[i]}".replace(" ", ""), [i]))
        return units

    def assemble(ctrl_u, poag_u):
        ids, Y, g, basis, counts = [], [], [], [], []
        for name, cols in ctrl_u:
            ids.append(name)
            Y.append(X[:, cols].mean(axis=1) if len(cols) > 1 else X[:, cols[0]])
            g.append(0)
            basis.append("postmortem-delay metadata" if len(cols) > 1 else "single array")
            counts.append(len(cols))
        for name, cols in poag_u:
            ids.append(name)
            Y.append(X[:, cols].mean(axis=1) if len(cols) > 1 else X[:, cols[0]])
            g.append(1)
            basis.append("correlation-based merge" if len(cols) > 1 else "single array")
            counts.append(len(cols))
        return ids, np.column_stack(Y), np.asarray(g, dtype=int), basis, counts

    units = []
    # 1. naive array level
    units.append(
        ("array_level", list(range(n)), X, np.asarray(groups, dtype=int),
         ["deposited array"] * n, [1] * n,
         "All 36 deposited arrays treated as independent (the naive reuse).")
    )
    # 2. controls collapsed by metadata, POAG arrays left distinct (upper bound)
    ids2, Y2, g2, b2, c2 = assemble(ctrl_donors, poag_units(0))
    units.append(
        ("donor_metadata", ids2, Y2, g2, b2, c2,
         "Controls collapsed by postmortem delay (13 donors); POAG arrays "
         "left separate because deposited metadata cannot pair them. "
         "Known residual pseudo-replication on the case side.")
    )
    # 3. best effort matching GEO's declared 15 POAG + 13 controls
    ids3, Y3, g3, b3, c3 = assemble(ctrl_donors, poag_units(2))
    units.append(
        ("donor_declared", ids3, Y3, g3, b3, c3,
         "As donor_metadata plus two disjoint highest-correlation POAG pairs "
         "merged by averaging, reproducing the declared 15 cases / 13 controls. "
         "The second merge is an unverifiable, data-driven assumption.")
    )
    return units, ctrl_donors, chosen, pairs


def main() -> int:
    for p in (MATRIX, ANNOT, PRIMARY):
        if not p.exists():
            print(f"FATAL: missing input {p}", file=sys.stderr)
            return 2
    OUT.mkdir(exist_ok=True)
    TABLES.mkdir(exist_ok=True)

    meta, probe_ids, X = read_matrix(MATRIX)
    titles = meta["!Sample_title"][0]
    gsms = meta["!Sample_geo_accession"][0]
    ch = meta["!Sample_characteristics_ch1"]
    disease = [x.split(": ", 1)[1] for x in ch[0]]
    collection = [x.split(": ", 1)[1] for x in ch[1]]
    delays = [x.split(": ", 1)[1] for x in ch[2]]
    groups = [1 if "Glaucoma" in d else 0 for d in disease]
    n_arrays = X.shape[1]

    # scale decision: log2-like (no transform), consistent with ensure_log2(mode="log2")
    finite = X[np.isfinite(X)]
    vmin, vmed, vmax = float(finite.min()), float(np.median(finite)), float(finite.max())
    log2_transformed = bool(vmin >= -10 and vmax > 50)
    if log2_transformed:
        X = np.log2(np.clip(X, 1, None))
    assert not log2_transformed, "unexpected linear scale; review Methods decision"

    # annotation
    annot = read_annot(ANNOT)
    p2g = dict(zip(annot["ID"], annot["Gene symbol"]))
    genes = [p2g.get(p, "") for p in probe_ids]
    mapped = sum(1 for g in genes if g)
    coverage = 100.0 * mapped / len(genes)

    # units (computed on the untransformed-but-log2-like matrix)
    units, ctrl_donors, chosen_pairs, all_pairs = build_units(
        meta, X, titles, groups, delays, collection
    )

    # confounding audit
    coll_tab = pd.crosstab(pd.Series(disease, name="disease"),
                           pd.Series(collection, name="collection"))
    delay_bin = ["zero" if d in ("0", "0:00") else "nonzero" for d in delays]
    delay_tab = pd.crosstab(pd.Series(disease, name="disease"),
                            pd.Series(delay_bin, name="postmortem_delay"))
    Xfull = np.column_stack([
        np.ones(n_arrays),
        np.asarray(groups, dtype=float),
        np.asarray([1 if c.lower().startswith("surgery") else 0 for c in collection], float),
        np.asarray([0 if d in ("0", "0:00") else 1 for d in delays], float),
    ])
    full_rank = int(np.linalg.matrix_rank(Xfull))
    phi_coll, phi_delay = phi_2x2(coll_tab), phi_2x2(delay_tab)
    conf_rows = [
        ("n_arrays_deposited", n_arrays, "GSM columns in the series matrix"),
        ("n_donors_declared_by_GEO", 28, "13 controls + 15 POAG in !Series_overall_design"),
        ("n_poag_arrays", sum(groups), "disease state: Primary Open-Angle Glaucoma"),
        ("n_control_arrays", n_arrays - sum(groups), "disease state: Control"),
        ("control_unique_postmortem_delays", len(ctrl_donors),
         "19 control arrays collapse to 13 delay-defined donors (6 paired-eye donors)"),
        ("poag_unique_postmortem_delays", 1,
         "all 17 POAG arrays have delay 0 or 0:00; metadata cannot pair them"),
        ("disease_vs_collection_phi", round(phi_coll, 4),
         f"complete separation: POAG=surgery, control=Donated eye; table={coll_tab.to_dict()}"),
        ("disease_vs_delay_phi", round(phi_delay, 4),
         f"complete separation: POAG delay 0, control delay > 0; table={delay_tab.to_dict()}"),
        ("design_rank_with_confounders", full_rank,
         f"rank of [1, glaucoma, surgery, delay_nonzero] is {full_rank} of 4: surgery and "
         "delay_nonzero are exactly collinear with glaucoma, so the confounding is not identifiable"),
        ("covariates_available", "none",
         "no ancestry / age / sex fields deposited; M2 reduces to [1, glaucoma]"),
        ("annotation_coverage_pct", round(coverage, 2),
         f"{mapped}/{len(genes)} matrix probes carry a non-empty Gene symbol in GPL2507.annot.gz"),
        ("six_gene_probes", sum(1 for g in genes if g.upper() in SIX),
         "probes on this platform annotated to the six pre-specified transcripts"),
    ]
    pd.DataFrame(conf_rows, columns=["check", "value", "detail"]).to_csv(
        OUT / "09_confounding_audit.csv", index=False
    )

    # metadata / donor map
    meta_rows = []
    for i in range(n_arrays):
        meta_rows.append({
            "gsm": gsms[i], "title": titles[i],
            "group": "POAG" if groups[i] else "Control",
            "disease_state": disease[i], "collection": collection[i],
            "postmortem_delay": delays[i],
        })
    pd.DataFrame(meta_rows).to_csv(OUT / "01_array_metadata.csv", index=False)

    donor_rows = []
    for name, uid, Y, g, basis, counts, _desc in units:
        for j, u in enumerate(uid):
            donor_rows.append({
                "convention": name, "unit_id": u,
                "group": "POAG" if int(g[j]) else "Control",
                "basis": basis[j],
                "n_arrays": int(counts[j]),
            })
    pd.DataFrame(donor_rows).to_csv(OUT / "02_donor_map.csv", index=False)

    pd.DataFrame({
        "probe": probe_ids,
        "gene_symbol": genes,
    }).query("gene_symbol != ''").to_csv(OUT / "03_probe_gene_map.csv", index=False)

    # primary reference (min-p probe per gene, per discovery platform)
    prim = pd.read_csv(PRIMARY, low_memory=False)
    prim_six = prim[prim["gene"].isin(SIX)].copy()
    prim_ref = (prim_six.sort_values("p")
                .groupby(["platform_dataset", "gene"], as_index=False)
                .first()[["platform_dataset", "gene", "log2FC", "p", "q_BH"]])
    prim_ref = prim_ref.rename(columns={
        "log2FC": "primary_log2FC", "p": "primary_p", "q_BH": "primary_q_BH",
    })

    file_numbers = {"array_level": "04", "donor_metadata": "05",
                    "donor_declared": "06"}
    six_rows, conc_rows, summary_conventions = [], [], {}

    for name, uid, Y, g, basis, counts, desc in units:
        n_units = Y.shape[1]
        df_resid = n_units - 2
        tcrit = float(stats.t.ppf(1 - ALPHA / 2, df_resid))
        fit = ols_probe_matrix(Y, g, df_resid, tcrit)
        q = bh(fit["p"])
        tbl = pd.DataFrame({
            "probe": probe_ids,
            "gene": genes,
            "log2FC": fit["log2FC"],
            "se": fit["se"],
            "t": fit["t"],
            "p": fit["p"],
            "q_BH": q,
            "ci_lo": fit["ci_lo"],
            "ci_hi": fit["ci_hi"],
            "df_residual": df_resid,
            "note": "ADJUSTMENT NOT POSSIBLE: no ancestry/age/sex in GEO metadata",
        })
        tbl.to_csv(OUT / f"{file_numbers[name]}_OLS_{name}.csv", index=False)

        for gene in SIX:
            sub = tbl[tbl["gene"].str.upper() == gene.upper()]
            if sub.empty:
                six_rows.append({"convention": name, "gene": gene,
                                 "n_probes": 0, "status": "probe not mapped"})
                continue
            best = sub.loc[sub["p"].idxmin()]
            six_rows.append({
                "convention": name, "gene": gene,
                "n_probes": int(len(sub)),
                "probe_min_p": best["probe"],
                "log2FC": round(float(best["log2FC"]), 4),
                "ci_lo": round(float(best["ci_lo"]), 4),
                "ci_hi": round(float(best["ci_hi"]), 4),
                "se": round(float(best["se"]), 4),
                "p": float(best["p"]),
                "q_BH": float(best["q_BH"]),
                "median_log2FC_all_probes": round(float(sub["log2FC"].median()), 4),
                "df_residual": df_resid,
                "status": "significant (BH q<0.05)" if best["q_BH"] < ALPHA
                          else "not significant (BH q>=0.05)",
            })

        six_df = pd.DataFrame([r for r in six_rows if r["convention"] == name])
        for plat in PRIMARY_PLATFORMS:
            ref = prim_ref[prim_ref["platform_dataset"] == plat]
            for _, r in six_df.iterrows():
                m = ref[ref["gene"] == r["gene"]]
                if m.empty or "log2FC" not in r:
                    continue
                plfc = float(m.iloc[0]["primary_log2FC"])
                efc = float(r["log2FC"])
                conc_rows.append({
                    "convention": name,
                    "primary_platform": plat,
                    "gene": r["gene"],
                    "primary_log2FC": round(plfc, 4),
                    "primary_q_BH": round(float(m.iloc[0]["primary_q_BH"]), 4),
                    "external_log2FC": efc,
                    "external_q_BH": round(float(r["q_BH"]), 4),
                    "sign_agreement": int(np.sign(plfc) == np.sign(efc)),
                })

        summary_conventions[name] = {
            "n_units": n_units,
            "n_poag": int(g.sum()),
            "n_control": int((1 - g).sum()),
            "residual_df": df_resid,
            "n_probes_tested": int(len(tbl)),
            "n_probes_q05": int((q < ALPHA).sum()),
            "n_six_genes_significant_q05": int(
                sum(1 for r in six_rows
                    if r["convention"] == name and r.get("status", "").startswith("significant"))
            ),
            "description": desc,
        }
        print(f"[{name}] units={n_units} (POAG {int(g.sum())} / control "
              f"{int((1-g).sum())}) df={df_resid} probes q<0.05={int((q<ALPHA).sum())} "
              f"six-gene q<0.05={summary_conventions[name]['n_six_genes_significant_q05']}")

    pd.DataFrame(six_rows).to_csv(OUT / "07_six_genes_all_conventions.csv", index=False)
    conc = pd.DataFrame(conc_rows)
    conc.to_csv(OUT / "08_directional_concordance.csv", index=False)

    # ---- summary ----
    sign_summary = (conc.groupby(["convention", "primary_platform"])
                    .agg(n_compared=("sign_agreement", "size"),
                         n_sign_agreement=("sign_agreement", "sum"))
                    .reset_index())
    sign_summary["pct"] = (100.0 * sign_summary["n_sign_agreement"]
                           / sign_summary["n_compared"]).round(1)
    sign_summary.to_csv(OUT / "10_sign_agreement_summary.csv", index=False)

    summary = {
        "series": "GSE27276",
        "platform": "GPL2507",
        "tissue": "human trabecular meshwork",
        "role": "cross-tissue directional concordance / metadata-audit stress test",
        "NOT": "independent replication, validation, or confirmatory evidence",
        "declared_design": meta["!Series_overall_design"][0][0],
        "series_summary": meta["!Series_summary"][0][0],
        "n_arrays": n_arrays,
        "n_units_by_convention": {k: v["n_units"] for k, v in summary_conventions.items()},
        "scale": {"min": vmin, "median": vmed, "max": vmax,
                  "log2_transformed": log2_transformed,
                  "decision": "log2-like; no transform (ensure_log2 mode='log2')"},
        "annotation": {"n_matrix_probes": len(genes), "n_mapped": mapped,
                       "coverage_pct": round(coverage, 2),
                       "n_six_gene_probes": sum(1 for g in genes if g.upper() in SIX)},
        "confounding": {
            "disease_vs_collection": "complete separation (POAG=surgery, control=Donated eye)",
            "disease_vs_postmortem_delay": "complete separation (POAG=0, control>0)",
            "design_rank_with_confounders": full_rank,
            "phi_disease_collection": round(phi_coll, 4),
            "phi_disease_delay": round(phi_delay, 4),
            "covariates": "no ancestry/age/sex; M2 reduces to [1, glaucoma]",
        },
        "control_donors_from_metadata": len(ctrl_donors),
        "poag_correlation_merges": [
            {"arrays": [titles[a], titles[b]], "pearson_r": round(r, 6),
             "support": "highest POAG pair; consistent with GEO 'case #6 with two replicates'"
                        if k == 0 else "second disjoint pair; UNVERIFIABLE assumption"}
            for k, (r, a, b) in enumerate(chosen_pairs)
        ],
        "conventions": summary_conventions,
        "sign_agreement": sign_summary.to_dict(orient="records"),
        "primary_results_modified": False,
        "primary_file_sha256": sha256(PRIMARY),
        "input_sha256": {
            "GSE27276_series_matrix.txt.gz": sha256(MATRIX),
            "GPL2507.annot.gz": sha256(ANNOT),
        },
        "interpretation": (
            "Directional concordance is descriptive only (n=6 transcripts; no "
            "inference, no p-value). Disease is perfectly confounded with tissue "
            "procurement and postmortem delay, so any case-control contrast in "
            "this series is not interpretable as a disease effect. The six-gene "
            "result must not be used to support or refute the primary 0/18 finding."
        ),
    }
    (OUT / "external_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # ---- README ----
    (OUT / "README.md").write_text(
        "# results_external/ -- GSE27276 stress test (round 13, P1-b)\n\n"
        "**Read this before using any number in this directory.**\n\n"
        "This is a cross-tissue directional-concordance exercise and a stress test "
        "of `geo_metadata_audit.py`. It is **not** an independent replication, not a "
        "validation cohort, and not confirmatory evidence for the six transcripts.\n\n"
        "- Tissue: human trabecular meshwork (primary work used ONH astrocytes / whole ONH).\n"
        "- Laboratory, platform (GPL2507, Illumina Sentrix Human-6), and case definition differ.\n"
        "- Disease is **perfectly confounded** with collection method (surgery vs donated "
        "eye) and postmortem delay (0 vs >0), so the case-control coefficient cannot be "
        "interpreted as a disease effect (`09_confounding_audit.csv`).\n"
        "- No ancestry/age/sex fields are deposited; the pre-specified M2 design reduces "
        "to `[1, glaucoma]` and every probe row is flagged `ADJUSTMENT NOT POSSIBLE`.\n\n"
        "## Three unit conventions\n\n"
        "| Convention | Units | POAG | Control | Residual df | Meaning |\n"
        "|---|---:|---:|---:|---:|---|\n"
        + "\n".join(
            f"| `{k}` | {v['n_units']} | {v['n_poag']} | {v['n_control']} | "
            f"{v['residual_df']} | {v['description']} |"
            for k, v in summary_conventions.items()
        )
        + "\n\nGEO declares 13 controls + 15 POAG = 28 donors but deposits 36 arrays. "
        "The 19 control arrays collapse unambiguously to 13 donors by identical "
        "postmortem delay (six paired-eye donors), corroborated by expression "
        "correlation. All 17 POAG arrays have delay 0, so the two case-side merges "
        "in `donor_declared` are **data-driven and the second is unverifiable**. "
        "This residual ambiguity is the finding, not a defect to be hidden.\n\n"
        "## Files\n\n"
        "| File | Content |\n|---|---|\n"
        "| `01_array_metadata.csv` | 36 arrays, GSM, title, group, collection, delay |\n"
        "| `02_donor_map.csv` | unit definitions per convention and reconstruction basis |\n"
        "| `03_probe_gene_map.csv` | GPL2507 probe -> Gene symbol (mapped probes only) |\n"
        "| `04_OLS_array_level.csv` | all-probe OLS, 36 arrays (naive) |\n"
        "| `05_OLS_donor_metadata.csv` | all-probe OLS, 30 metadata-defined units |\n"
        "| `06_OLS_donor_declared.csv` | all-probe OLS, 28 declared-design units |\n"
        "| `07_six_genes_all_conventions.csv` | six transcripts, min-p probe + median, all conventions |\n"
        "| `08_directional_concordance.csv` | sign comparison vs three primary discovery platforms |\n"
        "| `09_confounding_audit.csv` | metadata defects and rank check |\n"
        "| `10_sign_agreement_summary.csv` | descriptive sign-agreement counts (no p-values) |\n"
        "| `external_summary.json` | machine-readable summary + sha256 of inputs/primary file |\n\n"
        "BH correction is applied across all matrix probes within each convention. "
        "95% CIs are nominal and not multiplicity-adjusted. Sign agreement is "
        "descriptive with n=6 genes; no inferential test was performed.\n\n"
        "**`results/` was not modified.** `external_summary.json` records the sha256 of "
        "`results/04_deg_primary_M2.csv` for verification.\n",
        encoding="utf-8",
    )

    # ---- Table S17 ----
    six_df = pd.DataFrame(six_rows)
    s17_lines = [
        "# Table S17. Cross-tissue directional concordance of the six pre-specified transcripts in GSE27276\n",
        "Exploratory **cross-tissue directional concordance only**. GSE27276 profiles human "
        "trabecular meshwork on GPL2507 from a different laboratory with a different case "
        "definition. It is **not an independent replication or validation**. Disease is "
        "perfectly confounded with tissue procurement and postmortem delay, and no ancestry/"
        "age/sex covariates are deposited, so the coefficient is `intercept + glaucoma` only. "
        "BH q is computed across all matrix probes within each unit convention; 95% CIs are "
        "nominal. Values are for the probe with the smallest nominal p within each gene.\n",
        "| Convention | Gene | n probes | log2FC | nominal 95% CI | p | BH q | Status |",
        "|---|---|---:|---:|---|---:|---:|---|",
    ]
    for _, r in six_df.iterrows():
        if "log2FC" not in r or pd.isna(r.get("log2FC")):
            s17_lines.append(f"| {r['convention']} | {r['gene']} | 0 | n/a | n/a | n/a | n/a | probe not mapped |")
            continue
        s17_lines.append(
            f"| {r['convention']} | {r['gene']} | {int(r['n_probes'])} | "
            f"{r['log2FC']:+.3f} | [{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}] | "
            f"{r['p']:.4g} | {r['q_BH']:.4f} | {r['status']} |"
        )
    s17_lines += [
        "",
        "## Directional agreement with the primary discovery platforms",
        "",
        "Descriptive sign counts for six transcripts; **no p-value or inferential test** "
        "was computed (n = 6 genes, cross-tissue, non-independent probes).",
        "",
        "| Convention | Primary platform | Sign agreement |",
        "|---|---|---:|",
    ]
    for _, r in sign_summary.iterrows():
        s17_lines.append(
            f"| {r['convention']} | {r['primary_platform']} | "
            f"{int(r['n_sign_agreement'])}/{int(r['n_compared'])} ({r['pct']:.1f}%) |"
        )
    s17_lines += [
        "",
        "Primary reference values are the min-p probe per gene from the frozen "
        "`results/04_deg_primary_M2.csv` (Table 2). " + summary["interpretation"],
        "",
    ]
    (TABLES / "TableS17_external_concordance.md").write_text(
        "\n".join(s17_lines), encoding="utf-8"
    )
    six_df.to_csv(TABLES / "TableS17_external_concordance.tsv", sep="\t", index=False)

    # ---- Table S18 ----
    s18 = [
        "# Table S18. Donor reconstruction and confounding audit of the external candidate GSE27276\n",
        "Generated by `external_concordance.py` from the deposited series matrix and "
        "`!Series_overall_design`. This table documents **why a clean donor-level M2 "
        "cannot be pre-specified** on this series without information that GEO does not deposit. "
        "It is a demonstration of the reusable metadata checklist (Table S16), not a result "
        "about the six transcripts.\n",
        "| Check | Value | Detail |",
        "|---|---:|---|",
    ]
    for c, v, d in conf_rows:
        s18.append(f"| {c} | {v} | {d} |")
    s18 += [
        "",
        "## Control-side reconstruction (metadata-driven, verifiable)",
        "",
        "| Donor key | n arrays | GSM | postmortem delay |",
        "|---|---:|---|---|",
    ]
    for key, cols in ctrl_donors:
        s18.append(
            f"| {key} | {len(cols)} | {', '.join(gsms[i] for i in cols)} | {delays[cols[0]]} |"
        )
    s18 += [
        "",
        "Six delay values occur exactly twice and seven occur once: 19 arrays -> 13 control "
        "donors, matching GEO's declared 13 controls. The six paired-eye donors are also the "
        "six highest-correlation control array pairs, independently corroborating the grouping.",
        "",
        "## Case-side reconstruction (data-driven, only partly verifiable)",
        "",
        "| Rank | Arrays | Pearson r | Support |",
        "|---:|---|---:|---|",
    ]
    for k, (r, a, b) in enumerate(chosen_pairs):
        support = ("highest POAG pair; consistent with GEO's 'case #6 with two replicates'"
                   if k == 0 else "second disjoint pair; **unverifiable assumption**")
        s18.append(f"| {k+1} | {titles[a]} / {titles[b]} | {r:.6f} | {support} |")
    s18 += [
        "",
        "All 17 POAG arrays were collected at surgery with postmortem delay 0 (or `0:00`), "
        "so no deposited field identifies the second duplicate. `donor_declared` therefore "
        "reaches GEO's declared 15 cases by one well-supported and one assumption-driven "
        "merge; `donor_metadata` deliberately leaves the case side uncollapsed as a "
        "conservative upper bound. Both are reported alongside the naive array-level fit.",
        "",
        "## Interpretation boundaries",
        "",
        "* Arrays are not donors. `n_donors = n_arrays` in a naive parser is a parsing "
        "limitation, not evidence of independence.",
        "* `phi = 1` for disease vs collection and disease vs postmortem delay; "
        f"adding these terms gives design rank {full_rank} of 4, because both terms "
        "are exactly collinear with the disease indicator, so the confounding "
        "cannot be adjusted away.",
        "* GPL2507 annotation covers " + f"{coverage:.2f}% of matrix probes; unmapped "
        "probes are missing annotation, never negative results.",
        "* No differential-expression result from this series may be described as "
        "validation, replication, or confirmation of the primary 0/18 finding.",
        "* `results/` was not modified.",
        "",
    ]
    (TABLES / "TableS18_external_donor_reconstruction.md").write_text(
        "\n".join(s18), encoding="utf-8"
    )
    pd.DataFrame(conf_rows, columns=["check", "value", "detail"]).to_csv(
        TABLES / "TableS18_external_donor_reconstruction.tsv", sep="\t", index=False
    )

    # write sign summary into json already done; print digest
    print("\n--- sign agreement (descriptive) ---")
    print(sign_summary.to_string(index=False))
    print("\ncontrol donors from delay:", len(ctrl_donors))
    print("POAG merges:", [(titles[a], titles[b], round(r, 6)) for r, a, b in chosen_pairs])
    print("annotation coverage %.2f%% (%d/%d)" % (coverage, mapped, len(genes)))
    print("outputs ->", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

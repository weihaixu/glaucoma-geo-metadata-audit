#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""geo_metadata_audit.py - reusable GEO series-matrix metadata quality audit.

Read-only auditor for five defect classes that materially changed the effect
estimates in this re-analysis:

  1. free_text_covariates     - age/sex/ancestry buried in one free-text string
  2. group_x_ancestry_cells   - empty group x ancestry strata, rank/condition
  3. replicate_donor_overlap  - technical replicates and cross-platform donors
  4. annotation_availability  - missing / partial platform gene annotation
  5. scale_excluded_groups    - linear vs log2 scale, OHT/other excluded arms

Usage:
    D:/anaconda3/python.exe geo_metadata_audit.py
    D:/anaconda3/python.exe geo_metadata_audit.py --matrix NEW_series_matrix.txt.gz
    D:/anaconda3/python.exe geo_metadata_audit.py --out results_audit

It never writes into results/, never modifies an input matrix, and never
interprets "probe not mapped" as a negative biological result.
"""
import argparse
import csv
import gzip
import json
import math
import os
import re
import sys
from collections import defaultdict, Counter

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MATRICES = [
    ("GSE9944", "GPL571", "GSE9944-GPL571_series_matrix.txt.gz"),
    ("GSE9944", "GPL8300", "GSE9944-GPL8300_series_matrix.txt.gz"),
    ("GSE9944", "GPL91", "GSE9944-GPL91_series_matrix.txt.gz"),
    ("GSE2378", "GPL8300", "GSE2378-GPL8300_series_matrix.txt.gz"),
    ("GSE2378", "GPL91", "GSE2378-GPL91_series_matrix.txt.gz"),
    ("GSE45570", "GPL5175", "GSE45570_series_matrix.txt.gz"),
]
ANNOT_OF = {
    "GPL571": "GPL571.annot.gz",
    "GPL8300": "GPL8300.annot.gz",
    "GPL91": "GPL91.annot.gz",
    "GPL5175": "GPL5175.annot.gz",   # GEO returns 404 for this platform
}
COMPLETENESS = 0.80   # the pre-specified rule used by the primary pipeline
CHECKS = ["free_text_covariates", "group_x_ancestry_cells",
          "replicate_donor_overlap", "annotation_availability",
          "scale_excluded_groups"]


def read_matrix(path):
    """Parse !Sample_* metadata lines and a bounded sample of numeric rows."""
    meta = defaultdict(list)
    ids, nums, n_data_rows = [], [], 0
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        in_table = False
        for line in f:
            line = line.rstrip("\r\n")
            if line.startswith("!series_matrix_table_begin"):
                in_table = True
                continue
            if line.startswith("!series_matrix_table_end"):
                break
            if in_table:
                parts = line.split("\t")
                if not parts or parts[0].startswith("!") or parts[0].strip('"') == "ID_REF":
                    continue
                n_data_rows += 1
                ids.append(parts[0].strip().strip('"'))
                if len(nums) < 400:
                    row = []
                    for c in parts[1:]:
                        try:
                            row.append(float(c.strip().strip('"')))
                        except (ValueError, TypeError):
                            pass
                    if row:
                        nums.append(row)
                continue
            if line.startswith("!Sample_"):
                parts = line.split("\t")
                meta[parts[0]].append([c.strip().strip('"') for c in parts[1:]])
    return {"meta": meta, "ids": ids, "nums": nums, "n_data_rows": n_data_rows,
            "path": os.path.basename(path)}


def detect_platform(rel):
    """Read !Series_platform_id when the file name carries no GPL number."""
    try:
        with gzip.open(os.path.join(ROOT, rel), "rt", encoding="utf-8",
                       errors="replace") as f:
            for line in f:
                if line.startswith("!Series_platform_id"):
                    return line.split("\t")[1].strip().strip('"')
                if line.startswith("!series_matrix_table_begin"):
                    break
    except Exception:
        pass
    return None


def first(meta, key):
    v = meta.get(key)
    return v[0] if v else []


def classify(text):
    t = (text or "").lower()
    if "ocular hypertension" in t or re.search(r"\boht\b", t):
        return "excluded"
    if "glaucoma" in t or "poag" in t:
        return "glaucoma"
    if "normal" in t or "control" in t or "unaffected" in t:
        return "control"
    return "unknown"


def classify_title(t):
    if re.search(r"\sG\d", t) or re.search(r"^G\d", t):
        return "glaucoma"
    if re.search(r"\sN\d", t) or re.search(r"^N\d", t):
        return "control"
    return classify(t)


def group_labels(m):
    chars = m["meta"].get("!Sample_characteristics_ch1", [])
    for row in chars:
        if not row:
            continue
        keys = [c.split(":", 1)[0].strip().lower() for c in row if ":" in c]
        if "group" in keys and len(keys) >= len(row) * 0.8:
            return ([classify(c.split(":", 1)[1]) for c in row],
                    "structured !Sample_characteristics_ch1:group")
    src = first(m["meta"], "!Sample_source_name_ch1")
    if src and any(re.search(r"glaucoma|normal|control", s, re.I) for s in src):
        return [classify(s) for s in src], "!Sample_source_name_ch1"
    titles = first(m["meta"], "!Sample_title")
    return [classify_title(t) for t in titles], "!Sample_title G/N tokens"


def ancestry_labels(m, n):
    for row in m["meta"].get("!Sample_characteristics_ch1", []):
        if len(row) != n:
            continue
        out = []
        for c in row:
            lc = c.lower()
            if "caucasian" in lc:
                out.append("Caucasian")
            elif "african" in lc:
                out.append("African")
            else:
                out.append(None)
        if sum(x is not None for x in out) >= 0.8 * n:
            return out
    return None


def donor_ids(m):
    titles = first(m["meta"], "!Sample_title")
    return [re.sub(r"-rep\d+$", "", t) for t in titles]


def annot_stats(platform, ids):
    fn = ANNOT_OF.get(platform, platform + ".annot.gz")
    path = os.path.join(ROOT, fn)
    if not os.path.exists(path):
        path = os.path.join(ROOT, "external_inputs", fn)
    if not os.path.exists(path):
        # distinguish an explicitly missing GEO annotation from a partial mapping
        partial = os.path.join(ROOT, "GPL5175_platform_prefix.txt")
        return {"status": "missing", "file": fn,
                "partial_prefix_present": os.path.exists(partial),
                "mapped_ids": 0, "matrix_ids_covered": 0,
                "coverage_pct": 0.0,
                "note": "GEO has no official annot.gz for this platform; "
                        "probe not mapped is NOT a negative result"}
    header = None
    sym_idx = id_idx = None
    mapped = set()
    try:
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip("\r\n")
                if line.startswith("!platform_table_begin"):
                    continue
                if line.startswith("!platform_table_end"):
                    break
                cells = line.split("\t")
                if header is None:
                    if cells and cells[0].strip() == "ID":
                        header = [c.strip() for c in cells]
                        id_idx = 0
                        sym_idx = next((i for i, c in enumerate(header)
                                        if c.lower() in ("gene symbol", "symbol")), None)
                    continue
                if sym_idx is None or len(cells) <= sym_idx:
                    continue
                pid, sym = cells[id_idx].strip(), cells[sym_idx].strip()
                if pid and sym and sym not in ("---", "", "nan", "NA"):
                    mapped.add(pid)
    except Exception as e:
        return {"status": "unreadable", "file": fn, "error": type(e).__name__,
                "mapped_ids": 0, "matrix_ids_covered": 0, "coverage_pct": 0.0}
    idset = set(ids)
    cov = len(idset & mapped)
    return {"status": "available", "file": fn,
            "source": ("rebuilt from the complete SOFT platform table; GEO has no "
                       "official annot.gz" if fn == "GPL5175.annot.gz"
                       else "GEO official annot.gz"),
            "mapped_ids": len(mapped), "matrix_ids_covered": cov,
            "coverage_pct": round(100.0 * cov / max(len(idset), 1), 2)}


def audit_one(series, platform, filename, extra_platforms=None, role="primary"):
    m = read_matrix(os.path.join(ROOT, filename))
    meta = m["meta"]
    n = len(first(meta, "!Sample_geo_accession")) or len(first(meta, "!Sample_title"))
    labels, group_src = group_labels(m)
    anc = ancestry_labels(m, n)
    donors = donor_ids(m)
    flat = [v for row in m["nums"] for v in row]
    rec = {"series": series, "platform": platform,
           "dataset": os.path.basename(filename).replace("_series_matrix.txt.gz", ""),
           "role": role,
           "n_arrays": n, "n_probes": m["n_data_rows"], "group_source": group_src}
    metrics = []

    def put(cat, key, value, status="INFO", evidence=""):
        metrics.append({"dataset": rec["dataset"], "category": cat, "metric": key,
                        "value": value, "status": status, "evidence": evidence})

    # ---- 1. free-text covariates -------------------------------------------
    chars = meta.get("!Sample_characteristics_ch1", [])
    struct = Counter()
    free_cells = compound = 0
    age_free = sex_free = anc_free = 0
    for row in chars:
        for c in row:
            if not c:
                continue
            km = re.match(r"^\s*([A-Za-z_ ]+):\s*(.+)$", c)
            if km:
                struct[km.group(1).strip().lower()] += 1
            else:
                free_cells += 1
                hits = 0
                if re.search(r"age\s*\d|\d+-year-old|\d+\s*yrs", c, re.I):
                    age_free += 1; hits += 1
                if re.search(r"\b(male|female|man|woman)\b", c, re.I):
                    sex_free += 1; hits += 1
                if re.search(r"caucasian|african|ancestry|race", c, re.I):
                    anc_free += 1; hits += 1
                if hits >= 2:
                    compound += 1
    age_struct = sum(v for k, v in struct.items() if "age" in k)
    sex_struct = sum(v for k, v in struct.items() if "sex" in k or "gender" in k)
    feasible = [k for k, v in struct.items() if v >= COMPLETENESS * n]
    rec.update({"n_characteristics_rows": len(chars), "free_text_cells": free_cells,
                "compound_free_text_cells": compound,
                "structured_fields": dict(struct),
                "structured_adjustable_terms": feasible,
                "structured_age_cells": age_struct, "structured_sex_cells": sex_struct,
                "free_text_age_hits": age_free, "free_text_sex_hits": sex_free,
                "free_text_ancestry_hits": anc_free})
    put("free_text_covariates", "n_characteristics_rows", len(chars))
    put("free_text_covariates", "compound_free_text_cells", compound)
    put("free_text_covariates", "structured_age_cells", age_struct)
    put("free_text_covariates", "structured_sex_cells", sex_struct)
    put("free_text_covariates", "adjustable_terms_at_80pct", ",".join(feasible) or "none")
    if compound > 0 or (age_struct < COMPLETENESS * n and sex_struct < COMPLETENESS * n
                        and (age_free or sex_free)):
        st = "FAIL"
    elif age_struct < COMPLETENESS * n or sex_struct < COMPLETENESS * n:
        st = "WARN"
    else:
        st = "PASS"
    rec["check_free_text_covariates"] = st
    put("free_text_covariates", "class_status", st, st,
        "age/sex buried in free text -> structured parser returns few usable values")

    # ---- 2. group x ancestry zero cells ------------------------------------
    rec["group_labels"] = dict(Counter(labels))
    if anc is None:
        st = "NOT_APPLICABLE"
        rec.update({"zero_cells": None, "phi": None, "design_full_rank": None,
                    "design_condition_number": None})
        put("group_x_ancestry_cells", "ancestry_field", "absent")
    else:
        pairs = [(g, a) for g, a in zip(labels, anc)
                 if g in ("glaucoma", "control") and a is not None]
        ct = Counter(pairs)
        levels_g = ["glaucoma", "control"]
        # Caucasian-reference coding, identical to the primary model's
        # race_Caucasian term, so phi matches the manuscript's -0.354.
        anc_levels = set(a for _, a in pairs)
        levels_a = (["Caucasian"] if "Caucasian" in anc_levels else []) + \
                   sorted(anc_levels - {"Caucasian"})
        zeros = [(g, a) for g in levels_g for a in levels_a if ct[(g, a)] == 0]
        # phi on the 2x2 (glaucoma/control x majority/minority ancestry)
        phi = None
        if len(levels_a) == 2:
            a0, a1 = levels_a
            A, B = ct[("glaucoma", a0)], ct[("glaucoma", a1)]
            C, D = ct[("control", a0)], ct[("control", a1)]
            den = math.sqrt((A + B) * (C + D) * (A + C) * (B + D))
            phi = round((A * D - B * C) / den, 4) if den else None
        # full-rank / conditioning of [1, glaucoma, ancestry]
        X = np.array([[1.0, 1.0 if g == "glaucoma" else 0.0,
                       1.0 if a == levels_a[0] else 0.0] for g, a in pairs])
        rank = int(np.linalg.matrix_rank(X)) if len(X) else 0
        cond = round(float(np.linalg.cond(X)), 3) if rank == X.shape[1] else None
        rec.update({"group_ancestry_table": {f"{g}|{a}": ct[(g, a)]
                                             for g in levels_g for a in levels_a},
                    "zero_cells": len(zeros), "zero_cell_labels": zeros,
                    "phi": phi, "design_full_rank": rank == X.shape[1],
                    "design_condition_number": cond})
        put("group_x_ancestry_cells", "zero_cells", len(zeros))
        put("group_x_ancestry_cells", "phi", phi)
        put("group_x_ancestry_cells", "design_full_rank", rank == X.shape[1])
        put("group_x_ancestry_cells", "condition_number", cond)
        st = "FAIL" if zeros else "WARN"
        put("group_x_ancestry_cells", "class_status", st, st,
            "empty stratum forces extrapolation of adjusted disease coefficient")
    rec["check_group_x_ancestry_cells"] = st

    # ---- 3. replicates + donor overlap -------------------------------------
    nd = len(set(donors))
    rec.update({"n_donors": nd, "arrays_per_donor": round(n / max(nd, 1), 3),
                "technical_replicate_arrays": n - nd})
    put("replicate_donor_overlap", "n_donors", nd)
    put("replicate_donor_overlap", "arrays_per_donor", round(n / max(nd, 1), 3))
    overlap = 0
    if extra_platforms:
        for other in extra_platforms:
            overlap = max(overlap, len(set(donors) & set(other)))
    rec["cross_platform_shared_donors"] = overlap
    put("replicate_donor_overlap", "cross_platform_shared_donors", overlap)
    st = "WARN" if (n > nd or overlap > 0) else "PASS"
    rec["check_replicate_donor_overlap"] = st
    put("replicate_donor_overlap", "class_status", st, st,
        "same RNA re-hybridised / same donor across platforms is pseudo-replication")

    # ---- 4. annotation availability ----------------------------------------
    a = annot_stats(platform, m["ids"])
    rec["annotation"] = a
    for k in ("status", "mapped_ids", "matrix_ids_covered", "coverage_pct"):
        put("annotation_availability", k, a.get(k))
    st = "PASS" if a["status"] == "available" and a.get("coverage_pct", 0) > 0 else "FAIL"
    rec["check_annotation_availability"] = st
    put("annotation_availability", "class_status", st, st,
        "missing annotation is a missing-data limitation, NEVER a negative result")

    # ---- 5. scale + excluded groups ----------------------------------------
    if flat:
        arr = np.array(flat, dtype=float)
        med = float(np.median(arr)); mx = float(np.max(arr)); mn = float(np.min(arr))
        log2_like = bool(mx <= 20 and med < 14)
        rec.update({"value_min": round(mn, 3), "value_median": round(med, 3),
                    "value_max": round(mx, 3), "scale_inference":
                    "log2-like" if log2_like else "linear-like"})
        put("scale_excluded_groups", "value_median", round(med, 3))
        put("scale_excluded_groups", "value_max", round(mx, 3))
        put("scale_excluded_groups", "scale_inference", rec["scale_inference"])
    else:
        log2_like = None
        put("scale_excluded_groups", "scale_inference", "undetermined")
    excl = labels.count("excluded")
    rec["excluded_arrays"] = excl
    put("scale_excluded_groups", "excluded_arrays", excl)
    st = "WARN" if (excl > 0 or log2_like is False) else "PASS"
    rec["check_scale_excluded_groups"] = st
    put("scale_excluded_groups", "class_status", st, st,
        "OHT arm excluded by design; linear MAS5 values require log2 transform")
    rec["checks"] = {c: rec.get("check_" + c) for c in CHECKS}
    return rec, metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", action="append", default=[],
                    help="extra series_matrix.txt.gz to audit (repeatable)")
    ap.add_argument("--out", default="results_audit")
    ap.add_argument("--tables", default="tables")
    a = ap.parse_args()
    out = os.path.join(ROOT, a.out)
    tdir = os.path.join(ROOT, a.tables)
    os.makedirs(out, exist_ok=True)
    os.makedirs(tdir, exist_ok=True)

    targets = [(s, pf, fn, "primary") for s, pf, fn in DEFAULT_MATRICES]
    for p in a.matrix:
        base = os.path.basename(p)
        pm = re.search(r"GPL\d+", base)
        sm = re.match(r"(GSE\d+)", base)
        # `p` is a path relative to ROOT, e.g. external_inputs/GSE...txt.gz
        platform = pm.group(0) if pm else (detect_platform(p) or "UNKNOWN")
        targets.append((sm.group(1) if sm else "EXTRA",
                        platform, p, "external-candidate (metadata only)"))

    # pre-compute donor sets for cross-platform overlap within a series
    donor_sets = {}
    for s, pf, fn, role in targets:
        try:
            donor_sets[fn] = donor_ids(read_matrix(os.path.join(ROOT, fn)))
        except Exception:
            donor_sets[fn] = []

    records, metrics = [], []
    for s, pf, fn, role in targets:
        try:
            others = [donor_sets[g] for g in donor_sets
                      if g != fn and os.path.basename(g).startswith(s + "-")]
            rec, met = audit_one(s, pf, fn, extra_platforms=others, role=role)
            records.append(rec); metrics.extend(met)
            print("%-24s arrays=%2d donors=%2d free_text=%s zero_cells=%s annot=%s scale=%s" %
                  (rec["dataset"], rec["n_arrays"], rec["n_donors"],
                   rec["checks"]["free_text_covariates"],
                   rec["zero_cells"], rec["annotation"]["status"],
                   rec.get("scale_inference")), flush=True)
        except Exception as e:
            print("AUDIT FAILED %s: %s %s" % (fn, type(e).__name__, e), flush=True)
            metrics.append({"dataset": fn, "category": "audit_error", "metric": "exception",
                            "value": type(e).__name__, "status": "FAIL", "evidence": str(e)[:160]})

    # long report
    with open(os.path.join(out, "audit_report.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["dataset", "category", "metric", "value",
                                          "status", "evidence"])
        w.writeheader()
        for r in metrics:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in w.fieldnames})

    # wide checklist
    wide_cols = ["dataset", "role", "series", "platform", "n_arrays", "n_donors",
                 "n_probes", "compound_free_text_cells", "structured_age_cells",
                 "structured_sex_cells", "zero_cells", "phi", "design_full_rank",
                 "cross_platform_shared_donors", "annotation_status",
                 "annotation_source", "annotation_coverage_pct",
                 "scale_inference", "excluded_arrays"] + \
                ["check_" + c for c in CHECKS]
    with open(os.path.join(out, "audit_checklist.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=wide_cols)
        w.writeheader()
        for r in records:
            w.writerow({
                "dataset": r["dataset"], "role": r["role"],
                "series": r["series"], "platform": r["platform"],
                "n_arrays": r["n_arrays"], "n_donors": r["n_donors"],
                "n_probes": r["n_probes"],
                "compound_free_text_cells": r["compound_free_text_cells"],
                "structured_age_cells": r["structured_age_cells"],
                "structured_sex_cells": r["structured_sex_cells"],
                "zero_cells": r["zero_cells"], "phi": r["phi"],
                "design_full_rank": r["design_full_rank"],
                "cross_platform_shared_donors": r["cross_platform_shared_donors"],
                "annotation_status": r["annotation"]["status"],
                "annotation_source": r["annotation"].get("source", ""),
                "annotation_coverage_pct": r["annotation"].get("coverage_pct"),
                "scale_inference": r.get("scale_inference"),
                "excluded_arrays": r["excluded_arrays"],
                **{"check_" + c: r["checks"][c] for c in CHECKS}})

    # summary: occurrence of each defect class across audited matrices
    summary = {"generated_by": "geo_metadata_audit.py",
               "n_matrices": len(records),
               "completeness_rule": COMPLETENESS,
               "defect_occurrence": {},
               "constraints": [
                   "'probe not mapped' is a missing-annotation limitation, never a negative result",
                   "same-series platforms sharing donor IDs are repeated hybridisations, not independent cohorts",
                   "a full-rank design can still contain an empty group x ancestry stratum",
                   "detectable-effect / power statements are post hoc and are not equivalence tests"]}
    for c in CHECKS:
        summary["defect_occurrence"][c] = {
            "FAIL": sum(1 for r in records if r["checks"][c] == "FAIL"),
            "WARN": sum(1 for r in records if r["checks"][c] == "WARN"),
            "PASS": sum(1 for r in records if r["checks"][c] == "PASS"),
            "NOT_APPLICABLE": sum(1 for r in records if r["checks"][c] == "NOT_APPLICABLE")}
    with open(os.path.join(out, "audit_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with open(os.path.join(out, "audit_records.json"), "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False, default=str)

    # Table S16
    lines = [
        "# Table S16. Reusable GEO metadata audit: five defect classes",
        "",
        "Generated by `geo_metadata_audit.py` (read-only; no input or `results/` file modified).",
        "Six matrices are the primary re-analysis inputs; the seventh row is an "
        "**external candidate series audited for metadata only** - no differential "
        "expression was run on it, no result was entered into any table, and it "
        "must not be described as an independent replication.",
        "Status legend: FAIL = defect present and materially affects the model; "
        "WARN = requires explicit handling; PASS = no defect detected; "
        "NOT_APPLICABLE = field absent. `zero_cells` counts empty "
        "group x ancestry strata; `phi` is the 2x2 group-ancestry correlation "
        "with the Caucasian-reference indicator (identical coding to the "
        "primary model's `race_Caucasian` term); `design_full_rank` refers to "
        "the [1, glaucoma, ancestry] matrix.",
        "",
        "| Dataset | Role | Arrays | Donors | Free-text covariates | Zero cells | phi | Full rank | Shared donors | Annotation | Scale | Excluded arms |",
        "|---|---|---:|---:|---|---:|---:|---|---:|---|---|---:|",
    ]
    for r in records:
        asrc = r["annotation"].get("source", "")
        alab = r["annotation"]["status"] + \
               (" (rebuilt)" if "rebuilt" in asrc else
                " (GEO)" if asrc else "")
        lines.append("| %s | %s | %d | %d | %s | %s | %s | %s | %d | %s (%s%%) | %s | %d |" %
                     (r["dataset"], r["role"], r["n_arrays"], r["n_donors"],
                      r["checks"]["free_text_covariates"],
                      "n/a" if r["zero_cells"] is None else r["zero_cells"],
                      "n/a" if r["phi"] is None else r["phi"],
                      "n/a" if r["design_full_rank"] is None else r["design_full_rank"],
                      r["cross_platform_shared_donors"],
                      alab,
                      r["annotation"].get("coverage_pct", 0),
                      r.get("scale_inference", "undetermined"),
                      r["excluded_arrays"]))
    lines += ["", "## Occurrence across audited matrices", "",
              "| Defect class | FAIL | WARN | PASS | NOT_APPLICABLE |", "|---|---:|---:|---:|---:|"]
    for c in CHECKS:
        d = summary["defect_occurrence"][c]
        lines.append("| %s | %d | %d | %d | %d |" %
                     (c, d["FAIL"], d["WARN"], d["PASS"], d["NOT_APPLICABLE"]))
    lines += ["", "## Interpretation boundaries", "",
              "* GEO still returns 404 for `GPL5175.annot.gz`. The map used here was "
              "rebuilt locally from the complete 316,919-row SOFT platform table and "
              "covers 17,634 / 22,011 (80.11%) GSE45570 transcript clusters; it is "
              "NOT a GEO annotation file. Unmapped probes are missing annotation, "
              "never negative results.",
              "* Cross-platform shared donor IDs mean repeated hybridisations of "
              "the same RNA, not an independent cohort.",
              "* A zero cell with a full-rank design is a structural extrapolation "
              "problem, not classical collinearity.",
              "* For the external candidate GSE27276 the 36 deposited titles do not "
              "encode donor identifiers; the official GEO record documents paired "
              "eyes and one technical replicate, so the audit's `n_donors = "
              "n_arrays` is a parsing limitation, NOT evidence of 36 independent "
              "donors. Donor IDs must be reconstructed manually before any model "
              "is fitted.",
              "* This audit is descriptive. It does not re-fit any model, does not "
              "change the pre-specified primary M2, and does not change the 0/18 "
              "six-transcript conclusion.", ""]
    open(os.path.join(tdir, "TableS16_metadata_audit.md"), "w",
         encoding="utf-8").write("\n".join(lines))
    with open(os.path.join(tdir, "TableS16_metadata_audit.tsv"), "w",
              newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["dataset", "role", "n_arrays", "n_donors"] + ["check_" + c for c in CHECKS] +
                   ["zero_cells", "annotation_status", "annotation_coverage_pct",
                    "scale_inference", "excluded_arrays", "shared_donors"])
        for r in records:
            w.writerow([r["dataset"], r["role"], r["n_arrays"], r["n_donors"]] +
                       [r["checks"][c] for c in CHECKS] +
                       [r["zero_cells"], r["annotation"]["status"],
                        r["annotation"].get("coverage_pct", 0),
                        r.get("scale_inference"), r["excluded_arrays"],
                        r["cross_platform_shared_donors"]])

    open(os.path.join(out, "README.md"), "w", encoding="utf-8").write(
        "# geo_metadata_audit outputs\n\n"
        "Read-only audit of %d GEO series matrices (five defect classes).\n\n"
        "* `audit_report.csv` - long-form per-metric rows\n"
        "* `audit_checklist.csv` - wide checklist, one row per matrix\n"
        "* `audit_summary.json` - defect occurrence counts and interpretation boundaries\n"
        "* `audit_records.json` - full machine-readable record per matrix\n"
        "* `tables/TableS16_metadata_audit.md|tsv` - manuscript-ready supplementary table\n\n"
        "Reuse: `python geo_metadata_audit.py --matrix NEW_series_matrix.txt.gz`.\n"
        "The script never writes to `results/`, never edits an input matrix and "
        "never treats missing annotation as a negative result.\n" % len(records))
    print("WROTE %d metrics, %d records -> %s + TableS16" %
          (len(metrics), len(records), out), flush=True)
    return 0 if len(records) == len(targets) else 1


if __name__ == "__main__":
    sys.exit(main())

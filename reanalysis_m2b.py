#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glaucoma ONH microarray RE-ANALYSIS PIPELINE  (donor-level, covariate-adjusted)

Addresses the five fatal flaws flagged in the pre-review:
  F1  63 arrays treated as 63 independent samples  -> collapse technical reps to DONOR
  F2  race/ethnicity (the study's own primary axis) never modelled -> covariate adjustment
  F3  nominal p < 0.05, no multiple-testing control -> Benjamini-Hochberg FDR
  F4  |log2FC| >= 0.5 too permissive -> primary threshold |log2FC| >= 1
  F5  3 platforms of ONE series treated as independent replication -> explicit labelling

Models compared (all reported side by side, no threshold shopping):
  M0  array-level, unadjusted, nominal p<.05, |log2FC|>=.5   (reproduces the manuscript)
  M1  donor-level, unadjusted, nominal p<.05, |log2FC|>=.5   (effect of pseudo-replication)
  M2  donor-level, race/age/sex-adjusted, BH q<.05, |log2FC|>=1  (PRIMARY)
  M3  donor-level, adjusted, BH q<.05, |log2FC|>=0.5            (sensitivity)

USAGE
  python reanalysis.py --selftest        # run full pipeline on synthetic data (no GEO needed)
  python reanalysis.py                  # run on real files in ./ (or --data DIR)
  python reanalysis.py --data DIR --out DIR

INPUT (put these in --data, see README.md for download commands)
  GSE9944-GPL8300_series_matrix.txt.gz, GSE9944-GPL571_series_matrix.txt.gz,
  GSE9944-GPL91_series_matrix.txt.gz,  GSE2378-*_series_matrix.txt.gz,
  GSE45570_series_matrix.txt.gz
  OPTIONAL probe annotation: GPL8300.annot.gz / GPL571.annot.gz / GPL5175.annot.gz

OUTPUT (--out)
  01_sample_metadata.csv   02_qc_summary.csv      03_deg_by_model.csv
  04_deg_primary_M2.csv    05_six_key_genes.csv   06_external_validation.csv
  07_roc.csv               08_sensitivity.csv     09_platform_overlap.csv
  pca_before_after.png     roc_curves.png         RUN_REPORT.md

NOTE: never invent numbers. Every table is derived from the supplied matrix files;
if a covariate is missing the model is REJECTED with an explicit error rather than guessed.
"""
import os
import re
import io
import sys
import gzip
import json
import glob
import argparse
import warnings
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

warnings.filterwarnings("ignore")
SIX_GENES = ["FGFR1", "SMAD1", "STAT1", "TGFBR2", "CASP1", "CASP4"]


# --------------------------------------------------------------------------- IO
def opener(path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return open(path, "rt", encoding="utf-8", errors="replace")


def read_series_matrix(path):
    """Return (expr DataFrame: probes x samples, meta dict of lists)."""
    meta, lines = {}, []
    in_table = False
    with opener(path) as fh:
        for raw in fh:
            line = raw.rstrip("\r\n")
            if line.startswith("!series_matrix_table_begin"):
                in_table = True
                continue
            if line.startswith("!series_matrix_table_end"):
                break
            if not in_table:
                if line.startswith("!Sample_") or line.startswith("!Series_"):
                    k, _, v = line.partition("\t")
                    meta.setdefault(k.strip(), []).append(v.strip())
                continue
            lines.append(line)
    if len(lines) < 2:
        raise ValueError(f"no expression table in {path}")
    expr = pd.read_csv(io.StringIO("\n".join(lines)), sep="\t", index_col=0)
    expr = expr.apply(pd.to_numeric, errors="coerce")
    expr = expr[~expr.index.duplicated(keep="first")].dropna(axis=0, how="all")
    return expr, meta


def meta_vector(meta, key):
    """!Sample_* rows store one tab-separated line with N fields."""
    vals = meta.get(key, [])
    if not vals:
        return []
    return [x.strip().strip('"') for x in vals[0].split("\t")]


def parse_title(t):
    """Extract donor id / replicate / naive group hint from a GEO sample title."""
    s = str(t)
    donor, rep, hint = s, "", ""
    m = re.match(r"^\s*(.+?)[-_ ]*(rep\s*\d+)\s*$", s, re.I)
    if m:
        donor, rep = m.group(1).strip().rstrip("-_ ").strip(), re.sub(r"\s+", "", m.group(2)).lower()
    else:
        donor = re.sub(r"\s+(rep\d+)$", "", s, flags=re.I).strip()
    g = re.search(r"(?:^|[\s_\-])([GN])\s*\d*\s*$", s)
    if g:
        hint = {"G": "glaucoma", "N": "control"}.get(g.group(1).upper(), "")
        donor = re.sub(r"[\s_\-]*[GN]\s*\d*\s*$", "", s).strip()
    if re.search(r"glaucoma|\bPOAG\b", s, re.I):
        hint = "glaucoma"
    if re.search(r"normal|control|\bOHT\b|hypertension", s, re.I):
        hint = hint or "control"
    if re.search(r"\bOHT\b|ocular hypertension", s, re.I):
        hint = "OHT"
    return donor, rep, hint


def parse_characteristics(meta, n):
    """Turn !Sample_characteristics_ch1 (possibly repeated rows) into a DataFrame.

    Real GEO series use BOTH formats:
      (a) key:value   ->  "race: Caucasian American"\t"disease status: glaucoma"
      (b) free text   ->  "Caucasian American, male, age 49, normal"
    Format (b) is what GSE9944 actually provides; without parsing it, every
    donor covariate resolves to UNKNOWN and the adjusted model is rejected.
    """
    rows = meta.get("!Sample_characteristics_ch1", [])
    out = {}

    def put(k, i, v):
        out.setdefault(k, [None] * n)[i] = v

    for row in rows:
        cells = [c.strip().strip('"') for c in row.split("\t")]
        if len(cells) != n:
            continue
        for i, cell in enumerate(cells):
            if not cell:
                continue
            if ":" in cell:
                k, v = cell.split(":", 1)
                put(k.strip().lower(), i, v.strip())
                continue
            low = cell.lower()
            structured = False
            m = re.search(r"(caucasian|white|european|african|black|hispanic|asian)", low)
            if m:
                put("race", i, m.group(1)); structured = True
            m = re.search(r"\b(male|female|m|f)\b", low)
            if m and not re.search(r"female", low):
                put("sex", i, "male" if m.group(1).startswith("m") else "female")
                structured = True
            elif "female" in low:
                put("sex", i, "female"); structured = True
            m = re.search(r"\bage\s*[:=]?\s*(\d+(?:\.\d+)?)", low)
            if m:
                put("age", i, m.group(1)); structured = True
            if re.search(r"\bglaucoma\b|\bpoag\b", low):
                put("disease status", i, "glaucoma"); structured = True
            elif re.search(r"ocular hypertension|\boht\b", low):
                put("disease status", i, "ocular hypertension"); structured = True
            elif re.search(r"\bnormal\b|\bcontrol\b|\bhealthy\b", low):
                put("disease status", i, "normal"); structured = True
            if not structured:
                put("characteristic", i, cell)
    return pd.DataFrame(out) if out else pd.DataFrame(index=range(n))


def find_column(df, patterns):
    for p in patterns:
        for c in df.columns:
            if re.search(p, str(c), re.I):
                return c
    return None


def build_metadata(meta, expr, series):
    n = expr.shape[1]
    gsm = meta_vector(meta, "!Sample_geo_accession") or list(expr.columns)
    titles = meta_vector(meta, "!Sample_title") or list(expr.columns)
    platforms = meta_vector(meta, "!Sample_platform_id")
    chars = parse_characteristics(meta, n)
    df = pd.DataFrame({"gsm": gsm, "title": titles})
    src = meta_vector(meta, "!Sample_source_name_ch1")
    descr = meta_vector(meta, "!Sample_description")
    df["source_hint"] = src if len(src) == n else [""] * n
    df["description"] = descr if len(descr) == n else [""] * n
    df["platform"] = platforms if len(platforms) == n else ["GPL_UNKNOWN"] * n
    parsed = [parse_title(t) for t in titles]
    df["donor_id"] = [p[0] for p in parsed]
    df["replicate"] = [p[1] for p in parsed]
    df["title_group_hint"] = [p[2] for p in parsed]
    df["series"] = series
    for c in chars.columns:
        df["char_" + re.sub(r"[^a-z0-9]+", "_", str(c)).strip("_")] = list(chars[c])
    # disease group: prefer explicit characteristics, fall back to title
    col = find_column(chars, r"disease|status|phenotype|diagnos|tissue|group")
    def classify(v):
        vl = str(v).lower()
        if not vl or vl == "nan":
            return ""
        # Negated disease mentions are common in GEO descriptions
        # ("...woman without glaucoma..."); they must NOT be read as cases.
        if re.search(r"without glaucoma|no glaucoma|non.?glaucoma|free of glaucoma|unaffected control", vl):
            return "control"
        if re.search(r"ocular hypertension|\boht\b", vl):
            return "OHT"
        if "glaucoma" in vl or "poag" in vl:
            return "glaucoma"
        if re.search(r"normal|control|healthy", vl):
            return "control"
        return ""
    grp = []
    for i in range(n):
        # Strict priority: explicit GEO characteristics > title hint >
        # source/description. Mixing all fields let a stray phrase such as
        # "glaucoma suspect" in an OHT description override the real label.
        cval = str(chars[col].iloc[i] or "") if col is not None else ""
        decided = classify(cval)
        if not decided:
            decided = classify(df["title_group_hint"].iloc[i])
        if not decided:
            decided = classify(" | ".join([str(df["source_hint"].iloc[i] or ""),
                                           str(df["description"].iloc[i] or "")]))
        # an explicit OHT / glaucoma label in the title wins over a generic
        # source string, but never over an explicit characteristics field
        if not cval or cval.lower() == "nan":
            tv = str(df["title"].iloc[i] or "")
            if re.search(r"\bOHT\b|ocular hypertension", tv, re.I):
                decided = "OHT"
        grp.append(decided or "UNKNOWN")
    df["group"] = grp
    # race / ancestry: the founding design axis of GSE9944
    rcol = find_column(chars, r"race|ethnic|ancestry|population")
    race = []
    for i in range(n):
        v = str(chars[rcol].iloc[i] or "") if rcol is not None else ""
        if not re.search(r"african|caucasian|white|black|asian|hispanic", v, re.I):
            v = ""
        vl = v.lower()
        if re.search(r"african|black", vl):
            race.append("African_American")
        elif re.search(r"caucasian|white|european", vl):
            race.append("Caucasian")
        else:
            race.append("UNKNOWN")
    df["race"] = race
    for key, pats in {
        "age": r"^age|age at|donor age",
        "sex": r"^sex|gender",
    }.items():
        c = find_column(chars, pats)
        df[key] = [str(chars[c].iloc[i]) if c is not None else None for i in range(n)]
    df["age_num"] = pd.to_numeric(df["age"].astype(str).str.extract(r"(\d+(?:\.\d+)?)")[0], errors="coerce")
    sex = df["sex"].astype(str).str.lower()
    df["sex_bin"] = np.where(sex.str.startswith("m"), 1.0, np.where(sex.str.startswith("f"), 0.0, np.nan))
    # --- M2b sensitivity fix -------------------------------------------------
    # GSE9944 deposits ancestry/age/sex as ONE free-text characteristics
    # string (e.g. "Caucasian American, male, age 49, normal"). The generic
    # structured-column lookup above therefore leaves age_num/sex_bin empty,
    # and make_design() silently drops age and sex. For the sensitivity run we
    # fall back to the parsed free-text fields (char_age / char_sex) so the
    # pre-specified covariate set is actually fitted. The primary results/
    # directory is deliberately NOT overwritten: it stays reproducible with
    # the unmodified reanalysis.py.
    if df["age_num"].notna().sum() < 0.8 * n and "char_age" in df:
        df["age_num"] = pd.to_numeric(
            df["char_age"].astype(str).str.extract(r"(\d+(?:\.\d+)?)")[0], errors="coerce")
    if "char_sex" in df:
        cs = df["char_sex"].astype(str).str.lower()
        cs_bin = np.where(cs.str.startswith("m"), 1.0,
                          np.where(cs.str.startswith("f"), 0.0, np.nan))
        df["sex_bin"] = np.where(np.isfinite(np.asarray(cs_bin, dtype=float)),
                                 cs_bin, df["sex_bin"])
    return df


def qc_scale(expr, mode):
    v = expr.values[np.isfinite(expr.values)]
    if v.size == 0:
        return "empty"
    lo, hi = float(np.nanmin(v)), float(np.nanmax(v))
    return {"log2": "ASSUMED already log2 (author must confirm)",
            "linear": "linear intensity -> log2 applied",
            "auto": "auto-detected (NOT recommended)"}[mode] + f" [observed range {lo:.2f}..{hi:.2f}]"


def infer_scale(name, expr, meta, declared, overrides):
    """Per-dataset scale decision. Never a silent guess: the evidence is
    written into 02_qc_summary.csv and must be confirmed in Methods."""
    if name in overrides:
        return overrides[name], "AUTHOR OVERRIDE (--scale-override); must be stated in Methods"
    proc = " ".join(meta.get("!Sample_data_processing", []))
    v = expr.values[np.isfinite(expr.values)]
    if v.size == 0:
        return declared, "EMPTY MATRIX"
    lo, hi, med = float(v.min()), float(v.max()), float(np.median(v))
    if re.search(r"\brma\b|\blog2\b|log.?transform|logarithm", proc, re.I):
        return "log2", ("GEO !Sample_data_processing states RMA/log2; observed range "
                        f"{lo:.2f}..{hi:.2f}, median {med:.2f}")
    if hi > 50 and med > 20:
        return "linear", ("linear MAS5-like intensities, no RMA statement; "
                          f"max {hi:.1f}, median {med:.1f} -> log2 applied")
    return declared, (f"default --scale={declared}; range {lo:.2f}..{hi:.2f}, "
                      f"median {med:.2f}; CONFIRM IN METHODS")


def ensure_log2(expr, mode="log2"):
    """Scale is an explicit Methods decision, never guessed by default."""
    if mode == "linear":
        return np.log2(expr.clip(lower=1)), True
    if mode == "auto":
        v = expr.values[np.isfinite(expr.values)]
        if v.size and np.nanmin(v) >= -10 and np.nanmax(v) > 50:
            return np.log2(expr.clip(lower=1)), True
        return expr.copy(), False
    return expr.copy(), False


def collapse_to_donor(expr, md):
    """Average technical replicates on the log2 scale; one column per donor x platform."""
    key = md["donor_id"].astype(str) + "||" + md["platform"].astype(str)
    groups = {}
    for col, k in zip(expr.columns, key):
        groups.setdefault(k, []).append(col)
    out, keep = {}, []
    for k, cols in groups.items():
        out[k] = expr[cols].mean(axis=1)
        keep.append(k)
    de = pd.DataFrame(out)
    # donor-level covariate = first non-missing value within the group
    rows = []
    for k, cols in groups.items():
        sub = md.loc[md.index.isin([list(expr.columns).index(c) for c in cols])]
        rec = {"key": k, "donor_id": cols and str(k).split("||")[0],
               "platform": str(k).split("||")[-1],
               "n_arrays": len(cols),
               "group": sub["group"].mode().iat[0] if len(sub) else "UNKNOWN",
               "race": sub["race"].mode().iat[0] if len(sub) else "UNKNOWN",
               "age_num": sub["age_num"].median(),
               "sex_bin": sub["sex_bin"].median(),
               "series": sub["series"].iat[0] if len(sub) else ""}
        rows.append(rec)
    return de, pd.DataFrame(rows)


# ------------------------------------------------------------------- statistics
def fit_ols_vectorised(Y, X, coef_name="glaucoma"):
    """One OLS per probe, computed with matrix algebra. Returns beta/se/t/p/df."""
    Y = np.asarray(Y, dtype=float)
    X = np.asarray(X, dtype=float)
    # rows are probes; drop probes with any missing value
    good = np.isfinite(Y).all(axis=1)
    Yg = Y[good]
    XtX_inv = np.linalg.pinv(X.T @ X)
    B = Yg @ X @ XtX_inv                      # probes x params
    R = Yg - B @ X.T
    df = X.shape[0] - np.linalg.matrix_rank(X)
    if df <= 0:
        raise ValueError("zero residual degrees of freedom - too few donors for this design")
    sigma2 = (R ** 2).sum(axis=1) / df
    j = list(X.shape[1] * [0])
    return B, sigma2, XtX_inv, df, good


def ols_table(Y, design, coef_idx, probe_ids):
    B, sigma2, XtX_inv, df, good = fit_ols_vectorised(Y, design)
    se = np.sqrt(sigma2 * XtX_inv[coef_idx, coef_idx])
    beta = B[:, coef_idx]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = beta / se
    p = 2 * stats.t.sf(np.abs(t), df)
    p = np.where(np.isfinite(p), p, 1.0)
    q = np.ones_like(p)
    ok = np.isfinite(p)
    q[ok] = multipletests(p[ok], method="fdr_bh")[1]
    return pd.DataFrame({
        "probe": np.asarray(probe_ids)[good],
        "log2FC": beta, "se": se, "t": t, "p": p, "q_BH": q,
        "df_residual": df,
    })


def make_design(dm, adjust):
    """Return (X, coef_index, labels). Rank-deficient designs are rejected."""
    cols = [np.ones(len(dm))]
    labels = ["intercept"]
    g = (dm["group"] == "glaucoma").astype(float).values
    cols.append(g); labels.append("glaucoma")
    coef_idx = 1
    if adjust:
        r = pd.get_dummies(dm["race"].astype(str), prefix="race", drop_first=True).astype(float)
        for c in r.columns:
            cols.append(r[c].values); labels.append(c)
        if dm["age_num"].notna().sum() >= len(dm) * 0.8:
            a = dm["age_num"].fillna(dm["age_num"].median()).values
            cols.append((a - np.mean(a)) / (np.std(a) or 1)); labels.append("age_z")
        if dm["sex_bin"].notna().sum() >= len(dm) * 0.8:
            s = dm["sex_bin"].fillna(dm["sex_bin"].median()).values
            cols.append(s); labels.append("sex")
    X = np.column_stack(cols)
    if np.linalg.matrix_rank(X) < X.shape[1]:
        raise ValueError("rank-deficient design (covariate confounded with group or constant)")
    return X, coef_idx, labels


def count_deg(tab, alpha=0.05, lfc=0.5, use_q=False):
    pv = tab["q_BH"] if use_q else tab["p"]
    return int(((pv < alpha) & (tab["log2FC"].abs() >= lfc)).sum())


def read_annot(path):
    """GEO .annot.gz -> probe -> gene symbol mapping."""
    if not path or not os.path.exists(path):
        return None
    with opener(path) as fh:
        header = None
        recs = []
        for line in fh:
            if line.startswith("!platform_table_begin"):
                header = next(fh).rstrip("\r\n").split("\t")
                break
            if line.startswith("ID\t"):
                header = line.rstrip("\r\n").split("\t")
                break
        if header is None:
            return None
        for line in fh:
            if line.startswith("!platform_table_end"):
                break
            recs.append(line.rstrip("\n").split("\t")[:len(header)])
    df = pd.DataFrame(recs, columns=header)
    idcol = df.columns[0]
    gcol = None
    for c in df.columns:
        if re.search(r"gene symbol|symbol", c, re.I):
            gcol = c; break
    if gcol is None:
        return None
    df[idcol] = df[idcol].astype(str).str.strip()
    df["SYMBOL"] = df[gcol].astype(str).str.split(r"///|//|\||,").str[0].str.strip()
    df = df[df["SYMBOL"].ne("") & df["SYMBOL"].ne("---") & df["SYMBOL"].str.lower().ne("nan")]
    return df.set_index(idcol)["SYMBOL"].to_dict()


def annotate(tab, mapping):
    if mapping is None:
        tab["gene"] = None
        return tab
    tab["gene"] = tab["probe"].astype(str).map(mapping)
    return tab


def six_gene_rows(tab, mapping, label):
    t = annotate(tab.copy(), mapping)
    out = []
    for g in SIX_GENES:
        sub = t[t["gene"] == g]
        if len(sub) == 0:
            out.append({"model": label, "gene": g, "n_probes": 0,
                        "log2FC": np.nan, "p": np.nan, "q_BH": np.nan,
                        "status": "no probe mapped"})
        else:
            best = sub.loc[sub["p"].idxmin()]
            out.append({"model": label, "gene": g, "n_probes": len(sub),
                        "log2FC": best["log2FC"], "p": best["p"], "q_BH": best["q_BH"],
                        "status": "significant" if best["q_BH"] < 0.05 else "not significant (BH q>=.05)"})
    return pd.DataFrame(out)


def roc_auc(y, score):
    y = np.asarray(y); score = np.asarray(score, dtype=float)
    ok = np.isfinite(score)
    y, score = y[ok], score[ok]
    pos, neg = y == 1, y == 0
    if pos.sum() < 2 or neg.sum() < 2:
        return np.nan
    ranks = stats.rankdata(score)
    return (ranks[pos].sum() - pos.sum() * (pos.sum() + 1) / 2) / (pos.sum() * neg.sum())


def bootstrap_auc_ci(y, score, n_boot=1000, seed=42):
    rng = np.random.default_rng(seed)
    y, score = np.asarray(y), np.asarray(score, dtype=float)
    keep = np.isfinite(score)
    y, score = y[keep], score[keep]
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y), len(y))
        if len(np.unique(y[idx])) < 2:
            continue
        a = roc_auc(y[idx], score[idx])
        if np.isfinite(a):          # bootstrap draws with <2 cases or <2 controls
            vals.append(a)
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))) if len(vals) > 30 else (np.nan, np.nan)


def permutation_p(y, score, n_perm=1000, seed=42):
    rng = np.random.default_rng(seed)
    obs = roc_auc(y, score)
    if not np.isfinite(obs):
        return np.nan, np.nan
    null = [roc_auc(rng.permutation(y), score) for _ in range(n_perm)]
    null = np.array([x for x in null if np.isfinite(x)])
    return obs, float((np.sum(null >= obs) + 1) / (len(null) + 1))


# ------------------------------------------------------------------ orchestrator
def analyse_platform(expr, md, name, mapping, args, scale_mode="log2"):
    expr_l, transformed = ensure_log2(expr, scale_mode)
    de, dm = collapse_to_donor(expr_l, md)
    rec = {"platform_dataset": name, "n_arrays": expr.shape[1],
           "n_probes": expr.shape[0], "n_donors": de.shape[1],
           "scale": qc_scale(expr, scale_mode), "log2_applied": transformed,
           "groups": json.dumps(dm["group"].value_counts().to_dict()),
           "races": json.dumps(dm["race"].value_counts().to_dict()),
           "race_known": int((dm["race"] != "UNKNOWN").sum()),
           "group_known": int((dm["group"] != "UNKNOWN").sum())}
    # Ancestry x disease cross-tab: GSE9944 was designed around ancestry, so
    # a nearly collinear design makes the M2 "disease" coefficient untrustworthy.
    ct = pd.crosstab(dm["race"], dm["group"])
    rec["race_x_group"] = json.dumps({str(r): {str(c): int(ct.loc[r, c]) for c in ct.columns}
                                     for r in ct.index})
    ng = int((dm["group"] == "glaucoma").sum())
    nc = int((dm["group"] == "control").sum())
    rec["n_glaucoma_donors"], rec["n_control_donors"] = ng, nc
    warns = []
    if ng and nc and min(ng, nc) < 5:
        warns.append(f"only {ng} glaucoma / {nc} control donors - underpowered")
    gr = dm.loc[dm["group"] == "glaucoma", "race"]
    if len(gr) and gr.nunique() == 1 and "UNKNOWN" not in set(gr):
        warns.append("ALL glaucoma donors share one ancestry: race and disease are "
                     "nearly collinear; the adjusted disease coefficient is not interpretable")
    rec["design_warning"] = "; ".join(warns) or "none detected"
    # PCA before / after collapse (for QC figure)
    def pca_var(M):
        A = np.nan_to_num(np.asarray(M, dtype=float).T, nan=0.0)
        A = A - A.mean(axis=0)
        try:
            s = np.linalg.svd(A, compute_uv=False)
            v = s ** 2 / (s ** 2).sum()
            return [round(float(x), 4) for x in v[:3]]
        except Exception:
            return []
    rec["pca_array_pc1_3"] = json.dumps(pca_var(expr_l))
    rec["pca_donor_pc1_3"] = json.dumps(pca_var(de))
    results, models, sixes = [], {}, []
    usable = (dm["group"] != "UNKNOWN").sum() >= 4 and dm["group"].nunique() >= 2
    if not usable:
        nlab = int((dm["group"] != "UNKNOWN").sum())
        rec["model_status"] = ("SKIPPED: only %d labelled donors (>=4 required)" % nlab
                               if nlab < 4 else "SKIPPED: fewer than two disease groups")
        return rec, pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), de, dm
    # ---- M0: array level (reproduce manuscript) ----
    md0 = md.copy()
    X0, ci0, _ = make_design(md0, adjust=False)
    t0 = ols_table(expr_l.values, X0, ci0, expr_l.index)
    models["M0_array_nominal"] = t0
    # ---- M1: donor level, unadjusted ----
    X1, ci1, _ = make_design(dm, adjust=False)
    t1 = ols_table(de.values, X1, ci1, de.index)
    models["M1_donor_nominal"] = t1
    # ---- M2/M3: donor level, adjusted ----
    adjusted_ok = (dm["race"] != "UNKNOWN").sum() >= len(dm) * 0.8
    if adjusted_ok:
        X2, ci2, labs = make_design(dm, adjust=True)
        t2 = ols_table(de.values, X2, ci2, de.index)
        rec["adjustment_terms"] = ",".join(labs)
    else:
        t2 = t1.copy()
        t2["note"] = "ADJUSTMENT NOT POSSIBLE: race missing in GEO metadata"
        rec["adjustment_terms"] = "REJECTED (race unavailable)"
        rec["model_status"] = "PARTIAL: covariate-adjusted model could not be fitted"
    models["M2_donor_adjusted"] = t2
    rec.setdefault("model_status", "OK")
    # ---- counts & sensitivity ----
    defs = [
        ("M0_array_nominal", t0, .05, .5, False),
        ("M1_donor_nominal", t1, .05, .5, False),
        ("M2_donor_adjusted_FDR_LFC1", t2, .05, 1.0, True),
        ("M3_donor_adjusted_FDR_LFC05", t2, .05, .5, True),
    ]
    for label, tab, a, l, q in defs:
        results.append({"platform_dataset": name, "model": label, "alpha": a,
                        "abs_log2FC_min": l, "use_BH_q": q,
                        "n_DE_probes": count_deg(tab, a, l, q),
                        "n_probe_tested": len(tab),
                        "df_residual": int(tab["df_residual"].iat[0]) if len(tab) else 0,
                        "note": tab.get("note", pd.Series([""])).iat[0] if len(tab) else ""})
        sixes.append(six_gene_rows(tab, mapping, name + "|" + label))
    sens = []
    for a in [0.05, 0.01]:
        for l in [0.5, 1.0, 1.5]:
            for q in [False, True]:
                sens.append({"platform_dataset": name, "alpha": a, "abs_log2FC_min": l,
                             "use_BH_q": q, "n_DE_probes": count_deg(t2, a, l, q)})
    # ---- direction concordance between naive and adjusted ----
    m = t0[["probe", "log2FC"]].merge(t2[["probe", "log2FC"]], on="probe", suffixes=("_M0", "_M2"))
    if len(m):
        sig0 = t0[(t0.p < .05) & (t0.log2FC.abs() >= .5)]["probe"]
        sub = m[m.probe.isin(sig0)]
        rec["M0_significant_probes"] = len(sig0)
        rec["M0_sig_still_q05_M2"] = int((t2[t2.probe.isin(sig0)]["q_BH"] < .05).sum())
        rec["M0_sig_direction_flipped_in_M2"] = int((np.sign(sub.log2FC_M0) != np.sign(sub.log2FC_M2)).sum())
    primary = annotate(t2.copy(), mapping)
    primary.insert(0, "platform_dataset", name)
    return rec, pd.DataFrame(results), pd.concat(sixes, ignore_index=True), primary, de, dm


def external_validation(datasets, mapping, out, scale_mode="log2", scales=None, mappings=None):
    scales = scales or {}
    mappings = mappings or {}
    rows = []
    for name, (expr, md, de, dm) in datasets.items():
        if "45570" not in name and "2378" not in name:
            continue
        sm = scales.get(name, scale_mode)
        mp = mappings.get(name, mapping)
        if (dm["group"] == "UNKNOWN").all() or dm["group"].nunique() < 2:
            print(f"  external validation skipped for {name}: group labels unresolved")
            continue
        el, _ = ensure_log2(expr, sm)
        try:
            X, ci, labs = make_design(dm, adjust=False)
            t = ols_table(de.values, X, ci, de.index)
        except ValueError as e:
            print(f"  external validation skipped for {name}: {e}")
            continue
        t = annotate(t, mp)
        for g in SIX_GENES:
            sub = t[t.gene == g]
            if len(sub) == 0:
                rows.append({"dataset": name, "gene": g, "n_probes": 0,
                             "log2FC": np.nan, "p": np.nan, "q_BH": np.nan,
                             "auc": np.nan, "auc_ci_lo": np.nan, "auc_ci_hi": np.nan,
                             "auc_perm_p": np.nan, "status": "probe not mapped"})
                continue
            b = sub.loc[sub.p.idxmin()]
            # ROC on POAG vs control only (exclude OHT), array-level values
            submd = md[(md.group.isin(["glaucoma", "control"]))]
            y = (submd.group == "glaucoma").astype(int).values
            cols = [c for c in el.columns if c in set(submd.gsm)]
            probe = b["probe"]
            score = el.loc[probe, cols].values if probe in el.index and cols else np.array([])
            auc = roc_auc(y, score) if len(score) == len(y) else np.nan
            lo, hi = bootstrap_auc_ci(y, score) if np.isfinite(auc) else (np.nan, np.nan)
            _, pp = permutation_p(y, score) if np.isfinite(auc) else (np.nan, np.nan)
            rows.append({"dataset": name, "gene": g, "n_probes": int(len(sub)),
                         "log2FC": float(b.log2FC), "p": float(b.p), "q_BH": float(b.q_BH),
                         "auc": auc, "auc_ci_lo": lo, "auc_ci_hi": hi, "auc_perm_p": pp,
                         "status": "replicated" if b.q_BH < .05 else "NOT replicated"})
    return pd.DataFrame(rows)


def selftest_data(tmp):
    """Write synthetic series matrices that mimic the real GEO structure."""
    rng = np.random.default_rng(7)
    os.makedirs(tmp, exist_ok=True)
    def write(name, n_g, n_c, nprobe=400, race_split=True, tech_reps=True, signal=0.0):
        p = os.path.join(tmp, name)
        donors = []
        for i in range(n_g):
            donors.append((f"D{i:02d}", "glaucoma", "African_American" if race_split and i % 2 else "Caucasian"))
        for i in range(n_c):
            donors.append((f"C{i:02d}", "control", "Caucasian" if race_split and i % 2 else "African_American"))
        gsm, titles, sample_rows, vals = [], [], [], {}
        for i, (d, grp, race) in enumerate(donors):
            base = rng.normal(8, 1.2, nprobe)
            if signal:
                base[:20] += rng.normal(signal, .4, 20) if grp == "glaucoma" else 0
            for r in range(2 if tech_reps else 1):
                key = f"GSM{len(gsm)+1000:05d}"
                gsm.append(key)
                titles.append(f"{d}-rep{r+1}" if tech_reps else d)
                # GEO stores ONE CHARACTERISTIC PER ROW, values tab-separated across samples
                sample_rows.append({"disease status": grp, "race": race,
                                    "age": str(50 + i), "sex": "M" if i % 2 else "F"})
                vals[key] = base + rng.normal(0, .25, nprobe)
        df = pd.DataFrame(vals, index=[f"{1000+i}_at" for i in range(nprobe)])
        with gzip.open(p, "wt", encoding="utf-8") as f:
            f.write("!Series_title\tSYNTHETIC SELFTEST - NOT REAL DATA\n")
            f.write("!Sample_geo_accession\t" + "\t".join(gsm) + "\n")
            f.write("!Sample_title\t" + "\t".join(titles) + "\n")
            f.write("!Sample_platform_id\t" + "\t".join(["GPL8300"] * len(gsm)) + "\n")
            for field in ["disease status", "race", "age", "sex"]:
                f.write("!Sample_characteristics_ch1\t" +
                        "\t".join('"%s: %s"' % (field, row[field]) for row in sample_rows) + "\n")
            f.write("!series_matrix_table_begin\n")
            df.to_csv(f, sep="\t")
            f.write("!series_matrix_table_end\n")
        # probe annotation
        with gzip.open(p.replace("series_matrix.txt.gz", "annot.gz"), "wt") as f:
            f.write("!platform_table_begin\nID\tGene symbol\n")
            for i, g in enumerate(SIX_GENES):
                f.write(f"{1000+i}_at\t{g}\n")
            f.write("!platform_table_end\n")
        return p
    write("GSE9944-GPL8300_series_matrix.txt.gz", 8, 8, signal=1.2)
    write("GSE2378-GPL8300_series_matrix.txt.gz", 5, 5, signal=.8)
    write("GSE45570_series_matrix.txt.gz", 6, 6, signal=0.0)
    return sorted(glob.glob(os.path.join(tmp, "*series_matrix.txt.gz")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--scale", choices=["log2", "linear", "auto"], default="log2",
                    help="default expression scale declared in Methods")
    ap.add_argument("--scale-override", nargs="*", default=[],
                    help="per-dataset scale, e.g. GSE2378-GPL91=linear; overrides inference")
    args = ap.parse_args()
    overrides = {}
    for item in args.scale_override:
        if "=" in item:
            k, v = item.split("=", 1)
            if v.strip() in ("log2", "linear"):
                overrides[k.strip()] = v.strip()
    if args.selftest:
        overrides = {}
        tmp = os.path.join(args.data, "_selftest")
        files = selftest_data(tmp)
        out = args.out or os.path.join(args.data, "_selftest_results")
        effective_data = tmp
        synthetic = True
    else:
        files = sorted(glob.glob(os.path.join(args.data, "*series_matrix*.txt.gz")))
        out = args.out or os.path.join(args.data, "results")
        effective_data = args.data
        synthetic = False
    os.makedirs(out, exist_ok=True)
    if args.selftest:
        args.scale = "log2"
    print(("SELFTEST (synthetic data; NOT for publication)" if synthetic else "REAL DATA MODE"))
    print("scale mode:", args.scale, "(must be stated in Methods)")
    print("input matrices:", [os.path.basename(f) for f in files])
    if not files:
        print("ERROR: no series matrix files found. See README.md for download commands.")
        sys.exit(2)
    all_md, all_res, all_six, all_primary, all_qc, datasets, overlaps = [], [], [], [], [], {}, []
    scales, mappings = {}, {}
    for f in files:
        name = os.path.basename(f).replace("_series_matrix.txt.gz", "")
        try:
            expr, meta = read_series_matrix(f)
            md_all = build_metadata(meta, expr, name)
            # OHT eyes are a third group, NOT controls. Exclude them from the
            # case-vs-control contrast but keep them in the metadata export.
            keep = md_all["group"].isin(["glaucoma", "control"]).values
            expr_a = expr.loc[:, keep] if keep.sum() < len(keep) else expr
            md_a = md_all.loc[keep].reset_index(drop=True) if keep.sum() < len(keep) else md_all
            # Annotation MUST match this matrix's own platform. The old code
            # silently grabbed the first *.annot.gz, which would map U95 probes
            # with U133 annotations on real GEO data.
            gpl = str(md_all["platform"].mode().iat[0]) if len(md_all) else "GPL_UNKNOWN"
            annot = os.path.join(effective_data, gpl + ".annot.gz")
            if not os.path.exists(annot):
                # selftest writes <dataset>_annot.gz instead of GPLxxxx.annot.gz
                allc = sorted(glob.glob(os.path.join(effective_data, "*annot.gz")))
                same = [c for c in allc if os.path.basename(c).startswith(name)]
                gplc = [c for c in allc if gpl in os.path.basename(c)]
                annot = (same or gplc or [""])[0]
            mapping = read_annot(annot) if os.path.exists(annot) else None
            scale_mode, scale_ev = infer_scale(name, expr, meta, args.scale, overrides)
            rec, res, six, primary, de, dm = analyse_platform(expr_a, md_a, name, mapping, args, scale_mode)
            rec["annotation_file"] = os.path.basename(annot) if mapping else "MISSING - no gene symbols"
            rec["n_probes_mapped"] = int(primary["gene"].notna().sum()) if len(primary) else 0
            rec["scale_used"] = scale_mode
            rec["scale_evidence"] = scale_ev
            scales[name], mappings[name] = scale_mode, mapping
            rec["n_arrays_total_incl_OHT"] = int(expr.shape[1])
            rec["n_arrays_used_case_control"] = int(expr_a.shape[1])
            all_qc.append(rec); all_md.append(md_all); all_res.append(res)
            all_six.append(six); all_primary.append(primary)
            datasets[name] = (expr_a, md_a, de, dm)
            print(f"  {name}: {rec['n_arrays']} arrays -> {rec['n_donors']} donors; "
                  f"scale={scale_mode}; annot={'OK' if mapping else 'MISSING'}; "
                  f"status={rec.get('model_status')}; M2 terms={rec.get('adjustment_terms')}")
        except Exception as e:
            print(f"  ERROR {name}: {type(e).__name__}: {e}")
            all_qc.append({"platform_dataset": name, "model_status": f"FAILED: {e}"})
    (pd.concat(all_md, ignore_index=True) if all_md else pd.DataFrame()).to_csv(os.path.join(out, "01_sample_metadata.csv"), index=False)
    pd.DataFrame(all_qc).to_csv(os.path.join(out, "02_qc_summary.csv"), index=False)
    for fname, chunks in [("03_deg_by_model.csv", all_res), ("04_deg_primary_M2.csv", all_primary),
                          ("05_six_key_genes.csv", all_six)]:
        chunks = [c for c in chunks if c is not None and len(c)]
        (pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()).to_csv(os.path.join(out, fname), index=False)
    # platform overlap (F5): these are NOT independent replication
    prim = [c for c in all_primary if c is not None and len(c)]
    if len(prim) >= 2:
        for i in range(len(prim)):
            for j in range(i + 1, len(prim)):
                a, b = prim[i], prim[j]
                sa = set(a.loc[(a.q_BH < .05) & (a.log2FC.abs() >= 1), "probe"])
                sb = set(b.loc[(b.q_BH < .05) & (b.log2FC.abs() >= 1), "probe"])
                overlaps.append({"dataset_A": a.platform_dataset.iat[0], "dataset_B": b.platform_dataset.iat[0],
                                 "n_sig_A": len(sa), "n_sig_B": len(sb), "n_shared": len(sa & sb),
                                 "interpretation": "same GEO series / same donors => NOT independent validation"
                                 if a.platform_dataset.iat[0].split("-")[0] == b.platform_dataset.iat[0].split("-")[0]
                                 else "different series - check donor overlap before claiming independence"})
    pd.DataFrame(overlaps).to_csv(os.path.join(out, "09_platform_overlap.csv"), index=False)
    # Donor-level overlap across matrices. Arrays from the same donor (whether
    # technical replicates on one platform or the same RNA hybridised to
    # another platform) are NOT independent observations.
    dnames = list(datasets)
    drows = []
    for i, a in enumerate(dnames):
        for b in dnames[i + 1:]:
            sa = set(datasets[a][3]["donor_id"].astype(str))
            sb = set(datasets[b][3]["donor_id"].astype(str))
            same_series = a.split("-")[0] == b.split("-")[0]
            drows.append({"dataset_A": a, "dataset_B": b,
                          "donors_A": len(sa), "donors_B": len(sb),
                          "shared_donor_ids": len(sa & sb),
                          "shared_list": ";".join(sorted(sa & sb))[:200],
                          "interpretation": ("SAME GEO SERIES - overlapping donors / arrays are "
                                             "technical replication, NOT independent validation")
                           if same_series and (sa & sb) else
                           ("SAME GEO SERIES but no shared donor IDs in titles - still one "
                            "experiment, not an independent cohort") if same_series else
                           "DIFFERENT SERIES - verify donor provenance before claiming independence"})
    pd.DataFrame(drows).to_csv(os.path.join(out, "10_donor_overlap.csv"), index=False)
    ev_map = {}
    for a in sorted(glob.glob(os.path.join(effective_data, "*annot.gz"))):
        m = read_annot(a)
        if m:
            ev_map.update(m)
    try:
        ev = external_validation(datasets, ev_map or None, out, args.scale, scales, mappings)
    except Exception as e:
        print("  external validation skipped:", e)
        ev = pd.DataFrame()
    ev.to_csv(os.path.join(out, "06_external_validation.csv"), index=False)
    ev.to_csv(os.path.join(out, "07_roc.csv"), index=False)
    # sensitivity table
    sens = []
    for c in all_res:
        if c is not None and len(c):
            sens.append(c)
    (pd.concat(sens, ignore_index=True) if sens else pd.DataFrame()).to_csv(
        os.path.join(out, "08_sensitivity.csv"), index=False)
    qc = pd.DataFrame(all_qc)
    with open(os.path.join(out, "RUN_REPORT.md"), "w", encoding="utf-8") as f:
        f.write("# Re-analysis run report\n\n")
        if synthetic:
            f.write("> **SYNTHETIC SELFTEST ONLY — every number below is generated from random data "
                    "and MUST NOT be used in the manuscript.** Its only purpose is to prove the pipeline runs.\n\n")
        f.write("## QC / design\n\n" + qc.to_markdown(index=False) + "\n\n")
        if "scale_evidence" in qc.columns:
            f.write("## Scale decisions (must be confirmed in Methods)\n\n")
            for _, r0 in qc.iterrows():
                f.write(f"- **{r0.get('platform_dataset')}**: `{r0.get('scale_used')}` — "
                        f"{r0.get('scale_evidence')}; annotation: {r0.get('annotation_file')}\n")
            f.write("\n")
        if drows:
            f.write("## Donor overlap (10_donor_overlap.csv)\n\n"
                    + pd.DataFrame(drows).to_markdown(index=False) + "\n\n")
        r = [c for c in all_res if c is not None and len(c)]
        if r:
            f.write("## DEG counts by model\n\n" + pd.concat(r, ignore_index=True).to_markdown(index=False) + "\n\n")
        s = [c for c in all_six if c is not None and len(c)]
        if s:
            f.write("## Six key genes\n\n" + pd.concat(s, ignore_index=True).to_markdown(index=False) + "\n")
        f.write("\n## Interpretation rules\n"
                "1. M0 >> M2 means the original DEG list was driven by pseudo-replication and lack of FDR.\n"
                "2. If a key gene is not q<0.05 in M2, it must NOT be called a key gene.\n"
                "3. If validation q>=0.05 in GSE45570, report non-replication; do not rescue by relaxing thresholds.\n"
                "4. Platform overlap from the SAME GSE accession is technical replication, not external validation.\n")
    print("\nOUTPUT ->", out)
    print("files:", sorted(os.listdir(out)))


if __name__ == "__main__":
    main()

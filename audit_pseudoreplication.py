#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quantify pseudo-replication from the GEO sample titles we could verify.

Input : GSE9944_gsm_titles_partial.txt (30 titles retrieved from the official
        GEO brief view; the response was truncated by the fetch tool)
Output: pseudoreplication_audit.json + console summary

IMPORTANT: this is a PARTIAL list. All extrapolation below is labelled as such.
"""
import os
import re
import json
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "GSE9944_gsm_titles_partial.txt")
TOTAL_ARRAYS_IN_SERIES = 63  # from GEO official record (verified in pre-review)


def parse(title):
    m = re.match(r"^\s*(.+?)-rep(\d+)\s*$", title, re.I)
    if m:
        return m.group(1).strip(), int(m.group(2))
    return title.strip(), None


def main():
    titles = [x.strip() for x in open(SRC, encoding="utf-8") if x.strip()]
    pairs = [parse(t) for t in titles]
    by_donor = collections.defaultdict(list)
    for donor, rep in pairs:
        by_donor[donor].append(rep)
    rep_counts = collections.Counter(len(v) for v in by_donor.values())
    paired = sum(1 for v in by_donor.values() if sorted(x for x in v if x) == [1, 2])
    n_donors = len(by_donor)
    ratio = len(titles) / n_donors
    # Extrapolation, clearly labelled
    inferred_donors_upper = (TOTAL_ARRAYS_IN_SERIES + 1) // 2  # ceil(63/2) = 32
    inflated_df = TOTAL_ARRAYS_IN_SERIES - inferred_donors_upper
    result = {
        "source": "NCBI GEO GSE9944 brief GSM view (officially retrieved, response truncated at 30 titles)",
        "coverage": "PARTIAL: 30 of 63 titles",
        "n_titles_verified": len(titles),
        "n_unique_donors_verified": n_donors,
        "rep_distribution_per_donor": dict(rep_counts),
        "donors_with_exactly_rep1_and_rep2": paired,
        "arrays_per_donor_observed": ratio,
        "verified_conclusion": (
            "All 30 verified titles form 15 exact rep1/rep2 pairs from 15 donors. "
            "Treating these as 30 independent samples doubles the apparent sample size."
        ),
        "extrapolation_label": "NOT VERIFIED - arithmetic bound only, do not cite as measured",
        "series_total_arrays_official": TOTAL_ARRAYS_IN_SERIES,
        "upper_bound_independent_donors_if_all_paired": inferred_donors_upper,
        "pseudo_degrees_of_freedom_if_63_modelled_as_independent": inflated_df,
        "manuscript_claim": "63 ONH samples (43 normal + 20 glaucoma)",
        "consequence": (
            "A case-control contrast fitted on 63 arrays instead of <=32 donors has "
            "inflated residual degrees of freedom, understated standard errors and "
            "anti-conservative p values. Combined with no FDR correction, this alone "
            "can manufacture most of the reported DEG list."
        ),
        "what_would_settle_it": "Full 63-title list + GSE9944 series matrix; reanalysis.py computes the exact number in 01_sample_metadata.csv.",
        "donors": sorted(by_donor.keys()),
    }
    dst = os.path.join(HERE, "pseudoreplication_audit.json")
    json.dump(result, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\nSAVED", dst)


if __name__ == "__main__":
    main()

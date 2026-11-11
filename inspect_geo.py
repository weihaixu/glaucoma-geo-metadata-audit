#!/usr/bin/env python3
"""Inspect downloaded GEO files: sample metadata, value scale, probe IDs.

Read-only. Produces data/inspection.json consumed by reanalysis.py.
"""
import os
import re
import json
import gzip
import glob

HERE = os.path.dirname(os.path.abspath(__file__))


def opener(path):
    return gzip.open(path, "rt", encoding="utf-8", errors="replace") if path.endswith(".gz") else open(path, "rt", encoding="utf-8", errors="replace")


def inspect_matrix(path):
    meta, rows, header = {}, [], None
    in_table = False
    with opener(path) as fh:
        for line in fh:
            line = line.rstrip("\r\n")
            if line.startswith("!series_matrix_table_begin"):
                in_table = True
                continue
            if line.startswith("!series_matrix_table_end"):
                break
            if not in_table:
                if line.startswith("!Sample_"):
                    k, _, v = line.partition("\t")
                    meta.setdefault(k.strip(), []).append(v.strip().strip('"'))
                continue
            if header is None:
                header = line.split("\t")
                continue
            if len(rows) < 3:
                rows.append(line.split("\t"))
    return {
        "file": os.path.basename(path),
        "n_samples": len(meta.get("!Sample_geo_accession", [[]])[0].split("\t")) if meta.get("!Sample_geo_accession") else len(header) - 1,
        "n_cols": len(header) - 1 if header else 0,
        "titles": meta.get("!Sample_title", []),
        "platforms": meta.get("!Sample_platform_id", []),
        "characteristics": meta.get("!Sample_characteristics_ch1", []),
        "source": meta.get("!Sample_source_name_ch1", []),
        "description": [x[:400] for x in meta.get("!Sample_description", [])],
        "header_first": header[:6] if header else [],
        "first_rows": [r[:6] for r in rows],
    }


def inspect_soft(path):
    """Count SOFT sections; report whether platform/sample tables are embedded."""
    counts = {"^SERIES": 0, "^SAMPLE": 0, "^PLATFORM": 0}
    sample_table = 0
    platform_table = 0
    first_ids = []
    sample_lines = []
    with opener(path) as fh:
        for line in fh:
            for k in counts:
                if line.startswith(k):
                    counts[k] += 1
            if line.startswith("!Sample_table_begin"):
                sample_table += 1
            if line.startswith("!platform_table_begin"):
                platform_table += 1
            if line.startswith("!Sample_characteristics_ch1") and len(sample_lines) < 8:
                sample_lines.append(line.strip()[:200])
            if line.startswith("^SAMPLE") and len(first_ids) < 5:
                first_ids.append(line.strip())
    return {
        "file": os.path.basename(path),
        "counts": counts,
        "sample_tables": sample_table,
        "platform_tables": platform_table,
        "first_samples": first_ids,
        "sample_chars": sample_lines,
    }


if __name__ == "__main__":
    out = {"matrices": [], "soft": [], "annot": []}
    for p in sorted(glob.glob(os.path.join(HERE, "*series_matrix*.gz"))):
        try:
            out["matrices"].append(inspect_matrix(p))
        except Exception as e:
            out["matrices"].append({"file": os.path.basename(p), "error": str(e)})
    for p in sorted(glob.glob(os.path.join(HERE, "*family.soft.gz"))):
        try:
            out["soft"].append(inspect_soft(p))
        except Exception as e:
            out["soft"].append({"file": os.path.basename(p), "error": str(e)})
    for p in sorted(glob.glob(os.path.join(HERE, "*annot.gz"))):
        out["annot"].append({"file": os.path.basename(p), "bytes": os.path.getsize(p)})
    dst = os.path.join(HERE, "inspection.json")
    json.dump(out, open(dst, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(json.dumps(out, indent=2, ensure_ascii=False)[:12000])
    print("\nSAVED", dst)

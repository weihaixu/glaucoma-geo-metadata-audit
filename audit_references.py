"""Audit the 69 references of the original manuscript against v0.4 citation markers.

Read-only with respect to the original docx: parses work/manuscript_full.txt.
Writes work/data/references_audit.tsv / .json and prints a compact summary.
"""
import csv
import json
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
FULL = os.path.join(WORK, "manuscript_full.txt")
MAN = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.4.md")
OUT_TSV = os.path.join(ROOT, "references_audit.tsv")
OUT_JSON = os.path.join(ROOT, "references_audit.json")

# --- parse the 69 numbered references from the extracted original text ---
refs = {}
pat = re.compile(r"^\[\d{3}\]\s+(\d+)\.\s+(.*)$")
for line in open(FULL, encoding="utf-8"):
    m = pat.match(line.rstrip("\n"))
    if m:
        refs[int(m.group(1))] = m.group(2).strip()
assert set(refs) == set(range(1, 70)), "expected 69 references, got %d" % len(refs)

# --- citation markers in v0.4 body (numeric only) ---
s = open(MAN, encoding="utf-8").read()
# strip the non-paper front matter (version note) to avoid counting instructions
body = s.split("## Abstract", 1)[1]
marker = re.compile(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]")
used = Counter()
marker_hits = []
for m in marker.finditer(body):
    tok = m.group(1)
    nums = set()
    for part in re.split(r"\s*,\s*", tok):
        if "-" in part:
            a, b = part.split("-", 1)
            try:
                nums.update(range(int(a), int(b) + 1))
            except ValueError:
                pass
        elif part.strip().isdigit():
            nums.add(int(part.strip()))
    if nums:
        marker_hits.append((m.group(0), sorted(nums)))
        for n in nums:
            used[n] += 1

# --- classification (documented, reproducible rules) ---
COVID = {11, 12, 20, 28, 39, 56, 57, 58, 59, 67, 68, 69}
CROSS_DISEASE = {14, 16, 17, 29, 41, 42, 43, 48, 49, 50, 51, 53, 54, 55,
                 60, 61, 62, 63, 64, 65, 66, 23, 27, 30, 31, 32, 33, 34, 35, 40}
PREPRINT = {59, 67}
FORMAT_ISSUE = {8, 29, 59, 67}

def classify(n):
    tags = []
    if n in COVID:
        tags.append("COVID/antiviral sidetrack")
    if n in CROSS_DISEASE:
        tags.append("cross-disease extrapolation")
    if n in PREPRINT:
        tags.append("preprint")
    if n in FORMAT_ISSUE:
        tags.append("format/accuracy issue")
    if n not in used:
        tags.append("UNCITED in v0.4")
    if not tags:
        tags.append("retained candidate")
    return "; ".join(tags)

rows = []
for n in range(1, 70):
    txt = refs[n]
    yr = re.search(r"\b(19|20)\d{2}\b", txt)
    doi = re.search(r"doi:\s*(\S+)", txt, re.I)
    rows.append({
        "ref_no": n,
        "times_cited_in_v0.4": used.get(n, 0),
        "year": yr.group(0) if yr else "",
        "doi_or_url": doi.group(1) if doi else "",
        "classification": classify(n),
        "original_entry": txt,
    })

with open(OUT_TSV, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t")
    w.writeheader()
    w.writerows(rows)

summary = {
    "n_references_original": len(refs),
    "n_distinct_cited_in_v0.4": len(used),
    "n_citation_markers": len(marker_hits),
    "cited_numbers": sorted(used),
    "uncited_numbers": [n for n in range(1, 70) if n not in used],
    "covid_sidetrack": sorted(COVID),
    "cross_disease": sorted(CROSS_DISEASE),
    "preprints": sorted(PREPRINT),
    "citation_markers": [{"marker": a, "refs": b} for a, b in marker_hits],
}
with open(OUT_JSON, "w", encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=2)

print("original refs:", len(refs))
print("distinct cited in v0.4:", len(used), sorted(used))
print("markers:", len(marker_hits))
print("uncited:", summary["uncited_numbers"])
print("classification counts:", dict(Counter(r["classification"].split(";")[0] for r in rows)))
print("wrote", OUT_TSV, OUT_JSON)

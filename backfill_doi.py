# -*- coding: utf-8 -*-
"""Back-fill a real Zenodo DOI into manuscript v1.1 in three places.

Usage:
    D:/anaconda3/python.exe backfill_doi.py 10.5281/zenodo.1234567
    D:/anaconda3/python.exe backfill_doi.py 10.5281/zenodo.1234567 --dry-run

The three places are asserted to match exactly once each:
  1. Methods 2.6 (software and reproducibility)  - archive sentence
  2. Data availability                            - derived-file archive sentence
  3. Code availability                            - repository / DOI sentence

Refuses to run while identity placeholders remain, because a DOI-bearing
manuscript with empty author fields is not a submittable object. Run
apply_v11.py after filling data/author_profile.json first.

Nothing else is touched; v1.0 and all earlier versions stay byte-identical.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

W = Path(__file__).resolve().parent.parent
D = Path(__file__).resolve().parent
MAN = W / "青光眼生信稿件_全文重写稿_v1.1.md"

argv = [a for a in sys.argv[1:] if not a.startswith("--")]
DRY = "--dry-run" in sys.argv
if len(argv) != 1:
    sys.exit("usage: backfill_doi.py <DOI> [--dry-run]")

doi = argv[0].strip()
if not re.fullmatch(r"10\.\d{4,9}/zenodo\.\d{4,}", doi):
    sys.exit("DOI does not look like a Zenodo DOI: %r" % doi)

s = MAN.read_text(encoding="utf-8")

left = s.count("[AUTHOR INPUT REQUIRED")
if left:
    sys.exit("refusing: %d author placeholder(s) remain. Fill data/author_profile.json "
             "and rerun apply_v11.py first." % left)

EDITS = [
    ("An archived, version-locked copy of the code and derived tables will be deposited at Zenodo and cited by DOI in the final version.",
     "An archived, version-locked copy of the code and derived tables is deposited at Zenodo (doi:%s)." % doi,
     "Methods 2.6"),
    ("`tables/file_manifest.csv` (SHA-256 checksums) contain all derived files.",
     "`tables/file_manifest.csv` (SHA-256 checksums) contain all derived files; the archived snapshot is at doi:%s." % doi,
     "Data availability"),
    ("Archived at Zenodo, DOI:",
     "Archived at Zenodo, DOI: %s" % doi,
     "Code availability"),
]

# Code availability now reads "Archived at Zenodo, DOI: <repo>; repository: ..." when
# the profile supplied a code_doi. Normalise: strip any existing DOI token first.
s = re.sub(r"Archived at Zenodo, DOI:\s*(10\.5281/zenodo\.\d+)?", "Archived at Zenodo, DOI:", s)

for old, new, tag in EDITS:
    n = s.count(old)
    assert n == 1, "anchor %s matched %d times" % (tag, n)
    s = s.replace(old, new, 1)

# Exactly three occurrences of the DOI after the edit.
assert s.count("10.5281/zenodo.") == 3, s.count("10.5281/zenodo.")

print("DOI: %s" % doi)
for _, _, tag in EDITS:
    print("  filled:", tag)
print("occurrences:", s.count("10.5281/zenodo."))

if DRY:
    print("dry run - manuscript not written")
    sys.exit(0)

with open(MAN, "w", encoding="utf-8", newline="") as f:
    f.write(s)
print("written:", MAN.name)
print("\nnext: D:/anaconda3/python.exe cold_read_v10_postdoi.py")

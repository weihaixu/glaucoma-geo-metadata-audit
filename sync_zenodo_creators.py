# -*- coding: utf-8 -*-
"""Write Zenodo creators and licence from data/author_profile.json.

Usage:
    D:/anaconda3/python.exe sync_zenodo_creators.py --check   # dry run, reports gaps
    D:/anaconda3/python.exe sync_zenodo_creators.py --write

Zenodo needs one entry per author with a name in "Family, Given" order and an
affiliation; ORCID is optional but recommended. The script refuses to write
while any required field is empty, so the bundle can never claim an author
list that the profile does not contain.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
REL = D / "release" / ".zenodo.json"
PROF = D / "author_profile.json"

prof = json.loads(PROF.read_text(encoding="utf-8"))
z = json.loads(REL.read_text(encoding="utf-8"))

AFFS = [str(a).strip() for a in (prof.get("affiliations") or []) if str(a).strip()]
raw = prof.get("authors") or []
corr_email = str(prof.get("corresponding_email", "")).strip()

entries = []
for a in raw:
    if isinstance(a, dict):
        name = str(a.get("name", "")).strip()
        if name:
            entries.append({
                "name": name,
                "family": str(a.get("family", "")).strip(),
                "given": str(a.get("given", "")).strip(),
                "affiliations": a.get("affiliations") or [],
                "orcid": str(a.get("orcid", "")).strip(),
                "corr": bool(a.get("corresponding")),
            })
    elif str(a).strip():
        entries.append({"name": str(a).strip(), "family": "", "given": "",
                        "affiliations": [], "orcid": "", "corr": False})

gaps = []
if not entries:
    gaps.append("authors (list of names or objects)")
if not AFFS:
    gaps.append("affiliations")
if not corr_email:
    gaps.append("corresponding_email")
if not (prof.get("licence") or "").strip():
    gaps.append("licence")

print("profile: %d author(s), %d affiliation(s)" % (len(entries), len(AFFS)))
for e in entries:
    print("  -", e["name"], "(aff %s)" % (e["affiliations"] or "default"), "corresponding" if e["corr"] else "")
for g in gaps:
    print("  MISSING:", g)

if gaps:
    print("\nnot written: fill the fields above in data/author_profile.json")
    sys.exit(1)

creators = []
for e in entries:
    # Zenodo/DataCite wants "Family, Given"; the profile keeps the display
    # order used on the title page, so the two must be stated explicitly.
    if e["family"] and e["given"]:
        cname = "%s, %s" % (e["family"], e["given"])
    else:
        cname = e["name"]
        print("  WARNING: %r has no family/given split; using display order" % cname)
    c = {"name": cname}
    ids = e["affiliations"] or [1]
    aff_txt = "; ".join(AFFS[i - 1] for i in ids
                        if isinstance(i, int) and 0 < i <= len(AFFS)) or "; ".join(AFFS)
    if aff_txt:
        c["affiliation"] = aff_txt
    if e["orcid"]:
        c["orcid"] = e["orcid"]
    creators.append(c)

z["metadata"]["creators"] = creators
z["metadata"]["license"] = {"id": str(prof["licence"]).strip()}
z["metadata"]["upload_type"] = "software"

# --- optional version bump (tag/version, title suffix, cold-read claim)
ver = ""
if "--version" in sys.argv:
    i = sys.argv.index("--version")
    ver = str(sys.argv[i + 1]).strip() if i + 1 < len(sys.argv) else ""
if ver:
    z["metadata"]["version"] = ver
    t = str(z["metadata"].get("title", ""))
    z["metadata"]["title"] = re.sub(r"\(v[\d.]+\)\s*$", "(%s)" % ver, t)
    d = str(z["metadata"].get("description", ""))
    d = re.sub(r"Manuscript v[\d.]+ is journal-neutral\.", "Manuscript %s is journal-neutral." % ver, d)
    passed = ""
    if "--pass" in sys.argv:
        j = sys.argv.index("--pass")
        passed = str(sys.argv[j + 1]).strip() if j + 1 < len(sys.argv) else ""
    if passed:
        d = re.sub(r"Cold-read v[\d.]+: \d+/\d+ assertions pass",
                   "Cold-read %s: %s assertions pass" % (ver, passed), d)
    z["metadata"]["description"] = d

print("\ncreators -> %s" % json.dumps(creators, ensure_ascii=False))
print("licence  -> %s" % z["metadata"]["license"])
if ver:
    print("version  -> %s" % ver)
    print("title    -> %s" % z["metadata"]["title"])
    print("desc tail-> ...%s" % str(z["metadata"]["description"])[-190:])

if "--write" not in sys.argv:
    print("\ndry run: add --write to update release/.zenodo.json")
    sys.exit(0)

with open(REL, "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(z, indent=2, ensure_ascii=False) + "\n")
print("written:", REL)
print("next: build_release.py --build --allow-draft --zip --verify")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the Zenodo/GitHub release bundle for the v1.0 methodology-framed re-analysis.

Default (no flags): write UPLOAD_MANIFEST.tsv + DOWNLOAD_INPUTS.md and print a
READY / NOT READY status. Nothing is published by this script.

    D:/anaconda3/python.exe build_release.py                     # manifest + status
    D:/anaconda3/python.exe build_release.py --build            # copy to release_bundle/
    D:/anaconda3/python.exe build_release.py --build --zip      # also make release_bundle.zip
    D:/anaconda3/python.exe build_release.py --verify           # verify bundle sha256
    D:/anaconda3/python.exe build_release.py --build --include-inputs   # add raw GEO files

Guard rails: no synthetic self-tests, no chunk caches, no R package binaries, no
truncated downloads and no original GEO gz files (unless --include-inputs).
A NOT READY .zenodo.json (still containing __AUTHOR_INPUT_REQUIRED__) blocks
--build unless --allow-draft is given.
"""
import argparse
import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent          # work/data
RELEASE = DATA / "release"
BUNDLE = RELEASE / "release_bundle"
ZIP_PATH = RELEASE / "release_bundle.zip"
MANIFEST = RELEASE / "UPLOAD_MANIFEST.tsv"
FILE_MANIFEST = DATA / "tables" / "file_manifest.csv"
MANUSCRIPT = DATA.parent / "青光眼生信稿件_全文重写稿_v1.1.md"
PLACEHOLDER = "__AUTHOR_INPUT_REQUIRED__"

ROOT_DOCS = {"README.md", "REPRODUCIBILITY.md", "DECISION_LOG.md"}
ROOT_JSON = {
    "verified_references.json", "references_audit.json", "citation_remap.json",
    "pseudoreplication_audit.json", "GSE2378_metadata_audit.json",
    "GPL5175_annotation_status.json",
}
RESULT_DIRS = (
    "results", "results_m2b", "results_diagnostics",
    "results_limma", "results_genelevel", "results_power",
    "results_audit", "results_gpl5175", "results_external",
    "tables", "figures",
)
RELEASE_FILES = (
    ".zenodo.json", "ENVIRONMENT.md", "requirements.txt",
    "DECLARATIONS_12.md", "PUBLISH_STEPS.md", "DOWNLOAD_INPUTS.md",
    "build_release.py",
)
DERIVED_FILES = ("GPL5175.annot.gz",)
INPUT_GZ = (
    "GSE9944-GPL571_series_matrix.txt.gz", "GSE9944-GPL8300_series_matrix.txt.gz",
    "GSE9944-GPL91_series_matrix.txt.gz", "GSE2378-GPL8300_series_matrix.txt.gz",
    "GSE2378-GPL91_series_matrix.txt.gz", "GSE45570_series_matrix.txt.gz",
    "GPL8300.annot.gz", "GPL571.annot.gz", "GPL91.annot.gz",
)
BAD_PARTS = {
    "chunks", "chunks64", "chunks5175", "chunks_external",
    "external_inputs", "INCOMPLETE", "Rpackages", "Rlib", "__pycache__",
    "_selftest", "_selftest_results", "release_bundle",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def excluded(path, include_inputs):
    rel = path.relative_to(DATA).as_posix()
    parts = rel.split("/")
    if any(p in BAD_PARTS for p in parts):
        return True
    if any(p.startswith("results_trial") for p in parts):
        return True
    name = path.name
    if ".PARTIAL-DO-NOT-USE" in name or name.endswith(".log") or path.suffix in (".bin", ".pyc"):
        return True
    if name in ("UPLOAD_MANIFEST.tsv", "release_bundle.zip"):
        return True
    if path.suffix == ".gz" and not include_inputs:
        # GPL5175.annot.gz is a locally rebuilt DERIVED map, not a raw GEO
        # input; shipping the 200 KB file avoids re-downloading 219 chunks.
        if name == "GPL5175.annot.gz":
            return False
        return True
    return False


def dest_for(rel):
    return rel[len("release/"):] if rel.startswith("release/") else rel


def collect(include_inputs):
    seen, items = set(), []
    for d in RESULT_DIRS:
        base = DATA / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and not excluded(p, include_inputs):
                rel = p.relative_to(DATA).as_posix()
                if rel not in seen:
                    seen.add(rel)
                    items.append((p, dest_for(rel)))
    for p in sorted(DATA.iterdir()):
        if not p.is_file():
            continue
        keep = (p.suffix in (".py", ".R", ".tsv") or p.name in ROOT_DOCS or p.name in ROOT_JSON)
        if keep and not excluded(p, include_inputs):
            rel = p.relative_to(DATA).as_posix()
            if rel not in seen:
                seen.add(rel)
                items.append((p, dest_for(rel)))
    if include_inputs:
        for name in INPUT_GZ:
            p = DATA / name
            if p.is_file():
                rel = p.relative_to(DATA).as_posix()
                if rel not in seen:
                    seen.add(rel)
                    items.append((p, dest_for(rel)))
    for name in DERIVED_FILES:
        p = DATA / name
        if p.is_file() and not excluded(p, include_inputs):
            rel = p.relative_to(DATA).as_posix()
            if rel not in seen:
                seen.add(rel)
                items.append((p, dest_for(rel)))
    for name in RELEASE_FILES:
        p = RELEASE / name
        if p.is_file() and not excluded(p, include_inputs):
            rel = p.relative_to(DATA).as_posix()
            if rel not in seen:
                seen.add(rel)
                items.append((p, dest_for(rel)))
    return sorted(items, key=lambda x: x[1])


def write_download_inputs():
    rows = []
    with open(FILE_MANIFEST, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["path"].endswith(".gz") and ".PARTIAL" not in r["path"]:
                rows.append((r["path"], r["bytes"], r["sha256"]))
    lines = [
        "# Re-downloading the raw GEO inputs",
        "",
        "Raw series matrices and platform annotations are **not redistributed** in this",
        "archive by default. Re-download them into the repository root, then verify the",
        "SHA-256 values against `tables/file_manifest.csv` before running the pipeline.",
        "",
        "```bash",
        "D:/anaconda3/python.exe parallel_fetch.py --workers 3 --rounds 8 \\",
        "  --only GSE9944-GPL571_series_matrix.txt.gz GSE9944-GPL8300_series_matrix.txt.gz \\",
        "         GSE9944-GPL91_series_matrix.txt.gz GSE2378-GPL8300_series_matrix.txt.gz \\",
        "         GSE2378-GPL91_series_matrix.txt.gz GSE45570_series_matrix.txt.gz",
        "D:/anaconda3/python.exe parallel_fetch.py --workers 3 --rounds 8 \\",
        "  --only GPL8300.annot.gz GPL571.annot.gz GPL91.annot.gz",
        "```",
        "",
        "GEO has **no official** `GPL5175.annot.gz`. A local probe-to-gene map was",
        "rebuilt from the complete SOFT platform table (`results_gpl5175/`, Table S15);",
        "it covers 80.11% of GSE45570 transcript clusters and is used ONLY for an",
        "exploratory boundary check, never as validation. The 200 KB derived",
        "map `GPL5175.annot.gz` IS shipped in this archive; the 85 MB SOFT text",
        "prefix and all chunk caches are not. Unmapped probes remain missing",
        "annotation, never a negative result.",
        "",
        "| Input | Bytes | sha256 |",
        "|---|---:|---|",
    ]
    for name, size, digest in rows:
        lines.append("| `%s` | %s | `%s` |" % (name, size, digest))
    ext = DATA / "external_inputs"
    ext_files = ["GSE27276_series_matrix.txt.gz", "GPL2507.annot.gz"]
    if all((ext / f).is_file() for f in ext_files):
        lines += ["", "## Optional external candidate (cross-tissue concordance only)", "",
                  "These two files support `results_external/` (Tables S17-S18). "
                  "The GSE27276 contrast is an exploratory cross-tissue "
                  "directional-concordance exercise and a stress test of the "
                  "metadata audit. Disease is completely confounded with tissue "
                  "procurement and postmortem delay; this is NOT an independent "
                  "replication or a validation cohort. The raw files are not "
                  "redistributed.",
                  "", "| File | Bytes | sha256 |", "|---|---:|---|"]
        for nm in ext_files:
            p = ext / nm
            lines.append("| `%s` | %d | `%s` |" %
                         (nm, p.stat().st_size, sha256(p)))
    lines += ["", "Generated by `release/build_release.py`; no values are hand-entered.", ""]
    (RELEASE / "DOWNLOAD_INPUTS.md").write_text("\n".join(lines), encoding="utf-8")


def status():
    raw = (RELEASE / ".zenodo.json").read_text(encoding="utf-8")
    ready = PLACEHOLDER not in raw
    try:
        creators = json.loads(raw)["metadata"]["creators"]
        ready = ready and bool(creators)
    except Exception as exc:
        print("[ERROR] .zenodo.json invalid: %s" % exc)
        ready = False
    n_decl = MANUSCRIPT.read_text(encoding="utf-8").count("[AUTHOR INPUT REQUIRED") if MANUSCRIPT.exists() else -1
    print("Zenodo metadata : %s" % ("READY" if ready else "NOT READY (creators/licence placeholders remain)"))
    print("Manuscript      : %d / 12 author-declaration placeholders remain" % n_decl)
    return ready


def check_primary():
    lookup = {}
    with open(FILE_MANIFEST, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lookup[r["path"]] = r["sha256"]
    ok = True
    for rel in ("results/04_deg_primary_M2.csv", "results/07_roc.csv"):
        p = DATA / rel
        h = sha256(p) if p.is_file() else "MISSING"
        match = lookup.get(rel) == h
        ok &= match
        print("Primary %-34s %s  %s" % (rel, h[:12], "OK" if match else "MISMATCH"))
    return ok


def write_manifest(items):
    with open(MANIFEST, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["dest_path", "source_path", "bytes", "sha256"])
        for src, dest in items:
            w.writerow([dest, src.relative_to(DATA).as_posix(), src.stat().st_size, sha256(src)])
    return len(items)


def read_manifest():
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def build(rows, make_zip):
    BUNDLE.mkdir(parents=True, exist_ok=True)
    for r in rows:
        src = DATA / r["source_path"]
        dst = BUNDLE / r["dest_path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    shutil.copy2(MANIFEST, BUNDLE / "UPLOAD_MANIFEST.tsv")
    print("[BUILD] %d files copied to %s" % (len(rows), BUNDLE))
    if make_zip:
        with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for r in rows:
                z.write(BUNDLE / r["dest_path"], r["dest_path"])
            z.write(BUNDLE / "UPLOAD_MANIFEST.tsv", "UPLOAD_MANIFEST.tsv")
        print("[BUILD] archive: %s (%d bytes)" % (ZIP_PATH, ZIP_PATH.stat().st_size))


def verify(rows):
    bad = []
    for r in rows:
        p = BUNDLE / r["dest_path"]
        if not p.is_file():
            bad.append((r["dest_path"], "missing"))
        elif sha256(p) != r["sha256"]:
            bad.append((r["dest_path"], "sha mismatch"))
    extra = []
    declared = {r["dest_path"] for r in rows} | {"UPLOAD_MANIFEST.tsv"}
    for p in BUNDLE.rglob("*"):
        if p.is_file() and p.relative_to(BUNDLE).as_posix() not in declared:
            extra.append(p.relative_to(BUNDLE).as_posix())
    print("[VERIFY] %d files, %d mismatches, %d extra files" % (len(rows), len(bad), len(extra)))
    for d, why in bad[:10]:
        print("  FAIL %s (%s)" % (d, why))
    for d in extra[:10]:
        print("  EXTRA %s" % d)
    return not bad and not extra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="copy files into release_bundle/")
    ap.add_argument("--zip", action="store_true", help="also write release_bundle.zip")
    ap.add_argument("--verify", action="store_true", help="verify an existing bundle")
    ap.add_argument("--include-inputs", action="store_true", help="include the 9 raw GEO gz files")
    ap.add_argument("--allow-draft", action="store_true", help="allow --build while metadata is NOT READY")
    args = ap.parse_args()

    write_download_inputs()
    items = collect(args.include_inputs)
    n = write_manifest(items)
    total = sum(p.stat().st_size for p, _ in items)
    print("[MANIFEST] %d files, %.1f MB -> %s" % (n, total / 1048576.0, MANIFEST))
    ready = status()
    primary_ok = check_primary()
    if not primary_ok:
        print("[ERROR] primary result sha256 mismatch; do NOT publish")
        return 2

    rows = read_manifest()
    if args.build:
        if not ready and not args.allow_draft:
            print("[BLOCKED] .zenodo.json is NOT READY; fill the creators first (or use --allow-draft for a local dry run)")
            return 3
        build(rows, args.zip)
    if args.verify:
        return 0 if verify(rows) else 4
    print("[DONE] %s" % ("READY for author-side publishing" if ready else "NOT READY: author input required"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

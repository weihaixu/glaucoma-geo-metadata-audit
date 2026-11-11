# -*- coding: utf-8 -*-
"""Fetch Windows binary R packages into a project-local library.

Rationale: the primary M2 model was fitted with ordinary least squares in
Python. Round-9 task 1 asks for an independent limma (empirical-Bayes
moderated t) replication. R 4.2.0 is present at
`C:/Program Files/R/R-4.2.0`, but limma is not installed. We install into
`work/data/Rlib` so the user's R library is untouched and the analysis is
reproducible from the project directory alone.

Bioconductor blocks the default Python user-agent, so downloads go through
urllib with a browser UA; the packages are then installed from local zips.
"""
import gzip
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS = os.path.join(ROOT, "Rpackages")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"}
BIOC = "https://bioconductor.org/packages/3.15/bioc/bin/windows/contrib/4.2/"
CRAN = "https://cloud.r-project.org/bin/windows/contrib/4.2/"


def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


def find_version(base, package):
    txt = gzip.decompress(fetch(base + "PACKAGES.gz")).decode("utf-8", "replace")
    for block in txt.split("\n\n"):
        if re.search(r"^Package: %s$" % re.escape(package), block, re.M):
            m = re.search(r"^Version: (.+)$", block, re.M)
            return m.group(1).strip()
    raise RuntimeError("package %s not found at %s" % (package, base))


def main():
    os.makedirs(DOWNLOADS, exist_ok=True)
    targets = [
        ("limma", BIOC),
        ("statmod", CRAN),
    ]
    manifest = []
    for pkg, base in targets:
        ver = find_version(base, pkg)
        fn = "%s_%s.zip" % (pkg, ver)
        dest = os.path.join(DOWNLOADS, fn)
        if not os.path.exists(dest) or os.path.getsize(dest) < 10000:
            data = fetch(base + fn)
            with open(dest, "wb") as fh:
                fh.write(data)
            print("downloaded", fn, len(data), "bytes")
        else:
            print("cached", fn, os.path.getsize(dest), "bytes")
        manifest.append((pkg, ver, fn, os.path.getsize(dest)))
    with open(os.path.join(DOWNLOADS, "MANIFEST.tsv"), "w", encoding="utf-8") as fh:
        fh.write("package\tversion\tfile\tbytes\tsource\n")
        for (pkg, ver, fn, n), (_, base) in zip(manifest, targets):
            fh.write("%s\t%s\t%s\t%d\t%s\n" % (pkg, ver, fn, n, base))
    print("manifest written")


if __name__ == "__main__":
    main()

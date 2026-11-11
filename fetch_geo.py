#!/usr/bin/env python3
"""Fetch GEO SOFT / series-matrix files for the glaucoma re-analysis.

Robust to intermittent TLS handshake timeouts on ftp.ncbi.nlm.nih.gov.
Usage:  python fetch_geo.py            # download all known targets
        python fetch_geo.py --list     # just print the target list
"""
import os
import sys
import time
import socket
import hashlib
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
socket.setdefaulttimeout(60)

FTP = "https://ftp.ncbi.nlm.nih.gov/geo"
TARGETS = {
    # GSE9944: optic nerve head astrocytes, 63 arrays, SuperSeries GSE9963
    "GSE9944_family.soft.gz":
        f"{FTP}/series/GSE9nnn/GSE9944/soft/GSE9944_family.soft.gz",
    "GSE9944-GPL8300_series_matrix.txt.gz":
        f"{FTP}/series/GSE9nnn/GSE9944/matrix/GSE9944-GPL8300_series_matrix.txt.gz",
    "GSE9944-GPL571_series_matrix.txt.gz":
        f"{FTP}/series/GSE9nnn/GSE9944/matrix/GSE9944-GPL571_series_matrix.txt.gz",
    "GSE9944-GPL91_series_matrix.txt.gz":
        f"{FTP}/series/GSE9nnn/GSE9944/matrix/GSE9944-GPL91_series_matrix.txt.gz",
    # Platform annotation (probe -> gene symbol)
    "GPL8300_annot.gz":
        f"{FTP}/platforms/GPL8nnn/GPL8300/annot/GPL8300.annot.gz",
    "GPL571_annot.gz":
        f"{FTP}/platforms/GPL5nnn/GPL571/annot/GPL571.annot.gz",
    "GPL5175_annot.gz":
        f"{FTP}/platforms/GPL5nnn/GPL5175/annot/GPL5175.annot.gz",
    # GSE2378: same lab, ONH astrocytes, two platforms
    "GSE2378-GPL91_series_matrix.txt.gz":
        f"{FTP}/datasets/GSE2nnn/GSE2378/matrix/GSE2378-GPL91_series_matrix.txt.gz",
    "GSE2378-GPL8300_series_matrix.txt.gz":
        f"{FTP}/datasets/GSE2nnn/GSE2378/matrix/GSE2378-GPL8300_series_matrix.txt.gz",
    # GSE45570: whole ONH tissue, Exon 1.0 ST, POAG / OHT / control
    "GSE45570_series_matrix.txt.gz":
        f"{FTP}/series/GSE45nnn/GSE45570/matrix/GSE45570_series_matrix.txt.gz",
}


def fetch(name, url, retries=3):
    dst = os.path.join(HERE, name)
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        print(f"SKIP  {name} ({os.path.getsize(dst)} bytes already present)", flush=True)
        return True
    for k in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as r, open(dst + ".part", "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            size = os.path.getsize(dst + ".part")
            if size < 1000:
                raise IOError(f"suspiciously small payload: {size} bytes")
            os.replace(dst + ".part", dst)
            h = hashlib.sha256(open(dst, "rb").read()).hexdigest()[:16]
            print(f"OK    {name}  {size:,} bytes  sha256:{h}", flush=True)
            return True
        except Exception as e:
            print(f"RETRY {name} attempt {k+1}/{retries}: {type(e).__name__} {e}", flush=True)
            time.sleep(2)
    print(f"FAIL  {name}  {url}", flush=True)
    return False


if __name__ == "__main__":
    if "--list" in sys.argv:
        for n, u in TARGETS.items():
            print(n, u)
        sys.exit(0)
    ok = 0
    for n, u in TARGETS.items():
        ok += fetch(n, u)
    print(f"DONE  {ok}/{len(TARGETS)} files", flush=True)

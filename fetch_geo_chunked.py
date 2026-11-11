#!/usr/bin/env python3
"""Chunked, resumable GEO downloader (HTTP Range + thread pool).

The NCBI FTP-over-HTTPS endpoint throttles long single connections in this
network, so every file is fetched in 1 MiB ranges and reassembled locally.
Each chunk is cached under chunks/<filename>/ so a re-run resumes for free.
"""
import os
import sys
import time
import socket
import hashlib
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
CHUNK = 1 << 20
WORKERS = 6
socket.setdefaulttimeout(25)
UA = {"User-Agent": "Mozilla/5.0"}

FTP = "https://ftp.ncbi.nlm.nih.gov/geo"
# (filename, candidate URLs tried in order)
TARGETS = [
    ("GSE9944-GPL8300_series_matrix.txt.gz", [
        f"{FTP}/series/GSE9nnn/GSE9944/matrix/GSE9944-GPL8300_series_matrix.txt.gz"]),
    ("GSE9944-GPL571_series_matrix.txt.gz", [
        f"{FTP}/series/GSE9nnn/GSE9944/matrix/GSE9944-GPL571_series_matrix.txt.gz"]),
    ("GSE9944-GPL91_series_matrix.txt.gz", [
        f"{FTP}/series/GSE9nnn/GSE9944/matrix/GSE9944-GPL91_series_matrix.txt.gz"]),
    ("GSE2378-GPL91_series_matrix.txt.gz", [
        f"{FTP}/datasets/GSE2nnn/GSE2378/matrix/GSE2378-GPL91_series_matrix.txt.gz",
        f"{FTP}/series/GSE2nnn/GSE2378/matrix/GSE2378-GPL91_series_matrix.txt.gz"]),
    ("GSE2378-GPL8300_series_matrix.txt.gz", [
        f"{FTP}/datasets/GSE2nnn/GSE2378/matrix/GSE2378-GPL8300_series_matrix.txt.gz",
        f"{FTP}/series/GSE2nnn/GSE2378/matrix/GSE2378-GPL8300_series_matrix.txt.gz"]),
    ("GSE45570_series_matrix.txt.gz", [
        f"{FTP}/series/GSE45nnn/GSE45570/matrix/GSE45570_series_matrix.txt.gz",
        f"{FTP}/series/GSE45nnn/GSE45570/matrix/GSE45570-GPL5175_series_matrix.txt.gz"]),
    ("GPL8300.annot.gz", [f"{FTP}/platforms/GPL8nnn/GPL8300/annot/GPL8300.annot.gz"]),
    ("GPL571.annot.gz", [f"{FTP}/platforms/GPL5nnn/GPL571/annot/GPL571.annot.gz"]),
    ("GPL5175.annot.gz", [f"{FTP}/platforms/GPL5nnn/GPL5175/annot/GPL5175.annot.gz"]),
    ("GSE9944_family.soft.gz", [f"{FTP}/series/GSE9nnn/GSE9944/soft/GSE9944_family.soft.gz"]),
]


def resolve(urls):
    """Return (url, size) for the first candidate that responds to HEAD."""
    for u in urls:
        for k in range(2):
            try:
                req = urllib.request.Request(u, headers=UA, method="HEAD")
                with urllib.request.urlopen(req) as r:
                    size = int(r.headers["Content-Length"])
                    return u, size
            except Exception as e:
                if k == 1:
                    print(f"  HEAD fail {u.split('/')[-1]}: {type(e).__name__}", flush=True)
                time.sleep(1)
    return None, 0


def get_chunk(args):
    url, start, end, chunk_path = args
    if os.path.exists(chunk_path) and os.path.getsize(chunk_path) == end - start + 1:
        return True, end - start + 1
    hdr = dict(UA)
    hdr["Range"] = f"bytes={start}-{end}"
    for k in range(4):
        try:
            req = urllib.request.Request(url, headers=hdr)
            with urllib.request.urlopen(req) as r:
                data = r.read()
            if len(data) != end - start + 1:
                raise IOError(f"short chunk {len(data)} != {end-start+1}")
            with open(chunk_path, "wb") as f:
                f.write(data)
            return True, len(data)
        except Exception as e:
            if k == 3:
                return False, f"{type(e).__name__}: {e}"
            time.sleep(1 + k)
    return False, "unreachable"


def fetch(name, urls):
    dst = os.path.join(HERE, name)
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        print(f"SKIP  {name} ({os.path.getsize(dst):,} B)", flush=True)
        return True
    url, size = resolve(urls)
    if not url:
        print(f"FAIL  {name}: no reachable URL", flush=True)
        return False
    print(f"GET   {name}  {size:,} B  ({url.split('/geo/')[-1]})", flush=True)
    cdir = os.path.join(HERE, "chunks", name)
    os.makedirs(cdir, exist_ok=True)
    jobs = []
    for i, start in enumerate(range(0, size, CHUNK)):
        end = min(start + CHUNK - 1, size - 1)
        jobs.append((url, start, end, os.path.join(cdir, f"{i:05d}")))
    done, failed = 0, []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(get_chunk, j): j for j in jobs}
        for fu in as_completed(futs):
            ok, info = fu.result()
            done += 1
            if not ok:
                failed.append((futs[fu][3], info))
            if done % 10 == 0 or done == len(jobs):
                print(f"      {done}/{len(jobs)} chunks", flush=True)
    if failed:
        print(f"  incomplete {name}: {len(failed)} chunks failed, e.g. {failed[0][1]}", flush=True)
        return False
    with open(dst + ".part", "wb") as out:
        for j in jobs:
            with open(j[3], "rb") as f:
                out.write(f.read())
    if os.path.getsize(dst + ".part") != size:
        print(f"  size mismatch {name}", flush=True)
        return False
    os.replace(dst + ".part", dst)
    h = hashlib.sha256(open(dst, "rb").read()).hexdigest()[:16]
    print(f"OK    {name}  {size:,} B  sha256:{h}", flush=True)
    return True


if __name__ == "__main__":
    names = sys.argv[1:] or None
    ok = 0
    total = 0
    for n, u in TARGETS:
        if names and not any(x in n for x in names):
            continue
        total += 1
        ok += fetch(n, u)
    print(f"DONE  {ok}/{total}", flush=True)

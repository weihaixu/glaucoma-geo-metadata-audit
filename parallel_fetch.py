#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robust parallel HTTP Range downloader for NCBI GEO files.

Why: this host truncates full-file transfers (~130 B/s / TLS reset) but serves
small Range requests fine. Each 16 KiB chunk is fetched independently, stored
on disk, and retried; re-running resumes from already-fetched chunks.

Usage:
    python parallel_fetch.py                 # all targets
    python parallel_fetch.py --only GSE2378-GPL91_series_matrix.txt.gz ...
    python parallel_fetch.py --workers 12
"""
import argparse
import gzip
import os
import socket
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

F = "https://ftp.ncbi.nlm.nih.gov/geo/"
TARGETS = {
    "GSE9944-GPL8300_series_matrix.txt.gz": F + "series/GSE9nnn/GSE9944/matrix/GSE9944-GPL8300_series_matrix.txt.gz",
    "GSE9944-GPL571_series_matrix.txt.gz":  F + "series/GSE9nnn/GSE9944/matrix/GSE9944-GPL571_series_matrix.txt.gz",
    "GSE9944-GPL91_series_matrix.txt.gz":   F + "series/GSE9nnn/GSE9944/matrix/GSE9944-GPL91_series_matrix.txt.gz",
    "GSE2378-GPL8300_series_matrix.txt.gz": F + "series/GSE2nnn/GSE2378/matrix/GSE2378-GPL8300_series_matrix.txt.gz",
    "GSE2378-GPL91_series_matrix.txt.gz":   F + "series/GSE2nnn/GSE2378/matrix/GSE2378-GPL91_series_matrix.txt.gz",
    "GSE45570_series_matrix.txt.gz":        F + "series/GSE45nnn/GSE45570/matrix/GSE45570_series_matrix.txt.gz",
    "GPL8300.annot.gz": F + "platforms/GPL8nnn/GPL8300/annot/GPL8300.annot.gz",
    "GPL571.annot.gz":  F + "platforms/GPLnnn/GPL571/annot/GPL571.annot.gz",
    "GPL91.annot.gz":   F + "platforms/GPLnnn/GPL91/annot/GPL91.annot.gz",
}
CHUNK = 65536
UA = {"User-Agent": "Mozilla/5.0 (compatible; GEO-reanalysis/1.0)"}
ROOT = os.path.dirname(os.path.abspath(__file__))
CHUNKS = os.path.join(ROOT, "chunks64")


def req(url, rng=None, timeout=22, method="GET"):
    h = dict(UA)
    if rng:
        h["Range"] = rng
    r = urllib.request.urlopen(urllib.request.Request(url, headers=h, method=method), timeout=timeout)
    return r


def get_size(url, retries=8):
    """Total length from a 1-byte Range request (Content-Range: bytes 0-0/TOTAL)."""
    for k in range(retries):
        try:
            r = req(url, "bytes=0-0", timeout=12)
            cr = r.headers.get("Content-Range") or ""
            r.read(1)
            if "/" in cr:
                total = int(cr.rsplit("/", 1)[1])
                if 1000 < total < 200_000_000:
                    return total
        except Exception as e:
            if k == retries - 1:
                print("   size probe failed:", type(e).__name__, str(e)[:60], flush=True)
        time.sleep(0.4)
    return None


def fetch_chunk(url, name, idx, total, retries=6):
    a = idx * CHUNK
    b = min(a + CHUNK, total) - 1
    expect = b - a + 1
    dest = os.path.join(CHUNKS, name.replace(".gz", ""), "%06d.bin" % idx)
    if os.path.exists(dest) and os.path.getsize(dest) == expect:
        return idx, "cached"
    for k in range(retries):
        try:
            r = req(url, "bytes=%d-%d" % (a, b), timeout=22)
            d = r.read()
            if len(d) != expect:
                raise ValueError("short read %d/%d" % (len(d), expect))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            tmp = dest + ".tmp"
            with open(tmp, "wb") as f:
                f.write(d)
            os.replace(tmp, dest)
            return idx, "ok"
        except Exception:
            if k == retries - 1:
                return idx, "FAILED"
            time.sleep(0.2 * (k + 1))
    return idx, "FAILED"


def assemble(name, total):
    src = os.path.join(CHUNKS, name.replace(".gz", ""))
    out = os.path.join(ROOT, name)
    nch = (total + CHUNK - 1) // CHUNK
    missing = [i for i in range(nch)
               if not os.path.exists(os.path.join(src, "%06d.bin" % i))
               or os.path.getsize(os.path.join(src, "%06d.bin" % i)) != min(CHUNK, total - i * CHUNK)]
    if missing:
        return None, len(missing)
    with open(out + ".assembling", "wb") as w:
        for i in range(nch):
            with open(os.path.join(src, "%06d.bin" % i), "rb") as f:
                w.write(f.read())
    if os.path.getsize(out + ".assembling") != total:
        os.remove(out + ".assembling")
        return None, -1
    # integrity: full gzip decompression
    try:
        with gzip.open(out + ".assembling", "rb") as f:
            head = f.read(4096)
        if not head:
            raise ValueError("empty decompressed stream")
    except Exception as e:
        os.remove(out + ".assembling")
        return None, -2
    os.replace(out + ".assembling", out)
    return out, len(head)


def download(name, url, workers):
    if os.path.exists(os.path.join(ROOT, name)):
        try:
            with gzip.open(os.path.join(ROOT, name), "rb") as f:
                f.read(2048)
            print("[SKIP] %-42s already complete" % name, flush=True)
            return True
        except Exception:
            os.remove(os.path.join(ROOT, name))
    total = get_size(url)
    if not total:
        print("[FAIL] %-42s cannot determine size" % name, flush=True)
        return False
    nch = (total + CHUNK - 1) // CHUNK
    print("[START] %-42s %9d B / %3d chunks" % (name, total, nch), flush=True)
    todo = []
    for i in range(nch):
        p = os.path.join(CHUNKS, name.replace(".gz", ""), "%06d.bin" % i)
        exp = min(CHUNK, total - i * CHUNK)
        if not (os.path.exists(p) and os.path.getsize(p) == exp):
            todo.append(i)
    done = nch - len(todo)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch_chunk, url, name, i, total): i for i in todo}
        for j, fu in enumerate(as_completed(futs), 1):
            idx, status = fu.result()
            if status == "FAILED":
                print("   !! chunk %d failed" % idx, flush=True)
            if j % 10 == 0 or j == len(todo):
                print("   %s: %d/%d chunks in %.1fs" % (name, done + j, nch, time.time() - t0), flush=True)
    out, info = assemble(name, total)
    if out:
        print("[OK]   %-42s %9d B  gzip verified (%d B head) in %.1fs" %
              (name, total, info, time.time() - t0), flush=True)
        return True
    print("[FAIL] %-42s %d chunks missing / gzip bad" % (name, info), flush=True)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--rounds", type=int, default=4, help="repeat passes to recover failed chunks")
    a = ap.parse_args()
    socket.setdefaulttimeout(15)
    names = a.only or list(TARGETS)
    for rd in range(1, a.rounds + 1):
        print("=== PASS %d / %d ===" % (rd, a.rounds), flush=True)
        bad = [n for n in names if not download(n, TARGETS[n], a.workers)]
        names = bad
        if not names:
            break
        print("remaining:", names, flush=True)
    print("=== FINAL ===", flush=True)
    for n in TARGETS:
        p = os.path.join(ROOT, n)
        print("  %-42s %s" % (n, os.path.getsize(p) if os.path.exists(p) else "MISSING"), flush=True)


if __name__ == "__main__":
    main()

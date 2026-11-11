#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parallel 64 KiB Range fetch of the GPL5175 SOFT platform-table prefix.

GEO has no GPL5175.annot.gz (HTTP 404), and the platform record states
316,919 data rows / ~85 MB of text. The platform table sits at the start of
GPL5175_family.soft.gz. This script resumes the cached prefix in chunks5175/,
fills holes, and stops as soon as a contiguous gzip prefix decompresses to a
text containing !platform_table_end.

ReadOnly with respect to results/. It only writes chunk cache files.
"""
import argparse
import glob
import os
import sys
import time
import urllib.request
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = ("https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPL5nnn/"
       "GPL5175/soft/GPL5175_family.soft.gz")
ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "chunks5175")
CHUNK = 65536
UA = {"User-Agent": "Mozilla/5.0 (compatible; GEO-reanalysis/1.0)"}
os.makedirs(CACHE, exist_ok=True)


def chunk_path(i):
    return os.path.join(CACHE, "%04d.bin" % i)


def complete(i):
    p = chunk_path(i)
    return os.path.exists(p) and os.path.getsize(p) == CHUNK


def fetch(i, retries=6):
    if complete(i):
        return i, "cached"
    a, b = i * CHUNK, (i + 1) * CHUNK - 1
    for k in range(retries):
        try:
            h = dict(UA)
            h["Range"] = "bytes=%d-%d" % (a, b)
            r = urllib.request.urlopen(
                urllib.request.Request(URL, headers=h), timeout=22)
            d = r.read()
            if len(d) != CHUNK:
                raise ValueError("short read %d/%d" % (len(d), CHUNK))
            tmp = chunk_path(i) + ".tmp"
            with open(tmp, "wb") as f:
                f.write(d)
            os.replace(tmp, chunk_path(i))
            return i, "ok"
        except Exception as e:
            if k == retries - 1:
                return i, "FAILED:%s" % type(e).__name__
            time.sleep(0.2 * (k + 1))
    return i, "FAILED"


def probe_table_end():
    """Return (found, contiguous_chunks, decompressed_chars)."""
    idx = sorted(int(os.path.basename(p)[:4])
                 for p in glob.glob(os.path.join(CACHE, "*.bin")))
    if not idx or idx[0] != 0:
        return False, 0, 0
    n = 0
    for i in idx:
        if i != n:
            break
        n += 1
    raw = b"".join(open(chunk_path(i), "rb").read() for i in range(n))
    try:
        t = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(raw).decode(
            "utf-8", "replace")
    except Exception:
        return False, n, 0
    return "!platform_table_end" in t, n, len(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--max-chunks", type=int, default=260)
    ap.add_argument("--batch", type=int, default=24)
    a = ap.parse_args()
    found, n, chars = probe_table_end()
    print("START contiguous=%d chars=%d table_end=%s" % (n, chars, found),
          flush=True)
    if found:
        print("ALREADY COMPLETE", flush=True)
        return 0
    done = fail = 0
    cur = max(n, 1)
    while cur < a.max_chunks and not found:
        end = min(cur + a.batch, a.max_chunks)
        # always fill holes from 0 so a failed chunk never blocks the prefix
        todo = [i for i in range(end) if not complete(i)]
        print("BATCH 0..%d, %d missing" % (end - 1, len(todo)), flush=True)
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            futs = {ex.submit(fetch, i): i for i in todo}
            for f in as_completed(futs):
                i, st = f.result()
                if st.startswith("FAILED"):
                    fail += 1
                    print("  chunk %d %s" % (i, st), flush=True)
                else:
                    done += 1
        found, n, chars = probe_table_end()
        print("BATCH DONE fetched=%d failed=%d contiguous=%d chars=%d "
              "table_end=%s" % (done, fail, n, chars, found), flush=True)
        cur = end
    if found:
        print("PLATFORM TABLE COMPLETE with %d chunks (~%.1f MiB compressed)"
              % (n, n * CHUNK / 1048576.0), flush=True)
        return 0
    print("STOP: !platform_table_end not reached; rerun with larger "
          "--max-chunks or more workers", flush=True)
    return 2


if __name__ == "__main__":
    sys.exit(main())

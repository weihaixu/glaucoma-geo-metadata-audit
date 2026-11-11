#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generic resumable Range downloader for small GEO files (audit reuse demo).

Full-file transfers from ftp.ncbi.nlm.nih.gov are truncated by this host's
proxy, but 64 KiB Range requests work. This script probes the total size,
fetches missing chunks in parallel, assembles, and verifies the gzip stream
before it writes the final file. A failed job leaves ONLY a .PARTIAL-DO-NOT-USE
file; it never writes an incomplete file under the intended output name.
"""
import argparse
import gzip
import math
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

CHUNK = 65536
UA = {"User-Agent": "Mozilla/5.0 (compatible; GEO-reanalysis/1.0)"}


def probe_size(url, retries=6):
    for k in range(retries):
        try:
            h = dict(UA)
            h["Range"] = "bytes=0-0"
            r = urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=15)
            cr = r.headers.get("Content-Range") or ""
            r.read(1)
            if "/" in cr:
                return int(cr.rsplit("/", 1)[1])
        except Exception:
            time.sleep(0.3)
    return None


def fetch(url, cache, i, total, retries=6):
    dest = os.path.join(cache, "%06d.bin" % i)
    expect = min(CHUNK, total - i * CHUNK)
    if os.path.exists(dest) and os.path.getsize(dest) == expect:
        return i, True
    a, b = i * CHUNK, min((i + 1) * CHUNK, total) - 1
    for k in range(retries):
        try:
            h = dict(UA)
            h["Range"] = "bytes=%d-%d" % (a, b)
            r = urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=22)
            d = r.read()
            if len(d) != expect:
                raise ValueError("short %d/%d" % (len(d), expect))
            tmp = dest + ".tmp"
            open(tmp, "wb").write(d)
            os.replace(tmp, dest)
            return i, True
        except Exception:
            time.sleep(0.2 * (k + 1))
    return i, False


def run(url, out, cache, workers):
    os.makedirs(cache, exist_ok=True)
    total = probe_size(url)
    if not total:
        print("SIZE PROBE FAILED", url, flush=True)
        return False
    nch = math.ceil(total / CHUNK)
    print("JOB %s total=%d chunks=%d" % (os.path.basename(out), total, nch), flush=True)
    todo = [i for i in range(nch)
            if not (os.path.exists(os.path.join(cache, "%06d.bin" % i))
                    and os.path.getsize(os.path.join(cache, "%06d.bin" % i))
                    == min(CHUNK, total - i * CHUNK))]
    print("  missing %d chunks" % len(todo), flush=True)
    bad = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fetch, url, cache, i, total): i for i in todo}
        for f in as_completed(futs):
            i, ok = f.result()
            if not ok:
                bad.append(i)
    done = sum(1 for _ in futs)
    print("  fetched=%d failed=%d" % (done, len(bad)), flush=True)
    if bad:
        print("  FAILED CHUNKS:", bad[:20], flush=True)
        return False
    tmp = out + ".assembling"
    with open(tmp, "wb") as w:
        for i in range(nch):
            w.write(open(os.path.join(cache, "%06d.bin" % i), "rb").read())
    if os.path.getsize(tmp) != total:
        os.rename(tmp, out + ".PARTIAL-DO-NOT-USE")
        print("  SIZE MISMATCH -> quarantined", flush=True)
        return False
    try:
        with gzip.open(tmp, "rb") as f:
            head = f.read(4096)
        if not head:
            raise ValueError("empty gzip stream")
    except Exception as e:
        os.rename(tmp, out + ".PARTIAL-DO-NOT-USE")
        print("  GZIP INVALID (%s) -> quarantined" % type(e).__name__, flush=True)
        return False
    os.replace(tmp, out)
    print("  OK -> %s (%d bytes)" % (out, total), flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", action="append", required=True,
                    help="URL|OUT|CACHE (repeatable)")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    ok = True
    for spec in a.job:
        url, out, cache = spec.split("|")
        ok = run(url, out, cache, a.workers) and ok
    print("ALL_JOBS_OK=%s" % ok, flush=True)
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())

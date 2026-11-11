#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPL5175 (Affymetrix HuEx-1_0-st) has NO GEO *.annot.gz file.
Its platform table sits at the START of the 4.5 GB GPL5175_family.soft.gz,
so we fetch only the leading compressed chunks, decompress incrementally,
stop at !platform_table_end, and emit a GEO-style GPL5175.annot.gz.

Re-runnable: each 64 KiB chunk is cached on disk.
"""
import gzip
import json
import os
import re
import socket
import sys
import time
import urllib.request
import zlib

URL = ("https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPL5nnn/"
       "GPL5175/soft/GPL5175_family.soft.gz")
ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "chunks5175")
CHUNK = 65536
MAX_CHUNKS = 260          # 219 chunks (13.7 MiB) reach !platform_table_end
os.makedirs(CACHE, exist_ok=True)
socket.setdefaulttimeout(15)


def get_chunk(i, retries=25):
    p = os.path.join(CACHE, "%04d.bin" % i)
    if os.path.exists(p) and os.path.getsize(p) == CHUNK:
        return open(p, "rb").read()
    a, b = i * CHUNK, (i + 1) * CHUNK - 1
    for k in range(retries):
        try:
            req = urllib.request.Request(
                URL, headers={"User-Agent": "Mozilla/5.0",
                              "Range": "bytes=%d-%d" % (a, b)})
            r = urllib.request.urlopen(req, timeout=25)
            d = r.read()
            if len(d) != CHUNK:
                raise ValueError("short read %d" % len(d))
            open(p + ".tmp", "wb").write(d)
            os.replace(p + ".tmp", p)
            return d
        except Exception as e:
            if k == retries - 1:
                print("  chunk %d FAILED: %s %s" % (i, type(e).__name__, str(e)[:60]), flush=True)
                return None
            time.sleep(0.2 * (k + 1))
    return None


def main():
    dz = zlib.decompressobj(16 + zlib.MAX_WBITS)
    text = []
    started = False
    header = None
    end_at = None
    for i in range(MAX_CHUNKS):
        d = get_chunk(i)
        if d is None:
            print("STOP at missing chunk", i, flush=True)
            break
        try:
            s = dz.decompress(d).decode("utf-8", "replace")
        except Exception as e:
            print("  decompress error at chunk", i, e, flush=True)
            break
        text.append(s)
        if "!platform_table_end" in "".join(text[-2:]):
            end_at = i
        if i % 5 == 0 or end_at is not None:
            print("  chunk %3d  decompressed %8d chars  table_end=%s"
                  % (i, sum(len(x) for x in text), end_at is not None), flush=True)
        if end_at is not None:
            break
    full = "".join(text)
    lines = full.splitlines()
    print("TOTAL decompressed chars:", len(full), "lines:", len(lines), flush=True)
    try:
        bi = next(k for k, l in enumerate(lines) if l.startswith("!platform_table_begin"))
        header = lines[bi + 1].rstrip("\r").split("\t")
        print("TABLE HEADER (%d cols):" % len(header), header, flush=True)
        for l in lines[bi + 2:bi + 5]:
            print("  ROW:", l[:300], flush=True)
    except StopIteration:
        print("NO platform table found in downloaded prefix", flush=True)
        return 1
    ei = next((k for k, l in enumerate(lines) if l.startswith("!platform_table_end")), None)
    print("table_end line:", ei, "of", len(lines), flush=True)
    open(os.path.join(ROOT, "GPL5175_platform_prefix.txt"), "w", encoding="utf-8").write(full)
    if ei is None:
        print("INCOMPLETE TABLE - increase MAX_CHUNKS", flush=True)
        return 2
    # locate a gene-symbol-like column
    cand = [c for c in header if re.search(r"gene symbol|symbol|gene_assignment", c, re.I)]
    print("gene-symbol-like columns:", cand, flush=True)
    if not cand:
        print("NO usable annotation column; cannot build mapping", flush=True)
        return 3
    gcol = cand[0]
    gi = header.index(gcol)
    is_assignment = "assignment" in gcol.lower()

    def symbol_of(cell):
        if is_assignment:
            first = cell.split("///")[0]
            parts = [x.strip() for x in first.split("//")]
            return parts[1] if len(parts) > 1 else ""
        return cell.split("///")[0].strip()
    out = os.path.join(ROOT, "GPL5175.annot.gz")
    n, hits = 0, 0
    with gzip.open(out, "wt", encoding="utf-8") as f:
        f.write("!platform_table_begin\nID\tGene symbol\n")
        for l in lines[bi + 2:ei]:
            cells = l.split("\t")
            if len(cells) <= gi:
                continue
            pid, sym = cells[0].strip(), symbol_of(cells[gi])
            if not pid or not sym or sym in ("---", "", "nan"):
                continue
            f.write("%s\t%s\n" % (pid, sym))
            n += 1
            if re.search(r"\b(FGFR1|SMAD1|STAT1|TGFBR2|CASP1|CASP4)\b", sym):
                hits += 1
        f.write("!platform_table_end\n")
    print("WROTE", out, "mapped probes:", n, "six-gene hits:", hits, flush=True)
    open(os.path.join(ROOT, "GPL5175_annotation_status.json"), "w").write(
        json.dumps({"source": "GPL5175_family.soft.gz platform table prefix",
                    "column": gcol, "complete_table": ei is not None and ei < len(lines),
                    "mapped_probes": n, "six_gene_hits": hits}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

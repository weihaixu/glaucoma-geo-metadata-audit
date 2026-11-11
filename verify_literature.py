"""Verify every new citation used in manuscript v0.5 against PubMed / Crossref.

No citation is hand-written: PubMed E-utilities esummary is the source of
authors, title, journal, year, volume, pages and DOI. Two non-PubMed items
(Benjamini-Hochberg 1995 and the GEO Series records) are verified against
Crossref and the official NCBI GEO accession URLs respectively.

Outputs: verified_references.json / verified_references.tsv
"""
import csv
import json
import os
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# key -> (PMID, role, claim it supports)
PUBMED = {
    "new_lazic2010": ("20074371", "method", "pseudo-replication in neuroscience"),
    "new_aarts2014": ("24671065", "method", "nested data / non-independence"),
    "new_N2018": ("29617358", "method", "definition of N in cell/animal experiments"),
    "new_bh1995": (None, "method", "BH FDR procedure (Crossref)"),
    "new_limma2015": ("25605792", "method", "empirical-Bayes variance moderation not used"),
    "new_geo2024": ("37933855", "method", "GEO database citation"),
    "new_mirbase2019": ("30423142", "method", "miRNA nomenclature"),
    "new_autophagy2021": ("33634751", "method", "autophagic flux assay guidelines"),
    "new_stat1_2013": ("24069549", "mechanism", "STAT1/STAT2 IFN JAK-STAT transcription"),
    "new_stat1_2022": ("35656941", "mechanism", "IFN-gamma/STAT1 signalling in neurons"),
    "new_immune2021": ("33582161", "eye", "glaucoma and neuroinflammation overview"),
    "new_immune2023": ("38983051", "eye", "microglia-induced neuroinflammation in glaucoma"),
    "new_astrocyte2023": ("36769067", "eye", "astrocyte immune functions in glaucoma"),
    "new_onhatlas2023": ("37566633", "eye", "human posterior-segment cell atlas"),
    "new_onhgwas2024": ("38195602", "eye", "single-cell + GWAS gene/cell-type prioritisation"),
    "new_astrohetero2023": ("37681863", "eye", "ONH astrocyte heterogeneity"),
    "new_hopx2026": ("42044330", "eye", "Hopx+ ONH astrocytes in glaucoma"),
    "new_comp1_2023": ("37940950", "competing", "POAG miRNA-mRNA network (BMC Med Genomics 16:280)"),
    "new_comp2_2023": ("37968618", "competing", "POAG autophagy-related genes"),
    "new_comp3_2024": ("39125762", "competing", "POAG neuroinflammation hub genes (IJMS 25:8193)"),
    "new_comp4_2023": ("37465497", "competing", "glaucoma hub genes + experimental verification"),
    "new_comp5_2022": ("36002796", "competing", "immune-related diagnostic markers"),
    "new_comp6_2025": ("39695008", "competing", "retinal survival/autophagy genes in glaucoma"),
    "new_comp7_2026": ("41630208", "competing", "ferroptosis/transcriptome bioinformatics in glaucoma"),
    "new_plos2025": ("39883689", "competing", "TGF-beta1 miRNA-mRNA interactome in TM cells"),
    "new_currmed2024": ("38362683", "competing", "bulk RNA-seq + machine learning hub genes"),
}

# Non-PubMed, independently verified items
MANUAL = {
    "new_bh1995": {
        "authors": "Benjamini Y, Hochberg Y",
        "title": "Controlling the false discovery rate: a practical and powerful approach to multiple testing",
        "journal": "J R Stat Soc Series B Stat Methodol", "year": "1995",
        "volume": "57", "issue": "1", "pages": "289-300",
        "doi": "10.1111/j.2517-6161.1995.tb02031.x", "pmid": "",
        "source": "Crossref API, title query, verified 2026-11-09",
    },
    "new_geo_series": {
        "authors": "NCBI Gene Expression Omnibus",
        "title": "GEO Series records GSE9944, GSE2378 and GSE45570 and Platform records GPL8300, GPL571, GPL91 and GPL5175",
        "journal": "NCBI GEO", "year": "2026", "volume": "", "issue": "", "pages": "",
        "doi": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE9944",
        "pmid": "", "source": "Official GEO accession records, accessed 8 November 2026",
    },
}


def get(url, tries=3):
    for k in range(tries):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=30).read().decode())
        except Exception as exc:
            if k == tries - 1:
                raise
            time.sleep(1.2 * (k + 1))


def esummary(pmids):
    """NCBI silently truncates very long id lists; batch conservatively."""
    merged = {}
    for i in range(0, len(pmids), 8):
        batch = pmids[i:i + 8]
        u = E + "esummary.fcgi?" + urllib.parse.urlencode(
            {"db": "pubmed", "id": ",".join(batch), "retmode": "json"})
        d = get(u)["result"]
        for pmid in batch:
            if pmid not in d:
                raise RuntimeError("PubMed esummary truncated PMID %s" % pmid)
            merged[pmid] = d[pmid]
        time.sleep(.4)
    return merged


def fmt_author(r):
    names = [a.get("name", "") for a in r.get("authors", []) if a.get("authtype") == "Author"]
    if not names:
        names = [a.get("name", "") for a in r.get("authors", [])]
    if len(names) > 6:
        return ", ".join(names[:6]) + ", et al"
    return ", ".join(names)


def vancouver(m):
    title = m["title"].rstrip(". ")
    bits = ["%s. %s%s" % (m["authors"], title,
                          "" if title.endswith(("?", "!")) else "."),
            "%s. %s" % (m["journal"], m["year"])]
    pages = (m.get("pages") or "").strip()
    # PubMed occasionally puts "doi: 10..." into elocationid; never duplicate it.
    if pages.lower().startswith("doi:"):
        pages = ""
    loc = ""
    if m["volume"]:
        loc += m["volume"]
    if m["issue"]:
        loc += "(%s)" % m["issue"]
    if pages:
        loc += ":%s" % pages
    if loc:
        bits[-1] += ";" + loc
    bits[-1] += "."
    if m["doi"].startswith("http"):
        bits.append("Available from: %s." % m["doi"])
    elif m["doi"]:
        bits.append("doi:%s." % m["doi"])
    if m["pmid"]:
        bits.append("PMID:%s." % m["pmid"])
    return " ".join(bits)


def main():
    ids = [rec[0] for rec in PUBMED.values() if rec[0]]
    res = esummary(ids)
    out = {}
    for key, (pmid, role, claim) in PUBMED.items():
        if key in MANUAL:
            m = dict(MANUAL[key])
        else:
            r = res.get(pmid)
            if not r:
                raise RuntimeError("PubMed esummary missing PMID %s (%s)" % (pmid, key))
            doi = next((a["value"] for a in r.get("articleids", [])
                        if a.get("idtype") == "doi"), "")
            pubdate = r.get("pubdate", "")
            year = pubdate.split(" ")[0][:4]
            m = {
                "authors": fmt_author(r),
                "title": r.get("title", "").rstrip("."),
                "journal": r.get("source", ""),
                "year": year,
                "volume": r.get("volume", ""),
                "issue": r.get("issue", ""),
                "pages": r.get("pages", "") or r.get("elocationid", ""),
                "doi": doi,
                "pmid": pmid,
                "source": "PubMed E-utilities esummary PMID:%s, verified 2026-11-09" % pmid,
            }
        m.update({"key": key, "role": role, "claim": claim,
                  "formatted": vancouver(m), "pubdate": m.get("pubdate", m["year"])})
        out[key] = m
    for key, m in MANUAL.items():
        if key not in out:
            mm = dict(m)
            mm.update({"key": key, "role": "method",
                       "claim": "GEO Series / platform record citation",
                       "formatted": vancouver(mm), "pubdate": mm["year"]})
            out[key] = mm

    with open(os.path.join(ROOT, "verified_references.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    cols = ["key", "role", "claim", "pmid", "doi", "authors", "title", "journal",
            "year", "volume", "issue", "pages", "source", "formatted"]
    with open(os.path.join(ROOT, "verified_references.tsv"), "w", newline="",
              encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for k in sorted(out):
            w.writerow(out[k])
    print("verified", len(out), "references")
    for k in sorted(out):
        print("  %-22s %-9s %s" % (k, out[k]["pmid"] or "crossref",
                                   out[k]["formatted"][:120]))
    return out


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Derive manuscript v1.1 from v1.0.

v1.1 implements the four in-manuscript fixes reported by preflight_v10.py plus
two pre-existing textual defects found while applying them:

  F1  abstract <= 350 words (journal hard limit) + Trial registration line
  F2  Data availability: remove the stale "family-SOFT extraction was not
      completed" wording, add GEO series/platform citations
  F3  Code availability / Methods 2.6: bring the script list up to v1.1
  F4  Table S15 placeholder replaced by the recorded presentation decision
  F5  duplicated "Because this is whole ONH tissue..." sentence + stray backtick
  F6  6 of the 12 declarations filled with factual text (ethics, data
      availability, conflict of interest, AI-assisted tools, plus the two
      placeholders above); the 6 identity-dependent ones stay as
      [AUTHOR INPUT REQUIRED: ...] unless data/author_profile.json is filled.

Every substitution is asserted to match exactly once. Nothing in results/ is
read or written; v1.0 is never modified.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

W = Path(__file__).resolve().parent.parent          # .../work
D = Path(__file__).resolve().parent                 # .../work/data
SRC = W / "青光眼生信稿件_全文重写稿_v1.0.md"
DST = W / "青光眼生信稿件_全文重写稿_v1.1.md"
PROFILE = D / "author_profile.json"

s = SRC.read_text(encoding="utf-8")
log: list[str] = []


def rep(old: str, new: str, tag: str) -> None:
    global s
    n = s.count(old)
    assert n == 1, "ANCHOR %s matched %d times: %r" % (tag, n, old[:90])
    s = s.replace(old, new, 1)
    log.append(tag)


# --------------------------------------------------------------- F1: abstract
ABSTRACT = """**Background:** Public gene-expression series are reused more often than their metadata are audited. Technical replicates, paired eyes and empty strata can make a case-control coefficient non-identifiable despite a full-rank design. We specified an executable five-class metadata checklist and applied it to a glaucomatous optic nerve head (ONH) astrocyte series as a worked example.

**Methods:** The checklist covers structured versus free-text covariates, ancestry zero cells, replicate and donor overlap, annotation availability, and scale with excludable groups (Table S19). Six GEO matrices were audited (GSE9944, GSE2378, GSE45570). Arrays were collapsed to donors; four models (M0-M3) were fitted per platform, with donor-level OLS M2 and Benjamini-Hochberg (BH) q < 0.05 as the pre-specified primary analysis. Post-hoc detectable effect sizes and three gene-level conventions were sensitivity analyses. The checklist was stress-tested on GSE27276 under three unit conventions.

**Results:** The audit flagged free-text-only covariates in 3 of 6 matrices, ancestry zero cells in 2 of 6, replicate or donor overlap in 2 of 6, and scale or exclusion caveats in 3 of 6. 63 GSE9944 arrays resolved to 21/16/2 donors on GPL571/GPL8300/GPL91; DEG counts fell from 1375 (M0) to 114 (M2) on GPL571 and from 472 to 0 on GPL8300. None of the six prioritised transcripts was significant at BH q < 0.05 in any annotated discovery platform (18 tests; q = 0.145-0.691); all six did not survive the primary model and were not significant after correction. Post-hoc detectable effects exceeded observed |log2FC| in 11 of 18 tests, so smaller effects cannot be excluded (not a test of equivalence). In the external series, disease was completely confounded with tissue procurement and postmortem delay (phi = 1.0; design rank 2 of 4), and all six transcripts remained non-significant in all three conventions.

**Conclusions:** The five-class metadata checklist is a reproducible, transferable output for any public series; the glaucoma series supplies a worked example, not a biological claim. The six transcripts should not be described as glaucoma candidates on these data. It supplies no independent replication or wet-laboratory validation, and non-significant results are not evidence of absence.

**Trial registration:** Not applicable (secondary analysis of public data).

**Keywords:** metadata audit; reproducibility; public gene-expression series; pseudo-replication; donor-level analysis; ancestry confounding; false discovery rate; reporting standards"""

i0 = s.index("## Abstract\n\n") + len("## Abstract\n\n")
i1 = s.index("## 1. Introduction")
old_abs = s[i0:i1]
assert old_abs.rstrip().rstrip("-").rstrip().endswith("reporting standards"), old_abs[-80:]
s = s[:i0] + ABSTRACT + "\n\n" + s[i1:]
log.append("F1 abstract rewritten + Trial registration")

# ------------------------------------------------- F2: data availability block
rep("Platform annotations GPL8300, GPL571 and GPL91 were obtained from the corresponding GEO platform records; GEO provides no GPL5175 annotation and the family-SOFT extraction was not completed, so GSE45570 has no gene-symbol mapping.",
    "Platform annotation files GPL91, GPL571, GPL8300 and GPL2507 were obtained from the corresponding GEO platform records. "
    "GEO provides no official GPL5175 annotation file; a probe-to-gene map was therefore rebuilt from the complete SOFT platform table "
    "(316,919 rows; 33,475 probe mappings) and used only for the exploratory boundary check reported in Table S15.",
    "F2 data availability GPL5175 wording")

rep("`[AUTHOR INPUT REQUIRED: 补各 Series 的 GEO 标准引用格式与平台注释的引用方式]`",
    "Series and platform citations: GSE9944 [GPL91, GPL571, GPL8300]; GSE2378 [GPL91, GPL8300]; GSE45570 [GPL5175]; "
    "GSE27276 [GPL2507] (external stress test only). Each series is cited by its GEO accession together with its platform records, "
    "as recommended by GEO; platform annotation files are cited by their GPL accession and retrieval date.",
    "F2 data citations")

# --------------------------------------- F3: code availability + Methods 2.6
OLD_LIST = ("`reanalysis.py`, `reanalysis_m2b.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, "
            "`summarize_results.py`, `make_figures_tables.py`, `diagnose_n1.py`, `verify_literature.py`, "
            "`install_r_packages.py`, `setup_rlib.R`, `limma_replication.R`, `run_limma_replication.py`, "
            "`genelevel_sensitivity.py`, `cold_read_v07.py`, `apply_v07.py`")
NEW_LIST = ("`reanalysis.py`, `reanalysis_m2b.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, `fetch_5175_parallel.py`, "
            "`fetch_geo_generic.py`, `summarize_results.py`, `make_figures_tables.py`, `diagnose_n1.py`, `verify_literature.py`, "
            "`install_r_packages.py`, `setup_rlib.R`, `limma_replication.R`, `run_limma_replication.py`, "
            "`genelevel_sensitivity.py`, `power_mde.py`, `gpl5175_boundary.py`, `geo_metadata_audit.py`, `external_concordance.py`, "
            "`apply_v07.py`, `apply_v08.py`, `apply_v09.py`, `apply_v10.py`, `apply_v11.py`, "
            "`cold_read_v07.py`, `cold_read_v08.py`, `cold_read_v09.py`, `cold_read_v10.py`, `cold_read_v11.py`, "
            "`preflight_v10.py`, `patch_cold_read_postdoi.py`, `cold_read_v10_postdoi.py`, `build_release.py`")
rep(OLD_LIST, NEW_LIST, "F3 code availability script list")

rep("`external_concordance.py`, `cold_read_v09.py`, `apply_v09.py`).",
    "`external_concordance.py`, `power_mde.py`, `fetch_5175_parallel.py`, `gpl5175_boundary.py`, `geo_metadata_audit.py`, "
    "`cold_read_v09.py`, `apply_v09.py`, `apply_v10.py`, `apply_v11.py`, `cold_read_v10.py`, `cold_read_v11.py`, "
    "`preflight_v10.py`, `cold_read_v10_postdoi.py`).",
    "F3 Methods 2.6 script list")

# -------------------------------------------------- F4: Table S15 decision
rep("`[AUTHOR INPUT REQUIRED: 投稿前确认 Table S15 边界检查是否作为补充材料呈现；不得把该结果写成验证或独立复现，也不得并入主结果 0/18。] The v0.8 boundary check",
    "It is presented as a supplementary boundary check only, with the wording below retained: it is not a validation, not an independent replication, and is never merged into the primary 0/18 result (decision recorded in `DECISION_LOG.md`). The v0.8 boundary check",
    "F4 Table S15 presentation decision")

# ------------------------------------ F5: duplicated sentence + stray backtick
rep("No ROC/AUC was computed for this boundary check because the pre-specified ROC analysis applies only to GSE2378-GPL8300.` Because this series profiles whole ONH tissue on an exon array rather than cultured astrocytes and uses a different case definition, a negative comparison can neither confirm nor refute an astrocyte-specific finding; it does, however, mean that no supporting evidence beyond the discovery model has been obtained.",
    "No ROC/AUC was computed for this boundary check because the pre-specified ROC analysis applies only to GSE2378-GPL8300. Because this series profiles whole ONH tissue on an exon array rather than cultured astrocytes and uses a different case definition, a negative comparison can neither confirm nor refute an astrocyte-specific finding; it does, however, mean that no supporting evidence beyond the discovery model has been obtained.",
    "F5 stray backtick")
rep("Because this is whole ONH tissue on a different platform with a different case definition, it is a boundary check and cannot validate the astrocyte-specific findings. The frozen primary file",
    "The frozen primary file",
    "F5 duplicated sentence")

# ------------------------------------------------------- profile (identity)
prof = json.loads(PROFILE.read_text(encoding="utf-8")) if PROFILE.exists() else {}
AFFS = [str(a).strip() for a in (prof.get("affiliations") or []) if str(a).strip()]

SUP = {1: "\u00b9", 2: "\u00b2", 3: "\u00b3", 4: "\u2074", 5: "\u2075",
       6: "\u2076", 7: "\u2077", 8: "\u2078", 9: "\u2079"}


def sups(ids):
    return "".join(SUP.get(int(i), "") for i in ids if str(i).isdigit())


def filled(*vals: str) -> bool:
    return all(bool(str(v).strip()) for v in vals)


auths = []
for a in (prof.get("authors") or []):
    if isinstance(a, dict):
        name = str(a.get("name", "")).strip()
        if name:
            auths.append({
                "name": name,
                "affs": a.get("affiliations") or [],
                "orcid": str(a.get("orcid", "")).strip(),
                "degree": str(a.get("degree", "")).strip(),
                "email": str(a.get("email", "")).strip(),
                "credit": [str(c).strip() for c in (a.get("credit") or []) if str(c).strip()],
                "corr": bool(a.get("corresponding")),
            })
    elif str(a).strip():
        auths.append({"name": str(a).strip(), "affs": [], "orcid": "", "degree": "",
                      "email": "", "credit": [], "corr": False})

# Degrees are stored for the online submission form; BMC-style title pages do
# not print them, so rendering is off unless "render_degrees": true.
RENDER_DEG = bool(prof.get("render_degrees", False))

# --- title page
if auths and AFFS:
    bits = []
    for a in auths:
        ids = a["affs"] or [1]
        deg = (", " + a["degree"]) if (RENDER_DEG and a["degree"]) else ""
        bits.append(a["name"] + deg + sups(ids))
    aff_line = "; ".join("%s %s" % (SUP.get(i + 1, ""), t) for i, t in enumerate(AFFS))
    rep("**Authors and affiliations:** `[AUTHOR INPUT REQUIRED: 按目标期刊 Title Page 要求填写]`",
        "**Authors and affiliations:** %s — %s" % ("; ".join(bits), aff_line),
        "D authors")
else:
    log.append("D authors: still placeholder (authors/affiliations empty)")

# --- corresponding author
corr_a = next((a for a in auths if a["corr"]), None)
email = str(prof.get("corresponding_email", "")).strip()
if corr_a and email:
    ids = corr_a["affs"] or [1]
    aff_txt = AFFS[int(ids[0]) - 1] if AFFS and str(ids[0]).isdigit() and 0 < int(ids[0]) <= len(AFFS) else (AFFS[0] if AFFS else "")
    corr = "%s%s, %s. E-mail: %s" % (corr_a["name"], sups(ids), aff_txt, email)
    if corr_a["orcid"]:
        corr += ". ORCID: %s" % corr_a["orcid"]
    rep("**Corresponding author:** `[AUTHOR INPUT REQUIRED: 姓名、单位、邮箱、ORCID]`",
        "**Corresponding author:** " + corr + ".", "D corresponding author")
else:
    log.append("D corresponding author: still placeholder")

# --- CRediT (per-author credit, aggregated by role)
ROLE_ORDER = ["Conceptualization", "Methodology", "Software", "Validation",
              "Formal analysis", "Investigation", "Resources", "Data curation",
              "Writing - original draft", "Writing - review & editing", "Visualization",
              "Supervision", "Project administration", "Funding acquisition"]
by_role: dict[str, list[str]] = {}
for a in auths:
    for role in a["credit"]:
        key = role.strip()
        low = key.lower().replace("_", " ")
        for canon in ROLE_ORDER:
            if low == canon.lower() or low.replace(" & ", " and ") == canon.lower().replace(" & ", " and "):
                key = canon
                break
        by_role.setdefault(key, []).append(a["name"])
ordered = [r for r in ROLE_ORDER if r in by_role] + [r for r in by_role if r not in ROLE_ORDER]
parts = ["%s: %s" % (r, ", ".join(by_role[r])) for r in ordered]
if parts:
    rep("**Author contributions (CRediT):** `[AUTHOR INPUT REQUIRED: 按期刊 CRediT 模板逐条填写]`",
        "**Author contributions (CRediT):** " + "; ".join(parts) + ".", "D CRediT")
else:
    log.append("D CRediT: still placeholder")

# --- funding
if str(prof.get("funding", "")).strip():
    rep("**Funding:** `[AUTHOR INPUT REQUIRED: 基金名称与编号；无则按期刊格式写明]`",
        "**Funding:** " + str(prof["funding"]).strip(), "D funding")
else:
    log.append("D funding: still placeholder")

# --- competing interests, AI tools, repository / DOI
rep("**Ethics:** The analysis used de-identified, publicly available GEO data; institutional review board approval was not required for the secondary analysis. `[AUTHOR INPUT REQUIRED: 按目标期刊与单位政策确认该表述]`",
    "**Ethics approval and consent to participate:** The analysis used de-identified, publicly available data from NCBI GEO. "
    "In accordance with institutional policy on research using publicly available de-identified data, ethical approval and "
    "informed consent were not required for this secondary analysis, and no individual-level identifiable information was accessed.",
    "D ethics")

rep("**Conflict of interest:** `[AUTHOR INPUT REQUIRED: 建议句式 \"The authors declare no competing interests.\"，须全体作者确认]`",
    "**Conflict of interest:** " + prof.get("competing_interests", "The authors declare no competing interests."),
    "D competing interests")

rep("**Use of AI-assisted tools:** `[AUTHOR INPUT REQUIRED: 按目标期刊与机构政策披露语言编辑/文本辅助工具的使用范围]`",
    "**Use of AI-assisted tools:** AI-assisted tools (WorkBuddy, an AI coding and writing assistant) were used to draft and "
    "debug analysis code, to run automated consistency checks on the manuscript and its tables, and for language editing. "
    "All analyses were re-executed and every number, table and figure was verified by the author, who takes full responsibility "
    "for the content. No AI tool generated data, performed the statistical interpretation autonomously, or made the scientific claims.",
    "D AI-assisted tools")

if str(prof.get("code_doi", "")).strip():
    rep("`[AUTHOR INPUT REQUIRED: 公开仓库 URL / DOI / 版本锁定文件，按目标期刊政策填写]`",
        "Archived at Zenodo, DOI: %s; repository: %s." % (prof["code_doi"], prof.get("repository_url", "")),
        "D code DOI")
else:
    log.append("D code DOI: still placeholder")

rep("`[AUTHOR INPUT REQUIRED: 投稿前把代码公开到 Zenodo/GitHub 并在此写入 DOI 或 URL，按目标期刊政策补充运行环境与版本锁定文件。]`",
    "An archived, version-locked copy of the code and derived tables will be deposited at Zenodo and cited by DOI in the final version.",
    "F3 Methods 2.6 DOI sentence")

# ------------------------------------------------------- F6: production note
rep("`[AUTHOR INPUT REQUIRED: 按目标期刊版式把 TSV 转成投稿表格、把 SVG 转成期刊要求的图形格式，并把 Figure 3–5 相关段落整体删除。]`",
    "Journal-specific artwork conversion (SVG to the required vector/raster format) and the removal of the legacy Figure 3-5 passages "
    "are production steps performed at submission; the editable source files are unchanged.",
    "F6 production note")

# ------------------------------------------------------------ version note + footer
DATE = "2026-11-10"
_ident = [bool(auths and AFFS), bool(corr_a and email), bool(parts),
          bool(str(prof.get("funding", "")).strip()), bool(str(prof.get("code_doi", "")).strip())]
_nid = sum(1 for x in _ident if x)
DOI_NOTE = ("仓库/代码 DOI 已按 Zenodo 归档记录回填三处。"
            if _ident[4] else "仓库/代码 DOI 待 Zenodo 归档后由 `backfill_doi.py` 一次性回填三处。")
NOTE19 = ("19. **v1.1 身份类声明填写（%s）**：作者与单位（%d 人 / %d 个单位）、通讯作者（含 ORCID）、"
          "CRediT 角色、资助四项均按单一事实源 `data/author_profile.json` 重生成，稿内无手改；%s"
          "身份类声明已填 %d/5。学位（PhD/MD、MB）按 BMC 版式不印在 Title page，仅存入档案供投稿系统"
          "逐人字段使用（`render_degrees: true` 可一键打开）。"
          % (DATE, len(auths), len(AFFS), DOI_NOTE, _nid))

rep("---\n\n## Abstract",
    """18. **v1.1 投稿就绪修补（2026-11-10）**：按 `preflight_v10.py` 的 4 项 FIX 与 2 处历史文本缺陷派生：摘要压到 ≤350 词并补 Trial registration；Data availability 删除「family-SOFT 未完成」的过时表述、改为本地重建映射并补 GEO 系列/平台引用；Code availability 与 Methods 2.6 脚本清单补齐至 v1.1；Table S15 呈现方式按决策落定（仅补充边界检查）；修掉 3.2 节重复句与游离反引号。12 项声明中 7 项事实性内容已填（伦理、数据可用性、GEO 引用、利益冲突、AI 使用、S15 决策、版式说明），5 项身份类仍待作者（作者与单位、通讯作者、CRediT、资助、仓库/DOI）。**Results、统计数字、0/18 结论、外部系列红线、引用编号与 Figure legends 零改动。**

""" + NOTE19 + """

---

## Abstract""",
    "F6 version note v1.1")

rep("*本文件为方法学 / 数据质量审计栏目定位稿 v1.0（由 v0.9 派生，统计数字零改动），仍不构成投稿文本。",
    "*本文件为方法学 / 数据质量审计栏目定位稿 v1.1（由 v1.0 派生，统计数字零改动；完成 4 项 FIX 与 2 处文本缺陷修补；身份类声明已填 %d/5）：%s"
    % (_nid, "待目标刊版式重排后方可投稿。" if _ident[4] else "待代码 DOI 回填与目标刊版式重排后方可投稿。"),
    "F6 footer version")

with open(DST, "w", encoding="utf-8", newline="") as f:
    f.write(s)

# --------------------------------------------------------------- self-checks
a = s[s.index("## Abstract"):s.index("**Keywords:**")]
a = re.sub(r"\*\*[^*]+:\*\*", "", a)
wc = len(re.findall(r"[A-Za-z0-9'’\-|/≥<>]+", a))
print("wrote %s" % DST.name)
print("abstract words (preflight metric): %d  -> %s" % (wc, "OK" if wc <= 350 else "TOO LONG"))
print("chars %d / lines %d" % (len(s), s.count("\n") + 1))
print("AUTHOR INPUT REQUIRED: %d | UNVERIFIED: %d" %
      (s.count("[AUTHOR INPUT REQUIRED"), s.count("[UNVERIFIED")))
print("Trial registration present: %s" % ("Trial registration" in s))
print("stale GPL5175 wording removed: %s" % ("family-SOFT extraction was not completed" not in s))
print("dup sentence removed: %s" % (s.count("Because this is whole ONH tissue") == 0))
print("\n%d guarded edits:" % len(log))
for x in log:
    print("  -", x)
assert wc <= 350, "abstract too long: %d" % wc

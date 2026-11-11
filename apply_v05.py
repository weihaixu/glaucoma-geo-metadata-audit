"""Derive manuscript v0.5 from v0.4: verified reference list, renumbered
citations, cleared citation placeholders, structured declarations.

Rules:
* Retained original references keep their original bibliographic text (not
  re-verified entry by entry; flagged in the ledger for Zotero clean-up).
* Every new reference comes from verified_references.json (PubMed esummary /
  Crossref / official GEO accession). No citation is invented here.
* Final numbering follows first appearance in the manuscript body.
"""
import csv
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
SRC = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.4.md")
DST = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.5.md")
FULL = os.path.join(WORK, "manuscript_full.txt")
NEW = json.load(open(os.path.join(ROOT, "verified_references.json"), encoding="utf-8"))
LEDGER = os.path.join(ROOT, "literature_ledger.tsv")
REFTAB = os.path.join(ROOT, "references_v05.tsv")
GUIDE = os.path.join(WORK, "青光眼生信稿件_声明填写指南.md")
REMAP = os.path.join(ROOT, "citation_remap.json")

s = open(SRC, encoding="utf-8").read()

# ---- original bibliography -------------------------------------------------
orig = {}
for line in open(FULL, encoding="utf-8"):
    m = re.match(r"^\[\d{3}\]\s+(\d+)\.\s+(.*)$", line.rstrip("\n"))
    if m:
        orig[int(m.group(1))] = m.group(2).strip()
assert len(orig) == 69

# A correction that is safe to make from the deposited author string.
ORIG_FIX = {
    8: ("Williams PA, Marsh-Armstrong N, Howell GR; Lasker/IIoA; "
        "Glaucomatous Neurodegeneration Participants (2017) Neuroinflammation "
        "in glaucoma: A new opportunity. Exp Eye Res 157:20-27. "
        "doi:10.1016/j.exer.2017.02.014"),
}


def must(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        raise RuntimeError("expected %d occurrence(s), found %d: %r" % (count, n, old[:90]))
    s = s.replace(old, new)


# ---- 1. numeric citation markers -> stable keys ---------------------------
def numeric_to_keys(m):
    nums = []
    for part in re.split(r"\s*,\s*", m.group(1)):
        if "-" in part:
            a, b = part.split("-", 1)
            nums.extend(range(int(a), int(b) + 1))
        elif part.strip().isdigit():
            nums.append(int(part.strip()))
    return ", ".join("{{o%d}}" % n for n in nums)


s = re.sub(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", numeric_to_keys, s)

# ---- 2. sentence-level edits that remove cross-disease extrapolation ------
must(" and has been implicated in microglial polarization in an ischaemic "
     "white-matter injury model {{o41}}.", ".")
must("FGFR1 has been linked to TGF-beta1-induced fibrotic responses {{o53}} "
     "and to autophagy regulation in non-ocular models {{o54}}, {{o55}}.",
     "FGFR1 has been linked to TGF-beta1-induced fibrotic responses and "
     "autophagy regulation only in non-ocular models {{o53}}, {{o54}}, {{o55}}.")
must("their relevance to ONH astrocytes is untested.",
     "their relevance to ONH astrocytes is untested; miRNA names should follow "
     "current miRBase nomenclature {{new_mirbase2019}}, and an eye-specific "
     "TGF-beta1 miRNA-mRNA interactome in trabecular meshwork cells "
     "{{new_plos2025}} illustrates the tissue context that a generic network lacks.")

# ---- 3. five [CITATION NEEDED] placeholders -------------------------------
must("have been published in recent years. ", "have been published in recent years ")
must("the most widely used ONH astrocyte series. ", "the most widely used ONH astrocyte series ")

CIT_REPL = [
    "Recent eye-specific reviews of astrocyte and microglial immune responses "
    "place these pathways in a glaucomatous context {{new_astrocyte2023}}, "
    "{{new_immune2021}}, {{new_immune2023}}.",
    "{{new_comp1_2023}}, {{new_comp2_2023}}, {{new_comp3_2024}}, "
    "{{new_comp4_2023}}, {{new_comp5_2022}}, {{new_comp6_2025}}, "
    "{{new_comp7_2026}}, {{new_currmed2024}}.",
    "{{new_geo_series}}, {{new_geo2024}}.",
    "{{new_stat1_2013}}, {{new_stat1_2022}}",
    "Single-cell atlases of the human posterior segment and ONH now resolve "
    "cell-type composition and astrocyte heterogeneity {{new_onhatlas2023}}, "
    "{{new_astrohetero2023}}, {{new_onhgwas2024}}, {{new_hopx2026}}.",
]
cit = iter(CIT_REPL)
s, n_cit = re.subn(r"`\[CITATION NEEDED:[^\]]*\]`", lambda m: next(cit), s)
assert n_cit == 5, "expected 5 CITATION NEEDED placeholders, got %d" % n_cit

# ---- 4. methodological citations in Methods / Discussion -----------------
must("Six Series Matrix files were downloaded from NCBI GEO "
     "(https://www.ncbi.nlm.nih.gov/geo/):",
     "Six Series Matrix files were downloaded from NCBI GEO "
     "{{new_geo2024}}, {{new_geo_series}} "
     "(https://www.ncbi.nlm.nih.gov/geo/):")
must("Benjamini–Hochberg correction was applied across all tested probes on a platform.",
     "Benjamini–Hochberg correction {{new_bh1995}} was applied across all "
     "tested probes on a platform.")
must("does not use empirical-Bayes variance moderation (limma); it is therefore "
     "more conservative at small sample sizes.",
     "does not use empirical-Bayes variance moderation (limma) "
     "{{new_limma2015}}; it is therefore more conservative at small sample sizes.")
must("First, pseudo-replication: 63 GSE9944 arrays",
     "First, pseudo-replication {{new_lazic2010}}, {{new_aarts2014}}, "
     "{{new_N2018}}: 63 GSE9944 arrays")
must("`make_figures_tables.py`, `cold_read_v04.py`",
     "`make_figures_tables.py`, `cold_read_v05.py`, `verify_literature.py`, "
     "`apply_v05.py`", count=2)
must("autophagic flux was not measured, and no protein-level",
     "autophagic flux was not measured {{new_autophagy2021}}, and no protein-level")

# ---- 5. version note, declarations intro, bibliography -------------------
V05_NOTE = """## 00 · 版本说明（非论文正文，复制时从下一节开始）

本文件是 **v0.5 文献与声明修订稿**。v0.4 的全部真实统计数字（`work/data/results/`、`results_m2b/`）、Figure 1–2、Table 1–4 与 Table S1–S4 均保持不变；本轮只处理参考文献与投稿声明，未改动任何结果数值、图表或模型。

1. 定位仍为**决策树分支 A**：六个原优先转录本在主模型与 M2b 敏感性模型中均 q ≥ 0.05；论文定位为**方法学/数据质量重评估**。
2. **参考文献已整体重排**：原稿 69 条中删除 38 条（含 12 条 COVID/抗病毒支线、25 条未引用或跨疾病外推条目、1 条缺血白质损伤模型引用），保留 31 条；新增 **27 条**，全部经 PubMed E-utilities、Crossref 或 GEO 官方记录核验（其中 17 篇为 2022–2026 年发表的期刊文献，另有 1 条 GEO 官方数据记录）。正文引用编号按首次出现顺序自动重排，逐条回链见 `work/data/references_v05.tsv` 与 `literature_ledger.tsv`。
3. 正文 5 处文献待补标记与文末参考文献占位说明**全部清零**；保留条目的著者/年份/卷期页沿用原稿文本，尚未逐条用 Zotero 统一为目标期刊格式，定稿前须由作者复核（见台账 `verify_status` 列）。
4. 第一轮预审提到的 "2025 PLoS One 同类 GEO 挖掘研究" 未能在 PubMed 精确复核到对应条目，本轮未沿用该说法，改引同刊 2025 年一篇眼部 TGF-β1 miRNA–mRNA 研究，并另补 8 篇可核验的 2022–2026 同类研究。
5. **声明未代填**：作者、单位、ORCID、基金、CRediT、利益冲突、AI 工具披露、代码公开 DOI 均需作者本人确认，逐项模板见 `青光眼生信稿件_声明填写指南.md`。本稿不虚构任何作者或基金信息。
6. `[UNVERIFIED]` 仍标注原稿下游分析（DAVID/KOBAS/miRNA 预测）未重跑，其数字不得当作重跑结果。原稿 docx 全程未修改。
7. **M2b 是否升为主模型仍待作者决策**：本版沿用 `results/` 为主结果（GPL571 M2 = 114 个 DEG，q = 0.145–0.691）；若改以 `results_m2b/` 为主，需同步更新 Abstract、Results 3.1/3.2、Figure 1B、Table 1–2 与 Table S2–S3。
8. 标题另备一版（若作者坚持保留假设生成定位）：*"A hypothesis-generating, donor-level re-analysis of public ONH astrocyte microarray data"*。

---

"""
i0 = s.index("## 00 · 版本说明")
i1 = s.index("## Abstract")
s = s[:i0] + V05_NOTE + s[i1:]

must("## 6. Declarations\n\n",
     "## 6. Declarations\n\n"
     "> The following fields require author confirmation; journal-specific "
     "templates and suggested wording are in the accompanying "
     "`青光眼生信稿件_声明填写指南.md`. No funding, authorship or repository "
     "identifier is invented in this draft.\n\n")

# ---- 6. assign numbers by first appearance --------------------------------
keys = []
for m in re.finditer(r"\{\{([A-Za-z0-9_]+)\}\}", s):
    if m.group(1) not in keys:
        keys.append(m.group(1))
unknown = [k for k in keys if not (k.startswith("o") and k[1:].isdigit()) and k not in NEW]
assert not unknown, "unknown citation keys: %s" % unknown
num = {k: i + 1 for i, k in enumerate(keys)}

# ---- 7. build formatted bibliography -------------------------------------
def entry(k):
    if k.startswith("o"):
        n = int(k[1:])
        return ORIG_FIX.get(n, orig[n])
    return NEW[k]["formatted"]


def compress(nums):
    nums = sorted(set(nums))
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j - i >= 2:
            parts.append("%d-%d" % (nums[i], nums[j]))
        else:
            parts.extend(str(x) for x in nums[i:j + 1])
        i = j + 1
    return ",".join(parts)


s = re.sub(r"\{\{([A-Za-z0-9_]+)\}\}", lambda m: "[[%s]]" % m.group(1), s)


def merge(m):
    ks = re.findall(r"\[\[([A-Za-z0-9_]+)\]\]", m.group(0))
    return "[%s]" % compress(num[k] for k in ks)


s = re.sub(r"\[\[[A-Za-z0-9_]+\]\](?:,\s*\[\[[A-Za-z0-9_]+\]\])*", merge, s)

ref_lines = ["%d. %s" % (num[k], entry(k)) for k in keys]
i0 = s.index("## 7. References")
i1 = s.index("## 8. Figure legends")
s = s[:i0] + "## 7. References\n\n" + "\n\n".join(ref_lines) + "\n\n---\n\n" + s[i1:]

must("*本文件为图表与事实一致性修订后的全文中稿 v0.4，仍不构成投稿文本。",
     "*本文件为文献与声明修订后的全文中稿 v0.5，仍不构成投稿文本。")
must("图表与表格由 `work/data/make_figures_tables.py` 从结果表生成；",
     "图表与表格由 `work/data/make_figures_tables.py` 从结果表生成；新增参考文献由 "
     "`work/data/verify_literature.py` 经 PubMed/Crossref/GEO 官方记录核验，编号由 "
     "`work/data/apply_v05.py` 按首次出现顺序重排；")
open(DST, "w", encoding="utf-8").write(s)

# ---- 8. ledgers -----------------------------------------------------------
retained = sorted(int(k[1:]) for k in keys if k.startswith("o"))
used_new = [k for k in keys if not k.startswith("o")]
rows = []
for k in keys:
    if k.startswith("o"):
        n = int(k[1:])
        rows.append({"new_no": num[k], "key": k, "category": "retained",
                     "old_no": n, "verify_status": "original entry; author to re-verify in Zotero",
                     "pmid": "", "doi": (re.search(r"doi:\s*(\S+)", entry(k), re.I).group(1)
                                         if re.search(r"doi:\s*(\S+)", entry(k), re.I) else ""),
                     "claim": "original claim retained in v0.4 body", "formatted": entry(k)})
    else:
        m = NEW[k]
        rows.append({"new_no": num[k], "key": k, "category": "new",
                     "old_no": "", "verify_status": m["source"], "pmid": m["pmid"],
                     "doi": m["doi"], "claim": m["claim"], "formatted": m["formatted"]})
with open(REFTAB, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t")
    w.writeheader()
    w.writerows(rows)

led = []
COVID = {11, 12, 20, 28, 39, 56, 57, 58, 59, 67, 68, 69}
for n in range(1, 70):
    if n in retained:
        action, reason, new_no = "RETAIN", "cited in v0.4 body and claim judged within scope", num["o%d" % n]
    elif n == 41:
        action, reason, new_no = "REPLACE", "ischaemic white-matter model; replaced by STAT1/IFN reviews", ""
    elif n in COVID:
        action, reason, new_no = "DELETE", "COVID-19 / antiviral sidetrack removed in v0.2", ""
    else:
        action, reason, new_no = "DELETE", "uncited in v0.4 body (cross-disease or off-topic)", ""
    led.append({"old_no": n, "action": action, "new_no": new_no, "reason": reason,
                "original_entry": orig[n]})
for k in used_new:
    m = NEW[k]
    led.append({"old_no": "", "action": "ADD", "new_no": num[k],
                "reason": "%s | %s" % (m["role"], m["source"]),
                "original_entry": m["formatted"]})
with open(LEDGER, "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=["old_no", "action", "new_no", "reason", "original_entry"],
                       delimiter="\t")
    w.writeheader()
    w.writerows(led)
json.dump({"num": num, "keys": keys, "retained": retained,
           "added": used_new, "order": "first appearance in v0.5"},
          open(REMAP, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ---- 9. declaration guide -------------------------------------------------
GUIDE_TXT = """# 投稿声明填写指南（v0.5 配套，非论文正文）

> 本指南只提供**模板与建议句式**。所有作者姓名、单位、ORCID、基金编号、
> 利益冲突结论、AI 工具使用范围与代码仓库 DOI 必须由作者本人确认后填写，
> 本稿不代填、不虚构。

## 1. 逐项待填清单（v0.5 中共 12 处 `[AUTHOR INPUT REQUIRED]`）

| # | 位置 | 必填内容 | 建议句式 / 格式 | 风险 |
|---|---|---|---|---|
| 1 | Title page | 作者姓名、单位、通讯地址 | 按目标期刊 Title Page 模板 | 缺项直接退稿 |
| 2 | Title page | 通讯作者姓名、单位、邮箱、ORCID | `Name, MD, PhD; affiliation; email; ORCID 0000-0000-0000-0000` | 无 ORCID 部分期刊拒收 |
| 3 | Methods 2.6 | 代码公开仓库 | `Code and derived tables are archived at Zenodo (doi:10.5281/zenodo.XXXXXXX) under MIT licence.` | 仅"随稿附代码"多已不满足期刊政策 |
| 4 | Results 3.2 | 若补齐 GPL5175 映射后的逐基因统计 | 需重跑 `external_validation` 后填 log2FC/p/q/AUC/CI | 不得把 `probe not mapped` 写成阴性验证 |
| 5 | Declarations · Ethics | IRB 豁免表述 | `The analysis used de-identified, publicly available GEO data; institutional review board approval was not required for the secondary analysis.` | 需按单位政策确认 |
| 6 | Data availability | GEO 标准引用 | `GSE9944, GSE2378, GSE45570; GPL8300, GPL571, GPL91, GPL5175; NCBI GEO (accessed 8 November 2026).` | 附每个 Series 的 `acc.cgi?acc=` URL |
| 7 | Code availability | 仓库 URL / DOI / 版本锁定 | `README.md`, `REPRODUCIBILITY.md`, `tables/file_manifest.csv`, `requirements.txt`/`environment.yml` | 需锁定 Python 3.9.13 与包版本 |
| 8 | CRediT | 14 类贡献逐条 | 见第 2 节 | 期刊要求全体作者确认 |
| 9 | Funding | 基金名称与编号 | `This work was supported by ... (grant no. ...).` 或 `The authors received no specific funding for this work.` | 无基金也须明写 |
| 10 | Conflict of interest | 全体作者声明 | `The authors declare no competing interests.` | 需全体作者确认 |
| 11 | AI-assisted tools | 语言编辑/文本辅助范围 | 见第 3 节 | 多数期刊要求显式披露 |
| 12 | Supplementary / 期刊版式 | TSV→投稿表格、SVG→期刊图形格式、删除 Figure 3–5 段落 | 按目标期刊 Artwork/Table 规范 | 原稿 Figure 3–5 已被本重评估否定 |

## 2. CRediT 14 角色模板（逐位作者标注，可写 "not applicable"）

`Conceptualization` · `Data curation` · `Formal analysis` · `Funding acquisition` ·
`Investigation` · `Methodology` · `Project administration` · `Resources` ·
`Software` · `Supervision` · `Validation` · `Visualization` ·
`Writing – original draft` · `Writing – review & editing`

示例句式：`AB: Conceptualization, Methodology, Formal analysis, Writing – original draft.
CD: Data curation, Validation, Writing – review & editing. All authors read and
approved the final manuscript.`（作者缩写与贡献须由作者确认。）

## 3. AI 辅助工具披露（按目标期刊政策二选一，不得省略）

- 若仅用于语言/文字辅助：`During the preparation of this work the authors used
  [tool name] for language editing and text restructuring. The authors reviewed
  and edited all output and take full responsibility for the content of the
  publication.`
- 若涉及分析代码/统计解释：须额外写明工具参与的具体环节、人工复核方式与
  可复现脚本位置（`reanalysis.py`, `reanalysis_m2b.py`,
  `make_figures_tables.py`, `cold_read_v05.py`）。
- 填充前核对目标期刊最新的 AI / LLM 作者署名与披露政策；多数期刊不接受
  AI 工具列为作者。

## 4. 代码与数据公开的最小可核验包

1. 6 个 series matrix、3 个 annot 的获取方式与 SHA-256（`tables/file_manifest.csv`）。
2. 全部脚本、运行命令、环境版本（`REPRODUCIBILITY.md`, `README.md` v2.1）。
3. `results/`、`results_m2b/`、`figures/`、`tables/` 全部导出表。
4. 固定版本号（tag / release），生成 DOI 后回填正文与 Data/Code availability。
5. 若仓库含原始数据，确认 GEO 数据的再分发条款与许可。

## 5. 提交前逐刊政策核对（作者执行）

- 是否接受纯计算重分析 / 阴性结果 / 方法学审计稿；
- 是否要求 wet-lab 验证或独立队列；
- 数据可用性语句的最低要求（GEO accession 是否足够）；
- 代码是否必须公开到带 DOI 的仓库；
- AI 工具披露与 CRediT 格式；
- 单位预警名单、APC、正式 iThenticate/Turnitin 查重。

> 本指南与 `work/data/references_v05.tsv`、`literature_ledger.tsv`、
> `verified_references.tsv` 配套使用。新增 27 条文献均有 PMID/DOI 或 GEO
> 官方 URL 可核验；保留的 31 条沿用原稿条目，定稿前需用 Zotero/EndNote
> 统一为目标期刊格式并逐条回链。
"""
open(GUIDE, "w", encoding="utf-8").write(GUIDE_TXT)

print("wrote", DST)
print("references: %d (retained %d / new %d)" % (len(keys), len(retained), len(used_new)))
print("new 2022-2026:", sum(1 for k in used_new if NEW[k]["year"] >= "2022"))
print("wrote", REFTAB, LEDGER, GUIDE, REMAP)
print("first 8:", ref_lines[:8])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_v10.py -- derive manuscript v1.0 (methodology / data-quality framing)
and cold_read_v10.py from the frozen v0.9.

Every manuscript substitution is asserted to match exactly once. All Results
sections, all citation numbers, all numeric claims, all declaration
placeholders and every red-line sentence are preserved verbatim. v0.7, v0.8,
v0.9, results/, Figures 1-2 and Tables 1-4 are never modified. Decision A stands.
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
V9 = WORK / "青光眼生信稿件_全文重写稿_v0.9.md"
V10 = WORK / "青光眼生信稿件_全文重写稿_v1.0.md"
CR9 = ROOT / "cold_read_v09.py"
CR10 = ROOT / "cold_read_v10.py"

s = V9.read_text(encoding="utf-8")
assert hashlib.sha256(V9.read_bytes()).hexdigest().startswith("05c1aa8eb12e"), "v0.9 changed"
nrep = 0


def rep(old, new, tag=""):
    global s, nrep
    c = s.count(old)
    assert c == 1, "anchor [%s] matched %d times: %.110r" % (tag, c, old[:110])
    s = s.replace(old, new, 1)
    nrep += 1


def span(start, end, new, tag=""):
    global s, nrep
    i = s.index(start)
    j = s.index(end, i)
    assert i < j, tag
    s = s[:i] + new + s[j:]
    nrep += 1


# ---------------------------------------------------------------- title / running title
rep(
    "# Donor-level re-analysis of glaucomatous optic nerve head astrocyte microarrays: pseudo-replication and ancestry–disease confounding account for most reported differential expression",
    "# A reusable metadata-audit and donor-level re-analysis framework for public gene-expression series: a glaucomatous optic nerve head case study",
    "title")

rep(
    "**Running title:** Donor-level re-analysis of glaucomatous ONH astrocytes",
    "**Running title:** Reusable metadata audit of public expression series",
    "running title")

# ---------------------------------------------------------------- version note
rep(
    "本文件是 **v0.9 投稿可行性增强稿（P1-a / P1-b / P1-c / P1-d，P1 路线图全部执行完毕）**。v0.7 的全部真实统计数字（`work/data/results/`、`results_m2b/`、`results_diagnostics/`、`results_limma/`、`results_genelevel/`）、Figure 1–2、Table 1–4 与 Table S1–S12 均保持不变；v0.8 新增 Table S13–S16 与官方核验版 S14；v0.9 新增①外部跨组织方向一致性与 Table S17、②供体重建与混杂审计及 Table S18。所有新增结果都在独立目录（`results_power/`、`results_gpl5175/`、`results_audit/`、`results_external/`），决策 A 不变，主结论 0/18 与分支 A 定位不变，**仍不可投稿**：P1 只改善方法学与报告质量，没有新增独立人类队列、湿实验或真正的独立复现。",
    "本文件是 **v1.0 方法学 / 数据质量审计栏目定位稿**（由 v0.9 派生，定位重排，统计数字与红线措辞零改动）。v0.7 的全部真实统计数字（`work/data/results/`、`results_m2b/`、`results_diagnostics/`、`results_limma/`、`results_genelevel/`）、Figure 1–2、Table 1–4 与 Table S1–S12 均保持不变；v0.8 新增 Table S13–S16 与官方核验版 S14；v0.9 新增 Table S17–S18；v1.0 新增 Table S19 可复用元数据审计清单模板。所有新增结果都在独立目录（`results_power/`、`results_gpl5175/`、`results_audit/`、`results_external/`），决策 A 不变，主结论 0/18 不变。**定位改投方法学 / 数据质量审计栏目后，科学叙事从「六基因重评估」改为「公共表达谱复用前的可复用审计清单 + 一个 worked example」；创新性不足这一拒稿理由的权重下降，但 12 项声明、代码 DOI、单位口径确认与期刊格式未完成前，仍不构成投稿文本。**",
    "version note head")

rep(
    "1. 定位仍为**决策树分支 A**：六个原优先转录本在主模型与 M2b 敏感性模型中均 q ≥ 0.05；论文定位为**方法学/数据质量重评估**。",
    "1. **投稿定位为方法学 / 数据质量审计论文**；统计结论仍为**决策树分支 A**（六个原优先转录本在主模型与 M2b 敏感性模型中均 q ≥ 0.05）。v1.0 把六基因降级为 worked example / 有界的假设生成案例，主线改为 Table S19 的五类审计清单及其在 7 个 series matrix 上的应用。",
    "version note item 1")

rep(
    "本项是跨组织方向一致性练习与审计工具压力测试，**不是独立复现、不是验证队列、不支持也不否定主结论 0/18**；输出在独立 `results_external/`，`results/` 一个字节未改。\n\n---\n\n## Abstract",
    "本项是跨组织方向一致性练习与审计工具压力测试，**不是独立复现、不是验证队列、不支持也不否定主结论 0/18**；输出在独立 `results_external/`，`results/` 一个字节未改。\n"
    "17. **v1.0 栏目重定位（2026-11-09）**：按作者决定把投稿方向改为方法学 / 数据质量审计栏目。改标题、Running title、结构化摘要、Introduction 立题与 aims、新增 Methods 2.8（可复用五类审计清单）、改写 Discussion 首段与 Conclusions、Keywords 改为审计与报告规范主题、§9 增加 Table S19。**Results 3.1–3.5、Methods 2.1–2.7、Declarations、References、Figure legends 与全部引用编号原样保留**；所有统计数字、0/18 结论、外部系列红线、12 项声明与 10 个 UNVERIFIED 标记一处未动。候选 article type 与官方核验见 `青光眼生信稿件_方法学栏目定位与改稿方案.html`；本稿保持期刊中立，不写死任何刊名、分区、APC 或影响因子。\n\n---\n\n## Abstract",
    "version note item 17")

# ---------------------------------------------------------------- Abstract (full span)
NEW_ABSTRACT = """## Abstract

**Background:** Public gene-expression series are reused more often than their deposited metadata are audited. Technical replicates, paired eyes, repeated hybridisations of the same RNA and structurally empty strata can make a case-control coefficient non-identifiable even when the design matrix is full rank. We specified a short, executable metadata checklist to run before a series is reused, and applied it to a widely reused glaucomatous optic nerve head (ONH) astrocyte series as a worked example.

**Methods:** The checklist encodes five read-only checks on deposited metadata: structured versus free-text covariates, group-by-ancestry zero cells, replicate and donor overlap, platform annotation availability, and expression scale with excludable groups (Table S19). Six GEO series matrices were audited (GSE9944 on GPL91/GPL571/GPL8300, GSE2378 on GPL91/GPL8300, GSE45570 on GPL5175). Technical replicate arrays were collapsed to donors and four models (M0–M3) were fitted per platform, with donor-level OLS M2 controlling ancestry where deposited and Benjamini–Hochberg (BH) q < 0.05 as the pre-specified primary analysis. Detectable effect sizes were derived post hoc from per-probe standard errors and residual degrees of freedom; limma empirical-Bayes moderation and three gene-level conventions were used as sensitivity analyses. The checklist was then stress-tested on one external series (GSE27276) under three unit conventions.

**Results:** The audit flagged free-text-only covariates in 3 of 6 primary matrices, zero ancestry-by-disease cells in 2 of 6, replicate or donor overlap in 2 of 6, and scale or exclusion caveats in 3 of 6. In the worked example, 63 GSE9944 arrays resolved to 21 donors on GPL571, 16 on GPL8300 and 2 on GPL91, with five donor identifiers shared between platforms; DEG counts fell from 1375 (M0) to 114 (M2) on GSE9944-GPL571 and from 472 to 0 on GSE9944-GPL8300. None of the six originally prioritized transcripts was significant at BH q < 0.05 in any of the three annotated discovery platforms (18 tests; q = 0.145–0.691); all six **did not survive** the primary model and were **not significant** after correction. Post-hoc detectable effect sizes exceeded the observed |log2FC| in 11 of 18 tests, so smaller effects cannot be excluded; this is not a test of equivalence. In the external stress test, disease was completely confounded with tissue procurement and postmortem delay (phi = 1.0; design rank 2 of 4), and all six transcripts remained non-significant under all three unit conventions.

**Conclusions:** A five-class metadata checklist is a reproducible, transferable output that can be applied before any public series is reused; the glaucoma series supplies a worked example rather than a biological claim. The six transcripts should not be described as glaucoma candidates on the basis of these data. The checklist does not supply an independent replication or wet-laboratory validation, and non-significant results must not be interpreted as evidence of absence.

**Keywords:** metadata audit; reproducibility; public gene-expression series; pseudo-replication; donor-level analysis; ancestry confounding; false discovery rate; reporting standards

---

"""
span("## Abstract", "## 1. Introduction", NEW_ABSTRACT, "abstract")

# ---------------------------------------------------------------- Introduction lead
rep(
    "## 1. Introduction\n\nGlaucoma is a progressive",
    """## 1. Introduction

Public gene-expression repositories are reused far more often than their deposited metadata are audited. A secondary analysis typically inherits the original unit of analysis, the platform annotation available at the time, and whatever covariates happen to be encoded in free-text sample characteristics. When technical replicates, paired eyes, repeated hybridisations of the same RNA, or structurally empty strata are present, the resulting case-control coefficient is not identifiable as a disease effect even when the design matrix is full rank. Reporting standards for microarray reuse exist, but a short, executable checklist that can be run on a series matrix before any model is fitted has not been part of routine practice.

This study treats that gap as a methodological problem. We specify five read-only checks on deposited metadata (Table S19), implement them in a reusable script, and apply them to six primary series matrices plus one external candidate. The glaucoma optic nerve head (ONH) astrocyte series then serves as a worked example: it supplies a concrete, repeatedly reused dataset on which the consequences of each failed check can be quantified. The six transcripts prioritized in the original report are retained as a bounded, hypothesis-generating case study, not as the object of a biological claim. No mechanistic, therapeutic or clinical conclusion is drawn.

The disease context of that worked example is briefly summarised below before the audit aims are stated.

Glaucoma is a progressive""",
    "intro lead")

rep(
    """The present study therefore asks a different question from the original analysis: not "which genes are associated with glaucoma?", but "how many of the reported associations remain after the analysis unit, donor structure and multiple testing are handled correctly?". We reconstructed the analysis from the publicly deposited series matrices, explicitly modelled technical replicates and donor-level covariates, and reported the outcome for the six transcripts that the original report had prioritized. This is a methodological re-assessment with a bounded, hypothesis-generating interpretation; it was not designed to test a causal mechanism or to support clinical claims.""",
    """The present study therefore asks a methodological question: which defects in deposited metadata can be detected before a series is reused, and what happens to a published transcript list when they are handled explicitly? We reconstructed the analysis from the publicly deposited series matrices, applied the checklist to each series, modelled technical replicates and donor-level covariates, and reported the outcome for the six transcripts that the original report had prioritized as a bounded, hypothesis-generating case study. This is a methodological and data-quality re-assessment; it was not designed to test a causal mechanism or to support clinical claims.""",
    "intro question")

rep(
    "The specific aims were: (1) to reconstruct the exact array-to-donor structure of the three series; (2) to quantify the change in differential expression calls across a pre-specified hierarchy of four models; and (3) to determine whether the six previously prioritized transcripts survive the primary model and whether a whole-tissue comparison provides any supporting evidence.",
    "The specific aims were: (1) to define and implement a five-class metadata checklist that can be run on any public series matrix before reuse (Table S19); (2) to quantify, on a worked example, how differential expression calls change when the analysis unit, donor structure and multiple testing are handled under a pre-specified hierarchy of four models; and (3) to report the outcome for six previously prioritized transcripts as a bounded case study, and to stress-test the checklist on one external series without treating that comparison as validation.",
    "intro aims")

# ---------------------------------------------------------------- Methods 2.8
rep(
    "This is a cross-tissue directional-concordance exercise, not an independent replication or a validation cohort.\n\n---\n\n## 3. Results",
    """This is a cross-tissue directional-concordance exercise, not an independent replication or a validation cohort.

### 2.8 Reusable metadata-audit checklist

The audit is specified as five read-only checks on the deposited metadata of a series matrix (Table S19): (C1) whether age and sex are available as structured fields rather than compound free text; (C2) whether the group-by-ancestry table contains zero cells, with phi, Pearson r, VIF, condition number and design rank reported; (C3) whether the declared donor count differs from the array count because of technical replicates, paired eyes, shared donor identifiers or repeated hybridisations; (C4) whether an official platform annotation file exists and what fraction of matrix probes can be mapped; and (C5) whether the expression scale is compatible with the intended fold-change threshold and which groups must be excluded before fitting. `geo_metadata_audit.py` implements the checks and writes a per-series record with a FAIL/WARN/PASS flag together with the underlying metrics (`results_audit/`, Table S16). The checklist is deliberately a pre-fitting step: it does not estimate a disease effect, does not validate a finding and does not replace an a-priori power calculation. Its application to an external series is reported separately as a cross-tissue directional-concordance exercise (section 2.7), not as an independent replication. The template, decision rules, minimum reporting schema and interpretation boundaries are supplied as Table S19 so that the same checks can be applied to series outside this study.

---

## 3. Results""",
    "methods 2.8")

# ---------------------------------------------------------------- Discussion first paragraph
rep(
    "This donor-level re-analysis of a repeatedly reused glaucomatous ONH astrocyte series found that the transcript list on which downstream immune, autophagy and miRNA interpretations were built is not robust to the unit of analysis, donor ancestry and multiple-testing control. After collapsing technical replicates, adjusting for available covariates and applying BH correction, none of the six previously prioritized transcripts remained significant in any annotated discovery dataset, and the direction of the two most prominent effects was opposite to that in the original report. The appropriate conclusion is therefore a methodological one, not a biological one. This conclusion was unchanged when the statistical engine was replaced by limma's empirical-Bayes moderation and when probe selection was removed by gene-level aggregation.",
    "This study used a repeatedly reused glaucomatous ONH astrocyte series as a worked example for a five-class metadata audit of public expression data. The audit identified free-text-only covariates, structurally empty ancestry-by-disease cells, technical replicates and shared donor identifiers, platform-dependent annotation gaps, and scale or exclusion decisions that are rarely reported when a series is reused (Tables S16 and S19). Applying the corresponding corrections in the primary model left none of the six previously prioritized transcripts significant in any annotated discovery dataset, and the direction of the two most prominent effects was opposite to that in the original report. The appropriate conclusion is therefore a methodological one, not a biological one. This conclusion was unchanged when the statistical engine was replaced by limma's empirical-Bayes moderation and when probe selection was removed by gene-level aggregation.",
    "discussion lead")

# ---------------------------------------------------------------- Conclusions
rep(
    """## 5. Conclusions

In this donor-level re-analysis of public ONH astrocyte microarray data, technical replicate aggregation, covariate adjustment and BH correction reduced the reported differential expression signal substantially, and none of the six previously prioritized transcripts (FGFR1, SMAD1, STAT1, TGFBR2, CASP1, CASP4) was statistically significant in the primary model; all six **did not survive** FDR control. Effect directions for STAT1 and CASP1 were also opposite to those originally reported. The six transcripts should therefore not be described as glaucoma candidates on the basis of these data. The reproducible output of this study is a quantified demonstration of how pseudo-replication and ancestry–disease confounding generate apparently significant gene lists, together with a documented pipeline for re-analysing these public series. An external cross-tissue comparison did not provide independent confirmation and was itself limited by complete confounding of disease with tissue procurement.""",
    """## 5. Conclusions

We specified and implemented a five-class, read-only metadata checklist for public gene-expression series and applied it to six primary series matrices plus one external candidate (Tables S16 and S19). In the glaucoma ONH astrocyte worked example, technical replicate aggregation, covariate adjustment and BH correction reduced the reported differential expression signal substantially, and none of the six previously prioritized transcripts (FGFR1, SMAD1, STAT1, TGFBR2, CASP1, CASP4) was statistically significant in the primary model; all six **did not survive** FDR control. Effect directions for STAT1 and CASP1 were also opposite to those originally reported, so these transcripts should not be described as glaucoma candidates on the basis of these data. The reproducible output of this study is the checklist, its implementation and a documented donor-level pipeline, not a set of mechanistic or therapeutic claims. An external cross-tissue comparison did not provide independent confirmation and was itself limited by complete confounding of disease with tissue procurement. The checklist is intended as a pre-fitting screen for series reuse; it does not supply an independent cohort, a wet-laboratory validation or a test of equivalence.""",
    "conclusions")

# ---------------------------------------------------------------- supplementary S19
rep(
    "**Table S18.** Donor reconstruction and confounding audit of GSE27276: 36 arrays versus 28 declared donors, 13 control donors recovered from postmortem delay, two correlation-based case-side merges, phi = 1.0 for disease versus procurement and versus postmortem delay, and design rank 2 of 4 (`tables/TableS18_external_donor_reconstruction.tsv`; `results_external/`).\n\nFigure 1–2",
    """**Table S18.** Donor reconstruction and confounding audit of GSE27276: 36 arrays versus 28 declared donors, 13 control donors recovered from postmortem delay, two correlation-based case-side merges, phi = 1.0 for disease versus procurement and versus postmortem delay, and design rank 2 of 4 (`tables/TableS18_external_donor_reconstruction.tsv`; `results_external/`).

**Table S19.** Reusable metadata-audit checklist template for public gene-expression series: five read-only checks (C1–C5), required deposited fields, decision rules, reported metrics, FAIL/WARN meanings, actions before reuse and applicability boundaries, together with a minimum per-series reporting schema and mandatory interpretation boundaries (`tables/TableS19_metadata_audit_checklist.md|.tsv`; implementation in `work/data/geo_metadata_audit.py`). This is the primary methodological deliverable of the re-framed article; it contains no disease-effect estimate and no transcript-level claim.

Figure 1–2""",
    "S19 entry")

# ---------------------------------------------------------------- footer
rep(
    "*本文件为投稿可行性增强后的全文中稿 v0.9（P1 路线图全部执行完毕），仍不构成投稿文本。",
    "*本文件为方法学 / 数据质量审计栏目定位稿 v1.0（由 v0.9 派生，统计数字零改动），仍不构成投稿文本。",
    "footer")

# ---------------------------------------------------------------- invariants
assert s.count("[AUTHOR INPUT REQUIRED") == 12, s.count("[AUTHOR INPUT REQUIRED")
assert s.count("[UNVERIFIED") == 10, s.count("[UNVERIFIED")
assert "## 3. Results" in s and "### 3.5 Applying the audit checklist" in s
assert "### 2.8 Reusable metadata-audit checklist" in s
assert s.count("## 5. Conclusions") == 1
with open(V10, "w", encoding="utf-8", newline="") as f:
    f.write(s)
print("v1.0 written: %d substitutions, %d -> %d chars" % (nrep, len(V9.read_text(encoding="utf-8")), len(s)))
print("sha256 v0.9: %s" % hashlib.sha256(V9.read_bytes()).hexdigest()[:12])
print("sha256 v1.0: %s" % hashlib.sha256(V10.read_bytes()).hexdigest()[:12])

# ================================================================ cold_read_v10.py
c = CR9.read_text(encoding="utf-8")
ncr = 0


def crep(old, new, tag=""):
    global c, ncr
    k = c.count(old)
    assert k == 1, "cold-read anchor [%s] matched %d times: %.110r" % (tag, k, old[:110])
    c = c.replace(old, new, 1)
    ncr += 1


crep('"""Cold-read v9 for the P1-complete manuscript v0.9.',
     '"""Cold-read v10 for the methodology / data-quality framed manuscript v1.0.', "docstring")
crep('os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.9.md")',
     'os.path.join(WORK, "青光眼生信稿件_全文重写稿_v1.0.md")', "MAN")
crep('os.path.join(WORK, "青光眼生信稿件_cold-read_v0.9报告.md")',
     'os.path.join(WORK, "青光眼生信稿件_cold-read_v1.0报告.md")', "OUT")
crep('lines = ["# Cold-read v0.9（P1 路线图完成版）\\n",',
     'lines = ["# Cold-read v1.0（方法学 / 数据质量审计定位版）\\n",', "report title")

R_GROUP = r'''
# --- 15. R group: v1.0 methodology / data-quality re-framing ------------------
V7 = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.7.md")
V8 = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.8.md")
V9 = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.9.md")
S19M = os.path.join(TABD, "TableS19_metadata_audit_checklist.md")
S19T = os.path.join(TABD, "TableS19_metadata_audit_checklist.tsv")

new_title = ("# A reusable metadata-audit and donor-level re-analysis framework "
             "for public gene-expression series: a glaucomatous optic nerve head case study")
old_title = ("# Donor-level re-analysis of glaucomatous optic nerve head astrocyte "
             "microarrays: pseudo-replication and ancestry")
chk("R 定位", "v1.0 标题为可复用审计框架 + case study", new_title in s, "")
chk("R 定位", "旧标题已从正文移除", old_title not in s, "")

abst10 = seg("## Abstract", "## 1. Introduction")
intro10 = seg("## 1. Introduction", "## 2. Materials and methods")
conc10 = seg("## 5. Conclusions", "## 6. Declarations")
for p in ["worked example", "Table S19", "five-class", "metadata checklist",
          "did not survive", "not significant", "reporting standards"]:
    chk("R 摘要结论", "Abstract / Keywords / Conclusions 含 `%s`" % p, p in abst10 or p in conc10,
        "Abstract %d / Conclusions %d" % (abst10.count(p), conc10.count(p)))
for p in ["worked example", "hypothesis-generating", "methodological question",
          "five read-only checks"]:
    chk("R 立题", "Introduction 含 `%s`" % p, p in intro10, "命中 %d" % intro10.count(p))
chk("R 立题", "旧 aims 的基因导向问句已移除",
    'which genes are associated with glaucoma?' not in intro10, "")
chk("R 方法", "新增 Methods 2.8 审计清单",
    "### 2.8 Reusable metadata-audit checklist" in s, "")
chk("R 方法", "Methods 2.8 列出 C1–C5",
    all(("(C%d)" % k) in s for k in range(1, 6)), "")
chk("R 补充", "§9 有 Table S19 条目",
    "**Table S19.**" in s and "TableS19_metadata_audit_checklist" in s, "")
chk("R 补充", "Table S19 md/tsv 存在且 tsv 为 5 行",
    os.path.exists(S19M) and os.path.exists(S19T)
    and len(pd.read_csv(S19T, sep="\t")) == 5, "")
for p in ["new method", "novel framework", "we propose a new", "for the first time"]:
    chk("R 反面", "不得出现 `%s`" % p, p not in body, "命中 %d" % body.count(p))
for p in ["BMC Medical Research Methodology", "BioData Mining", "impact factor",
          "Scopus", "article processing charge"]:
    chk("R 期刊中立", "正文不写死 `%s`" % p, p not in s, "命中 %d" % s.count(p))
chk("R 结论", "Conclusions 仍声明六基因未存活",
    bool(re.search(r"did not survive|not significant|no longer", conc10, re.I)), "")
chk("R 结论", "Conclusions 保留无独立验证表述",
    "does not supply an independent cohort" in conc10, "")

# Citation set must be identical to v0.9 (re-framing must not touch references).
def cite_set(txt):
    b = txt[txt.index("## Abstract"):txt.index("## 6. Declarations")]
    out = set()
    for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", b):
        for part in re.split(r"\s*,\s*", m.group(1)):
            if "-" in part:
                a, z = part.split("-")[:2]
                if a.isdigit() and z.isdigit():
                    out.update(range(int(a), int(z) + 1))
            elif part.isdigit():
                out.add(int(part))
    return out


v9txt = open(V9, encoding="utf-8").read()
chk("R 引用守恒", "v1.0 正文引用编号集合与 v0.9 完全一致",
    cite_set(s) == cite_set(v9txt), "v1.0 %d / v0.9 %d" % (len(cite_set(s)), len(cite_set(v9txt))))
chk("R 占位符", "12 项声明与 10 个 UNVERIFIED 仍保留",
    s.count("[AUTHOR INPUT REQUIRED") == 12 and s.count("[UNVERIFIED") == 10,
    "%d / %d" % (s.count("[AUTHOR INPUT REQUIRED"), s.count("[UNVERIFIED")))
chk("R 红线", "0/18 与外部系列红线仍写入",
    "0/18" in s and "not an independent replication" in s, "")
for tag, path, prefix in [("v0.7", V7, "3fcfdbb3d2d2"),
                          ("v0.8", V8, "7bb05464f69f"),
                          ("v0.9", V9, "05c1aa8eb12e")]:
    chk("R 版本冻结", "%s 字节未变" % tag,
        os.path.exists(path) and hashlib.sha256(open(path, "rb").read()).hexdigest().startswith(prefix),
        prefix)
p04 = os.path.join(ROOT, "results", "04_deg_primary_M2.csv")
chk("R 主结果冻结", "04_deg_primary_M2.csv sha256 未变",
    hashlib.sha256(open(p04, "rb").read()).hexdigest().startswith("48876f29f3d0"), "")
chk("R 版本说明", "版本说明含 v1.0 栏目重定位条",
    "v1.0 栏目重定位" in s, "")

'''
crep("# --- report ---", R_GROUP + "\n# --- report ---", "R group")
crep('lines.append("- 本检查不能替代机构权限下的 iThenticate/Turnitin 相似度自查，也不能替代逐刊政策人工核对。\\n")',
     'lines.append("- v1.0 新增 **R 组**：方法学 / 数据质量栏目定位断言（新标题、worked example 立题、Methods 2.8、Table S19、期刊中立、禁用 overclaim、引用编号集合与 v0.9 一致、v0.7/v0.8/v0.9 与主结果字节未变、12 项声明与 10 个 UNVERIFIED 保留）。\\n")\n'
     'lines.append("- 本检查不能替代机构权限下的 iThenticate/Turnitin 相似度自查，也不能替代逐刊政策人工核对。\\n")',
     "report note")

with open(CR10, "w", encoding="utf-8", newline="") as f:
    f.write(c)
print("cold_read_v10.py derived; %d substitutions, %d chars" % (ncr, len(c)))
print("OK -> %s / %s" % (V10.name, CR10.name))

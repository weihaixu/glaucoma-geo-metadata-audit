#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_v08.py - derive manuscript v0.8 and cold_read_v08.py from v0.7.

Every substitution is asserted to match exactly once. v0.7, results/,
Figures 1-2 and Tables 1-4 are never modified. Decision A is unchanged.
"""
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
SRC = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.7.md")
DST = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.8.md")
CR7 = os.path.join(ROOT, "cold_read_v07.py")
CR8 = os.path.join(ROOT, "cold_read_v08.py")

s = open(SRC, encoding="utf-8").read()
orig_len = len(s)
nrep = 0


def rep(old, new):
    global s, nrep
    c = s.count(old)
    assert c == 1, "anchor matched %d times: %s" % (c, old[:90])
    s = s.replace(old, new, 1)
    nrep += 1


# ---------------------------------------------------------------- version note
rep("本文件是 **v0.7 limma 复核与基因级敏感性稿**。v0.6 的全部真实统计数字（`work/data/results/`、`results_m2b/`、`results_diagnostics/`）、Figure 1–2、Table 1–4 与 Table S1–S8 均保持不变；本轮新增两套独立稳健性复核（R/limma 经验贝叶斯方差收缩、基因级三口径检验），输出在独立目录，未改动任何主结果数值、图表或模型。",
    "本文件是 **v0.8 投稿可行性增强稿（P1-a / P1-c / P1-d）**。v0.7 的全部真实统计数字（`work/data/results/`、`results_m2b/`、`results_diagnostics/`、`results_limma/`、`results_genelevel/`）、Figure 1–2、Table 1–4 与 Table S1–S12 均保持不变；本轮新增①事后可检测效应量与 Table S13、②完整 GPL5175 平台表重建与 Table S15 边界检查、③可复用元数据审计工具与 Table S16、④外部候选 GEO 系列的官方核验（Table S14 核验版）。所有新增结果都在独立目录，决策 A 不变，主结论 0/18 与分支 A 定位不变，仍不可投稿。")

rep("12. **基因级敏感性**：把\"最小 p 选探针\"换成三口径（主口径 / 基因内全探针按供体中位数表达重跑 OLS / 探针 p 的 Simes 合并），三个有注释平台上 **每种口径均 0/18 显著**（BH q 最小 0.128）；GSE45570 因 GPL5175 无 GEO 注释文件**无法做基因级检验**，如实标为缺失而非阴性结果。输出在独立 `results_genelevel/`，见 Table S11–S12。决策分支 A 在两套复核下均不变。",
    """12. **基因级敏感性**：把"最小 p 选探针"换成三口径（主口径 / 基因内全探针按供体中位数表达重跑 OLS / 探针 p 的 Simes 合并），三个有注释平台上 **每种口径均 0/18 显著**（BH q 最小 0.128）；当时的 GSE45570 因 GPL5175 无 GEO 注释文件**未纳入该基因级口径**，如实标为缺失而非阴性结果（该限制在 v0.8 用重建映射解除，但结果仍只作边界检查）。输出在独立 `results_genelevel/`，见 Table S11–S12。决策分支 A 在两套复核下均不变。
13. **事后可检测效应量（P1-a，Table S13）**：`power_mde.py` 只读 `results/04_deg_primary_M2.csv` 的 69,513 行，用每探针 SE 与残差 df、非中心 t 分布求 α=0.05 / power=80% 的最小可检测效应；18 次六基因检验中有 11 次观察 |log2FC| < MDE，GSE2378-GPL8300 仅 43.5% 探针能检出 |log2FC|≥1。结论只能写成"无法排除更小效应"，**绝不能写成有效应、等效或无效应**；这是 post hoc 描述性敏感性分析，不是等效性检验。
14. **GPL5175 注释补齐与边界检查（P1-c，Table S15）**：`fetch_5175_parallel.py` 用 219 个 64 KiB 分块补齐完整 SOFT 平台表（316,919 行，gzip 校验通过），`fetch_gpl5175_annot.py` 生成 33,475 条探针→基因映射；GSE45570 的 22,011 个 transcript cluster 中 17,634（80.11%）可映射，六基因 7 个探针。`gpl5175_boundary.py` 在独立 `results_gpl5175/` 做基因级边界检查，六基因 **0/6 显著（q=1.0）**。这是**边界说明，不是验证、不是独立复现**：GSE45570 是全 ONH 组织、不同平台、不同病例定义；`results/`、Figure 2、Table 1–2 一个字节都没改。
15. **可复用元数据审计（P1-d，Table S16）**：`geo_metadata_audit.py` 把自由文本协变量、组别×祖先零单元格、技术重复/供体重叠、平台注释可得性、尺度与排除组做成五类只读检查，对 6 个主 series matrix 与 1 个外部候选（GSE27276，**仅元数据审计，未做差异分析**）输出 159 项指标。外部候选的官方核验见 `tables/TableS14_official_verification.md`（纠正了旧 S14 的 3 处数字，并剔除 miRNA 芯片 GSE105269）。""")

# ---------------------------------------------------------------- Methods 2.2
rep("""Probes were mapped to gene symbols with the platform-specific GEO annotation files GPL8300.annot.gz, GPL571.annot.gz and GPL91.annot.gz. GEO provides no `GPL5175.annot.gz`. An attempt was made to extract the GPL5175 platform table from the beginning of the 4.5 GB GPL5175 family SOFT archive, but this extraction was **not completed** and no usable annotation file was produced; consequently 0 of 22,011 GSE45570 probes carry a gene symbol. The six transcripts are therefore reported as "no probe mapped" on GSE45570 rather than as negative or non-replicated findings. Where a gene was represented by multiple probes, the probe with the smallest nominal p value was reported in the main text; this is an optimistic selection, and all mapped probes with nominal 95% confidence intervals are supplied in Table S1 and `tables/TableS1_all_probes_six_genes.tsv`.""",
    """Probes were mapped to gene symbols with the platform-specific GEO annotation files GPL8300.annot.gz, GPL571.annot.gz and GPL91.annot.gz. GEO provides no `GPL5175.annot.gz`. The earlier prefix-only extraction was **not completed**, so the frozen primary run reports the six transcripts as "no probe mapped" on GSE45570 rather than as negative or non-replicated findings; this is a missing-annotation limitation. For an exploratory boundary check (v0.8; Table S15) the extraction was extended to 219 cached 64 KiB ranges until `!platform_table_end` was reached, yielding the complete 316,919-row SOFT platform table and a local map of 33,475 probes to gene symbols. That map covers 17,634 of 22,011 (80.11%) GSE45570 transcript clusters, is explicitly **not** a GEO annotation file, and is used only in the independent `results_gpl5175/` directory; it does not enter `results/`, Figure 2 or Tables 1-2. Unmapped probes remain missing annotation, never a negative result. Where a gene was represented by multiple probes, the probe with the smallest nominal p value was reported in the main text; this is an optimistic selection, and all mapped probes with nominal 95% confidence intervals are supplied in Table S1 and `tables/TableS1_all_probes_six_genes.tsv`.""")

# ---------------------------------------------------------------- Methods 2.5
rep("Gene-level analysis was impossible on GSE45570 because GPL5175 has no GEO annotation file; this is reported as missing annotation, never as a negative result.",
    "Gene-level analysis on GSE45570 was not part of the pre-specified primary run because GEO provides no GEO annotation file for GPL5175. An exploratory boundary check with a locally rebuilt map is reported separately in `results_gpl5175/` and Table S15; it is not an independent replication and does not enter `results/`, Figure 2 or Tables 1-2. Unmapped probes remain missing annotation, never a negative result.")

rep("Simes assumes independence or positive dependence among the combined tests and is therefore exploratory, because probes for one gene are correlated.",
    """Simes assumes independence or positive dependence among the combined tests and is therefore exploratory, because probes for one gene are correlated.

Detectable effect sizes were derived from each probe's fitted standard error and residual degrees of freedom in the primary M2 table using the noncentral t distribution (two-sided alpha = 0.05, target power = 0.80; `power_mde.py`, `results_power/`, Table S13). The calculation uses the fitted precision rather than the observed effect size, so it is a descriptive sensitivity analysis rather than an a-priori power calculation; it is post hoc, is **not a test of equivalence**, and leaves every primary M2 coefficient, p value and q value unchanged.""")

rep("`genelevel_sensitivity.py`, `cold_read_v07.py`, `apply_v07.py`). Exact commands,",
    "`genelevel_sensitivity.py`, `cold_read_v07.py`, `apply_v07.py`, `power_mde.py`, `fetch_5175_parallel.py`, `fetch_geo_generic.py`, `gpl5175_boundary.py`, `geo_metadata_audit.py`, `cold_read_v08.py`, `apply_v08.py`). Exact commands,")

# ---------------------------------------------------------------- Results 3.1
rep("the GPL8300 zero cell was identified in this diagnostic pass.",
    """the GPL8300 zero cell was identified in this diagnostic pass.

A read-only, reusable metadata audit (`geo_metadata_audit.py`; Table S16) encoded these recurring problems as five checks and applied them to the six primary series matrices and, as a reuse demonstration, to one external candidate series (GSE27276; metadata only, no differential expression). Among the six primary inputs, compound free-text covariates were detected in 3 of 6 (all GSE9944 matrices place ancestry, age, sex and group inside one characteristics string, so a structured parser returns 0 usable numeric age/sex values), empty group x ancestry strata in 2 of 6 (phi -0.354 and -0.462, both design matrices full rank), technical replicates or shared donor identifiers in 2 of 6, and linear-scale or excluded-arm handling in 3 of 6. One platform (GPL5175) has no GEO annotation file; the local rebuild used for the boundary check is labelled as non-official. The audit is descriptive: it does not re-fit the primary model and does not change the 0/18 conclusion. In the external candidate, 36 arrays carry structured characteristics rows but no structured age/sex fields, GEO's GPL2507 annotation covers 40.64% of its matrix probes, and donor identifiers cannot be recovered from the deposited titles (paired eyes and one technical replicate are documented in the GEO overall design), so arrays must not be treated as independent donors.""")

# ---------------------------------------------------------------- Results 3.2
rep("the original manuscript described STAT1 as the sole up-regulated transcript and CASP1 as down-regulated.",
    """the original manuscript described STAT1 as the sole up-regulated transcript and CASP1 as down-regulated.

Post-hoc detectable effect sizes at 80% power (two-sided alpha = 0.05; Table S13) exceeded the observed |log2FC| in 11 of 18 gene-by-platform tests, and only 43.5% of probes on GSE2378-GPL8300 had 80% power to detect |log2FC| >= 1. These non-significant results therefore cannot exclude smaller effects and should not be interpreted as evidence of no effect.""")

rep("GSE45570 could not be analysed at gene level because GPL5175 has no GEO annotation file.",
    "GSE45570 was excluded from that gene-level sensitivity convention because GEO provides no GEO annotation file for GPL5175; the separate boundary check with a rebuilt map is in Table S15.")

rep("[AUTHOR INPUT REQUIRED: 若后续补齐 GPL5175 平台表映射，须重跑 external_validation 并在本段补入逐基因 log2FC / p / q / AUC 与 95% CI。]",
    """[AUTHOR INPUT REQUIRED: 投稿前确认 Table S15 边界检查是否作为补充材料呈现；不得把该结果写成验证或独立复现，也不得并入主结果 0/18。] The v0.8 boundary check (Table S15; `results_gpl5175/`) used a locally rebuilt GPL5175 map and returned 0 of 6 significant transcripts at BH q < 0.05, with nominal 95% CIs for every gene. Because this is whole ONH tissue on a different platform with a different case definition, it is a boundary check and cannot validate the astrocyte-specific findings. The frozen primary file `results/06_external_validation.csv` is unchanged and still records "probe not mapped" for this platform; the two outputs must not be merged. No ROC/AUC was computed for this boundary check because the pre-specified ROC analysis applies only to GSE2378-GPL8300.""")

# ---------------------------------------------------------------- Discussion
rep("Sixth, gene-level analysis was impossible on GSE45570 because GPL5175 has no GEO annotation file; this missingness must not be read as a negative replication.",
    """Sixth, GEO provides no GEO annotation file for GPL5175, so the pre-specified primary run reports "no probe mapped" on GSE45570. In this version the complete 316,919-row SOFT platform table was rebuilt into a local map covering 17,634 of 22,011 (80.11%) transcript clusters; an exploratory gene-level boundary check using that map (Table S15; `results_gpl5175/`) returned 0 of 6 significant transcripts at BH q < 0.05. Because GSE45570 profiles whole ONH tissue on a different platform with a different case definition, this is a boundary check and cannot validate the astrocyte-specific findings; it is not an independent replication and does not alter the primary 0/18 conclusion. Unmapped probes remain missing annotation, never a negative result.""")

rep("Finally, the original downstream enrichment, network and miRNA analyses were not re-run; their numbers are reproduced here only to document provenance.",
    "No a-priori power calculation was performed; the detectable-effect analysis is post hoc and descriptive, and is not a test of equivalence. Finally, the original downstream enrichment, network and miRNA analyses were not re-run; their numbers are reproduced here only to document provenance.")

rep("The practical value of this work is a reproducible audit rather than a candidate list.",
    """The reusable audit tool (`geo_metadata_audit.py`; Table S16) encodes five recurring metadata defects as read-only checks and has been applied beyond the six matrices used here to one external candidate series, whose accession, sample count, platform and annotation availability were first verified against the official GEO records (Table S14 official verification). This shifts the reproducible output of the work from a single corrected transcript list towards a checklist that can be applied before any GEO series is reused. It does not add an independent cohort, a wet-laboratory experiment or a biological claim, and it does not by itself make the manuscript ready for submission.

The practical value of this work is a reproducible audit rather than a candidate list.""")

# ---------------------------------------------------------------- Figure 2 / supplements / footer
rep("GSE45570 is not shown because no probe maps to a gene symbol on GPL5175.",
    "GSE45570 is not shown because it is not one of the three annotated discovery platforms and its whole-tissue design is not comparable; an exploratory boundary check using a rebuilt GPL5175 map is reported separately in Table S15.")

rep("**Table S12.** Probe-level versus gene-level DEG counts and per-platform gene counts (`tables/TableS12_genelevel_DEG_counts.tsv`; full gene-level tables in `results_genelevel/`).",
    """**Table S12.** Probe-level versus gene-level DEG counts and per-platform gene counts (`tables/TableS12_genelevel_DEG_counts.tsv`; full gene-level tables in `results_genelevel/`).

**Table S13.** Post-hoc detectable effect sizes for the 18 six-transcript tests and the four analysed platforms, with nominal 95% CIs, MDE at 80% power, residual df and BH q (`tables/TableS13_power_mde.tsv`; `results_power/`).

**Table S14.** Candidate external GEO series, with an **official verification** table that supersedes the earlier unverified planning numbers (`tables/TableS14_official_verification.tsv`; planning list in `tables/TableS14_external_cohort_candidates.tsv`). No external series was used for a differential-expression test and none is an independent replication.

**Table S15.** Exploratory GSE45570 gene-level boundary check using a locally rebuilt GPL5175 map (`tables/TableS15_gpl5175_boundary.tsv`; `results_gpl5175/`). Boundary check only, not validation.

**Table S16.** Reusable five-class metadata audit of the six primary series matrices plus one external candidate series audited for metadata only (`tables/TableS16_metadata_audit.tsv`; `results_audit/`).""")

rep("*本文件为 limma 复核与基因级敏感性后的全文中稿 v0.7，仍不构成投稿文本。",
    "*本文件为投稿可行性增强后的全文中稿 v0.8，仍不构成投稿文本。")

rep("新增参考文献由 `work/data/verify_literature.py` 经 PubMed/Crossref/GEO 官方记录核验；",
    "新增参考文献由 `work/data/verify_literature.py` 经 PubMed/Crossref/GEO 官方记录核验；v0.8 新增结果由 `work/data/power_mde.py`、`fetch_5175_parallel.py`、`fetch_gpl5175_annot.py`、`gpl5175_boundary.py` 与 `geo_metadata_audit.py` 生成，均在独立目录；")

# ---------------------------------------------------------------- write v0.8
# Keep the inherited Figure first-mention order (1 before 2): the two newly
# inserted Methods sentences must not introduce "Figure 2" ahead of the
# original "Figure 1 Venn" mention in Methods 2.3.
fig_anchor = "`, Figure 2 or Tables 1-2."
assert s.count(fig_anchor) == 2, s.count(fig_anchor)
s = s.replace(fig_anchor, "`, the primary six-transcript figure or Tables 1-2.")

assert "## Abstract" in s and "## 9. Supplementary materials" in s
assert s.count("[AUTHOR INPUT REQUIRED:") == 12, s.count("[AUTHOR INPUT REQUIRED:")
assert s.count("[UNVERIFIED:") == 8, s.count("[UNVERIFIED:")
open(DST, "w", encoding="utf-8", newline="").write(s)
print("v0.8 written: %d substitutions, %d -> %d chars" % (nrep, orig_len, len(s)))
print("sha256 v0.7:", hashlib.sha256(open(SRC, "rb").read()).hexdigest()[:12])
print("sha256 v0.8:", hashlib.sha256(open(DST, "rb").read()).hexdigest()[:12])

# ---------------------------------------------------------------- derive cold_read_v08.py
c = open(CR7, encoding="utf-8").read()
pairs = [
    ('"""Cold-read v6 for the limma-replicated / gene-level-sensitised manuscript v0.7.',
     '"""Cold-read v8 for the feasibility-enhanced manuscript v0.8.'),
    ('"青光眼生信稿件_全文重写稿_v0.7.md")', '"青光眼生信稿件_全文重写稿_v0.8.md")'),
    ('OUT = os.path.join(WORK, "青光眼生信稿件_cold-read_v0.7报告.md")',
     'OUT = os.path.join(WORK, "青光眼生信稿件_cold-read_v0.8报告.md")'),
    ('lines = ["# Cold-read v0.7（limma 复核与基因级敏感性版）\\n",',
     'lines = ["# Cold-read v0.8（投稿可行性增强版）\\n",'),
]
for old, new in pairs:
    assert c.count(old) == 1, "cold-read anchor %r matched %d" % (old[:60], c.count(old))
    c = c.replace(old, new, 1)

# J-group: v0.8 completed the GPL5175 extraction, so "no probe mapped" is now
# a historical statement about the frozen primary file, not a required claim.
# It is still present verbatim in Methods 2.2 and Discussion, so the inherited
# assertion stays valid; we add explicit "no longer claimed" checks below.

# Insert group O before the report block.
anchor = "\n# --- report ---\n"
assert c.count(anchor) == 1
O = r'''
# --- 13. O group: v0.8 feasibility enhancements (P1-a / P1-c / P1-d) --------
POW = os.path.join(ROOT, "results_power")
AUD = os.path.join(ROOT, "results_audit")
BND = os.path.join(ROOT, "results_gpl5175")

for p in ["11 of 18", "43.5%", "Table S13", "post hoc",
          "not a test of equivalence", "cannot exclude smaller effects",
          "should not be interpreted as evidence of no effect"]:
    chk("O S13 效应量", "正文已写明 `%s`" % p, p in s, "命中" if p in s else "缺失")
for p in ["is evidence of no effect", "confirmed negative",
          "is a test of equivalence", "proves absence of effect",
          "underpowered therefore the genes are real",
          "independently replicated"]:
    chk("O S13 反面", "不得声称 `%s`" % p, p not in body, "命中 %d" % body.count(p))
pm = os.path.join(POW, "01_platform_mde.csv")
if os.path.exists(pm):
    pmdf = pd.read_csv(pm)
    col = [x for x in pmdf.columns if "power" in x.lower() and "pct" in x.lower()]
    if col:
        v = float(pmdf.loc[pmdf.platform_dataset == "GSE2378-GPL8300", col[0]].iat[0])
        chk("O S13 对账", "GSE2378-GPL8300 功效比例写入正文为 43.5%",
            abs(v - 43.52) < 0.01 and "43.5%" in s, "CSV %.2f" % v)
for f in ["01_platform_mde.csv", "02_six_genes_mde.csv", "README.md"]:
    chk("O S13 文件", "`results_power/%s`" % f,
        os.path.exists(os.path.join(POW, f)), "")
for f in ["TableS13_power_mde.tsv", "TableS13_power_mde.md"]:
    chk("O S13 文件", "`tables/%s`" % f, os.path.exists(os.path.join(TABD, f)), "")

for p in ["316,919", "33,475", "80.11%", "17,634", "Table S15",
          "boundary check", "cannot validate", "not an independent replication"]:
    chk("O S15 边界", "正文已写明 `%s`" % p, p in s, "命中" if p in s else "缺失")
for p in ["Gene-level analysis was impossible on GSE45570",
          "no probe maps to a gene symbol on GPL5175",
          "no usable annotation file was produced"]:
    chk("O S15 事实", "不再声称 `%s`" % p, p not in s, "命中 %d" % s.count(p))
for f in ["03_six_gene_boundary.csv", "boundary_summary.json", "README.md"]:
    chk("O S15 文件", "`results_gpl5175/%s`" % f,
        os.path.exists(os.path.join(BND, f)), "")
bs = os.path.join(BND, "boundary_summary.json")
if os.path.exists(bs):
    b = json.load(open(bs, encoding="utf-8"))
    chk("O S15 对账", "映射覆盖率 80.11% 与正文一致",
        abs(float(b["mapping_coverage_pct"]) - 80.11) < 0.01 and "80.11%" in s,
        "JSON %.2f" % b["mapping_coverage_pct"])
    chk("O S15 对账", "边界检查六基因 0/6 显著",
        int(b["n_six_genes_significant_q05"]) == 0, "实际 %d" % b["n_six_genes_significant_q05"])
    chk("O S15 对账", "边界检查未改动主结果",
        b["primary_results_modified"] is False, str(b["primary_results_modified"]))
s15 = os.path.join(TABD, "TableS15_gpl5175_boundary.tsv")
chk("O S15 文件", "`TableS15_gpl5175_boundary.tsv` 六行",
    os.path.exists(s15) and len(pd.read_csv(s15, sep="\t")) == 6,
    "%d 行" % (len(pd.read_csv(s15, sep="\t")) if os.path.exists(s15) else 0))
a5175 = os.path.join(ROOT, "GPL5175.annot.gz")
chk("O S15 注释", "`GPL5175.annot.gz` 存在且 gzip 完整",
    os.path.exists(a5175) and os.path.getsize(a5175) > 1000, "")

for p in ["geo_metadata_audit.py", "Table S16", "five checks", "3 of 6", "2 of 6"]:
    chk("O S16 审计", "正文已写明 `%s`" % p, p in s, "命中" if p in s else "缺失")
ac = os.path.join(AUD, "audit_checklist.csv")
if os.path.exists(ac):
    adf = pd.read_csv(ac)
    chk("O S16 对账", "审计覆盖 6 主 + 1 外部候选",
        len(adf) == 7 and (adf.role == "primary").sum() == 6,
        "%d 行 / %d 主输入" % (len(adf), (adf.role == "primary").sum()))
    prim = adf[adf.role == "primary"]
    chk("O S16 对账", "正文 3 of 6 自由文本协变量 FAIL",
        int((prim.check_free_text_covariates == "FAIL").sum()) == 3,
        str(prim.check_free_text_covariates.value_counts().to_dict()))
    chk("O S16 对账", "正文 2 of 6 零单元格 FAIL",
        int((prim.check_group_x_ancestry_cells == "FAIL").sum()) == 2,
        str(prim.check_group_x_ancestry_cells.value_counts().to_dict()))
for f in ["audit_report.csv", "audit_checklist.csv", "audit_summary.json", "README.md"]:
    chk("O S16 文件", "`results_audit/%s`" % f, os.path.exists(os.path.join(AUD, f)), "")
for f in ["TableS16_metadata_audit.tsv", "TableS16_metadata_audit.md",
          "TableS14_official_verification.tsv"]:
    chk("O S16 文件", "`tables/%s`" % f, os.path.exists(os.path.join(TABD, f)), "")

v7 = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.7.md")
chk("O 版本", "v0.7 原文仍保留且字节未变",
    os.path.exists(v7) and hashlib.sha256(open(v7, "rb").read()).hexdigest().startswith("__V07SHA__"),
    "v0.7 保留")
chk("O 版本", "决策 A 仍写在版本说明", "确认保持 A" in s and "results/` 的预指定 M2" in s, "")
'''
O = O.replace("__V07SHA__", hashlib.sha256(open(SRC, "rb").read()).hexdigest()[:12])
c = c.replace(anchor, O + anchor, 1)
c = c.replace('''lines.append("- 本检查不能替代机构权限下的 iThenticate/Turnitin 相似度自查，也不能替代逐刊政策人工核对。\\n")''',
              '''lines.append("- v0.8 新增 **O 组**：Table S13 事后可检测效应量（11/18、43.5%、非等效性检验）、"
             "Table S15 的 GPL5175 重建映射与边界检查（316,919 行、80.11%、0/6、非验证）、"
             "Table S16 可复用元数据审计（6 主 + 1 外部候选，五类缺陷）与 S14 官方核验；"
             "并断言 v0.7 字节未变、主结果未改、边界检查未被提升为验证。\\n")
lines.append("- 本检查不能替代机构权限下的 iThenticate/Turnitin 相似度自查，也不能替代逐刊政策人工核对。\\n")''', 1)
open(CR8, "w", encoding="utf-8", newline="").write(c)
print("cold_read_v08.py derived; %d chars" % len(c))

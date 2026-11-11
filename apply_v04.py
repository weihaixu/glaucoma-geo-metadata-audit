#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Derive manuscript v0.4 from v0.3 by exact, asserted replacements.

Every numeric table inserted here is rebuilt from work/data/tables/*.tsv, which
themselves come from results/*.csv. No number is typed by hand.
"""
import os
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
SRC = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.3.md")
DST = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.4.md")
TAB = os.path.join(ROOT, "tables")

s = open(SRC, encoding="utf-8").read()
reps = []


def rep(old, new, tag):
    assert old in s, "ANCHOR NOT FOUND: " + tag
    assert s.count(old) == 1, "ANCHOR NOT UNIQUE: " + tag
    reps.append((old, new, tag))


# ---------------------------------------------------------------- dynamic tables
deg = pd.read_csv(os.path.join(TAB, "Table1_DEG_by_model.tsv"), sep="\t")
order = ["GSE9944-GPL571", "GSE9944-GPL8300", "GSE2378-GPL8300", "GSE45570"]
lines = ["| Dataset | M0 | M1 | **M2 (primary)** | M3 | Probes tested | Residual df (M2) |",
         "|---|---:|---:|---:|---:|---:|---:|"]
for d in order:
    g = deg[deg.Dataset == d].set_index("Model")
    lines.append("| %s | %d | %d | **%d** | %d | %d | %d |" % (
        d, g.loc["M0_array_nominal", "DE probes"], g.loc["M1_donor_nominal", "DE probes"],
        g.loc["M2_donor_adjusted_FDR_LFC1", "DE probes"],
        g.loc["M3_donor_adjusted_FDR_LFC05", "DE probes"],
        g.loc["M2_donor_adjusted_FDR_LFC1", "Probes tested"],
        g.loc["M2_donor_adjusted_FDR_LFC1", "Residual df"]))
table1 = "\n".join(lines)

t2 = pd.read_csv(os.path.join(TAB, "Table2_six_genes_M2.tsv"), sep="\t")
lines = ["| Dataset | Gene | Probes (n) | log2FC [nominal 95% CI] | Nominal p | BH q | n G / n C |",
         "|---|---|---:|---|---:|---:|---:|"]
for _, r in t2.iterrows():
    lfc = "%+.3f" % float(r["log2FC"])
    lines.append("| %s | %s | %d | %s %s | %.4g | %.3f | %d / %d |" % (
        r["Dataset"], r["Gene"], int(r["All probes (n)"]), lfc, r["95% CI"],
        float(r["Nominal p"]), float(r["BH q"]),
        int(r["n glaucoma"]), int(r["n control"])))
table2 = "\n".join(lines)

# ---------------------------------------------------------------- 00 version note
rep("""## 00 · 版本说明（非论文正文，复制时从下一节开始）

本文件是 **v0.3 真实数据回填稿**，基于 `work/data/results/` 中 `reanalysis.py` 对 6 个 GEO series matrix 的真实重跑结果，以及 `facts_for_manuscript.md` 自动汇总的事实表。相较 v0.2：

1. **定位按决策树分支 A 改变**：六个原先被优先关注的转录本在主模型（供体级 + 协变量校正 + BH-FDR）中**全部 q ≥ 0.05**，因此不再称为候选基因（candidates），论文改定位为**方法学/数据质量重评估**，兼作假设生成的边界说明。
2. **三类统计类占位符（数据待补、计划待做、作者待确认）已全部清空**：统计数字来自真实结果表，原先计划的分析已执行并写入 Methods 2.8。
3. 原稿下游分析（DAVID / KOBAS / GenCLiP / miRNA 预测）**本轮未重跑**，其数字一律标 `[UNVERIFIED: ...]`，不得当作重跑结果引用。
4. 剩余占位符只属于**外部输入**：作者声明、文献重排、图 1–5 与表格原文件。原稿 docx 全程未修改。
5. 标题另备一版（若作者坚持保留假设生成定位）：*"A hypothesis-generating, donor-level re-analysis of public ONH astrocyte microarray data"*。本稿正文按方法学重评估版撰写。""",
"""## 00 · 版本说明（非论文正文，复制时从下一节开始）

本文件是 **v0.4 图表与事实一致性修订稿**。v0.3 的真实统计数字（`work/data/results/`）保持不变；本轮补齐图表、表格、效应量 CI 与可复现清单，并修正三处 v0.3 与结果表不一致的表述。

1. 定位仍为**决策树分支 A**：六个原先被优先关注的转录本在主模型（供体级 + 协变量校正 + BH-FDR）中**全部 q ≥ 0.05**，论文定位为**方法学/数据质量重评估**，兼作假设生成的边界说明。
2. **新增 Figure 1–2（PNG/SVG）与 Table 1–4、Table S1–S4**，全部由 `results/*.csv` 经 `make_figures_tables.py` 生成；Table 2 补入名义 95% CI、每组 n、全探针中位数，Table S1 给出全部 61 个映射探针的逐探针 CI。
3. **事实修订一**：主模型实际拟合的协变量只有 ancestry（`02_qc_summary.csv:adjustment_terms`）；v0.3 写成 "ancestry, age and sex" 与结果表不符，已改。自由文本年龄/性别在 `reanalysis_m2b.py` 中解析后另跑 M2b，结论不变（0/18），见 Results 3.2 与 Table S2–S3。
4. **事实修订二**：GPL5175 平台表映射**未完成**（官方无 annot 文件），v0.3 Methods 2.2 把未完成的步骤写成已完成，已改为如实说明；GSE45570 六基因保持 `probe not mapped`，不得写成阴性验证。
5. **事实修订三**：`08_sensitivity.csv` 只是 `03_deg_by_model.csv` 的副本，网格未导出；本轮从 `04_deg_primary_M2.csv` 重算真实 alpha × |log2FC| × FDR 网格（Table S4），Methods 2.5 的敏感性描述现有据可依。
6. 原稿下游分析（DAVID / KOBAS / GenCLiP / miRNA 预测）**未重跑**，其数字一律标 `[UNVERIFIED: ...]`，不得当作重跑结果引用。剩余占位符只属于**外部输入**：作者声明、代码公开 DOI、文献重排。原稿 docx 全程未修改。
7. 标题另备一版（若作者坚持保留假设生成定位）：*"A hypothesis-generating, donor-level re-analysis of public ONH astrocyte microarray data"*。本稿正文按方法学重评估版撰写。""", "00 version note")

# ---------------------------------------------------------------- Abstract
rep("M1 (donor-level, nominal), M2 (donor-level with ancestry, age and sex covariates, Benjamini–Hochberg q < 0.05, |log2FC| ≥ 1; primary)",
    "M1 (donor-level, nominal), M2 (donor-level with ancestry where the deposited metadata permitted it, Benjamini–Hochberg q < 0.05, |log2FC| ≥ 1; primary)",
    "abstract M2 covariates")
rep("Platform-specific GEO annotations mapped probes to gene symbols; ROC analysis used bootstrap confidence intervals and label permutation.",
    "Platform-specific GEO annotations mapped probes to gene symbols; ROC analysis used bootstrap confidence intervals and label permutation. Numeric age and sex were not usable in the primary run and were evaluated separately in a covariate-complete sensitivity model (M2b).",
    "abstract covariate caveat")
rep("Moreover, the direction of effect was opposite to that reported in the original manuscript: STAT1 was lower and CASP1 higher in glaucomatous samples.\n\n**Conclusions:**",
    "Moreover, the direction of effect was opposite to that reported in the original manuscript: STAT1 was lower and CASP1 higher in glaucomatous samples. In the covariate-complete sensitivity model (M2b), no transcript was significant either (0 of 18 tests; q = 0.077–0.893), and the GSE9944-GPL571 M2 count fell from 114 to 95.\n\n**Conclusions:**",
    "abstract M2b")

# ---------------------------------------------------------------- Methods 2.2
rep("""Probes were mapped to gene symbols with the platform-specific GEO annotation files GPL8300.annot.gz, GPL571.annot.gz and GPL91.annot.gz. GEO provides no `GPL5175.annot.gz`; its platform table was therefore extracted from the beginning of the GPL5175 family SOFT archive and converted to the same two-column format. Where a gene was represented by multiple probes, the probe with the smallest nominal p value was reported; this is an optimistic selection and is listed as a limitation. Six probes could not be assigned a symbol on platforms without a usable annotation file and were reported as "no probe mapped" rather than silently dropped.""",
"""Probes were mapped to gene symbols with the platform-specific GEO annotation files GPL8300.annot.gz, GPL571.annot.gz and GPL91.annot.gz. GEO provides no `GPL5175.annot.gz`. An attempt was made to extract the GPL5175 platform table from the beginning of the 4.5 GB GPL5175 family SOFT archive, but this extraction was **not completed** and no usable annotation file was produced; consequently 0 of 22,011 GSE45570 probes carry a gene symbol. The six transcripts are therefore reported as "no probe mapped" on GSE45570 rather than as negative or non-replicated findings. Where a gene was represented by multiple probes, the probe with the smallest nominal p value was reported in the main text; this is an optimistic selection, and all mapped probes with nominal 95% confidence intervals are supplied in Table S1 and `tables/TableS1_all_probes_six_genes.tsv`.""",
    "methods 2.2 annotation")

# ---------------------------------------------------------------- Methods 2.5
rep("""Technical replicate arrays were collapsed by averaging within a donor identifier parsed from the GEO sample title (`rep1/rep2` pairs). For each platform separately, ordinary least squares was fitted probe-wise with a design matrix containing an intercept, an indicator for glaucoma, and — where the deposited metadata supported it — ancestry (Caucasian as reference), mean-centred age and sex. Rank-deficient designs were rejected rather than fitted. Age and sex were included only when ≥80% of donors had usable values; GSE2378 and GSE45570 had no ancestry field, so their adjusted models were explicitly marked `ADJUSTMENT NOT POSSIBLE` and the corresponding M2/M3 rows are donor-level FDR results without ancestry adjustment.""",
"""Technical replicate arrays were collapsed by averaging within a donor identifier parsed from the GEO sample title (`rep1/rep2` pairs). For each platform separately, ordinary least squares was fitted probe-wise with a design matrix containing an intercept, an indicator for glaucoma and — on the two GSE9944 platforms with a usable ancestry field — a Caucasian-reference ancestry indicator. Rank-deficient designs were rejected rather than fitted. **Numeric age and sex did not enter any model in the primary run**: GSE9944 deposits ancestry, age and sex inside a single free-text characteristics string, the structured-field parser returned 0 of 96 usable numeric values, and the pre-specified ≥80% completeness rule therefore excluded both terms. The fitted M2 design on GSE9944-GPL571 and -GPL8300 was `intercept + glaucoma + ancestry` (residual df 18 and 13); the terms actually fitted are recorded in `02_qc_summary.csv:adjustment_terms`. GSE2378 and GSE45570 have no ancestry field, so the covariate-adjusted design was rejected and the corresponding M2/M3 rows are donor-level, unadjusted fits with BH correction and the pre-specified fold-change threshold, explicitly marked `ADJUSTMENT NOT POSSIBLE`. A covariate-complete sensitivity run (M2b), in which age and sex are parsed from the free text, is reported in Results 3.2 and Tables S2–S3.""",
    "methods 2.5 design")
rep("| **M2 (primary)** | **donor** | **ancestry, age, sex where available** | **BH q < 0.05, |log2FC| ≥ 1** |",
    "| **M2 (primary)** | **donor** | **ancestry where available; M2b adds age and sex** | **BH q < 0.05, |log2FC| ≥ 1** |",
    "methods 2.5 table")
rep("Benjamini–Hochberg correction was applied across all tested probes on a platform. Sensitivity analyses varied alpha (0.05, 0.01), |log2FC| (0.5, 1.0, 1.5) and whether FDR was applied.",
    "Benjamini–Hochberg correction was applied across all tested probes on a platform. Sensitivity analyses varied alpha (0.05, 0.01), |log2FC| (0.5, 1.0, 1.5) and whether FDR was applied; the full grid was recomputed from the probe-level M2 table and is given in Table S4 (`tables/TableS4_sensitivity_grid.tsv`).",
    "methods 2.5 sensitivity")

# ---------------------------------------------------------------- Methods 2.6
rep("Scripts, input manifests and all output tables are provided as supplementary code (`work/data/reanalysis.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, `summarize_results.py`, `cold_read_v03.py`).",
    "Scripts, input manifests, figures and all output tables are provided as supplementary code (`work/data/reanalysis.py`, `reanalysis_m2b.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, `summarize_results.py`, `make_figures_tables.py`, `cold_read_v04.py`). Exact commands, environment versions and limitations are in `REPRODUCIBILITY.md`; SHA-256 checksums and byte sizes for every input, script and result file are in `tables/file_manifest.csv`.",
    "methods 2.6 reproducibility")

# ---------------------------------------------------------------- Results 3.1 / Table 1
rep("""**Table 1.** DEG counts by model and platform (new; generated from `03_deg_by_model.csv`). `[AUTHOR INPUT REQUIRED: 把 `results/03_deg_by_model.csv` 排成期刊表格，补残差自由度列。]`""",
    table1 + """

**Table 1.** Differentially expressed probes by model and platform, generated from `results/03_deg_by_model.csv` (full version with residual df, probes tested and adjustment status: `tables/Table1_DEG_by_model.tsv`). M2/M3 on GSE2378-GPL8300 and GSE45570 are donor-level BH results **without** ancestry adjustment because the covariate-adjusted design was rejected; the primary M2 design on the two GSE9944 platforms contains ancestry only. Counts are shown for all four analysable platforms; the two GPL91 subsets (two donors each) were not modelled.""",
    "results 3.1 table 1")

# ---------------------------------------------------------------- Results 3.2 / Table 2
old_table2 = """| Gene | GSE2378-GPL8300 log2FC | p | BH q | GSE9944-GPL8300 log2FC | p | BH q |
|---|---|---|---|---|---|---|
| FGFR1 | +0.729 | 0.0084 | 0.354 | +0.440 | 0.0313 | 0.576 |
| SMAD1 | +0.845 | 0.0031 | 0.290 | +0.458 | 0.0612 | 0.679 |
| STAT1 | −0.821 | 0.0143 | 0.433 | −0.968 | 0.0054 | 0.428 |
| TGFBR2 | +0.603 | 0.0009 | 0.227 | +0.484 | 0.0696 | 0.691 |
| CASP1 | +1.921 | 0.0007 | 0.224 | +0.467 | 0.0024 | 0.356 |
| CASP4 | +0.784 | 0.0031 | 0.290 | +0.740 | 0.0228 | 0.543 |

**Table 2.** Six originally prioritized transcripts in the primary M2 model. Values are per platform, probe with smallest nominal p per gene. `[AUTHOR INPUT REQUIRED: 补 95% CI、每组 n、多探针全部结果（不得只报最优探针）；见 `results/05_six_key_genes.csv`、`04_deg_primary_M2.csv`。]`"""
rep(old_table2,
    table2 + """

**Table 2.** Six originally prioritized transcripts in the primary M2 model across the three annotated discovery platforms. Values are for the probe with the smallest nominal p within each gene; **95% CIs are nominal and not multiplicity-adjusted**. Median effects over all mapped probes, residual df, probe identifiers and the complete per-probe table (61 probes) are given in `tables/Table2_six_genes_M2.tsv` and Table S1 (`tables/TableS1_all_probes_six_genes.tsv`). No gene-by-platform test reaches BH q < 0.05.""",
    "results 3.2 table 2")

rep("In the whole-tissue comparison (GSE45570, 6 POAG versus 6 control)",
    """Because the primary M2 design did not contain age or sex, we repeated the full hierarchy in a covariate-complete sensitivity run (M2b) after parsing age and sex from the free-text GEO descriptions. On GSE9944-GPL571 and -GPL8300 the fitted terms became `intercept, glaucoma, race_Caucasian, age_z, sex`. The M2 DEG count on GSE9944-GPL571 changed from 114 to 95 (M3: 640 to 516), the other three platforms were unchanged, and none of the six transcripts reached BH q < 0.05 in any of the 18 tests (q = 0.077–0.893). STAT1 remained lower and CASP1 higher in glaucomatous samples. Whether to promote M2b to the primary model is an author decision; either specification supports the same conclusion. Full comparisons are in Tables S2–S3.

In the whole-tissue comparison (GSE45570, 6 POAG versus 6 control)""",
    "results 3.2 M2b")

# ---------------------------------------------------------------- Results 3.3
rep("Gene–pathway and miRNA–mRNA networks were constructed in Cytoscape 3.8.0 (Figure 3–5).",
    "Gene–pathway and miRNA–mRNA networks were constructed in Cytoscape 3.8.0 (three network figures in the original report).",
    "results 3.3 figure refs")

# ---------------------------------------------------------------- Declarations
rep("Platform annotations GPL8300, GPL571 and GPL91 were obtained from the corresponding GEO platform records; the GPL5175 platform table was extracted from the GPL5175 family SOFT archive. `results/` contains all derived tables.",
    "Platform annotations GPL8300, GPL571 and GPL91 were obtained from the corresponding GEO platform records; GEO provides no GPL5175 annotation and the family-SOFT extraction was not completed, so GSE45570 has no gene-symbol mapping. `results/`, `results_m2b/`, `figures/`, `tables/` and `tables/file_manifest.csv` (SHA-256 checksums) contain all derived files.",
    "declarations data")
rep("**Code availability:** Analysis scripts are supplied as supplementary code (`reanalysis.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, `summarize_results.py`, `cold_read_v03.py`) with a run manifest in `README.md`.",
    "**Code availability:** Analysis scripts are supplied as supplementary code (`reanalysis.py`, `reanalysis_m2b.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, `summarize_results.py`, `make_figures_tables.py`, `cold_read_v04.py`) with a run manifest in `README.md`, exact commands and environment versions in `REPRODUCIBILITY.md`, and a checksummed file list in `tables/file_manifest.csv`.",
    "declarations code")

# ---------------------------------------------------------------- Section 8
rep("""**Figure 1.** Reconstructed array-to-donor structure of the three GEO series and DEG counts across the four models. A, number of arrays and independent donors per platform; B, DEG counts for M0/M1/M2/M3; C, ancestry × disease cross-tabulation for GSE9944-GPL571 and -GPL8300. `[AUTHOR INPUT REQUIRED: 用 `results/01_sample_metadata.csv`、`02_qc_summary.csv`、`03_deg_by_model.csv` 重绘；原稿 Figure 1 Venn 图不再适用于本稿。]`

**Figure 2.** Expression of the six originally prioritized transcripts. A, GSE2378-GPL8300 (7 glaucoma versus 6 control donors); B, GSE9944-GPL8300 (10 versus 6 donors); C, GSE45570 POAG versus control (6 versus 6). Display donor-level values, log2FC from M2, nominal p and BH q; significance annotation must use q < 0.05. `[AUTHOR INPUT REQUIRED: 用 `results/05_six_key_genes.csv` 与表达矩阵重绘；原稿 Figure 2 的 CK 标注与 up/down 方向均与重跑结果不符，不得沿用。]`

**Figure 3.** Gene-function clustering reported in the original manuscript (GenCLiP 3). `[UNVERIFIED: 原稿图，未重跑；建议删除。]`

**Figure 4.** Gene–pathway network reported in the original manuscript. `[UNVERIFIED: 原稿图，未重跑；建议删除。]`

**Figure 5.** Predicted miRNA–mRNA network reported in the original manuscript; all interactions are computational predictions. `[UNVERIFIED: 原稿图，未重跑；建议删除。]`""",
"""**Figure 1.** Reconstructed array-to-donor structure and model hierarchy, generated from `results/01_sample_metadata.csv`, `02_qc_summary.csv` and `03_deg_by_model.csv` (files: `figures/Figure1.png`, `Figure1.svg`). A, arrays deposited in each series matrix (96 in total) versus independent donors entering the models (66 donor-platform records); GSE45570 contributes 18 arrays of which 12 are used after excluding six OHT eyes. B, numbers of differentially expressed probes for M0–M3 on the four analysable platforms: 1375 / 1075 / 114 / 640, 472 / 337 / 0 / 0, 748 / 748 / 1 / 2 and 89 / 89 / 0 / 0. Red zeros mark the two platforms with no M2 calls. C, ancestry × disease cross-tabulation for GSE9944-GPL571 and -GPL8300; on GPL571 all three glaucoma donors are African American and all nine Caucasian donors are controls. The original Venn figure is not applicable to this re-analysis.

**Figure 2.** Six originally prioritized transcripts in the primary M2 model, generated from `results/05_six_key_genes.csv` and `04_deg_primary_M2.csv` (files: `figures/Figure2.png`, `Figure2.svg`). A, log2FC and BH q for six transcripts × three annotated discovery platforms; 0 of 18 tests reach q < 0.05. B, nominal p (open circles) versus BH q (filled squares) for all 18 tests on a log scale; the dashed line marks q = 0.05 and the shaded p < 0.05 zone contains no BH q value. C, forest plot of all 23 probes mapped to the six transcripts on GSE9944-GPL571 with nominal 95% CIs; probes within one gene are not independent and the intervals are not multiplicity-adjusted. GSE45570 is not shown because no probe maps to a gene symbol on GPL5175.""",
    "section 8 legends")

# ---------------------------------------------------------------- Section 9
rep("""**Table S1.** Complete M2 results for all probes on every platform (`results/04_deg_primary_M2.csv`).

**Table S2.** Six originally prioritized transcripts across all four models (`results/05_six_key_genes.csv`).

**Table S3.** Donor overlap across platforms and series (`results/10_donor_overlap.csv`; `01_sample_metadata.csv`).

**Table S4.** External comparison and ROC/AUC with bootstrap CI and permutation p (`results/06_external_validation.csv`, `07_roc.csv`).

**Table S5.** Sensitivity grid (`results/08_sensitivity.csv`) and QC/scale decisions (`02_qc_summary.csv`).

**Table S6.** `[UNVERIFIED: 原稿 Table 1、Table 2、Table S1–S3（GO/KEGG/KOBAS 术语与 miRNA 清单）未随本稿重跑；若保留须明确标注为原稿结果。]`

`[AUTHOR INPUT REQUIRED: 原 docx 中 Figure 1–5 与全部表格文件均缺失；投稿前须按第 8 节重绘图 1–2 并补齐 Table 1–2。]`""",
"""**Table S1.** All 61 probes mapped to the six transcripts on the three annotated discovery platforms, with log2FC, SE, nominal 95% CI, nominal p, BH q and residual df (`tables/TableS1_all_probes_six_genes.tsv`).

**Table S2.** Primary M2 versus covariate-complete M2b DEG counts (`tables/TableS2_M2_vs_M2b_DEG_counts.tsv`).

**Table S3.** Primary M2 versus M2b statistics for the six transcripts (`tables/TableS3_M2_vs_M2b_six_genes.tsv`).

**Table S4.** Alpha × |log2FC| × FDR sensitivity grid recomputed from `results/04_deg_primary_M2.csv` (`tables/TableS4_sensitivity_grid.tsv`). Note that `results/08_sensitivity.csv` is a copy of `03_deg_by_model.csv` and does not contain the grid.

**Table S5.** Complete M2 results for all probes on every platform (`results/04_deg_primary_M2.csv`); six transcripts across all four models (`results/05_six_key_genes.csv`); donor overlap (`results/10_donor_overlap.csv`); external comparison and ROC/AUC (`results/06_external_validation.csv`, `07_roc.csv`); QC/scale decisions (`02_qc_summary.csv`).

**Table S6.** `[UNVERIFIED: 原稿 Table 1、Table 2、Table S1–S3（GO/KEGG/KOBAS 术语与 miRNA 清单）未随本稿重跑；若保留须明确标注为原稿结果。]`

Figure 1–2 and Table 1–4 are now supplied as editable SVG/TSV files under `work/data/figures/` and `work/data/tables/`, with SHA-256 checksums in `tables/file_manifest.csv`. `[AUTHOR INPUT REQUIRED: 按目标期刊版式把 TSV 转成投稿表格、把 SVG 转成期刊要求的图形格式，并把 Figure 3–5 相关段落整体删除。]`""",
    "section 9 supplementary")

# ---------------------------------------------------------------- footer
rep("*本文件为真实数据回填后的全文中稿 v0.3，仍不构成投稿文本。所有统计数字来自 `work/data/results/`；标注 `[UNVERIFIED]` 的数字来自原稿、未经本轮重跑。原稿 `D:\\BaiduSyncdisk\\待研究相关资料\\青光眼生信研究\\Manuscript.docx` 未被修改。*",
    "*本文件为图表与事实一致性修订后的全文中稿 v0.4，仍不构成投稿文本。所有统计数字来自 `work/data/results/` 与 `work/data/results_m2b/`；图表与表格由 `work/data/make_figures_tables.py` 从结果表生成；标注 `[UNVERIFIED]` 的数字来自原稿、未经重跑。原稿 `D:\\BaiduSyncdisk\\待研究相关资料\\青光眼生信研究\\Manuscript.docx` 未被修改。*",
    "footer")

for old, new, tag in reps:
    s = s.replace(old, new, 1)
open(DST, "w", encoding="utf-8").write(s)
print("replacements applied: %d" % len(reps))
print("output:", DST, len(s), "chars")

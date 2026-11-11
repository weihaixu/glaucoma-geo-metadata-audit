# -*- coding: utf-8 -*-
"""Derive manuscript v0.7 from v0.6.

All changes are textual. Primary numbers (results/, Figure 1-2, Table 1-4,
Table S1-S8), the 58 references and decision A are unchanged. Round 9 adds
two independent robustness analyses:
  * real R/limma 3.52.4 empirical-Bayes replication (results_limma/, S9-S10);
  * gene-level sensitivity under three conventions (results_genelevel/, S11-S12).
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
SRC = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.6.md")
DST = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.7.md")

s = open(SRC, encoding="utf-8").read()


def must(old, new):
    global s
    n = s.count(old)
    assert n == 1, "expected exactly 1 match, got %d for: %r" % (n, old[:120])
    s = s.replace(old, new, 1)


# ------------------------------------------------------------- 00 version note
must("本文件是 **v0.6 决策落定与 N1 整改稿**。v0.5 的全部真实统计数字（`work/data/results/`、`results_m2b/`）、Figure 1–2、Table 1–4 与 Table S1–S6 均保持不变；本轮只落定主模型决策、重算供体级 ROC 诊断并据实修订表述，未改动任何主结果数值、图表或模型。",
     "本文件是 **v0.7 limma 复核与基因级敏感性稿**。v0.6 的全部真实统计数字（`work/data/results/`、`results_m2b/`、`results_diagnostics/`）、Figure 1–2、Table 1–4 与 Table S1–S8 均保持不变；本轮新增两套独立稳健性复核（R/limma 经验贝叶斯方差收缩、基因级三口径检验），输出在独立目录，未改动任何主结果数值、图表或模型。")

must("（African-American 对照 = 0）。诊断输出在独立的 `results_diagnostics/`，不覆盖 `results/`。",
     "（African-American 对照 = 0）。诊断输出在独立的 `results_diagnostics/`，不覆盖 `results/`。\n"
     "11. **limma 复核已真实执行**：本机 R 4.2.0 装 limma 3.52.4（Bioconductor 3.15 Windows 二进制包，项目内 `Rlib/`，不污染用户库）。用与主 M2 完全相同的供体级 log2 矩阵和设计矩阵跑 `lmFit → eBayes → topTable`；导出前重建的 Python OLS 与主结果 69,513 行 log2FC/se 最大误差 4.4e-16，limma logFC 与 OLS 系数最大误差 3.3e-14。六基因 **0/18 仍不显著**（limma q = 0.116–0.663）；DEG 数在 GPL571 由 114 增至 128（M2）/ 640 增至 709（M3），GPL8300 由 0 增至 2，属敏感性结果，**不回写主表**。输出在独立 `results_limma/`，见 Table S9–S10。\n"
     "12. **基因级敏感性**：把\"最小 p 选探针\"换成三口径（主口径 / 基因内全探针按供体中位数表达重跑 OLS / 探针 p 的 Simes 合并），三个有注释平台上 **每种口径均 0/18 显著**（BH q 最小 0.128）；GSE45570 因 GPL5175 无 GEO 注释文件**无法做基因级检验**，如实标为缺失而非阴性结果。输出在独立 `results_genelevel/`，见 Table S11–S12。决策分支 A 在两套复核下均不变。")

# ------------------------------------------------------------------- Abstract
must("Numeric age and sex were not usable in the primary run and were evaluated separately in a covariate-complete sensitivity model (M2b).",
     "Numeric age and sex were not usable in the primary run and were evaluated separately in a covariate-complete sensitivity model (M2b). Robustness was additionally assessed with limma empirical-Bayes moderation and with three gene-level testing conventions, all on the same donor-level matrices.")

must("and the GSE9944-GPL571 M2 count fell from 114 to 95.",
     "and the GSE9944-GPL571 M2 count fell from 114 to 95. An independent limma replication (0/18 tests significant; BH q = 0.116–0.663) and three gene-level conventions (0/18 in each) left the conclusion unchanged.")

# ------------------------------------------------------------ Methods 2.5 / 2.6
must("none of these estimates is used for inference or can establish diagnostic performance.",
     "none of these estimates is used for inference or can establish diagnostic performance.\n\n"
     "Two robustness analyses addressed the statistical engine and the unit of testing. First, the primary M2 design matrix and the donor-level log2 expression matrix of each of the four analysed platforms were exported unchanged to R 4.2.0 and refitted with limma 3.52.4 [35] (`lmFit` with `method=\"ls\"`, `eBayes` with `trend=FALSE, robust=FALSE`, `topTable` with BH adjustment). A reconstructed Python OLS reproduced the primary coefficients and standard errors to within 4.4e-16 before export, and limma logFC values matched the OLS coefficients to within 3.3e-14 across all 69,513 probe-by-platform tests (Table S10). Empirical-Bayes prior degrees of freedom estimated by `eBayes` were 2.25–4.58, giving moderated-test total df of 13.28–20.25. Second, to remove smallest-p probe selection, all probes mapping to one gene were collapsed to their per-donor median log2 expression and the model was refitted with BH correction across genes; Simes combination of the probe-level M2 p values within each gene was computed as an additional gene-level convention (Tables S11–S12). Gene-level analysis was impossible on GSE45570 because GPL5175 has no GEO annotation file; this is reported as missing annotation, never as a negative result. Simes assumes independence or positive dependence among the combined tests and is therefore exploratory, because probes for one gene are correlated.")

must("The pipeline is a probe-wise OLS with BH correction and does not use empirical-Bayes variance moderation (limma) [35]; it is therefore more conservative at small sample sizes.",
     "The primary pipeline is a probe-wise OLS with BH correction; it was additionally replicated with empirical-Bayes variance moderation (limma 3.52.4 [35]) in R 4.2.0 as a sensitivity analysis (Tables S9–S10), while the pre-specified primary results remain the OLS fit.")

old_scripts = "`work/data/reanalysis.py`, `reanalysis_m2b.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, `summarize_results.py`, `make_figures_tables.py`, `diagnose_n1.py`, `cold_read_v06.py`, `verify_literature.py`, `apply_v06.py`"
new_scripts = "`work/data/reanalysis.py`, `reanalysis_m2b.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, `summarize_results.py`, `make_figures_tables.py`, `diagnose_n1.py`, `verify_literature.py`, `install_r_packages.py`, `setup_rlib.R`, `limma_replication.R`, `run_limma_replication.py`, `genelevel_sensitivity.py`, `cold_read_v07.py`, `apply_v07.py`"
must(old_scripts, new_scripts)
must(old_scripts.replace("`work/data/reanalysis.py`", "`reanalysis.py`"),
     new_scripts.replace("`work/data/reanalysis.py`", "`reanalysis.py`"))

# --------------------------------------------------------------------- Results
must("No gene-by-platform test reaches BH q < 0.05.",
     "No gene-by-platform test reaches BH q < 0.05; the same holds under limma moderation and under gene-level aggregation (Tables S9–S12).")

must("Full comparisons are in Tables S2–S3.",
     "Full comparisons are in Tables S2–S3.\n\n"
     "**3.3 Robustness to the statistical engine and to gene-level aggregation.** Replacing the OLS engine with limma empirical-Bayes moderation on the identical matrices left all 18 six-gene tests non-significant (BH q = 0.116–0.663; Table S9). Engine-dependent DEG counts did change: on GSE9944-GPL571 the M2 count rose from 114 to 128 and the M3 count from 640 to 709, and on GSE9944-GPL8300 from 0 to 2, whereas GSE2378-GPL8300 (1) and GSE45570 (0) were unchanged (Table S10). Because the primary model was pre-specified as the OLS fit, these counts are reported as sensitivity results and are not substituted into Table 1. Collapsing probes to genes (9,084 / 13,101 / 9,068 genes on the three annotated platforms) and re-fitting the same design gave 2, 34 and 0 genes meeting the M2 threshold; all three gene-level conventions — smallest-p probe, per-donor median expression, and Simes combination — returned 0 of 18 significant results for the six transcripts, with minimum BH q of 0.128 (median-expression convention) and 0.219 (Simes; Table S11). GSE45570 could not be analysed at gene level because GPL5175 has no GEO annotation file. These checks do not rescue the transcript list; they show that the negative result is not an artefact of the OLS engine or of choosing one probe per gene.")

# ------------------------------------------------------------------ Discussion
must("The appropriate conclusion is therefore a methodological one, not a biological one.",
     "The appropriate conclusion is therefore a methodological one, not a biological one. This conclusion was unchanged when the statistical engine was replaced by limma's empirical-Bayes moderation and when probe selection was removed by gene-level aggregation.")

must("Fourth, probe-wise OLS with BH correction lacks empirical-Bayes variance moderation and is conservative in small samples; a limma-based replication with the same design matrix is desirable. Fifth, where several probes mapped to one gene, the smallest p value was reported, which is optimistic; the complete per-probe results are supplied in the supplementary tables and the resulting inflation in apparent ROC discrimination is quantified in Table S7. Sixth, the whole-tissue comparison used a different tissue, platform and case definition and provides no confirmatory evidence. Seventh, no functional or wet-laboratory validation was performed.",
     "Fourth, a limma replication confirmed the six-gene conclusion but increased the number of BH-significant probe-level calls on GSE9944-GPL571 from 114 to 128 (M2) and on -GPL8300 from 0 to 2; the pre-specified OLS fit is retained as primary, so these engine-dependent counts are reported as sensitivity results rather than substituted into the main tables. Fifth, where several probes mapped to one gene the smallest p value was reported, which is optimistic; gene-level aggregation and Simes combination both left all 18 tests non-significant, but Simes is exploratory because probes within a gene are correlated. Sixth, gene-level analysis was impossible on GSE45570 because GPL5175 has no GEO annotation file; this missingness must not be read as a negative replication. Seventh, the whole-tissue comparison used a different tissue, platform and case definition and provides no confirmatory evidence. Eighth, no functional or wet-laboratory validation was performed.")

# ------------------------------------------------------------ Supplementary list
must("**Table S8.** Quantitative ancestry × disease diagnostics for all six platforms: design terms and rank, condition number, VIF, phi coefficient, Pearson r, smallest cell and zero-cell flag (`tables/TableS8_collinearity_diagnostics.tsv`).",
     "**Table S8.** Quantitative ancestry × disease diagnostics for all six platforms: design terms and rank, condition number, VIF, phi coefficient, Pearson r, smallest cell and zero-cell flag (`tables/TableS8_collinearity_diagnostics.tsv`).\n\n"
     "**Table S9.** limma 3.52.4 versus primary OLS for the six transcripts under the identical probe-selection convention (18 rows; `tables/TableS9_limma_vs_OLS_six_genes.tsv`). Per-probe reconciliation for all 69,513 tests is in `results_limma/01_probe_reconciliation.csv`.\n\n"
     "**Table S10.** limma prior/total degrees of freedom and probe-level DEG counts under both engines at the M2 and M3 thresholds (`tables/TableS10_limma_DEG_counts.tsv`; `results_limma/03_dataset_summary.csv`, `session_info.txt`).\n\n"
     "**Table S11.** BH q for the six transcripts under three testing conventions on the three annotated platforms (`tables/TableS11_genelevel_six_genes_q.tsv`).\n\n"
     "**Table S12.** Probe-level versus gene-level DEG counts and per-platform gene counts (`tables/TableS12_genelevel_DEG_counts.tsv`; full gene-level tables in `results_genelevel/`).")

# --------------------------------------------------------------------- footnote
must("*本文件为决策落定与 N1 整改后的全文中稿 v0.6，仍不构成投稿文本。",
     "*本文件为 limma 复核与基因级敏感性后的全文中稿 v0.7，仍不构成投稿文本。")
must("图表与表格由 `work/data/make_figures_tables.py`、`work/data/diagnose_n1.py` 从结果表生成；",
     "图表与表格由 `work/data/make_figures_tables.py`、`work/data/diagnose_n1.py`、`work/data/run_limma_replication.py` 与 `work/data/genelevel_sensitivity.py` 从结果表生成；")

open(DST, "w", encoding="utf-8").write(s)
print("wrote", os.path.basename(DST), "bytes", len(s.encode("utf-8")), "words", len(s.split()))
for bad in ["does not use empirical-Bayes", "a limma-based replication with the same design matrix is desirable",
            "cold_read_v06.py", "apply_v06.py", "v0.6 决策落定", "Table S1–S6"]:
    print("residual %-62s : %d" % (bad, s.count(bad)))

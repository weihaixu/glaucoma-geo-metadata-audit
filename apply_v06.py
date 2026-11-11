# -*- coding: utf-8 -*-
"""Derive manuscript v0.6 from v0.5.

Changes (all textual; NO primary number is changed):
  1. Author decision CONFIRMED: primary model stays A (results/, pre-specified
     M2); results_m2b/ remains a sensitivity run. Removes all "pending"
     wording about that decision.
  2. N1 rectification: donor-level ROC recomputation (diagnose_n1.py) showed
     zero numerical change (one array per donor on GSE2378-GPL8300), so the
     ROC wording is corrected to explain the real weakness: circular probe
     selection, with quantified inflation in Table S7.
  3. Ancestry x disease wording tightened: VIF/phi/condition number show the
     problem is a structural zero cell, not classical multicollinearity.
     Adds the GPL8300 zero cell that the qualitative QC check missed.
  4. Adds Table S7/S8, updates the script lists and the version footnote.
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
SRC = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.5.md")
DST = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.6.md")

s = open(SRC, encoding="utf-8").read()


def must(old, new):
    global s
    n = s.count(old)
    assert n == 1, "expected exactly 1 match, got %d for: %r" % (n, old[:110])
    s = s.replace(old, new, 1)


# ---------------------------------------------------------------- 00 version note
must("本文件是 **v0.5 文献与声明修订稿**。v0.4 的全部真实统计数字（`work/data/results/`、`results_m2b/`）、Figure 1–2、Table 1–4 与 Table S1–S4 均保持不变；本轮只处理参考文献与投稿声明，未改动任何结果数值、图表或模型。",
     "本文件是 **v0.6 决策落定与 N1 整改稿**。v0.5 的全部真实统计数字（`work/data/results/`、`results_m2b/`）、Figure 1–2、Table 1–4 与 Table S1–S6 均保持不变；本轮只落定主模型决策、重算供体级 ROC 诊断并据实修订表述，未改动任何主结果数值、图表或模型。")

must("7. **M2b 是否升为主模型仍待作者决策**：本版沿用 `results/` 为主结果（GPL571 M2 = 114 个 DEG，q = 0.145–0.691）；若改以 `results_m2b/` 为主，需同步更新 Abstract、Results 3.1/3.2、Figure 1B、Table 1–2 与 Table S2–S3。",
     "7. **主模型决策已由作者于 2026-11-09 确认保持 A**：`results/` 的预指定 M2 为唯一主结果（GPL571 M2 = 114 个 DEG，q = 0.145–0.691，M3 = 640），`results_m2b/` 仅作协变量完整的敏感性分析（M2 = 95、M3 = 516，六基因 q = 0.077–0.893）。Abstract、Results 3.1/3.2、Figure 1B/2、Table 1–2 与 Table S2–S3 全部沿用主结果，无需同步改动；决策理由与影响清单见 `work/data/DECISION_LOG.md`。")

must("8. 标题另备一版（若作者坚持保留假设生成定位）：*\"A hypothesis-generating, donor-level re-analysis of public ONH astrocyte microarray data\"*。",
     "8. 标题另备一版（若作者坚持保留假设生成定位）：*\"A hypothesis-generating, donor-level re-analysis of public ONH astrocyte microarray data\"*。\n"
     "9. **N1 整改（第二轮模拟预审发现）**：`diagnose_n1.py` 用同一探针把 ROC 评分从芯片级换成供体级，结果与 `results/07_roc.csv` **6/6 精确一致、Δ=0**（GSE2378-GPL8300 为 1 张芯片/1 供体，13/13），因此 `07_roc.csv` 无需改任何数字。真实缺陷是探针在同一批 13 个供体上按最小 p 挑选后再评估，属循环论证；Table S7 量化了选择偏倚（选定探针 AUC 与全探针中位 AUC 之差 −0.119 至 +0.190）并给出无选择的基因级 AUC 与 BH 校正后的置换 q。Methods 2.5、Results 3.2 与 Discussion 已据实改写。\n"
     "10. **共线措辞收紧**：Table S8 给出 phi、Pearson r、VIF、条件数、秩与零单元格。VIF 1.14–1.16、条件数 3.76–6.29 说明并非经典多重共线，问题是**结构性失衡与零单元格**，故全文不再用 \"nearly collinear\"；同时补出主 QC 未标记的 GSE9944-GPL8300 零单元格（African-American 对照 = 0）。诊断输出在独立的 `results_diagnostics/`，不覆盖 `results/`。")

# ------------------------------------------------------------------- Abstract
must("On GPL571, all three glaucoma donors were of African ancestry, making ancestry and disease nearly collinear.",
     "On GPL571, all three glaucoma donors were of African ancestry and all nine Caucasian donors were controls, leaving an empty ancestry-by-disease cell (phi = −0.354; VIF 1.14) that makes the adjusted disease coefficient uninterpretable.")

# --------------------------------------------------------------- Methods 2.5 ROC
must("For the comparison series, single-gene ROC analysis used array-level expression in POAG versus control eyes only, with 1,000 bootstrap resamples for the AUC 95% CI and 1,000 label permutations for an empirical p value.",
     "For the comparison series, single-gene ROC was computed for POAG versus control eyes only, with 1,000 bootstrap resamples for the AUC 95% CI and 1,000 label permutations for an empirical p value. On GSE2378-GPL8300, the only platform with reported ROC in `07_roc.csv`, each donor contributed exactly one array (13 arrays / 13 donors); a donor-level recomputation using the identical probe and label order therefore reproduced all six AUCs exactly (Table S7; `results_diagnostics/07b_roc_donorlevel.csv`). The probe for each gene was nonetheless selected by the smallest nominal p on these same donors, so the AUC is circular. Table S7 additionally reports the median AUC across all probes mapped to a gene, a selection-free gene score (median expression across those probes) and BH-adjusted permutation q values; none of these estimates is used for inference or can establish diagnostic performance.")

# --------------------------------------------------------- Methods 2.6 / declarations
old_scripts = "`work/data/reanalysis.py`, `reanalysis_m2b.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, `summarize_results.py`, `make_figures_tables.py`, `cold_read_v05.py`, `verify_literature.py`, `apply_v05.py`"
new_scripts = "`work/data/reanalysis.py`, `reanalysis_m2b.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, `summarize_results.py`, `make_figures_tables.py`, `diagnose_n1.py`, `cold_read_v06.py`, `verify_literature.py`, `apply_v06.py`"
must(old_scripts, new_scripts)
must("(`reanalysis.py`, `reanalysis_m2b.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, `summarize_results.py`, `make_figures_tables.py`, `cold_read_v05.py`, `verify_literature.py`, `apply_v05.py`)",
     "(`reanalysis.py`, `reanalysis_m2b.py`, `parallel_fetch.py`, `fetch_gpl5175_annot.py`, `summarize_results.py`, `make_figures_tables.py`, `diagnose_n1.py`, `cold_read_v06.py`, `verify_literature.py`, `apply_v06.py`)")

# ------------------------------------------------------- Results 3.1 collinearity
must("**Table 1.** Differentially expressed probes by model and platform, generated from `results/03_deg_by_model.csv`",
     "Quantitative diagnostics for the ancestry × disease structure are given in Table S8. On GSE9944-GPL571 and -GPL8300 the phi coefficients were −0.354 and −0.372, the VIF for the disease term 1.14 and 1.16, the design condition numbers 3.76 and 6.29 and both cross-tabulations contained a zero cell (GPL571: zero glaucoma donors of Caucasian ancestry; GPL8300: zero African-American controls). Linear collinearity is therefore mild and both design matrices are full rank; the limitation is a structural imbalance with an empty stratum, so the adjusted disease coefficient relies on extrapolation across ancestry groups. The qualitative QC check in the primary run flagged only GPL571; the GPL8300 zero cell was identified in this diagnostic pass.\n\n"
     "**Table 1.** Differentially expressed probes by model and platform, generated from `results/03_deg_by_model.csv`")

# -------------------------------------------------------------- Results 3.2 ROC
must("Exploratory single-gene ROC analysis on GSE2378-GPL8300 gave AUC values of 0.119–1.000 with wide bootstrap 95% CIs (for example, FGFR1 0.857–1.000) and permutation p values of 0.002–0.994; these uncorrected, small-sample estimates do not establish diagnostic value and were not used for inference.",
     "Exploratory single-gene ROC analysis on GSE2378-GPL8300 gave AUC values of 0.119–1.000 with wide bootstrap 95% CIs (for example, FGFR1 0.857–1.000) and permutation p values of 0.002–0.994. Recomputing the same AUCs at donor level changed no value (Δ = 0 on all six genes, one array per donor; Table S7), but the probe for each gene had been chosen by the smallest nominal p on these same 13 donors. The median AUC across all probes of a gene was 0.238–0.976, and the selection-free gene-level score gave 0.167–1.000, i.e. probe selection alone shifted apparent discrimination by up to 0.19 in either direction. These circular, small-sample estimates do not establish diagnostic value and were not used for inference; the apparent contrast with the non-significant BH q values in M2 is a consequence of selection bias rather than a model discrepancy.")

# ------------------------------------------------------------------- Discussion
must("Third, ancestry was an explicit design axis of GSE9944 but is almost completely confounded with disease on GPL571, where every glaucoma donor is African American and every Caucasian donor is a control; a \"disease\" coefficient estimated there cannot be separated from an ancestry effect.",
     "Third, ancestry was an explicit design axis of GSE9944 but is structurally unbalanced against disease: on GPL571 every glaucoma donor is African American and every Caucasian donor is a control, and on GPL8300 there are no African-American controls, so both ancestry × disease tables contain a zero cell (Table S8). Although VIF (1.14–1.16) and condition numbers (3.76–6.29) show no classical multicollinearity and the design matrices are full rank, a \"disease\" coefficient estimated across an empty stratum cannot be separated from an ancestry effect.")

# ------------------------------------------------------------------ Limitations
must("Fifth, where several probes mapped to one gene, the smallest p value was reported, which is optimistic; the complete per-probe results are supplied in the supplementary tables.",
     "Fifth, where several probes mapped to one gene, the smallest p value was reported, which is optimistic; the complete per-probe results are supplied in the supplementary tables and the resulting inflation in apparent ROC discrimination is quantified in Table S7.")

# ------------------------------------------------------------ Supplementary list
must("**Table S5.** Complete M2 results for all probes on every platform (`results/04_deg_primary_M2.csv`); six transcripts across all four models (`results/05_six_key_genes.csv`); donor overlap (`results/10_donor_overlap.csv`); external comparison and ROC/AUC (`results/06_external_validation.csv`, `07_roc.csv`); QC/scale decisions (`02_qc_summary.csv`).",
     "**Table S5.** Complete M2 results for all probes on every platform (`results/04_deg_primary_M2.csv`); six transcripts across all four models (`results/05_six_key_genes.csv`); donor overlap (`results/10_donor_overlap.csv`); external comparison and ROC/AUC (`results/06_external_validation.csv`, `07_roc.csv`); QC/scale decisions (`02_qc_summary.csv`). The donor-level ROC diagnostic is in the independent `results_diagnostics/07b_roc_donorlevel.csv` and does not replace `07_roc.csv`.")

must("**Table S6.** `[UNVERIFIED: 原稿 Table 1、Table 2、Table S1–S3（GO/KEGG/KOBAS 术语与 miRNA 清单）未随本稿重跑；若保留须明确标注为原稿结果。]`",
     "**Table S6.** `[UNVERIFIED: 原稿 Table 1、Table 2、Table S1–S3（GO/KEGG/KOBAS 术语与 miRNA 清单）未随本稿重跑；若保留须明确标注为原稿结果。]`\n\n"
     "**Table S7.** Donor-level versus array-level single-gene ROC on every annotated platform, including arrays per donor, all-probe median AUC, a selection-free gene-level AUC, selection inflation, bootstrap CI, permutation p and BH-adjusted permutation q. Six of six array-level values reconcile exactly with `results/07_roc.csv`; Δ = 0 (`tables/TableS7_donor_vs_array_ROC.tsv`).\n\n"
     "**Table S8.** Quantitative ancestry × disease diagnostics for all six platforms: design terms and rank, condition number, VIF, phi coefficient, Pearson r, smallest cell and zero-cell flag (`tables/TableS8_collinearity_diagnostics.tsv`).")

# --------------------------------------------------------------------- footnote
must("*本文件为文献与声明修订后的全文中稿 v0.5，仍不构成投稿文本。所有统计数字来自 `work/data/results/` 与 `work/data/results_m2b/`；图表与表格由 `work/data/make_figures_tables.py` 从结果表生成；新增参考文献由 `work/data/verify_literature.py` 经 PubMed/Crossref/GEO 官方记录核验，编号由 `work/data/apply_v05.py` 按首次出现顺序重排；标注 `[UNVERIFIED]` 的数字来自原稿、未经重跑。",
     "*本文件为决策落定与 N1 整改后的全文中稿 v0.6，仍不构成投稿文本。主模型已由作者确认保持 A（`results/` 的预指定 M2；`results_m2b/` 仅敏感性）；所有主统计数字来自 `work/data/results/`，诊断数字来自独立的 `work/data/results_diagnostics/`；图表与表格由 `work/data/make_figures_tables.py`、`work/data/diagnose_n1.py` 从结果表生成；新增参考文献由 `work/data/verify_literature.py` 经 PubMed/Crossref/GEO 官方记录核验；标注 `[UNVERIFIED]` 的数字来自原稿、未经重跑。")

must("Whether to promote M2b to the primary model is an author decision; either specification supports the same conclusion.",
     "The author confirmed the pre-specified M2 in `results/` as the primary model and retained M2b as a sensitivity analysis; either specification supports the same conclusion (decision recorded in `DECISION_LOG.md`).")

# --------------------------------------------- residual over-claims in Results 3.1
must("故全文不再用 \"nearly collinear\"；同时补出",
     "故全文不再沿用旧稿的共线性表述；同时补出")
must("The 114 M2 calls on GPL571 cannot be interpreted as disease signal: ancestry and disease were nearly collinear on that platform, and the adjusted coefficient is not identifiable from the deposited design.",
     "The 114 M2 calls on GPL571 cannot be interpreted as disease signal: the ancestry × disease table contains a zero cell there (Table S8), and although the design matrix is full rank the adjusted disease coefficient relies on extrapolation across an empty stratum.")

open(DST, "w", encoding="utf-8").write(s)
print("wrote", os.path.basename(DST), "bytes", len(s.encode("utf-8")), "words", len(s.split()))
for bad in ["nearly collinear", "still pending", "v0.5 文献与声明修订稿", "cold_read_v05.py", "array-level expression in POAG"]:
    print("residual %-40s : %d" % (bad, s.count(bad)))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_v09.py -- derive manuscript v0.9 and cold_read_v09.py from v0.8.

Round 13 completes roadmap item P1-b (cross-tissue directional concordance on
GSE27276).  Every replacement is guarded by an exact-count assertion, so a
silently changed anchor aborts the whole derivation instead of producing a
half-updated manuscript.

Reads (unmodified):
    青光眼生信稿件_全文重写稿_v0.8.md
    data/cold_read_v08.py
Writes:
    青光眼生信稿件_全文重写稿_v0.9.md
    data/cold_read_v09.py
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # work/data
WORK = ROOT.parent                              # work
SRC = WORK / "青光眼生信稿件_全文重写稿_v0.8.md"
DST = WORK / "青光眼生信稿件_全文重写稿_v0.9.md"
CR8 = ROOT / "cold_read_v08.py"
CR9 = ROOT / "cold_read_v09.py"

s = open(SRC, encoding="utf-8").read()
nrep = 0


def rep(old: str, new: str, tag: str = "") -> None:
    global s, nrep
    c = s.count(old)
    assert c == 1, "anchor %s matched %d times: %.90s" % (tag, c, old)
    s = s.replace(old, new, 1)
    nrep += 1


# ---------------------------------------------------------------- 1. version note
rep(
    "本文件是 **v0.8 投稿可行性增强稿（P1-a / P1-c / P1-d）**。v0.7 的全部真实统计数字（`work/data/results/`、`results_m2b/`、`results_diagnostics/`、`results_limma/`、`results_genelevel/`）、Figure 1–2、Table 1–4 与 Table S1–S12 均保持不变；本轮新增①事后可检测效应量与 Table S13、②完整 GPL5175 平台表重建与 Table S15 边界检查、③可复用元数据审计工具与 Table S16、④外部候选 GEO 系列的官方核验（Table S14 核验版）。所有新增结果都在独立目录，决策 A 不变，主结论 0/18 与分支 A 定位不变，仍不可投稿。",
    "本文件是 **v0.9 投稿可行性增强稿（P1-a / P1-b / P1-c / P1-d，P1 路线图全部执行完毕）**。v0.7 的全部真实统计数字（`work/data/results/`、`results_m2b/`、`results_diagnostics/`、`results_limma/`、`results_genelevel/`）、Figure 1–2、Table 1–4 与 Table S1–S12 均保持不变；v0.8 新增 Table S13–S16 与官方核验版 S14；v0.9 新增①外部跨组织方向一致性与 Table S17、②供体重建与混杂审计及 Table S18。所有新增结果都在独立目录（`results_power/`、`results_gpl5175/`、`results_audit/`、`results_external/`），决策 A 不变，主结论 0/18 与分支 A 定位不变，**仍不可投稿**：P1 只改善方法学与报告质量，没有新增独立人类队列、湿实验或真正的独立复现。",
    "版本说明首段",
)

rep(
    "15. **可复用元数据审计（P1-d，Table S16）**：`geo_metadata_audit.py` 把自由文本协变量、组别×祖先零单元格、技术重复/供体重叠、平台注释可得性、尺度与排除组做成五类只读检查，对 6 个主 series matrix 与 1 个外部候选（GSE27276，**仅元数据审计，未做差异分析**）输出 159 项指标。外部候选的官方核验见 `tables/TableS14_official_verification.md`（纠正了旧 S14 的 3 处数字，并剔除 miRNA 芯片 GSE105269）。",
    "15. **可复用元数据审计（P1-d，Table S16）**：`geo_metadata_audit.py` 把自由文本协变量、组别×祖先零单元格、技术重复/供体重叠、平台注释可得性、尺度与排除组做成五类只读检查，对 6 个主 series matrix 与 1 个外部候选（GSE27276，**在 S16 中仅做元数据审计**）输出 159 项指标。外部候选的官方核验见 `tables/TableS14_official_verification.md`（纠正了旧 S14 的 3 处数字，并剔除 miRNA 芯片 GSE105269）。\n"
    "16. **外部跨组织方向一致性（P1-b 完成，Table S17 / S18）**：`external_concordance.py` 对 GSE27276（人小梁网、GPL2507、36 张芯片而 GEO 声明 28 供体）跑三口径 OLS：36 芯片 / 30 单位 / 28 单位，残差 df 34 / 28 / 26；六基因在**每种口径下均 0/6 显著**（q = 0.330–0.805），与三个注释发现平台的方向一致性为每格 2/6 或 3/6（合计 23/54 = 42.6%，纯描述、无检验）。BH q<0.05 的全探针数为 1115 / 1108 / 704。关键发现不是转录本结果，而是**疾病与取材方式（手术 vs 捐献眼）、死后延迟完全混杂**（phi 均为 1.0，加入混杂项后设计秩 2/4），且无祖先/年龄/性别字段，M2 只能退化为 `intercept + glaucoma`。对照侧 19 张芯片按死后延迟归并为 13 供体（与 GEO 一致），病例侧 17 张芯片全部延迟 0，只能靠表达相关性找出两对重复，其中第二对是**不可核实的假设**。本项是跨组织方向一致性练习与审计工具压力测试，**不是独立复现、不是验证队列、不支持也不否定主结论 0/18**；输出在独立 `results_external/`，`results/` 一个字节未改。",
    "版本说明 15/16",
)

# ---------------------------------------------------------------- 2. abstract
rep(
    "An independent limma replication (0/18 tests significant; BH q = 0.116–0.663) and three gene-level conventions (0/18 in each) left the conclusion unchanged.",
    "An independent limma replication (0/18 tests significant; BH q = 0.116–0.663) and three gene-level conventions (0/18 in each) left the conclusion unchanged. An exploratory external cross-tissue comparison (GSE27276) returned no significant six-transcript result under any of three unit conventions, but disease was completely confounded with tissue procurement and postmortem delay, so it cannot serve as validation.",
    "Abstract Results",
)

# ---------------------------------------------------------------- 3. Methods 2.6 script list
rep(
    "`cold_read_v08.py`, `apply_v08.py`).",
    "`cold_read_v08.py`, `apply_v08.py`, `external_concordance.py`, `cold_read_v09.py`, `apply_v09.py`).",
    "Methods 2.6 脚本清单",
)

# ---------------------------------------------------------------- 4. Methods 2.7
M27 = """### 2.7 External cross-tissue comparison (exploratory, not a validation)

To stress-test the metadata checklist on a series outside the primary re-analysis, one public GEO series of human trabecular meshwork was examined (GSE27276, GPL2507; 17 POAG and 19 control arrays). Its accession, sample counts, platform and annotation availability were checked against the official GEO records before use (Table S14 official verification). GEO declares 13 controls and 15 POAG donors but deposits 36 arrays, so three unit conventions were fitted: all 36 arrays as separate units (`array_level`, residual df 34); 30 units in which the 19 control arrays were collapsed to 13 donors by identical postmortem delay while case arrays were left separate (`donor_metadata`, residual df 28); and 28 units matching the declared design, in which two disjoint highest-correlation case-array pairs were additionally averaged (`donor_declared`, residual df 26). The second case-side merge is a data-driven assumption and is not verifiable from the deposited fields (Table S18). Series matrix values were log2-like (range 5.84–15.27) and were not transformed. Probes were mapped with `GPL2507.annot.gz`; 19,219 of 47,293 (40.64%) matrix probes carried a gene symbol and 12 probes mapped to the six pre-specified transcripts. No ancestry, age or sex field is deposited, so the pre-specified M2 design reduced to `intercept + glaucoma` and every test carries the flag `ADJUSTMENT NOT POSSIBLE`. A probe-wise OLS with BH correction across all matrix probes was fitted within each convention; 95% CIs are nominal. Direction agreement with the min-p probe estimates of the frozen primary M2 table was counted as a descriptive sign comparison over six transcripts only, with no inferential test. All outputs are in `results_external/`; no file in `results/` was used for fitting or modified. This is a cross-tissue directional-concordance exercise, not an independent replication or a validation cohort."""

rep(
    "No formal power calculation was performed because the analysis was a re-assessment of existing data.\n\n---\n\n## 3. Results",
    "No formal power calculation was performed because the analysis was a re-assessment of existing data.\n\n" + M27 + "\n\n---\n\n## 3. Results",
    "Methods 2.7 插入点",
)

# ---------------------------------------------------------------- 5. Results 3.5
R35 = """### 3.5 Applying the audit checklist to an external GEO series (exploratory)

The external series (GSE27276) tests the checklist because its deposited metadata fail the same checks in a different way. Its 36 arrays do not correspond to 36 donors: GEO declares 13 controls and 15 POAG donors, six controls and one case contributing both eyes, and one technical replicate between two cases. Among controls, six postmortem-delay values occur exactly twice and seven occur once, so 19 arrays resolve to 13 donors; these six pairs are also the six highest-correlation control array pairs (Table S18). All 17 case arrays were collected at surgery with postmortem delay recorded as 0 or 0:00, so no deposited field pairs them; the two merges needed to reach the declared 15 cases were selected by expression correlation (POAG 6 / POAG 11, r = 0.9808; POAG 16 / POAG 17, r = 0.9656), and the second remains an unverifiable assumption. Disease is completely confounded with tissue procurement (all 17 cases from surgery, all 19 controls from donated eyes; phi = 1.0) and with postmortem delay (all cases 0, all controls > 0; phi = 1.0); adding both terms to the design gives rank 2 of 4, so the confound cannot be adjusted away. No ancestry, age or sex field is available, and the primary M2 therefore reduced to `intercept + glaucoma`.

Under the three unit conventions, 1115 (36 arrays, residual df 34), 1108 (30 units, df 28) and 704 (28 units, df 26) probes reached BH q < 0.05. Because the conventions differ in both the number of units and the case-side averaging, this difference illustrates sensitivity to the unit of analysis rather than providing a clean estimate of pseudo-replication inflation. None of the six transcripts reached BH q < 0.05 in any convention (0 of 6 in each; q = 0.330–0.805; Table S17). Direction agreement with the three annotated discovery platforms was 2 of 6 or 3 of 6 transcripts in every convention-by-platform cell (23 of 54 comparisons overall, 42.6%); this is a descriptive count with no inferential test and is not evidence of directional concordance. Because the tissue, laboratory, platform and case definition all differ and disease is inseparable from procurement and postmortem interval, this comparison can neither support nor refute the primary 0/18 finding. It is reported as a cross-tissue directional-concordance exercise and as a demonstration of the checklist, not as an independent replication, a validation cohort or confirmatory evidence. Outputs are in `results_external/`; `results/` was not modified."""

rep(
    "---\n\n## 4. Discussion",
    R35 + "\n\n---\n\n## 4. Discussion",
    "Results 3.5 插入点",
)

# ---------------------------------------------------------------- 6. Discussion limitations
rep(
    "Eighth, no functional or wet-laboratory validation was performed.",
    "Eighth, no functional or wet-laboratory validation was performed. Ninth, the external cross-tissue comparison (GSE27276) is not an independent validation: disease is fully confounded with procurement and postmortem delay, donor identity is only partly recoverable, no ancestry/age/sex covariates are deposited and direction agreement was 2-3 of 6 transcripts.",
    "Limitations 第九条",
)

# ---------------------------------------------------------------- 7. Discussion audit paragraph
rep(
    "It does not add an independent cohort, a wet-laboratory experiment or a biological claim, and it does not by itself make the manuscript ready for submission.",
    "Extending that checklist to a differential-expression contrast in GSE27276 (Tables S17–S18) exposed complete confounding of disease with tissue procurement and postmortem delay and left all six transcripts non-significant under three unit conventions; this is a cross-tissue directional-concordance exercise, not an independent replication. The work still adds no wet-laboratory experiment or biological claim, and it does not by itself make the manuscript ready for submission.",
    "Discussion 审计工具段",
)

# ---------------------------------------------------------------- 8. Conclusions
rep(
    "The reproducible output of this study is a quantified demonstration of how pseudo-replication and ancestry–disease confounding generate apparently significant gene lists, together with a documented pipeline for re-analysing these public series.",
    "The reproducible output of this study is a quantified demonstration of how pseudo-replication and ancestry–disease confounding generate apparently significant gene lists, together with a documented pipeline for re-analysing these public series. An external cross-tissue comparison did not provide independent confirmation and was itself limited by complete confounding of disease with tissue procurement.",
    "Conclusions",
)

# ---------------------------------------------------------------- 9. supplementary S14/S17/S18
rep(
    "**Table S14.** Candidate external GEO series, with an **official verification** table that supersedes the earlier unverified planning numbers (`tables/TableS14_official_verification.tsv`; planning list in `tables/TableS14_external_cohort_candidates.tsv`). No external series was used for a differential-expression test and none is an independent replication.",
    "**Table S14.** Candidate external GEO series, with an **official verification** table that supersedes the earlier unverified planning numbers (`tables/TableS14_official_verification.tsv`; planning list in `tables/TableS14_external_cohort_candidates.tsv`). The exploratory cross-tissue contrast on GSE27276 is reported separately in Tables S17–S18; no external series provides an independent replication.",
    "§9 S14",
)

rep(
    "**Table S16.** Reusable five-class metadata audit of the six primary series matrices plus one external candidate series audited for metadata only (`tables/TableS16_metadata_audit.tsv`; `results_audit/`).",
    "**Table S16.** Reusable five-class metadata audit of the six primary series matrices plus one external candidate series audited for metadata only (`tables/TableS16_metadata_audit.tsv`; `results_audit/`).\n\n"
    "**Table S17.** Exploratory cross-tissue directional concordance of the six transcripts in GSE27276 under three unit conventions, with log2FC, nominal 95% CI, p, BH q and descriptive sign counts against the three annotated discovery platforms (`tables/TableS17_external_concordance.tsv`; `results_external/`). Not a validation or an independent replication.\n\n"
    "**Table S18.** Donor reconstruction and confounding audit of GSE27276: 36 arrays versus 28 declared donors, 13 control donors recovered from postmortem delay, two correlation-based case-side merges, phi = 1.0 for disease versus procurement and versus postmortem delay, and design rank 2 of 4 (`tables/TableS18_external_donor_reconstruction.tsv`; `results_external/`).",
    "§9 S16/S17/S18",
)

# ---------------------------------------------------------------- 10. footer
rep(
    "*本文件为投稿可行性增强后的全文中稿 v0.8，仍不构成投稿文本。",
    "*本文件为投稿可行性增强后的全文中稿 v0.9（P1 路线图全部执行完毕），仍不构成投稿文本。",
    "Footer 版本",
)
rep(
    "v0.8 新增结果由 `work/data/power_mde.py`、`fetch_5175_parallel.py`、`fetch_gpl5175_annot.py`、`gpl5175_boundary.py` 与 `geo_metadata_audit.py` 生成，均在独立目录；",
    "v0.8 新增结果由 `work/data/power_mde.py`、`fetch_5175_parallel.py`、`fetch_gpl5175_annot.py`、`gpl5175_boundary.py` 与 `geo_metadata_audit.py` 生成，v0.9 新增结果由 `work/data/external_concordance.py` 生成，均在独立目录（`results_external/` 不覆盖 `results/`）；",
    "Footer 脚本",
)

# ---------------------------------------------------------------- sanity
assert s.count("[AUTHOR INPUT REQUIRED:") == 12, s.count("[AUTHOR INPUT REQUIRED:")
assert s.count("[UNVERIFIED") == 10, s.count("[UNVERIFIED")
assert s.count("[UNVERIFIED:") == 8, s.count("[UNVERIFIED:")
for banned in ["independently replicated", "is evidence of no effect",
               "confirmed negative", "is a test of equivalence",
               "was replicated", "were replicated", "validated candidates",
               "key genes", "new method", "demonstrated", "novel", "showed that"]:
    assert banned not in s[s.index("## Abstract"):s.index("## 6. Declarations")], banned
assert "Figure 3–5" not in s[s.index("## Abstract"):s.index("## 6. Declarations")]

open(DST, "w", encoding="utf-8", newline="").write(s)
print("manuscript: %d substitutions, %d -> %d chars" % (nrep, len(open(SRC, encoding="utf-8").read()), len(s)))
print("sha256 v0.8:", hashlib.sha256(open(SRC, "rb").read()).hexdigest()[:12])
print("sha256 v0.9:", hashlib.sha256(open(DST, "rb").read()).hexdigest()[:12])

# ================================================================ cold read v09
c = open(CR8, encoding="utf-8").read()
cn = 0


def crep(old: str, new: str, tag: str = "") -> None:
    global c, cn
    k = c.count(old)
    assert k == 1, "cold-read anchor %s matched %d times: %.90s" % (tag, k, old)
    c = c.replace(old, new, 1)
    cn += 1


crep('"""Cold-read v8 for the feasibility-enhanced manuscript v0.8.',
     '"""Cold-read v9 for the P1-complete manuscript v0.9.', "docstring title")
crep("assertion that neither analysis was silently promoted to the primary result.\n\"\"\"",
     "assertion that neither analysis was silently promoted to the primary result.\n"
     "Adds group P: the GSE27276 cross-tissue directional-concordance stress test,\n"
     "donor reconstruction, confounding audit, and anti-overclaim assertions.\n\"\"\"",
     "docstring tail")
crep('"青光眼生信稿件_全文重写稿_v0.8.md")',
     '"青光眼生信稿件_全文重写稿_v0.9.md")', "MAN")
crep('"青光眼生信稿件_cold-read_v0.8报告.md")',
     '"青光眼生信稿件_cold-read_v0.9报告.md")', "OUT")
crep('lines = ["# Cold-read v0.8（投稿可行性增强版）\\n",',
     'lines = ["# Cold-read v0.9（P1 路线图完成版）\\n",', "report title")
crep('`results_diagnostics`、`results_limma` 与 `results_genelevel`\\n"',
     '`results_diagnostics`、`results_limma`、`results_genelevel`、`results_power`、'
     '`results_gpl5175`、`results_audit` 与 `results_external`\\n"',
     "report baseline")

PGROUP = r'''
# --- 14. P group: v0.9 external cross-tissue concordance (P1-b) --------------
EXT = os.path.join(ROOT, "results_external")
for p in ["Table S17", "Table S18", "GSE27276", "GPL2507", "results_external/",
          "cross-tissue directional-concordance", "not an independent replication",
          "ADJUSTMENT NOT POSSIBLE", "0 of 6", "23 of 54", "42.6%",
          "phi = 1.0", "rank 2 of 4", "40.64%", "12 probes",
          "residual df 34", "residual df 28", "residual df 26",
          "1115", "1108", "704", "q = 0.330", "0.9808", "0.9656"]:
    chk("P S17/S18 正文", "正文已写明 `%s`" % p, p in s,
        "命中" if p in s else "缺失")
for p in ["independently replicated", "independent validation cohort",
          "independent replication of the six transcripts",
          "confirmed the primary finding", "validated the six transcripts",
          "replication was successful", "the genes are real"]:
    chk("P 反面", "不得声称 `%s`" % p, p not in body,
        "命中 %d" % body.count(p))
for p in ["is a validation cohort", "provides independent confirmation",
          "replicates the discovery finding"]:
    chk("P 反面", "不得把外部系列写成 `%s`" % p, p not in body,
        "命中 %d" % body.count(p))

esf = os.path.join(EXT, "external_summary.json")
if os.path.exists(esf):
    e = json.load(open(esf, encoding="utf-8"))
    chk("P 对账", "GSE27276 / GPL2507 与 36 张芯片",
        e["series"] == "GSE27276" and e["platform"] == "GPL2507" and e["n_arrays"] == 36, "")
    chk("P 对账", "三口径单位数 36 / 30 / 28",
        e["n_units_by_convention"] == {"array_level": 36, "donor_metadata": 30,
                                       "donor_declared": 28},
        str(e["n_units_by_convention"]))
    chk("P 对账", "对照侧 13 供体来自死后延迟",
        e["control_donors_from_metadata"] == 13, "")
    chk("P 对账", "注释覆盖 40.64% 与 12 个六基因探针",
        abs(float(e["annotation"]["coverage_pct"]) - 40.64) < 0.01
        and int(e["annotation"]["n_six_gene_probes"]) == 12, "")
    chk("P 对账", "疾病与取材/延迟完全混杂，phi 均为 1.0，设计秩 2",
        abs(float(e["confounding"]["phi_disease_collection"])) == 1.0
        and abs(float(e["confounding"]["phi_disease_delay"])) == 1.0
        and int(e["confounding"]["design_rank_with_confounders"]) == 2, "")
    conv = e["conventions"]
    chk("P 对账", "三口径全探针 BH 数 1115 / 1108 / 704",
        [conv[k]["n_probes_q05"] for k in ("array_level", "donor_metadata", "donor_declared")]
        == [1115, 1108, 704], "")
    chk("P 对账", "三口径六基因均 0/6 显著",
        all(conv[k]["n_six_genes_significant_q05"] == 0 for k in conv), "")
    chk("P 对账", "三口径残差 df 34 / 28 / 26",
        [conv[k]["residual_df"] for k in ("array_level", "donor_metadata", "donor_declared")]
        == [34, 28, 26], "")
    chk("P 对账", "主结果未被修改且 sha256 与实物一致",
        e["primary_results_modified"] is False
        and hashlib.sha256(open(os.path.join(ROOT, "results", "04_deg_primary_M2.csv"), "rb").read())
        .hexdigest() == e["primary_file_sha256"], "")
    chk("P 对账", "两对病例合并 r = 0.980778 / 0.965582",
        len(e["poag_correlation_merges"]) == 2
        and abs(e["poag_correlation_merges"][0]["pearson_r"] - 0.980778) < 1e-6
        and abs(e["poag_correlation_merges"][1]["pearson_r"] - 0.965582) < 1e-6, "")
    chk("P 对账", "角色标记为 cross-tissue 且明确 NOT validation",
        "cross-tissue" in e["role"] and "validation" in e["NOT"], "")
s17f = os.path.join(TABD, "TableS17_external_concordance.tsv")
if os.path.exists(s17f):
    d17 = pd.read_csv(s17f, sep="\t")
    chk("P S17 对账", "18 行（6 基因 × 3 口径）且全部不显著",
        len(d17) == 18 and all(str(x).startswith("not significant") for x in d17["status"]),
        "%d 行" % len(d17))
    chk("P S17 对账", "六基因 q 最小 0.3298 / 最大 0.8049",
        abs(float(d17["q_BH"].min()) - 0.329841) < 0.001
        and abs(float(d17["q_BH"].max()) - 0.804949) < 0.001, "")
c8f = os.path.join(EXT, "08_directional_concordance.csv")
if os.path.exists(c8f):
    d8 = pd.read_csv(c8f)
    chk("P 对账", "方向一致性 23/54 = 42.6%",
        len(d8) == 54 and int(d8["sign_agreement"].sum()) == 23
        and abs(100.0 * d8["sign_agreement"].mean() - 42.6) < 0.1, "")
for f in ["01_array_metadata.csv", "02_donor_map.csv", "03_probe_gene_map.csv",
          "04_OLS_array_level.csv", "05_OLS_donor_metadata.csv",
          "06_OLS_donor_declared.csv", "07_six_genes_all_conventions.csv",
          "08_directional_concordance.csv", "09_confounding_audit.csv",
          "10_sign_agreement_summary.csv", "external_summary.json", "README.md"]:
    chk("P 文件", "`results_external/%s`" % f,
        os.path.exists(os.path.join(EXT, f)), "")
for f in ["TableS17_external_concordance.tsv", "TableS17_external_concordance.md",
          "TableS18_external_donor_reconstruction.tsv",
          "TableS18_external_donor_reconstruction.md",
          "TableS14_official_verification.tsv"]:
    chk("P 文件", "`tables/%s`" % f, os.path.exists(os.path.join(TABD, f)), "")
chk("P 脚本", "`external_concordance.py` 存在",
    os.path.exists(os.path.join(ROOT, "external_concordance.py")), "")
v8 = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.8.md")
chk("P 版本", "v0.8 原文仍保留且字节未变",
    os.path.exists(v8) and hashlib.sha256(open(v8, "rb").read()).hexdigest()
    .startswith("7bb05464f69f"), "v0.8 保留")
chk("P 主结果", "`results/` 目录文件数仍为 13",
    len([x for x in os.listdir(os.path.join(ROOT, "results")) if x.endswith(".csv")]) <= 13,
    "")

'''
crep("# --- report ---\n", PGROUP + "# --- report ---\n", "P 组插入点")

crep(
    'lines.append("- 本检查不能替代机构权限下的 iThenticate/Turnitin 相似度自查，也不能替代逐刊政策人工核对。\\n")',
    'lines.append("- v0.9 新增 **P 组**：GSE27276 跨组织方向一致性（36/30/28 单位、残差 df 34/28/26、'
    '1115/1108/704 个 BH 显著探针、三口径六基因均 0/6）、供体重建（19 对照芯片→13 供体、两对病例相关合并）'
    '与完全混杂审计（phi=1.0、设计秩 2/4）；并断言方向一致性 23/54 为纯描述、外部系列未写成独立复现或验证、'
    'v0.8 字节未变、主结果 sha256 未变。\\n")\n'
    'lines.append("- 本检查不能替代机构权限下的 iThenticate/Turnitin 相似度自查，也不能替代逐刊政策人工核对。\\n")',
    "报告说明 P 组",
)

open(CR9, "w", encoding="utf-8", newline="").write(c)
print("cold-read: %d substitutions, %d -> %d chars" % (cn, len(open(CR8, encoding="utf-8").read()), len(c)))
print("OK -> %s / %s" % (DST.name, CR9.name))

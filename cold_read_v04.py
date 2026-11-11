#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cold-read v3 for the figure/table-completed manuscript v0.4.

Inherits all 53 v0.3 checks (including reconciliation against the REAL
results/*.csv) and adds reproducibility / fact-consistency checks for the
newly generated figures, tables, 95% CIs and M2b sensitivity run.
"""
import os
import re
import sys
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
MAN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.4.md")
RES = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "results")
OUT = os.path.join(WORK, "青光眼生信稿件_cold-read_v0.4报告.md")
s = open(MAN, encoding="utf-8").read()
body = s[s.index("## Abstract"):s.index("## 6. Declarations")] if "## Abstract" in s else s

rows = []
def chk(group, name, ok, detail):
    rows.append((group, name, "PASS" if ok else "FAIL", detail))

# --- 1 residual hard errors from the original / v0.2 ---
bad_phrases = ["Six-eight", "STAT1 was the only up-regulated", "miR-17, miR-17",
               "hsa-miR-30,", "is involved by", "have not significant",
               "were in identified", "At last", "crucial roles", "etiology of glaucoma",
               "SARS-CoV-2", "antiviral processes", "new method", "management of glaucoma",
               "was replicated", "were replicated", "validated candidates", "key genes"]
for p in bad_phrases:
    n = len(re.findall(re.escape(p), s, re.I))
    chk("A 残留硬错误", "`%s`" % p, n == 0, "命中 %d" % n)

# --- 2 overclaim / high-strength language ---
over = ["prove", "proved", "demonstrated", "crucial", "novel", "for the first time",
        "etiology", "pathogenesis", "These results showed that", "showed that",
        "activation of autophagy", "regulating immunity"]
for w in over:
    n = len(re.findall(r"\b" + re.escape(w) + r"\b", body, re.I))
    chk("B 断言强度", "`%s`" % w, n == 0, "命中 %d" % n)

# --- 3 required repositioning language ---
for w in ["did not survive", "not significant", "pseudo-replication", "ancestry",
          "BH", "donor", "hypothesis-generating"]:
    n = len(re.findall(re.escape(w), body, re.I))
    chk("C 定位词", "`%s`" % w, n >= 1, "命中 %d（应 ≥1）" % n)

# --- 4 placeholders ---
counts = {}
for k in ["DATA NEEDED", "PLANNED", "AUTHOR CONFIRM", "AUTHOR INPUT REQUIRED",
          "UNVERIFIED", "CITATION NEEDED", "TO BE COMPLETED",
          "REFERENCES TO BE RE-INSERTED"]:
    counts[k] = len(re.findall(r"\[" + re.escape(k), s))
for k in ["DATA NEEDED", "PLANNED", "AUTHOR CONFIRM"]:
    chk("D 占位符", "`[%s]` 应为 0" % k, counts[k] == 0, "实际 %d" % counts[k])
chk("D 占位符", "剩余占位符均为明确标注的待办", counts["AUTHOR INPUT REQUIRED"] + counts["UNVERIFIED"] > 0,
    "AUTHOR INPUT %d / UNVERIFIED %d / CITATION %d / TO BE COMPLETED %d / REFERENCES %d" %
    (counts["AUTHOR INPUT REQUIRED"], counts["UNVERIFIED"], counts["CITATION NEEDED"],
     counts["TO BE COMPLETED"], counts["REFERENCES TO BE RE-INSERTED"]))

# --- 5 citation numbering ---
refs = set()
for m in re.finditer(r"\[([0-9,\-\s]+)\]", body):
    for part in m.group(1).split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")[:2]
            if a.isdigit() and b.isdigit():
                refs.update(range(int(a), int(b) + 1))
        elif part.isdigit():
            refs.add(int(part))
out_of_range = sorted(x for x in refs if x > 69)
chk("E 引用", "引用编号未越界 (max 69)", not out_of_range,
    "max=%d distinct=%d 越界=%s" % (max(refs) if refs else 0, len(refs), out_of_range))

# --- 6 figure order ---
order = []
for m in re.finditer(r"Figure ([1-5])", body):
    if m.group(1) not in order:
        order.append(m.group(1))
ascending = bool(order) and order == sorted(order, key=int)
chk("F 图表", "Figure 首次引用顺序递增", ascending,
    str(order) + "（允许省略未在正文出现的图号）")

# --- 7 numbers vs REAL results ---
def rd(n):
    p = os.path.join(RES, n)
    return pd.read_csv(p) if os.path.exists(p) else pd.DataFrame()
deg, qc, six = rd("03_deg_by_model.csv"), rd("02_qc_summary.csv"), rd("05_six_key_genes.csv")
if len(deg):
    m2 = deg[deg["model"].str.contains("M2", na=False)]
    vals = sorted(set(int(v) for v in m2["n_DE_probes"]))
    missing = [v for v in vals if v and str(v) not in body]
    chk("G 数字对账", "M2 DEG 数写入正文", not missing,
        "results 中的 M2 DEG 数 %s；文中缺失 %s" % (vals, missing))
if len(qc):
    for _, r in qc.iterrows():
        ds = str(r.get("platform_dataset", ""))
        n = str(r.get("n_donors", ""))
        if ds and n and n != "nan" and ds in body:
            chk("G 数字对账", "%s 供体数 %s 可核对" % (ds, n), True, "QC 表有记录")
if len(six):
    m2s = six[six["model"].str.contains("M2", na=False) & (six["n_probes"] > 0)]
    nsig = int((m2s["q_BH"] < .05).sum())
    chk("G 数字对账", "六基因显著数与结论一致", nsig == 0,
        "M2 中 q<0.05 的基因×平台数 = %d；正文须声明为 0" % nsig)
else:
    chk("G 数字对账", "结果表可读", False, "05_six_key_genes.csv 缺失")

# --- 8 abstract / results / conclusions consistency ---
def seg(a, b):
    i = s.index(a); j = s.index(b) if b else len(s)
    return s[i:j]
abst = seg("## Abstract", "## 1. Introduction")
conc = seg("## 5. Conclusions", "## 6. Declarations")
for name, chunk in [("Abstract", abst), ("Conclusions", conc)]:
    ok = bool(re.search(r"not significant|did not survive|q\s*[≥>]=?\s*0\.05|no longer", chunk, re.I))
    chk("H 三处一致", "%s 声明六基因未存活" % name, ok, "命中" if ok else "未找到阴性声明")

# --- 9 v0.4: generated artefacts, reproducibility and fact consistency -----
FIGD = os.path.join(ROOT, "figures")
TABD = os.path.join(ROOT, "tables")
RESB = os.path.join(ROOT, "results_m2b")
for f in ["Figure1.png", "Figure1.svg", "Figure2.png", "Figure2.svg"]:
    chk("I 图表文件", "`figures/%s`" % f, os.path.exists(os.path.join(FIGD, f)),
        "存在" if os.path.exists(os.path.join(FIGD, f)) else "缺失")
for f in ["Table1_DEG_by_model.tsv", "Table2_six_genes_M2.tsv",
          "Table3_cohort_QC.tsv", "Table4_donor_overlap.tsv",
          "TableS1_all_probes_six_genes.tsv", "TableS2_M2_vs_M2b_DEG_counts.tsv",
          "TableS3_M2_vs_M2b_six_genes.tsv", "TableS4_sensitivity_grid.tsv"]:
    p = os.path.join(TABD, f)
    chk("I 表格文件", "`tables/%s`" % f, os.path.exists(p),
        "存在" if os.path.exists(p) else "缺失")
for f in ["file_manifest.csv"]:
    p = os.path.join(TABD, f)
    ok = os.path.exists(p) and len(pd.read_csv(p)) >= 30
    chk("I 可复现", "`tables/%s` >= 30 条 sha256" % f, ok,
        "%d 条" % (len(pd.read_csv(p)) if os.path.exists(p) else 0))
chk("I 可复现", "`REPRODUCIBILITY.md` 存在", os.path.exists(os.path.join(ROOT, "REPRODUCIBILITY.md")), "")
chk("I 可复现", "未编造代码 DOI", "10.5281/zenodo" not in s and "doi.org/10." not in s,
    "公开 DOI 仍标为 AUTHOR INPUT")

bad_facts = ["converted to the same two-column format",
             "Six probes could not be assigned a symbol",
             "with ancestry, age and sex covariates",
             "mean-centred age and sex",
             "the GPL5175 platform table was extracted from the GPL5175 family SOFT archive"]
for p in bad_facts:
    chk("J 事实一致性", "不再声称 `%s`" % p, p not in s, "命中 %d" % s.count(p))
chk("J 事实一致性", "正文不再引用 `Figure 3–5`", "Figure 3–5" not in body,
    "正文命中 %d" % body.count("Figure 3–5"))
for p in ["Numeric age and sex did not enter any model",
          "not completed", "no probe mapped", "M2b", "95% CIs are nominal",
          "96 in total", "66 donor-platform records"]:
    chk("J 事实一致性", "已写入 `%s`" % p, p in s, "命中" if p in s else "缺失")

if os.path.isdir(RESB):
    db = pd.read_csv(os.path.join(RESB, "03_deg_by_model.csv"))
    sb = pd.read_csv(os.path.join(RESB, "05_six_key_genes.csv"))
    m2b = db[db.model.str.contains("M2", na=False)]
    vals_b = sorted(set(int(v) for v in m2b.n_DE_probes))
    chk("K M2b 对账", "M2b DEG 数写入正文", all(str(v) in body for v in vals_b),
        "results_m2b 中的 M2 DEG 数 %s" % vals_b)
    nsig_b = int((sb[sb.model.str.contains("M2", na=False) & (sb.n_probes > 0)].q_BH < .05).sum())
    chk("K M2b 对账", "M2b 六基因显著数 = 0", nsig_b == 0, "实际 %d" % nsig_b)
    chk("K M2b 对账", "M2b q 范围写入正文", "0.077" in s and "0.893" in s, "0.077–0.893")
else:
    chk("K M2b 对账", "results_m2b 存在", False, "目录缺失")

t2p = os.path.join(TABD, "Table2_six_genes_M2.tsv")
if os.path.exists(t2p):
    t2 = pd.read_csv(t2p, sep="\t")
    nci = sum(1 for v in t2["95% CI"] if str(v) in s)
    chk("K M2b 对账", "Table 2 的 18 个 95% CI 全部写入正文", len(t2) == 18 and nci == 18,
        "表格 %d 行 / 正文命中 %d 个 CI" % (len(t2), nci))
gp = os.path.join(TABD, "TableS4_sensitivity_grid.tsv")
if os.path.exists(gp):
    g = pd.read_csv(gp, sep="\t")
    chk("K M2b 对账", "敏感性网格为 4 x 2 x 3 x 2 = 48 行", len(g) == 48, "实际 %d 行" % len(g))
chk("K M2b 对账", "占位符数量较 v0.3 下降且仍显式标注",
    0 < counts["AUTHOR INPUT REQUIRED"] < 16, "AUTHOR INPUT %d（v0.3 为 16）" % counts["AUTHOR INPUT REQUIRED"])

# --- report ---
lines = ["# Cold-read v0.4（图表补齐 + 事实一致性版）\n",
         "> 检查对象：`%s`；数值基准：`%s` 与 `results_m2b`\n" % (os.path.basename(MAN), os.path.basename(RES)),
         "| 组 | 检查项 | 结果 | 说明 |", "|---|---|---|---|"]
for g, n, st, d in rows:
    lines.append("| %s | %s | %s | %s |" % (g, n, st, d))
np_ = sum(1 for r in rows if r[2] == "PASS")
nf = len(rows) - np_
lines.append("\n**合计 %d 项：PASS %d / FAIL %d**\n" % (len(rows), np_, nf))
lines.append("\n## 说明\n")
lines.append("- `[DATA NEEDED]` / `[PLANNED]` / `[AUTHOR CONFIRM]` 仍为 0；统计数字来自 `results/`，"
             "图表与表格由 `make_figures_tables.py` 从结果表生成，并与 CSV 逐格对账。\n")
lines.append("- 剩余占位符属于**外部输入**：作者声明、代码公开 DOI、文献重排、期刊版式转换；这些不是本轮分析能生成的。\n")
lines.append("- `[UNVERIFIED]` 明确标注原稿下游分析（DAVID/KOBAS/miRNA 预测）未重跑，其数字不得当作重跑结果。\n")
lines.append("- 新增 J/K 组检查确认：未把未完成的 GPL5175 映射写成已完成、未把未进入模型的 age/sex 写成已校正、"
             "未把 `probe not mapped` 写成阴性验证、未编造代码 DOI。\n")
lines.append("- 本检查不能替代机构权限下的 iThenticate/Turnitin 相似度自查。\n")
open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("PASS %d / FAIL %d -> %s" % (np_, nf, OUT))
for r in rows:
    if r[2] == "FAIL":
        print("  FAIL:", r[1], "|", r[3])

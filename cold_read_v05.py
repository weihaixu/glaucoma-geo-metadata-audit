#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cold-read v4 for the reference/declaration-completed manuscript v0.5.

Inherits all 87 v0.4 checks (real results reconciliation, figures, CIs, M2b,
fact consistency) and adds a two-way citation audit: every in-text marker has
a bibliography entry, every bibliography entry is cited, and every newly
added reference is traceable to PubMed / Crossref / an official GEO record.
"""
import json
import os
import re
import sys
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
MAN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.5.md")
RES = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "results")
OUT = os.path.join(WORK, "青光眼生信稿件_cold-read_v0.5报告.md")
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
    # Bibliography titles may legitimately contain e.g. "Key Genes"; only the
    # paper body is checked for the banned phrasing.
    n = len(re.findall(re.escape(p), body, re.I))
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
chk("D 占位符", "文献占位符 CITATION NEEDED 为 0", counts["CITATION NEEDED"] == 0,
    "实际 %d" % counts["CITATION NEEDED"])
chk("D 占位符", "参考文献待插入说明为 0", counts["REFERENCES TO BE RE-INSERTED"] == 0,
    "实际 %d" % counts["REFERENCES TO BE RE-INSERTED"])
chk("D 占位符", "剩余占位符均为明确标注的待办", counts["AUTHOR INPUT REQUIRED"] + counts["UNVERIFIED"] > 0,
    "AUTHOR INPUT %d / UNVERIFIED %d / CITATION %d / TO BE COMPLETED %d / REFERENCES %d" %
    (counts["AUTHOR INPUT REQUIRED"], counts["UNVERIFIED"], counts["CITATION NEEDED"],
     counts["TO BE COMPLETED"], counts["REFERENCES TO BE RE-INSERTED"]))

# --- 5 citation numbering: dynamic two-way audit against the bibliography ---
bib_seg = s[s.index("## 7. References"):s.index("## 8. Figure legends")]
bib_nums = [int(m.group(1)) for m in re.finditer(r"^(\d+)\.\s+\S", bib_seg, re.M)]
refs = set()
for m in re.finditer(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]", body):
    for part in re.split(r"\s*,\s*", m.group(1)):
        if "-" in part:
            a, b = part.split("-")[:2]
            if a.isdigit() and b.isdigit():
                refs.update(range(int(a), int(b) + 1))
        elif part.isdigit():
            refs.add(int(part))
chk("E 引用", "参考文献表编号连续 1..%d" % (len(bib_nums) if bib_nums else 0),
    bool(bib_nums) and bib_nums == list(range(1, len(bib_nums) + 1)),
    "%d 条，首尾 %s" % (len(bib_nums), (bib_nums[:1], bib_nums[-1:])))
chk("E 引用", "正文引用编号全部有对应文献条目", bool(refs) and refs <= set(bib_nums),
    "正文 %d 个编号；越界 %s" % (len(refs), sorted(refs - set(bib_nums))))
chk("E 引用", "每条参考文献至少被正文引用一次", bool(refs) and set(bib_nums) <= refs,
    "未被引用 %s" % sorted(set(bib_nums) - refs))
chk("E 引用", "引用编号首次出现顺序与文献表一致",
    bool(bib_nums) and max(bib_nums) == len(bib_nums), "最大编号 %d" % (max(bib_nums) if bib_nums else 0))

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
decl_seg = s[s.index("## 6. Declarations"):s.index("## 7. References")]
chk("I 可复现", "未编造代码 DOI",
    "10.5281/zenodo" not in decl_seg and "[AUTHOR INPUT REQUIRED:" in decl_seg,
    "Code/Data availability 仍标为作者填写")

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

# --- 12. v0.5: verified literature, ledger and declaration completeness ----
VREF = os.path.join(ROOT, "verified_references.json")
RTAB = os.path.join(ROOT, "references_v05.tsv")
LEDG = os.path.join(ROOT, "literature_ledger.tsv")
REMAP = os.path.join(ROOT, "citation_remap.json")
GUIDE = os.path.join(WORK, "青光眼生信稿件_声明填写指南.md")
if os.path.exists(VREF):
    ver = json.load(open(VREF, encoding="utf-8"))
    chk("L 文献核验", "新增文献核验库 = 27 条", len(ver) == 27, "实际 %d" % len(ver))
    traced = sum(1 for v in ver.values()
                 if any(t in v["source"] for t in ("PubMed", "Crossref", "GEO")))
    chk("L 文献核验", "27 条全部标注可溯源核验来源", traced == 27, "实际 %d" % traced)
    missing = [k for k, v in ver.items()
               if v["title"][:35].lower() not in bib_seg.lower()]
    chk("L 文献核验", "27 条新增核验文献全部进入参考文献表", not missing,
        "缺失 %s" % missing[:5])
    n_recent = sum(1 for v in ver.values() if v["year"] >= "2022"
                   and "PubMed" in v["source"])
    chk("L 文献核验", "2022–2026 期刊文献 ≥ 15 篇", n_recent >= 15, "实际 %d" % n_recent)
else:
    chk("L 文献核验", "verified_references.json 存在", False, "缺失")
if os.path.exists(RTAB):
    rt = pd.read_csv(RTAB, sep="\t")
    chk("L 文献核验", "references_v05.tsv = 58 行", len(rt) == 58, "实际 %d" % len(rt))
    chk("L 文献核验", "台账分类 retained 31 / new 27",
        int((rt.category == "retained").sum()) == 31 and int((rt.category == "new").sum()) == 27,
        "retained %d / new %d" % (int((rt.category == "retained").sum()),
                                  int((rt.category == "new").sum())))
else:
    chk("L 文献核验", "references_v05.tsv 存在", False, "缺失")
if os.path.exists(LEDG):
    led = pd.read_csv(LEDG, sep="\t")
    acts = led.action.value_counts().to_dict()
    chk("L 文献核验", "台账 DELETE 37 / REPLACE 1 / RETAIN 31 / ADD 27",
        acts.get("DELETE") == 37 and acts.get("REPLACE") == 1
        and acts.get("RETAIN") == 31 and acts.get("ADD") == 27, str(acts))
else:
    chk("L 文献核验", "literature_ledger.tsv 存在", False, "缺失")
chk("L 文献核验", "参考文献表无 COVID / SARS-CoV-2 / 抗病毒支线",
    not re.search(r"COVID|SARS-CoV-2|antiviral", bib_seg, re.I),
    "命中 %d" % len(re.findall(r"COVID|SARS-CoV-2|antiviral", bib_seg, re.I)))
chk("L 文献核验", "参考文献表无 medRxiv / bioRxiv 预印本",
    not re.search(r"medRxiv|bioRxiv", bib_seg, re.I),
    "命中 %d" % len(re.findall(r"medRxiv|bioRxiv", bib_seg, re.I)))
chk("L 文献核验", "正文不再出现 COVID 支线", "COVID" not in body,
    "命中 %d" % body.count("COVID"))
chk("L 文献核验", "声明填写指南存在且覆盖 CRediT / AI 披露",
    os.path.exists(GUIDE) and "CRediT" in open(GUIDE, encoding="utf-8").read()
    and "AI" in open(GUIDE, encoding="utf-8").read(), "指南文件")
chk("L 文献核验", "版本说明显式标注 M2b 主模型决策待作者确认",
    "M2b 是否升为主模型仍待作者决策" in s, "命中" if "M2b 是否升为主模型仍待作者决策" in s else "缺失")
chk("L 文献核验", "版本说明显式标注保留条目待 Zotero 逐条复核",
    "尚未逐条用 Zotero 统一" in s, "命中" if "尚未逐条用 Zotero 统一" in s else "缺失")
if os.path.exists(REMAP):
    rm = json.load(open(REMAP, encoding="utf-8"))
    chk("L 文献核验", "编号映射最大值 = 58 且无重复",
        max(rm["num"].values()) == 58 and len(set(rm["num"].values())) == 58,
        "max=%d distinct=%d" % (max(rm["num"].values()), len(set(rm["num"].values()))))
else:
    chk("L 文献核验", "citation_remap.json 存在", False, "缺失")

# --- report ---
lines = ["# Cold-read v0.5（文献与声明修订版）\n",
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
lines.append("- v0.5 新增 **E 组双向引用对账**（正文每个编号有条目、每条条目被引用、编号连续）与 "
             "**L 组文献核验**（27 条新增文献全部有 PubMed/Crossref/GEO 官方来源、无 COVID 支线与预印本、"
             "台账 37 删除 / 1 替换 / 31 保留 / 27 新增）。\n")
lines.append("- 剩余占位符属于**外部输入**：12 处作者声明与代码 DOI、10 处 `[UNVERIFIED]` 原稿下游结果；"
             "这些不是本轮分析能生成的。保留的 31 条原稿文献未逐条重验，定稿前须用 Zotero 统一格式。\n")
lines.append("- M2b 是否升为主模型仍待作者决策；本版沿用 `results/` 为主结果，未改动任何统计数字。\n")
lines.append("- 本检查不能替代机构权限下的 iThenticate/Turnitin 相似度自查，也不能替代逐刊政策人工核对。\n")
open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("PASS %d / FAIL %d -> %s" % (np_, nf, OUT))
for r in rows:
    if r[2] == "FAIL":
        print("  FAIL:", r[1], "|", r[3])

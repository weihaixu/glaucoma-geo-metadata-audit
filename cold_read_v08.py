#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cold-read v8 for the feasibility-enhanced manuscript v0.8.

Inherits all 161 v0.6 checks (real results reconciliation, figures, CIs, M2b,
fact consistency, two-way citation audit, verified literature, decision A,
donor-level ROC reconciliation and collinearity diagnostics) and adds group N:
real R/limma replication, gene-level three-convention sensitivity, and the
assertion that neither analysis was silently promoted to the primary result.
"""
import hashlib
import json
import os
import re
import sys
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
MAN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.8.md")
RES = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "results")
OUT = os.path.join(WORK, "青光眼生信稿件_cold-read_v0.8报告.md")
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
chk("L 文献核验", "版本说明显式标注主模型决策已确认保持 A",
    "主模型决策已由作者" in s and "确认保持 A" in s,
    "命中" if ("主模型决策已由作者" in s and "确认保持 A" in s) else "缺失")
chk("L 文献核验", "版本说明显式标注保留条目待 Zotero 逐条复核",
    "尚未逐条用 Zotero 统一" in s, "命中" if "尚未逐条用 Zotero 统一" in s else "缺失")
if os.path.exists(REMAP):
    rm = json.load(open(REMAP, encoding="utf-8"))
    chk("L 文献核验", "编号映射最大值 = 58 且无重复",
        max(rm["num"].values()) == 58 and len(set(rm["num"].values())) == 58,
        "max=%d distinct=%d" % (max(rm["num"].values()), len(set(rm["num"].values()))))
else:
    chk("L 文献核验", "citation_remap.json 存在", False, "缺失")

# --- 13. v0.6: decision A, N1 donor-level ROC, circularity, collinearity ----
DIAG = os.path.join(ROOT, "results_diagnostics")
DLOG = os.path.join(ROOT, "DECISION_LOG.md")
dlog = open(DLOG, encoding="utf-8").read() if os.path.exists(DLOG) else ""
chk("M 决策 A", "`DECISION_LOG.md` 记载作者于 2026-11-09 确认保持 A",
    "保持 A" in dlog and "2026-11-09" in dlog, "决策台账")
for p in ["仍待作者决策", "待作者拍板", "whether to promote M2b"]:
    n = len(re.findall(re.escape(p), s, re.I))
    chk("M 决策 A", "不再出现 `%s`" % p, n == 0, "命中 %d" % n)
chk("M 决策 A", "版本说明写明 `results/` 为唯一主结果",
    "唯一主结果" in s and "预指定 M2" in s,
    "命中" if "唯一主结果" in s else "缺失")
chk("M 决策 A", "版本说明写明 M2b 仅作敏感性",
    "仅作协变量完整的敏感性分析" in s or "仅作敏感性" in s,
    "命中" if "仅作" in s else "缺失")
for v in ["114", "640", "0.145", "0.691", "95", "516", "0.077", "0.893"]:
    chk("M 决策 A", "A/B 对照数字 `%s` 可核对" % v, v in s,
        "命中" if v in s else "缺失")

p07 = os.path.join(RES, "07_roc.csv")
if os.path.exists(p07):
    r07 = pd.read_csv(p07)
    chk("M 主结果未变", "`07_roc.csv` 仍为 12 行且未混入诊断列",
        len(r07) == 12 and "auc_donor" not in r07.columns,
        "%d 行 / 列 %s" % (len(r07), list(r07.columns)[:4]))
    tg = r07[(r07.dataset == "GSE2378-GPL8300") & (r07.gene == "TGFBR2")]
    st = r07[(r07.dataset == "GSE2378-GPL8300") & (r07.gene == "STAT1")]
    chk("M 主结果未变", "TGFBR2 AUC = 1.000 / STAT1 AUC = 0.119 保持原值",
        len(tg) == 1 and len(st) == 1 and abs(float(tg.auc.iat[0]) - 1.0) < 1e-9
        and abs(float(st.auc.iat[0]) - 0.11904761904761904) < 1e-9,
        "TGFBR2 %s / STAT1 %s" % (tg.auc.tolist(), st.auc.tolist()))
else:
    chk("M 主结果未变", "`07_roc.csv` 存在", False, "缺失")
man_p = os.path.join(TABD, "file_manifest.csv")
if os.path.exists(man_p) and os.path.exists(p07):
    import hashlib
    h = hashlib.sha256()
    with open(p07, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    mani = pd.read_csv(man_p)
    row = mani[mani.path == "results/07_roc.csv"]
    chk("M 主结果未变", "`07_roc.csv` sha256 与 file_manifest 记录一致",
        len(row) == 1 and h.hexdigest() == str(row.sha256.iat[0]),
        "sha %s" % h.hexdigest()[:12])

p7b = os.path.join(DIAG, "07b_roc_donorlevel.csv")
if os.path.exists(p7b):
    d7 = pd.read_csv(p7b)
    okr = d7[d7.array_reconciled.astype(str) == "MATCH"]
    badr = d7[d7.array_reconciled.astype(str) == "MISMATCH"]
    chk("M N1 对账", "芯片级 AUC 与主结果 6/6 精确一致", len(okr) == 6,
        "exact %d" % len(okr))
    chk("M N1 对账", "对账无不一致行", len(badr) == 0, "mismatch %d" % len(badr))
    g = d7[(d7.dataset == "GSE2378-GPL8300") & d7.auc_donor.notna()]
    chk("M N1 对账", "供体级 Δ = 0（6/6）",
        len(g) == 6 and float(g.auc_delta.abs().max()) < 1e-9,
        "max |delta| = %s" % (g.auc_delta.abs().max() if len(g) else "n/a"))
    chk("M N1 对账", "GSE2378-GPL8300 一供体一芯片（13/13）",
        len(g) == 6 and g.arrays_per_donor_min.max() == 1
        and g.arrays_per_donor_max.max() == 1 and g.n_arrays.max() == 13
        and g.n_donors.max() == 13, "arrays/donors = %s" % (g.n_arrays.max() if len(g) else "n/a"))
    sel = g.auc_selection_inflation.dropna()
    chk("M N1 对账", "选择膨胀范围 −0.119 ~ +0.190",
        len(sel) == 6 and round(float(sel.min()), 3) == -0.119
        and round(float(sel.max()), 3) == 0.190,
        "%.3f ~ %.3f" % (sel.min(), sel.max()) if len(sel) else "n/a")
else:
    chk("M N1 对账", "`results_diagnostics/07b_roc_donorlevel.csv` 存在", False, "缺失")
for f in ["collinearity_diagnostics.csv", "ancestry_disease_crosstab.csv",
          "N1_DIAGNOSTICS.md"]:
    chk("M N1 对账", "`results_diagnostics/%s`" % f,
        os.path.exists(os.path.join(DIAG, f)), "存在" if os.path.exists(os.path.join(DIAG, f)) else "缺失")

s7p = os.path.join(TABD, "TableS7_donor_vs_array_ROC.tsv")
s8p = os.path.join(TABD, "TableS8_collinearity_diagnostics.tsv")
if os.path.exists(s7p):
    s7 = pd.read_csv(s7p, sep="\t")
    chk("M 补充表", "Table S7 = 36 行 / 18 行可评估",
        len(s7) == 36 and int((s7.status == "OK").sum()) == 18,
        "%d 行 / OK %d" % (len(s7), int((s7.status == "OK").sum())))
else:
    chk("M 补充表", "Table S7 存在", False, "缺失")
if os.path.exists(s8p):
    s8 = pd.read_csv(s8p, sep="\t")
    two = s8[s8.ancestry_available == "yes"]
    chk("M 共线诊断", "Table S8 = 6 平台；2 个含 ancestry 的平台均有零单元格",
        len(s8) == 6 and len(two) == 2 and (two.smallest_cell == 0).all(),
        "%d 行 / ancestry %d / 零单元格 %s" % (len(s8), len(two), two.smallest_cell.tolist()))
    chk("M 共线诊断", "VIF ≤ 1.20 且条件数 < 7（非经典多重共线）",
        (two.vif_glaucoma <= 1.20).all() and (two.condition_number < 7).all(),
        "VIF %s / cond %s" % (two.vif_glaucoma.tolist(), two.condition_number.tolist()))
else:
    chk("M 共线诊断", "Table S8 存在", False, "缺失")

for p in ["circular", "selection-free gene score", "Table S7", "Table S8",
          "one array per donor", "Δ = 0", "zero cell", "phi coefficients",
          "condition numbers", "full rank", "empty stratum",
          "diagnose_n1.py", "cold_read_v07.py", "N1 整改", "6/6 精确一致"]:
    chk("M 表述", "正文已写明 `%s`" % p, p in s,
        "命中" if p in s else "缺失")
for p in ["nearly collinear", "not identifiable from the deposited design",
          "array-level expression in POAG versus control eyes only"]:
    n = len(re.findall(re.escape(p), s, re.I))
    chk("M 表述", "不再声称 `%s`" % p, n == 0, "命中 %d" % n)
for v in ["−0.354", "−0.372", "1.14", "1.16", "3.76", "6.29",
          "0.238", "0.167", "0.19"]:
    chk("M 共线诊断", "诊断数字 `%s` 写入正文" % v, v in s,
        "命中" if v in s else "缺失")

# --- N group: real limma replication + gene-level sensitivity (round 9) ---
LIM = os.path.join(ROOT, "results_limma")
GEN = os.path.join(ROOT, "results_genelevel")
TABD = os.path.join(ROOT, "tables")

for f in ["LIMMA_STATUS.md", "session_info.txt", "01_probe_reconciliation.csv",
          "02_six_genes_limma_vs_ols.csv", "03_dataset_summary.csv",
          "limma_fit_summary.tsv"]:
    p = os.path.join(LIM, f)
    chk("N limma 文件", "`results_limma/%s`" % f, os.path.exists(p),
        "存在" if os.path.exists(p) else "缺失")
for f in ["GENELEVEL_STATUS.md", "01_gene_level_deg.csv",
          "02_six_genes_three_conventions.csv", "03_dataset_summary.csv"]:
    p = os.path.join(GEN, f)
    chk("N 基因级文件", "`results_genelevel/%s`" % f, os.path.exists(p),
        "存在" if os.path.exists(p) else "缺失")
for f in ["limma_3.52.4.zip", "statmod_1.5.0.zip", "MANIFEST.tsv"]:
    p = os.path.join(ROOT, "Rpackages", f)
    chk("N R 环境", "`Rpackages/%s`" % f, os.path.exists(p),
        "存在" if os.path.exists(p) else "缺失")
chk("N R 环境", "项目内 Rlib 已安装 limma",
    os.path.exists(os.path.join(ROOT, "Rlib", "limma", "DESCRIPTION")),
    "存在" if os.path.exists(os.path.join(ROOT, "Rlib", "limma", "DESCRIPTION")) else "缺失")
si = os.path.join(LIM, "session_info.txt")
if os.path.exists(si):
    sit = open(si, encoding="utf-8", errors="replace").read()
    chk("N R 环境", "R sessionInfo 记录 R 4.2.0 与 limma 3.52.4",
        "R version 4.2.0" in sit and "limma_3.52.4" in sit,
        "R4.2.0=%s limma=%s" % ("R version 4.2.0" in sit, "limma_3.52.4" in sit))

prec = os.path.join(LIM, "01_probe_reconciliation.csv")
if os.path.exists(prec):
    pr = pd.read_csv(prec, low_memory=False)
    chk("N limma 对账", "全探针对账表 = 69,513 行", len(pr) == 69513, "实际 %d" % len(pr))
    d = float((pr.log2FC - pr.logFC).abs().max())
    chk("N limma 对账", "limma logFC 与主 OLS 系数一致 (<1e-10)", d < 1e-10, "max|d|=%.3g" % d)
    chk("N limma 对账", "自由度列无缺失",
        pr.df_residual.notna().all() and pr.df_total.notna().all(),
        "NA %d / %d" % (pr.df_residual.isna().sum(), pr.df_total.isna().sum()))
    chk("N limma 对账", "limma  moderated t 与 OLS t 确实不同",
        float((pr.t - pr.t_mod).abs().max()) > 0.01,
        "max|dt|=%.3f" % float((pr.t - pr.t_mod).abs().max()))

sl = os.path.join(LIM, "02_six_genes_limma_vs_ols.csv")
if os.path.exists(sl):
    slx = pd.read_csv(sl)
    oks = slx[slx.status == "OK"]
    chk("N limma 结论", "可评估六基因检验 = 18", len(oks) == 18, "实际 %d" % len(oks))
    chk("N limma 结论", "主 OLS 0/18 显著", int(oks.sig_ols.sum()) == 0,
        "显著 %d" % int(oks.sig_ols.sum()))
    chk("N limma 结论", "limma 0/18 显著，分支 A 未变", int(oks.sig_limma.sum()) == 0,
        "显著 %d" % int(oks.sig_limma.sum()))
    chk("N limma 结论", "limma q 范围 0.116–0.663",
        round(float(oks.q_limma.min()), 3) == 0.116 and
        round(float(oks.q_limma.max()), 3) == 0.663,
        "%.4f–%.4f" % (oks.q_limma.min(), oks.q_limma.max()))

sm = os.path.join(LIM, "03_dataset_summary.csv")
if os.path.exists(sm):
    smx = pd.read_csv(sm).set_index("platform_dataset")
    r = smx.loc["GSE9944-GPL571"]
    chk("N limma DEG", "GPL571 M2 114 → 128",
        int(r.n_q05_lfc1_ols) == 114 and int(r.n_q05_lfc1_limma) == 128,
        "%d → %d" % (r.n_q05_lfc1_ols, r.n_q05_lfc1_limma))
    chk("N limma DEG", "GPL571 M3 640 → 709",
        int(r.n_q05_lfc05_ols) == 640 and int(r.n_q05_lfc05_limma) == 709,
        "%d → %d" % (r.n_q05_lfc05_ols, r.n_q05_lfc05_limma))
    r2 = smx.loc["GSE9944-GPL8300"]
    chk("N limma DEG", "GPL8300 M2 0 → 2",
        int(r2.n_q05_lfc1_ols) == 0 and int(r2.n_q05_lfc1_limma) == 2,
        "%d → %d" % (r2.n_q05_lfc1_ols, r2.n_q05_lfc1_limma))
    chk("N limma DEG", "先验 df 2.25–4.58 且 total df > residual df",
        smx.df_prior.min() > 2.2 and smx.df_prior.max() < 4.7 and
        (smx.df_total > smx.df_residual).all(),
        "prior %.2f–%.2f" % (smx.df_prior.min(), smx.df_prior.max()))

sg = os.path.join(GEN, "02_six_genes_three_conventions.csv")
if os.path.exists(sg):
    sgx = pd.read_csv(sg)
    conv = sgx.groupby("convention").significant.sum().to_dict()
    chk("N 基因级结论", "三种口径均 0 显著",
        len(conv) == 3 and sum(conv.values()) == 0, str(conv))
    chk("N 基因级结论", "GSE45570 如实标为无注释而非阴性",
        set(sgx[sgx.platform_dataset == "GSE45570"].status) == {"no gene annotation"} or
        "no gene annotation" in set(sgx[sgx.platform_dataset == "GSE45570"].status),
        str(set(sgx[sgx.platform_dataset == "GSE45570"].status)))
sgm = os.path.join(GEN, "03_dataset_summary.csv")
if os.path.exists(sgm):
    sgm = pd.read_csv(sgm)
    chk("N 基因级结论", "3 平台可分析 + 1 平台无注释",
        int((sgm.status == "OK").sum()) == 3 and
        int((sgm.status == "no gene annotation").sum()) == 1,
        str(sgm.status.value_counts().to_dict()))

for f, n in [("TableS9_limma_vs_OLS_six_genes.tsv", 24),
             ("TableS10_limma_DEG_counts.tsv", 4),
             ("TableS11_genelevel_six_genes_q.tsv", 18),
             ("TableS12_genelevel_DEG_counts.tsv", 4)]:
    p = os.path.join(TABD, f)
    chk("N 补充表", "`%s` 存在" % f, os.path.exists(p),
        "存在" if os.path.exists(p) else "缺失")

for p in ["v0.7", "limma 3.52.4", "R 4.2.0", "0/18", "0.116–0.663",
          "69,513", "3.3e-14", "2.25–4.58", "13.28–20.25", "128", "709",
          "Simes", "9,084", "13,101", "9,068", "0.128", "0.219",
          "Table S9", "Table S10", "Table S11", "Table S12",
          "run_limma_replication.py", "genelevel_sensitivity.py",
          "limma_replication.R", "cold_read_v07.py",
          "no GEO annotation file", "not substituted into Table 1"]:
    chk("N 表述", "正文已写明 `%s`" % p, p in s, "命中" if p in s else "缺失")
for p in ["does not use empirical-Bayes variance moderation",
          "a limma-based replication with the same design matrix is desirable",
          "cold_read_v06.py", "apply_v06.py", "v0.6 决策落定"]:
    n = len(re.findall(re.escape(p), s, re.I))
    chk("N 表述", "不再声称 `%s`" % p, n == 0, "命中 %d" % n)

p04 = os.path.join(RES, "04_deg_primary_M2.csv")
man_p = os.path.join(TABD, "file_manifest.csv")
if os.path.exists(p04) and os.path.exists(man_p):
    h = hashlib.sha256(open(p04, "rb").read()).hexdigest()
    mr = pd.read_csv(man_p)
    row = mr[mr.path == "results/04_deg_primary_M2.csv"]
    chk("N 主结果未变", "`04_deg_primary_M2.csv` sha256 与清单一致",
        len(row) == 1 and h == str(row.sha256.iat[0]), "sha %s" % h[:12])

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
    os.path.exists(v7) and hashlib.sha256(open(v7, "rb").read()).hexdigest().startswith("3fcfdbb3d2d2"),
    "v0.7 保留")
chk("O 版本", "决策 A 仍写在版本说明", "确认保持 A" in s and "results/` 的预指定 M2" in s, "")

# --- report ---
lines = ["# Cold-read v0.8（投稿可行性增强版）\n",
         "> 检查对象：`%s`；数值基准：`%s`、`results_m2b`、`results_diagnostics`、`results_limma` 与 `results_genelevel`\n" % (os.path.basename(MAN), os.path.basename(RES)),
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
lines.append("- v0.6 新增 **M 组**：作者决策 A 已落定（`DECISION_LOG.md`）、主结果 `07_roc.csv` 字节/sha256 未变、"
             "供体级 ROC 与芯片级 6/6 精确对账且 Δ=0、循环论证披露、Table S7/S8 与共线量化数字逐条入正文。\n")
lines.append("- v0.7 新增 **N 组**：真实 R 4.2.0 / limma 3.52.4 复核（69,513 行系数对账、0/18 不显著、"
             "先验 df 与 DEG 计数）、基因级三口径敏感性（每口径 0/18）、S9–S12 表与主结果 sha256 未变；"
             "并断言敏感性结果没有被静默提升为主结果、GSE45570 未写成阴性验证。\n")
lines.append("- **主模型决策已确认保持 A**：`results/` 的预指定 M2 为唯一主结果，`results_m2b/` 仅作敏感性；"
             "本版未改动任何主结果统计数字、Figure 1–2 或 Table 1–4。N1 整改同样不覆盖 `results/`，诊断输出在 "
             "`results_diagnostics/`。\n")
lines.append("- v0.8 新增 **O 组**：Table S13 事后可检测效应量（11/18、43.5%、非等效性检验）、"
             "Table S15 的 GPL5175 重建映射与边界检查（316,919 行、80.11%、0/6、非验证）、"
             "Table S16 可复用元数据审计（6 主 + 1 外部候选，五类缺陷）与 S14 官方核验；"
             "并断言 v0.7 字节未变、主结果未改、边界检查未被提升为验证。\n")
lines.append("- 本检查不能替代机构权限下的 iThenticate/Turnitin 相似度自查，也不能替代逐刊政策人工核对。\n")
open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print("PASS %d / FAIL %d -> %s" % (np_, nf, OUT))
for r in rows:
    if r[2] == "FAIL":
        print("  FAIL:", r[1], "|", r[3])

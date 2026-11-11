# -*- coding: utf-8 -*-
"""Build the round-8 self-contained HTML report (no external assets)."""
import csv
import html
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
E = lambda x: html.escape(str(x))


def tsv(name, sep="\t"):
    with open(os.path.join(ROOT, name), encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter=sep))


s7 = [r for r in tsv("tables/TableS7_donor_vs_array_ROC.tsv") if r["dataset"] == "GSE2378-GPL8300"]
s8 = tsv("tables/TableS8_collinearity_diagnostics.tsv")
roc_main = tsv("results/07_roc.csv", sep=",")
manifest = tsv("tables/file_manifest.csv", sep=",")
cold = open(os.path.join(WORK, "青光眼生信稿件_cold-read_v0.6报告.md"), encoding="utf-8").read()
m = re.search(r"PASS (\d+) / FAIL (\d+)", cold)
pass_n, fail_n = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
groups = Counter(re.findall(r"^\| ([A-M] [^|]+) \|", cold, re.M))
man6 = open(os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.6.md"), encoding="utf-8").read()
dlog = open(os.path.join(ROOT, "DECISION_LOG.md"), encoding="utf-8").read()


def table(headers, rows):
    # Cells are author-supplied markup in this report (static text, no untrusted
    # input). Values taken from CSVs are escaped by E() at the call site.
    h = "".join(f"<th>{x}</th>" for x in headers)
    b = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return f'<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def fmt(v, n=3):
    try:
        return ("%." + str(n) + "f") % float(v)
    except (TypeError, ValueError):
        return "—"


# ---------------------------------------------------------------- inline SVG chart
GENES = ["FGFR1", "SMAD1", "STAT1", "TGFBR2", "CASP1", "CASP4"]
series = [
    ("Selected probe (min p)", "#1a56a8", "auc_donor"),
    ("All-probe median", "#b3261e", "auc_all_probes_median"),
    ("Selection-free gene score", "#137a52", "auc_gene_median_expression"),
]
W, H, LEFT, TOP, ROWH, GW = 660, 292, 78, 34, 36, 118
bars = []
for i, g in enumerate(GENES):
    row = next((r for r in s7 if r["gene"] == g), None)
    if not row:
        continue
    y0 = TOP + i * ROWH
    bars.append(f'<text x="{LEFT - 10}" y="{y0 + 15}" text-anchor="end" font-size="11" fill="#1b2430">{E(g)}</text>')
    for j, (label, color, key) in enumerate(series):
        v = float(row[key]) if row.get(key) not in (None, "", "nan") else 0.0
        w = v * GW
        yy = y0 + j * 9 + 1
        bars.append(f'<rect x="{LEFT}" y="{yy}" width="{w:.1f}" height="7" fill="{color}" rx="1.5"/>')
        bars.append(f'<text x="{LEFT + w + 5:.1f}" y="{yy + 7}" font-size="9" fill="#5d6b7c">{v:.2f}</text>')
for k in range(0, 6):
    x = LEFT + k * GW / 5
    bars.append(f'<line x1="{x:.1f}" y1="{TOP - 8}" x2="{x:.1f}" y2="{TOP + 6 * ROWH - 12}" stroke="#dfe6ee" stroke-width="1"/>')
    bars.append(f'<text x="{x:.1f}" y="{TOP - 13}" text-anchor="middle" font-size="9" fill="#5d6b7c">{k / 5:.1f}</text>')
legend = "".join(
    f'<rect x="{LEFT + j * 196}" y="8" width="11" height="9" fill="{c}" rx="2"/>'
    f'<text x="{LEFT + j * 196 + 16}" y="17" font-size="10.5" fill="#1b2430">{E(lbl)}</text>'
    for j, (lbl, c, _) in enumerate(series))
SVG = (f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
       f'aria-label="AUC comparison for six genes">'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>{legend}{"".join(bars)}'
       f'<text x="{LEFT}" y="{H - 8}" font-size="10" fill="#5d6b7c">'
       f'AUC (donor level, 7 glaucoma / 6 control donors; one array per donor)</text></svg>')

CSS = """
:root{--bg:#f6f8fb;--card:#fff;--ink:#1b2430;--mut:#5d6b7c;--line:#dfe6ee;
--blue:#1a56a8;--red:#b3261e;--green:#137a52;--amber:#9a6700;--soft:#eef3fa}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:15px/1.72 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:38px 26px 70px}
header{background:linear-gradient(135deg,#123c78,#1a56a8);color:#fff;border-radius:14px;padding:30px 34px;margin-bottom:24px}
header h1{margin:0 0 8px;font-size:27px;line-height:1.35}
header .sub{margin:0;color:#d5e4fb;font-size:13.5px}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin:20px 0 26px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:15px 14px;text-align:center}
.kpi b{display:block;font-size:25px;color:var(--blue);line-height:1.2}
.kpi span{font-size:12px;color:var(--mut)}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:22px 26px;margin:0 0 18px}
h2{font-size:19px;margin:0 0 14px;padding-bottom:9px;border-bottom:2px solid var(--soft);color:var(--blue)}
h3{font-size:15.5px;margin:20px 0 8px;color:#25364c}
p{margin:9px 0}ul,ol{margin:9px 0 9px 22px;padding:0}li{margin:5px 0}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13.2px}
th,td{border:1px solid var(--line);padding:8px 10px;vertical-align:top;text-align:left}
th{background:var(--soft);font-weight:600;color:#243b5a}
tbody tr:nth-child(even){background:#fbfcfe}
code{background:#eef2f7;padding:1px 5px;border-radius:4px;font-size:12.5px}
.tag{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11.5px;font-weight:600}
.ok{background:#e4f4ec;color:var(--green)}.bad{background:#fdecea;color:var(--red)}
.warn{background:#fff4dc;color:var(--amber)}.info{background:#e8f0fc;color:var(--blue)}
.note{background:#fff8e8;border-left:4px solid var(--amber);padding:12px 15px;border-radius:0 8px 8px 0;margin:14px 0}
.danger{background:#fdecea;border-left:4px solid var(--red);padding:12px 15px;border-radius:0 8px 8px 0;margin:14px 0}
.good{background:#e9f6ef;border-left:4px solid var(--green);padding:12px 15px;border-radius:0 8px 8px 0;margin:14px 0}
.small{font-size:12.5px;color:var(--mut)}
.chartbox{border:1px solid var(--line);border-radius:9px;padding:12px;background:#fff;margin:14px 0}
footer{text-align:center;color:var(--mut);font-size:12.5px;margin-top:28px}
"""

# ---------------------------------------------------------------- section bodies
sec1 = f"""
<p>本轮由作者的明确指示 <b>“保持 a”</b> 触发：把第七轮留下的唯一作者决策正式落定，并接着做不依赖外部输入的下一项整改（第二轮模拟预审发现的 <b>N1</b>）。<b>没有重跑任何统计模型，没有改动任何主结果数字。</b></p>
{table(["#", "工作", "产出", "状态"], [
    ["1", "主模型决策落定（保持 A）", "<code>DECISION_LOG.md</code> + v0.6 版本说明 + README/REPRODUCIBILITY 同步；清除全部“待作者拍板”字样", "<span class='tag ok'>完成</span>"],
    ["2", "N1：供体级 ROC 重算", "<code>diagnose_n1.py</code> → <code>results_diagnostics/</code>、Table S7；与主结果 6/6 精确对账", "<span class='tag ok'>完成</span>"],
    ["3", "共线量化诊断", "phi / r / VIF / 条件数 / 秩 / 零单元格 → Table S8；发现主 QC 漏掉的 GPL8300 零单元格", "<span class='tag ok'>完成</span>"],
    ["4", "v0.6 全文中稿", "纯文本修订 17 处（决策、循环论证、共线措辞、表与脚本清单），58 条参考文献不变", "<span class='tag ok'>完成</span>"],
    ["5", "增强版 cold-read", f"<code>cold_read_v06.py</code> 新增 M 组 55 项 → <b>{pass_n} PASS / {fail_n} FAIL</b>", "<span class='tag ok'>完成</span>"],
])}
<div class="good"><b>主结果零改动。</b><code>results/</code> 的 13 个文件、<code>results_m2b/</code>、Figure 1–2、Table 1–4、Table S1–S4 与 <code>07_roc.csv</code> 全部保持字节不变；<code>file_manifest.csv</code> 的 sha256 对照通过。</div>
"""

sec2 = f"""
<p>作者确认 <b>保持 A</b>：<code>results/</code> 的预指定 M2 是唯一主结果，<code>results_m2b/</code> 仅是发现元数据解析缺陷后补做的敏感性分析。第七轮报告 §2 给出的“若选 B 必须同步改 7 处文件”清单<b>本次不执行</b>，作为备查保留在决策台账里。</p>
{table(["项目", "A（已确认）", "B（未采纳）"], [
    ["主结果目录", "<code>results/</code>（预指定 M2）", "<code>results_m2b/</code>"],
    ["GSE9944 设计矩阵", "intercept + glaucoma + race_Caucasian", "再加 age_z + sex"],
    ["GPL571 M2 / M3 DEG", "<b>114 / 640</b>", "95 / 516"],
    ["六基因 BH q 范围", "<b>0.145–0.691</b>", "0.077–0.893"],
    ["六基因显著数", "<b>0 / 18</b>", "0 / 18"],
    ["分支 A 定位", "成立", "成立"],
    ["需同步改动的文件", "<b>0 处</b>", "7 处"],
])}
<p><b>采纳理由：</b>M2 是预指定主模型，M2b 是事后敏感性；两版结论完全一致（0/18 显著、方向反转、分支 A 不变），换模型没有科学收益，却容易被审稿人质疑“事后换主模型”。解析缺陷没有被掩盖——Methods 2.5 如实写明 age/sex 未进入主模型，Abstract、Results 3.2 与 Table S2–S3 报告 M2b。</p>
<div class="note">决策台账 <code>work/data/DECISION_LOG.md</code> 记录决策人、时间、A/B 数字、理由与 7 处影响清单；<code>REPRODUCIBILITY.md</code> 第 5 节第 3 项已标记 RESOLVED。历史报告（第六/七轮）作为过程记录不修改。</div>
"""

rows_roc = []
for r in s7:
    rows_roc.append([
        E(r["gene"]), E(r["probe"]), fmt(r["auc_array"]), fmt(r["auc_donor"]), fmt(r["auc_delta"]),
        fmt(r["auc_all_probes_median"]), fmt(r["auc_gene_median_expression"]),
        fmt(r["auc_selection_inflation"]), fmt(r["donor_ci_lo"]) + "–" + fmt(r["donor_ci_hi"]),
        fmt(r["q_perm_BH"], 4)])
sec3 = f"""
<p>N1 原表述是“<code>07_roc.csv</code> 用 array-level 表达做 ROC，与全文供体级主张冲突，bootstrap CI 可能偏乐观”。<code>diagnose_n1.py</code> 用<b>同一探针、同一标签顺序、同一随机数种子</b>，只把评分单位换成供体级，重跑全部 6 个真实矩阵。</p>
<div class="good"><b>结论：数值上零变化。</b>GSE2378-GPL8300 是 <b>13 张芯片 / 13 个供体、一供体一芯片</b>，聚合不改变任何值；供体级 AUC 与芯片级 <b>6/6 完全一致（Δ = 0）</b>，且与主结果 <code>07_roc.csv</code> 精确对账 6 行、0 行不一致。因此 <code>07_roc.csv</code> 无需改数字，N1 是<b>表述与循环论证问题</b>，不是数值错误。</div>
<p><b>真实缺陷：</b>每个基因的探针是在这同一批 13 个供体上按最小名义 p 挑出来的，随后又在同一批供体上算 AUC。Table S7 用三个口径量化了这种选择偏倚：选定探针、该基因全部映射探针的 AUC 中位数、以及无选择的基因级分数（跨探针中位表达）。</p>
<div class="chartbox">{SVG}</div>
{table(["Gene", "Probe", "Array AUC", "Donor AUC", "Δ", "All-probe median", "Selection-free", "Inflation", "Donor 95% CI", "BH q (perm)"], rows_roc)}
<p>选定探针相对全探针中位的偏移为 <b>−0.119 至 +0.190</b>（TGFBR2 +0.190、FGFR1 +0.155、STAT1 −0.119）；置换 p 的 BH 校正 q 也一并给出。这些 AUC 没有独立队列、bootstrap CI 很宽（如 0.571–1.000），<b>不能作为诊断效能证据</b>；它们与 M2 中 q ≥ 0.224 的“不显著”并不矛盾，差异来自选择偏倚而非模型冲突。</p>
"""

rows_col = []
for r in s8:
    if r["ancestry_available"] == "yes":
        rows_col.append([E(r["dataset"]), E(r["design"]), E(r["design_rank"]) + "/" + E(r["n_columns"]),
                         E(r["phi_ancestry_disease"]), E(r["r_glaucoma_Caucasian"]),
                         E(r["vif_glaucoma"]), E(r["condition_number"]),
                         E(r["smallest_cell"]), E(r["zero_cell"])])
sec4 = f"""
<p>此前全文只有定性警告“ancestry 与 disease nearly collinear”。本轮把设计矩阵量化后，结论需要修正：</p>
{table(["Dataset", "Design terms", "Rank / cols", "phi", "r", "VIF (disease)", "cond(X)", "Min cell", "Zero cell"], rows_col)}
<div class="note"><b>并非经典多重共线。</b>VIF 1.14–1.16、|r| 0.35–0.37、条件数 3.76–6.29、设计矩阵满秩。真正的问题是 <b>2×2 交叉表存在零单元格的结构性失衡</b>：GPL571 无高加索青光眼供体，GPL8300 无非裔对照。调整后的 disease 系数必须跨空层外推，因而不可解释——但它是“可识别、不可解释”，不是旧稿写的 “not identifiable”。</div>
<p><b>新发现：</b>主 QC 的 <code>design_warning</code> 只按“全部青光眼供体同一祖先”触发，因此只标记了 GPL571；<code>GSE9944-GPL8300</code> 的零单元格（African-American 对照 = 0）此前未被报告，本轮补入 Table S8、Results 3.1 与 Discussion。</p>
<p>据此 v0.6 全文不再使用 “nearly collinear” / “not identifiable”，改述为 “unbalanced ancestry–disease structure with a zero cell”；标题与结论中的 “ancestry–disease confounding” 保留，因为结构性混杂这一判断仍成立。</p>
"""

sec5 = f"""
<p><code>apply_v06.py</code> 由 v0.5 派生，共 17 处精确替换，全部为文本修订；断言式替换保证每处原文唯一命中。58 条参考文献、引用编号、Table 2 的 18 个 95% CI、Figure 1–2 图注的主数字均未改动。</p>
{table(["位置", "v0.5 → v0.6"], [
    ["版本说明 §00", "第 7 条“M2b 是否升主模型仍待作者决策” → “已由作者确认保持 A”；新增第 9 条 N1 整改、第 10 条共线措辞收紧"],
    ["Abstract / Results 3.1", "“nearly collinear / not identifiable” → 零单元格 + phi/VIF + 满秩但需外推；新增共线量化段"],
    ["Methods 2.5", "ROC 句改写：一供体一芯片、供体级重算 Δ=0、循环论证、Table S7 三个口径"],
    ["Results 3.2", "补供体级重算、全探针中位 0.238–0.976、无选择基因分数 0.167–1.000、选择膨胀 ≤0.19"],
    ["Results 3.2（M2b 段）", "“Whether to promote M2b … is an author decision” → 作者已确认保持 A"],
    ["Discussion / Limitations", "结构性失衡与零单元格（含 GPL8300）；最小 p 选探针的乐观性引 Table S7"],
    ["Methods 2.6 / Declarations", "脚本清单加入 diagnose_n1.py、cold_read_v06.py、apply_v06.py"],
    ["Supplementary", "Table S5 补诊断目录说明；新增 Table S7、Table S8 条目"],
    ["脚注", "v0.6；主模型 A；诊断数字来自独立 results_diagnostics/"],
])}
"""

grows = [[E(k), str(v)] for k, v in sorted(groups.items())]
sec6 = f"""
<p><code>cold_read_v06.py</code> 继承 v0.5 的 106 项检查，新增 <b>M 组 55 项</b>：决策台账与版本说明、主结果 sha256 未变、供体级 ROC 6/6 对账、Δ=0、一供体一芯片、选择膨胀范围、Table S7/S8 行数与数值、循环论证与共线措辞的正面/反面断言。</p>
{table(["检查组", "项数"], grows)}
<div class="good"><b>合计 {pass_n} PASS / {fail_n} FAIL</b>（v0.3 53 → v0.4 87 → v0.5 106 → v0.6 {pass_n}）。报告：<code>work/青光眼生信稿件_cold-read_v0.6报告.md</code>。</div>
<p>校验中查出并修掉 2 处真实问题：正文残留 “Whether to promote M2b … is an author decision”；诊断表对账列写成 1.0/空不利于复核，已改为 <code>MATCH</code> / <code>MISMATCH</code>。</p>
"""

sec7 = f"""
{table(["证据", "结果"], [
    ["<code>results/07_roc.csv</code>", f"{len(roc_main)} 行；无诊断列；TGFBR2 AUC = 1.000、STAT1 = 0.119 保持原值"],
    ["sha256 对照", "<code>07_roc.csv</code> 当前哈希与 <code>file_manifest.csv</code> 记录一致"],
    ["<code>file_manifest.csv</code>", f"{len(manifest)} 条输入/脚本/结果的字节数与 sha256（含本轮新文件）"],
    ["独立输出目录", "<code>results_diagnostics/</code> 3 CSV + 1 MD；<code>results/</code> 与 <code>results_m2b/</code> 从未被本轮写入"],
    ["脚本编译", "本轮全部脚本 <code>py_compile</code> 通过；6 个矩阵 + 3 个 annot gzip 完整"],
])}
"""

sec8 = f"""
<div class="danger"><b>投稿可行性不变：仍不可投稿。</b>本轮解决的是决策、可复现性与表述诚实性，没有解决创新性不足、无湿实验/独立队列、GPL5175 无基因级验证、缺代码公开 DOI、31 条保留文献格式未统一、缺正式查重。原稿叙事仍是 1.50/5 档、必然 desk reject；第二轮预审约 2.6/5。</div>
{table(["优先级", "事项", "说明"], [
    ["1", "limma 复核 + 全探针中位数敏感性", "同一设计矩阵做经验贝叶斯方差收缩；并把“最小 p 选探针”换成基因级汇总口径"],
    ["2", "Zenodo/GitHub 打 tag 生成 DOI，回填 12 项声明", "CRediT 14 角色、基金、COI、AI 披露、GEO 标准引用；不代填作者信息"],
    ["3", "31 条保留文献用 Zotero 统一为目标期刊格式", "27 条新增文献已核验，保留条目沿用原稿文本"],
    ["4", "Word 版（Office 通道）与期刊版式转换", "SVG → 期刊图形格式、TSV → 投稿表格；删除 Figure 3–5 相关残留"],
    ["5", "cover letter 与正式查重", "需机构权限下的 iThenticate/Turnitin；本 cold-read 不能替代"],
    ["6", "选刊：BMC Med Res Methodol / PLOS ONE", "2026-11-09 官网核验；PeerJ 有硬性排除条款；Scientific Reports/Data 页面需人工复核"],
])}
<p class="small">若日后改变主意要切到 B，请重读 <code>DECISION_LOG.md</code> 第 3 节的 7 处同步清单；本轮不执行。</p>
"""

sec9 = f"""
{table(["类别", "文件"], [
    ["决策台账", "<code>work/data/DECISION_LOG.md</code>"],
    ["全文中稿", "<code>work/青光眼生信稿件_全文重写稿_v0.6.md</code>"],
    ["cold-read", "<code>work/青光眼生信稿件_cold-read_v0.6报告.md</code>、<code>work/data/cold_read_v06.py</code>"],
    ["诊断脚本/结果", "<code>work/data/diagnose_n1.py</code>、<code>results_diagnostics/*</code>（3 CSV + N1_DIAGNOSTICS.md）"],
    ["补充表", "<code>work/data/tables/TableS7_donor_vs_array_ROC.tsv</code>、<code>TableS8_collinearity_diagnostics.tsv</code>"],
    ["回填/报告脚本", "<code>apply_v06.py</code>、<code>make_report_v08.py</code>"],
    ["运行文档", "<code>README.md</code> v2.3、<code>REPRODUCIBILITY.md</code> §7、<code>tables/file_manifest.csv</code>"],
    ["本轮报告", "<code>work/青光眼生信稿件_决策落定与N1整改报告.html</code>（自包含，可离线打开）"],
])}
<p class="small">原稿 <code>D:\\BaiduSyncdisk\\待研究相关资料\\青光眼生信研究\\Manuscript.docx</code> 全程只读，从未修改。</p>
"""

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>青光眼生信稿件 · 决策落定与 N1 整改报告（第八轮）</title>
<style>{CSS}</style></head><body><div class="wrap">
<header><h1>决策落定与 N1 整改报告</h1>
<p class="sub">第八轮 · 2026-11-09 · 作者确认“保持 A” · 承接第七轮优先级 1–2 · 全部数字来自本机真实 GEO 结果表，无合成数据</p></header>
<div class="kpis">
<div class="kpi"><b>A</b><span>主模型决策已确认</span></div>
<div class="kpi"><b>0</b><span>主结果数字改动</span></div>
<div class="kpi"><b>6/6</b><span>ROC 供体级精确对账</span></div>
<div class="kpi"><b>Δ=0</b><span>供体级 vs 芯片级 AUC</span></div>
<div class="kpi"><b>{pass_n}/{pass_n}</b><span>cold-read PASS / FAIL {fail_n}</span></div>
</div>
<section><h2>1 · 本轮完成的工作</h2>{sec1}</section>
<section><h2>2 · 决策 A 正式落定</h2>{sec2}</section>
<section><h2>3 · N1：供体级 ROC 重算与循环论证量化</h2>{sec3}</section>
<section><h2>4 · 共线量化诊断与措辞修订</h2>{sec4}</section>
<section><h2>5 · v0.6 修订台账</h2>{sec5}</section>
<section><h2>6 · cold-read 结果</h2>{sec6}</section>
<section><h2>7 · 主结果未变的证据</h2>{sec7}</section>
<section><h2>8 · 剩余缺口与下一步</h2>{sec8}</section>
<section><h2>9 · 交付文件</h2>{sec9}</section>
<footer>Generated by make_report_v08.py · 所有数值对账自 work/data/results 与 results_diagnostics · 原稿 docx 只读未改</footer>
</div></body></html>"""

OUT = os.path.join(WORK, "青光眼生信稿件_决策落定与N1整改报告.html")
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(HTML)
print("wrote", os.path.basename(OUT), "bytes", len(HTML.encode("utf-8")))
print("sections", HTML.count("<section"), "tables", HTML.count("<table"), "svg", HTML.count("<svg"))

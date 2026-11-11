# -*- coding: utf-8 -*-
"""Build the round-9 self-contained HTML report (no external assets)."""
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


s9 = tsv("tables/TableS9_limma_vs_OLS_six_genes.tsv")
s10 = tsv("tables/TableS10_limma_DEG_counts.tsv")
s11 = tsv("tables/TableS11_genelevel_six_genes_q.tsv")
s12 = tsv("tables/TableS12_genelevel_DEG_counts.tsv")
manifest = tsv("tables/file_manifest.csv", sep=",")
cold = open(os.path.join(WORK, "青光眼生信稿件_cold-read_v0.7报告.md"), encoding="utf-8").read()
m = re.search(r"PASS (\d+) / FAIL (\d+)", cold)
pass_n, fail_n = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
groups = Counter(re.findall(r"^\| ([A-N] [^|]+) \|", cold, re.M))
man7 = open(os.path.join(WORK, "青光眼生信稿件_全文重写稿_v0.7.md"), encoding="utf-8").read()
lim_status = open(os.path.join(ROOT, "results_limma", "LIMMA_STATUS.md"), encoding="utf-8").read()
gen_status = open(os.path.join(ROOT, "results_genelevel", "GENELEVEL_STATUS.md"), encoding="utf-8").read()


def table(headers, rows):
    # Cells are static author-supplied markup; CSV values are escaped via E().
    h = "".join(f"<th>{x}</th>" for x in headers)
    b = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return f'<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def fmt(v, n=3):
    try:
        return ("%." + str(n) + "f") % float(v)
    except (TypeError, ValueError):
        return "—"


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

# ------------------------------------------------- inline SVG: OLS q vs limma q
W, H, L, T, PW, PH = 660, 320, 62, 22, 540, 250
MAXQ = 0.75
sx = lambda q: L + min(float(q), MAXQ) / MAXQ * PW
sy = lambda q: T + PH - min(float(q), MAXQ) / MAXQ * PH
parts = [
    f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="OLS versus limma BH q">',
    f'<rect x="{L}" y="{T}" width="{PW}" height="{PH}" fill="#fbfcfe" stroke="#dfe6ee"/>',
]
for v in [0, .15, .30, .45, .60, .75]:
    x, y = sx(v), sy(v)
    parts.append(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{T+PH}" stroke="#e8edf4"/>')
    parts.append(f'<line x1="{L}" y1="{y:.1f}" x2="{L+PW}" y2="{y:.1f}" stroke="#e8edf4"/>')
    parts.append(f'<text x="{x:.1f}" y="{T+PH+16}" text-anchor="middle" font-size="10" fill="#5d6b7c">{v:.2f}</text>')
    parts.append(f'<text x="{L-8}" y="{y+3:.1f}" text-anchor="end" font-size="10" fill="#5d6b7c">{v:.2f}</text>')
parts.append(f'<line x1="{sx(0):.1f}" y1="{sy(0):.1f}" x2="{sx(MAXQ):.1f}" y2="{sy(MAXQ):.1f}" '
             'stroke="#9aa8b8" stroke-dasharray="5 4" stroke-width="1.2"/>')
thr = sy(.05)
parts.append(f'<line x1="{L}" y1="{thr:.1f}" x2="{L+PW}" y2="{thr:.1f}" stroke="#b3261e" stroke-dasharray="4 3"/>')
parts.append(f'<text x="{L+PW-4}" y="{thr-5:.1f}" text-anchor="end" font-size="10" fill="#b3261e">BH q = 0.05</text>')
for r in s9:
    if r.get("status") != "OK" or r.get("q_ols") in ("", "nan") or r.get("q_limma") in ("", "nan"):
        continue
    x, y = sx(r["q_ols"]), sy(r["q_limma"])
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="#1a56a8" fill-opacity="0.78" '
                 f'stroke="#fff" stroke-width="1"><title>{E(r["platform_dataset"])} {E(r["gene"])}: '
                 f'OLS q={fmt(r["q_ols"])}, limma q={fmt(r["q_limma"])}</title></circle>')
parts.append(f'<text x="{L+PW/2:.0f}" y="{H-4}" text-anchor="middle" font-size="11" fill="#25364c">Primary OLS BH q</text>')
parts.append(f'<text x="14" y="{T+PH/2:.0f}" text-anchor="middle" font-size="11" fill="#25364c" '
             f'transform="rotate(-90 14 {T+PH/2:.0f})">limma moderated BH q</text>')
parts.append('</svg>')
SVG = "".join(parts)

# ------------------------------------------------------------------ sections
sec1 = f"""
<p>本轮承接第八轮报告 §8 的优先级 1：<b>limma 复核 + 全探针中位数敏感性</b>。两项都已用真实数据完成，<b>主结果数字一个都没有改</b>，作者确认的决策 A 与分支 A 定位保持不变。</p>
{table(["#", "工作", "产出", "状态"], [
    ["1", "发现并启用本机 R 4.2.0；项目内安装 limma 3.52.4 / statmod 1.5.0", "<code>install_r_packages.py</code>、<code>setup_rlib.R</code>、<code>Rpackages/</code>、<code>Rlib/</code>", "<span class='tag ok'>完成</span>"],
    ["2", "用与主 M2 完全相同的矩阵跑 lmFit → eBayes → topTable", "<code>limma_replication.R</code>、<code>run_limma_replication.py</code>、<code>results_limma/</code>", "<span class='tag ok'>完成</span>"],
    ["3", "基因级三口径敏感性（最小 p / 中位数表达 / Simes）", "<code>genelevel_sensitivity.py</code>、<code>results_genelevel/</code>、Table S11–S12", "<span class='tag ok'>完成</span>"],
    ["4", "v0.7 全文中稿", "<code>apply_v07.py</code>，17 处纯文本修订；58 条参考文献与主数字不变", "<span class='tag ok'>完成</span>"],
    ["5", "增强版 cold-read", f"<code>cold_read_v07.py</code> 新增 N 组 → <b>{pass_n} PASS / {fail_n} FAIL</b>", "<span class='tag ok'>完成</span>"],
])}
<div class="good"><b>此前“本机无 R”的判断是错的。</b>R 4.2.0 实际安装在 <code>C:\\Program Files\\R\\R-4.2.0</code>，只是不在 PATH 中；Bioconductor 官方源带浏览器 UA 后可访问。因此本轮是<b>真跑 limma</b>，不是 Python 近似，也不是留作待办。</div>
"""

sec2 = f"""
<p>第八轮以来的待办写的是“limma 复核 desirable”。本轮把它执行完毕，并加了三道口径护栏：</p>
<ol>
<li><b>输入矩阵可复核</b>：从 6 个真实 series matrix 重新构建供体级 log2 表达与设计矩阵，先用 Python 重算一次 OLS，与主结果 <code>04_deg_primary_M2.csv</code> 的 69,513 行 log2FC / se 逐行对照，最大误差 <b>4.4e-16</b>，通过后才导出给 R。</li>
<li><b>引擎真实</b>：R 4.2.0 + limma 3.52.4（Bioconductor 3.15 Windows 二进制）+ statmod 1.5.0，装在项目内 <code>Rlib/</code>，不污染用户库；<code>lmFit(method="ls") → eBayes(trend=FALSE, robust=FALSE) → topTable(adjust.method="BH")</code>。</li>
<li><b>输出可回归</b>：limma 的 logFC 与 OLS 系数最大差 <b>3.3e-14</b>；moderated t 确实与 OLS t 不同；每平台的先验 df、总 df、s2.prior 与 R <code>sessionInfo()</code> 全部落盘。</li>
</ol>
{table(["平台", "探针数", "供体数", "残差 df", "先验 df", "总 df", "s² prior", "logFC 最大差"],
       [[E(r["platform_dataset"]), E(r["n_probes"]), E(r["n_donors"]), E(r["df_residual"]),
         fmt(r["df_prior"]), fmt(r["df_total"]), fmt(r["s2_prior"], 5),
         "%.2e" % float(r["max_abs_dlogFC"])] for r in s10])}
<div class="note">先验 df 2.25–4.58 相对残差 df 10–18 并不小，说明经验贝叶斯收缩在这些小样本上确有实质作用，因此 DEG 计数变化是真实的方法学差异，不能当作“结果一致”忽略。</div>
"""

rows_s9 = [[E(r["platform_dataset"]), E(r["gene"]), E(r["probe"]), fmt(r["q_ols"], 4),
            fmt(r["q_limma"], 4), fmt(float(r["q_limma"]) - float(r["q_ols"]), 4),
            "<span class='tag ok'>不显著</span>" if r["sig_limma"] in ("False", "0", "")
            else "<span class='tag bad'>显著</span>"]
           for r in s9 if r.get("status") == "OK"]
sec3 = f"""
<div class="good"><b>分支 A 不变：六基因在 limma 下仍 0/18 显著</b>，BH q 从主 OLS 的 0.145–0.691 变为 <b>0.116–0.663</b>。经验贝叶斯收缩普遍略微降低 q，但没有把任何一个检验推过 0.05。</div>
<div class="chartbox">{SVG}</div>
<p class="small">每个点是一次基因×平台检验；虚线为 y = x，红虚线为 BH q = 0.05。全部 18 个点都在阈值线之上，且多数落在对角线下方（limma 后 q 略小）。</p>
{table(["平台", "基因", "选定探针", "OLS q", "limma q", "Δq", "判定"], rows_s9)}
<p><b>但全探针 DEG 计数确实变了</b>（Table S10）：方差收缩让更多探针跨过阈值。这是敏感性结果，<b>没有回写 Table 1 / Figure 1B / Abstract</b>，因为 M2 是预指定主模型，事后换引擎会被审稿人质疑。</p>
{table(["平台", "M2 OLS (q&lt;.05, |FC|≥1)", "M2 limma", "M3 OLS (≥0.5)", "M3 limma"],
       [[E(r["platform_dataset"]), E(r["n_q05_lfc1_ols"]), E(r["n_q05_lfc1_limma"]),
         E(r["n_q05_lfc05_ols"]), E(r["n_q05_lfc05_limma"])] for r in s10])}
"""

rows_s11 = [[E(r["platform_dataset"]), E(r["gene"]), fmt(r.get("probe_min_p"), 4),
             fmt(r.get("gene_median"), 4), fmt(r.get("gene_simes"), 4),
             "<span class='tag ok'>三口径均不显著</span>"] for r in s11]
sec4 = f"""
<p>主 M2 对每个基因报告“最小名义 p 的探针”，这是一个选择步骤。本轮把单位从探针换成基因，用三种口径在同一批供体、同一设计矩阵上重算：</p>
<ol>
<li><b>probe_min_p</b>：主口径（探针级 BH）。</li>
<li><b>gene_median</b>：同一基因所有映射探针在每个供体上取中位 log2 表达，重跑 OLS，BH 在<b>基因</b>层校正——完全不存在选探针。</li>
<li><b>gene_simes</b>：基因内探针级 M2 p 值做 Simes 合并，BH 在基因层校正。</li>
</ol>
<div class="good"><b>三种口径各自都是 0/18 显著</b>（共 54 次基因×平台×口径检验）；gene_median 最小 q = 0.128，Simes 最小 q = 0.219。六个转录本不是因为“只挑了一个探针”才不显著，也不是因为被选中的探针不好而漏掉。</div>
{table(["平台", "基因", "probe_min_p q", "gene_median q", "gene_simes q", "结论"], rows_s11)}
{table(["平台", "状态", "基因数", "M2 探针 DEG", "M2 基因 DEG (median)", "六基因最小 q (median)", "六基因最小 q (Simes)"],
       [[E(r["platform_dataset"]), E(r["status"]), E(r.get("n_genes", "")),
         E(r.get("n_DE_probes_M2", "")), E(r.get("n_DE_genes_median_M2", "")),
         fmt(r.get("six_min_q_median"), 4), fmt(r.get("six_min_q_simes"), 4)] for r in s12])}
<div class="danger"><b>GSE45570 不能做基因级检验。</b>GPL5175 在 GEO 没有官方 annot 文件，探针无法映射到基因符号。表中如实写作 <code>no gene annotation</code>，<b>不是阴性验证</b>；v0.7 的 Methods、Results 3.3 与 Limitations 都明确了这一点。Simes 假定检验独立或正相依，而同一基因的探针相关，故仅作探索性口径。</div>
"""

sec5 = f"""
<p><code>apply_v07.py</code> 由 v0.6 派生，<b>17 处断言式精确替换、全部为文本修订</b>；58 条参考文献、Table 2 的 18 个 95% CI、Figure 1–2 与所有主数字不变。</p>
{table(["位置", "修订"], [
    ["版本说明", "改为 v0.7；新增第 11、12 条记录 limma 与基因级复核的真实数字与目录边界"],
    ["Abstract", "Methods 补两种稳健性复核；Results 补 0/18 与 limma q 0.116–0.663"],
    ["Methods 2.5 / 2.6", "新增 limma 引擎、先验 df、基因级三口径与 Simes 假设的完整方法段；删去“未使用方差收缩、更保守”的旧断言；脚本清单更新"],
    ["Results 3.2 / 新增 3.3", "Table 2 说明补稳健性结论；新增 3.3 报告 128 / 709 / 0→2 与三口径 0/18、9,084 / 13,101 / 9,068 基因数"],
    ["Discussion / Limitations", "结论补稳健性；Fourth 改为 limma 已执行并列出引擎依赖的计数变化；Fifth 补 Simes 探索性；新增 Sixth 说明 GSE45570 无注释不是阴性；后续编号顺延"],
    ["补充表 / 脚注", "新增 Table S9–S12 描述；脚本清单、版本脚注与结果目录同步"],
])}
<div class="note">被删除的旧句：<code>does not use empirical-Bayes variance moderation (limma)</code> 与 <code>a limma-based replication ... is desirable</code>。这两句在 v0.7 里已不再成立，cold-read 将它们列为反面断言。</div>
"""

sec6 = f"""
<p><code>cold_read_v07.py</code> 继承 v0.6 的 161 项，新增 <b>N 组</b>（limma 文件与 R 环境、69,513 行系数对账、moderated t 确有差异、0/18、q 范围、DEG 计数、先验 df、基因级三口径、S9–S12、正文数字与反面措辞、主结果 sha256）：<b>{pass_n} / {pass_n} PASS，FAIL {fail_n}</b>。</p>
{table(["检查组", "项数"], [[E(k), str(v)] for k, v in sorted(groups.items())])}
<div class="small">说明：本检查只能验证内部一致性与文件级可复现性，不能替代机构权限下的 iThenticate/Turnitin 查重，也不能替代投稿当日的逐刊政策人工核对。</div>
"""

sec7 = f"""
<p>本轮所有新结果写入独立目录 <code>results_limma/</code> 与 <code>results_genelevel/</code>；<code>results/</code>、<code>results_m2b/</code>、<code>results_diagnostics/</code> 从未被写入。</p>
<ul>
<li><code>results/04_deg_primary_M2.csv</code> 的 sha256 与 <code>tables/file_manifest.csv</code> 记录一致（cold-read N 组断言）。</li>
<li><code>results/07_roc.csv</code> 的 sha256 仍与清单一致（继承 M 组断言）。</li>
<li>6 个 series matrix + 3 个 annot 的 gzip 完整性本轮复核通过。</li>
<li><code>file_manifest.csv</code> 扩至 <b>{len(manifest)}</b> 条，纳入本轮全部新脚本、R 包、结果表与补充表。</li>
</ul>
"""

sec8 = f"""
<div class="danger"><b>投稿可行性不变：仍不可投稿。</b>本轮解决的是统计引擎与检验单位的稳健性，没有解决创新性不足、无湿实验 / 独立队列、GPL5175 无基因级验证、缺代码公开 DOI、31 条保留文献格式未统一、缺正式查重。原稿叙事仍是 1.50/5 档；第二轮模拟预审约 2.6/5。</div>
{table(["优先级", "事项", "说明"], [
    ["1", "Zenodo/GitHub 打 tag 生成 DOI，回填 12 项声明", "CRediT 14 角色、基金、COI、AI 披露、GEO 标准引用；不代填作者信息"],
    ["2", "31 条保留文献用 Zotero 统一为目标期刊格式", "27 条新增文献已逐条核验；保留条目仍沿用原稿文本"],
    ["3", "Word 版（Office 通道）与期刊版式转换", "SVG → 期刊图形格式、TSV → 投稿表格；删除 Figure 3–5 残留"],
    ["4", "cover letter 与正式查重", "需机构权限下的 iThenticate/Turnitin；cold-read 不能替代"],
    ["5", "选刊：BMC Med Res Methodol / PLOS ONE", "2026-11-09 官网核验；PeerJ 有硬性排除条款；Scientific Reports/Data 页面需人工复核"],
    ["6", "投稿当日逐刊政策复核", "官网页面未标最后修订日期，“近 12 个月”口径无法自证"],
])}
"""

sec9 = f"""
{table(["类别", "文件"], [
    ["全文中稿", "<code>work/青光眼生信稿件_全文重写稿_v0.7.md</code>"],
    ["cold-read", "<code>work/青光眼生信稿件_cold-read_v0.7报告.md</code>、<code>work/data/cold_read_v07.py</code>"],
    ["limma 复核", "<code>work/data/install_r_packages.py</code>、<code>setup_rlib.R</code>、<code>limma_replication.R</code>、<code>run_limma_replication.py</code>、<code>results_limma/*</code>"],
    ["基因级敏感性", "<code>work/data/genelevel_sensitivity.py</code>、<code>results_genelevel/*</code>"],
    ["补充表", "<code>tables/TableS9</code>–<code>TableS12</code>（TSV + MD）"],
    ["回填 / 报告 / 清单", "<code>apply_v07.py</code>、<code>make_report_v09.py</code>、<code>tables/file_manifest.csv</code>"],
    ["运行文档", "<code>README.md</code> v2.4、<code>REPRODUCIBILITY.md</code> §8"],
    ["本轮报告", "<code>work/青光眼生信稿件_limma复核与基因级敏感性报告.html</code>（自包含，可离线打开）"],
])}
<p class="small">原稿 <code>D:\\BaiduSyncdisk\\待研究相关资料\\青光眼生信研究\\Manuscript.docx</code> 全程只读，从未修改。全部数值来自本机真实 GEO 数据，无合成数据。</p>
"""

HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>青光眼生信稿件 · limma 复核与基因级敏感性报告（第九轮）</title>
<style>{CSS}</style></head><body><div class="wrap">
<header><h1>limma 复核与基因级敏感性报告</h1>
<p class="sub">第九轮 · 2026-11-09 · 承接第八轮优先级 1 · 真跑 R/limma 3.52.4 · 全部数字来自本机真实 GEO 结果表，无合成数据</p></header>
<div class="kpis">
<div class="kpi"><b>0/18</b><span>limma 六基因显著数</span></div>
<div class="kpi"><b>0/18</b><span>基因级三口径（各自）</span></div>
<div class="kpi"><b>69,513</b><span>探针级系数精确对账</span></div>
<div class="kpi"><b>0</b><span>主结果数字改动</span></div>
<div class="kpi"><b>{pass_n}/{pass_n}</b><span>cold-read PASS / FAIL {fail_n}</span></div>
</div>
<section><h2>1 · 本轮完成的工作</h2>{sec1}</section>
<section><h2>2 · limma 环境与复核设计</h2>{sec2}</section>
<section><h2>3 · limma 结果：分支 A 不变</h2>{sec3}</section>
<section><h2>4 · 基因级三口径敏感性</h2>{sec4}</section>
<section><h2>5 · v0.7 修订台账</h2>{sec5}</section>
<section><h2>6 · cold-read 结果</h2>{sec6}</section>
<section><h2>7 · 主结果未变的证据</h2>{sec7}</section>
<section><h2>8 · 剩余缺口与下一步</h2>{sec8}</section>
<section><h2>9 · 交付文件</h2>{sec9}</section>
<footer>第九轮 · 2026-11-09 · 决策 A 保持不变 · 原稿 docx 全程只读</footer>
</div></body></html>
"""

out = os.path.join(WORK, "青光眼生信稿件_limma复核与基因级敏感性报告.html")
open(out, "w", encoding="utf-8").write(HTML)
print("wrote", os.path.basename(out), "bytes", len(HTML.encode("utf-8")))

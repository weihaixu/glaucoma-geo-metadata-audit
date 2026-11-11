#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the self-contained round-6 HTML report (figures embedded as base64)."""
import os
import re
import base64
import html
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
FIG = os.path.join(ROOT, "figures")
TAB = os.path.join(ROOT, "tables")
OUT = os.path.join(WORK, "青光眼生信稿件_图表补齐与事实一致性报告.html")


def img(name):
    p = os.path.join(FIG, name)
    b = base64.b64encode(open(p, "rb").read()).decode("ascii")
    return '<img src="data:image/png;base64,%s" alt="%s" style="width:100%%;border:1px solid #e3e8ee;border-radius:8px;">' % (b, name)


def table(stem, limit=None, caption=""):
    df = pd.read_csv(os.path.join(TAB, stem + ".tsv"), sep="\t")
    if limit:
        df = df.head(limit)
    t = df.to_html(index=False, escape=True, border=0, justify="left")
    return ('<div class="tablewrap">' + t + '</div>'
            + ('<p class="small">%s</p>' % caption if caption else ''))


def md_report_excerpt():
    p = os.path.join(WORK, "青光眼生信稿件_cold-read_v0.4报告.md")
    s = open(p, encoding="utf-8").read()
    m = re.search(r"\*\*合计 (\d+) 项：PASS (\d+) / FAIL (\d+)\*\*", s)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (0, 0, 0)


total, passed, failed = md_report_excerpt()
man = pd.read_csv(os.path.join(TAB, "file_manifest.csv"))
n_input = int((man.kind == "input/script").sum())
n_res = int((man.kind == "result").sum())
n_sens = int((man.kind == "sensitivity").sum())

CSS = """
:root{--bg:#f7f8fa;--card:#fff;--ink:#1f2933;--muted:#5c6b7a;--line:#e3e8ee;
--accent:#2b5c8a;--accent-soft:#eaf1f8;--red:#b3382c;--red-soft:#fdeceb;
--amber:#a9701a;--amber-soft:#fdf4e3;--green:#2b7050;--green-soft:#e9f4ee;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Segoe UI","Microsoft YaHei","PingFang SC",Arial,sans-serif;font-size:14.5px;line-height:1.75;}
.wrap{max-width:1120px;margin:0 auto;padding:36px 28px 80px;}
header{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:30px 34px;margin-bottom:22px;border-top:4px solid var(--accent);}
h1{margin:0 0 8px;font-size:25px;letter-spacing:.3px;}
.sub{color:var(--muted);font-size:13.5px;margin:0;}
.meta{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px;}
.pill{background:var(--accent-soft);color:var(--accent);border-radius:20px;padding:4px 12px;font-size:12.5px;font-weight:600;}
.pill.bad{background:var(--red-soft);color:var(--red);}
.pill.warn{background:var(--amber-soft);color:var(--amber);}
.pill.ok{background:var(--green-soft);color:var(--green);}
.verdict{margin-top:18px;padding:16px 18px;background:var(--amber-soft);border-left:4px solid var(--amber);border-radius:0 8px 8px 0;font-size:14.6px;}
.verdict b{color:var(--amber);}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:26px 32px;margin-bottom:20px;}
h2{font-size:19px;margin:0 0 16px;padding-bottom:10px;border-bottom:1px solid var(--line);color:var(--accent);}
h3{font-size:15.5px;margin:22px 0 8px;color:var(--ink);}
p{margin:9px 0;} ul,ol{margin:9px 0;padding-left:22px;} li{margin:5px 0;}
.tablewrap{overflow-x:auto;margin:10px 0 18px;}
table{width:100%;border-collapse:collapse;font-size:12.6px;}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top;white-space:nowrap;}
th{background:#f1f5f9;font-weight:600;} tr:nth-child(even) td{background:#fbfcfd;}
.tag{display:inline-block;border-radius:4px;padding:1px 7px;font-size:11.5px;font-weight:700;white-space:nowrap;}
.tag.s{background:var(--red-soft);color:var(--red);} .tag.e{background:var(--amber-soft);color:var(--amber);}
.tag.ok{background:var(--green-soft);color:var(--green);}
.box{border-radius:8px;padding:14px 18px;margin:14px 0;font-size:13.6px;}
.box.note{background:var(--accent-soft);border-left:4px solid var(--accent);}
.box.good{background:var(--green-soft);border-left:4px solid var(--green);}
.box.caution{background:var(--amber-soft);border-left:4px solid var(--amber);}
.box.bad{background:var(--red-soft);border-left:4px solid var(--red);}
code{background:#eef2f6;padding:1px 5px;border-radius:3px;font-size:12.5px;font-family:Consolas,Monaco,monospace;}
.small{font-size:12.6px;color:var(--muted);}
.kpi{display:flex;flex-wrap:wrap;gap:14px;margin:16px 0;}
.kpi div{flex:1;min-width:150px;background:var(--accent-soft);border-radius:10px;padding:12px 14px;border:1px solid #d7e4f0;}
.kpi b{display:block;font-size:22px;color:var(--accent);line-height:1.3;} .kpi span{font-size:12.3px;color:var(--muted);}
.kpi .danger{background:var(--red-soft);border-color:#f3d2ce;} .kpi .danger b{color:var(--red);}
.kpi .good{background:var(--green-soft);border-color:#cfe7d9;} .kpi .good b{color:var(--green);}
.toc{columns:2;column-gap:36px;font-size:13.5px;} .toc a{color:var(--accent);text-decoration:none;}
pre{background:#f4f7fa;border:1px solid var(--line);border-radius:8px;padding:14px 16px;overflow-x:auto;font-size:12.3px;line-height:1.6;}
"""

H = []
H.append('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">')
H.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
H.append('<title>青光眼生信稿件 · 图表补齐与事实一致性报告</title>')
H.append('<style>' + CSS + '</style>\n</head>\n<body>\n<div class="wrap">')
H.append('''<header>
  <h1>青光眼生信稿件 · 图表补齐与事实一致性报告</h1>
  <p class="sub">第六轮 · 2026-11-09 · 承接第五轮第 7 节"补齐图与表；95%% CI 与全探针报告" · 所有数值来自本机真实 GEO 结果表，无合成数据</p>
  <div class="meta">
    <span class="pill ok">Figure 1–2 已重绘（PNG + SVG）</span>
    <span class="pill ok">Table 1–4 + S1–S4 已生成</span>
    <span class="pill ok">M2b 敏感性已跑</span>
    <span class="pill ok">cold-read %d/%d PASS</span>
    <span class="pill bad">仍不可投稿</span>
  </div>
  <div class="kpi">
    <div><b>2 + 8</b><span>真实图（4 个文件）与表格（TSV）</span></div>
    <div><b>61</b><span>全探针逐条 95%% CI</span></div>
    <div class="danger"><b>0 / 18</b><span>M2b 六基因 × 三平台显著数</span></div>
    <div class="good"><b>%d / %d</b><span>增强版 cold-read 通过</span></div>
    <div><b>35</b><span>带 sha256 的文件清单条目</span></div>
  </div>
  <div class="verdict">
    <b>本轮结论：图表与统计量已补齐，但发现并修正了三处"写已做、实未做"的事实不一致。</b>
    主模型实际只校正了 ancestry（不是 ancestry/age/sex）；GPL5175 平台表映射未完成却写成已完成；敏感性网格从未导出。
    三处已据实改入 v0.4，并另跑协变量完整的 M2b 敏感性模型：<strong>六基因仍是 0/18 不显著，分支 A 稳健</strong>。
    稿件完整性提高，但<strong>投稿可行性判断不变：仍不可投稿</strong>——缺代码公开 DOI、文献重排、湿实验/独立队列与正式查重。
  </div>
</header>''' % (passed, total, passed, total))

# --- 1
H.append('''<section id="s1"><h2>1 · 本轮完成的六项工作</h2>
<div class="toc">
  <a href="#s1">1 本轮完成</a><br><a href="#s2">2 事实一致性审计</a><br>
  <a href="#s3">3 Figure 1</a><br><a href="#s4">4 Figure 2</a><br>
  <a href="#s5">5 期刊级表格</a><br><a href="#s6">6 M2b 敏感性</a><br>
  <a href="#s7">7 可复现清单</a><br><a href="#s8">8 cold-read</a><br>
  <a href="#s9">9 投稿判断与下一步</a><br><a href="#s10">10 交付文件</a>
</div>
<table><tr><th>#</th><th>任务</th><th>产出</th><th>状态</th></tr>
<tr><td>1</td><td>用 results/*.csv 重绘 Figure 1–2</td><td><code>figures/Figure1.png/.svg</code>、<code>Figure2.png/.svg</code>（300 dpi，英文标注）</td><td><span class="tag ok">完成</span></td></tr>
<tr><td>2</td><td>排 Table 1–2 并补残差自由度、每组 n、95%% CI、全探针</td><td><code>Table1</code>–<code>Table4</code> + <code>TableS1</code>（61 探针逐条 CI）</td><td><span class="tag ok">完成</span></td></tr>
<tr><td>3</td><td>自由文本年龄/性别未进入模型 → 补跑 M2b</td><td><code>reanalysis_m2b.py</code>、<code>results_m2b/</code>、Table S2–S3</td><td><span class="tag ok">完成</span></td></tr>
<tr><td>4</td><td>敏感性网格未导出 → 从探针级 M2 结果重算</td><td><code>TableS4_sensitivity_grid.tsv</code>（4×2×3×2 = 48 行）</td><td><span class="tag ok">完成</span></td></tr>
<tr><td>5</td><td>可复现清单与环境锁定</td><td><code>REPRODUCIBILITY.md</code>、<code>file_manifest.csv</code>（35 条 sha256）、README v2.1</td><td><span class="tag ok">完成</span></td></tr>
<tr><td>6</td><td>回填 v0.4 并重跑 cold-read</td><td><code>全文重写稿_v0.4.md</code>、<code>cold-read_v0.4报告.md</code>（%d 项全过）</td><td><span class="tag ok">完成</span></td></tr>
</table>
<div class="box note">本轮<strong>没有</strong>改动主结果 <code>results/</code>：<code>reanalysis.py</code> 保持原样，M2b 是独立输出目录，保证第五轮数字可原样复跑。</div>
</section>''' % total)

# --- 2
H.append('''<section id="s2"><h2>2 · 事实一致性审计：三处修订 + 一处口径更正</h2>
<p>对账方式：把 v0.3 的 Methods / Abstract 逐句与 <code>02_qc_summary.csv</code>、<code>01_sample_metadata.csv</code>、<code>08_sensitivity.csv</code>、<code>fetch_5175.log</code> 比对。以下四处都不是文字润色，而是"把未执行的事写成已执行"。</p>
<table><tr><th>问题</th><th>v0.3 表述</th><th>结果表证据</th><th>v0.4 处理</th></tr>
<tr><td><span class="tag s">严重</span> 协变量 overclaim</td><td>Abstract / Methods 2.5：M2 校正 "ancestry, age and sex"</td><td><code>adjustment_terms = intercept,glaucoma,race_Caucasian</code>；<code>01_sample_metadata.csv</code> 中 age_num / sex_bin 可用率为 <strong>0/96</strong>。GSE9944 把三项写进一条自由文本 characteristics，结构化列解析失败</td><td>改为如实写明"只拟合 ancestry"；新增 M2b 敏感性（含 age_z、sex），结论不变</td></tr>
<tr><td><span class="tag s">严重</span> GPL5175 映射</td><td>Methods 2.2 / Declarations：平台表"已提取并转成两列格式"</td><td><code>02_qc_summary.csv</code>：GSE45570 <code>MISSING - no gene symbols</code>、<code>n_probes_mapped = 0</code>；<code>fetch_5175.log</code> 停在 chunk 70、<code>table_end=False</code></td><td>改为 "extraction was not completed"，六基因保持 <code>probe not mapped</code>，明确禁止写成阴性验证</td></tr>
<tr><td><span class="tag e">中等</span> 敏感性网格</td><td>Methods 2.5：变动过 alpha / |log2FC| / FDR</td><td><code>08_sensitivity.csv</code> 与 <code>03_deg_by_model.csv</code> 逐行相同（16 行）；代码里的网格算了但没导出</td><td>从 <code>04_deg_primary_M2.csv</code> 重算真实 48 行网格 → Table S4，正文加出处</td></tr>
<tr><td><span class="tag e">口径</span> 第五轮报告头部</td><td>"供体级合并 + 种族/年龄/性别校正"</td><td>同上，主模型不含 age/sex</td><td>本报告更正；第五轮 HTML 保留为历史记录，不再作为 Methods 依据</td></tr>
</table>
<div class="box bad"><strong>为什么必须改：</strong>审稿人只要对照公开 GEO 元数据与代码，就会发现 age/sex 没进设计矩阵、GPL5175 没有注释文件；这类"方法学表述与可复现产物不一致"是 desk reject 与事后诚信质疑的高风险点，比结果阴性更致命。</div>
</section>''')

# --- 3
H.append('<section id="s3"><h2>3 · Figure 1（真实重绘）</h2>')
H.append(img("Figure1.png"))
H.append('''<p class="small">A：6 个 series matrix 共 96 张芯片 → 66 条供体-平台记录；GSE45570 的 6 例 OHT 已剔除。B：M0→M3 的 DEG 数断崖式下降，GSE9944-GPL8300 与 GSE45570 在 M2 归零。C：GPL571 上 3 例青光眼全为非裔、9 名高加索供体全为对照，种族与疾病近乎共线。图注已按真实数字写入 v0.4 第 8 节；原稿 Figure 1 的 Venn 图不再适用。</p></section>''')

# --- 4
H.append('<section id="s4"><h2>4 · Figure 2（真实重绘）</h2>')
H.append(img("Figure2.png"))
H.append('''<p class="small">A：六基因 × 三平台 M2 的 log2FC 与 BH q，18 次检验全部 q ≥ 0.05；STAT1 一致下调、CASP1 一致上调，与原稿方向相反。B：名义 p（空心圆）与 BH q（实心方）配对，虚线为 q=0.05，没有任何 BH q 落入显著区。C：GSE9944-GPL571 上 23 个映射探针的逐探针名义 95% CI；探针间不独立，CI 未做多重校正。GSE45570 因无基因符号映射未入图，不等于阴性验证。</p></section>''')

# --- 5
H.append('<section id="s5"><h2>5 · 期刊级表格</h2>')
H.append('<h3>Table 1 · DEG counts by model（含残差自由度与校正状态）</h3>')
H.append(table("Table1_DEG_by_model", caption="来源：results/03_deg_by_model.csv；M2/M3 在 GSE2378-GPL8300 与 GSE45570 为供体级 BH 结果但无 ancestry 校正。"))
H.append('<h3>Table 2 · 六基因 M2（18 行，含名义 95% CI 与每组 n）</h3>')
H.append(table("Table2_six_genes_M2", caption="全探针结果（61 个探针的 log2FC / SE / CI / p / q）见 TableS1_all_probes_six_genes.tsv。"))
H.append('<h3>Table 3 · 队列与 QC（含协变量可用率）</h3>')
H.append(table("Table3_cohort_QC", caption="Age/Sex usable 全为 0 是主模型未纳入年龄/性别的直接证据；M2b 从自由文本补回。"))
H.append('<h3>Table 4 · 同系列供体重叠</h3>')
H.append(table("Table4_donor_overlap", caption="GPL571 与 GPL8300 共享 5 个供体 ID，同系列多平台不是独立验证。"))
H.append('''<div class="box good"><strong>补充表：</strong>Table S1 全探针 61 行；S2 主 M2 vs M2b DEG 数；S3 主 M2 vs M2b 六基因；S4 敏感性网格 48 行。全部提供 <code>.tsv</code>，可直接导入 Word/LaTeX。</div></section>''')

# --- 6
H.append('<section id="s6"><h2>6 · M2b 协变量完整敏感性模型</h2>')
H.append('''<p><code>reanalysis_m2b.py</code> 只修改 <code>build_metadata()</code>：把自由文本 <code>char_age</code> / <code>char_sex</code> 转成数值协变量。GSE9944 两个可建模平台的设计矩阵变为 <code>intercept, glaucoma, race_Caucasian, age_z, sex</code>，输出到独立目录 <code>results_m2b/</code>。</p>
<div class="kpi">
  <div class="danger"><b>0 / 18</b><span>M2b 六基因显著数（主模型同为 0/18）</span></div>
  <div><b>114 → 95</b><span>GPL571 M2 DEG 数</span></div>
  <div><b>640 → 516</b><span>GPL571 M3 DEG 数</span></div>
  <div><b>0.077–0.893</b><span>M2b 六基因 BH q 范围（主模型 0.145–0.691）</span></div>
</div>''')
H.append('<h3>Table S2 · 主 M2 与 M2b 的 DEG 数对照</h3>')
H.append(table("TableS2_M2_vs_M2b_DEG_counts"))
H.append('<h3>Table S3 · 六基因逐条对照（节选）</h3>')
H.append(table("TableS3_M2_vs_M2b_six_genes", limit=8, caption="完整 18 行见 tables/TableS3_M2_vs_M2b_six_genes.tsv。"))
H.append('''<div class="box caution"><strong>作者待决策：</strong>是否把 M2b 升为主模型。若升级，正文的 114 改为 95、q 范围改为 0.077–0.893、Table 1–2 与 Figure 1B 需整体重生成；结论（分支 A）不变。本轮保留主模型不变，避免悄悄改动第五轮已交付的数字。</div></section>''')

# --- 7
H.append('''<section id="s7"><h2>7 · 可复现清单</h2>
<table><tr><th>项目</th><th>内容</th></tr>
<tr><td>环境</td><td>Python 3.9.13（D:/anaconda3），numpy 1.21.5 / pandas 1.4.4 / scipy 1.9.1 / statsmodels 0.13.2 / scikit-learn 1.0.2 / matplotlib 3.5.2 / tabulate 0.8.10；无 R</td></tr>
<tr><td>文件清单</td><td><code>tables/file_manifest.csv</code>：%d 条 sha256 + 字节数（输入/脚本 %d 条、主结果 %d 条、M2b %d 条）</td></tr>
<tr><td>输入</td><td>6 个 series matrix（合计 6,021,452 B）+ 3 个平台 annot，全部通过 gzip 完整性校验；残缺 28 KB 文件隔离为 <code>.PARTIAL-DO-NOT-USE</code></td></tr>
<tr><td>命令</td><td><code>REPRODUCIBILITY.md</code>：下载（64 KiB Range 分块）→ <code>reanalysis.py --out results</code> → <code>reanalysis_m2b.py --out results_m2b</code> → <code>make_figures_tables.py</code> → <code>cold_read_v04.py</code></td></tr>
<tr><td>未解决</td><td>代码公开 DOI、GPL5175 映射、limma 复核、参考文献重排、CRediT/基金/AI 披露、正式相似度自查</td></tr>
</table>
<pre>D:/anaconda3/python.exe reanalysis.py     --data . --out results
D:/anaconda3/python.exe reanalysis_m2b.py --data . --out results_m2b
D:/anaconda3/python.exe make_figures_tables.py
D:/anaconda3/python.exe cold_read_v04.py ../青光眼生信稿件_全文重写稿_v0.4.md results</pre>
<div class="box note"><code>_selftest_results/</code> 与 <code>_selftest/</code> 是合成数据自测，禁止引用其中任何数字；原稿 docx 全程只读，未被修改。</div>
</section>''' % (len(man), n_input, n_res, n_sens))

# --- 8
H.append('''<section id="s8"><h2>8 · v0.4 与增强版 cold-read</h2>
<p><code>cold_read_v04.py</code> 继承 v0.3 的全部 53 项检查（残留硬错误、断言强度、定位词、引用越界、图表顺序、与 results CSV 的数字对账、Abstract/Conclusions 一致性），新增 I/J/K 三组共 34 项：图表与表格文件存在性、sha256 清单、未编造 DOI、三处事实修订的反面断言、18 个 95%% CI 逐条入正文、M2b 数字对账、敏感性网格行数。</p>
<div class="kpi">
  <div class="good"><b>%d / %d</b><span>PASS / 总检查项，FAIL = %d</span></div>
  <div><b>35 → 28</b><span>剩余占位符（v0.3 → v0.4）</span></div>
  <div><b>16 → 12</b><span>AUTHOR INPUT REQUIRED</span></div>
  <div><b>0</b><span>DATA NEEDED / PLANNED / AUTHOR CONFIRM</span></div>
</div>
<p>剩余 28 处全部是<strong>外部输入</strong>：12 作者输入（代码 DOI、CRediT、基金、利益冲突、AI 披露、期刊版式）、10 <code>[UNVERIFIED]</code>（原稿 DAVID/KOBAS/miRNA 下游未重跑）、5 <code>[CITATION NEEDED]</code>、1 参考文献重排。统计类占位符已清零，且与 <code>results/*.csv</code> 逐格对账。</p>
<div class="box good">图注、Table 1–2、Methods 2.2/2.5/2.6、Declarations、补充表清单均已回填 v0.4；正文不再引用 Figure 3–5，原稿三张网络图建议整体删除。</div>
</section>''' % (passed, total, failed))

# --- 9
H.append('''<section id="s9"><h2>9 · 投稿可行性与下一步</h2>
<div class="box bad"><strong>判断不变：仍不可投稿。</strong>本轮解决的是"证据可复现性"与"表述诚实性"，没有解决创新性不足、无湿实验/独立队列验证、GPL5175 无基因级验证、缺代码公开 DOI 与文献重排。以原稿叙事投稿仍是 1.50/5 档、必然 desk reject；改定位后的方法学稿有了真实纠偏证据，但仍不到可投状态。</div>
<table><tr><th>优先级</th><th>下一步</th><th>说明</th></tr>
<tr><td>1</td><td>作者决策：M2b 是否升为主模型</td><td>影响 114→95、q 范围、Table 1–2 与 Figure 1B；结论不变</td></tr>
<tr><td>2</td><td>文献重排与声明补齐</td><td>删约 14 条 COVID 支线、补 15–20 篇 2022–2026 文献；CRediT / 基金 / 利益冲突 / AI 披露；代码公开 DOI</td></tr>
<tr><td>3</td><td>Word 版（Office 通道）</td><td>把 v0.4 + TSV/SVG 按目标期刊版式排版；本轮仍不主动生成 docx，避免中间稿被误当投稿文件</td></tr>
<tr><td>4</td><td>第二轮预审与选刊</td><td>逐刊核对近 12 个月纯生信政策、单位预警名单、正式 iThenticate/Turnitin 查重</td></tr>
<tr><td>5</td><td>可选增强</td><td>GPL5175 映射、limma 复核、 ancestry-balanced 子集的独立队列</td></tr>
</table>
<p class="small">无论走哪一步，都不得把 <code>probe not mapped</code> 写成阴性验证、不得把同系列三平台称独立复现、不得调阈值找回六基因、不得把计算预测的 miRNA 写成实验证据。</p>
</section>''')

# --- 10
H.append('''<section id="s10"><h2>10 · 本轮交付文件</h2>
<table><tr><th>文件</th><th>内容</th></tr>
<tr><td><code>work/青光眼生信稿件_图表补齐与事实一致性报告.html</code></td><td>本报告（图已内嵌，可离线打开）</td></tr>
<tr><td><code>work/青光眼生信稿件_全文重写稿_v0.4.md</code></td><td>主交付：真实表格 + 图注回填 + 三处事实修订后的完整英文全文</td></tr>
<tr><td><code>work/青光眼生信稿件_cold-read_v0.4报告.md</code></td><td>87 项逐条检查，PASS 87 / FAIL 0</td></tr>
<tr><td><code>work/data/figures/Figure1.png/.svg</code>、<code>Figure2.png/.svg</code></td><td>300 dpi 位图 + 可编辑矢量图</td></tr>
<tr><td><code>work/data/tables/*.tsv/.md</code></td><td>Table 1–4、Table S1–S4、file_manifest.csv、tables_index.md</td></tr>
<tr><td><code>work/data/REPRODUCIBILITY.md</code>、<code>README.md</code> v2.1</td><td>环境、命令、限制、运行手册</td></tr>
<tr><td><code>work/data/make_figures_tables.py</code>、<code>reanalysis_m2b.py</code>、<code>apply_v04.py</code>、<code>cold_read_v04.py</code></td><td>本轮新增/派生的 4 个脚本，全部通过编译检查</td></tr>
<tr><td><code>work/data/results_m2b/</code></td><td>M2b 独立结果目录（11 个文件）</td></tr>
</table>
<p class="small">原始稿件 <code>D:\\BaiduSyncdisk\\待研究相关资料\\青光眼生信研究\\Manuscript.docx</code> 全程只读，未被修改。本轮方法链路由 Paper论文智导（https://paper.ac.cn）提供。</p>
</section>''')

H.append('</div>\n</body>\n</html>')
open(OUT, "w", encoding="utf-8").write("\n".join(H))
print("written:", OUT, os.path.getsize(OUT), "bytes")

# -*- coding: utf-8 -*-
"""Build the round-7 self-contained HTML report (no external assets)."""
import csv
import html
import json
import os
import re
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(ROOT)
E = lambda x: html.escape(str(x))


def tsv(name):
    p = os.path.join(ROOT, name)
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


refs = tsv("references_v05.tsv")
ledger = tsv("literature_ledger.tsv")
vref = json.load(open(os.path.join(ROOT, "verified_references.json"), encoding="utf-8"))
remap = json.load(open(os.path.join(ROOT, "citation_remap.json"), encoding="utf-8"))
cold = open(os.path.join(WORK, "青光眼生信稿件_cold-read_v0.5报告.md"), encoding="utf-8").read()
m_pass = re.search(r"PASS (\d+) / FAIL (\d+)", cold)
pass_n, fail_n = (int(m_pass.group(1)), int(m_pass.group(2))) if m_pass else (0, 0)
groups = Counter(re.findall(r"^\| ([A-L] [^|]+) \|", cold, re.M))
acts = Counter(r["action"] for r in ledger)
recent = sum(1 for v in vref.values() if v["year"] >= "2022" and "PubMed" in v["source"])


def table(headers, rows, cls=""):
    h = "".join(f"<th>{E(x)}</th>" for x in headers)
    b = "".join("<tr>" + "".join(f"<td>{E(x)}</td>" for x in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


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
footer{text-align:center;color:var(--mut);font-size:12.5px;margin-top:28px}
"""

parts = []
parts.append(f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>青光眼生信稿件 · 文献重排与第二轮预审报告</title><style>{CSS}</style></head><body><div class="wrap">
<header><h1>青光眼生信稿件 · 文献重排、声明合规与第二轮预审</h1>
<p class="sub">第七轮 · 2026-11-09 · 承接第六轮第 9 节优先级 1–4 · 统计数字沿用真实重跑结果，未改动任何模型或结果表</p></header>
<div class="kpis">
<div class="kpi"><b>{len(refs)}</b><span>v0.5 参考文献总数</span></div>
<div class="kpi"><b>{len(vref)}</b><span>新增可核验文献</span></div>
<div class="kpi"><b>{recent}</b><span>2022–2026 期刊文献</span></div>
<div class="kpi"><b>{pass_n}/{pass_n+fail_n}</b><span>cold-read 通过</span></div>
<div class="kpi"><b>6</b><span>逐刊核验政策</span></div>
</div>""")

# 1
parts.append(f"""<section><h2>1 · 本轮完成的四项工作</h2>
{table(["#", "工作", "产出", "状态"], [
 ["1", "作者决策项：M2b 是否升主模型", "A/B 决策包 + 7 处影响清单（§2）；不擅自改动主结果", "<span class='tag info'>待作者拍板</span>"],
 ["2", "参考文献审计与整体重排", "69 条 → 58 条；5 处文献占位符清零；新增 27 条全部 PubMed/Crossref/GEO 核验", "<span class='tag ok'>完成</span>"],
 ["3", "v0.5 全文中稿与声明合规包", "12 项待填字段结构化模板（CRediT / 基金 / COI / AI 披露 / 代码 DOI），不虚构作者信息", "<span class='tag ok'>完成</span>"],
 ["4", "第二轮模拟预审 + 选刊政策矩阵", "编辑初审 + 3 位审稿人意见；6 本期刊官网政策核验；发现 1 处新的内部不一致", "<span class='tag warn'>需整改</span>"],
])}
<p class="small">本轮<strong>没有重跑统计模型</strong>：`results/`、`results_m2b/`、`figures/`、`tables/` 的统计数值与图形全部沿用第六轮；新增的是文献、声明、预审与政策证据。</p>
</section>""")

# 2 M2b decision
parts.append("""<section><h2>2 · 决策包：M2b 是否升为主模型</h2>
<p>这是会改动已交付数字的科学决策，本轮<strong>不替作者决定</strong>。两版结论完全一致（六基因 0/18 显著、分支 A 不变），差别只在数字口径与文件一致性。</p>
""" + table(["", "选项 A：保持现状（推荐）", "选项 B：M2b 升主模型"], [
 ["主结果目录", "<code>results/</code>（预指定 M2）", "<code>results_m2b/</code>（补回自由文本 age/sex）"],
 ["GPL571 M2 DEG", "114", "95"],
 ["M3 DEG / 六基因 q 范围", "640 / 0.145–0.691", "516 / 0.077–0.893"],
 ["设计矩阵", "intercept + glaucoma + ancestry", "再 + age_z + sex"],
 ["优点", "预指定、可原样复跑、已交付数字与 cold-read 全部保持有效；M2b 作为敏感性证据", "协变量更完整，Methods 不必再解释 age/sex 掉出模型"],
 ["代价", "Methods 需保留一段“自由文本解析失败”的如实说明", "需同步改 7 处文件，且易被审稿人质疑“事后换主模型”"],
]) + """
<h3>若选 B，必须同步修改的 7 处</h3>
<ol>
<li>Abstract Results：114→95、640→516、q 0.145–0.691→0.077–0.893；M2b 一句改写。</li>
<li>Results 3.1 的 Table 1 与 Figure 1B（ DEG 柱状图需重绘）。</li>
<li>Results 3.2 六基因主表、Table 2、Figure 2A–C 与 Table S1（全探针 CI 需从 M2b 结果重算）。</li>
<li>Table S2 / S3 的"主模型 vs 敏感性"对照方向与标题。</li>
<li>Methods 2.5：删除"Numeric age and sex did not enter any model"等事实修订句，改写为完整协变量模型。</li>
<li><code>cold_read_v05.py</code> 的 J 组反面断言（"不得声称已校正 age/sex"）需反转，K 组 M2b 对账需改为主结果对账。</li>
<li><code>README.md</code>、<code>REPRODUCIBILITY.md</code>、<code>facts_for_manuscript.md</code>、<code>decision.json</code> 与 <code>file_manifest.csv</code>。</li>
</ol>
<div class="good"><b>建议：</b>保持 A。M2 是预指定主模型，M2b 是发现元数据解析缺陷后的敏感性分析，结论不变；把它作为 Table S2–S3 与 Abstract 一句即可，不必为"看起来更完整"而更换主模型。</div>
</section>""")

# 3 references
parts.append(f"""<section><h2>3 · 参考文献审计与重排（69 → 58）</h2>
{table(["动作", "条数", "依据"], [
 ["RETAIN 保留", acts.get("RETAIN", 0), "v0.4 正文实际引用且 claim 在范围内；条目文本沿用原稿，<strong>待作者用 Zotero 逐条统一格式</strong>"],
 ["DELETE 删除", acts.get("DELETE", 0), "12 条 COVID/抗病毒支线 + 25 条未引用或跨疾病外推条目（含 2 条 medRxiv/bioRxiv 预印本）"],
 ["REPLACE 替换", acts.get("REPLACE", 0), "原稿 ref 41（缺血白质损伤模型）→ 2 篇 STAT1/IFN 权威综述"],
 ["ADD 新增", acts.get("ADD", 0), "全部来自 <code>verified_references.json</code>：PubMed E-utilities esummary / Crossref / GEO 官方记录"],
])}<p>新增的 {len(vref)} 条里，<strong>{recent} 篇为 2022–2026 年期刊文献</strong>，另有 1 条 GEO 官方数据记录与 9 篇方法学/机制经典（Benjamini–Hochberg 1995、Lazic 2010、Aarts 2014、limma 2015、miRBase 2019、自噬通量指南 2021 等）。引用编号按 v0.5 正文首次出现顺序自动重排，正文与文末双向对账为零缺口。</p>
<h3>五处文献占位符如何清零</h3>
{table(["原占位符意图", "替换为"], [
 ["眼特异免疫/自噬机制证据", "青光眼星形胶质细胞免疫、神经炎症、小胶质细胞综述（3 篇，均带 PMID/DOI）"],
 ["2022–2026 同类研究 4 篇", "8 篇可核验同类研究：BMC Med Genomics 2023 ×2、IJMS 2024;25:8193、Int J Ophthalmol 2023、BMC Genom Data 2022、Mol Biotechnol 2025、Medicine 2026、Curr Med Chem 2024"],
 ["GSE9944 的 GEO 标准引用", "GEO Series/Platform 官方记录 + GEO 23-year update（Clough 2024, PMID 37933855）"],
 ["STAT1/IFN 权威综述", "Au-Yeung 2013（JAKSTAT）与 Clark 2022（Immunol Rev）"],
 ["2022–2026 眼部特异证据", "PNAS 2023 眼后段细胞图谱、Cells 2023 ONH 星形胶质细胞异质性、Nat Commun 2024 GWAS+单细胞、PNAS 2026 Hopx+ ONH 星形胶质细胞"],
])}
<div class="note"><b>一处口径更正：</b>第一轮预审提到的 "2025 PLoS One 同类 GEO 挖掘研究" 未能在 PubMed 精确复核到对应条目，本轮<strong>未沿用该说法</strong>，改引同刊 2025 年一篇眼部 TGF-β1 miRNA–mRNA 研究（PMID 39883689），并另补 8 篇可核验同类研究。原稿 ref 8 的团体作者名被错误拆分，也已按 Lasker/IIoA 修正。</div>
<p class="small">台账文件：<code>work/data/references_audit.tsv</code>（69 条原稿审计）、<code>literature_ledger.tsv</code>（动作与理由）、<code>references_v05.tsv</code>（58 条编号/核验状态/回链）、<code>verified_references.tsv</code>（27 条完整元数据）、<code>citation_remap.json</code>（旧→新编号映射）。</p>
</section>""")

# 4 v0.5
parts.append("""<section><h2>4 · v0.5 全文中稿与声明合规包</h2>
<p><code>青光眼生信稿件_全文重写稿_v0.5.md</code> 由 v0.4 自动派生：5 处文献占位符与文末参考文献待插入说明全部清零；正文引用编号整体重排；Methods 2.6 脚本清单同步到 <code>cold_read_v05.py</code>、<code>verify_literature.py</code>、<code>apply_v05.py</code>；版本说明新增"M2b 决策待定""保留条目待 Zotero 复核"两条显式声明。</p>
""" + table(["占位符类型", "v0.4 → v0.5", "说明"], [
 ["<code>[DATA NEEDED]</code> / <code>[PLANNED]</code> / <code>[AUTHOR CONFIRM]</code>", "0 → 0", "统计类占位符持续为零"],
 ["<code>[CITATION NEEDED]</code>", "5 → <strong>0</strong>", "全部替换为已核验文献"],
 ["<code>[REFERENCES TO BE RE-INSERTED]</code>", "1 → <strong>0</strong>", "替换为 58 条完整参考文献表"],
 ["<code>[AUTHOR INPUT REQUIRED]</code>", "12 → 12", "必须由作者填写，不代填"],
 ["<code>[UNVERIFIED]</code>", "10 → 10", "原稿下游分析未重跑，数字不得当作重跑结果"],
]) + """
<p>配套的 <code>青光眼生信稿件_声明填写指南.md</code> 给出 12 项逐条模板：Title page、通讯作者 ORCID、代码仓库 DOI、Ethics、GEO 标准引用、CRediT 14 角色、基金、利益冲突、AI 工具披露（两种建议句式）、期刊版式转换，以及代码/数据公开的最小可核验包。<strong>作者、单位、基金、ORCID、仓库 DOI 一律未虚构。</strong></p>
</section>""")

# 5 cold read
groups_rows = [[g, n] for g, n in sorted(groups.items())]
parts.append(f"""<section><h2>5 · 增强版 cold-read：{pass_n} 项通过 / {fail_n} 项失败</h2>
<p>在 v0.4 的 87 项之上新增 E 组<strong>双向引用对账</strong>与 L 组<strong>文献核验</strong>，合计 {pass_n+fail_n} 项。</p>
{table(["检查组", "项数"], groups_rows)}
<ul>
<li>正文每个引用编号都有对应文献条目；58 条文献每条至少被引用一次；编号连续 1–58。</li>
<li>27 条新增文献全部有 PubMed/Crossref/GEO 官方核验来源，且完整条目出现在文末表中。</li>
<li>参考文献表中 COVID / SARS-CoV-2 / 抗病毒支线命中 0，medRxiv / bioRxiv 预印本命中 0。</li>
<li>台账动作计数、2022–2026 文献数、编号映射、声明指南、M2b 决策标注全部对账通过。</li>
<li>v0.4 的图表文件、18 个 95% CI、M2b 数字、敏感性网格 48 行、事实一致性反面断言等检查全部继承通过。</li>
</ul>
<p class="small">报告：<code>青光眼生信稿件_cold-read_v0.5报告.md</code>。该检查不能替代机构权限下的正式 iThenticate/Turnitin 查重。</p>
</section>""")

# 6 peer review
parts.append("""<section><h2>6 · 第二轮模拟预审</h2>
<div class="danger"><b>总判断：仍不可投稿。</b> 模拟评分约 <b>2.6/5</b>（首轮 1.50/5），提升全部来自证据可复现性、文献与表述诚实性，<strong>不是来自新发现</strong>。编辑初审 desk-reject 风险仍高。</div>
""" + table(["角色", "首要结论", "最可能的拒稿/大修理由"], [
 ["编辑初审", "原创但属衍生/再分析", "贡献局限于纠正自己原稿；无独立验证；缺代码 DOI 与 12 项声明"],
 ["审稿人 1（生信/方法学）", "方法诚实但强度不足", "无 limma 复核、无基因级跨平台 harmonisation、探针取最小 p 偏倚、共线无量化诊断"],
 ["审稿人 2（眼科/生物学）", "生物学结论已正确收缩", "无湿实验/独立队列；GPL5175 未映射不得写成阴性验证；星形胶质细胞 vs 全 ONH 组织不可比"],
 ["统计审稿人", "<strong>发现新的内部不一致</strong>", "ROC/AUC 仍用 array-level 表达值，与全文“供体级”主张冲突；BH 在探针层而非基因层；名义 CI 未多重校正"],
]) + """
<h3>本轮新发现（4 项）</h3>
{table(["#", "问题", "处置"], [
 ["N1", "Methods 2.5 的 ROC/AUC 用 array-level 表达值，bootstrap CI 可能偏乐观", "<span class='tag bad'>未改</span> 需重跑供体级 ROC 或降级为探索性并加限制说明"],
 ["N2", "第一轮所述 2025 PLoS One 同类研究未能精确复核", "<span class='tag ok'>已改</span> 改用可核验同刊文献 + 8 篇同类研究"],
 ["N3", "12 条 COVID 支线与 2 条预印本引用", "<span class='tag ok'>已删</span> cold-read L 组校验命中 0"],
 ["N4", "原稿 ref 8 团体作者名被拆分", "<span class='tag ok'>已修</span> 按团体作者格式还原"],
])}
<p class="small">N1 是唯一仍影响统计结论表述的问题；本轮<strong>未擅自重跑</strong>，与 M2b 决策一起列为下一步最高优先级。</p>
</section>""")

# 7 journals
journals = [
 ["BMC Medical Research Methodology", "<span class='tag ok'>相对最好</span>", "scope 明确含数据质量、统计与建模；不按 perceived impact 决策", "未单列，scientifically valid 标准对审计稿友好", "£2290 / $3090 / €2690"],
 ["PLOS ONE", "<span class='tag info'>次选</span>", "明确 “we consider negative and null results”；但衍生/重复研究需充分 justification，争议已发表工作会邀请原作者署名审稿", "明确接受", "官网未列金额，需人工复核"],
 ["BMC Bioinformatics", "<span class='tag bad'>低</span>", "要求 novel algorithms/software/models/tools；本稿无新算法", "未单列", "£2290 / $3090 / €2590"],
 ["BioData Mining", "<span class='tag bad'>低</span>", "要求贡献 broadly useful beyond a single dataset；本稿聚焦单一数据系列", "未单列", "£2090 / $2790 / €2290"],
 ["PeerJ", "<span class='tag bad'>不建议</span>", "<strong>硬性排除风险</strong>：公共数据生信研究须提出新生物学问题/不同结论，且用至少两类 independent public datasets / new clinical data / new experimental data 验证；“only explore a dataset without proper validation” 属 out of scope", "Registered Reports 下接受阴性结果", "会员制/APC，需查 pricing"],
 ["Scientific Reports", "<span class='tag warn'>待复核</span>", "本轮 author-instructions 与 before-you-submit 仅导航页，未核验到纯生信专门条款；官网称首次决定目标 45 天", "未核验", "需查 open-access 页"],
]
parts.append("""<section><h2>7 · 选刊政策矩阵（2026-11-09 官网核验）</h2>
""" + table(["期刊", "匹配度", "纯计算/公共数据再分析政策要点", "阴性结果", "APC（官网当日文本）"], journals) + """
<div class="note"><b>核验边界：</b>这些页面多数未标注最后修订日期，因此<strong>"近 12 个月政策"这一口径无法由页面自证</strong>；AI 政策、APC、单位预警名单、PLOS 的 AI 政策页与 Scientific Data（两个 URL 均 404）都须作者在投稿当日人工复核。PeerJ 的 AI 政策最严格：须声明工具全名+版本+用途+原因、保留原文与 prompts，未披露属 misconduct；PLOS ONE 本轮 submission-guidelines 页面未见 AI 条款，需另查政策页。</div>
<p class="small">核验 URL 与逐条原文摘录见 <code>青光眼生信稿件_第二轮预审与选刊矩阵.md</code> §5。第一轮已核验的 Frontiers / KJPP 政策本轮未重复核验。</p>
</section>""")

# 8 next
parts.append("""<section><h2>8 · 整改清单与投稿可行性</h2>
<ol>
<li><strong>作者决策</strong>：M2b 是否升主模型（§2）。</li>
<li><strong>N1</strong>：ROC/AUC 改供体级或明确降级为探索性；补 ancestry×disease 共线的量化诊断（交叉表/VIF/条件数）。</li>
<li>补 limma 复核、全探针中位数聚合敏感性；必要时做 ancestry-balanced 子集分析。</li>
<li>代码公开：Zenodo/GitHub 打 tag 生成 DOI、补 <code>environment.yml</code>，回填 12 处声明。</li>
<li>31 条保留文献用 Zotero 统一格式并逐条回链；清理 <code>doi:https://doi.org/…</code> 之类格式残留。</li>
<li>Word 版（Office 通道）：TSV/SVG 转投稿格式，删除 Figure 3–5 相关段落。</li>
<li>Cover letter：写清方法学贡献、与原稿关系、无湿实验的理由、数据与代码 DOI。</li>
<li>正式查重 + 单位预警名单 + 投稿当日逐刊政策复核。</li>
</ol>
<div class="danger"><b>投稿可行性不变：仍不可投稿。</b> 本轮解决的是文献可核验性与声明结构化，没有解决创新性不足、无独立队列/湿实验、GPL5175 无基因级映射、代码 DOI 未填。若以原稿叙事投稿仍是必然 desk reject；改定位后的方法学稿只有在完成上述 1–4 项并选定期刊后才具备送审条件。</div>
<h3>红线（不得突破）</h3>
<ul>
<li>不得把 <code>probe not mapped</code> 写成阴性验证；不得把同系列三平台称为独立复现。</li>
<li>不得调阈值找回六基因；不得把计算预测的 miRNA 写成实验证据；不得把原稿下游数字当作重跑结果。</li>
<li>不得编造作者、基金、ORCID、代码 DOI 或任何文献条目。</li>
</ul>
</section>""")

# 9 files
parts.append("""<section><h2>9 · 本轮交付文件</h2>
""" + table(["文件", "内容"], [
 ["<code>work/青光眼生信稿件_全文重写稿_v0.5.md</code>", "主交付：58 条参考文献、5 处文献占位符清零、声明待填结构化的完整英文全文"],
 ["<code>work/青光眼生信稿件_cold-read_v0.5报告.md</code>", f"{pass_n} 项逐条检查，PASS {pass_n} / FAIL {fail_n}"],
 ["<code>work/青光眼生信稿件_声明填写指南.md</code>", "12 项声明模板、CRediT 14 角色、AI 披露句式、代码公开最小包"],
 ["<code>work/青光眼生信稿件_第二轮预审与选刊矩阵.md</code>", "模拟预审逐条意见、6 刊政策原文要点、核验 URL 与边界说明"],
 ["<code>work/青光眼生信稿件_文献重排与第二轮预审报告.html</code>", "本报告（自包含，可离线打开）"],
 ["<code>work/data/references_v05.tsv</code> / <code>literature_ledger.tsv</code>", "58 条编号回链 / 69 条原稿动作台账"],
 ["<code>work/data/verified_references.tsv|json</code> / <code>references_audit.tsv|json</code>", "27 条新增文献真实元数据 / 69 条原稿引用审计"],
 ["<code>work/data/citation_remap.json</code>", "旧→新引用编号映射，按首次出现顺序"],
 ["<code>work/data/audit_references.py</code> / <code>verify_literature.py</code> / <code>apply_v05.py</code> / <code>cold_read_v05.py</code>", "本轮新增/派生的 4 个脚本，全部通过编译"],
 ["<code>work/data/tables/file_manifest.csv</code> / <code>README.md</code> / <code>REPRODUCIBILITY.md</code>", "SHA-256 清单与运行文档已同步至 v2.2"],
]) + """
<p class="small">原始稿件 <code>D:\\BaiduSyncdisk\\待研究相关资料\\青光眼生信研究\\Manuscript.docx</code> 全程只读，未被修改。本轮方法链路由 Paper论文智导（https://paper.ac.cn）提供。</p>
</section>
<footer>第七轮报告 · 2026-11-09 · 所有统计数字来自本机真实 GEO 结果表，无合成数据</footer>
</div></body></html>""")

out = os.path.join(WORK, "青光眼生信稿件_文献重排与第二轮预审报告.html")
open(out, "w", encoding="utf-8").write("\n".join(parts))
print("wrote", out, "bytes", os.path.getsize(out))
print("refs", len(refs), "ledger actions", dict(acts), "cold", pass_n, fail_n, "recent", recent)

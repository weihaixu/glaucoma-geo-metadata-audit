# -*- coding: utf-8 -*-
"""One-time, assertion-guarded sync of the release package to manuscript v1.0
(methodology / data-quality framing). Re-runnable only from a v0.9 state.
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent
R = D / "release"
log = []


def load(p):
    return p.read_text(encoding="utf-8")


def save(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def rep(p, old, new, tag=""):
    s = load(p)
    c = s.count(old)
    assert c == 1, "%s :: [%s] matched %d times: %.100r" % (p.name, tag, c, old[:100])
    save(p, s.replace(old, new, 1))
    log.append("%s <- %s" % (p.name, tag or old[:36]))


# ---------------------------------------------------------------- build_release.py
p = R / "build_release.py"
rep(p, '"""Build the Zenodo/GitHub release bundle for the v0.9 re-analysis.',
       '"""Build the Zenodo/GitHub release bundle for the v1.0 methodology-framed re-analysis.',
       "docstring")
rep(p, 'MANUSCRIPT = DATA.parent / "青光眼生信稿件_全文重写稿_v0.9.md"',
       'MANUSCRIPT = DATA.parent / "青光眼生信稿件_全文重写稿_v1.0.md"', "MANUSCRIPT")

# ---------------------------------------------------------------- PUBLISH_STEPS.md
p = R / "PUBLISH_STEPS.md"
s = load(p)
for a, b in [("v0.9", "v1.0"), ("351/351", "388/388"),
             ("cold_read_v09", "cold_read_v10"),
             ("S13/S15/S16/S17/S18", "S13/S15/S16/S17/S18/S19"),
             ("S1–S18.tsv", "S1–S19.tsv")]:
    s = s.replace(a, b)
save(p, s)
log.append("PUBLISH_STEPS.md <- global version bump")
rep(p, "# 从「v1.0 增强稿」到「可投稿」：逐步操作与验收",
       "# 从「v1.0 方法学 / 数据质量审计定位稿」到「可投稿」：逐步操作与验收", "title")
rep(p, "> 当前状态：主模型决策 A 已锁定，cold-read v1.0 = 388/388 PASS，**仍不可投稿**。",
       "> 当前状态：主模型决策 A 已锁定，cold-read v1.0 = 388/388 PASS，投稿方向已改为方法学 / 数据质量审计栏目；"
       "**栏目方向成立，但 12 项声明、代码 DOI、单位口径确认与期刊格式未完成前仍不构成投稿文本**。", "status")
rep(p,
    """> **流程变更（2026-11-09 第十三轮）**：`青光眼生信稿件_全文重写稿_v1.0.md`
> 与 `cold_read_v10.py` **已经存在**；v1.0 是 P1 路线图全部执行完毕的版本
> （S13 事后效应量、S15 边界检查、S16 元数据审计、S17/S18 跨组织方向一致性，
> 388/388 PASS）。因此不要再由 v0.8 派生，而是**直接在 v1.0 上回填 12 项声明
> 与 DOI**；回填后仍叫 v1.0，是否升 v1.0 由作者决定。""",
    """> **流程变更（2026-11-09 第十四轮）**：`青光眼生信稿件_全文重写稿_v1.0.md`
> 与 `cold_read_v10.py` **已经存在**；v1.0 是把 P1 全部结果重新定位为
> 「可复用元数据审计清单 + 一个 worked example」的方法学 / 数据质量栏目稿
> （新增 Methods 2.8、Table S19，388/388 PASS；统计数字与引用编号零改动）。
> 因此不要再由 v0.9 派生，而是**直接在 v1.0 上回填 12 项声明与 DOI**；
> 回填后仍叫 v1.0，是否升 v1.1 由作者决定。""", "section 5 flow")
rep(p, "> **关键陷阱**：`cold_read_v10.py` 继承自 v0.8，仍有 4 处断言按「尚未填 DOI /",
       "> **关键陷阱**：`cold_read_v10.py` 继承自 v0.9，仍有 4 处断言按「尚未填 DOI /", "trap")
rep(p, "- 原稿 `Manuscript.docx` 全程只读，从未修改。",
       """- 不得把 v1.0 的方法学定位再写回「六基因发现」叙事；Table S19 是主交付物，
  六个转录本只是 worked example；
- 稿件正文保持期刊中立，不写死刊名、分区、影响因子或 APC；这些只在选刊材料中出现，
  且须按投稿当日官方页面复核；
- 原稿 `Manuscript.docx` 全程只读，从未修改。""", "red lines")
rep(p,
    """**即使 1–7 全部完成，创新性不足、无湿实验/独立队列、GPL5175 无基因级验证
这几条科学缺口依然存在；第二轮模拟预审约 2.6/5，投稿前须由作者判断是否值得投。**
P1 路线图（P0 之外的低成本增强项）到 v1.0 已全部执行完毕，但它只提升方法学与
报告质量，**没有补上 P2 所需的新数据或湿实验**；模拟加权总分仍在 ≈3.4 一档
（方法维与论证维各约 +0.2 由工具化与审计示范带来），远未到接收线。""",
    """**即使 1–7 全部完成，无湿实验/独立队列、GPL5175 无基因级验证这几条科学缺口
依然存在；第二轮模拟预审约 2.6/5 是生物学论著口径下的判断，投稿前须由作者
判断是否值得投。** 改投方法学 / 数据质量审计栏目后，「创新性不足」这一 desk-reject
理由的权重明显下降（目标栏目按科学有效性而非 perceived impact 评估），但**这是
栏目匹配度的改变，不是数据或验证的补强**：P1 只提升方法学与报告质量，P2 所需的
新数据或湿实验仍未补上。选刊核验记录、未核验项与待作者确认清单见
`青光眼生信稿件_方法学栏目定位与改稿方案.html`；**最终以本单位科研管理部门
当年目录为准**。""", "readiness")

# ---------------------------------------------------------------- DECLARATIONS_12.md
p = R / "DECLARATIONS_12.md"
s = load(p).replace("v0.9", "v1.0").replace("cold_read_v09.py", "cold_read_v10.py")
save(p, s)
log.append("DECLARATIONS_12.md <- version bump")
rep(p,
    "v1.0 新增 Table S17/S18 与 `results_external/`；它们不改变 12 项声明的内容，但第 #6 项的数据可用性列表若提及外部系列，须注明 GSE27276 为**跨组织方向一致性练习**、GPL2507 为官方 annot，且不构成独立复现。",
    """v1.0 新增 Table S17/S18 与 `results_external/`；它们不改变 12 项声明的内容，但第 #6 项的数据可用性列表若提及外部系列，须注明 GSE27276 为**跨组织方向一致性练习**、GPL2507 为官方 annot，且不构成独立复现。

**v1.0 栏目重定位补充**：新增 Table S19（可复用审计清单模板）与 Methods 2.8，稿件定位为方法学 / 数据质量审计。12 项声明的内容不变，但第 #6 项数据可用性应同时列出 `geo_metadata_audit.py`、`results_audit/` 与 Table S19；第 #11 项 AI 工具披露须按目标期刊当期政策填写；cover letter 须说明「为何是方法学而非生物学论著」。稿件正文保持期刊中立，刊名、分区、APC 只在选刊材料中出现。""",
    "footer")

# ---------------------------------------------------------------- .zenodo.json
p = R / ".zenodo.json"
z = json.loads(load(p))
m = z["metadata"]
m["title"] = ("Reproducibility package for a reusable metadata-audit and donor-level "
              "re-analysis framework for public gene-expression series (v1.0)")
m["version"] = "v1.0"
m["description"] = (
    "Code, derived result tables, figures, supplementary tables and run documentation for a "
    "methodological / data-quality audit of six NCBI GEO series matrices (GSE9944 on "
    "GPL91/GPL571/GPL8300, GSE2378 on GPL91/GPL8300, GSE45570 on GPL5175), reframed in v1.0 "
    "as a reusable five-class metadata-audit checklist with the glaucoma optic nerve head "
    "series as a worked example. The primary results are the pre-specified donor-level OLS M2 "
    "in results/; results_m2b/, results_diagnostics/, results_limma/, results_genelevel/, "
    "results_power/, results_gpl5175/, results_audit/ and results_external/ contain sensitivity, "
    "boundary, audit and descriptive analyses ONLY. Raw GEO series matrices and platform "
    "annotations are NOT redistributed; they are re-downloaded with the supplied fetch scripts "
    "and their SHA-256 checksums are recorded in tables/file_manifest.csv. GEO has no official "
    "GPL5175 annotation file: a local probe-to-gene map was rebuilt from the complete 316,919-row "
    "SOFT platform table and used ONLY for an exploratory GSE45570 boundary check (Table S15), "
    "never as validation. Table S13 reports post-hoc detectable effect sizes, Table S16 the "
    "observed five-class metadata audit of six primary matrices plus one external candidate, "
    "Table S14 the official GEO verification of external cohort candidates, Tables S17-S18 an "
    "exploratory cross-tissue directional concordance contrast in GSE27276 under three unit "
    "conventions, and Table S19 the reusable checklist template, decision rules, minimum "
    "reporting schema and interpretation boundaries. Disease in GSE27276 is completely "
    "confounded with tissue procurement and postmortem delay, donor identity is only partly "
    "recoverable, and that comparison is NOT an independent replication or validation cohort. "
    "No independent replication or wet-laboratory validation is claimed anywhere; the six "
    "prioritised transcripts remain 0/18 non-significant in the primary model and serve only as "
    "a bounded worked example, not a biological claim. Manuscript v1.0 is journal-neutral. "
    "Cold-read v1.0: 388/388 assertions pass; results/ and manuscripts v0.7-v0.9 are unchanged.")
for k in ["metadata audit checklist", "reporting standards", "worked example"]:
    if k not in m["keywords"]:
        m["keywords"].append(k)
save(p, json.dumps(z, indent=2, ensure_ascii=False) + "\n")
log.append(".zenodo.json <- v1.0 metadata")

# ---------------------------------------------------------------- README / REPRODUCIBILITY
p = D / "README.md"
assert "## 19." not in load(p)
with open(p, "a", encoding="utf-8", newline="") as f:
    f.write("""

## 19. v2.9 新增（2026-11-09）：方法学 / 数据质量审计栏目重定位 · 第十四轮

作者决定把投稿方向改为**方法学 / 数据质量审计栏目**。`apply_v10.py` 用 14 处断言式替换从 v0.9 派生 `青光眼生信稿件_全文重写稿_v1.0.md`（sha `53f53d91619b`），并派生 `cold_read_v10.py`（新增 R 组 37 项）→ **388/388 PASS / FAIL 0**。

- **叙事切换**：标题改为「可复用元数据审计框架 + 青光眼 ONH case study」；结构化摘要的 Background 改为公共表达谱复用前的元数据缺陷；Introduction 新增两段方法学立题并把 aims 改为「定义清单 → worked example → 外部压力测试」；Discussion 首段与 Conclusions 以清单和流水线为结论；Keywords 改为 metadata audit / reproducibility / reporting standards。六基因降级为 **worked example / 有界的假设生成案例**，不是生物学主张。
- **新增交付**：Methods 2.8 写明 C1–C5 五类只读检查；`tables/TableS19_metadata_audit_checklist.md|.tsv` 给出可复用模板（必填字段、判据、FAIL/WARN 含义、复用前动作、适用边界、最小报告 schema、强制解释边界）；§9 增加 S19 条目。
- **零改动**：Results 3.1–3.5、Methods 2.1–2.7、Declarations、References、Figure legends、**58 个引用编号集合**、全部统计数字、0/18 与红线措辞、12 项声明与 10 个 UNVERIFIED 标记原样保留（R 组用 v0.9 正文动态对账）。v0.7 `3fcfdbb3d2d2`、v0.8 `7bb05464f69f`、v0.9 `05c1aa8eb12e`、`results/04_deg_primary_M2.csv` `48876f29f3d0` 全部未变。
- **期刊中立**：稿件正文不写刊名、分区、IF、APC。官方核验记录（BMC Medical Research Methodology 的 aims/scope、article types、两个 Collection；BioData Mining 的 scope 与 article types）与待作者确认清单在 `青光眼生信稿件_方法学栏目定位与改稿方案.html`。分区/IF/APC/预警名单/单位目录**未做单位口径核验**，最终以本单位科研管理部门当年目录为准。
- **可行性判断更新**：栏目方向成立，创新性不足这条 desk-reject 理由的权重下降；但**这不是数据或验证的补强**，12 项声明、代码 DOI、单位口径与期刊格式未完成前**仍不构成投稿文本**。P2 的新队列/湿实验缺口不变。
- 发布包升 v1.0：`build_release.py` 的 MANUSCRIPT、`.zenodo.json`、`PUBLISH_STEPS.md`、`DECLARATIONS_12.md` 同步；`REPRODUCIBILITY.md` §13 给出复跑命令。
""")
log.append("README.md <- section 19")

p = D / "REPRODUCIBILITY.md"
assert "## 13." not in load(p)
with open(p, "a", encoding="utf-8", newline="") as f:
    f.write("""

## 13. Round 14 (2026-11-09): reframing for a methodology / data-quality article (v1.0)

```bash
cd work/data
D:/anaconda3/python.exe apply_v10.py          # -> manuscript v1.0 + cold_read_v10.py
D:/anaconda3/python.exe cold_read_v10.py      # 388 PASS / 0 FAIL
D:/anaconda3/python.exe apply_release_v10.py  # -> release package + run docs
cd release
D:/anaconda3/python.exe build_release.py --build --allow-draft --zip --verify
```

* `apply_v10.py` performs 14 asserted single-match substitutions on v0.9. All
  Results sections (3.1-3.5), Methods 2.1-2.7, Declarations, References and
  Figure legends are preserved verbatim. The R group of `cold_read_v10.py`
  verifies that the set of in-text citation numbers in v1.0 equals that of
  v0.9, that no numeric claim changed, that all 12 author-declaration
  placeholders and 10 UNVERIFIED markers remain, and that v0.7
  (`3fcfdbb3d2d2`), v0.8 (`7bb05464f69f`), v0.9 (`05c1aa8eb12e`) and
  `results/04_deg_primary_M2.csv` (`48876f29f3d0`) are byte-identical.
* New artefact: `tables/TableS19_metadata_audit_checklist.md|.tsv` - a
  reusable five-class checklist (structured covariates, group-by-ancestry zero
  cells, replicate/donor overlap, annotation availability, scale and excluded
  groups) with decision rules, a minimum per-series reporting schema and
  mandatory interpretation boundaries. It is a template, contains no
  disease-effect estimate and makes no transcript-level claim.
* The manuscript is journal-neutral: no journal name, quartile, impact factor
  or APC appears in the article text. Journal/category verification is kept in
  the separate positioning report and is explicitly dated.
* **Submission readiness: the category direction is viable, but the manuscript
  is still not a submission text** until the 12 author declarations, the code
  DOI, institutional journal-list confirmation and the target-journal format
  are completed. Reframing changes editorial fit, not the evidence base: no
  independent human cohort, wet-laboratory validation or biological claim was
  added, and the six transcripts remain 0/18 non-significant in the
  pre-specified primary model.
""")
log.append("REPRODUCIBILITY.md <- section 13")

print("OK, %d guarded updates:" % len(log))
for x in log:
    print("  -", x)

# 从「v1.1 投稿就绪稿」到「已投稿」：逐步操作与验收

> 本文件只描述**操作顺序**。所有对外发布动作（建仓库、授权 Zenodo、点 Publish、投稿）
> 必须由作者本人执行；本会话只准备本地文件、不代替作者对外发布。
> **当前状态（2026-11-10）**：cold-read v1.1 = **403/403 PASS**；投稿闸门 FIX = **0**；
> 12 项声明已填 **11** 项，仅剩 #3 / #7（同一个代码 DOI，等 Zenodo 归档后一次性回填三处）；
> 八项行政确认已由作者答复并记入 `DECISION_LOG.md`。**剩余链路 = 发布包 → tag v1.1 →
> Zenodo DOI → 回填 → 版式重排 + cover letter → 投稿**（目标 Collection 截止 2027-01-04）。

---

## 第 0 步 · 先看清哪一步卡在哪

| 优先级 | 事项 | 谁能做 | 是否阻塞投稿 |
|---|---|---|---|
| 1 | GitHub tag v1.1 → Zenodo 出 DOI → 回填三处 | 作者本人发布；agent 准备与回填 | 是 |
| 2 | 31 条保留文献用 Zotero 统一为目标期刊格式 | 作者本人 | 是 |
| 3 | Word 版与期刊版式（TSV→表格、SVG→图形） | agent 可转换，版式规范需作者确认 | 是 |
| 4 | cover letter + 机构权限下的 iThenticate/Turnitin 查重 | 作者本人 / 机构 | 是 |
| 5 | 投稿当日逐刊政策复核（APC、预警名单、分区） | 作者本人 | 是 |

**先做 1，再做 2，最后 3–5**。原因：DOI 会写进正文，正文定稿后才能做版式转换与查重；
Zotero 改动会影响引用编号，必须在 cold-read 最终版之前完成。

---

## 第 1 步 · 作者与声明（已完成，改法在此）

**单一事实源 = `data/author_profile.json`。稿内不手改作者信息**，改 JSON 后重跑：

```bash
cd /c/Users/china/WorkBuddy/2026-11-08-19-05-23/work/data
D:/anaconda3/python.exe apply_v11.py          # 由 v1.0 重生成 v1.1（v1.0 不被覆盖）
D:/anaconda3/python.exe cold_read_v11.py      # 期望 403/403
D:/anaconda3/python.exe preflight_v10.py v1.1 # 期望 FIX 0
```

- 作者 4 人、单位 1 个（四人同属 ¹，作者 2026-11-10 确认单位只有一个且完全一致）、
  通讯作者 Weihai Xu（ORCID 0000-0002-6566-2828）、资助 YK2023033。
  学位（PhD, MD / MB）存于 JSON，按 BMC 版式不印在 Title page；需要印时把
  `"render_degrees": true` 重跑即可。
- CRediT 由 `authors[].credit` 聚合，渲染顺序按 CRediT 官方 14 类；**分工已由作者确认（2026-11-10）**，
  如日后调整改 `authors[].credit` 重跑 `apply_v11.py` 即可。
- 声明 #5（伦理）、#10（COI）、#11（AI 工具）、#6（GEO 引用）、#4（Table S15 呈现）已由脚本写入事实性文本。
- 10 处 `[UNVERIFIED]` 按 `DECISION_LOG.md` 的决定**全部保留**，不得静默删除。

---

## 第 2 步 · 生成发布包（本机执行）

```bash
cd /c/Users/china/WorkBuddy/2026-11-08-19-05-23/work/data/release
D:/anaconda3/python.exe build_release.py                                # 写 UPLOAD_MANIFEST.tsv + DOWNLOAD_INPUTS.md + 状态检查
D:/anaconda3/python.exe build_release.py --build --zip --verify         # 生成 release_bundle/ 与 zip，并逐文件校验 sha256
D:/anaconda3/python.exe build_release.py --build --include-inputs       # 可选：连同 6 矩阵 + 3 annot 一起打包
```

**默认排除**：`chunks*/`（463 个 .bin 分块）、`Rpackages/`、`Rlib/`、`__pycache__/`、
`_selftest*/`、`results_trial*/`（合成/调试数据，禁止引用）、`*.log`、
`*.PARTIAL-DO-NOT-USE`、`GPL5175_platform_prefix.txt`、以及原始 `*.gz`。
原始 GEO 输入默认**不再分发**：包内 `DOWNLOAD_INPUTS.md` 给出重新下载命令，
`tables/file_manifest.csv` 给出每个输入的 sha256。若确认 GEO 再分发条款后再用 `--include-inputs`。

> 发布包只含代码、结果表、图、补充表与文档，**不含稿件正文**——稿件由期刊系统接收，
> 因此不存在「包内稿件写着待回填 DOI」的循环依赖。

---

## 第 3 步 · GitHub 仓库 + 版本锁定

把 `release_bundle/` 的内容作为仓库根目录（`.zenodo.json` 必须位于仓库根目录，
Zenodo 的 GitHub 集成会自动读取它）：

```bash
cd <path-to>/release_bundle
git init
git add -A
git commit -m "Reproducibility package for the v1.1 re-analysis"
git tag -a v1.1 -m "v1.1: metadata-audit checklist (Table S19) + donor-level OLS M2 + S13/S15/S16/S17/S18 sensitivity and boundary analyses"
git remote add origin https://github.com/<AUTHOR>/<REPO>.git
git push -u origin main
git push origin v1.1
```

然后在 GitHub 上从 `v1.1` 建一个 Release。**tag 一旦发布就不要覆盖**：
稿件里所有数字都对应这个不可变版本。若发现包内错误，改完打 `v1.1.1`，不要强推原 tag。

---

## 第 4 步 · Zenodo 生成 DOI（两条路径，任选其一）

- **GitHub 集成（推荐）**：登录 Zenodo → 账户菜单 → *GitHub* → 授权并 *Enable* 该仓库
  → 第 3 步的 Release 会自动创建一个 deposition → 核对 `.zenodo.json` 带入的元数据
  （version 应为 `v1.1`，4 个 creator，licence `cc-by-4.0`）→ *Publish* → 得到 `10.5281/zenodo.XXXXXXX`。
- **手动上传**：Zenodo → *New Upload* → 上传 `release_bundle.zip` → 按 `.zenodo.json`
  逐字段填写 → *Publish* → 得到 DOI。
- 建议先在 `sandbox.zenodo.org` 演练一次（sandbox 的 DOI 不可用于正式投稿）。
- 验收：DOI 可解析；deposition 里的文件清单与 `UPLOAD_MANIFEST.tsv` 一致；
  `results/04_deg_primary_M2.csv` 的 sha256 与正文/cold-read 台账一致。

---

## 第 5 步 · 回填 DOI（三处一致），再跑最终闸门

拿到 DOI 后**一条命令回填**，不要手改（手改容易出现三处不一致）：

```bash
cd /c/Users/china/WorkBuddy/2026-11-08-19-05-23/work/data
D:/anaconda3/python.exe backfill_doi.py 10.5281/zenodo.XXXXXXX   # Methods 2.6 / Data availability / Code availability
D:/anaconda3/python.exe cold_read_v10_postdoi.py                 # 期望 410/410（DOI 后专用基线）
D:/anaconda3/python.exe preflight_v10.py v1.1                    # 期望 FIX 0 / PENDING 0
```

- `backfill_doi.py` 会校验格式（`10.5281/zenodo.<digits>`）并拒绝在仍有其他占位符时写入。
- 回填后 `cold_read_v11.py` 的 `I 可复现` 断言（"尚未填 DOI"）会 FAIL，**这是设计如此**，
  最终闸门改跑 `cold_read_v10_postdoi.py`；两者互不覆盖对方的报告。
- **不得改动任何统计数字、Figure 1–2、Table 1–4、58 条文献编号。**

---

## 第 6 步 · Zotero 统一 31 条保留文献（不要改编号）

用 `references_v05.tsv`、`literature_ledger.tsv`、`verified_references.tsv` 建库，
只统一**格式**（著者、年份、卷期页、DOI），**保持 1–58 的编号与首次出现顺序不变**：
v0.5 起 cold-read 的 E 组会做「正文每个编号有条目 + 每条条目被引用 + 编号连续」双向对账，
改编号会直接触发 FAIL。27 条新增文献已逐条经 PubMed/Crossref/GEO 核验，无需重查；
31 条保留文献仍沿用原稿文本，需作者逐条回链确认。

---

## 第 7 步 · 版式、cover letter、查重、投稿

1. `figures/Figure1–2.svg` → 目标期刊图形格式（TIFF/EPS/PDF，按 Artwork 规范）；
   `tables/Table1–4 + S1–S19.tsv` → 投稿表格。**v1.1 正文已无 Figure 3–5 引用**
   （cold-read J 组已断言），无需再删段落（补充材料 S6 的 `[UNVERIFIED]` 溯源说明要保留）。
2. 按 `青光眼生信稿件_版式重排映射_v1.0.md` 生成 Word 版；按 `cover_letter_v1.1_draft.md`
   填 4 处占位（作者、单位、日期、期刊编辑），明确说明这是**方法学/数据质量重评估 + 阴性结果**，
   不是新的疾病机制发现，并说明 Table S19 的可迁移性。
3. 机构权限下跑 iThenticate/Turnitin；cold-read 不能替代相似度自查。
4. 投稿当日复核：APC 与 OA、单位预警名单、中科院/JCR 分区、Collection 截止日期。
   Collection（*Reproducibility, transparency, and open science*）截止 **2027-01-04**；
   赶不上就投普通 Research article，无截止压力——**不要为赶时间跳过声明与核验**。

---

## 发布红线（任何一步都不得越线）

- 不得把 `probe not mapped` / `no gene annotation` 写成阴性验证；
- 不得把同系列三平台称为独立复现；不得把 ROC/AUC 写成诊断价值；
- 不得调阈值「找回」六基因；不得把 limma 的 128 / 709 / 2 或 M2b 的 95 / 516
  静默提升为主结果（主结果只有 `results/` 的预指定 OLS M2）；
- 不得把未进入主模型的 age/sex 写成已校正；
- 不得上传 `.PARTIAL-DO-NOT-USE`、合成自测 `_selftest*` / `results_trial*` 或残缺日志；
- 不得把 GSE27276 跨组织比较写成独立复现、验证队列或「已补上独立队列」；
  该系列疾病与取材方式/死后延迟完全混杂（phi = 1.0，设计秩 2/4）；
- 不得把 `results_external/` 的三口径结果并入 `results/` 或主表 0/18；
- 不得把方法学定位再写回「六基因发现」叙事；Table S19 是主交付物，
  六个转录本只是 worked example；
- 稿件正文保持期刊中立，不写死刊名、分区、影响因子或 APC；这些只在选刊材料中出现，
  且须按投稿当日官方页面复核；
- 原稿 `Manuscript.docx` 全程只读，从未修改。

**即使 1–7 全部完成，无湿实验/独立队列、GPL5175 无基因级验证这几条科学缺口
依然存在。** 改投方法学 / 数据质量审计栏目后，「创新性不足」这一 desk-reject
理由的权重明显下降（目标栏目按科学有效性而非 perceived impact 评估），但**这是
栏目匹配度的改变，不是数据或验证的补强**。选刊核验记录与待作者确认清单见
`青光眼生信稿件_方法学栏目定位与改稿方案.html`；**最终以本单位科研管理部门
当年目录为准**。

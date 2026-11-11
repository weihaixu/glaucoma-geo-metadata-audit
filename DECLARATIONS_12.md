# 12 项作者声明工作表（配套 `青光眼生信稿件_全文重写稿_v1.1.md`）

> **v1.1 状态（2026-11-10）**：作者与单位、通讯作者、CRediT、资助四项已按 `data/author_profile.json`
> 重生成；伦理、COI、AI 工具、GEO 引用、Table S15 呈现五项已写入事实性文本。
> **12 项中 11 项已落定，仅剩 #3 / #7（同一个代码 DOI）待 Zenodo 归档后回填。**
> 本表保留为逐项验收依据；下拉清单中的行号来自 v0.7，**请按占位符文本搜索定位，不要按行号跳转**。

> **v1.0 更新（2026-11-09）**：表内行号来自 v0.7；v1.0 因新增 S13/S15/S16 段落已整体偏移，**请按 `[AUTHOR INPUT REQUIRED: ...]` 占位符文本搜索定位**，不要按行号跳转。占位符仍为 12 处、内容未变。**本表不代填任何作者身份、基金、利益冲突或 AI 工具信息。**
> 分类：`本人` = 只能由作者/单位确认；`DOI 后` = 拿到 Zenodo DOI 后可回填（agent 可代笔）；
> `重跑后` = 需新的外部数据/分析；`本机` = 格式转换类，可在本地执行。

| # | v0.7 位置（行号已过期，按占位符定位） | 必填内容 | 分类 | 可复制句式 / 验收标准 |
|---|---|---|---|---|
| 1 | line 5 · Title page `Authors and affiliations` | 全体作者姓名、单位、顺序 | 本人 | 按目标期刊 Title Page 模板；**缺项直接退稿** |
| 2 | line 7 · `Corresponding author` | 姓名、单位、邮箱、ORCID | 本人 | `Name, MD, PhD; affiliation; email; ORCID 0000-0000-0000-0000`；部分期刊无 ORCID 拒收 |
| 3 | line 99 · Methods 2.6 末 | 公开代码仓库 DOI / URL、版本锁定文件 | DOI 后 | `Code and derived tables are archived at Zenodo (doi:10.5281/zenodo.XXXXXXX) under [licence].` + 引用 `release/requirements.txt`、`release/ENVIRONMENT.md` |
| 4 | line 155 · Results 3.2 | 确认 Table S15 边界检查是否作为补充材料呈现 | 本人（决定呈现方式） | GPL5175 映射已在 v0.8 补齐（Table S15，0/6 显著，q=1.0），但**这是边界检查，不得写成验证或独立复现，也不得并入主结果 0/18**；`results/06_external_validation.csv` 仍记录 `probe not mapped`，两份输出不得合并 |
| 5 | line 193 · `Ethics` | IRB 豁免表述是否符合作者单位政策 | 本人 | `The analysis used de-identified, publicly available GEO data; institutional review board approval was not required for the secondary analysis.` |
| 6 | line 195 · `Data availability` | 3 个 Series + 4 个平台的 GEO 标准引用与 `acc.cgi?acc=` URL | DOI 后（引用格式需本人核对期刊要求） | `GSE9944, GSE2378, GSE45570; GPL8300, GPL571, GPL91, GPL5175; NCBI GEO (accessed 8 November 2026).`；GPL5175 须注明「无官方注释文件」 |
| 7 | line 197 · `Code availability` | 仓库 URL / DOI / tag / 版本锁定 | DOI 后 | 与 #3 保持一致的 DOI；附 `README.md`、`REPRODUCIBILITY.md`、`tables/file_manifest.csv`、`release/requirements.txt` |
| 8 | line 199 · `Author contributions (CRediT)` | 14 类角色逐位作者标注 | 本人 | `Conceptualization / Data curation / Formal analysis / Funding acquisition / Investigation / Methodology / Project administration / Resources / Software / Supervision / Validation / Visualization / Writing - original draft / Writing - review & editing`；须全体作者确认 |
| 9 | line 201 · `Funding` | 基金名称与编号，或明确无资助 | 本人 | `This work was supported by ... (grant no. ...).` / `The authors received no specific funding for this work.` **无基金也须明写** |
| 10 | line 203 · `Conflict of interest` | 全体作者利益冲突结论 | 本人 | `The authors declare no competing interests.` |
| 11 | line 205 · `Use of AI-assisted tools` | 工具名称、参与环节、人工复核方式 | 本人 | 语言辅助：`During the preparation of this work the authors used [tool name] for language editing and text restructuring. The authors reviewed and edited all output and take full responsibility for the content of the publication.`；若涉及分析代码/统计解释，须额外写明具体环节与可复现脚本位置（`reanalysis.py`、`reanalysis_m2b.py`、`run_limma_replication.py`、`genelevel_sensitivity.py`）；多数期刊不接受 AI 列为作者 |
| 12 | line 363 · Figure legends 后说明 | TSV→投稿表格、SVG→期刊图形格式、删除 Figure 3–5 残留 | 本机（版式规范需本人确认目标期刊） | 按目标期刊 Artwork/Table 规范转换；**删除前确认**：v0.7 正文已无 `Figure 3–5` 引用（cold-read J 组断言），补充材料 S6 关于原稿表格的 `[UNVERIFIED]` 说明需保留或显式改写 |

## 另有两类占位符不属于这 12 项

- **10 处 `[UNVERIFIED]`**（v1.0 实测行号 20/85/89/130/180/184/188/206/382/414）：原稿 DAVID/KOBAS/miRNA 预测等下游结果，本轮未重跑。保留为溯源说明，**数字不得当作重跑结果**，也不得静默删除后当作已验证；处置三选一见 `青光眼生信稿件_投稿前操作清单_v1.0.md` §3。
- **2026-11-10 补充**：回填 #6/#7 前必须先完成稿内 6 处 P0 修补（尤其 Data availability 的 "family-SOFT extraction was not completed" 已过时、Code availability 脚本清单停留 v0.7 且**不得删除 `cold_read_v07.py`**）。回填 DOI 后 `cold_read_v10.py` 有 **5 处**断言会 FAIL，改跑 `cold_read_v10_postdoi.py`。

## 验收

填完后逐条检查：12 个 `[AUTHOR INPUT REQUIRED: ...]` 是否都有实质内容；DOI 是否可解析；
全体作者是否确认 CRediT / COI / AI 披露；Target journal 的 AI 与数据可用性政策是否在投稿当日复核过。
**回填 DOI 会触发 `cold_read_v10.py` 的 4 处断言冲突，见 `release/PUBLISH_STEPS.md` 第 5 步（已按 v1.0 流程改写）。**
v1.0 新增 Table S17/S18 与 `results_external/`；它们不改变 12 项声明的内容，但第 #6 项的数据可用性列表若提及外部系列，须注明 GSE27276 为**跨组织方向一致性练习**、GPL2507 为官方 annot，且不构成独立复现。

**v1.0 栏目重定位补充**：新增 Table S19（可复用审计清单模板）与 Methods 2.8，稿件定位为方法学 / 数据质量审计。12 项声明的内容不变，但第 #6 项数据可用性应同时列出 `geo_metadata_audit.py`、`results_audit/` 与 Table S19；第 #11 项 AI 工具披露须按目标期刊当期政策填写；cover letter 须说明「为何是方法学而非生物学论著」。稿件正文保持期刊中立，刊名、分区、APC 只在选刊材料中出现。

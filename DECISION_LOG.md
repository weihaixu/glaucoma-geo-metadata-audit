# 主模型决策台账 · DECISION LOG

**决策项**：M2b（补回自由文本 age/sex 的协变量完整模型）是否升为主模型？
**决策结果**：**保持 A** —— `results/` 的预指定 M2 继续作为唯一主结果；`results_m2b/` 仅作敏感性分析。
**决策人**：稿件作者（用户）
**确认时间**：2026-11-09
**记录人**：本会话（agent 未替作者拍板，仅执行确认结果）

---

## 1. 两个选项的对照（数字均来自真实 GEO 重跑）

| 项目 | A（已确认） | B（未采纳） |
|---|---|---|
| 主结果目录 | `results/`（预指定 M2） | `results_m2b/` |
| 设计矩阵（GSE9944 两平台） | `intercept, glaucoma, race_Caucasian` | 再加 `age_z, sex` |
| GSE9944-GPL571 M2 DEG | **114** | 95 |
| GSE9944-GPL571 M3 DEG | **640** | 516 |
| 六基因 BH q 范围 | **0.145–0.691** | 0.077–0.893 |
| 六基因显著数 | **0 / 18** | 0 / 18 |
| 分支 A（方法学/数据质量重评估） | 成立 | 成立 |
| 需同步改动的文件 | **0 处** | 7 处（见第 3 节） |

## 2. 采纳 A 的理由

1. M2 是**预指定**主模型，M2b 是在发现"GSE9944 把 ancestry/age/sex 写成一条自由文本、结构化解析漏掉 age/sex"之后补做的**敏感性分析**。把事后补做的模型升为主模型，容易被审稿人质疑"事后换模型"。
2. 两版核心结论完全一致（六基因 0/18 显著、方向反转、分支 A 不变），换模型不带来科学结论上的收益。
3. A 保持 `results/` 可原样复跑，已交付的 Figure 1–2、Table 1–4、Table S1–S4、v0.4/v0.5 的 cold-read 断言全部继续有效。
4. 解析缺陷没有被掩盖：Methods 2.5 如实写明"Numeric age and sex did not enter any model in the primary run"，Abstract 与 Results 3.2 报告 M2b 结果，Table S2–S3 给出逐项对照。这比"看起来更完整"更重要。

**前提**：作者已阅读第六轮报告 §6 与第七轮报告 §2 的 A/B 对照与代价说明。

## 3. 若日后改选 B，必须同步修改的 7 处（保留备查，本次不执行）

1. Abstract Results：114→95、640→516、q 0.145–0.691→0.077–0.893；M2b 一句改写。
2. Results 3.1 的 Table 1 与 Figure 1B（DEG 柱状图需重绘）。
3. Results 3.2 六基因主表、Table 2、Figure 2A–C 与 Table S1（全探针 CI 需从 M2b 重算）。
4. Table S2 / S3 的"主模型 vs 敏感性"对照方向与标题。
5. Methods 2.5：删除 "Numeric age and sex did not enter any model" 等事实修订句。
6. `cold_read_v*.py` 的 J 组反面断言（"不得声称已校正 age/sex"）与 K 组 M2b 对账方向。
7. `README.md`、`REPRODUCIBILITY.md`、`facts_for_manuscript.md`、`decision.json`、`file_manifest.csv`。

## 4. 本次决策的实际影响

- **主结果数值：零改动。** `results/` 目录下 13 个文件、`results_m2b/`、Figure 1–2、Table 1–4 与 Table S1–S4 全部保持字节不变。
- 第七轮报告 §1/§2 中"待作者拍板"的状态已被本台账与第八轮报告取代；历史报告作为过程记录不修改。
- v0.6 版本说明第 7 条由"待决策"改为"已确认保持 A"；`REPRODUCIBILITY.md` 第 5 节与 `README.md` 同步。
- `cold_read_v06.py` 增加"决策 A 已确认、M2b 仅敏感性、不得出现待决策字样"的断言。
- 决策本身不解决任何审稿意见；创新性不足、无湿实验/独立队列、GPL5175 无基因级验证、缺代码公开 DOI、文献格式统一与正式查重仍然待办。**投稿可行性不变：仍不可投稿。**

## 5. 与 N1 整改的关系（同轮完成，但不属该决策）

第二轮模拟预审发现的 N1（ROC/AUC 用 array-level）在本轮另行重算：`diagnose_n1.py` → `results_diagnostics/`。结果为 Δ=0（GSE2378-GPL8300 一供体一芯片），故主结果 `07_roc.csv` 也无需改数字；修订只涉及表述与新增 Table S7/S8。两项工作都遵循"不覆盖 `results/`"的原则。

## 2026-11-10 · 投稿行政八项确认（作者答复）

| # | 事项 | 作者答复 | 影响 |
|---|---|---|---|
| 1 | 用途与截止 | 单位考核一般要求，无硬截止 | 不为结项倒排，质量优先 |
| 2 | 是否投 Collection | 投 *Reproducibility, transparency, and open science*（截止 2027-01-04） | 8 周内完成声明、DOI 链路与版式 |
| 3 | APC 预算与 OA | 有预算（约 $2000+），全 OA 可接受 | BMC MRM 无支付障碍 |
| 4 | 单位考核口径 | 无硬性要求，SCI 收录即可 | 选刊底线宽松，但分区/APC 仍建议投稿当日复核 |
| 5 | 创新性自评 | 方法学框架 + 领域案例两者并重 | 与 v1.0「框架 + worked example」结构一致；但生物学侧主结果为 0/18 阴性，cover letter 不得写成生物学发现 |
| 6 | 周期上限 | 8 周内投稿（2026 年内） | 与 Collection 截止匹配 |
| 7 | 预印本 / AI | 不挂预印本；按期刊要求声明 AI 使用 | 稿内 AI 声明占位须在 Declarations 阶段填写 |
| 8 | 预警名单 | 已核对，BMC MRM 不在名单 | 投稿当日再复核一次 |

结论：投稿目标锁定 BMC Medical Research Methodology · Research article · Reproducibility Collection（2027-01-04）。剩余阻塞 = 12 项声明 + 10 处 UNVERIFIED 处置 + zenodo creators/DOI 链路 + 4 处稿内 FIX。

## 2026-11-10 · v1.1 投稿就绪修补的六项决定

| # | 决定 | 理由 | 落地 |
|---|---|---|---|
| 1 | 摘要压到 347 词并补 `Trial registration: Not applicable` | 目标刊硬限制 350 词；结构化摘要必需子节 | `apply_v11.py` F1 |
| 2 | 10 处 `[UNVERIFIED]` **全部保留**，不改写、不删除 | 这些数字来自原稿、本轮未重跑；删除会让读者误以为已重跑验证，保留标记是唯一诚实的处置 | 未改稿，cold-read T/K 组继续断言计数 = 10 |
| 3 | Data availability 的 GPL5175 表述改为「无官方注释 → 本地重建映射（316,919 行 / 33,475 探针），仅用于 Table S15 边界检查」 | 原句「family-SOFT extraction was not completed」与 v0.8 实际完成状态矛盾 | `apply_v11.py` F2 |
| 4 | Code availability 与 Methods 2.6 脚本清单补齐至 v1.1（含 v08/v09/v10/v11、external_concordance、geo_metadata_audit、preflight、postdoi 补丁） | 原清单停在 v0.7，与发布包不符 | `apply_v11.py` F3 |
| 5 | Table S15 呈现方式定为「仅补充材料中的边界检查」 | 不写验证、不进主结果 0/18 | `apply_v11.py` F4 |
| 6 | 修掉 3.2 节重复句与游离反引号 | 历史编辑遗留，属明显文本缺陷 | `apply_v11.py` F5 |

配套：5 项身份类声明改为由 `data/author_profile.json` 单点驱动（`apply_v11.py` 注入），DOI 由 `backfill_doi.py` 三处一致回填，Zenodo creators 由 `sync_zenodo_creators.py` 从同一 profile 生成。假身份全链路测试达 410/410，测试产物已清理。

## 2026-11-10 · v1.1 身份类声明填写（作者提供）

作者在会话中给出 4 位作者、单位、通讯作者与基金信息；**全部经 `data/author_profile.json` 单点注入**，
稿内无手改。填写后 v1.1 = `8a1594a7497a…`（v1.0 仍为 `53f53d91619b…`，零改动）。

| 项 | 内容 | 处置 |
|---|---|---|
| 作者顺序 | Weihai Xu、Qiliang Li、Qiang Ma、Yanchun Guo | 四人同属单位 ¹（作者 2026-11-10 确认：单位只有 1 个、四人完全一致） |
| 单位 | Department of Ophthalmology, Binhai County People's Hospital, Kangda College of Nanjing Medical University, Yancheng, Jiangsu Province 224500, China | 作者确认唯一单位，不做 ¹² 拆分；邮编从 `China,224500` 规范为 `… Province 224500, China` |
| 通讯作者 | Weihai Xu / ¹ / xwh1979@126.com / ORCID 0000-0002-6566-2828 | 稿内三要素齐备 |
| 资助 | Yancheng Municipal Health Commission, Jiangsu Province, China（grant no. YK2023033） | 按 BMC 句式写入 Funding |
| 学位 | Xu：PhD, MD；Li/Ma/Guo：MB | **BMC 版式不印学位**；存入 JSON，投稿系统逐人字段用；`render_degrees: true` 可一键印出 |
| CRediT | Xu：概念/方法/软件/形式分析/初稿/监督/项目管理/经费；Li：调查/数据整理/验证/审阅；Ma：调查/数据整理/可视化/审阅；Guo：调查/验证/审阅 | **已由作者确认按此执行（2026-11-10）**，不再改动；如日后调整，改 `authors[].credit` 后重跑 `apply_v11.py` |

连带变更（均为机制性，不涉统计）：
1. `apply_v11.py` 支持 `degree` / `family` / `given` / `render_degrees`，CRediT 渲染顺序改为官方 14 类；
   版本说明新增第 19 条、页脚身份类计数改为动态（4/5，DOI 项待填）。
2. `cold_read_v11.py` 把「身份类占位符 = 5」的写死断言改为**由 `author_profile.json` 实时推导**，
   并新增一条「作者/通讯/CRediT/资助已写入且无占位残留」正向断言 → 402 → **403/403**。
3. `sync_zenodo_creators.py`：licence 改为 `{"id": ...}` 结构（原为裸字符串，会让 Zenodo 拒收）、
   支持 `family, given`、新增 `--version/--pass` 同步 `.zenodo.json` 的 version / title / cold-read 声明。
4. `preflight_v10.py`：版本检查改为跟随稿件版本；八项行政确认从 `DECISION_LOG.md` 读出后由
   `PENDING` 降为 `NOTE`；DOI 待办文案改为跟随版本。
5. `release/PUBLISH_STEPS.md`、`release/DECLARATIONS_12.md` 同步到 v1.1；`build_release.py` 的
   MANUSCRIPT 指向 v1.1。发布包 202 文件 / 107.7 MB，`--build --zip --verify` = 0 处 sha256 不符、0 个多余文件。

**结果**：闸门 READY 34 / PENDING 3 / FIX 0 / NOTE 11；PENDING 三项全部指向同一个代码 DOI。
剩余链路 = 发布包 → GitHub tag `v1.1` → Zenodo DOI → `backfill_doi.py` → postdoi 410/410 → 版式 + cover letter → 投稿。

# 青光眼生信稿件 · 统计重跑运行手册 v2.4

## 0. 状态（2026-11-08 更新，必读）

- **6 个 series matrix 已全部下载并通过 gzip 完整性校验**：GSE9944 三平台、GSE2378 两平台、GSE45570，合计约 6.0 MB。
- 本机出口对 NCBI 限速（约 130 B/s 至 20 KB/s 波动），整文件下载会被掐断；最终用 `parallel_fetch.py` 的 **64 KiB HTTP Range 分块 + 断点续传 + 低并发** 完成。所有分块缓存在 `chunks64/`，可重复运行。
- `results/` 为**真实数据**跑出的结果；`_selftest_results/` 与 `results_trial*/` 分别是合成数据自测与调试中间产物，**禁止引用其数字**。
- **GPL5175 在 GEO 官方没有 `annot.gz`**（目录 404、平台记录无 supplementary_file）。`fetch_gpl5175_annot.py` 曾从 4.5 GB 的 `GPL5175_family.soft.gz` **开头**增量解压平台表，但**当时未完成**（仅得到 `GPL5175_platform_prefix.txt`，未生成可用的 `GPL5175.annot.gz`）；冻结的主结果 `results/` 中 GSE45570 仍为 `n_probes_mapped=0`、六基因 `probe not mapped`，**不得写成阴性验证**。**【v0.8 更新，见 §17】** 该提取已用 219 个分块补齐，重建的本地映射仅用于 `results_gpl5175/` 的边界检查，不是 GEO 官方注释，也不构成验证。
- 运行前请确认 `results/RUN_REPORT.md` 中每个数据集的 `scale_evidence` 已写进 Methods；`--scale-override NAME=log2|linear` 可显式覆盖。

## 0.1 本次真实运行的命令

```bash
D:/anaconda3/python.exe parallel_fetch.py --workers 3 --rounds 4   # 下载 6 矩阵 + 3 注释
D:/anaconda3/python.exe fetch_gpl5175_annot.py                     # 生成 GPL5175 注释
D:/anaconda3/python.exe reanalysis.py --out results                # 真实重跑
D:/anaconda3/python.exe summarize_results.py results               # 生成回填事实表
D:/anaconda3/python.exe reanalysis.py --selftest                   # 回归自测（合成数据）
```

## 1. 文件清单

| 文件 | 作用 |
|---|---|
| `reanalysis.py` | 主分析管线：解析 → QC → 供体级合并 → 协变量模型 → FDR → 验证 → ROC |
| `fetch_geo.py` | 直连下载器（适合网络良好时） |
| `fetch_geo_chunked.py` | HTTP Range 分块 + 断点续传下载器（适合限速网络） |
| `inspect_geo.py` | 下载后检查样本元数据、表达值量纲、探针 ID |
| `audit_pseudoreplication.py` | 从已核验的 GSM 标题量化伪重复 |
| `parallel_fetch.py` | **实际使用的下载器**：64 KiB Range 分块、并发、断点续传、gzip 完整性校验 |
| `fetch_gpl5175_annot.py` | 从 GPL5175 family SOFT 开头增量解压平台表，生成缺失的 `GPL5175.annot.gz` |
| `summarize_results.py` | 把 `results/*.csv` 汇总为 `facts_for_manuscript.md`，供稿件回填 |
| `cold_read_v03.py` | 回填后全文稿的 cold-read（数字与真实结果表对账） |
| `GSE9944_gsm_titles_partial.txt` | 官方 GEO 抓取到的前 30 条标题（响应被截断） |
| `pseudoreplication_audit.json` | 伪重复审计结果 |
| `README.md` | 本手册 |

## 2. 环境

已在 `D:\anaconda3\python.exe`（Python 3.9.13）验证：numpy 1.21.5 / pandas 1.4.4 / scipy 1.9.1 / statsmodels 0.13.2 / scikit-learn 1.0.2 / matplotlib 3.5.2 / tabulate。
其他环境需 `pip install numpy pandas scipy statsmodels scikit-learn matplotlib tabulate`。

## 3. 数据获取

把下列文件放到本目录（总约 5–15 MB）：

```
https://ftp.ncbi.nlm.nih.gov/geo/series/GSE9nnn/GSE9944/matrix/GSE9944-GPL8300_series_matrix.txt.gz
https://ftp.ncbi.nlm.nih.gov/geo/series/GSE9nnn/GSE9944/matrix/GSE9944-GPL571_series_matrix.txt.gz
https://ftp.ncbi.nlm.nih.gov/geo/series/GSE9nnn/GSE9944/matrix/GSE9944-GPL91_series_matrix.txt.gz
https://ftp.ncbi.nlm.nih.gov/geo/series/GSE2nnn/GSE2378/matrix/GSE2378-GPL91_series_matrix.txt.gz
https://ftp.ncbi.nlm.nih.gov/geo/series/GSE2nnn/GSE2378/matrix/GSE2378-GPL8300_series_matrix.txt.gz
https://ftp.ncbi.nlm.nih.gov/geo/series/GSE45nnn/GSE45570/matrix/GSE45570_series_matrix.txt.gz
```

探针注释（用于把 Affy 探针映射到基因符号，六个关键基因必须能映射）。**实测修正**：GPL5175 的 `annot/` 目录返回 404，GEO 平台记录也没有 supplementary annotation；实际需要的是 GPL8300 / GPL571 / GPL91 三个：

```
https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPL8nnn/GPL8300/annot/GPL8300.annot.gz
https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPLnnn/GPL571/annot/GPL571.annot.gz
https://ftp.ncbi.nlm.nih.gov/geo/platforms/GPLnnn/GPL91/annot/GPL91.annot.gz
```

GSE45570（GPL5175）的基因符号由 `fetch_gpl5175_annot.py` 从 `GPL5175_family.soft.gz` 的平台表生成同名 `GPL5175.annot.gz`，不依赖把 4.5 GB 文件整个下载。

网络良好时：

```bash
python fetch_geo.py                # 直连（本次未成功）
python parallel_fetch.py --workers 3 --rounds 4   # 本次实际使用，推荐
python fetch_gpl5175_annot.py      # GPL5175 专用
python inspect_geo.py              # 检查量纲与元数据
```

Windows curl 需加 `--ssl-no-revoke`（否则 Schannel 报 `CRYPT_E_REVOCATION_OFFLINE`）：

```bash
curl.exe -L --ssl-no-revoke -O <URL>
```

> 也可以直接在 GEO 网页点 "Series Matrix File(s)" 下载后手工放入本目录。文件名保持原样即可。

## 4. 运行

```bash
python reanalysis.py --selftest                 # ① 先自测（不需要任何数据）
python reanalysis.py                            # ② 真实数据，默认 GEO 值已 log2
python reanalysis.py --scale linear             #    若 Methods 声明是线性强度需 log2
python reanalysis.py --data DIR --out DIR       #    自定义目录
```

**`--scale` 必须写进 Methods。** 默认 `log2` = 假定 GEO 提供的已是 log2 归一化值；若实际是 MAS5 线性强度，用 `linear`。不要用 `auto`，它会改变 log2FC 阈值判定。

## 5. 输出（`results/`）

| 文件 | 内容 |
|---|---|
| `01_sample_metadata.csv` | 每个 GSM 的供体、技术重复、组别、种族、年龄、性别；**独立供体数在这里精确落定** |
| `02_qc_summary.csv` | 芯片数→供体数、量纲、四组人数、PCA 前 3 主成分、模型是否可拟合 |
| `03_deg_by_model.csv` | M0/M1/M2/M3 四个模型的 DEG 数与残差自由度 |
| `04_deg_primary_M2.csv` | 主模型逐探针 log2FC / p / BH q / 基因符号 |
| `05_six_key_genes.csv` | 六个基因在四个模型中的显著性 |
| `06_external_validation.csv` | GSE2378 / GSE45570 中六基因的复现情况 |
| `07_roc.csv` | AUC、bootstrap 95% CI、标签置换 p |
| `08_sensitivity.csv` | 阈值网格（alpha × |log2FC| × 是否 FDR） |
| `09_platform_overlap.csv` | 跨平台/跨数据集重叠，并标注是否同一 GSE（同系列 = 技术重复，非独立验证） |
| `10_donor_overlap.csv` | **供体 ID 级重叠**（同一供体在不同平台杂交的实锤） |
| `facts_for_manuscript.md` | 自动汇总的可回填事实表：QC、DEG 数、六基因 M2 数值、外部验证、决策分支 |
| `decision.json` | 自动判定的 A/B/C/D 分支 |
| `RUN_REPORT.md` | 自动汇总 + 四条解释规则 |

**`02_qc_summary.csv` 新增列**：`scale_used` / `scale_evidence`（每个数据集的量纲判定依据）、`annotation_file` / `n_probes_mapped`、`race_x_group`（种族×疾病交叉表）、`design_warning`（共线/样本量警告）、`n_glaucoma_donors` / `n_control_donors`。

## 6. 四个模型（并列报告，禁止阈值挑拣）

| 模型 | 分析单位 | 协变量 | 判定 |
|---|---|---|---|
| M0 | 芯片（复现原稿） | 无 | nominal p<0.05, |log2FC|≥0.5 |
| M1 | 供体 | 无 | nominal p<0.05, |log2FC|≥0.5 |
| **M2（主）** | **供体** | **种族/年龄/性别** | **BH q<0.05, |log2FC|≥1** |
| M3 | 供体 | 种族/年龄/性别 | BH q<0.05, |log2FC|≥0.5（敏感性） |

若 GEO 元数据里种族字段缺失或与设计矩阵共线，脚本会**拒绝拟合 M2 并写明原因**，不会猜测或静默降级。OHT 眼被排除在 case-vs-control 之外（不并入对照组）。

## 7. QC 验收门槛（投稿前逐项打勾）

- [ ] `02_qc_summary.csv` 中 `n_donors < n_arrays`，且供体数与 GSM 标题解析一致
- [ ] `race_known / n_donors ≥ 0.8`，否则 M2 不可拟合，投稿定位必须再降级
- [ ] 四组（高加索/非裔 × 正常/青光眼）各供体数明确写出；任一组 n<4 须报告检验效能不足
- [ ] `--scale` 与 Methods 描述一致；表达值范围与所选量纲匹配
- [ ] 六个基因在 `05_six_key_genes.csv` 中均有探针映射（无映射不得宣称验证）
- [ ] 同系列不同平台的重叠在 `09_platform_overlap.csv` 中被标注为技术重复
- [ ] GSE2378 按平台分层：GPL91 仅 2 例（1 G + 1 N），不得与 GPL8300 的 13 例拼成单一矩阵；该数据集无种族/年龄/性别字段，M2 的协变量校正无法在其上执行，须写入 Limitations
- [ ] GSE45570 的 18 例按 6 POAG / 6 OHT / 6 对照分组，OHT 未混入对照
- [ ] 所有数字来自 `results/`，`_selftest_results/` 的内容不得出现在稿件中

## 8. 结果分支决策

| 分支 | M2 后情况 | 动作 |
|---|---|---|
| **A（最可能）** | 六个基因全部 q≥0.05 | 不能称 "key genes"。改为「假设生成式候选优先级」，或把论文重定位为方法学警示（伪重复+种族混杂如何制造 DEG 列表）；如六基因全部消失，建议放弃该叙事 |
| **B** | 1–2 个 q<0.05 且 GSE45570 复现 | 收缩到 1–2 个基因，补 ROC + 最小湿实验，投中低区综合刊 |
| **C** | ≥3 个 q<0.05 且复现 | 保留核心叙事但全程用 candidate / predicted，补实验后可上探专科刊 |
| **D** | M2 后全平台 DEG 极少（<20） | 说明原 820/484/1209 主要是伪重复＋未做 FDR 的产物；不得调阈值找回，应撤下重做或改投数据/方法学论文 |

**无论哪一分支**：都不得把 GSE9944 的三个平台当作独立数据集，不得把 GSE45570 的阴性写成"验证成功"，不得把计算预测的 miRNA 写成实验证据。

## 9. 与全文重写稿 v0.2 的接合

| v0.2 占位符 | 由哪张表填 |
|---|---|
| `[PLANNED]` donor-level / FDR / 协变量校正 | `02_qc_summary.csv`、`03_deg_by_model.csv` |
| `[DATA NEEDED]` DEG 数、log2FC、adjusted P | `04_deg_primary_M2.csv` |
| `[DATA NEEDED]` 六基因精确 P / 效应量 / CI | `05_six_key_genes.csv`、`06_external_validation.csv` |
| `[DATA NEEDED]` ROC / AUC | `07_roc.csv` |
| `[AUTHOR CONFIRM]` 供体数、种族分层 n、批次 | `01_sample_metadata.csv` |
| Methods 的预处理与模型描述 | `--scale` 选择 + 第 6 节模型表 |

填完后需重跑第三轮的 cold-read 数字一致性检查，并重新核对摘要 / Results / Discussion 三处结论强度。

## 10. 已知限制

- 线性回归逐探针拟合 + BH，等价于 limma 的简化版，**没有** empirical Bayes 方差收缩；小样本下比 limma 更保守。若目标期刊要求 limma，请在 R 中用 `limma::lmFit` + `eBayes` 复算，模型矩阵与本脚本一致。
- 批次校正未做（GEO 元数据无批次字段）；若发现批次与组别共线，必须在 Limitations 说明，不可强行校正。**已实测：GSE2378 的 15 个 GSM 横跨 GPL91（2 例）与 GPL8300（13 例），且 brief 记录完全没有 characteristics 字段**，所以该数据集既不能跨平台直接合并，也无法做种族/年龄/性别校正——只能做供体级 + FDR 的简化分析，并如实披露。
- **63 张芯片的真实构成已从 series matrix 精确落定**：GPL571 42 张（21 供体，rep1/rep2 成对）、GPL8300 19 张（16 供体）、GPL91 2 张（2 供体）。GPL571 与 GPL8300 有 **5 个共享供体 ID**（同批 RNA 跨平台杂交），见 `10_donor_overlap.csv`；"同系列多平台取交集 = 独立复现"不成立。
- **实测种族×疾病共线**：GPL571 的 21 个供体仅 3 例青光眼，且全部为 African American（Caucasian 组 9 例全为对照）。该平台 M2 的疾病系数不可解释，其显著探针数不得作为疾病信号引用；`design_warning` 已自动标注。
- GSE2378 的 description 里有年龄/性别，但没有种族字段，M2 的种族校正无法在其上执行；脚本会明确写 `ADJUSTMENT NOT POSSIBLE`，不会静默降级。
- ROC 用单基因表达值 + bootstrap CI + 标签置换，n=12 时区间会很宽，只作探索性结果。
- GSE2378 与 GSE9944 同属 Northwestern / Hernandez 实验室、同为 ONH 星形胶质细胞，供体是否重叠需作者核对原文；在确认前不得称 "independent cohort"。
- 六个基因多探针时取 p 最小者，属于乐观选择；正式稿件应报告所有探针或用中位数聚合。

## 11. v2.1 新增（2026-11-09）：图表、CI、M2b 与可复现清单

- `make_figures_tables.py` 只用 `results/*.csv` 生成 `figures/Figure1–2.{png,svg}`、`tables/Table1–4` 与 `TableS1–3`（含全探针 95% CI、每组 n、M2 vs M2b 对照）。脚本不产生任何合成数值。
- **发现并已记录一处方法学不一致**：`02_qc_summary.csv:adjustment_terms` 显示主模型实际只拟合了 `intercept, glaucoma, race_Caucasian`；GSE9944 把 ancestry/age/sex 写成**一条自由文本** characteristics，通用的结构化列查找没能把 `char_age`/`char_sex` 转成数值，导致 age/sex 静默掉出模型（导出元数据里 `age_num`/`sex_bin` 可用率为 0/96）。
- `reanalysis_m2b.py` 只改 `build_metadata()`，从自由文本补回 age/sex，输出到独立的 `results_m2b/`（`reanalysis.py` 保持不变，保证 `results/` 可原样复跑）。M2b 中 GPL571/GPL8300 的设计矩阵变为 `intercept,glaucoma,race_Caucasian,age_z,sex`。
- **主模型决策已由作者确认：保持 A**（2026-11-09）。`results/` 的预指定 M2 是唯一主结果（GPL571 M2 = 114、M3 = 640、六基因 q = 0.145–0.691）；`results_m2b/` 仅作敏感性（95 / 516 / q 0.077–0.893）。两版均为 0/18 显著，`results/` 与所有主表/主图字节不变。完整决策见 `DECISION_LOG.md`。
- `REPRODUCIBILITY.md` = 环境版本 + 精确复跑命令 + 已知限制；`tables/file_manifest.csv` = 6 个矩阵、3 个 annot、脚本与结果表的 sha256/字节数（31 条）。
- `cold_read_v04.py` 在 v0.3 的 53 项检查上增加图表文件、CI、M2b 数字与"不得声称已做 age/sex 校正"等检查。

## 12. v2.2 新增（2026-11-09）：文献重排、声明、第二轮预审

- **本轮没有重跑任何统计模型**；`results/`、`results_m2b/`、Figure 1–2 与 Table 1–4/S1–4 的数值沿用 v2.1。
- `audit_references.py`：解析原稿 69 条参考文献与 v0.4 的 18 个引用标记（32 个不同编号、37 条未引用），输出 `references_audit.tsv|.json`。
- `verify_literature.py`：从 PubMed E-utilities esummary（按 8 个 PMID 分批，避免 NCBI 静默截断）、Crossref（BH 1995）与 GEO 官方记录核验 27 条新增文献，输出 `verified_references.tsv|.json`。**没有手写或编造任何引用**。
- `apply_v05.py`：由 v0.4 派生 v0.5，31 条保留 + 27 条新增 = 58 条，编号按正文首次出现顺序自动重排；5 处文献占位符与文末待插入说明清零；输出 `references_v05.tsv`、`literature_ledger.tsv`、`citation_remap.json` 与 `青光眼生信稿件_声明填写指南.md`。保留的 31 条仍须作者用 Zotero 统一格式。
- `cold_read_v05.py`：在 v0.4 的 87 项上增加双向引用对账与文献核验，共 **106 项 PASS / 0 FAIL**。
- `青光眼生信稿件_第二轮预审与选刊矩阵.md`：模拟编辑初审 + 3 位审稿人；联网核验 6 本期刊官方投稿政策（BMC Med Res Methodol / BMC Bioinformatics / BioData Mining / PLOS ONE / PeerJ / Scientific Reports）。要点：PeerJ 对公共数据生信研究要求至少两类独立验证，本稿不满足；PLOS ONE 明确接受阴性结果但拒绝无充分理由的衍生研究。
- **第二轮预审新发现 N1**：`07_roc.csv` 的 ROC/AUC 仍用 array-level 表达值，与全文"供体级"主张冲突；需供体级重算或明确降级为探索性。本轮未擅自重跑。
- **M2b 决策在第八轮已落定**：作者确认保持 A，见 `DECISION_LOG.md`；本节"待作者决策"的状态已被取代，历史记录保留。
- `tables/file_manifest.csv` 已纳入本轮新增脚本与台账的 sha256；运行文档以 `REPRODUCIBILITY.md` 第 6 节为准。

## 13. v2.3 新增（2026-11-09）：决策 A 落定与 N1 整改

- 作者确认 **保持 A**：`results/` 的预指定 M2 为唯一主结果，`results_m2b/` 仅敏感性。主结果目录、Figure 1–2、Table 1–4、Table S1–S4 与 `07_roc.csv` 全部字节不变；台账见 `DECISION_LOG.md`。
- `diagnose_n1.py`：用同一探针、只把 ROC 评分单位从芯片换成供体，并与 `results/07_roc.csv` 对账 **6/6 精确一致、Δ=0**（GSE2378-GPL8300 为 13 arrays / 13 donors，一供体一芯片）。因此 N1 不是数值错误，而是**循环论证**：探针在同一批供体上按最小 p 挑选后再算 AUC。Table S7 给出全探针中位 AUC、无选择基因级 AUC、选择膨胀（−0.119 至 +0.190）、bootstrap CI 与 BH 校正后的置换 q。
- 共线量化（Table S8）：phi −0.354 / −0.372、VIF 1.14 / 1.16、条件数 3.76 / 6.29、设计矩阵满秩，但两个平台均有**零单元格**。故全文不再写 "nearly collinear"，改述为结构性失衡；另补出主 QC 未标记的 GSE9944-GPL8300 零单元格（African-American 对照 = 0）。
- 诊断输出在独立 `results_diagnostics/`（3 CSV + 1 MD），另有 `tables/TableS7`、`TableS8`。`results/`、`results_m2b/` 从未被本轮写入。
- `apply_v06.py` → `青光眼生信稿件_全文重写稿_v0.6.md`（纯文本修订：决策表述、ROC/循环论证、共线措辞、Table S7/S8、脚本清单）；`cold_read_v06.py` 增加决策一致性、循环论证、共线数字与"不得称已校正 age/sex"等断言。
- `REPRODUCIBILITY.md` 第 5 节第 3、6 项已标记 RESOLVED，并新增第 7 节；`file_manifest.csv` 纳入本轮新文件。

## 14. v2.4 新增（2026-11-09）：真跑 limma + 基因级敏感性

- **更正一条环境事实**：本机其实有 R 4.2.0（`C:/Program Files\R\R-4.2.0`），只是不在 PATH 里；此前"无 R"结论作废。`install_r_packages.py` 带浏览器 UA 从 Bioconductor 3.15 / CRAN 下载 Windows 二进制包，`setup_rlib.R` 装到项目内 `Rlib/`（limma 3.52.4、statmod 1.5.0），**不改用户 R 库**。
- `run_limma_replication.py`：先用重建的 Python OLS 与主结果 69,513 行 log2FC/se 对账（最大误差 4.4e-16）才允许导出，再调 `limma_replication.R` 跑 `lmFit → eBayes → topTable`；limma logFC 与 OLS 系数最大差 3.3e-14。先验 df 2.25–4.58、总 df 13.28–20.25。
- **limma 结论：分支 A 不变**。六基因 0/18 仍不显著（q 0.116–0.663）；但 DEG 计数 GPL571 M2 114→128 / M3 640→709、GPL8300 M2 0→2。这是敏感性结果，**不回写 Table 1、Figure 1、Abstract**；主模型仍是预指定的 OLS M2。
- `genelevel_sensitivity.py`：把"最小 p 选探针"换成三口径（探针最小 p / 基因内全探针按供体中位数表达重跑 OLS / Simes 合并 p），**每种口径都 0/18 显著**；三平台基因数 9,084 / 13,101 / 9,068。GSE45570 因 GPL5175 无 GEO 注释文件**无法做基因级检验**，如实标 `no gene annotation`，不得写成阴性验证；Simes 因探针相关仅作探索性。
- 新结果在独立 `results_limma/`、`results_genelevel/` 与 `tables/TableS9–S12`；`results/`、`results_m2b/`、`results_diagnostics/` 从未被本轮写入。`apply_v07.py` → v0.7（17 处纯文本修订，58 条文献与主数字不变）；`cold_read_v07.py` 增加 N 组 67 项 → **228/228 PASS，FAIL 0**。
- `REPRODUCIBILITY.md` §3 环境段改写、§5 第 4 项标 RESOLVED、新增 §8；`file_manifest.csv` 纳入本轮全部新文件（含 R 包与 sessionInfo）。

## 15. v2.5 新增（2026-11-09）：投稿前发布准备包 · 第十轮

- **决策 A 不变。本轮零改动**：`results/` 13 个主结果、`results_m2b/`、Figure 1–2、Table 1–4/S1–S12、`file_manifest.csv`、v0.7 正文与 cold-read 报告全部保持字节不变；重跑 `cold_read_v07.py` 仍 **228/228 PASS，FAIL 0**（重跑产生的报告差异已还原为原字节）。
- 新增 `release/`：`.zenodo.json`（creators/licence 仍是 `__AUTHOR_INPUT_REQUIRED__` 占位）、`requirements.txt`（Python 3.9.13 的 7 个包精确版本）、`ENVIRONMENT.md`（R 4.2.0 / limma 3.52.4 / statmod 1.5.0）、`DECLARATIONS_12.md`（12 项声明逐项工作表）、`PUBLISH_STEPS.md`（tag → DOI → 回填 → 查重的 7 步命令）、`build_release.py`、`UPLOAD_MANIFEST.tsv`、`DOWNLOAD_INPUTS.md`。
- `build_release.py` 白名单打包：默认 **137 个文件 / 75.3 MB**，排除 `chunks*/`、`Rpackages/`、`Rlib/`、`_selftest*/`、`results_trial*/`、`*.log`、`*.PARTIAL-DO-NOT-USE` 与原始 `*.gz`（GEO 输入默认不再分发，改用重下载命令 + sha256）；`.zenodo.json` 未填完时判定 NOT READY 并拒绝 `--build`。草稿模式实测 `--build --allow-draft --zip --verify` → zip 26,670,003 字节、**0 处 sha 不一致 / 0 个多余文件**，含占位元数据的草稿包验证后已删除。
- **关键陷阱（务必先读）**：回填真实 DOI 并填完 12 项声明后，`cold_read_v07.py` 的 L68–71、L160–162、L201–202 与 L516 说明会 FAIL，必须派生 `cold_read_v08.py` 改写这 4 处断言（详见 `release/PUBLISH_STEPS.md` 第 5 步）。Zotero 统一文献**只改格式、不改 1–58 编号顺序**，否则 E 组双向引用对账 FAIL。
- 完整操作路径、责任划分、验收清单与发布红线见 `work/青光眼生信稿件_第十轮投稿前操作手册.html`（自包含，可离线打开）。**投稿可行性不变：仍不可投稿**；创新性不足、无湿实验/独立队列、GPL5175 无基因级验证、正式查重等缺口未解决。

## 16. v2.6 新增（2026-11-09）：投稿可行性提升路线图 · 第十一轮

- 主交付 `work/青光眼生信稿件_投稿可行性提升路线图.html`：按模拟评审五维（贡献 30 / 方法 25 / 论证 25 / 写作 10 / 规范 10）把现状 ≈2.6/5 拆成评分卡，给出 **P0 合规（≈2.7）/ P1 低成本实质增强（≈3.4）/ P2 结构性重构（≈4.0）** 三档动作与模拟估计（**不是录用概率**）。结论：只做 P0/P0+润色救不了创新性不足与无独立验证；推荐 **P0 + P1 完整版**，关键是把研究问题从「重分析自己原稿」升级为「公共 ONH 表达谱可重复性审计方法」。
- **P1-a 已真跑**：`power_mde.py` 只读 `results/04_deg_primary_M2.csv` 的 69,513 行主 M2 拟合，用每探针 SE + 残差 df 与非中心 t 求 α=0.05 双侧 / power=80% 的 MDE（**不使用观察效应量**，避免经典 post-hoc power 谬误）；输出到独立 `results_power/` 与 `tables/TableS13_power_mde.tsv|.md`。结果：GSE2378-GPL8300 仅 **43.52%** 探针有能力检出 |log2FC|≥1（GPL571 90.71%、GPL8300 94.24%、GSE45570 95.28%）；六基因 **11/18** 次 |log2FC| < MDE，GPL571 为 6/6。**结论是「不显著不能排除更小效应」，绝不是「有效应」或「等效」**，主结论 0/18 与分支 A 定位不变。
- **P1-b/c/d/e** 为待执行：S14 列出独立队列候选（GSE27276 / GSE138125 / GSE4316 人小梁网、GSE26299 小鼠 ONH、GSE110019 / GSE139605 模型 ONH），**全部标为未核验的规划线索**，样本量/平台/组织须到 GEO 官方核实；GPL5175 平台表补齐命令与成功判据；`geo_metadata_audit.py` 工具化设计（对应 BioData Mining 的 beyond-a-single-dataset）；以及 5 项表述性修订与 7 段式 cover letter。P2 给出独立队列 / 湿实验最小设计 / 改栏目三条路径。
- `release/build_release.py` 的 `RESULT_DIRS` 加入 `results_power`，发布包清单随之刷新；`tables/file_manifest.csv` **本轮仍未改动**（新增 S13/S14 的 sha 由 `release/UPLOAD_MANIFEST.tsv` 记录，v0.8 定稿时再统一并入主台账，避免破坏 cold-read 的 sha 断言）。
- 期刊方向沿用 2026-11-09 官网核验结论（见 `青光眼生信稿件_第二轮预审与选刊矩阵.md` §5），**本轮未重新核验分区/IF/APC/AI 政策/单位预警名单**，正式冲稳保选刊表需作者先确认用途、考核口径、预算、周期等 8 项信息。**投稿可行性不变：仍不可投稿。**

## 17. v2.7 新增（2026-11-09）：P1 逐步执行 · 第十二轮

按 `青光眼生信稿件_投稿可行性提升路线图.html` 的 P1 顺序逐项执行；**决策 A 与主结果零改动**。

- **P1-b 官方核验**：到 NCBI GEO 官方 accession viewer 核实候选，新增 `tables/TableS14_official_verification.tsv|.md`。纠正 3 处：GSE27276 = 13 controls / 15 POAG cases、36 GSM、GPL2507（旧表 19/17、17/19、15/13 作废）；GSE26299 = 40 DBA/2J + 10 D2-Gpnmb+ + 10 young、108 GSM、GPL1261；GSE138125 平台为 GPL21827 且**无**官方 annot.gz。另核实 GSE110019 = 猫 ONH RNA-seq 16 GSM、GSE139605 = 小鼠 ONH 星形胶质细胞 RNA-seq 16 GSM；**GSE105269 是房水 miRNA 芯片，剔除**。所有 accession 仍未做任何差异分析，不得称独立复现。
- **P1-c GPL5175 补齐**：`fetch_5175_parallel.py` 以 8 workers / 219 个 64 KiB 分块补齐完整 SOFT 平台表（13.7 MiB 压缩、87.9 MB 文本、检测到 `!platform_table_end`）；`fetch_gpl5175_annot.py`（MAX_CHUNKS 140→260）生成 `GPL5175.annot.gz`，316,919 行中 33,475 探针有基因符号、六基因 8 个探针。GSE45570 的 22,011 个 transcript cluster 中 17,634（80.11%）可映射。`gpl5175_boundary.py` 在独立 `results_gpl5175/` 做基因级边界检查（排除 6 个 OHT，6 POAG / 6 对照，残差 df 10，17,324 基因 BH），六基因 **0/6 显著（q=1.0）**，见 Table S15。**这是边界说明，不是验证、不是独立复现**；`results/` 未改。
- **P1-d 可复用审计**：`geo_metadata_audit.py` 把五类缺陷做成只读检查（自由文本协变量、组别×祖先零单元格、技术重复/供体重叠、注释可得性、尺度与排除组），对 6 个主 matrix + 1 个外部候选（GSE27276，**仅元数据审计**）输出 159 项指标、`audit_checklist.csv`、`audit_summary.json` 与 Table S16。主输入中自由文本协变量 FAIL 3/6、零单元格 FAIL 2/6（phi −0.354 / −0.462，设计满秩）、供体重叠 WARN 2/6；尺度推断与 `02_qc_summary.csv` 完全一致。外部候选 36 arrays 但 title 不含供体 ID（官方记录有双眼配对与 1 个技术重复），**不能把 36 张芯片当 36 个独立供体**。
- **P1-a 回填 v0.8**：`apply_v08.py` 用 17 处断言式替换从 v0.7 派生 `青光眼生信稿件_全文重写稿_v0.8.md`，并派生 `cold_read_v08.py`（新增 O 组断言）。**cold-read v0.8 = 283/283 PASS / FAIL 0**；v0.7 字节未变（sha `3fcfdbb3d2d2`），主结果 sha 仍 `48876f29f3d0` / `29a75234a169`，`file_manifest.csv`、Figure 1–2、Table 1–4 未动。正文新增 S13 的 11/18 与 43.5%、S15 的 80.11% 边界说明、S16 的五类审计，并修正所有因 GPL5175 补齐而过时的表述（Methods 2.2/2.5、Results 3.1/3.2/3.3、Discussion、Figure 2 图注、补充材料）。
- **发布包同步**：`release/build_release.py` 的 MANUSCRIPT → v0.8、RESULT_DIRS 纳入 `results_audit/` 与 `results_gpl5175/`、排除 `external_inputs/` 与分块缓存；`.zenodo.json` 升 v0.8 并更新描述；`PUBLISH_STEPS.md` / `DECLARATIONS_12.md` 改为「直接在 v0.8 回填 DOI，不再由 v0.7 派生 v0.8」；`DOWNLOAD_INPUTS.md` 追加外部候选输入 sha。
- **仍需作者本人**：填 `.zenodo.json` 的 3 个 creators 占位与 12 项声明 → `build_release.py --build --zip` → GitHub tag **v0.8** → Zenodo DOI → 回填并改 `cold_read_v08.py` 的 4 处断言 → Zotero / Word / cover letter / 查重 / 选刊。**投稿可行性不变：仍不可投稿**；创新性不足、无湿实验与独立队列的缺口未变。完整执行报告见 `青光眼生信稿件_第十二轮P1执行报告.html`。


## 18. v2.8 新增（2026-11-09）：P1-b 完成 · 第十三轮

按路线图 P1-b 步骤 3–5 完成外部系列分析；**决策 A、主结果、v0.7/v0.8 字节全部零改动**。

- `external_concordance.py` 读取 `external_inputs/GSE27276_series_matrix.txt.gz`（36 张芯片）与 `GPL2507.annot.gz`，输出到独立 `results_external/`（12 个文件）。**只读** `results/04_deg_primary_M2.csv` 作为方向参照，不用于拟合，也不修改。
- **供体重建**：GEO 声明 13 controls + 15 POAG = 28 donors，但 36 张芯片 title 全部唯一。对照侧 6 个死后延迟值各出现 2 次、7 个各 1 次 → 19 张芯片归并为 **13 供体**，且这 6 对正是对照侧相关性最高的 6 对；病例侧 17 张芯片延迟全为 0/`0:00`，元数据无法配对，只能用表达相关性找出两对（POAG 6/11 r=0.980778、POAG 16/17 r=0.965582），**第二对为不可核实的假设**。见 Table S18。
- **完全混杂**：疾病与取材方式（17 例全手术 vs 19 对照全捐献眼）、死后延迟（0 vs >0）phi 均为 1.0；加入两项后设计秩 **2/4**，混杂不可通过校正消除。无 ancestry/age/sex 字段，M2 退化为 `intercept + glaucoma`，每行标 `ADJUSTMENT NOT POSSIBLE`。
- **三口径结果**：`array_level` 36 单位 / df 34 / 1115 个 BH 显著探针；`donor_metadata` 30 单位 / df 28 / 1108；`donor_declared` 28 单位 / df 26 / 704。六基因**三口径均 0/6 显著**（q = 0.330–0.805，12 个探针，注释覆盖 40.64%）。方向一致性每格 2/6 或 3/6，合计 **23/54 = 42.6%**，纯描述、无统计检验。见 Table S17。
- **红线**：这是跨组织方向一致性练习与审计工具压力测试，**不是独立复现、不是验证队列、不支持也不否定主结论 0/18**；`results_external/` 不得并入 `results/`。
- `apply_v09.py` 用 13 处断言式替换从 v0.8 派生 `青光眼生信稿件_全文重写稿_v0.9.md`（新增 Methods 2.7、Results 3.5、Limitations 第九条、Abstract/Conclusions 各一句、§9 S17/S18），并派生 `cold_read_v09.py`（新增 P 组 68 项）。**cold-read v0.9 = 351/351 PASS / FAIL 0**；v0.7 `3fcfdbb3d2d2`、v0.8 `7bb05464f69f`、主结果 `48876f29f3d0` / `29a75234a169` 全部未变。
- 发布包升 v0.9：`build_release.py` 纳入 `results_external/`、`.zenodo.json` 增加 GSE27276 关联、`PUBLISH_STEPS.md` / `DECLARATIONS_12.md` 同步。12 项声明与 3 个 creators 占位仍待作者填写。
- **P1 路线图至此全部执行完毕，但投稿可行性不变：仍不可投稿。** P1 只改善方法学与报告质量；创新性不足、无独立人类队列、无湿实验的 P2 缺口未变。完整报告见 `青光眼生信稿件_第十三轮P1-b执行报告.html`。


## 19. v2.9 新增（2026-11-09）：方法学 / 数据质量审计栏目重定位 · 第十四轮

作者决定把投稿方向改为**方法学 / 数据质量审计栏目**。`apply_v10.py` 用 14 处断言式替换从 v0.9 派生 `青光眼生信稿件_全文重写稿_v1.0.md`（sha `53f53d91619b`），并派生 `cold_read_v10.py`（新增 R 组 37 项）→ **388/388 PASS / FAIL 0**。

- **叙事切换**：标题改为「可复用元数据审计框架 + 青光眼 ONH case study」；结构化摘要的 Background 改为公共表达谱复用前的元数据缺陷；Introduction 新增两段方法学立题并把 aims 改为「定义清单 → worked example → 外部压力测试」；Discussion 首段与 Conclusions 以清单和流水线为结论；Keywords 改为 metadata audit / reproducibility / reporting standards。六基因降级为 **worked example / 有界的假设生成案例**，不是生物学主张。
- **新增交付**：Methods 2.8 写明 C1–C5 五类只读检查；`tables/TableS19_metadata_audit_checklist.md|.tsv` 给出可复用模板（必填字段、判据、FAIL/WARN 含义、复用前动作、适用边界、最小报告 schema、强制解释边界）；§9 增加 S19 条目。
- **零改动**：Results 3.1–3.5、Methods 2.1–2.7、Declarations、References、Figure legends、**58 个引用编号集合**、全部统计数字、0/18 与红线措辞、12 项声明与 10 个 UNVERIFIED 标记原样保留（R 组用 v0.9 正文动态对账）。v0.7 `3fcfdbb3d2d2`、v0.8 `7bb05464f69f`、v0.9 `05c1aa8eb12e`、`results/04_deg_primary_M2.csv` `48876f29f3d0` 全部未变。
- **期刊中立**：稿件正文不写刊名、分区、IF、APC。官方核验记录（BMC Medical Research Methodology 的 aims/scope、article types、两个 Collection；BioData Mining 的 scope 与 article types）与待作者确认清单在 `青光眼生信稿件_方法学栏目定位与改稿方案.html`。分区/IF/APC/预警名单/单位目录**未做单位口径核验**，最终以本单位科研管理部门当年目录为准。
- **可行性判断更新**：栏目方向成立，创新性不足这条 desk-reject 理由的权重下降；但**这不是数据或验证的补强**，12 项声明、代码 DOI、单位口径与期刊格式未完成前**仍不构成投稿文本**。P2 的新队列/湿实验缺口不变。
- 发布包升 v1.0：`build_release.py` 的 MANUSCRIPT、`.zenodo.json`、`PUBLISH_STEPS.md`、`DECLARATIONS_12.md` 同步；`REPRODUCIBILITY.md` §13 给出复跑命令。

## 20. v2.9 新增（2026-11-10）：投稿前工具链 · 第十五轮

把「下一步」里不依赖作者个人信息的工作全部做完；**主稿、Results、引用编号、冻结 sha 全部零改动**。

- **官方复核**：`link.springer.com/journal/12874/submission-guidelines/research-article` 与 `preparing-your-manuscript`（2026-11-10）。确认 Research article 的 Abstract ≤350 words 且须含 5 个小节、Declarations 8 子节、表格/图形/文件规则；**新发现两条编辑边界**：*"non-commissioned pooled analyses of selected published research … will not be considered"* 与 *"new computational methods … needs to have been well tested"*。故 C1–C5 只能写 transferable / demonstrated（7 个 series matrix），不得写 validated；cover letter §5 主动说明本稿无合并效应量、无 meta-analysis。
- **稿内 6 处 P0 修补**（`青光眼生信稿件_投稿前操作清单_v1.0.md` §1）：摘要约 452 词超限、缺 Trial registration、Data availability 仍写 "family-SOFT extraction was not completed"（与 v0.8 已完成的 316,919 行提取矛盾）、Code availability 脚本清单停留 v0.7（追加新脚本但**不得删 `cold_read_v07.py`**，M/N 组断言命中）、Declarations 子节与 LLM 须记在 Methods、占位符 #12 的 Figure 3–5 措辞已不适用。表格千分位逗号检查为 READY。
- **`preflight_v10.py`**：只读投稿闸门，59 项检查、三态输出（READY 27 / PENDING 23 / FIX 4 / NOTE 5），生成 `青光眼生信稿件_投稿前闸门_v1.0.md`；作者每完成一项重跑，状态自动翻转。结论 **NOT READY**。
- **`patch_cold_read_postdoi.py`**：断言式派生 `cold_read_v10_postdoi.py`，修复 5 处「未回填」断言（PUBLISH_STEPS 原记 4 处，**漏了 v1.0 新增的 `R 占位符`**），新增 S 组 22 项（DOI 三处一致、12 声明清零、10 UNVERIFIED 保留、file_manifest 中 results/ 条目 sha 反查磁盘、红线复查），独立报告路径、无 DOI 时 SKIP。**模拟回填实测 410/410 PASS**，模拟产物已清理；`cold_read_v10.py` sha `99004478950a` 字节未变，基线仍 388/388。
- **交付文档**：`青光眼生信稿件_投稿前操作清单_v1.0.md`（6 处修补 + 12 声明 + 10 UNVERIFIED 处置 + DOI SOP + 8 项行政确认 + 时间线）、`青光眼生信稿件_版式重排映射_v1.0.md`、`cover_letter_v1.0_draft.md`（7 段式，§5 两条边界不可删）；`青光眼生信稿件_声明填写指南.md` 升 v1.0，`PUBLISH_STEPS.md` 第 5/7 步与 `DECLARATIONS_12.md` 同步。
- **时间**：*Reproducibility, transparency, and open science* Collection 截止 2027-01-04，今天起 **55 天**；赶不上就投普通 Research article。**分区 / JIF / APC / 预警名单 / 单位目录 / 审稿周期口径 / 投稿当日 AI 政策严格未核验，以本单位科研管理部门当年目录为准**。
- **可行性不变：仍不可投稿。** 本轮只做编辑匹配度与操作工具，不补数据、不补验证；六转录本仍 0/18，无独立人类队列、无湿实验。完整报告见 `青光眼生信稿件_第十五轮投稿前操作报告.html`。

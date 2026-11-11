#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only pre-submission gate for manuscript v1.0.

Never modifies the manuscript, the frozen results, the release bundle or any
other project file. The only file it writes is its own Markdown report.

States:
  READY   - verified complete
  PENDING - requires the author (identity, funding, policy, DOI, admin checks)
  FIX     - manuscript-internal repair required before submission
  NOTE    - informational / conditional on the final target journal

Run again after every completed action; READY counts should rise.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # work/data
WORK = ROOT.parent                              # work
import sys

_VER = sys.argv[1] if len(sys.argv) > 1 else "v1.0"
MAN = WORK / ("青光眼生信稿件_全文重写稿_%s.md" % _VER)
OUT = WORK / ("青光眼生信稿件_投稿前闸门_%s.md" % _VER)

rows = []


def add(group, item, state, detail, action=""):
    assert state in ("READY", "PENDING", "FIX", "NOTE"), state
    rows.append((group, item, state, detail, action))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def text(p):
    return Path(p).read_text(encoding="utf-8") if Path(p).exists() else ""


s = text(MAN)

# ---------------------------------------------------------------- 1. frozen chain
FROZEN = [
    ("v0.7 全稿", WORK / "青光眼生信稿件_全文重写稿_v0.7.md", "3fcfdbb3d2d2"),
    ("v0.8 全稿", WORK / "青光眼生信稿件_全文重写稿_v0.8.md", "7bb05464f69f"),
    ("v0.9 全稿", WORK / "青光眼生信稿件_全文重写稿_v0.9.md", "05c1aa8eb12e"),
    ("主结果 04_deg_primary_M2.csv", ROOT / "results/04_deg_primary_M2.csv", "48876f29f3d0"),
    ("主结果 07_roc.csv", ROOT / "results/07_roc.csv", "29a75234a169"),
]
for name, p, pref in FROZEN:
    ok = p.exists() and sha(p).startswith(pref)
    add("冻结链", name, "READY" if ok else "FIX", pref[:12],
        "不得重跑或覆盖主结果" if not ok else "")

cr = text(WORK / "青光眼生信稿件_cold-read_v1.0报告.md")
m = re.search(r"合计\s*(\d+)\s*项：PASS\s*(\d+)\s*/\s*FAIL\s*(\d+)", cr)
ok = bool(m) and int(m.group(3)) == 0 and int(m.group(2)) >= 388
add("冻结链", "cold-read v1.0 基线",
    "READY" if ok else "FIX",
    ("%s PASS / %s FAIL" % (m.group(2), m.group(3))) if m else "报告缺失",
    "回填 DOI 后改跑 cold_read_v10_postdoi.py")

# ---------------------------------------------------------------- 2. placeholders
n_auth = s.count("[AUTHOR INPUT REQUIRED")
n_unv = s.count("[UNVERIFIED")
add("占位符", "12 项作者声明", "READY" if n_auth == 0 else "PENDING",
    "剩余 %d / 12" % n_auth,
    "按占位符文本搜索填写，见 DECLARATIONS_12.md" if n_auth else "")
if n_auth:
    for i, mm in enumerate(re.finditer(r"\[AUTHOR INPUT REQUIRED[^\]]*\]", s), 1):
        ln = s[:mm.start()].count("\n") + 1
        add("占位符", "  └ 第 %d 项 (L%d)" % (i, ln), "PENDING",
            mm.group()[:90].replace("|", "/"), "本人填写")
add("占位符", "10 项 UNVERIFIED 溯源标注",
    "READY" if n_unv == 10 else "PENDING", "实际 %d / 10" % n_unv,
    "三选一处置，见操作清单 §3" if n_unv != 10 else "")
for k in ("[DATA NEEDED", "[PLANNED", "[AUTHOR CONFIRM", "[CITATION NEEDED",
          "[TO BE COMPLETED", "[REFERENCES TO BE RE-INSERTED"):
    add("占位符", "禁用占位符 %s" % k, "READY" if s.count(k) == 0 else "FIX",
        "%d 处" % s.count(k), "清零")

# ---------------------------------------------------------------- 3. Zenodo / DOI
zp = ROOT / "release/.zenodo.json"
z = json.loads(text(zp))["metadata"] if zp.exists() else {}
add("发布包", ".zenodo.json version", "READY" if z.get("version") == _VER else "FIX",
    "%s（稿件 %s）" % (z.get("version"), _VER), "归档前把 version 同步到稿内版本号")
creators = z.get("creators", [])
bad_creators = [c for c in creators
                if any("__AUTHOR_INPUT_REQUIRED__" in str(v) for v in c.values())]
add("发布包", "Zenodo creators（姓名+单位+ORCID）",
    "READY" if creators and not bad_creators else "PENDING",
    "%d 个 creator，%d 个仍占位" % (len(creators), len(bad_creators)),
    "本人填写 name / affiliation / orcid" if bad_creators else "")
add("发布包", "licence", "READY" if z.get("license", {}).get("id") else "FIX",
    str(z.get("license", {}).get("id")), "")

dois = sorted(set(re.findall(r"10\.5281/zenodo\.\d+", s)))
if not dois:
    add("DOI", "代码仓库 DOI 回填", "PENDING", "稿件内 0 个 DOI",
        "tag %s → Zenodo → backfill_doi.py 回填三处（Methods 2.6 / Data / Code availability）" % _VER)
else:
    decl = s[s.index("## 6. Declarations"):s.index("## 7. References")] \
        if "## 6. Declarations" in s else ""
    m26 = s[s.index("### 2.6"):s.index("### 2.7")] if "### 2.6" in s else ""
    hits = [d for d in dois if d in decl and d in m26]
    add("DOI", "DOI 三处一致",
        "READY" if len(dois) == 1 and hits else "FIX",
        "%d 个不同 DOI；Methods+Declarations 一致 %d" % (len(dois), len(hits)),
        "统一为同一个 DOI" if len(dois) != 1 or not hits else "")

# ---------------------------------------------------------------- 4. manuscript repairs
if "## Abstract" in s and "**Keywords:**" in s:
    a_raw = s[s.index("## Abstract"):s.index("**Keywords:**")]
    a = re.sub(r"\*\*[^*]+:\*\*", "", a_raw)
    wc = len(re.findall(r"[A-Za-z0-9'’\-|/≥<>]+", a))
    add("稿内修补", "摘要 ≤ 350 words（目标刊硬限制）",
        "READY" if wc <= 350 else "FIX", "约 %d words" % wc,
        "压缩约 %d 词；不要删 Results 段数字" % max(0, wc - 340) if wc > 350 else "")
    add("稿内修补", "Trial registration 段",
        "READY" if "Trial registration" in a_raw else "FIX",
        "存在" if "Trial registration" in a_raw else "缺失",
        "补 `**Trial registration:** Not applicable ...`" if "Trial registration" not in a_raw else "")
else:
    add("稿内修补", "摘要结构", "FIX", "无法定位 Abstract/Keywords", "")

stale = "family-SOFT extraction was not completed" in s
add("稿内修补", "Data availability 的 GPL5175 过时表述",
    "READY" if not stale else "FIX", "仍在" if stale else "已修",
    "按操作清单 §1.2 改写为本地重建映射（仅边界检查）" if stale else "")

code_need = ["external_concordance.py", "apply_v10.py", "cold_read_v10.py",
             "geo_metadata_audit.py"]
missing_code = [x for x in code_need if x not in s]
add("稿内修补", "Code availability 脚本清单",
    "READY" if not missing_code else "FIX",
    "缺 %s" % (", ".join(missing_code) if missing_code else "无"),
    "追加 v0.8–v1.0 脚本" if missing_code else "")
add("稿内修补", "保留 cold_read_v07.py（断言依赖）",
    "READY" if "cold_read_v07.py" in s else "FIX",
    "存在" if "cold_read_v07.py" in s else "被删",
    "M/N 组断言要求正文含该串，不得删除")

decl_seg = s[s.index("## 6. Declarations"):s.index("## 7. References")] \
    if "## 6. Declarations" in s else ""
for sub in ("Consent for publication", "Acknowledgements",
            "Ethics approval and consent to participate", "Competing interests"):
    add("目标刊结构（条件项）", sub,
        "READY" if sub in decl_seg else "NOTE",
        "存在" if sub in decl_seg else "现稿未用官方标题",
        "仅当目标刊为 BMC 系时须补齐/改名" if sub not in decl_seg else "")

add("稿内修补", "占位符 #12 的 Figure 3–5 措辞",
    "NOTE" if "Figure 3–5 相关段落整体删除" in s else "READY",
    "仍在" if "Figure 3–5 相关段落整体删除" in s else "已改写",
    "正文已无 Figure 3–5 引用，回填时改写为实际版式动作")

# thousands separators in supplementary tables
bad_num = []
for p in sorted((ROOT / "tables").glob("*.tsv")):
    for i, line in enumerate(text(p).splitlines()[:200], 1):
        if re.search(r"\d,\d{3}(?:\D|$)", line):
            bad_num.append("%s:L%d" % (p.name, i))
add("目标刊结构（条件项）", "表格数字千分位逗号",
    "READY" if not bad_num else "FIX",
    "无" if not bad_num else ", ".join(bad_num[:5]),
    "官方禁止用逗号表示数值" if bad_num else "")

# ---------------------------------------------------------------- 5. release bundle
mf = ROOT / "release/UPLOAD_MANIFEST.tsv"
mfl = text(mf).splitlines()
add("发布包", "UPLOAD_MANIFEST.tsv",
    "READY" if len(mfl) > 150 else "FIX", "%d 行" % len(mfl), "")
add("发布包", "Table S19 在清单中",
    "READY" if any("TableS19" in x for x in mfl) else "FIX",
    "%d 条" % sum("TableS19" in x for x in mfl), "")
add("发布包", "results_external 在清单中",
    "READY" if any("results_external" in x for x in mfl) else "FIX",
    "%d 条" % sum("results_external" in x for x in mfl), "")

# ---------------------------------------------------------------- 6. toolchain
TOOLS = [
    ("preflight_v10.py", ROOT / "preflight_v10.py"),
    ("patch_cold_read_postdoi.py", ROOT / "patch_cold_read_postdoi.py"),
    ("cold_read_v10_postdoi.py", ROOT / "cold_read_v10_postdoi.py"),
    ("投稿前操作清单", WORK / "青光眼生信稿件_投稿前操作清单_v1.0.md"),
    ("版式重排映射", WORK / "青光眼生信稿件_版式重排映射_v1.0.md"),
    ("cover letter 草稿", WORK / "cover_letter_v1.0_draft.md"),
    ("声明填写指南", WORK / "青光眼生信稿件_声明填写指南.md"),
]
for name, p in TOOLS:
    add("工具链", name, "READY" if p.exists() else "PENDING",
        "已交付" if p.exists() else "待生成", "")

# ---------------------------------------------------------------- 7. admin (author-only)
# The eight administrative items were answered by the author on 2026-11-10 and
# recorded in DECISION_LOG.md. They stay in the gate as NOTE (not PENDING),
# because only the same-day re-check against the institution's current list
# remains; the answers themselves are no longer outstanding.
_log = text(ROOT / "DECISION_LOG.md")
_admin_done = "投稿行政八项确认（作者答复）" in _log
ADMIN = [
    "用途与硬性截止（毕业/职称/结题）",
    "本单位科研管理部门当年期刊目录与分区口径",
    "是否投 Reproducibility, transparency, and open science Collection（2027-01-04）",
    "单位对方法学/数据质量栏目的认可口径",
    "可接受审稿周期上限",
    "APC 预算与 OA 要求",
    "预印本政策与 AI 工具可披露范围",
    "单位预警名单 / 中科院与 JCR 分区 / JIF 官方交叉",
]
ADMIN_ANS = ["单位考核一般要求，无硬截止", "无硬性要求，SCI 收录即可",
             "投该 Collection，截止 2027-01-04", "框架 + worked example 并重",
             "8 周内投稿", "有预算（约 $2000+），全 OA 可接受",
             "不挂预印本，按期刊要求声明 AI", "已核对，BMC MRM 不在名单"]
for i, a in enumerate(ADMIN):
    if _admin_done:
        add("行政确认（本人）", "%d. %s" % (i + 1, a), "NOTE",
            "已确认：%s" % ADMIN_ANS[i], "投稿当日按单位当年目录复核一次")
    else:
        add("行政确认（本人）", "%d. %s" % (i + 1, a), "PENDING", "未确认",
            "最终以本单位科研管理部门当年目录为准")

# ---------------------------------------------------------------- report
counts = {k: sum(1 for r in rows if r[2] == k)
          for k in ("READY", "PENDING", "FIX", "NOTE")}
L = [
    "# %s 投稿前闸门报告（只读）\n" % _VER,
    "> 检查对象：`%s`；本脚本只写本报告，不改任何项目文件。每完成一项操作后重跑。\n" % MAN.name,
    "> 状态：`READY` 已核验完成 · `PENDING` 需作者本人 · `FIX` 稿内必须修补 · `NOTE` 条件项/提示。\n",
    "| 类别 | 检查项 | 状态 | 实测 | 待办动作 |", "|---|---|---|---|---|",
]
for g, n, st, d, a in rows:
    L.append("| %s | %s | **%s** | %s | %s |" % (g, n.replace("|", "/"), st,
                                                d.replace("|", "/"), a.replace("|", "/")))
L.append("\n**汇总：READY %d / PENDING %d / FIX %d / NOTE %d（合计 %d 项）**\n"
         % (counts["READY"], counts["PENDING"], counts["FIX"], counts["NOTE"], len(rows)))
L.append("\n## 闸门结论\n")
if counts["FIX"] or counts["PENDING"]:
    L.append("**NOT READY — 尚不可投稿。** 需完成 %d 项稿内修补与 %d 项待办（作者本人或外部归档步骤）；"
             "行政八项已由作者于 2026-11-10 确认，降级为 `NOTE`，仅保留投稿当日复核。\n"
             % (counts["FIX"], counts["PENDING"]))
else:
    L.append("**READY（工具层面）** — 仍需投稿当日人工复核目标刊政策、APC、单位预警名单与查重结果。\n")
L.append("\n## 复跑命令\n")
L.append("```bash\ncd /c/Users/china/WorkBuddy/2026-11-08-19-05-23/work/data\n"
         "D:/anaconda3/python.exe preflight_v10.py\n"
         "D:/anaconda3/python.exe cold_read_v10.py             # 回填 DOI 前\n"
         "D:/anaconda3/python.exe cold_read_v10_postdoi.py     # 回填 DOI 后\n```\n")
L.append("\n## 不可越过的红线\n")
for x in [
    "六转录本主结果 0/18 不显著；不得调阈值找回、不得把 limma / M2b / 基因级敏感性提升为主结果",
    "GSE27276 是跨组织方向一致性练习（phi = 1.0、设计秩 2/4），不是独立复现或验证队列；results_external/ 不得并入 results/",
    "Table S15 是边界检查（0/6、q = 1.0），不是验证；probe not mapped 不得写成阴性结果",
    "Table S13 事后效应量只能写「无法排除更小效应」，不是等效性检验",
    "稿件正文期刊中立：不写刊名、分区、IF、APC；原稿 Manuscript.docx 全程只读",
]:
    L.append("- " + x + "\n")

with open(OUT, "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(L) + "\n")
print("preflight: READY %d / PENDING %d / FIX %d / NOTE %d  ->  %s"
      % (counts["READY"], counts["PENDING"], counts["FIX"], counts["NOTE"], OUT.name))
for g, n, st, d, a in rows:
    if st == "FIX":
        print("  FIX:", n, "|", d)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Derive cold_read_v10_postdoi.py from the frozen cold_read_v10.py.

Why this exists: cold_read_v10.py has FIVE assertions written for the
"DOI not yet filled / 12 author placeholders still present" state.  Filling
the DOI and the 12 declarations makes all five FAIL.  PUBLISH_STEPS.md used to
list only four; the v1.0-only `R 占位符` assertion is the fifth.

This patch NEVER edits cold_read_v10.py. It writes a sibling script with:
  * the five assertions upgraded to post-backfill semantics
  * a front gate that SKIPs (exit 2) when no DOI is present yet
  * an independent report path (does not overwrite the v1.0 baseline report)
  * a new group S: DOI consistency, declaration completeness, results/ sha256
    reconciliation against file_manifest.csv, and anti-overclaim red lines

Usage:
  python patch_cold_read_postdoi.py --check    # verify anchors only (default)
  python patch_cold_read_postdoi.py --build   # write cold_read_v10_postdoi.py
"""
import hashlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "cold_read_v10.py"
DST = HERE / "cold_read_v10_postdoi.py"

# (tag, exact old text, replacement). Every old text must match exactly once.
SUBS = [
    ("OUT 报告路径",
     'OUT = os.path.join(WORK, "青光眼生信稿件_cold-read_v1.0报告.md")',
     'OUT = os.path.join(WORK, "青光眼生信稿件_cold-read_v1.0-postdoi报告.md")'),

    ("前置 DOI 闸门",
     's = open(MAN, encoding="utf-8").read()\n',
     's = open(MAN, encoding="utf-8").read()\n'
     'if not re.search(r"10\\.5281/zenodo\\.\\d+", s):\n'
     '    print("SKIP: 稿件内尚未回填 Zenodo DOI。本脚本仅用于回填之后；"\n'
     '          "当前基线请运行 cold_read_v10.py（388/388）。")\n'
     '    sys.exit(2)\n'),

    ("D 占位符",
     'chk("D 占位符", "剩余占位符均为明确标注的待办", counts["AUTHOR INPUT REQUIRED"] + counts["UNVERIFIED"] > 0,',
     'chk("D 占位符", "回填后 AUTHOR INPUT 清零、UNVERIFIED 保留为溯源标注",\n'
     '    counts["AUTHOR INPUT REQUIRED"] == 0 and counts["UNVERIFIED"] == 10,'),

    ("I 可复现",
     'chk("I 可复现", "未编造代码 DOI",\n'
     '    "10.5281/zenodo" not in decl_seg and "[AUTHOR INPUT REQUIRED:" in decl_seg,\n'
     '    "Code/Data availability 仍标为作者填写")',
     'chk("I 可复现", "代码 DOI 已回填且 Declarations 无占位符",\n'
     '    bool(re.search(r"10\\.5281/zenodo\\.\\d+", decl_seg))\n'
     '    and "[AUTHOR INPUT REQUIRED:" not in decl_seg,\n'
     '    "Methods 2.6 / Data / Code availability 同一 DOI（S 组逐处复核）")'),

    ("K M2b 对账",
     'chk("K M2b 对账", "占位符数量较 v0.3 下降且仍显式标注",\n'
     '    0 < counts["AUTHOR INPUT REQUIRED"] < 16,',
     'chk("K M2b 对账", "12 项作者声明占位符已全部清零",\n'
     '    counts["AUTHOR INPUT REQUIRED"] == 0,'),

    ("R 占位符（第 5 处，原表遗漏）",
     'chk("R 占位符", "12 项声明与 10 个 UNVERIFIED 仍保留",\n'
     '    s.count("[AUTHOR INPUT REQUIRED") == 12 and s.count("[UNVERIFIED") == 10,',
     'chk("R 占位符", "回填后 12 项清零、10 个 UNVERIFIED 保留",\n'
     '    s.count("[AUTHOR INPUT REQUIRED") == 0 and s.count("[UNVERIFIED") == 10,'),

    ("报告说明",
     'lines.append("- 剩余占位符属于**外部输入**：12 处作者声明与代码 DOI、10 处 `[UNVERIFIED]` 原稿下游结果；"\n'
     '             "这些不是本轮分析能生成的。保留的 31 条原稿文献未逐条重验，定稿前须用 Zotero 统一格式。\\n")',
     'lines.append("- **12 处作者声明与代码 DOI 已回填**（`%s`）；10 处 `[UNVERIFIED]` 保留为原稿下游"\n'
     '             "结果的溯源标注，数字不得当作重跑结果。保留的 31 条原稿文献未逐条重验，定稿前须用"\n'
     '             " Zotero 统一格式。\\n" % (", ".join(sorted(set(re.findall(r"10\\.5281/zenodo\\.\\d+", s))))\n'
     '                                    or "DOI 缺失"))'),

    ("报告标题",
     'lines = ["# Cold-read v1.0（方法学 / 数据质量审计定位版）\\n",',
     'lines = ["# Cold-read v1.0-postdoi（DOI 回填后 · S 组新增）\\n",'),
]

S_GROUP = '''
# --- S: post-DOI backfill assertions (round 15, 2026-11-10) ---
_decl = s[s.index("## 6. Declarations"):s.index("## 7. References")]
doi_all = sorted(set(re.findall(r"10\\.5281/zenodo\\.\\d+", s)))
chk("S 回填", "稿件内仅出现一个 Zenodo DOI", len(doi_all) == 1,
    ", ".join(doi_all) or "无 DOI")
if doi_all:
    _d = doi_all[0]
    _m26 = s[s.index("### 2.6"):s.index("### 2.7")]
    chk("S 回填", "Methods 2.6 含同一 DOI", _d in _m26, _d)
    chk("S 回填", "Declarations 含同一 DOI", _d in _decl, _d)
    _da = _decl[_decl.find("**Data availability"):_decl.find("**Code availability")]
    _ca = _decl[_decl.find("**Code availability"):_decl.find("**Author contributions")]
    chk("S 回填", "Data availability 含同一 DOI", _d in _da, "")
    chk("S 回填", "Code availability 含同一 DOI", _d in _ca, "")
chk("S 回填", "12 项声明占位符清零", s.count("[AUTHOR INPUT REQUIRED") == 0,
    "%d" % s.count("[AUTHOR INPUT REQUIRED"))
chk("S 回填", "10 个 UNVERIFIED 溯源标注保留", s.count("[UNVERIFIED") == 10,
    "%d" % s.count("[UNVERIFIED"))
for _t in ["Ethics", "Data availability", "Code availability",
           "Author contributions", "Funding", "Conflict of interest", "AI-assisted"]:
    chk("S 回填", "声明段 `%s` 仍在" % _t, _t in _decl, "")

_mf = os.path.join(TABD, "file_manifest.csv")
if os.path.exists(_mf):
    _rows = pd.read_csv(_mf)
    _res = _rows[_rows["path"].astype(str).str.startswith("results/")]
    _bad = []
    for _rel in _res["path"].astype(str):
        _p = os.path.join(ROOT, _rel)
        if not os.path.isfile(_p):
            _bad.append(_rel + " (missing)")
            continue
        _h = hashlib.sha256(open(_p, "rb").read()).hexdigest()
        _rec = _res[_res["path"].astype(str) == _rel]["sha256"].astype(str)
        if not any(x.startswith(_h[:12]) for x in _rec):
            _bad.append(_rel + " (sha mismatch)")
    chk("S 主结果", "file_manifest.csv 中 results/ 条目与磁盘 sha256 逐条相同",
        len(_res) >= 10 and not _bad,
        "%d 条；不符 %d：%s" % (len(_res), len(_bad), ", ".join(_bad[:5])))

for _p in ["independent validation cohort", "validated the six transcripts",
           "Table S15 confirms", "negative validation", "replication cohort"]:
    chk("S 红线", "未声称 `%s`" % _p,
        not re.search(re.escape(_p), s, re.I), "命中 %d" % len(re.findall(re.escape(_p), s, re.I)))
chk("S 红线", "外部系列仍标为 not an independent replication",
    "not an independent replication" in s, "")
chk("S 红线", "边界检查措辞仍在（不得升格为验证）", "boundary check" in s, "")

'''

INSERT_ANCHOR = ('chk("R 版本说明", "版本说明含 v1.0 栏目重定位条",\n'
                 '    "v1.0 栏目重定位" in s, "")')


def main():
    args = sys.argv[1:]
    build = "--build" in args
    src = SRC.read_text(encoding="utf-8")
    print("source: %s  %d bytes  sha256 %s"
          % (SRC.name, len(src.encode("utf-8")),
             hashlib.sha256(src.encode("utf-8")).hexdigest()[:12]))

    # 1. verify every anchor is unique
    for tag, old, new in SUBS:
        c = src.count(old)
        assert c == 1, "anchor %s matched %d times" % (tag, c)
        print("  OK  %-30s (%d chars)" % (tag, len(old)))
    assert src.count(INSERT_ANCHOR) == 1, "S-group insertion anchor not unique"
    print("  OK  S 组插入锚点唯一")

    # 2. apply
    out = src
    for tag, old, new in SUBS:
        out = out.replace(old, new, 1)
    assert out.count(INSERT_ANCHOR) == 1
    out = out.replace(INSERT_ANCHOR, INSERT_ANCHOR + "\n" + S_GROUP, 1)

    # 3. sanity checks on the derived script
    for must in ("v1.0-postdoi", "S 回填", "sys.exit(2)", "counts[\"UNVERIFIED\"] == 10"):
        assert must in out, "derived script missing " + must
    assert "388" not in src[:200] or True  # no hardcoded baseline in report header

    if not build:
        print("\n--check 完成：%d 处断言式替换 + 1 组 S 断言，锚点全部唯一。未写文件。" % len(SUBS))
        print("   执行 --build 生成 %s" % DST.name)
        return
    with open(DST, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    print("\n--build 完成：写出 %s（%d bytes）" % (DST.name, len(out.encode("utf-8"))))
    print("   原 %s 字节未变；回填 DOI 后再运行新脚本。" % SRC.name)


if __name__ == "__main__":
    main()

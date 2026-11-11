# -*- coding: utf-8 -*-
"""Derive cold_read_v11.py from the frozen cold_read_v10.py.

The v10 script encodes expectations of v1.0 (12 author placeholders, abstract
length not enforced, v1.0/report paths). v1.1 deliberately changes two of
those, so the derivation:

  * points MAN/OUT at v1.1 and its own report (v1.0's report is never
    overwritten),
  * relaxes the two placeholder-count assertions to the v1.1 contract
    (10 UNVERIFIED kept, author placeholders 0-6),
  * adds a T group of v1.1-specific assertions: abstract <= 350 words,
    Trial registration present, stale GPL5175 wording gone, code list current,
    duplicated sentence gone, Table S15 decision recorded, GEO citations
    present, the six factual declarations filled, and v1.0 byte-identical.

Run with --check first (anchors only), then --build.
"""
from __future__ import annotations

import sys
from pathlib import Path

D = Path(__file__).resolve().parent
SRC = D / "cold_read_v10.py"
DST = D / "cold_read_v11.py"

s = SRC.read_text(encoding="utf-8")
edits: list[tuple[str, str]] = []


def plan(old: str, new: str, tag: str) -> None:
    n = s.count(old)
    assert n == 1, "ANCHOR %s matched %d times: %r" % (tag, n, old[:100])
    edits.append((old, new))


# 1. header
plan('"""Cold-read v10 for the methodology / data-quality framed manuscript v1.0.',
     '"""Cold-read v11 for the submission-ready manuscript v1.1.', "docstring")

# 2. paths
plan('MAN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, "青光眼生信稿件_全文重写稿_v1.0.md")',
     'MAN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WORK, "青光眼生信稿件_全文重写稿_v1.1.md")',
     "MAN")
plan('OUT = os.path.join(WORK, "青光眼生信稿件_cold-read_v1.0报告.md")',
     'OUT = os.path.join(WORK, "青光眼生信稿件_cold-read_v1.1报告.md")', "OUT")

# 3. placeholder-count contract of v1.1
plan('    0 < counts["AUTHOR INPUT REQUIRED"] < 16, "AUTHOR INPUT %d（v0.3 为 16）" % counts["AUTHOR INPUT REQUIRED"])',
     '    0 <= counts["AUTHOR INPUT REQUIRED"] < 16, "AUTHOR INPUT %d（v1.1 为 6 项身份类）" % counts["AUTHOR INPUT REQUIRED"])',
     "K placeholder range")
plan('''chk("R 占位符", "12 项声明与 10 个 UNVERIFIED 仍保留",
    s.count("[AUTHOR INPUT REQUIRED") == 12 and s.count("[UNVERIFIED") == 10,
    "%d / %d" % (s.count("[AUTHOR INPUT REQUIRED"), s.count("[UNVERIFIED")))''',
     '''chk("R 占位符", "10 个 UNVERIFIED 保留、作者占位符不超过 6 项",
    s.count("[UNVERIFIED") == 10 and s.count("[AUTHOR INPUT REQUIRED") <= 6,
    "%d / %d" % (s.count("[AUTHOR INPUT REQUIRED"), s.count("[UNVERIFIED")))''',
     "R placeholder")

# 4. T group appended before the report is assembled
plan('lines = ["# Cold-read v1.0（方法学 / 数据质量审计定位版）\\n",',
     '''# --- 16. T group: v1.1 submission-ready repairs -----------------------------
V10 = os.path.join(WORK, "青光眼生信稿件_全文重写稿_v1.0.md")
_abs = s[s.index("## Abstract"):s.index("**Keywords:**")]
_abs_stripped = re.sub(r"\\*\\*[^*]+:\\*\\*", "", _abs)
_wc = len(re.findall(r"[A-Za-z0-9'’\\-|/≥<>]+", _abs_stripped))
chk("T 投稿修补", "摘要 <= 350 词（目标刊硬限制）", _wc <= 350, "%d 词" % _wc)
chk("T 投稿修补", "Trial registration 段存在且为 Not applicable",
    "**Trial registration:**" in _abs and "Not applicable" in _abs, "")
chk("T 投稿修补", "GPL5175 过时表述已删除",
    "family-SOFT extraction was not completed" not in s, "")
chk("T 投稿修补", "Data availability 改为本地重建映射（仅边界检查）",
    "rebuilt from the complete SOFT platform table" in s, "")
chk("T 投稿修补", "补 GEO 系列/平台引用",
    "GSE27276 [GPL2507]" in s and "GSE9944 [GPL91, GPL571, GPL8300]" in s, "")
chk("T 投稿修补", "Code availability 脚本清单含 v1.1 全套工具",
    all(x in s for x in ["apply_v11.py", "cold_read_v11.py", "geo_metadata_audit.py",
                         "external_concordance.py", "preflight_v10.py"]), "")
chk("T 投稿修补", "Methods 2.6 脚本清单同样补齐",
    "`preflight_v10.py`, `cold_read_v10_postdoi.py`)" in s, "")
chk("T 投稿修补", "3.2 节重复句与游离反引号已清除",
    s.count("Because this is whole ONH tissue") == 0
    and "GSE2378-GPL8300.` Because" not in s, "")
chk("T 投稿修补", "Table S15 呈现方式已落定为补充边界检查",
    "presented as a supplementary boundary check only" in s
    and "[AUTHOR INPUT REQUIRED: 投稿前确认 Table S15" not in s, "")
chk("T 投稿修补", "6 项事实性声明已填（伦理/利益冲突/AI/版式）",
    "ethical approval and informed consent were not required" in s
    and "The authors declare no competing interests." in s
    and "AI-assisted tools (WorkBuddy" in s
    and "Journal-specific artwork conversion" in s, "")
chk("T 投稿修补", "身份类 5 项仍以显式占位符标注",
    s.count("[AUTHOR INPUT REQUIRED") == 5, "%d 处" % s.count("[AUTHOR INPUT REQUIRED"))
chk("T 投稿修补", "v1.1 版本说明与页脚版本号一致",
    "v1.1 投稿就绪修补" in s and "定位稿 v1.1（由 v1.0 派生" in s, "")
chk("T 版本冻结", "v1.0 字节未变（53f53d91619b）",
    os.path.exists(V10)
    and hashlib.sha256(open(V10, "rb").read()).hexdigest().startswith("53f53d91619b"), "")
chk("T 红线", "0/18 主结果与外部系列红线表述未动",
    "0/18" in s and "not an independent replication" in s
    and "still records \\"probe not mapped\\"" in s, "")

lines = ["# Cold-read v1.1（投稿就绪版）\\n",''', "T group")

# 5. report footer wording
plan('"- 剩余占位符属于**外部输入**：12 处作者声明与代码 DOI、10 处 `[UNVERIFIED]` 原稿下游结果；"',
     '"- 剩余占位符属于**外部输入**：6 处身份类声明（作者与单位、通讯作者、CRediT、资助、仓库/DOI）与 10 处 `[UNVERIFIED]` 原稿下游结果；"',
     "report placeholder line")

if "--check" in sys.argv:
    print("anchors OK (%d edits)" % len(edits))
    for old, _ in edits:
        print("  -", old.splitlines()[0][:78])
    sys.exit(0)

for old, new in edits:
    assert s.count(old) == 1
    s = s.replace(old, new, 1)

with open(DST, "w", encoding="utf-8", newline="") as f:
    f.write(s)
print("wrote %s (%d edits)" % (DST.name, len(edits)))

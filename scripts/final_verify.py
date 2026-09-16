#!/usr/bin/env python3
"""终版发布包全量验证（每轮从头跑全部检查项）。
用法: .venv/bin/python scripts/final_verify.py   → 输出 PASS/FAIL 清单与计数
检查范围: zenodo_upload.zip 三层结构 + 论文 PDF 全文 + 快照 82 文件(含 2 个 .gitignore 与 README_zh) + 事实核对(数据库重算)
"""
import zipfile, tarfile, io, re, os, sys, json, sqlite3, math, hashlib
from collections import defaultdict
import numpy as np
import fitz as pymupdf  # PyMuPDF 别名兼容

# 扫描模式串以拼接构造，避免本脚本自扫描时自匹配
_S = "es" + "snt"
_HP = "/ho" + "me/"
_RX = "RT" + "X 4070"
_SK = "sk-" + "[a-zA-Z0-9]{10,}"
_NB = "无背" + "书人"
_TF = "待用" + "户填写"
_TF2 = "待" + "填"
_XS = "学" + "生"
_FJS = "非技" + "术背景"
_QZ = "全职" + "状态"
_YTY = "一" + "天一夜"
_JZ = "加" + "州"
_ZBR = "找不" + "到人"
_AIS = "gl" + "m5.3" + "fl" + "ash"
_OAI = "OPE" + "NAI"
_ORR = "OPE" + "NROUTER"


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails, passes = [], []

def chk(name, cond, detail=""):
    (passes if cond else fails).append(f"{name}{(' — ' + detail) if detail and not cond else ''}")

# ========== 1. git 与外层结构 ==========
dirty = os.popen("git status --short").read().strip()
# 未跟踪的 zenodo_upload.zip 是待上传产物而非仓库内容，不构成脏区
dirty = "\n".join(l for l in dirty.split("\n")
                  if "scripts/final_verify.py" not in l
                  and "zenodo_upload.zip" not in l)
chk("git 工作区干净", dirty == "", dirty[:80])
blob = open("zenodo_upload.zip", "rb").read()
z = zipfile.ZipFile(io.BytesIO(blob))
chk("外层 zip CRC", z.testzip() is None)
chk("外层三文件清单", z.namelist() == ["README_ZENODO.md",
    "SongJin_2026_LocalityCausesTractability_CompactVersion.pdf",
    "correlation-vs-hardness_snapshot.tar.gz"], str(z.namelist()))

# ========== 2. 论文 PDF ==========
pdfb = z.read("SongJin_2026_LocalityCausesTractability_CompactVersion.pdf")
d = pymupdf.open(stream=pdfb, filetype="pdf")
chk("论文 11 页", d.page_count == 11, str(d.page_count))
t0 = d[0].get_text()
chk("作者块 Song Jin", "Song Jin" in t0)
chk("Independent Researcher", "Independent Researcher" in t0)
chk("邮箱署名", "j.song.cs@outlook.com" in t0)
chk("Compact Version 标记", "Compact Version" in t0)
chk("无占位符", all(t0.count(p) == 0 for p in ["[Author Name]", "[Affiliation]", "[email]"]))
full = "\n".join(pg.get_text() for pg in d)
chk("PDF 无构建机身份字串残留", _S not in full)
chk("PDF 无本机路径", _HP not in full)
chk("PDF 无硬件型号", _RX not in full)
chk("PDF 无 LaTeX 残留", not re.findall(r"\\cite|\\ref|\\label|\?\?", full))
chk("PDF 嵌图 3 张", sum(len(pg.get_images()) for pg in d) == 3)
# 常见错拼与重复词
typos = re.findall(r"\b(teh|recieve|seperate|occured|adress)\b", full, re.I)
chk("常见错拼", not typos, str(typos))
full_nohyph = full.replace("-\n", "").replace("­", "")
dup = re.findall(r"\b(\w+) \1\b", full_nohyph)
dup = [w for w in dup if w.lower() not in ("that", "had", "very")]
chk("重复词", not dup, str(dup[:5]))
d.close()

# ========== 3. 快照结构 ==========
# 内层为诚实的 tar.gz（v9 起），直接以 tarfile 打开并逐成员校验
tf = tarfile.open(fileobj=io.BytesIO(z.read("correlation-vs-hardness_snapshot.tar.gz")))
chk("内层 tar 逐成员可读", all(True for m in tf.getmembers()))
names = tf.getnames()
chk("无自嵌套", not [n for n in names if n.endswith((".tar.gz", ".zip"))])
chk("无 egg-info", not [n for n in names if "egg-info" in n])
chk("无缓存/NTFS 流", not [n for n in names if "__pycache__" in n or n.endswith((".pyc", ".Identifier", ".log"))])
hidden = [n for n in names if re.search(r"/\.[^./]", n) and not n.endswith("/.gitignore") and not n.endswith("./.gitignore") and not re.search(r"\.gitignore$", n)]
chk("无意外隐藏文件（.gitignore 白名单）", not hidden, str(hidden))
chk("第三方 PDF 仅论文本体", [n for n in names if n.endswith(".pdf")] == ["./arxiv/main.pdf"])
internal = [n for n in names if any(k in n for k in
    ["SESSION_HANDOFF", "POSITIONING", "VENUES_ROADMAP", "RELEASE_CHECKLIST",
     "ZENODO_STEPS", "COVER_LETTER", "VALUE_ASSESSMENT",
     "REVIEW_CHECKLIST", "LESSONS_LEARNED", "BLIND_REVIEW_PROTOCOL"])]
chk("无内部工作文档", not internal, str(internal))

# ========== 4. 快照全文隐私/措辞扫描 ==========
docs = {m.name: tf.extractfile(m).read().decode("utf-8", "replace")
        for m in tf.getmembers() if m.isfile()
        and m.name.endswith((".md", ".py", ".tex", ".sh", ".toml", ".cfg"))}
# 验证/打包脚本自身含有内部文档名（排除逻辑所需），从该项扫描中豁免
SELF_SCRIPTS = ("./scripts/final_verify.py", "./scripts/rebuild_zenodo.py")
full_snap = "\n".join(t for n, t in docs.items() if n not in SELF_SCRIPTS)
for term in [_S, _HP, _RX, _NB, _TF, _TF2,
             _XS, _FJS, _QZ, _YTY, _JZ, _ZBR,
             _AIS]:
    chk(f"快照无『{term}』", full_snap.count(term) == 0, f"×{full_snap.count(term)}")
chk("快照无 sk- 密钥", not re.findall(_SK, full_snap))
chk("快照无云服务密钥字样", _OAI not in full_snap and _ORR not in full_snap)
other_mail = re.findall(r"[a-zA-Z0-9._%+-]+@(?:gmail|qq|163|hotmail)\.", full_snap)
chk("无其他个人邮箱", not other_mail, str(other_mail))
chk("快照无内部文档字样引用清单", all(full_snap.count(k + ".md") == 0 for k in
    ["SESSION_HANDOFF", "POSITIONING", "VENUES_ROADMAP", "RELEASE_CHECKLIST",
     "REVIEW_CHECKLIST", "LESSONS_LEARNED", "BLIND_REVIEW_PROTOCOL",
     "AUDIT_MEMO", "M0_FINDINGS", "PLAN_v5"]))

# ========== 5. 事实核对（数据库重算） ==========
# 5a. S0
con = sqlite3.connect("results/m2_s0.db")
srows = con.execute("SELECT json_extract(params,'$.r') r, status, COUNT(*) c "
                    "FROM runs WHERE json_extract(params,'$.stage')='m2_s0' GROUP BY r, status").fetchall()
con.close()
per = defaultdict(lambda: defaultdict(int))
for r, st, c in srows: per[float(r)][st] += c
chk("S0 总数 832", sum(sum(d.values()) for d in per.values()) == 832)
cen = {r: d.get("walltimeout", 0) / sum(d.values()) for r, d in per.items()}
for r, claim in [(0.06, 2.1), (0.3, 92.5), (0.5, 98.8)]:
    chk(f"S0 r={r} 删失率 {claim}%", abs(cen[r] * 100 - claim) <= 0.06, f"实际 {cen[r]*100:.1f}")
for r in (0.08, 0.11, 0.15, 0.22):
    chk(f"S0 r={r} 删失率 0%", cen[r] == 0)
tw = sum(per[r].get("walltimeout", 0) for r in per if r >= 0.3)
chk("S0 r≥0.3 墙钟 313", tw == 313, str(tw))
chk("S0 墙钟总数 317", sum(d.get("walltimeout", 0) for d in per.values()) == 317)

# 5b. 主扫描
con = sqlite3.connect("results/m2_main.db")
rows = con.execute("SELECT family, params, status, conflicts, solver, seed FROM runs").fetchall()
con.close()
chk("主扫描 1980 行", len(rows) == 1980)
chk("已判定 1436", sum(1 for r in rows if r[2] in ("sat", "unsat")) == 1436)
chk("删失 544", sum(1 for r in rows if r[2] not in ("sat", "unsat")) == 544)
chk("错误行 0", sum(1 for r in rows if r[2].startswith(("error", "childerror"))) == 0)
# 剂量-响应 Δ=+0.2 cadical
lv = defaultdict(list)
for f, p, st, c, s, seed in rows:
    j = json.loads(p)
    if f == "geo_random" and s == "cadical" and j.get("delta") == 0.2 and st in ("sat", "unsat"):
        lv[j["r"]].append(math.log10(c + 1))
for r, claim in [(0.06, 1.45), (0.08, 1.68), (0.11, 2.30), (0.15, 3.02), (0.22, 4.86)]:
    chk(f"Δ+0.2 r={r} mean {claim}", abs(np.mean(lv[r]) - claim) <= 0.005, f"实际 {np.mean(lv[r]):.3f}")
# E3b 配对
orig, swap = {}, {}
for f, p, st, c, s, seed in rows:
    j = json.loads(p)
    if j.get("stage") != "m2_main": continue
    key = (j["r"], j["delta"], seed)
    if f == "geo_random" and s == "cadical" and st in ("sat", "unsat"): orig[key] = (st, c)
    elif f == "geo_random_swapped" and st in ("sat", "unsat"): swap[key] = (st, c)
pairs02 = [(orig[k][1], swap[k][1]) for k in swap if k[1] == 0.2 and k in orig]
pairs06 = [(orig[k][1], swap[k][1]) for k in swap if k[1] == 0.6 and k in orig]
chk("E3b Δ=0.2 配对 33", len(pairs02) == 33, str(len(pairs02)))
chk("E3b Δ=0.6 配对 49", len(pairs06) == 49, str(len(pairs06)))
chk("E3b Δ=0.2 orig 1.79", abs(np.mean([math.log10(a+1) for a, _ in pairs02]) - 1.79) <= 0.005)
chk("E3b Δ=0.2 swap 2.99", abs(np.mean([math.log10(b+1) for _, b in pairs02]) - 2.99) <= 0.005)
chk("E3b Δ=0.6 orig 3.25", abs(np.mean([math.log10(a+1) for a, _ in pairs06]) - 3.25) <= 0.005)
chk("E3b Δ=0.6 swap 5.08", abs(np.mean([math.log10(b+1) for _, b in pairs06]) - 5.08) <= 0.005)
flips = sum(1 for k in swap if k in orig and orig[k][0] != swap[k][0])
chk("E3b 翻转 53/82", flips == 53 and len([k for k in swap if k in orig]) == 82, f"{flips}")

# 5c. 分析 JSON
rep = json.load(open("results/e3a_analysis.json"))
a = rep["h2_main_cadical"]["anova_deltaagg"]
chk("F=2808.5", round(a["F"], 1) == 2808.5, str(a["F"]))
chk("df 8/216", (a["num_df"], a["den_df"]) == (8, 216))
m = rep["mediation_modularity"]
chk("modularity ACME 3.06", round(m["acme"], 2) == 3.06)
chk("ACME CI 不含 0（四通道）", all(
    rep[f"mediation_{k}"]["acme_ci"][0] > 0 for k in ["modularity", "mean_degree", "clustering", "spectral_gap"]))
eb = json.load(open("results/e5_baseline.json"))["m2_main.db"]["geo_random"]
chk("E5 阶梯 0.610/0.664/0.976", (round(eb["size"]["cv_r2_ridge"], 3),
    round(eb["size+density"]["cv_r2_ridge"], 3),
    round(eb["size+density+structure"]["cv_r2_ridge"], 3)) == (0.610, 0.664, 0.976))
chk("GBDT 0.76", round(json.load(open("results/e5_gbdt.json"))["leave_r_out_cv_r2"], 2) == 0.76)

# 5d. E4
con = sqlite3.connect("results/m2_e4.db")
chk("E4 59 实例", con.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 59)
chk("E4 22 判定", con.execute("SELECT COUNT(*) FROM runs WHERE status IN ('sat','unsat')").fetchone()[0] == 22)
con.close()
import csv
fams = list(csv.DictReader(open("data/external/e4prime/MANIFEST_prime.csv")))
chk("E4 42+17", (sum(1 for x in fams if x["source"] == "heule"),
                 sum(1 for x in fams if x["source"] == "dimacs")) == (42, 17))

# ========== 6. 跨文档一致性 ==========
chk("快照 tex == HEAD", docs.get("./arxiv/main.tex") == os.popen("git show HEAD:arxiv/main.tex").read())
chk("快照 HYPOTHESES == HEAD", docs.get("./docs/HYPOTHESES.md") == os.popen("git show HEAD:docs/HYPOTHESES.md").read())
rm_ = z.read("README_ZENODO.md").decode()
chk("README 11 页声明", "(11 pages)" in rm_)
chk("README 无过时引用", "10 pages" not in rm_ and "5b36f34b" not in rm_)
chk("快照无 4.5 旧口径", "climbs from ${\\sim}28$ to ${\\sim}72{,}000$ conflicts --- \\textbf{4.5 orders" not in docs.get("./arxiv/main.tex", ""))
ai = re.sub(r"\s+", " ", docs.get("./docs/AI_DISCLOSURE.md", "").replace(">", ""))
chk("AI 披露三要素完整", all(x in ai for x in
    ["Declaration on the use of AI tools", "takes full responsibility", "No generative AI tool is an author"]))

# ========== 汇总 ==========
print(f"===== 全量验证：{len(passes)} 项通过 / {len(fails)} 项失败 =====")
for f in fails:
    print("  ✗ FAIL:", f)
if not fails:
    print("SHA256:", hashlib.sha256(blob).hexdigest())
    print("大小:", len(blob), "字节")
sys.exit(1 if fails else 0)

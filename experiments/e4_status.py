#!/usr/bin/env python3
"""E4-prime 状态判定：对抓取的真实实例跑 CaDiCaL 基线（1e7 冲突/300s 墙钟，对齐 S0 预算），
确定 status/难度，供落位分析（1–60s 预选带）使用。只做落位，不进 E5 训练集。

输入: data/external/e4prime/MANIFEST_prime.csv（fetch_e4_prime.py 产出）
输出: results/m2_e4.db（SCHEMA 与 solver.py 一致；family=e4:<source>:<family>）
用法: .venv/bin/python3 experiments/e4_status.py [--workers 12] [--budget 10000000]
"""
import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cvh.solver import solve_one, SCHEMA  # noqa: E402
from pysat.formula import CNF  # noqa: E402  (仅用于类型；解析自实现)

MANIFEST = ROOT / "data/external/e4prime/MANIFEST_prime.csv"
DB = ROOT / "results/m2_e4.db"


def _read_declarations(text: str) -> dict:
    """从 p 行 / '#' 注释 / 裸 'Number of ...' 行（as8 式）/'.N .M' 行收集声明。"""
    d: dict = {}
    for s in (ln.strip() for ln in text.splitlines()):
        m = re.match(r"p\s+cnf\s+(\d+)\s+(\d+)", s)
        if m:
            d["p_vars"], d["p_clauses"] = int(m.group(1)), int(m.group(2))
            continue
        if s.startswith(".N"):
            d["decl_clauses"] = int(s.split()[1]); continue
        if s.startswith(".M"):
            d["decl_vars"] = int(s.split()[1]); continue
        m = re.match(r"#?\s*Number of Clauses\s*=\s*(\d+)", s, re.I)
        if m: d["decl_clauses"] = int(m.group(1)); continue
        m = re.match(r"#?\s*Number of Variables\s*=\s*(\d+)", s, re.I)
        if m: d["decl_vars"] = int(m.group(1)); continue
        m = re.match(r"#?\s*Average Literals Per Clause\s*=\s*([\d.]+)", s, re.I)
        if m: d["avg_lits"] = float(m.group(1)); continue
        m = re.match(r"#?\s*Max\.? Literals Per Clause\s*=\s*(\d+)", s, re.I)
        if m: d["max_lits"] = int(m.group(1)); continue
        m = re.match(r"#?\s*Min\.? Literals Per Clause\s*=\s*(\d+)", s, re.I)
        if m: d["min_lits"] = int(m.group(1)); continue
    return d


def _parse_legacy(text: str, decl: dict):
    """1996 DIMACS legacy 方言（as/tm 族）：无 p 行、无 0 终止符；声明来自
    '.N/.M' 或 'Number of ...' 行。每个非声明/非注释行 = 一个子句；
    token 语法：'N<k>' = 取反，'-<k>' = 取反，'<k>' = 正文字。
    变量基判定：文件含裸 '0' token → 0-based（'0' = 变量 0，as 族实证：
    as9 声明 avg 4.2957 与逐行 token 统计精确吻合）；否则若 max token ==
    声明变量数 → 1-based（tm 族：max 2421 == .M 2421）；否则若 ==
    声明变量数-1 → 0-based；以上皆不满足 → 拒绝。"""
    clause_lines = []
    for s in (ln.strip() for ln in text.splitlines()):
        if not s or s.startswith(("#", "c", "%", ".", "p")):
            continue
        if re.match(r"(Number|Average|Max\.?|Min\.?)\b", s):
            continue                                   # as8 式声明行
        clause_lines.append(s)

    def raw(t):                                        # 'N12'->12, '-3'->3, '5'->5
        return int(t[1:]) if t.startswith("N") and t[1:].isdigit() \
            else abs(int(t)) if t.lstrip("-").isdigit() and t.startswith("-") \
            else int(t) if t.isdigit() else None

    toks = [(t, raw(t)) for s in clause_lines for t in s.split()]
    if any(v is None for _, v in toks):
        raise ValueError("unknown token shape in legacy file")
    has_zero = any(v == 0 for _, v in toks)
    max_raw = max(v for _, v in toks)
    dv = decl.get("decl_vars")
    if has_zero:
        base = 0
    elif dv and max_raw == dv:
        base = 1
    elif dv and max_raw == dv - 1:
        base = 0
    else:
        raise ValueError(f"cannot determine variable base (max={max_raw}, M={dv})")

    clauses = []
    for s in clause_lines:
        cl = []
        for t in s.split():
            v = raw(t)
            dimacs = v + 1 if base == 0 else v         # 0-based → DIMACS +1
            cl.append(-dimacs if t.startswith(("N", "-")) else dimacs)
        clauses.append(cl)

    if decl.get("decl_clauses") and len(clauses) != decl["decl_clauses"]:
        raise ValueError(f"clause count mismatch: parsed {len(clauses)} "
                         f"vs declared {decl['decl_clauses']}")
    if decl.get("avg_lits") is not None:
        sizes = [len(c) for c in clauses]
        if abs(sum(sizes) / len(sizes) - decl["avg_lits"]) > 5e-3:
            raise ValueError(f"avg literals mismatch: {sum(sizes)/len(sizes):.4f} "
                             f"vs declared {decl['avg_lits']}")
    if decl.get("max_lits") is not None and max(map(len, clauses)) != decl["max_lits"]:
        raise ValueError("max literals mismatch")
    if decl.get("min_lits") is not None and min(map(len, clauses)) != decl["min_lits"]:
        raise ValueError("min literals mismatch")
    n_vars = max((abs(l) for c in clauses for l in c), default=0)
    if dv and n_vars > dv:
        raise ValueError(f"variable index {n_vars} exceeds declared {dv}")
    return n_vars, clauses


def parse_dimacs(path: Path):
    """DIMACS 解析（标准 + 1996 legacy 方言）+ 声明自校验。

    标准格式：'p cnf' 头 + 整数流 + 0 终止符；容忍 c/#/% 注释与 SATLIB 式
    % 0 结尾。legacy 格式（as/tm 族）见 _parse_legacy。
    任何"解析计数与文件声明不符"的情况一律 raise —— 杜绝静默截断
    （2026-09-12 前旧版把 as/tm 族截成 1–21 条子句的事故根因）。"""
    text = path.read_text()
    decl = _read_declarations(text)
    if not decl.get("p_clauses") and (decl.get("decl_clauses") or decl.get("decl_vars")):
        n_vars, clauses = _parse_legacy(text, decl)
        return n_vars, clauses, decl.get("decl_clauses") or 0

    n_vars = decl.get("p_vars", 0)
    declared = decl.get("p_clauses", 0)
    toks: list[int] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(("p ", "c", "%", "#")):
            continue
        for t in line.split():
            if t == "0":
                toks.append(0)
                continue
            try:
                toks.append(int(t))
            except ValueError:
                pass          # 容忍行内杂质 token
    clauses, cur = [], []
    for t in toks:
        if t == 0:
            if cur:
                clauses.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        clauses.append(cur)
    if declared and len(clauses) != declared:
        raise ValueError(f"clause count mismatch: parsed {len(clauses)} "
                         f"vs declared {declared}")
    return n_vars or (max((abs(l) for c in clauses for l in c), default=0)), clauses, declared


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--budget", type=int, default=10_000_000)
    args = ap.parse_args()

    import sqlite3
    from concurrent.futures import ThreadPoolExecutor, as_completed

    DB.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)

    rows = list(csv.DictReader(open(MANIFEST)))
    done = {(r[0], r[1]) for r in con.execute("SELECT family, inst_id FROM runs")}
    jobs = []
    for r in rows:
        rel = r["file"]
        fam = f"e4:{r['source']}:{r['family']}"
        inst_id = rel
        if (fam, inst_id) in {(x[0], x[1]) for x in done}:
            continue
        p = ROOT / "data/external/e4prime" / rel
        if not p.exists():
            continue
        jobs.append((fam, inst_id, p))

    print(f"{len(jobs)} instances to solve (budget={args.budget}, workers={args.workers})")

    def run(job):
        fam, inst_id, p = job
        n_vars, clauses, declared = parse_dimacs(p)
        t0 = time.time()
        res = solve_one(clauses, n_vars, "cadical", conflict_budget=args.budget)
        rec = {"family": fam, "params": json.dumps({"file": str(p.relative_to(ROOT)),
                                                    "n_vars": n_vars,
                                                    "n_clauses": declared or len(clauses)}),
               "seed": 0, "solver": "cadical", "inst_id": inst_id,
               "n_vars": n_vars, "n_clauses": len(clauses),
               "metrics_json": None, "swap_rejection_rate": None, **res,
               "parse_s": round(time.time() - t0, 3)}
        return rec

    COLS = ("family, params, seed, solver, inst_id, n_vars, n_clauses, metrics_json, "
            "swap_rejection_rate, status, conflicts, decisions, propagations, "
            "wall_s, conflict_budget")

    def upsert(con, rec):
        con.execute(
            f"INSERT OR REPLACE INTO runs ({COLS}) VALUES "
            "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            tuple(rec.get(c) for c in COLS.split(", ")))
        con.commit()

    with ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(run, j): j for j in jobs}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                rec = fut.result()
            except Exception as e:  # noqa: BLE001
                j = futs[fut]
                print(f"[{i}/{len(jobs)}] FAIL {j[1]}: {e}", flush=True)
                continue
            upsert(con, rec)
            print(f"[{i}/{len(jobs)}] {rec['inst_id']} {rec['status']} "
                  f"conf={rec['conflicts']} wall={rec['wall_s']}", flush=True)
    con.close()


if __name__ == "__main__":
    main()

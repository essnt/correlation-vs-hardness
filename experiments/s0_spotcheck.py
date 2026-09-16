#!/usr/bin/env python3
"""AMEND-2(3b) spot-check：对 S0 中 α_c 低置信（交叉点 resolution <60% 或测量饱和）
的 r，在 α_c ± 0.2 处用 4 个新鲜种子（16–19，避开 S0 的 0–15）× 10⁸ 冲突预算 ×
480s 墙钟重测，用于给 α_c 偏差定界。只产出数据，不改 α_c。

AMEND-2 偏差方向：墙钟删失偏 UNSAT 侧 → resolved-SAT 率抬高 → α_c 系统性高估。
spot-check 若在 α_c − 0.2 处发现大量 UNSAT（1e8 预算下），说明 α_c 确实被高估。

低置信 r 集合由与 m2_e3a_main.alpha_c_from_s0 相同的判据现场重算（读 m2_s0.db）。
产出: results/m2_s0_spotcheck.db + stdout 表。
建议: E3a 主扫描结束后以 --workers 4 运行（内存护栏）。
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cvh.solver import run_batch  # noqa: E402
from m2_s0_alpha_c import coarse_crossings  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
S0_DB = ROOT / "results" / "m2_s0.db"
DB = ROOT / "results" / "m2_s0_spotcheck.db"
if not (S0_DB.resolve().is_relative_to(ROOT) and DB.resolve().is_relative_to(ROOT)):
    raise ValueError("DB paths must stay inside the project root")
R_LEVELS = [0.06, 0.08, 0.11, 0.15, 0.22, 0.3, 0.5, 0.8, 1.5]
BUDGET, WALL, EXTRA_SEEDS = 100_000_000, 480.0, range(16, 20)


def s0_resolved_counts():
    con = sqlite3.connect(S0_DB)
    counts: dict[float, dict[float, list[int]]] = {}
    for params, status in con.execute("SELECT params, status FROM runs"):
        p = json.loads(params)
        if p.get("stage") != "m2_s0" or status not in ("sat", "unsat"):
            continue
        cell = counts.setdefault(float(p["r"]), {}).setdefault(float(p["alpha"]), [0, 0])
        cell[0 if status == "sat" else 1] += 1
    con.close()
    return counts


def alpha_c_table():
    """与 m2_e3a_main.alpha_c_from_s0 相同口径（AMEND-2 兼容）→ {r: (alpha_c, low)}"""
    counts = s0_resolved_counts()
    coarse = coarse_crossings()
    out, low = {}, set()
    for r in R_LEVELS:
        cells = sorted((a, c) for a, c in counts.get(r, {}).items())
        if len(cells) < 3:
            out[r] = coarse[r]
            low.add(r)
            continue
        prev, crossed = None, None
        for a, (s, u) in cells:
            rate = s / (s + u)
            if prev is not None and prev[1] >= 0.5 > rate:
                pa, pr = prev
                crossed = pa + (pr - 0.5) / (pr - rate) * (a - pa)
                break
            prev = (a, rate)
        if crossed is None:
            crossed = min(cells, key=lambda ac: abs(ac[1][0] / sum(ac[1]) - 0.5))[0]
        pair = [c for a, c in cells if abs(a - crossed) <= 0.05 + 1e-9]
        if pair and sum(s + u for s, u in pair) / (16 * len(pair)) < 0.6:
            low.add(r)
        out[r] = crossed
    return out, low


def main():
    ac, low = alpha_c_table()
    print("alpha_c:", {r: round(a, 3) for r, a in sorted(ac.items())})
    print("low-confidence:", sorted(low))
    if not low:
        print("nothing to spot-check")
        return
    jobs = []
    for r in sorted(low):
        for d in (-0.2, +0.2):
            a = round(ac[r] + d, 2)
            for s in EXTRA_SEEDS:
                jobs.append(("geo_random",
                             {"n": 400, "alpha": a, "r": r,
                              "stage": "m2_s0_spotcheck", "spot_offset": d},
                             s, "cadical", BUDGET, False, WALL))
    print(f"{len(jobs)} spot-check jobs (budget {BUDGET:.0e}, wall {WALL}s)")
    n = run_batch(jobs, DB, workers=int(sys.argv[sys.argv.index("--workers") + 1])
                  if "--workers" in sys.argv else 4)
    print(f"wrote {n} runs to {DB}")
    con = sqlite3.connect(DB)
    for params, status, conf in con.execute(
            "SELECT params, status, conflicts FROM runs ORDER BY params"):
        p = json.loads(params)
        print(f"r={p['r']:.2f} offset={p.get('spot_offset'):+.1f} a={p['alpha']:.2f} "
              f"seed={p.get('seed')} -> {status} conf={conf}")
    con.close()


if __name__ == "__main__":
    main()

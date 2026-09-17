#!/usr/bin/env python3
"""S0 收尾：从 m2_s0.db 提取 alpha_c(r)（与 m2_e3a_main.py 口径一致）+ 置信标记 + 图。

口径（AMEND-2 统一后，2026-09-10）：resolved-only——SAT 率只用 sat/unsat 行，
walltimeout/budget 行只计删失、不进阈值。每格给出删失率与 SAT 率；
无交叉格标记 lattice_nearest（AMEND-2 容忍项）。
输出 results/s0_alpha_c.json 与 results/figures/fig_s0_alphac.png，
并同步 arxiv/figures/（论文嵌图单源双写，LESSONS #17）。
"""
import json
import os
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))   # cvh 包导入引导（与 e5_gbdt 等一致）
DB = ROOT / "results/m2_s0.db"
FIG = ROOT / "results/figures/fig_s0_alphac.png"
R_LEVELS = [0.06, 0.08, 0.11, 0.15, 0.22, 0.3, 0.5, 0.8, 1.5]

CENSOR = {"budget", "walltimeout", "walltimeout_budget"}


def load():
    con = sqlite3.connect(DB)
    cells = defaultdict(lambda: defaultdict(lambda: {"sat": 0, "unsat": 0, "censored": 0}))
    for params, status in con.execute("SELECT params, status FROM runs"):
        p = json.loads(params)
        if p.get("stage") != "m2_s0":
            continue
        r, a = float(p["r"]), float(p["alpha"])
        c = cells[r][a]
        if status == "sat":
            c["sat"] += 1
        elif status == "unsat":
            c["unsat"] += 1
        elif status in CENSOR or status.startswith("walltimeout"):
            c["censored"] += 1
    con.close()
    return {r: dict(sorted(v.items())) for r, v in cells.items()}


def crossing(cells, use_censored_as_unsat):
    """返回 (alpha_c, flagged)。flagged='lattice_nearest' 若无真实交叉。"""
    pts = []
    for a, c in cells.items():
        s = c["sat"]
        u = c["unsat"] + (c["censored"] if use_censored_as_unsat else 0)
        n = s + u
        if n:
            pts.append((a, s / n, n))
    pts.sort()
    if not pts:
        return None, "no_data"
    prev = None
    for a, rate, n in pts:
        if prev and prev[1] >= 0.5 > rate:
            pa, pr, _ = prev
            return pa + (pr - 0.5) / (pr - rate) * (a - pa), "crossing"
        prev = (a, rate, n)
    best = min(pts, key=lambda t: abs(t[1] - 0.5))
    return best[0], "lattice_nearest"


def main():
    cells = load()
    # 与 m2_e3a_main.alpha_c_from_s0 同口径：测量饱和 r 回退 R3 粗测值
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from m2_s0_alpha_c import coarse_crossings
    coarse = coarse_crossings()
    out = {"r_levels": R_LEVELS, "cells": {}, "alpha_c_frozen": {},
           "flags": {}, "censor_rate": {}}
    for r in R_LEVELS:
        if r not in cells:
            continue
        rc = cells[r]
        out["cells"][str(r)] = {str(a): c for a, c in rc.items()}
        total = sum(sum(c.values()) for c in rc.values())
        cens = sum(c["censored"] for c in rc.values())
        out["censor_rate"][str(r)] = round(cens / total, 3) if total else None
        # 与 E3a 同判据：resolved 格 <3 个 ⇒ 测量饱和 ⇒ 粗测回退
        n_res_cells = sum(1 for a, c in sorted(rc.items()) if c["sat"] + c["unsat"] > 0)
        if n_res_cells < 3:
            out["alpha_c_frozen"][str(r)] = round(coarse[r], 4)
            out["flags"][str(r)] = {"frozen": "measurement_saturated_coarse_fallback"}
            continue
        # AMEND-2 冻结口径：只用 resolved（sat/unsat）行
        a1, f1 = crossing(rc, False)
        if a1 is None:
            out["alpha_c_frozen"][str(r)] = round(coarse[r], 4)
            out["flags"][str(r)] = {"frozen": "measurement_saturated_coarse_fallback"}
            continue
        out["alpha_c_frozen"][str(r)] = round(a1, 4)
        out["flags"][str(r)] = {"frozen": f1}
    (ROOT / "results/s0_alpha_c.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))

    # 图：alpha_c(r)（resolved-only 单口径）+ r=每格删失率
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import shutil

    rs = [r for r in R_LEVELS if str(r) in out["alpha_c_frozen"]]
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(rs, [out["alpha_c_frozen"][str(r)] for r in rs], "o-", label="frozen (resolved-only, AMEND-2)")
    for r in rs:
        if out["flags"][str(r)]["frozen"] == "lattice_nearest":
            ax[0].annotate("△", (r, out["alpha_c_frozen"][str(r)]), fontsize=11, color="tab:red")
    ax[0].set_xlabel("locality radius r"); ax[0].set_ylabel(r"$\alpha_c(r)$")
    ax[0].legend(); ax[0].set_title("S0: SAT-rate 0.5 crossing (n=400, 16 seeds)")
    xs = [x for x in out["censor_rate"] if out["censor_rate"][x] is not None]
    ax[1].bar(range(len(xs)), [out["censor_rate"][x] for x in xs])
    ax[1].set_xticks(range(len(xs)), xs, rotation=45)
    ax[1].set_ylabel("censored fraction"); ax[1].set_title("censoring per r (budget+walltime)")
    ax[1].axhline(0.3, color="tab:red", ls=":", label="30% flag")
    ax[1].legend()
    plt.tight_layout()
    plt.savefig(FIG, dpi=150)
    arx = ROOT / "arxiv/figures/fig_s0_alphac.png"
    arx.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FIG, arx)          # 论文嵌图同步（LESSONS #17）
    print(json.dumps({r: out["alpha_c_frozen"][str(r)] for r in rs}, indent=0))
    print("flags:", json.dumps(out["flags"]))
    print("censor_rate:", json.dumps(out["censor_rate"]))
    print("-> results/s0_alpha_c.json", FIG)


if __name__ == "__main__":
    main()

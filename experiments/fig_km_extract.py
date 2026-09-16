#!/usr/bin/env python3
"""论文嵌图 fig_km 再生：Kaplan–Meier time-to-decision by locality radius (Δ-pooled)。

数据: results/m2_main.db 的 geo_random × cadical 行（全部 Δ 臂合并，Δ-pooled）。
duration = conflicts；event = status ∈ {sat, unsat}（budget/walltimeout 行按删失处理）。
输出 results/figures/fig_km.png 并同步 arxiv/figures/（论文嵌图单源双写，LESSONS #17）。
"""
import json
import shutil
import sqlite3
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results/figures/fig_km.png"
ARX = ROOT / "arxiv/figures/fig_km.png"
RS = [0.06, 0.08, 0.11, 0.15, 0.22, 0.3, 0.5, 0.8, 1.5]


def load():
    con = sqlite3.connect(ROOT / "results/m2_main.db")
    query = "SELECT params, status, conflicts FROM runs WHERE family = ? AND solver = ?"
    rows = con.execute(query, ("geo_random", "cadical")).fetchall()
    con.close()
    per_r = defaultdict(lambda: {"dur": [], "event": []})
    for params, status, conflicts in rows:
        r = json.loads(params).get("r")
        if conflicts is None or conflicts <= 0:
            continue
        per_r[r]["dur"].append(float(conflicts))
        per_r[r]["event"].append(status in ("sat", "unsat"))
    return per_r


def main():
    per_r = load()
    fig, ax = plt.subplots(figsize=(11, 6))
    cmap = plt.get_cmap("viridis")
    rs = [r for r in RS if r in per_r]
    for i, r in enumerate(rs):
        kmf = KaplanMeierFitter(label=f"r={r}")
        kmf.fit(per_r[r]["dur"], event_observed=per_r[r]["event"])
        kmf.plot_survival_function(ax=ax, ci_show=False,
                                   color=cmap(i / max(len(rs) - 1, 1)))
    ax.set_xlabel("conflicts (CaDiCaL budget scale)")
    ax.set_ylabel("P(not yet decided)")
    ax.set_yscale("log")               # KM 惯例对数纵轴：显示小 r 的删失平台
    ax.set_ylim(0.005, 1.15)
    ax.set_title("Kaplan–Meier: time-to-decision by locality radius (Δ-pooled)")
    ax.legend(loc="center right", ncol=2)
    fig.tight_layout()
    fig.savefig(FIG, dpi=150)
    ARX.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FIG, ARX)          # 论文嵌图同步（LESSONS #17）
    print("wrote", FIG, "and", ARX)


if __name__ == "__main__":
    main()

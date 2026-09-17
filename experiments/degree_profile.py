#!/usr/bin/env python3
"""Literal-degree 形态重测（H2 前提偏离披露的 committed 数据源）。

背景：论文 Threats 段披露 geo_random 主族在 Δ=+0.2 臂的 literal-degree
分布形态跨 r 漂移（SD/CV/max），超出冻结前提的 <5% 匹配判据。初版数字
（SD 2.23–2.73、CV ~0.5→0.37）来自 2026-09-11 一次未入库的补测；2026-09-12
独立审查发现其低端不可复现（SD 低端实为 ~2.37），本脚本将重测固化为 committed
产物：对 results/m2_main.db 中 family=geo_random、delta=+0.2 的 9 r 格
× 30 种子，用与实验完全一致的确定性生成路径（locality_kernel planted=False）
重生成实例并逐格核对 inst_id 与 DB 精确一致，再计算每实例的 literal-degree
（变量被文字引用的次数，正负均计）分布统计。

口径：SD 与 CV 为 per-instance 值的 per-r 均值；max 为每 r 跨 30 种子的
全局最大（非 per-instance 均值）。

输出: results/degree_profile.json + stdout 摘要
"""
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cvh.generators import locality_kernel  # noqa: E402

DB = ROOT / "results/m2_main.db"
OUT = ROOT / "results/degree_profile.json"


def degree_stats(inst) -> dict:
    cnt: Counter = Counter()
    for cl in inst.clauses:
        for lit in cl:
            cnt[abs(lit)] += 1
    degs = [cnt.get(v, 0) for v in range(1, inst.n_vars + 1)]
    m = sum(degs) / len(degs)
    sd = (sum((d - m) ** 2 for d in degs) / len(degs)) ** 0.5
    return {"mean_degree": m, "sd": sd, "cv": sd / m, "max": max(degs)}


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT params, seed, inst_id FROM runs WHERE family = ?",
        ("geo_random",)).fetchall()
    seen = {}
    for (p, seed, iid) in rows:
        d = json.loads(p)
        if d.get("delta") != 0.2:
            continue
        seen[(d["r"], d["alpha"], seed)] = (iid, d["n"])

    per_r: dict = {}
    matched = 0
    for (r, alpha, seed), (iid, n) in sorted(seen.items()):
        inst = locality_kernel(n, alpha, r, seed, planted=False)
        if inst.inst_id != iid:
            raise SystemExit(f"inst_id mismatch at r={r} alpha={alpha} seed={seed}")
        matched += 1
        per_r.setdefault(r, []).append(degree_stats(inst))

    out = {"meta": {
                "source_db": "results/m2_main.db",
                "family": "geo_random (locality_kernel planted=False)",
                "arm": "delta=+0.2, n=400, 30 seeds per radius",
                "instances": matched,
                "caliber": "SD/CV = per-instance value averaged per radius; "
                           "max_global = global max across the 30 seeds per "
                           "radius; max_mean = per-instance max averaged per radius",
           },
           "per_r": {}}
    for r in sorted(per_r):
        sts = per_r[r]
        out["per_r"][str(r)] = {
            "n": len(sts),
            "mean_degree": round(sum(s["mean_degree"] for s in sts) / len(sts), 4),
            "sd_mean": round(sum(s["sd"] for s in sts) / len(sts), 4),
            "cv_mean": round(sum(s["cv"] for s in sts) / len(sts), 4),
            "max_global": max(s["max"] for s in sts),
            "max_mean": round(sum(s["max"] for s in sts) / len(sts), 3),
        }
    sds = [out["per_r"][k]["sd_mean"] for k in out["per_r"]]
    cvs = [out["per_r"][k]["cv_mean"] for k in out["per_r"]]
    mxs = [out["per_r"][k]["max_global"] for k in out["per_r"]]
    out["summary"] = {
        "sd_low": min(sds), "sd_high": max(sds),
        "sd_drift_pct": round((max(sds) - min(sds)) / min(sds) * 100, 1),
        "cv_low": min(cvs), "cv_high": max(cvs),
        "max_low": min(mxs), "max_high": max(mxs),
        "max_drift_pct": round((max(mxs) - min(mxs)) / min(mxs) * 100, 1),
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    s = out["summary"]
    print(f"instances: {matched} (inst_id 全部与 DB 一致)")
    for k in out["per_r"]:
        e = out["per_r"][k]
        print(f"  r={k:<5} mean_deg={e['mean_degree']:<7.3f} sd={e['sd_mean']:.3f} "
              f"cv={e['cv_mean']:.3f} max={e['max_global']}")
    print(f"summary: SD {s['sd_low']:.3f}-{s['sd_high']:.3f} "
          f"(+{s['sd_drift_pct']}%) | CV {s['cv_low']:.3f}-{s['cv_high']:.3f} | "
          f"max {s['max_low']}-{s['max_high']} (+{s['max_drift_pct']}%)")
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()

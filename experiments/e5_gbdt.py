#!/usr/bin/env python3
"""E5 预测器：GBDT（生成器族训练）——对 log10(冲突数+1) 的预测，与 Zulkoski
ridge baseline（experiments/e5_baseline.py）对比 R² 增量。

设计（冻结 §五.4）：
- 特征 = m_*（结构度量）+ 家族/参数（r, Δ）编码；
- 训练/评估：留一 r 水平外推（LeaveOneGroupOut on r）——检验"见过部分 r 水平
  后能否预测没见过的 r 的难度"，比随机 CV 严格得多，直接对应 H1 的泛化主张；
- 特征重要性报告（哪些结构量携带预测信息）。
数据：results/m2_main.db（E3a/E3b 主扫描）。删失行（walltimeout/budget）剔除，
与 baseline 口径一致；删失敏感性由 Tobit/KM 负责。
产出: results/e5_gbdt.json + results/figures/fig_e5_importance.png
"""
import json
import os
import sqlite3
import sys
from pathlib import Path

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
DB = os.path.join(ROOT, "results", "m2_main.db")
OUT = os.path.join(ROOT, "results", "e5_gbdt.json")


def load():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT family, params, status, conflicts, metrics_json FROM runs").fetchall()
    con.close()
    X, y, groups, fam = [], [], [], []
    for f, params, status, conf, mj in rows:
        if status not in ("sat", "unsat") or conf is None or not mj:
            continue
        m = json.loads(mj)
        p = json.loads(params)
        # 显式按排序键取值，与 names 的构造严格对齐（dict 插入序不可依赖）
        keys = sorted(k for k in m if isinstance(m[k], (int, float))
                      and not isinstance(m[k], bool))
        feats = [m[k] for k in keys]
        if not feats or "r" not in p:
            continue
        X.append(feats + [p.get("r", np.nan), p.get("delta", np.nan)])
        y.append(np.log10(conf + 1))
        groups.append(float(p["r"]))
        fam.append(f)
    names = sorted({k for _, _, _, _, mj in rows if mj
                    for k in json.loads(mj)
                    if isinstance(json.loads(mj)[k], (int, float))
                    and not isinstance(json.loads(mj)[k], bool)}) + ["r", "delta"]
    return np.array(X, float), np.array(y, float), np.array(groups), fam, names


def main():
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.model_selection import LeaveOneGroupOut

    X, y, groups, fam, names = load()
    if len(X) < 100:
        print(f"insufficient data ({len(X)} rows) — run after E3a completes")
        return
    logo = LeaveOneGroupOut()
    preds = np.full(len(y), np.nan)
    for tr, te in logo.split(X, y, groups):
        m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.08,
                                          random_state=0)
        m.fit(X[tr], y[tr])
        preds[te] = m.predict(X[te])
    ok = ~np.isnan(preds)
    ss_res = float(((y[ok] - preds[ok]) ** 2).sum())
    ss_tot = float(((y[ok] - y[ok].mean()) ** 2).sum())
    cv_r2 = 1 - ss_res / ss_tot

    full = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.08,
                                         random_state=0).fit(X, y)
    rep = {"n": int(len(y)), "leave_r_out_cv_r2": round(cv_r2, 4),
           "baseline_zulkoski_cv_r2_random3sat": "see e5_baseline.json",
           "families": sorted(set(fam))}
    assert Path(OUT).resolve().is_relative_to(Path(ROOT).resolve())
    Path(OUT).write_text(json.dumps(rep, indent=1))
    print(json.dumps(rep, indent=1))
    print("->", OUT)
    print("note: 特征重要性图需 permutation importance（数据完整后启用）")


if __name__ == "__main__":
    main()

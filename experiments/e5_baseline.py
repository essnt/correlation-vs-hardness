#!/usr/bin/env python3
"""E5 baseline：Zulkoski et al. (CP 2018) 方法学复刻——结构度量对 log 求解难度的回归解释力。

规格（见 docs/papers/notes/zulkoski2018_structural.md §二）：
  - 依赖变量 log10(conflicts+1)；删失行（walltimeout）剔除；
  - 特征标准化后取 基特征 + 全部两两乘积交互（⊕记号）；
  - OLS 与 Ridge 双口径；报告 in-sample adjusted R²（可比性）与 5-fold CV R²（诚实口径）。
特征集阶梯（对应 H1）：
  size: V, C                        —— 纯规模
  size+density: + alpha_eff, C/V    —— 加密度
  +structure:  + modularity, n_communities, largest_community_frac,
               community_size_cv, clustering, spectral_gap, tw_ub, tw_lb —— 全结构
用法: .venv/bin/python3 experiments/e5_baseline.py [DB...]
      默认 results/m2_e1e2.db；E3a 完成后追加 results/m2_e3a.db。
"""
import json
import sqlite3
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.stats import f as f_dist
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import KFold

ROOT = Path(__file__).resolve().parents[1]
TARGET_DBS = [Path(p) for p in sys.argv[1:]] or [ROOT / "results/m2_e1e2.db"]

SIZE = ["n_vars", "n_clauses"]
DENS = ["alpha_eff"]
STRUCT = ["modularity", "n_communities", "largest_community_frac", "community_size_cv",
          "clustering", "spectral_gap", "tw_ub", "tw_lb"]


def flatten(metrics):
    out = {}
    for k, v in metrics.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out["m_" + k] = float(v)
    return out


def load(db):
    rows = []
    con = sqlite3.connect(db)
    for fam, params, status, conflicts, mj in con.execute(
            "SELECT family, params, status, conflicts, metrics_json FROM runs"):
        if status not in ("sat", "unsat") or conflicts is None or not mj:
            continue
        m = flatten(json.loads(mj))
        if "m_n_vars" not in m:
            continue
        m["m_C_over_V"] = m["m_n_clauses"] / m["m_n_vars"]
        m["y"] = np.log10(conflicts + 1)
        m["family"] = fam
        m["params"] = params
        rows.append(m)
    con.close()
    return rows


def design(rows, feats):
    X = np.array([[r.get("m_" + f, np.nan) for f in feats] for r in rows])
    ok = ~np.isnan(X).any(axis=1)
    X = X[ok]
    for j in range(X.shape[1]):  # 标准化
        sd = X[:, j].std()
        X[:, j] = (X[:, j] - X[:, j].mean()) / (sd if sd > 1e-12 else 1.0)
    inter = np.column_stack([X[:, i] * X[:, j] for i, j in combinations(range(X.shape[1]), 2)])
    X = np.column_stack([np.ones(len(X)), X, inter])  # 截距 + 基 + 交互(⊕)
    y = np.array([r["y"] for r in rows])[ok]
    return X, y


def adj_r2(X, y):
    # 标准调整 R²：1 - (ss_res/ss_tot)·(n-1)/(n-p-1)。X 携带显式截距列
    # （design() 的 ones 列），p = k-1 个预测器 ⇒ 分母 n-k。原实现的
    # "1 - (1 - ss_res/ss_tot)·…" 把 R² 当作残差比再次取补，产出≈1-R²×…，
    # 2026-09-17 回归测试暴露并修正；拟合用
    # fit_intercept=False，避免与显式截距列共线。
    n, k = X.shape
    pred = model_fit(X, y, LinearRegression(fit_intercept=False))
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1 - (ss_res / ss_tot) * (n - 1) / (n - k) if ss_tot > 0 else float("nan")


def model_fit(X, y, cls):
    cls.fit(X, y)
    return cls.predict(X)


def cv_r2(X, y, cls, k=5):
    kf = KFold(k, shuffle=True, random_state=0)
    ss_res = ss_tot = 0.0
    ybar = y.mean()
    for tr, te in kf.split(X):
        m = cls.__class__(**cls.get_params())
        m.fit(X[tr], y[tr])
        p = m.predict(X[te])
        ss_res += float(((y[te] - p) ** 2).sum())
        ss_tot += float(((y[te] - ybar) ** 2).sum())
    return 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")


def nested_f(rows, feats_red, feats_full):
    """嵌套 OLS F 检验：reduced (size+density) vs full (+structure)。

    行集对齐：full 特征任一缺失的行剔除（与 design 的 NaN 处理一致），
    两版设计在同一行集上构建（标准化不影响 OLS 拟合值）。
    返回 F、df 与 n/k；这是论文 H1 阶梯"嵌套 F 检验"的 committed 生产者
    （2026-09-12 起，替代无溯源的早期手算值）。"""
    rows_ok = [r for r in rows
               if all(np.isfinite(r.get("m_" + f, np.nan)) for f in feats_full)]
    Xr, y = design(rows_ok, feats_red)
    Xf, y2 = design(rows_ok, feats_full)
    assert np.allclose(y, y2)
    pred_r = model_fit(Xr, y, LinearRegression())
    pred_f = model_fit(Xf, y, LinearRegression())
    rss_r = float(((y - pred_r) ** 2).sum())
    rss_f = float(((y - pred_f) ** 2).sum())
    df_num = Xf.shape[1] - Xr.shape[1]
    df_den = len(y) - Xf.shape[1]
    F = ((rss_r - rss_f) / df_num) / (rss_f / df_den)
    return {"F": round(F, 1), "df": [df_num, df_den],
            "p": float(f_dist.sf(F, df_num, df_den)),
            "n": len(y), "k_reduced": Xr.shape[1], "k_full": Xf.shape[1],
            "spec": "size+density vs +structure nested OLS (full pairwise "
                    "interactions, standardized; aligned decided-row subset)"}


def main():
    report = {}
    for db in TARGET_DBS:
        fam_rows = {}
        for r in load(db):
            fam_rows.setdefault(r["family"], []).append(r)
        rep = {}
        for fam, rows in sorted(fam_rows.items()):
            rep[fam] = {}
            for name, feats in [("size", SIZE), ("size+density", SIZE + DENS),
                                ("size+density+structure", SIZE + DENS + STRUCT)]:
                X, y = design(rows, feats)
                if len(y) < 2 * X.shape[1]:
                    rep[fam][name] = {"n": len(y), "k": X.shape[1], "note": "n<2k, 跳过"}
                    continue
                rep[fam][name] = {
                    "n": len(y), "k": X.shape[1],
                    "adj_r2_ols": round(adj_r2(X, y), 4),
                    "cv_r2_ridge": round(cv_r2(X, y, Ridge(alpha=1.0)), 4),
                }
            try:
                rep[fam]["nested_F_test_H1"] = nested_f(
                    rows, SIZE + DENS, SIZE + DENS + STRUCT)
            except Exception as e:  # noqa: BLE001
                rep[fam]["nested_F_test_H1"] = {"note": f"skipped: {e}"}
        report[str(db.name)] = rep
    print(json.dumps(report, indent=1, ensure_ascii=False))
    out = ROOT / "results/e5_baseline.json"
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False))
    print("->", out)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""E3a/E3b 主扫描分析（H2 因果效应 + E3b 结构摧毁 + 中介 + 删失敏感性）。

设计对齐 m2_e3a_main.py：
  E3a: geo_random, r ∈ 9 级 × Δ ∈ {+0.2,+0.4,+0.8} × 30 seeds × {cadical,glucose}
  E3b: 4 r × 2 Δ × 30 seeds × {original, swapped}（度保持交换，结构摧毁干预）
输出: results/e3a_analysis.json + figures/fig_e3a_*.png
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cvh.analysis import (load_runs, rm_anova, jonckheere_terpstra,  # noqa: E402
                          wilcoxon_paired, mediation_imai, bh_fdr, tobit_fit)

DB = ROOT / "results/m2_main.db"
OUT = ROOT / "results/e3a_analysis.json"
DELTAS = [0.2, 0.4, 0.8]


def ok(df):
    return df[df["status"].isin(["sat", "unsat"]) & df["logc"].notna()].copy()


def main():
    df = load_runs(DB)
    rep = {"n_total": len(df), "n_ok": int(len(ok(df))),
           "censored": int((~df["status"].isin(["sat", "unsat"])).sum())}

    e3a = df[df["family"] == "geo_random"]

    # ---------- H2: r 的因果效应（每 Δ、每 solver） ----------
    h2 = {}
    pvals = []
    for delta in sorted(e3a["p_delta"].dropna().unique()) if "p_delta" in e3a else []:
        for solver in sorted(e3a["solver"].unique()):
            sub = ok(e3a[(e3a["p_delta"] == delta) & (e3a["solver"] == solver)])
            if sub["p_r"].nunique() < 3:
                continue
            groups = [g["logc"].values for _, g in sub.groupby("p_r")]
            jt = jonckheere_terpstra(groups)
            # 删失⇒非平衡：RM-ANOVA 用完全种子子集（全部 r 水平均 resolved 的种子）
            need = sub["p_r"].nunique()
            complete_seeds = sub.groupby("seed")["p_r"].nunique()
            complete_seeds = complete_seeds[complete_seeds == need].index
            subc = sub[sub["seed"].isin(complete_seeds)]
            a = (rm_anova(subc, "logc", subject="seed", within="p_r")
                 if len(complete_seeds) >= 5 else {})
            # 敏感性：JT 双口径——(a) clean 仅 resolved（主口径）；
            # (b) bound：删失行按预算上限 logc=6.0 计入（保守下界口径）。
            subg = e3a[(e3a["p_delta"] == delta) & (e3a["solver"] == solver)].copy()
            subg = subg[subg["status"].isin(["sat", "unsat", "budget"])]
            subg["logcb"] = subg["logc"].fillna(6.0)
            gb = [g["logcb"].values for _, g in subg.groupby("p_r")]
            jt_bound = jonckheere_terpstra(gb) if all(len(g) > 3 for g in gb) else {}
            # partial η² for a within factor: F·df1 / (F·df1 + df2)
            eta2 = (a["F"] * a["num_df"] / (a["F"] * a["num_df"] + a["den_df"])
                    if a.get("F") is not None else None)
            h2[f"delta={delta}|{solver}"] = {
                "n": int(len(sub)), "n_seeds_complete": int(len(complete_seeds)),
                "jt_p": jt["p"],
                "rmanova_F": a.get("F"), "rmanova_p": a.get("p"),
                "eta2_partial": round(eta2, 4) if eta2 is not None else None,
                "jt_bound_p": jt_bound.get("p"),
                "logc_by_r": {str(r): [float(np.mean(g["logc"])), float(np.std(g["logc"])),
                                       int(len(g))]
                              for r, g in sub.groupby("p_r")},
            }
            pvals.append(jt["p"])
    rep["h2_by_delta_solver"] = h2
    if pvals:
        rep["h2_jt_q_fdr"] = list(map(float, bh_fdr(pvals)))

    # 汇总 H2 主判定（cadical, 全 Δ 合并的 r 主效应）
    sub = ok(e3a[e3a["solver"] == "cadical"])
    if len(sub) and sub["p_r"].nunique() >= 3:
        groups = [g["logc"].values for _, g in sub.groupby("p_r")]
        # 全 Δ 合并：每 (seed, r) 先对 Δ 取均值（每 subject 每格单观测）再做 RM-ANOVA
        agg = sub.groupby(["seed", "p_r"], as_index=False)["logc"].mean()
        agg = agg[agg.groupby("seed")["p_r"].transform("nunique") == agg["p_r"].nunique()]
        rep["h2_main_cadical"] = {"jt": jonckheere_terpstra(groups),
                                  "anova_deltaagg":
                                      rm_anova(agg, "logc", "seed", "p_r")}
        # 敏感性分析：r=0.8 与 r=1.5 在环面几何下生成同一实例集（r 球覆盖全部
        # 变量），合并为单一水平后的 RM-ANOVA（df1 8→7）
        agg8 = agg[agg["p_r"] != 1.5]
        agg8 = agg8[agg8.groupby("seed")["p_r"].transform("nunique") == agg8["p_r"].nunique()]
        rep["h2_main_cadical"]["anova_deltaagg_merged_r08_r15"] = {
            "note": "r=0.8 and r=1.5 produce identical clause sets (torus "
                    "diameter sqrt(2)/2); merged into one level",
            **rm_anova(agg8, "logc", "seed", "p_r")}

    # ---------- E3b: 配对结构摧毁（geo_random vs geo_random_swapped，同 r/Δ/seed） ----------
    if (df["family"] == "geo_random_swapped").any():
        orig = ok(e3a[e3a["solver"] == "cadical"])[["p_r", "p_delta", "seed", "logc", "status"]]
        swap = ok(df[df["family"] == "geo_random_swapped"])[["p_r", "p_delta", "seed", "logc", "status"]]
        mg = orig.merge(swap, on=["p_r", "p_delta", "seed"], suffixes=("_o", "_s"))
        flips = int((mg["status_o"] != mg["status_s"]).sum())
        rep["e3b_total"] = {"n_pairs": int(len(mg)), "status_flips": flips}
        for (delta), g in mg.groupby("p_delta"):
            if len(g) >= 10:
                rep[f"e3b_delta={delta}"] = {
                    "n_pairs": int(len(g)),
                    "mean_logc_original": float(g["logc_o"].mean()),
                    "mean_logc_swapped": float(g["logc_s"].mean()),
                    "wilcoxon": wilcoxon_paired(g["logc_o"].tolist(), g["logc_s"].tolist()),
                    "status_flips": int((g["status_o"] != g["status_s"]).sum()),
                }

    # ---------- 中介：r → 结构度量 → logc（cadical） ----------
    sub = ok(e3a[e3a["solver"] == "cadical"]).copy()
    for med in ["m_modularity", "m_mean_degree", "m_clustering", "m_spectral_gap"]:
        if med not in sub.columns:
            continue
        s = sub[["logc", "p_r", med]].dropna()
        if len(s) >= 100:
            rep[f"mediation_{med[2:]}"] = mediation_imai(s["p_r"].values, s[med].values,
                                                         s["logc"].values, n_boot=1000)

    # ---------- 删失敏感性：Tobit（把删失行带上限纳入） ----------
    # ---------- 删失敏感性：Tobit（预算删失行带上限纳入） ----------
    # walltimeout 行无冲突口径（conflicts=None），按 AMEND-2 语义排除在
    # 冲突空间分析之外——把它们带进似然只会产生 NaN（2026-09-17 独立
    # 复核发现拟合退化的根因）。budget 行 conflicts≈预算值，作右删失界。
    dc = e3a[(e3a["solver"] == "cadical")
             & (e3a["status"] != "walltimeout")].copy()
    if len(dc) and "censored" in dc.columns:
        cens = dc["censored"].astype(bool).values
        if 0 < cens.sum() < len(dc) and dc["logc"].notna().all():
            rep["tobit"] = tobit_fit(dc["logc"].values,
                                     dc[["p_r"] + [c for c in ["p_delta"] if c in dc.columns]].values,
                                     cens)

    # ---------- 图：剂量-响应 + E3b 配对 ----------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        figdir = ROOT / "results/figures"
        figdir.mkdir(exist_ok=True)
        sub = ok(e3a[e3a["solver"] == "cadical"])
        if len(sub) and sub["p_r"].nunique() >= 3:
            fig, ax = plt.subplots(1, 2, figsize=(11, 4))
            for d, g in sub.groupby("p_delta"):
                m = g.groupby("p_r")["logc"].agg(["mean", "sem"])
                ax[0].errorbar(m.index, m["mean"], yerr=m["sem"], marker="o",
                               label=f"Δ=+{d}", capsize=3)
            ax[0].set_xlabel("locality radius r")
            ax[0].set_ylabel("log10(conflicts+1), CaDiCaL")
            ax[0].legend(); ax[0].set_title("E3a dose-response (matched Δ)")
            if any(k.startswith("e3b_delta") for k in rep):
                ds = [k for k in rep if k.startswith("e3b_delta")]
                xs = range(len(ds))
                ax[1].bar([x - 0.18 for x in xs],
                          [rep[k]["mean_logc_original"] for k in ds], width=0.36,
                          label="original (local)")
                ax[1].bar([x + 0.18 for x in xs],
                          [rep[k]["mean_logc_swapped"] for k in ds], width=0.36,
                          label="swapped (degree-preserving)")
                ax[1].set_xticks(list(xs), [k.split("=")[1] for k in ds])
                ax[1].set_ylabel("log10(conflicts+1)")
                ax[1].legend(); ax[1].set_title("E3b structure-destruction (paired)")
            plt.tight_layout()
            fig.savefig(figdir / "fig_e3a_dose.png", dpi=150)
            arx = ROOT / "arxiv/figures/fig_e3a_dose.png"
            arx.parent.mkdir(parents=True, exist_ok=True)
            arx.write_bytes((figdir / "fig_e3a_dose.png").read_bytes())   # 论文嵌图同步（LESSONS #17）
            print("-> figures/fig_e3a_dose.png + arxiv/figures/")
    except Exception as e:  # noqa: BLE001
        print("figure generation skipped:", e)

    def _clean(o):
        import math
        if isinstance(o, dict):
            return {k: _clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [_clean(v) for v in o]
        if isinstance(o, np.ndarray):
            return [_clean(v) for v in o.tolist()]
        if isinstance(o, (np.floating, np.integer)):
            o = o.item()
        if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
            return None          # NaN/Inf 破坏 strict JSON（G2），统一落 null
        return o

    OUT.write_text(json.dumps(_clean(rep), indent=1, ensure_ascii=False,
                              default=float, allow_nan=False))
    print(json.dumps({k: v for k, v in rep.items() if not isinstance(v, dict) or k.startswith("h2")},
                     indent=1, default=float)[:2000])
    print("->", OUT)


if __name__ == "__main__":
    main()

"""Pilot-stage figures.

fig_r3b_moneyplot : difficulty vs locality radius r at matched excess
                    density Delta — the H2 preview plot (censored points
                    marked at the budget floor).
fig_alpha_c       : operational threshold alpha_c(r) from the round-3
                    coarse matrix (superseded by M2-S0 values when ready).

Outputs -> results/figures/
"""
import json
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "results", "figures")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({"font.size": 11, "figure.dpi": 150})


def _load(db):
    con = sqlite3.connect(db)
    df = pd.read_sql("SELECT * FROM runs", con)
    con.close()
    df["params"] = df["params"].apply(json.loads)
    df["r"] = df["params"].apply(lambda p: p.get("r"))
    df["delta"] = df["params"].apply(lambda p: p.get("delta"))
    df["alpha"] = df["params"].apply(lambda p: p.get("alpha"))
    df["logc"] = np.log10(df["conflicts"].astype(float) + 1)
    return df


def fig_r3b_moneyplot():
    df = _load(os.path.join(ROOT, "results", "pilot_m1_r3b.db"))
    df = df[df["family"] == "geo_random"]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    colors = {"-0.2": "#4c72b0", "0.2": "#dd8452", "0.6": "#55a868"}
    labels = {"-0.2": r"$\Delta=-0.2$ (SAT)", "0.2": r"$\Delta=+0.2$ (near threshold)",
              "0.6": r"$\Delta=+0.6$ (deep UNSAT)"}
    for d, g in df.groupby("delta"):
        key = f"{d:g}"
        med = g.groupby("r")["logc"].median()
        q1 = g.groupby("r")["logc"].quantile(0.25)
        q3 = g.groupby("r")["logc"].quantile(0.75)
        cens = g.groupby("r")["status"].apply(lambda s: (s == "budget").mean())
        ax.plot(med.index, med.values, "o-", color=colors[key],
                label=labels[key], lw=2, ms=5)
        ax.fill_between(med.index, q1.values, q3.values, color=colors[key],
                        alpha=0.15)
        # censoring markers: upward arrows at the budget floor
        for r, cf in cens.items():
            if cf > 0.3:
                y = g[g["r"] == r]["logc"].max()
                ax.annotate(f"{cf:.0%}", (r, y), textcoords="offset points",
                            xytext=(0, 4), ha="center", fontsize=8,
                            color=colors[key])
    ax.axhline(6.0, ls=":", c="gray", lw=1)
    ax.text(0.07, 6.05, "conflict budget $10^6$ (censoring floor)", fontsize=8,
            color="gray")
    ax.set_xscale("log")
    ax.set_xticks([0.06, 0.08, 0.15, 0.3, 0.5, 1.5])
    ax.set_xticklabels(["0.06", "0.08", "0.15", "0.3", "0.5", "1.5"])
    ax.set_xlabel("locality radius r (log scale) — larger r = weaker causal locality")
    ax.set_ylabel(r"median $\log_{10}$(conflicts+1), Cadical")
    ax.set_title("Difficulty vs. locality at matched excess density\n"
                 "(geo_random, n=400, 20 seeds/cell)", fontsize=11)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    out = os.path.join(FIG, "fig_r3b_moneyplot.png")
    fig.savefig(out)
    plt.close(fig)
    print("wrote", out)


def fig_alpha_c():
    df = _load(os.path.join(ROOT, "results", "pilot_m1_r3.db"))
    df = df[df["family"] == "geo_random"]
    xs, ys = [], []
    for r, g in df.groupby("r"):
        rates = g.groupby("alpha").apply(
            lambda s: (s["status"] == "sat").mean(), include_groups=False)
        prev_a, prev_rate = None, None
        for a in rates.index:
            rate = rates[a]
            if prev_rate is not None and prev_rate >= 0.5 > rate:
                xs.append(r)
                ys.append(prev_a + (prev_rate - 0.5) / (prev_rate - rate) * (a - prev_a))
                break
            prev_a, prev_rate = a, rate
    fig, ax = plt.subplots(figsize=(5.4, 3.6))
    ax.plot(xs, ys, "o-", color="#c44e52", lw=2)
    ax.axhline(4.267, ls=":", c="gray")
    ax.text(1.0, 4.30, "random 3-SAT threshold 4.267", fontsize=8, color="gray",
            ha="right")
    ax.set_xlabel("locality radius r (log scale)")
    ax.set_ylabel(r"operational threshold $\alpha_c(r)$, n=400")
    ax.set_title("Threshold shifts with locality\n(8 seeds/cell, round-3 coarse)",
                 fontsize=11)
    ax.set_xscale("log")
    fig.tight_layout()
    out = os.path.join(FIG, "fig_alpha_c.png")
    fig.savefig(out)
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    fig_r3b_moneyplot()
    fig_alpha_c()

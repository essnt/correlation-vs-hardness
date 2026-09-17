"""Statistical analysis toolkit for the correlation-vs-hardness study.

Implements the analysis plan frozen in docs/HYPOTHESES.md v1.0:

- load_runs           : runs DB -> tidy DataFrame (params/metrics flattened)
- Tobit               : type-I right-censored regression by MLE (the frozen
                        primary model for log10 conflicts under budget
                        censoring)
- km_curve            : Kaplan-Meier on log10 conflicts, censored at budget
- rm_anova            : repeated-measures ANOVA (balanced cells required)
- jonckheere_terpstra : ordered-alternative trend test, Monte-Carlo
                        permutation p (tie-robust — censored rows tie at the
                        budget floor)
- wilcoxon_paired     : signed-rank paired test (E3b)
- mediation_imai      : product-of-coefficients causal mediation
                        (Imai, Keele & Tingley 2011) with bootstrap ACME CI
- bh_fdr              : Benjamini-Hochberg

Run as a script: smoke test on the R3b pilot database.
"""
from __future__ import annotations

import json
import sqlite3

import numpy as np
import pandas as pd
from scipy import stats

# --------------------------------------------------------------------------- #
# loading
# --------------------------------------------------------------------------- #


def load_runs(db_path: str) -> pd.DataFrame:
    con = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM runs", con)
    con.close()
    # error/childerror 行无有效冲突口径，不属删失语义——显式排除
    #（当前库中为 0 行，纯防御性；censored 只覆盖 budget/walltimeout）
    df = df[~df["status"].astype(str).str.startswith(("error", "childerror"))]
    df["params"] = df["params"].apply(json.loads)
    df["metrics"] = df["metrics_json"].apply(lambda s: json.loads(s) if s else {})
    pkeys = sorted({k for d in df["params"] for k in d})
    mkeys = sorted({k for d in df["metrics"] for k in d})
    for k in pkeys:
        df[f"p_{k}"] = df["params"].apply(lambda d, k=k: d.get(k))
    for k in mkeys:
        df[f"m_{k}"] = df["metrics"].apply(lambda d, k=k: d.get(k))
    df["logc"] = np.log10(df["conflicts"].astype(float) + 1.0)
    df.loc[df["status"] == "walltimeout", "logc"] = np.nan  # conflicts unknown
    df["censored"] = df["status"].isin(["budget", "walltimeout"]).astype(int)
    df["resolved"] = df["status"].isin(["sat", "unsat"]).astype(int)
    return df


# --------------------------------------------------------------------------- #
# Tobit (type I, right-censored) via MLE
# --------------------------------------------------------------------------- #


def tobit_fit(y, X, censored) -> dict:
    """y observed (censored rows carry the censoring value), X design with
    intercept column, censored boolean mask.  Returns beta, sigma, loglik,
    per-coefficient Wald p-values."""
    from statsmodels.base.model import GenericLikelihoodModel

    y = np.asarray(y, float)
    X = np.asarray(X, float)
    cens = np.asarray(censored, dtype=bool)

    class _Tobit(GenericLikelihoodModel):
        def __init__(self, *args, **kw):
            super().__init__(*args, **kw)
            self.cens = cens

        def loglike(self, params):
            beta = params[:-1]
            sigma = float(np.exp(params[-1]))
            xb = np.asarray(self.exog, float) @ beta
            ll = np.zeros(len(y))
            unc = ~self.cens
            if unc.any():
                ll[unc] = stats.norm.logpdf(y[unc] - xb[unc], scale=sigma)
            if self.cens.any():
                ll[self.cens] = stats.norm.logsf(
                    (y[self.cens] - xb[self.cens]) / sigma)
            return float(ll.sum())

    model = _Tobit(y, X)
    start = np.r_[np.linalg.lstsq(X[~cens], y[~cens], rcond=None)[0], 0.0]
    res = model.fit(start_params=start, method="nm", maxiter=5000, disp=0)
    beta = np.asarray(res.params[:-1])
    return {"beta": beta, "sigma": float(np.exp(res.params[-1])),
            "loglik": float(res.llf), "pvals": list(res.pvalues[:-1])}


# --------------------------------------------------------------------------- #
# Kaplan-Meier on log10 conflicts (budget censoring)
# --------------------------------------------------------------------------- #


def km_curve(durations, censored) -> dict:
    from lifelines import KaplanMeierFitter
    kmf = KaplanMeierFitter()
    # "event" = resolved within budget; censored = hit the budget ceiling
    kmf.fit(durations, event_observed=~np.asarray(censored, dtype=bool))
    return {"survival_function": kmf.survival_function_,
            "median": kmf.median_survival_time_}


# --------------------------------------------------------------------------- #
# repeated-measures ANOVA
# --------------------------------------------------------------------------- #


def rm_anova(df: pd.DataFrame, depvar: str, subject: str, within: str) -> dict:
    from statsmodels.stats.anova import AnovaRM
    res = AnovaRM(df, depvar=depvar, subject=subject, within=[within]).fit()
    table = res.anova_table
    return {"F": float(table["F Value"].iloc[0]),
            "p": float(table["Pr > F"].iloc[0]),
            "num_df": int(table["Num DF"].iloc[0]),
            "den_df": int(table["Den DF"].iloc[0])}


# --------------------------------------------------------------------------- #
# Jonckheere-Terpstra trend test (Monte Carlo permutation, tie-robust)
# --------------------------------------------------------------------------- #


def _jt_stat(groups: list[np.ndarray]) -> float:
    stat = 0.0
    for i in range(len(groups) - 1):
        for j in range(i + 1, len(groups)):
            x = np.sort(groups[i])
            y = groups[j]
            idx = np.searchsorted(x, y, side="left")      # y > x pairs
            stat += float(idx.sum())
            stat += 0.5 * float(np.sum(np.isin(y, x)))    # ties
    return stat


def jonckheere_terpstra(groups: list[np.ndarray], n_perm: int = 10_000,
                        seed: int = 42) -> dict:
    """H0: no location trend across ordered groups.  Groups must be given in
    increasing treatment order.  Monte Carlo permutation p-value.

    Tie handling: tied observations receive the standard 0.5 credit in
    `_jt_stat` (this data ties heavily at the budget cap from censoring);
    the permutation p-value counts permutations with statistic >= the
    observed one (inclusive) and uses the add-one estimator
    (extreme + 1) / (n_perm + 1)."""
    pooled = np.concatenate(groups)
    sizes = [len(g) for g in groups]
    observed = _jt_stat(groups)
    rng = np.random.default_rng(seed)
    extreme = 0
    for _ in range(n_perm):
        perm = rng.permutation(pooled)
        split = np.split(perm, np.cumsum(sizes)[:-1])
        if _jt_stat(split) >= observed:
            extreme += 1
    return {"JT": observed, "p": (extreme + 1) / (n_perm + 1), "n_perm": n_perm}


# --------------------------------------------------------------------------- #
# paired test (E3b)
# --------------------------------------------------------------------------- #


def wilcoxon_paired(a, b) -> dict:
    res = stats.wilcoxon(a, b)
    return {"statistic": float(res.statistic), "p": float(res.pvalue),
            "median_diff": float(np.median(np.asarray(a) - np.asarray(b)))}


# --------------------------------------------------------------------------- #
# causal mediation (Imai, Keele & Tingley 2011), linear-linear, bootstrap
# --------------------------------------------------------------------------- #


def mediation_imai(treatment, mediator, outcome, n_boot: int = 2000,
                   seed: int = 42) -> dict:
    """ACME = a*b (no treatment-mediator interaction).  Bootstrap percentile
    CI; ADE = direct effect.  OLS throughout — for censored outcomes run this
    on the uncensored subset and cross-check with the floor-imputed version
    (frozen robustness requirement)."""

    def _ols(y, X):
        return np.linalg.lstsq(X, y, rcond=None)[0]

    def _design(t):
        return np.column_stack([np.ones_like(t, dtype=float), t])

    treatment = np.asarray(treatment, float)
    mediator = np.asarray(mediator, float)
    outcome = np.asarray(outcome, float)

    a = float(_ols(mediator, _design(treatment))[1])
    X2 = np.column_stack([np.ones_like(treatment), treatment, mediator])
    b, cp = float(_ols(outcome, X2)[2]), float(_ols(outcome, X2)[1])
    acme = a * b

    rng = np.random.default_rng(seed)
    n = len(treatment)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        t_, m_, y_ = treatment[idx], mediator[idx], outcome[idx]
        a_i = _ols(m_, _design(t_))[1]
        b_i = _ols(y_, np.column_stack([np.ones_like(t_), t_, m_]))[2]
        boots[i] = a_i * b_i
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"a": a, "b": b, "acme": acme, "acme_ci": (float(lo), float(hi)),
            "ade": cp,
            "total_effect": float(np.polyfit(treatment, outcome, 1)[0])}


# --------------------------------------------------------------------------- #
# multiple testing
# --------------------------------------------------------------------------- #


def bh_fdr(pvals) -> np.ndarray:
    from statsmodels.stats.multitest import multipletests
    return multipletests(pvals, method="fdr_bh")[1]


# --------------------------------------------------------------------------- #
# smoke test on the R3b pilot database
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import os
    ROOT = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    db = os.path.join(ROOT, "results", "pilot_m1_r3b.db")
    df = load_runs(db)
    df = df[df["family"] == "geo_random"]
    d02 = df[df["p_delta"] == 0.2]

    print("=== RM-ANOVA: logc ~ r (Delta=+0.2, 20 seeds) ===")
    print(rm_anova(d02, "logc", "seed", "p_r"))

    print("\n=== Jonckheere-Terpstra trend across r (Delta=+0.2) ===")
    groups = [g["logc"].values for _, g in d02.groupby("p_r")]
    print(jonckheere_terpstra(groups, n_perm=5000))

    print("\n=== Mediation: r -> tw_ub -> logc (Delta=+0.2) ===")
    sub = d02.dropna(subset=["m_tw_ub"])
    print(mediation_imai(sub["p_r"].values, sub["m_tw_ub"].values,
                         sub["logc"].values, n_boot=1000))

    print("\n=== Tobit: logc ~ r (Delta=+0.2, budget-censored at floor) ===")
    X = np.column_stack([np.ones(len(d02)), d02["p_r"].values])
    t = tobit_fit(d02["logc"].values, X, d02["censored"].values)
    print(t)

    print("\n=== SMOKE TEST COMPLETE ===")

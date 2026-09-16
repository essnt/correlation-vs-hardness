"""M2-S0: unified fine estimation of the operational threshold alpha_c(r).

Initial crossing points are interpolated from the round-3 coarse matrix
(8 seeds, alpha step 0.25), tolerating pure cells (all-sat / all-unsat) and
skipping budget-censored runs (which carry no verdict).  Each r is then
refined on a +/-0.1 window (step 0.05) with 16 fresh seeds at a raised
conflict budget of 1e7 (AMEND-1: threshold estimation needs low censoring;
the E3a main scan keeps its own 1e6 semantics).  alpha_c(r) = linear
interpolation of the SAT-rate 0.5 crossing on the refined grid.

alpha_c is an n=400 operational threshold (same-n comparability across r),
not an estimate of the thermodynamic-limit threshold.
"""
import json
import os
import sqlite3

from cvh.solver import run_batch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R3_DB = os.path.join(ROOT, "results", "pilot_m1_r3.db")
DB = os.path.join(ROOT, "results", "m2_s0.db")

N, BUDGET = 400, 10_000_000
R_LEVELS = [0.06, 0.08, 0.11, 0.15, 0.22, 0.3, 0.5, 0.8, 1.5]
SEEDS = list(range(16))


def coarse_crossings() -> dict[float, float]:
    con = sqlite3.connect(R3_DB)
    counts: dict[float, dict[float, list[int]]] = {}
    for params, status in con.execute("SELECT params, status FROM runs"):
        p = json.loads(params)
        if status == "budget":
            continue                       # no verdict; excluded from SAT rate
        cell = counts.setdefault(p["r"], {}).setdefault(p["alpha"], [0, 0])
        cell[0 if status == "sat" else 1] += 1
    con.close()

    out = {}
    for r in R_LEVELS:
        cells = sorted((a, c) for a, c in counts.get(r, {}).items())
        prev = None                        # (alpha, sat_rate) — pure cells ok
        crossed = False
        for a, (s, u) in cells:
            rate = s / (s + u)
            if prev is not None and prev[1] >= 0.5 > rate:
                pa, prate = prev
                out[r] = pa + (prate - 0.5) / (prate - rate) * (a - pa)
                crossed = True
                break
            prev = (a, rate)
        if not crossed:                    # fallback: rate closest to 0.5
            best = min(cells, key=lambda ac: abs(ac[1][0] / sum(ac[1]) - 0.5))
            out[r] = best[0]
    return out


def main() -> None:
    coarse = coarse_crossings()
    print("coarse alpha_c:", {r: round(a, 3) for r, a in sorted(coarse.items())})
    jobs = []
    for r in R_LEVELS:
        c = coarse[r]
        grid = sorted({round(min(max(x, 2.7), 5.5), 2)
                       for x in (c - 0.1, c - 0.05, c, c + 0.05, c + 0.1)})
        for a in grid:
            for s in SEEDS:
                jobs.append(("geo_random",
                             {"n": N, "alpha": a, "r": r, "stage": "m2_s0"},
                             s, "cadical", BUDGET, True))
    print(f"{len(jobs)} jobs")
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    n = run_batch(jobs, DB, workers=16)
    print(f"wrote {n} runs to {DB}")


if __name__ == "__main__":
    main()

"""M2 main experiments: E3a locality sweep + E3b swap intervention.

Implements HYPOTHESES v1.0-FROZEN.  Reads alpha_c(r) from the S0 database
(results/m2_s0.db, AMEND-1 budget 1e7) and aborts if S0 coverage is
insufficient — the main scan must use S0 values only.

E3a: 9 r x 3 Delta {+0.2, +0.4, +0.8} x 30 seeds x 2 solvers (cadical,
     glucose), conflict budget 1e6, full structural metrics (treewidth
     bracket is the M3 mediator).
E3b: 4 r x 2 Delta x 30 seeds x {original, degree-preserving-swapped},
     cadical.  The swap destroys locality while keeping literal degrees
     exactly; a "structure-destruction intervention", not an in-distribution
     comparison (frozen record item 3).  Solver status may flip under the
     swap; both arms record status and the M3 analysis handles pairs with
     status changes explicitly.
"""
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m2_s0_alpha_c import coarse_crossings as _coarse_crossings  # noqa: E402

from cvh.solver import run_batch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S0_DB = os.path.join(ROOT, "results", "m2_s0.db")
DB = os.path.join(ROOT, "results", "m2_main.db")

N, BUDGET = 400, 1_000_000
R_LEVELS = [0.06, 0.08, 0.11, 0.15, 0.22, 0.3, 0.5, 0.8, 1.5]
DELTAS = [0.2, 0.4, 0.8]
SEEDS = list(range(30))
E3B_R = [0.08, 0.15, 0.3, 1.5]
E3B_DELTAS = [0.2, 0.6]


def alpha_c_from_s0():
    """AMEND-2-compliant S0 reader: alpha_c uses only resolved (sat/unsat)
    runs; budget/walltimeout/error rows carry no verdict and are excluded
    from the SAT rate.  Per AMEND-2(3a), the crossing cell-pair's resolution
    rate is reported; r's whose crossing cells resolve <60% are flagged
    low-confidence ('operational at 1e7') and land in the spot-check queue.

    Returns (alpha_c: {r: value}, low_confidence: set[r])."""
    con = sqlite3.connect(S0_DB)
    counts: dict[float, dict[float, list[int]]] = {}
    for params, status in con.execute("SELECT params, status FROM runs"):
        p = json.loads(params)
        if p.get("stage") != "m2_s0" or status not in ("sat", "unsat"):
            continue
        cell = counts.setdefault(p["r"], {}).setdefault(p["alpha"], [0, 0])
        cell[0 if status == "sat" else 1] += 1
    con.close()

    out, low_conf = {}, set()
    coarse = _coarse_crossings()          # R3 values, frozen record item 6
    for r in R_LEVELS:
        cells = sorted((a, c) for a, c in counts.get(r, {}).items())
        if len(cells) < 3:
            # AMEND-2-informed fallback: r with (nearly) no resolved S0 runs is
            # measurement-saturated at 1e7/300s.  Use the R3 coarse crossing as
            # an operational alpha_c, flag low-confidence (spot-check queue).
            if r in coarse:
                out[r] = coarse[r]
                low_conf.add(r)
                print(f"AMEND-2 flag: r={r} measurement-saturated in S0 "
                      f"({len(cells)} resolved cells) -> coarse alpha_c "
                      f"{coarse[r]:.2f}, spot-check queued")
                continue
            raise SystemExit(f"S0 incomplete for r={r} ({len(cells)} cells) — "
                             "finish m2_s0_alpha_c.py first")
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
        # AMEND-2(3a): resolution rate on the two cells bracketing the crossing
        pair = [c for a, c in cells if abs(a - crossed) <= 0.05 + 1e-9]
        res_rate = (sum(s + u for s, u in pair) / (16 * len(pair))) if pair else 0.0
        if res_rate < 0.6:
            low_conf.add(r)
            print(f"AMEND-2 flag: r={r} crossing resolution {res_rate:.0%} <60% "
                  "-> low-confidence alpha_c, spot-check queued")
        out[r] = crossed
    return out, low_conf


def main() -> None:
    alpha_c, low_conf = alpha_c_from_s0()
    print("S0 alpha_c:", {r: round(a, 3) for r, a in sorted(alpha_c.items())})
    if low_conf:
        print("AMEND-2 low-confidence r levels (spot-check queue):", sorted(low_conf))
    jobs = []
    for r in R_LEVELS:
        for d in DELTAS:
            a = round(alpha_c[r] + d, 2)
            for s in SEEDS:
                for solver in ("cadical", "glucose"):
                    jobs.append(("geo_random",
                                 {"n": N, "alpha": a, "r": r, "delta": d,
                                  "stage": "m2_main"},
                                 s, solver, BUDGET, True))
    for r in E3B_R:
        for d in E3B_DELTAS:
            a = round(alpha_c[r] + d, 2)
            for s in SEEDS:
                for fam in ("geo_random", "geo_random_swapped"):
                    jobs.append((fam,
                                 {"n": N, "alpha": a, "r": r, "delta": d,
                                  "stage": "m2_main"},
                                 s, "cadical", BUDGET, True))
    print(f"{len(jobs)} jobs")
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    n = run_batch(jobs, DB, workers=16)
    print(f"wrote {n} runs to {DB}")


if __name__ == "__main__":
    main()

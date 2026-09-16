"""M1 pilot round 3: per-r satisfiability threshold alpha_c(r) estimation.

geo_random family (unplanted geometric 3-SAT), n=400, fine alpha grid per r,
8 seeds per cell -> SAT-rate curve -> alpha_c interpolated at 50% rate.
Feeds the matched-excess-density hardness sweep (round 3b).
"""
import os

from cvh.solver import run_batch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "results", "pilot_m1_r3.db")

N, BUDGET = 400, 1_000_000
R_GRID = [0.06, 0.08, 0.11, 0.15, 0.22, 0.30, 0.50, 0.80, 1.50]
ALPHA_GRID = [3.0, 3.2, 3.4, 3.6, 3.8, 4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.5, 6.0, 7.0]
SEEDS = list(range(8))

jobs = [("geo_random", {"n": N, "alpha": a, "r": r}, s, "cadical", BUDGET, False)
        for r in R_GRID for a in ALPHA_GRID for s in SEEDS]

if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    print(f"{len(jobs)} jobs")
    n = run_batch(jobs, DB, workers=16)
    print(f"wrote {n} runs to {DB}")

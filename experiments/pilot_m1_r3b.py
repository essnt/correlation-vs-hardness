"""M1 pilot round 3b: matched-excess-density hardness vs locality (H2 preview).

At each r, alpha is set relative to that r's own threshold alpha_c(r)
(estimated in round 3), removing the distance-to-threshold confound.
Delta grid: SAT side (-0.2) and UNSAT side (+0.2, +0.6).
Full structural metrics recorded (treewidth bracket = mediator for M3).
"""
import os

from cvh.solver import run_batch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "results", "pilot_m1_r3b.db")

N, BUDGET = 400, 1_000_000
ALPHA_C = {0.06: 3.00, 0.08: 3.25, 0.15: 4.15, 0.30: 4.15, 1.50: 4.20}
DELTAS = [-0.2, +0.2, +0.6]
SEEDS = list(range(20))

jobs = []
for r, ac in ALPHA_C.items():
    for d in DELTAS:
        a = round(ac + d, 2)
        for s in SEEDS:
            jobs.append(("geo_random", {"n": N, "alpha": a, "r": r, "delta": d},
                         s, "cadical", BUDGET, True))

if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    print(f"{len(jobs)} jobs")
    n = run_batch(jobs, DB, workers=16)
    print(f"wrote {n} runs to {DB}")

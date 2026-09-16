"""M2 E1+E2: parallel-safe batch that does NOT depend on S0.

Runs alongside the S0 pool with a small worker count (4) — total load stays
at ~20 cores on this machine.

E1 (treewidth ladder): tw_controlled family, k in {3,5,8,12,16,20},
    n in {300,600}, planted arm (easiness robustness) + unplanted arm
    (primary difficulty-vs-treewidth curve), 20 seeds, cadical, budget 1e6,
    full metrics.
E2 (random reference / anchor): uniform random 3-SAT across 12 alpha levels
    x 30 seeds — this is the independent random curve against which the
    r=1.5 anchor (frozen HYPOTHESES item, R3b follow-up) is compared.
"""
import os

from cvh.solver import run_batch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "results", "m2_e1e2.db")

BUDGET = 1_000_000
K_LEVELS = [3, 5, 8, 12, 16, 20]
N_TW = [300, 600]
SEEDS_TW = list(range(20))
ALPHA_GRID = [3.0, 3.4, 3.8, 4.0, 4.1, 4.2, 4.26, 4.4, 4.6, 4.8, 5.2, 5.6]
SEEDS_E2 = list(range(30))

jobs = []
for planted in (False, True):
    for k in K_LEVELS:
        for n in N_TW:
            for s in SEEDS_TW:
                jobs.append(("tw_controlled",
                             {"n": n, "alpha": 4.0, "k": k, "planted": planted},
                             s, "cadical", BUDGET, True))
for a in ALPHA_GRID:
    for s in SEEDS_E2:
        jobs.append(("random3sat", {"n": 400, "alpha": a}, s,
                     "cadical", BUDGET, True))

if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    print(f"{len(jobs)} jobs")
    n = run_batch(jobs, DB, workers=4)
    print(f"wrote {n} runs to {DB}")

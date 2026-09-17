"""M1 pilot: first controlled E3a sweep + E3b paired check + calibration.

Outputs (results/pilot_m1.db):
  - conflicts-vs-r curve at n=400, alpha=4.3 (the H2 pilot signal)
  - sigma-redundancy histograms per r  (covariate soundness)
  - tw bracket soundness + lb/ub ordering consistency (Kendall tau)
  - E3b paired: original vs degree-preserving-swapped at matched r
  - runtime span calibration for the >=3-orders-of-magnitude rule
"""
import json
import sys
from pathlib import Path

from cvh.solver import run_batch

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "results" / "pilot_m1.db"
if not DB.resolve().is_relative_to(ROOT):  # V2 样式：路径包含性校验（行为不变）
    raise ValueError("DB path must stay inside the project root")

N, ALPHA, BUDGET = 400, 4.3, 15.0  # BUDGET = 冲突预算（run_batch 第 5 参），非墙钟
R_GRID = [0.04, 0.06, 0.08, 0.11, 0.15, 0.22, 0.30, 0.50, 0.80, 1.50]
SEEDS = list(range(10))

jobs = []
for r in R_GRID:
    for s in SEEDS:
        jobs.append(("locality_kernel", {"n": N, "alpha": ALPHA, "r": r},
                     s, "cadical", BUDGET, True))
# E3b paired arms at two r values
for r in [0.08, 0.30]:
    for s in SEEDS:
        jobs.append(("locality_swapped", {"n": N, "alpha": ALPHA, "r": r},
                     s, "cadical", BUDGET, True))
# tiny-timeout probe of the censoring path (one job)
jobs.append(("random3sat", {"n": 150, "alpha": 6.0}, 0, "cadical", 0.001, False))

if __name__ == "__main__":
    DB.parent.mkdir(parents=True, exist_ok=True)
    n = run_batch(jobs, DB, workers=int(sys.argv[1]) if len(sys.argv) > 1 else None)
    print(f"wrote {n} runs to {DB}")

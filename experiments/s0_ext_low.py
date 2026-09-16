#!/usr/bin/env python3
"""S0 补充：r=0.06 网格下探（S0 精测发现阈值触及网格下限 2.9，SAT 率在 2.9 处
仅 ~0.2 ⇒ 真实 α_c(0.06) < 2.9）。加测 α ∈ [2.5, 2.8] 步长 0.05 × 16 seeds，
预算对齐 S0（10⁷）。幂等：run_batch resume 自动跳过已完成格。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from cvh.solver import run_batch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "results", "m2_s0.db")


def main():
    jobs = []
    for a in (2.5, 2.55, 2.6, 2.65, 2.7, 2.75, 2.8):
        for s in range(16):
            jobs.append(("geo_random",
                         {"n": 400, "alpha": a, "r": 0.06, "stage": "m2_s0"},
                         s, "cadical", 10_000_000, True))
    print(f"{len(jobs)} jobs")
    n = run_batch(jobs, DB, workers=16)
    print(f"wrote {n}")


if __name__ == "__main__":
    main()

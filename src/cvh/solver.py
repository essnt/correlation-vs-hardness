"""Solver harness: CDCL via python-sat with conflict-budget truncation.

Primary hardness metric is log10(conflicts) with administrative censoring at
a fixed conflict budget B: finishers report exact conflicts, budget-exhausted
runs are censored at B.  The budget is checked by the solver at every
conflict, so there is no hang risk (a thread-based wall-clock interrupt was
tried first and abandoned: CaDiCaL ignores interrupt() deep in search and the
caller then deadlocks on accum_stats — see docs/PILOT_FINDINGS.md).
"""
from __future__ import annotations

import json
import os

# BLAS thread cap BEFORE numpy enters the process: with 16-20 worker
# processes, numpy's default multi-threaded BLAS oversubscribes the cores
# (each worker spawned ~20 threads; observed 392% CPU per worker and a
# 4x slowdown of every other pool on the machine).
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sqlite3
import time
from typing import Any

from pysat.solvers import Cadical153, Glucose4

SOLVERS = {"cadical": Cadical153, "glucose": Glucose4}

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    family TEXT NOT NULL, params TEXT NOT NULL, seed INTEGER NOT NULL,
    inst_id TEXT NOT NULL, n_vars INTEGER, n_clauses INTEGER,
    metrics_json TEXT, swap_rejection_rate REAL,
    solver TEXT, status TEXT, conflicts INTEGER, decisions INTEGER,
    propagations INTEGER, wall_s REAL, conflict_budget INTEGER,
    UNIQUE(family, params, seed, solver)
);
"""


def _solve_child(clauses, solver_name, budget, q):
    """Runs in an isolated child process.  Solves and pushes the full result
    through a queue; if the parent times out first the child is terminated
    and its partial state is simply discarded (no shared-state deadlock —
    the lesson from the R3 thread+interrupt incident)."""
    S = SOLVERS[solver_name]
    s = S(bootstrap_with=clauses)
    if budget:
        s.conf_budget(budget)
    t0 = time.perf_counter()
    sat = s.solve_limited()
    wall = time.perf_counter() - t0
    st = s.accum_stats()
    q.put(("ok", sat, st.get("conflicts"), st.get("decisions"),
           st.get("propagations"), wall))


def solve_one(clauses: list[list[int]], n_vars: int, solver: str = "cadical",
              conflict_budget: int = 1_000_000,
              wall_timeout: float = 300.0) -> dict[str, Any]:
    """Solve with a conflict budget AND a wall-clock child-process guard.

    The conflict budget (checked per conflict) is the primary censoring
    mechanism.  The wall guard (300s, per AMEND-2) exists for pathological
    runs where conflicts are rare but propagation bursts are enormous — those
    would otherwise run unboundedly; they return status='walltimeout' with
    conflicts=None and are excluded from conflict-based analyses."""
    import multiprocessing as mp

    ctx = mp.get_context("spawn")
    q = ctx.SimpleQueue()
    p = ctx.Process(target=_solve_child,
                    args=(clauses, solver, conflict_budget, q))
    p.start()
    p.join(wall_timeout)
    if p.is_alive():
        p.terminate()
        p.join(5)
        if p.is_alive():
            p.kill()
            p.join()  # 收割干净，不留僵尸子进程
        return {"solver": solver, "status": "walltimeout", "conflicts": None,
                "decisions": None, "propagations": None,
                "wall_s": wall_timeout, "conflict_budget": conflict_budget}
    if p.exitcode != 0:
        # child was killed / crashed (e.g. OOM) — never q.get() on a dead
        # child that may not have put anything: that deadlocks forever
        return {"solver": solver, "status": f"childerror({p.exitcode})",
                "conflicts": None, "decisions": None, "propagations": None,
                "wall_s": None, "conflict_budget": conflict_budget}
    # exitcode 0 ⇒ the child put its result before exiting: plain get() is safe
    kind, sat, conf, dec, prop, wall = q.get()
    status = "sat" if sat is True else ("unsat" if sat is False else "budget")
    return {"solver": solver, "status": status, "conflicts": conf,
            "decisions": dec, "propagations": prop, "wall_s": wall,
            "conflict_budget": conflict_budget}


def _make_instance(family: str, params: dict, seed: int):
    from .generators import (random_3sat, planted_hidden, locality_kernel,
                             degree_preserving_randomize, tw_controlled)
    if family == "random3sat":
        return random_3sat(params["n"], params["alpha"], seed)
    if family == "geo_random":
        return locality_kernel(params["n"], params["alpha"], params["r"], seed,
                               planted=False)
    if family == "locality_kernel":
        return locality_kernel(params["n"], params["alpha"], params["r"], seed)
    if family == "tw_controlled":
        return tw_controlled(params["n"], params["alpha"], params["k"], seed,
                             planted=params.get("planted", True))
    if family == "planted_hidden":
        return planted_hidden(params["n"], params["alpha"], seed,
                              q_hidden=params.get("q_hidden", 0.5))
    if family == "geo_random_swapped":
        base = locality_kernel(params["n"], params["alpha"], params["r"], seed,
                               planted=False)
        inst, swap_stats = degree_preserving_randomize(base, seed)
        inst._swap_stats = swap_stats
        return inst
    if family == "locality_swapped":
        base = locality_kernel(params["n"], params["alpha"], params["r"], seed)
        inst, swap_stats = degree_preserving_randomize(base, seed)
        inst._swap_stats = swap_stats
        return inst
    raise ValueError(family)


def _worker(args):
    (family, params, seed, solver, conflict_budget, measure_metrics, *rest) = args
    wall_timeout = rest[0] if rest else 300.0   # AMEND-2 default; spot-check uses 480
    try:
        inst = _make_instance(family, params, seed)
        row = {"family": family, "params": json.dumps(params, sort_keys=True),
               "seed": seed, "inst_id": inst.inst_id,
               "n_vars": inst.n_vars, "n_clauses": len(inst.clauses),
               "metrics_json": None, "swap_rejection_rate": None}
        if measure_metrics:
            from .metrics import all_metrics
            row["metrics_json"] = json.dumps(all_metrics(inst), sort_keys=True)
        if hasattr(inst, "_swap_stats"):
            row["swap_rejection_rate"] = inst._swap_stats["rejection_rate"]
        res = solve_one(inst.clauses, inst.n_vars, solver, conflict_budget,
                        wall_timeout=wall_timeout)
        row.update({k: v for k, v in res.items()})
        return row
    except Exception as e:                      # one bad job must not kill the pool
        return {"family": family, "params": json.dumps(params, sort_keys=True),
                "seed": seed, "inst_id": "ERROR", "n_vars": None,
                "n_clauses": None, "metrics_json": None,
                "swap_rejection_rate": None, "solver": solver,
                "status": f"error: {e}", "conflicts": None, "decisions": None,
                "propagations": None, "wall_s": None,
                "conflict_budget": conflict_budget}


def run_batch(jobs: list[tuple], db_path: str, table: str = "runs",
              workers: int | None = None, resume: bool = True) -> int:
    """jobs: (family, params_dict, seed, solver, conflict_budget,
    measure_metrics[, wall_timeout]).  The optional 7th element overrides the
    default wall timeout for that job (s0_spotcheck uses it).

    Dispatch is THREAD-based: each job's solve runs in its own spawned child
    process (see solve_one), and pool workers are daemon processes which are
    not allowed to spawn children — threads are.

    resume=True (default) skips jobs whose row already carries a final verdict
    (sat/unsat/budget/walltimeout) for the same UNIQUE key
    (family, params, seed, solver).  error/childerror rows are recomputed.
    This makes every experiment script idempotent-resumable: restarting after
    a crash recomputes only what is missing, never the whole grid.

    Caveat: conflict_budget is not part of the UNIQUE key — experiments that
    change the budget must tag it in params (S0 uses stage=m2_s0, the main
    scan stage=m2_main, so their rows never collide)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    FINAL = ("sat", "unsat", "budget", "walltimeout")
    done = set()
    if resume:
        for fam, params, seed, solver, status in con.execute(
                f"SELECT family, params, seed, solver, status FROM {table}"):
            if status in FINAL:
                done.add((fam, params, seed, solver))
    todo = [j for j in jobs
            if (j[0], json.dumps(j[1], sort_keys=True), j[2], j[3]) not in done]
    skipped = len(jobs) - len(todo)
    if skipped:
        print(f"resume: {skipped} of {len(jobs)} jobs already final, running {len(todo)}")
    written = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_worker, job) for job in todo]
        for fut in as_completed(futs):
            row = fut.result()
            cols = list(row.keys())
            con.execute(
                f"INSERT OR REPLACE INTO {table} ({', '.join(cols)}) "
                f"VALUES ({', '.join('?' for _ in cols)})",
                [row[c] for c in cols])
            written += 1
            con.commit()          # per-row: a kill loses at most the in-flight row
    con.commit()
    con.close()
    return written

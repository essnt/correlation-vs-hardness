"""E6 (exploratory): LLM branching-ordering experiment — HYPOTHESES v1.0 H3.

Question: does the quality of an LLM's branching decisions on SAT instances
depend on the instances' locality radius r?  Conceptually, strong locality
(small r) means local decisions suffice — a P-time LLM with a local view
should branch well; weak locality (large r) needs global coordination.

Setup (planted geo_random, n=50, guaranteed-SAT, planted sigma = oracle):
  policies: JW (Jeroslow-Wang baseline), random, llm (qwen3:8b via ollama,
  used for the first MAX_LLM_LEVELS decision levels then JW fallback).
  Each policy runs a full DPLL with node cap; record decisions-to-solve,
  sigma-match rate per decision, and Kendall tau between the LLM ranking
  and the JW ranking at each LLM-consulted level.

Modes:
  --dry-run : no LLM calls (JW/random arms only) — validates the machinery
  --llm     : include the LLM arm (default; calls ollama at localhost:11434)

Output -> results/e6.json
"""
from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

from scipy import stats as sps

from cvh.generators import locality_kernel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "e6.json")

N, ALPHA = 50, 4.0
R_LEVELS = [0.08, 0.2, 0.5]
ALPHA_ARMS = [4.0, 7.0]   # 4.0: planted-easy (decisions ~ n, no discrimination);
                          # 7.0: beyond planting threshold (decisions >> n)
SEEDS = list(range(10))
MAX_LLM_LEVELS = 12
NODE_CAP = 20000
OLLAMA = "http://localhost:11434/api/chat"
MODEL = "qwen3:8b"


def ollama_chat(prompt: str) -> str:
    u = urllib.parse.urlparse(OLLAMA)
    assert u.scheme == "http" and u.hostname in ("localhost", "127.0.0.1"), \
        "OLLAMA endpoint must be local"
    body = json.dumps({"model": MODEL, "stream": False, "think": False,
                       "options": {"temperature": 0, "num_predict": 256},
                       "messages": [{"role": "user", "content": prompt}]})
    req = urllib.request.Request(OLLAMA, data=body.encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["message"]["content"]


# ----------------------------------------------------------------- DPLL ---- #

class State:
    def __init__(self, clauses):
        self.clauses = [list(c) for c in clauses]

    def literal_value(self, l, assign):
        if abs(l) in assign:
            return (l > 0) == assign[abs(l)]
        return None

    def clause_status(self, c, assign):
        vals = [self.literal_value(l, assign) for l in c]
        if any(v is True for v in vals):
            return "sat"
        if all(v is False for v in vals):
            return "conflict"
        unassigned = [l for l, v in zip(c, vals) if v is None]
        if len(unassigned) == 1:
            return "unit"
        return "open"

    def propagate(self, assign):
        """Unit propagation to fixpoint. Returns False on conflict."""
        changed = True
        while changed:
            changed = False
            for c in self.clauses:
                st = self.clause_status(c, assign)
                if st == "conflict":
                    return False
                if st == "unit":
                    l = [l for l in c if self.literal_value(l, assign) is None][0]
                    assign[abs(l)] = l > 0
                    changed = True
        return True


def jw_candidates(state: State, assign: dict, k: int = 8):
    """Jeroslow-Wang two-sided weights over open variables."""
    weight = Counter()
    for c in state.clauses:
        st = [state.literal_value(l, assign) for l in c]
        if any(v is True for v in st):
            continue
        open_lits = [l for l, v in zip(c, st) if v is None]
        for l in open_lits:
            weight[abs(l)] += 2.0 ** (-len(open_lits))
    ranked = sorted(weight, key=weight.get, reverse=True)[:k]
    return ranked


def dpll_solve(clauses, n_vars, policy: str, seed: int, llm_fn=None,
               sigma=None):
    """Greedy DPLL with chronological backtracking and a node cap.
    Returns dict(decisions, solved, sigma_match)."""
    state = State(clauses)
    rng = random.Random(seed)
    stats = {"decisions": 0, "sigma_match": 0, "sigma_total": 0}
    cache: dict[tuple, list[int]] = {}

    def search(assign, level) -> bool:
        if not state.propagate(assign):
            return False
        open_vars = [v for v in range(1, n_vars + 1) if v not in assign]
        if not open_vars:
            return True
        if stats["decisions"] >= NODE_CAP:
            return False
        stats["decisions"] += 1

        cands = jw_candidates(state, assign)
        if policy == "random" or (not cands):
            var = rng.choice(open_vars)
            val = rng.random() < 0.5
        elif policy == "llm" and level < MAX_LLM_LEVELS and llm_fn:
            key = (tuple(sorted(assign.items())), tuple(cands))
            if key not in cache:
                cache[key] = llm_fn(state, assign, cands)
            ranking = cache[key]
            var = ranking[0] if ranking else cands[0]
            val = jw_polarity(state, assign, var, rng)  # variable ordering is the treatment
        else:  # JW
            var = cands[0]
            val = jw_polarity(state, assign, var, rng)

        if sigma is not None:
            stats["sigma_total"] += 1
            stats["sigma_match"] += int(val == sigma[var - 1])

        for value in (val, not val):  # try chosen polarity first, backtrack to other
            assign[var] = value
            if search(assign, level + 1):
                return True
            del assign[var]
        return False

    solved = search({}, 0)
    return {"decisions": stats["decisions"], "solved": solved,
            "sigma_match": stats["sigma_match"] / max(stats["sigma_total"], 1)}


def jw_polarity(state: State, assign: dict, var: int, rng) -> bool:
    pos = neg = 0.0
    for c in state.clauses:
        st = [state.literal_value(l, assign) for l in c]
        if any(v is True for v in st) or var not in [abs(l) for l, v in zip(c, st) if v is None]:
            continue
        open_lits = [l for l, v in zip(c, st) if v is None]
        for l in open_lits:
            if abs(l) == var:
                w = 2.0 ** (-len(open_lits))
                if l > 0:
                    pos += w
                else:
                    neg += w
    return pos >= neg


# ----------------------------------------------------------------- LLM ----- #

def llm_rank(state: State, assign: dict, cands: list[int]) -> list[int]:
    """Ask qwen3:8b to rank candidate branching variables; returns a
    permutation of cands (best first), degraded to identity on any failure."""
    open_clauses = [c for c in state.clauses
                    if not any(state.literal_value(l, assign) is True for l in c)]
    snippet = "; ".join(
        " ".join(f"{l}" for l in c) for c in open_clauses[:40])
    prompt = (
        "We are deciding which variable to branch on next in a SAT problem.\n"
        f"Unsatisfied/open clauses (negative sign = NOT x): {snippet}\n"
        f"Candidate variables (ranked by a standard heuristic): {cands}\n"
        "Rank these candidate variables so that branching on the first one "
        "is most likely to let unit propagation decide many clauses quickly.\n"
        'Reply ONLY with a JSON array of the variable indices, best first, '
        'e.g. [3, 17, 5].')
    try:
        content = ollama_chat(prompt)
        match = __import__("re").search(r"\[[\d\s,]+\]", content)
        ranking = json.loads(match.group(0))
        ranking = [v for v in ranking if v in cands]
        rest = [v for v in cands if v not in ranking]
        return ranking + rest
    except Exception as e:
        print(f"llm_rank failed: {e}")
        return list(cands)


# ----------------------------------------------------------------- main ---- #

def kendall_llm_vs_jw(state, assign, cands, llm_fn, cache):
    key = (tuple(sorted(assign.items())), tuple(cands))
    if key not in cache:
        cache[key] = llm_fn(state, assign, cands)
    ranking = cache[key]
    if len(ranking) < 2:
        return None
    tau, _ = sps.kendalltau(range(len(cands)),
                            [ranking.index(v) for v in cands])
    return tau


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0,
                    help="only run the first N (r, seed) blocks — smoke mode")
    args = ap.parse_args()

    llm_fn = None if args.dry_run else llm_rank
    results = []
    blocks = 0
    for r in R_LEVELS:
        for alpha in ALPHA_ARMS:
            for seed in SEEDS:
                if args.limit and blocks >= args.limit:
                    break
                blocks += 1
                inst = locality_kernel(N, alpha, r, seed=seed, planted=True)
                for policy in (["jw", "random"] if args.dry_run
                               else ["jw", "random", "llm"]):
                    res = dpll_solve(inst.clauses, N, policy, seed=seed,
                                     llm_fn=llm_fn, sigma=inst.sigma)
                    res["alpha"] = alpha
                    results.append({"r": r, "seed": seed, "policy": policy,
                                    "inst_id": inst.inst_id, **res})
                    print(f"r={r} a={alpha} seed={seed} {policy}: {res}",
                          flush=True)

    assert Path(OUT).resolve().is_relative_to(Path(ROOT).resolve())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    Path(OUT).write_text(json.dumps(results, indent=1))
    # summary
    for policy in {x["policy"] for x in results}:
        dec = [x["decisions"] for x in results if x["policy"] == policy and x["solved"]]
        if dec:
            print(f"{policy}: median decisions {statistics.median(dec):.0f} "
                  f"(n={len(dec)})")


if __name__ == "__main__":
    main()

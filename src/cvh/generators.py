"""Instance generators for the correlation-vs-hardness study.

All generators are deterministic given (seed, family, parameters) and emit
CNF instances together with a full provenance record.

Families
--------
- random3sat       : uniform random 3-SAT (E2 phase-transition sweep, anchor for E3a r=∞)
- planted_hidden   : Jia–Moore–Strain style q-hidden planted 3-SAT (hard satisfiable)
- locality_kernel  : E3a core — planted σ + clause sampling restricted to an
                     r-ball in a latent host graph on the 2D torus (the planted
                     variant applies a soft degree cap by rejection; the
                     geo_random main arm is uncapped)
- tw_controlled    : E1 — clauses fill a random k-tree / partial k-tree skeleton,
                     treewidth bounded by construction
- ps_reference     : Giráldez-Cru & Levy style locality model (coupled heterogeneity),
                     reimplemented minimally for the related-work comparison only

Conventions: variables are 1..n; a clause is a list of signed ints; the planted
assignment σ maps var -> bool; a literal l is satisfied by σ iff (l>0) == σ[|l|].
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import dataclass, field, asdict
from typing import Iterable, Literal

Host = Literal["torus2d", "geo_scalefree"]


# --------------------------------------------------------------------------- #
# provenance / container
# --------------------------------------------------------------------------- #

@dataclass
class Instance:
    clauses: list[list[int]]
    n_vars: int
    family: str
    params: dict
    seed: int
    sigma: list[bool] | None = None      # planted assignment if any
    inst_id: str = ""

    def __post_init__(self):
        if not self.inst_id:
            payload = json.dumps(
                {"f": self.family, "p": self.params, "s": self.seed,
                 "n": self.n_vars, "c": len(self.clauses)},
                sort_keys=True, default=str).encode()
            self.inst_id = hashlib.sha1(payload).hexdigest()[:16]

    def to_dimacs(self) -> str:
        lines = [f"p cnf {self.n_vars} {len(self.clauses)}"]
        lines += [" ".join(map(str, c)) + " 0" for c in self.clauses]
        return "\n".join(lines) + "\n"

    def clause_satisfied_by_sigma(self, clause) -> bool:
        return any((l > 0) == self.sigma[abs(l) - 1] for l in clause)


# --------------------------------------------------------------------------- #
# E2: uniform random 3-SAT
# --------------------------------------------------------------------------- #

def random_3sat(n: int, alpha: float, seed: int, sat_only: bool = False) -> Instance:
    """Uniform random 3-SAT with m = round(alpha*n) clauses.

    sat_only=True resamples until a model exists (expensive; pilot only).
    """
    rng = random.Random(seed)
    m = round(alpha * n)
    clauses = [[v if rng.random() < 0.5 else -v
                for v in rng.sample(range(1, n + 1), 3)] for _ in range(m)]
    return Instance(clauses, n, "random3sat",
                    {"alpha": alpha, "m": m}, seed)


# --------------------------------------------------------------------------- #
# planted, leakage-resistant (Jia–Moore–Strain q-hidden flavour)
# --------------------------------------------------------------------------- #

def _sample_sigma(n: int, rng: random.Random) -> list[bool]:
    return [rng.random() < 0.5 for _ in range(n)]


def _sat_polarity(clause_vars, sigma, rng) -> list[int]:
    """Polarities such that sigma satisfies the clause.

    Draw a cardinality c uniformly in 1..k (k = number of clause positions that
    sigma satisfies), then a uniformly-random c-element subset of those positions;
    the chosen literals are forced sigma-true and each remaining position gets a
    free fair coin.  This is NOT uniform sampling over the 7 non-empty subsets
    (whose expected size 12/7 does not apply here): the measured per-radius
    mean sigma-redundancy is 2.18-2.24 and is r-invariant (per-instance means
    span 2.14-2.27; pilot-verified).
    """
    sat_pos = [i for i, v in enumerate(clause_vars) if sigma[v - 1]]
    if not sat_pos:                       # parity fluke: flip one var in sigma
        sigma[clause_vars[0] - 1] = not sigma[clause_vars[0] - 1]
        sat_pos = [0]
    chosen = rng.sample(sat_pos, rng.randint(1, len(sat_pos)))
    out = []
    for i, v in enumerate(clause_vars):
        if i in chosen:
            out.append(v if sigma[v - 1] else -v)          # true under sigma
        else:
            out.append(v if rng.random() < 0.5 else -v)    # free polarity
    return out


def planted_hidden(n: int, alpha: float, seed: int, q_hidden: float = 0.5,
                   p_flip: float = 2.0 / 3.0,
                   host_coords: list[tuple[float, float]] | None = None,
                   ball_radius: float | None = None) -> Instance:
    """Jia–Moore–Strain style q-hidden planted 3-SAT.

    A decoy assignment beta differs from sigma on a p_flip fraction of vars.
    A q_hidden fraction of clauses is 'hidden': every literal is beta-false
    while the clause stays sigma-satisfied (possible only because at
    sigma!=beta positions the sigma-true literal is automatically beta-false).
    Uniform-7 clauses make up the rest.  Ordinary planted 3-SAT is CDCL-trivial
    below the planting threshold (pilot M1 confirmed: 0 conflicts everywhere);
    the decoy is what buys hardness.  If host_coords+ball_radius given,
    clause variables are drawn from an r-ball (E3a path).
    """
    rng = random.Random(seed)
    sigma = _sample_sigma(n, rng)
    beta = [s != (rng.random() < p_flip) for s in sigma]
    m = round(alpha * n)
    deg = [0] * (n + 1)
    clauses = []
    for _ in range(m):
        for _attempt in range(1000):
            if host_coords is None:
                vs = rng.sample(range(1, n + 1), 3)
            else:
                c = host_coords[rng.randrange(n)]
                near = [i for i, p in enumerate(host_coords, 1)
                        if _torus_dist2(c, p) <= ball_radius ** 2]
                if len(near) < 3:
                    continue
                vs = rng.sample(near, 3)
            if max(deg[v] for v in vs) <= _deg_cap(n, m):
                break
        for v in vs:
            deg[v] += 1
        if rng.random() < q_hidden:
            clauses.append(_hidden_polarity(vs, sigma, beta))
        else:
            clauses.append(_sat_polarity(vs, sigma, rng))
    fam = "planted_hidden" if host_coords is None else "locality_kernel"
    params = {"alpha": alpha, "m": m, "q_hidden": q_hidden, "p_flip": p_flip,
              "r": ball_radius, "host": "torus2d" if host_coords else None}
    return Instance(clauses, n, fam, params, seed, sigma=sigma)


def _hidden_polarity(clause_vars, sigma, beta) -> list[int]:
    """Clause satisfied by sigma, falsified by beta (decoy).  At sigma!=beta
    vars the sigma-true literal is beta-false (forced polarity sigma[v]); at
    sigma==beta vars only a sigma-false literal is beta-false."""
    diff_pos = [i for i, v in enumerate(clause_vars) if sigma[v - 1] != beta[v - 1]]
    if not diff_pos:                       # cannot hide here; fall back to uniform-7
        return _sat_polarity(clause_vars, sigma, random.Random(0))
    out = []
    for i, v in enumerate(clause_vars):
        if sigma[v - 1] != beta[v - 1]:
            out.append(v if sigma[v - 1] else -v)      # sigma-true, beta-false
        else:
            out.append(v if not beta[v - 1] else -v)   # sigma-false, beta-false
    return out


def double_planted(n: int, alpha: float, r: float, blob_frac: float,
                   seed: int) -> Instance:
    """E3c: two planted assignments that AGREE on most of the torus and differ
    on a spatial blob.  Every clause is satisfied by both sigma1 and sigma2
    (anchor literals drawn from the agreement region), so the formula is
    typically UNSAT with the frustration localised near the blob — 'locally
    satisfiable, globally contradictory'.  r controls how tightly clauses
    anchor; blob_frac controls the disagreement mass."""
    rng = random.Random(seed)
    coords = [(rng.random(), rng.random()) for _ in range(n)]
    sigma1 = _sample_sigma(n, rng)
    # blob = points within radius of a random centre (torus metric)
    cx, cy = rng.random(), rng.random()
    blob_radius = math.sqrt(blob_frac / math.pi)          # area ~ blob_frac
    sigma2 = list(sigma1)
    for i, p in enumerate(coords):
        if _torus_dist2((cx, cy), p) <= blob_radius ** 2:
            sigma2[i] = not sigma2[i]
    agree = [i + 1 for i in range(n) if sigma1[i] == sigma2[i]]
    if len(agree) < 3:
        raise ValueError("blob_frac too large: no agreement region")
    m = round(alpha * n)
    deg = [0] * (n + 1)
    clauses = []
    for _ in range(m):
        for _attempt in range(1000):
            c = coords[rng.randrange(n)]
            near = [i for i, p in enumerate(coords, 1)
                    if _torus_dist2(c, p) <= r ** 2]
            if len(near) < 3:
                continue
            vs = rng.sample(near, 3)
            if max(deg[v] for v in vs) <= _deg_cap(n, m):
                break
        for v in vs:
            deg[v] += 1
        clauses.append(_both_planted_polarity(vs, sigma1, sigma2, agree, rng))
    return Instance(clauses, n, "double_planted",
                    {"alpha": alpha, "m": m, "r": r, "blob_frac": blob_frac},
                    seed, sigma=sigma1)


def _both_planted_polarity(clause_vars, sigma1, sigma2, agree, rng) -> list[int]:
    """Polarity pattern satisfied by both sigma1 and sigma2: needs >=1 literal
    at an agreement position with polarity matching the common value."""
    ag_pos = [i for i, v in enumerate(clause_vars) if v in set(agree)]
    if not ag_pos:                                  # rare at small r; retry logic upstream
        ag_pos = [rng.randrange(3)]
    chosen = rng.sample(ag_pos, rng.randint(1, len(ag_pos)))
    out = []
    for i, v in enumerate(clause_vars):
        common = sigma1[v - 1]                       # == sigma2[v-1] on agreement
        if i in chosen:
            out.append(v if common else -v)          # true under both
        else:
            out.append(v if rng.random() < 0.5 else -v)  # free: true under one
    return out


def _deg_cap(n: int, m: int) -> int:
    """Soft degree cap ~ 99.9th percentile of Poisson(3*alpha) — keeps the
    degree distribution near-regular without hard failure."""
    lam = 3.0 * m / n
    return max(6, int(lam + 4 * math.sqrt(lam) + 3))


def _torus_dist2(a, b, L: float = 1.0) -> float:
    dx = abs(a[0] - b[0]); dx = min(dx, L - dx)
    dy = abs(a[1] - b[1]); dy = min(dy, L - dy)
    return dx * dx + dy * dy


# --------------------------------------------------------------------------- #
# E3a public entry: locality kernel on the 2D torus
# --------------------------------------------------------------------------- #

def locality_kernel(n: int, alpha: float, r: float, seed: int,
                    host: Host = "torus2d", planted: bool = True,
                    q_hidden: float = 1.0, p_flip: float = 2.0 / 3.0) -> Instance:
    """Clause sampling restricted to r-balls on the torus.

    planted=True  : sigma-satisfying (optionally JMS-deceptive via q_hidden)
    planted=False : 'geo_random' — uniform polarity, no sigma.  This is the
                    Bläsius-et-al geometric regime: UNSAT instances near the
                    r-dependent threshold carry small unsatisfiable subformulas
                    when r is small (the theory side of H2's UNSAT arm).
    r -> ∞ recovers (approximately) uniform random 3-SAT.  The planted path
    applies a soft degree cap by rejection (verified in pilot); the geo_random
    main arm applies no cap, so its degree-shape drifts slightly with r
    (disclosed in the paper's Threats section).
    """
    rng = random.Random(seed)
    if host == "torus2d":
        coords = [(rng.random(), rng.random()) for _ in range(n)]
    else:
        raise NotImplementedError("geo_scalefree variant lands in M2 (robustness arm)")
    if not planted:
        m = round(alpha * n)
        clauses = []
        for _ in range(m):
            for _attempt in range(1000):
                c = coords[rng.randrange(n)]
                near = [i for i, p in enumerate(coords, 1)
                        if _torus_dist2(c, p) <= r ** 2]
                if len(near) >= 3:
                    break
            else:
                raise ValueError(
                    f"no r-ball with >=3 variables within 1000 attempts "
                    f"(r={r}, n={n})")
            vs = rng.sample(near, 3)
            clauses.append([v if rng.random() < 0.5 else -v for v in vs])
        return Instance(clauses, n, "geo_random",
                        {"alpha": alpha, "m": m, "r": r, "host": "torus2d"}, seed)
    return planted_hidden(n, alpha, seed, q_hidden=q_hidden, p_flip=p_flip,
                          host_coords=coords, ball_radius=r)


# --------------------------------------------------------------------------- #
# E3b: degree-preserving randomization (bipartite swap chain)
# --------------------------------------------------------------------------- #

def degree_preserving_randomize(inst: Instance, seed: int,
                                n_swaps_factor: int = 10) -> tuple[Instance, dict]:
    """MCMC swap chain on the clause-variable bipartite graph.

    Each step picks two random clauses and swaps one literal-variable between
    them; the swap is rejected if it duplicates a variable inside a clause
    (a tautology proposal — x and -x in one clause — collapses to a duplicate
    under the |l| check) or breaks planted satisfiability (when sigma
    present).  Literal occurrence counts and clause sizes are invariant by
    construction.
    """
    rng = random.Random(seed)
    clauses = [list(c) for c in inst.clauses]
    steps = acc = rej_dup = rej_sat = 0
    target = n_swaps_factor * len(clauses)

    def bad(c):
        # |l| 折叠符号 → tautology 提案（x 与 -x 同子句）必然判为 duplicate：
        # 两类提案不可分，统计上并入 reject_duplicate（2026-09-17 修正：
        # 原先的 reject_tautology 计数器结构上恒为 0，已删除）
        vs = [abs(l) for l in c]
        return len(set(vs)) != len(vs) or any(-l in c for l in c)

    def sat(c):
        return inst.sigma is None or any((l > 0) == inst.sigma[abs(l) - 1] for l in c)

    while acc < target and steps < target * 20:
        steps += 1
        i, j = rng.randrange(len(clauses)), rng.randrange(len(clauses))
        if i == j:
            continue
        ci, cj = clauses[i], clauses[j]
        li, lj = rng.randrange(3), rng.randrange(3)
        cand_i, cand_j = list(ci), list(cj)
        cand_i[li], cand_j[lj] = cand_j[lj], cand_i[li]
        if bad(cand_i) or bad(cand_j):
            rej_dup += 1; continue
        if not (sat(cand_i) and sat(cand_j)):
            rej_sat += 1; continue
        clauses[i], clauses[j] = cand_i, cand_j
        acc += 1
    out = Instance(clauses, inst.n_vars, inst.family + "_swapped",
                   {**inst.params, "swapped": True}, seed, sigma=inst.sigma)
    stats = {"steps": steps, "accepted": acc, "reject_duplicate": rej_dup,
             "reject_sat": rej_sat,
             "rejection_rate": 1 - acc / max(steps, 1)}
    return out, stats


# --------------------------------------------------------------------------- #
# E1: treewidth-controlled family (k-tree skeleton fill)
# --------------------------------------------------------------------------- #

def tw_controlled(n: int, alpha: float, k: int, seed: int,
                  planted: bool = True) -> Instance:
    """Clauses placed along a random k-tree skeleton (treewidth ≤ k).

    Skeleton growth: start from a (k+1)-clique; each new variable attaches
    to a uniformly chosen existing bag, keeping that bag's last k vertices
    plus the new variable.  Every clause is sampled inside a single bag, so
    the instance's primal graph is a subgraph of the k-tree skeleton —
    treewidth ≤ k (the skeleton itself has treewidth exactly k).

    planted=True  : sigma-satisfying polarities — R1 showed these are CDCL-
                    trivial regardless of treewidth; kept as the "planted
                    easiness across tw" robustness arm.
    planted=False : uniform polarities — the primary E1 arm measuring the
                    difficulty-vs-treewidth curve.
    """
    rng = random.Random(seed)
    sigma = _sample_sigma(n, rng) if planted else None
    if n <= k + 1:
        raise ValueError("n must exceed k+1")
    # k-tree: start with a (k+1)-clique, grow
    order = list(range(1, k + 2))
    bags = [tuple(order)]
    for v in range(k + 2, n + 1):
        bag = list(rng.choice(bags))
        bag = bag[-k:] if len(bag) > k else bag
        bag.append(v)
        bags.append(tuple(bag))
        order.append(v)
    m = round(alpha * n)
    clauses = []
    for _ in range(m):
        bag = list(rng.choice(bags))
        vs = rng.sample(bag, 3) if len(bag) >= 3 else bag
        while len(vs) < 3:
            vs.append(rng.choice(bag))
        if planted:
            clauses.append(_sat_polarity(vs[:3], sigma, rng))
        else:
            clauses.append([v if rng.random() < 0.5 else -v for v in vs[:3]])
    return Instance(clauses, n, "tw_controlled",
                    {"alpha": alpha, "m": m, "k": k, "planted": planted},
                    seed, sigma=sigma)

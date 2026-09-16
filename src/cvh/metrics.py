"""Structural metrics for CNF instances.

Every metric is a pure function of the clause list (+ n_vars) so results are
reproducible and cacheable.  Treewidth is reported as a bracket [lb, ub].
"""
from __future__ import annotations

import math
from collections import Counter

import networkx as nx
import numpy as np


def primal_graph(inst) -> nx.Graph:
    """Variable-interaction graph: variables are nodes, co-occurrence in a
    clause adds a clique edge."""
    g = nx.Graph()
    g.add_nodes_from(range(1, inst.n_vars + 1))
    for c in inst.clauses:
        vs = [abs(l) for l in c]
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                g.add_edge(vs[i], vs[j])
    return g


def incidence_graph(inst) -> nx.BipartiteGraph | nx.Graph:
    g = nx.Graph()
    var_nodes = range(1, inst.n_vars + 1)
    g.add_nodes_from(var_nodes, bipartite=0)
    for ci, c in enumerate(inst.clauses):
        cn = ("c", ci)
        g.add_node(cn, bipartite=1)
        for l in c:
            g.add_edge(cn, abs(l))
    return g


# --------------------------------------------------------------------------- #
# treewidth bracket
# --------------------------------------------------------------------------- #

def treewidth_bracket(g: nx.Graph, known_ub: int | None = None) -> tuple[int, int, str]:
    """(lower_bound, upper_bound, method).

    Upper bound: min-fill elimination (numpy-accelerated greedy), OR a
    constructor-guaranteed bound when the caller provides one (e.g. the
    k-tree family has treewidth <= k by construction — running min-fill on
    its dense primal graphs costs minutes for zero information).
    Lower bound: degeneracy (valid since every k-tree is k-degenerate),
    NOT the min-degree heuristic width — adding fill edges here would
    silently turn the lb into an inflated ub (bug caught in M1 pilot)."""
    if g.number_of_nodes() == 0:
        return 0, 0, "empty"
    lb = max(nx.core_number(g).values()) if g.number_of_nodes() else 0
    if known_ub is not None:
        return int(lb), int(known_ub), "construction+degeneracy"
    ub, fill_edges = _min_fill_ub(g)
    return int(lb), int(ub), f"minfill(fill={fill_edges})+degeneracy"


def _min_fill_ub(g: nx.Graph) -> tuple[int, int]:
    """Exact min-fill elimination upper bound.

    fill(v) = C(deg,2) - triangles(v); triangles via (A@A)∘A with float32
    BLAS on the compacted alive-submatrix (nodes removed each round)."""
    n = g.number_of_nodes()
    nodes = sorted(g.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    A = nx.to_numpy_array(g, nodelist=nodes, weight=None).astype(np.float32)
    np.fill_diagonal(A, 0.0)
    alive = list(range(n))
    ub = 0
    fill_total = 0
    while len(alive) > 1:
        sub = A[np.ix_(alive, alive)]
        deg = sub.sum(axis=1)
        AA = sub @ sub
        tri = np.einsum("ij,ij->i", AA, sub) / 2.0
        fill = deg * (deg - 1) / 2.0 - tri
        vi = int(np.argmin(fill))
        ub = max(ub, int(deg[vi]))
        fill_total += int(round(fill[vi]))
        v = alive[vi]
        nbrs = [alive[j] for j in np.where(sub[vi] > 0)[0]]
        # fill-in: connect the eliminated node's neighbours, then remove it
        A[np.ix_(nbrs, nbrs)] = 1.0
        np.fill_diagonal(A, 0.0)
        A[v, :] = 0.0
        A[:, v] = 0.0
        alive.pop(vi)
    return ub, fill_total


# --------------------------------------------------------------------------- #
# spectral / community metrics
# --------------------------------------------------------------------------- #

def spectral_gap(g: nx.Graph) -> float | None:
    """1 - lambda2/lambda1 of the largest connected component's adjacency
    (normalised spectral gap; None for degenerate graphs)."""
    if g.number_of_nodes() < 3:
        return None
    comps = [g.subgraph(c).copy() for c in nx.connected_components(g)]
    g = max(comps, key=lambda x: x.number_of_nodes())
    if g.number_of_nodes() < 3:
        return None
    A = nx.to_numpy_array(g, nodelist=sorted(g.nodes()), weight=None)
    ev = np.linalg.eigvalsh(A)
    l1, l2 = ev[-1], ev[-2]
    if abs(l1) < 1e-12:
        return None
    return float(1 - l2 / l1)


def community_metrics(inst, resolution: float = 1.0) -> dict:
    """Leiden partition of the primal graph -> modularity + HCS-style proxies
    (hierarchy depth via recursive partitioning is E5 work; here flat stats)."""
    import igraph as ig
    import leidenalg as la
    g = primal_graph(inst)
    if g.number_of_edges() == 0:
        return {"modularity": None, "n_communities": None, "community_size_cv": None}
    edges = [(u - 1, v - 1) for u, v in g.edges()]
    ig_g = ig.Graph(n=g.number_of_nodes(), edges=edges)
    part = la.find_partition(ig_g, la.RBConfigurationVertexPartition,
                             resolution_parameter=resolution, seed=42)
    sizes = sorted(part.sizes(), reverse=True)
    mod = ig_g.modularity(part, resolution=resolution)
    cv = float(np.std(sizes) / np.mean(sizes)) if sizes else None
    return {"modularity": float(mod), "n_communities": len(sizes),
            "largest_community_frac": sizes[0] / g.number_of_nodes(),
            "community_size_cv": cv}


def clustering_coef(g: nx.Graph) -> float:
    return float(nx.average_clustering(g)) if g.number_of_nodes() else 0.0


# --------------------------------------------------------------------------- #
# solution-space geometry proxies
# --------------------------------------------------------------------------- #

def backbone_fraction(inst) -> float | None:
    """Fraction of variables fixed across sampled solutions (WalkSAT samples;
    pilot-stage: returns None until sampler lands in M1-d)."""
    return None


def sigma_redundancy_hist(inst) -> list[int]:
    """For planted instances: how many of the 3 literals sigma satisfies, per
    clause.  Measured mean ≈2.14–2.23, r-invariant (pilot).  旧注"uniform-7
    预言 12/7≈1.714"不适用于本构造：12/7 只是纯 uniform-7 抽样下满足位置数的
    期望；实际模式经 σ-子集均匀抽样 + β-诱饵约束填充（2026-09-11 勘误）。"""
    assert inst.sigma is not None
    return [sum((l > 0) == inst.sigma[abs(l) - 1] for l in c) for c in inst.clauses]


def all_metrics(inst) -> dict:
    g = primal_graph(inst)
    known_ub = inst.params.get("k") if inst.family == "tw_controlled" else None
    lb, ub, method = treewidth_bracket(g, known_ub=known_ub)
    out = {
        "n_vars": inst.n_vars,
        "n_clauses": len(inst.clauses),
        "alpha_eff": len(inst.clauses) / inst.n_vars,
        "graph_density": nx.density(g),
        "mean_degree": 2 * g.number_of_edges() / max(g.number_of_nodes(), 1),
        "clustering": clustering_coef(g),
        "tw_lb": lb, "tw_ub": ub, "tw_method": method,
    }
    sg = spectral_gap(g)
    out["spectral_gap"] = sg
    out.update(community_metrics(inst))
    if inst.sigma is not None:
        h = Counter(sigma_redundancy_hist(inst))
        out["sigma_redundancy_mean"] = sum(k * v for k, v in h.items()) / sum(h.values())
    return out

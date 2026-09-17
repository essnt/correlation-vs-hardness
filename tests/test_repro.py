"""Reproducibility regression tests: generator determinism, the E3b
degree-preservation invariant, and the DIMACS declaration-checked parser.

These complement tests/test_probsat.py (probSAT wrapper). They are
self-contained: no external data files or solver binaries are required.
"""
import importlib.util
from pathlib import Path

import pytest

from cvh.generators import degree_preserving_randomize, locality_kernel

# experiments/ is not an importable package (script layout); load the parser
# module directly from its file. e4_status bootstraps its own src/ path.
_E4_PATH = Path(__file__).resolve().parents[1] / "experiments" / "e4_status.py"
_spec = importlib.util.spec_from_file_location("e4_status", _E4_PATH)
_e4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_e4)
parse_dimacs = _e4.parse_dimacs


def _literal_occurrences(clauses):
    counts = {}
    for clause in clauses:
        for lit in clause:
            counts[lit] = counts.get(lit, 0) + 1
    return counts


def test_locality_kernel_determinism():
    a1 = locality_kernel(60, 3.0, 0.5, seed=7, planted=False)
    a2 = locality_kernel(60, 3.0, 0.5, seed=7, planted=False)
    b = locality_kernel(60, 3.0, 0.5, seed=8, planted=False)
    assert a1.to_dimacs() == a2.to_dimacs()
    assert a1.to_dimacs() != b.to_dimacs()


def test_locality_kernel_clause_shape():
    n, alpha = 60, 3.0
    inst = locality_kernel(n, alpha, 0.5, seed=3, planted=False)
    assert len(inst.clauses) == int(alpha * n)
    for clause in inst.clauses:
        vs = [abs(l) for l in clause]
        assert len(vs) == 3 and len(set(vs)) == 3
        assert all(1 <= v <= n for v in vs)


def test_degree_preserving_swap_keeps_literal_occurrences_exact():
    inst = locality_kernel(80, 4.0, 0.3, seed=11, planted=False)
    swapped, _stats = degree_preserving_randomize(inst, seed=42)
    assert len(swapped.clauses) == len(inst.clauses)
    assert _literal_occurrences(inst.clauses) == _literal_occurrences(swapped.clauses)


def test_parse_dimacs_standard_dialect(tmp_path):
    cnf = "c standard dialect smoke test\np cnf 4 2\n1 -2 3 0\n-1 2 -4 0\n"
    p = tmp_path / "smoke.cnf"
    p.write_text(cnf)
    n_vars, clauses, declared = parse_dimacs(p)
    assert n_vars == 4
    assert len(clauses) == 2 and declared == 2
    assert clauses[0] == [1, -2, 3]


def test_parse_dimacs_declared_count_mismatch_raises(tmp_path):
    # 声明 3 条子句但只给出 2 条 → 必须 raise（静默截断即 2026-09-12 事故根因）
    cnf = "p cnf 4 3\n1 -2 3 0\n-1 2 -4 0\n"
    p = tmp_path / "bad.cnf"
    p.write_text(cnf)
    with pytest.raises(Exception):
        parse_dimacs(p)


def test_swap_stats_partition():
    # 拒绝原因计数与 steps/accepted 的守恒（tautology 提案在 |l| 检查下
    # 并入 reject_duplicate——stats 中不存在独立的 reject_tautology 键）
    inst = locality_kernel(60, 3.0, 0.5, seed=5, planted=False)
    _swapped, stats = degree_preserving_randomize(inst, seed=1)
    assert stats["accepted"] == 10 * len(inst.clauses)
    assert (stats["reject_duplicate"] + stats["reject_sat"]
            <= stats["steps"] - stats["accepted"])
    assert "reject_tautology" not in stats


def test_adj_r2_df_penalty():
    # 自由度惩罚方向：加入无用列必须降低 adjusted R²；强拟合保持高分。
    # （2026-09-17 修正：分母 n-k，截距由 X 内 ones 列计一次）
    import importlib.util

    import numpy as np

    _p = Path(__file__).resolve().parents[1] / "experiments" / "e5_baseline.py"
    _spec = importlib.util.spec_from_file_location("e5_baseline", _p)
    _eb = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_eb)
    rng = np.random.default_rng(0)
    n = 80
    x = rng.normal(size=n)
    y = 2.0 * x + rng.normal(scale=0.5, size=n)
    X1 = np.column_stack([np.ones(n), x])
    X2 = np.column_stack([np.ones(n), x, rng.normal(size=n)])
    a1 = _eb.adj_r2(X1, y)
    a2 = _eb.adj_r2(X2, y)
    assert a1 > 0.9
    assert a1 > a2

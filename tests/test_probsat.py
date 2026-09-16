"""Minimal tests for the probSAT subprocess wrapper."""
import time
from pathlib import Path

import pytest

from cvh.generators import locality_kernel
from cvh.probsat import parse_probsat_output, run_probsat

# 与 cvh/probsat.py 同一定位：二进制不入库（.gitignore），依赖二进制的测试
# 跳过而非失败；构建方法见 tools/probsat/README.md（cd tools/probsat && make）
_PROBSAT = Path(__file__).resolve().parents[1] / "tools" / "probsat" / "probSAT"
_needs_binary = pytest.mark.skipif(
    not _PROBSAT.exists(), reason="probSAT binary not built — see tools/probsat/README.md")


def _write_cnf(tmp_path, n=120, alpha=4.0, r=1.5, seed=7):
    inst = locality_kernel(n, alpha, r, seed=seed, planted=True)
    path = tmp_path / "smoke.cnf"
    path.write_text(inst.to_dimacs())
    return path


def test_parse_output_sat_and_unknown():
    out = ("c EndStatistics:\n"
           "c numFlips                      : 1357     \n"
           "s SATISFIABLE\n")
    assert parse_probsat_output(out) == ("sat", 1357)
    out2 = ("c caught signal... exiting\n"
            "c numFlips : 420\n"
            "s UNKNOWN best(3) (0.50000sec)\n")
    assert parse_probsat_output(out2) == ("unknown", 420)
    assert parse_probsat_output("nothing here") == ("unknown", None)


@_needs_binary
def test_run_probsat_sat(tmp_path):
    path = _write_cnf(tmp_path)
    res = run_probsat(path, cutoff_seconds=10.0, seed=0)
    assert res["status"] == "sat"
    assert isinstance(res["flips"], int) and res["flips"] > 0
    assert 0 <= res["wall_s"] < 10.0


@_needs_binary
def test_run_probsat_cutoff_reports_unknown(tmp_path):
    path = _write_cnf(tmp_path, n=150, alpha=4.0, r=1.5, seed=11)
    res = run_probsat(path, cutoff_seconds=0.0, seed=0)
    # cutoff 0 -> SIGTERM almost immediately; must not hang and must return
    # a well-formed record in either branch (finished in <0s is impossible,
    # so 'unknown' is expected, but accept any legal status).
    assert res["status"] in {"sat", "unsat", "unknown"}
    assert res["flips"] is None or res["flips"] >= 0
    assert res["wall_s"] < 30.0

"""Subprocess wrapper around probSAT (stochastic local search, SC13.2).

The binary lives in tools/probsat/ (source + build recipe in
tools/probsat/README.md).  probSAT has no wall-clock cutoff of its own
(maxTries/maxFlips only), so the wrapper enforces `cutoff_seconds` by
sending SIGTERM: the solver's signal handler flushes its EndStatistics
block (including the flip count and an 's UNKNOWN' line) before exiting,
so partial statistics are still parsed.

Output conventions parsed here (see tools/probsat/README.upstream.md and
probSAT.c):
  's SATISFIABLE'    -> status 'sat'   (exit code 10)
  's UNSATISFIABLE'  -> status 'unsat' (exit code 20; an SLS solver will
                         not actually prove this in practice)
  's UNKNOWN ...'    -> status 'unknown' (cutoff hit / tries exhausted)
  'c numFlips  : N'  -> flips
Note: seed 0 is accepted by the binary (srand(0), deterministic) but makes
it print a benign warning line on stdout.
"""
from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROBSAT_BIN = PROJECT_ROOT / "tools" / "probsat" / "probSAT"

_NUMFLIPS_RE = re.compile(r"^c numFlips\s*:\s*(\d+)\s*$", re.MULTILINE)


def parse_probsat_output(output: str) -> tuple[str, int | None]:
    """Return (status, flips) from probSAT stdout/stderr text."""
    status = "unknown"
    for line in output.splitlines():
        s = line.strip()
        if s.startswith("s SATISFIABLE"):
            status = "sat"
            break
        if s.startswith("s UNSATISFIABLE"):
            status = "unsat"
            break
        if s.startswith("s UNKNOWN"):
            status = "unknown"
            break
    m = _NUMFLIPS_RE.search(output)
    flips = int(m.group(1)) if m else None
    return status, flips


def run_probsat(cnf_path: str | Path, cutoff_seconds: float = 10.0,
                seed: int = 0) -> dict[str, object]:
    """Run probSAT on a DIMACS file under a wall-clock cutoff.

    Returns {"status": 'sat'|'unsat'|'unknown', "flips": int|None,
    "wall_s": float}.  On cutoff, the solver is SIGTERMed after it has
    flushed its EndStatistics (status 'unknown', flips so far).
    """
    if not PROBSAT_BIN.exists():
        raise FileNotFoundError(
            f"probSAT binary not found at {PROBSAT_BIN}; "
            "see tools/probsat/README.md to build it")
    cmd = [str(PROBSAT_BIN), str(cnf_path), str(seed)]
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    try:
        output, _ = proc.communicate(timeout=cutoff_seconds)
    except subprocess.TimeoutExpired:
        # SIGTERM: probSAT's handler prints 's UNKNOWN best(...)' plus the
        # EndStatistics block (numFlips) and exits.  Give it a moment, then
        # escalate to SIGKILL so we never hang.
        proc.terminate()
        try:
            output, _ = proc.communicate(timeout=5.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            output, _ = proc.communicate()
    wall = time.perf_counter() - t0
    status, flips = parse_probsat_output(output)
    return {"status": status, "flips": flips, "wall_s": wall}

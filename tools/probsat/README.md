# probSAT (v SC13.2) — provenance, build, usage

Stochastic local search SAT solver used as the SLS contrast to the CDCL
harness in `src/cvh/solver.py`.

- Upstream: single-file C program by **Adrian Balint & Ulrich Schöning**,
  University of Ulm.  probSAT won the SAT Competition 2013 (random track);
  the paper is "Choosing Probability Distributions for Stochastic Local
  Search and the Role of Make versus Break", SAT 2012, LNCS 7317, pp. 16-29.
- Source obtained from GitHub mirror: <https://github.com/adrianopolus/probSAT>
  (commit on `master` as of 2026-09-09).  `probSAT.c` self-reports
  **version SC13.2** (the SAT Competition 2013 version).
- License: upstream `LICENSE` file kept in this directory (MIT).

## Local modifications

One minimal patch for modern GCC (>= 14 promotes
`-Wincompatible-pointer-types` to a hard error):

```diff
-void handle_interrupt() {
+void handle_interrupt(int sig) {
```

Nothing else was changed (verified against upstream `master`).

## Build

```sh
cd tools/probsat && make
```

Upstream `makefile` uses
`gcc -Wall -Wextra -static -O3 -funroll-loops -fexpensive-optimizations probSAT.c -lm -o probSAT`
(static linking worked on this machine; if it fails, drop `-static`).
The built binary `probSAT` is **not committed** (see root `.gitignore`).

## Invocation

```
./probSAT [options] <DIMACS CNF instance> [<seed>]
```

Defaults: break-only polynomial function (`--fct 0`, `--eps 1.0`,
k-dependent `--cb` = 2.06 for 3-SAT), no wall-clock limit (`maxTries`/
`maxFlips` effectively unbounded).  Seed is the second positional argument;
`seed=0` is accepted (`srand(0)`, deterministic) with a benign warning.

Output conventions: `s SATISFIABLE` (exit code 10) / `s UNSATISFIABLE`
(exit 20) / `s UNKNOWN`; flip count in the `c numFlips : N` line of the
`c EndStatistics:` block.  On SIGTERM the handler flushes that block
before exiting, which is how `src/cvh/probsat.py` implements its
`cutoff_seconds` wall-clock cutoff while still reporting flips so far.

## Smoke test (2026-09-09, gcc 15.2.0, WSL2 x86-64)

Instance: `cvh.generators.locality_kernel(200, 4.0, 1.5, seed=1,
planted=False)` (200 vars / 800 clauses), seed 42:

```
c EndStatistics:
c numFlips                      : 1357
s SATISFIABLE
```

Python wrapper: `from cvh.probsat import run_probsat;
run_probsat("/path/x.cnf", cutoff_seconds=10, seed=0) -> dict(status, flips, wall_s)`.

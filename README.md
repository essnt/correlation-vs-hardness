> 中文版（Chinese version）：[README_zh.md](README_zh.md)

# Correlation vs. Hardness — An Interventional Empirical Study of Causal Correlation Structure and Computational Hardness

**Core question**: with density, scale, degree distribution, and clause content
all held controlled, does changing *only* the "locality radius r" of variable
interaction (how quickly correlations decay) suffice to shift the difficulty of
SAT solving by orders of magnitude?

This design originates from a long-standing conjecture — that real-world causal
structure is local: no arbitrarily strong long-range correlations — which may be
one of the preconditions for the computability of the world. The project turns
that conjecture into a falsifiable, controlled experiment: locality becomes a
tunable knob (r), and we test whether it causally determines SAT solving
difficulty.

## Hypotheses (preregistered at the end of M1 in docs/HYPOTHESES.md)

- **H1** (CDCL families only): after controlling for density and scale, a
  combination of structural metrics explains solving time significantly better
  than density alone.
- **H2** (core): with n, α, literal degree distribution, clause content
  distribution, and σ-satisfaction redundancy all controlled, varying r alone still produces
  a significant causal effect (2×2 factorial + paired design).
- **H3** (exploratory): LLM branching-guide quality improves with stronger
  locality. (**Cut**: E6 hit the preregistered kill line; negative result
  recorded in docs/HYPOTHESES.md and docs/REPORT_zh.md §10.)

## Main results (completed 2026-09-10)

- **Threshold curve**: α_c(r) is bracketed from above at <2.5 at r=0.06 (SAT
  rate declines from ~0.31 to ~0.13 across the probed grid; the 0.5-crossing is
  unreachable), rises through 3.35→4.23 at r=0.08→0.22, and enters measurement
  saturation at r≥0.3 (near-threshold instances undecidable within 10⁷
  conflicts / 300 s; pilot coarse estimates ~4.4–4.7) — locality moves the
  sat/unsat boundary itself.
- **H2 confirmed**: at matched threshold offsets Δ, difficulty among decided
  instances spans 3.4 orders of magnitude (1.45→4.86; ≥4.5 counting
  budget-censored runs at their lower bound); F(8,216)=2808.5 (p≈1e-213),
  JT p≤1e-4 (q≤1e-4 after FDR), partial η²≈0.99.
- **E3b scalpel**: degree-preserving swaps that destroy locality raise
  difficulty ×16–68 (p≤7e-10), flipping 53 of the 82 resolved pairs'
  satisfiability; the ratio is a composite spanning those status changes
  (within the 29 status-stable pairs the elevation persists, ×11/×1.8 per
  arm, p≤3.9e-3).
- **Mediation (exploratory, post-hoc mediator set per AMEND-5)**: modularity
  ACME 3.06 [2.84,3.37] (~94% of total effect);
  all four channels' CIs exclude 0.
- **H1 ladder**: across the main scan, structural-feature CV R² 0.66→0.976
  (random-family control shows zero gain); GBDT leave-one-r-out extrapolation
  0.76.
- See docs/REPORT.md (in-depth report, English; Chinese original in
  docs/REPORT_zh.md), docs/paper_draft_en.md (English paper v0.2),
  docs/PRESPEC_AUDIT.md (preregistration audit), docs/M2_LOG.md (full
  experiment log).

## Repository layout

```
docs/          preregistration, prespecification audit, literature notes, reports
src/cvh/       core library (generators / metrics / solver harness / statistics)
experiments/   experiment scripts (E1–E6)
data/          instances and benchmarks (content-addressed; large files git-ignored)
results/       result databases (SQLite) and figures
```

## Milestones

- **M0** ✅ literature check and novelty positioning (Go/No-Go)
- **M1** ✅ infrastructure + pilot calibration + preregistration
- **M2** ✅ core experiments (E1–E4)
- **M3** ✅ predictors (E5), E6 (hit the preregistered kill line and was cut;
  negative result archived), analysis and writing
- **M4** ✅ wrap-up and release (archived on Zenodo, open-sourced on GitHub)

## Honest boundaries

This work does not attack P vs NP itself; it promises neither new theorems nor
publication; negative results are reported just as completely.

## Reproduce

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest tests/ -q           # probSAT-dependent tests auto-skip if the binary is missing
cd tools/probsat && make && cd ../..           # optional: build probSAT per tools/probsat/README.md
.venv/bin/python experiments/e3a_analysis.py   # deterministically regenerate analysis JSON and figures from results/*.db
bash scripts/status.sh                         # progress reconciliation
```

All figures are regenerated from results/*.db by committed scripts; per-
experiment methodology and the full record are in docs/REPORT_zh.md
(§13 reproduction guide). The result databases ship with the repository:
re-running experiment scripts resumes and automatically skips jobs that
already carry a verdict (`status.sh` reconciles progress); the tracked
repository content (code plus all result databases) is about 5 MB, and a
fresh clone including the full git history is about 9 MB (past revisions
of the result databases and packaged artifacts dominate the history).

Platform notes: the paths above run on Linux / macOS / Windows
(Python 3.11–3.14); all dependencies ship prebuilt wheels for the three
platforms, and the CDCL solver is bundled with the python-sat wheel.
`status.sh` is a bash script — on Windows, run it in WSL/Git Bash, or skip it
(progress reconciliation only). The probSAT binary is an optional build
(requires a C compiler); relevant tests auto-skip when it is missing.

## Citation

An archived version of this repository (compact paper + full snapshot) is
published on Zenodo:
**DOI 10.5281/zenodo.22777748** (https://zenodo.org/records/22777748) — the
concept DOI, which always resolves to the latest version; the version-specific
DOI of the first release (2026-09-15) is 10.5281/zenodo.22777749.

```bibtex
@misc{song2026locality,
  author       = {Song, Jin},
  title        = {Locality Causes Tractability? An Intervention Study on the
                  Variable-Interaction Radius in Geometric Random Satisfiability},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.22777748},
  url          = {https://zenodo.org/records/22777748}
}
```

# Locality Causes Tractability? An Intervention Study on the Variable-Interaction Radius in Geometric Random Satisfiability

**Author:** Jin Song (Independent Researcher)
**Version:** Journal version, prepared for journal submission. A compact
version of this work remains archived in Zenodo versions 1-3; versions 4
and later carry the full journal version, substantially expanded with complete
threshold tables, per-arm dose-response details, censoring-sensitivity
analyses, and the protocol appendix (including the JAIR Reproducibility
Checklist).
**License:** PDF & text: CC-BY-4.0. Code in the snapshot: MIT, except the bundled probSAT tool (`tools/probsat/`), which retains its original research-use license (see `tools/probsat/LICENSE`).

## Contents
1. `SongJin_2026_LocalityCausesTractability_JournalVersion.pdf` - the paper (19 pages).
2. `correlation-vs-hardness_snapshot.tar.gz` - full snapshot of the research repository:
   - `src/cvh/` generators, solver harness (resume-per-row), metrics, statistics
   - `experiments/` every experiment script (S0, E1-E6, E4, E5, spotcheck)
   - `results/` SQLite databases (all raw solve runs), analysis JSON, figures
   - `docs/` preregistration (HYPOTHESES.md + AMEND-1–5), prespecification audit
     (PRESPEC_AUDIT.md), experiment log (M2_LOG.md), full report (REPORT.md;
     Chinese original REPORT_zh.md), reader's guide (REPORT_GUIDE.md;
     Chinese original REPORT_zh_导读.md), literature notes, AI-use
     disclosure (AI_DISCLOSURE.md)
   - `data/external/e4prime/` external-instance manifest for E4-prime (SHA256 per
     instance; the third-party benchmark files themselves are not redistributed —
     refetch them from the public suites and verify against the manifest)
   - `scripts/` verification & packaging utilities (final_verify, rebuild_zenodo)
   - `tools/probsat/` bundled third-party probSAT solver (research-use license)
   - `tests/` unit tests; `LICENSE` + third-party license notices
   - `jair/` LaTeX source of the journal version (official JAIR author kit format)
   - `arxiv/` LaTeX source of the compact version (archived in Zenodo v1-v3)

## One-paragraph abstract
Holding the number of variables fixed, matching clause density relative to each
radius's own threshold, and keeping clause-content statistics r-invariant by
construction, varying only the radius r within which clause variables are sampled
from a 2-D
torus changes CDCL SAT difficulty: the operational satisfiability
boundary lies below 2.5 at r=0.06 and near ≈4.3 by r=0.22, and at matched threshold offsets difficulty
spans 3.4 orders of magnitude among decided instances (>=4.5 counting
budget-censored runs at their lower bound; F(8,216)=2808.5; JT p<=1e-4, FDR
q<=1e-4; partial eta^2~0.99). A degree-preserving swap that destroys locality raises
difficulty 16-68x (p<=7e-10) and flips 53 of the 82 resolved pairs'
satisfiability; the ratio is a composite spanning those status changes
(within the 29 status-stable pairs the elevation persists, 11x/1.8x per
arm, p<=3.9e-3); post-hoc, exploratory causal mediation analysis is consistent
with ~94% of the effect flowing through
community-structure restructuring. Scope: n=400, direct CNF, CDCL solvers.

## Reproduce
Every figure regenerates from the SQLite stores via committed scripts; see
README inside the snapshot. Contact: j.song.cs@outlook.com

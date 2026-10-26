# Locality Causes Tractability? An Intervention Study on the Variable-Interaction Radius in Geometric Random Satisfiability

**Author:** Jin Song (Independent Researcher)
**Version:** Constraints submission version (v8). A compact version of this
work remains archived in Zenodo versions 1-3; versions 4-7 carry the JAIR
journal version, substantially expanded with complete threshold tables,
per-arm dose-response details, censoring-sensitivity analyses, and the
protocol appendix. Version 8 adapts that journal version for Springer
*Constraints* (sn-jnl template, numbered references, unstructured abstract,
Statements and Declarations back matter, a Related Work paragraph on
structural tractability in constraint programming) and adds re-presentations
and robustness analyses of the same deposited data. The headline results and
the three figure files are unchanged.
**License:** PDF & text: CC-BY-4.0. Code in the snapshot: MIT, except the
bundled probSAT tool (`tools/probsat/`), which retains its original
research-use license (see `tools/probsat/LICENSE`). The `constraints/`
directory contains the Springer Nature `sn-jnl` class and bst files (LaTeX
Project Public License) plus their `.sty` dependencies, each redistributed
under the permissive LaTeX license stated in its own header, separate from
the MIT-licensed research code.

## Contents
1. `SongJin_2026_LocalityCausesTractability_ConstraintsVersion.pdf` - the paper (25 pages).
2. `correlation-vs-hardness_snapshot.tar.gz` - full snapshot of the research repository:
   - `src/cvh/` generators, solver harness (resume-per-row), metrics, statistics
   - `experiments/` every experiment script (S0, E1-E6, E4, E5, spotcheck)
   - `results/` SQLite databases (all raw solve runs), analysis JSON, figures
   - `docs/` preregistration (HYPOTHESES.md + AMEND-1-5), prespecification audit
     (PRESPEC_AUDIT.md), experiment log (M2_LOG.md), full report (REPORT.md;
     Chinese original REPORT_zh.md), reader's guide (REPORT_GUIDE.md;
     Chinese original REPORT_zh_导读.md), literature notes, AI-use
     disclosure (AI_DISCLOSURE.md)
   - `data/external/e4prime/` external-instance manifest for E4-prime (SHA256 per
     instance; the third-party benchmark files themselves are not redistributed -
     refetch them from the public suites and verify against the manifest)
   - `scripts/` verification & packaging utilities (final_verify, rebuild_zenodo)
   - `tools/probsat/` bundled third-party probSAT solver (research-use license)
   - `tests/` unit tests; `LICENSE` + third-party license notices
   - `constraints/` LaTeX source of the Constraints version (sn-jnl class,
     sn-basic.bst, LPPL-licensed dependencies, figures)
   - `jair/` LaTeX source of the JAIR journal version (official JAIR author kit format)
   - `arxiv/` LaTeX source of the compact version (archived in Zenodo v1-v3)

## Changes in v8 relative to v7
- **Constraints presentation:** Springer sn-jnl template with numbered
  references, unstructured abstract, Statements and Declarations back matter,
  removal of the JAIR-specific reproducibility-checklist appendix, and a new
  Related Work paragraph on structural tractability in constraint programming
  (four references).
- **Re-presentations and robustness analyses of the same deposited data:** a
  new Table 4 (E3b composition by (Delta, r)), the r=1.5 sham-arm analysis,
  the 240-pair censoring-aware direction test, the intervention-check metrics,
  the S0 alpha_c confidence interval and seed-bootstrap statement, the H1
  cell-dummy baseline with its extrapolation positioning, the mediation
  collinearity/placebo caveat, the five-row E1 600 s wall-timeout
  disclosure, and two added Threats sentences on the Construct paragraph
  (residual threat from conditioning on non-empty radius balls; conflict
  counts do not measure propagation/inprocessing work). No new experiments
  were run and no headline result was recomputed.
- **Text-level corrections and disclosure refinements:** the instance-geometry
  description now says "continuous 2-D unit torus" (v7 said "discrete ...
  torus of side sqrt(n)"; implementation and diameter are unchanged); the
  contribution claim now reads "first threshold-matched, preregistered
  intervention scan" and the IJCAI 2017 locality-generator sentence is
  completed; two Introduction sentences state the two disclosed design limits
  up front; the abstract opening now reads "a popular intuition"; the
  abstract conclusion is weakened to "consistent with spatial locality
  contributing to the causal channel" (v7: "it behaves as the causal
  channel") and the contribution bullet now says the paired Wilcoxon tests
  "probe the causal contribution of the structure-destroying bundle" (v7:
  "isolate the causal contribution of spatial structure"); the abstract's
  E3b presentation now reads "within the nine status-stable sat--sat pairs
  the elevation is x10.7" (v7: "within the 29 status-stable pairs ... 11x
  and 1.8x per offset arm"), drawn from the new Table 4; the E4 placement
  claim is narrowed to "among the instances decided within budget ... overlaps
  the middle" (v7: "spans the middle"); the nested OLS F-test is now read as
  "descriptive ... not independent confirmation" (v7: "confirms the ladder");
  the E1 conclusion sentence was restructured and several Discussion/E4
  wordings tightened; the AMEND-5 timing now reads "at an audit prior to
  unblinding" (v7: "at independent-review disposition"); the generator's
  clause-center description is corrected to "pick the position of a uniformly
  chosen variable as the center" (v7: "pick a centre uniformly"; Sec. 3 and
  Appendix D) — a textual correction of the description, the implementation
  is unchanged; solver-scope disclosures were refined (the post-freeze
  Delta=+0.6 arm and the E3b swap arm are labeled CaDiCaL-only), the
  240-pair direction-test exclusion count is completed (82 + 94 + 60 + 4),
  two redundant words were dropped from the abstract, inline citations of
  Tables 1 and 2 were added in the running text, and a one-sentence pointer
  to the AI-use disclosure was added at the end of the Methods section.
- The compact version's source (`arxiv/`) received the same textual
  corrections where the two versions share text (instance geometry, generator
  center selection, completed IJCAI-2017 sentence, contribution hedge with the
  "probe the structure-destroying bundle" wording, the abstract's weakened
  conclusion, Discussion softening, AMEND-5 timing, the singular Figure 1
  caption, the added inline citations of Tables 1 and 2, table footnote
  markers); its PDF was recompiled (13 pages, 3
  figures). As an archived record it otherwise keeps its v7 wording: the
  abstract opening and the per-arm stratified E3b presentation, and the E4,
  nested-F, E1-conclusion, up-front-design-limit, and solver-scope (CaDiCaL)
  refinements, the Methods-section AI-disclosure pointer, and the
  post-semicolon contrast clause of the completed IJCAI-2017 sentence, are
  journal-version only.
- No table values or figure files were altered (table footnote markers were
  normalized from symbols to letters); the three figure files are
  byte-identical to v7.

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
arm, p<=3.9e-3). The swap is a composite intervention, so the paired contrast
is attributed to the structure-destroying bundle rather than to spatial
locality alone; post-hoc, exploratory mediation over four collinear mediators
yields a ~94% community-restructuring share, a consistency check rather than
a mechanism fraction. Scope: n=400, direct CNF, CDCL solvers.

## Reproduce
Every figure regenerates from the SQLite stores via committed scripts; the
Constraints source is in `constraints/` and compiles against the pinned TeX
environment used for the deposit. Contact: j.song.cs@outlook.com

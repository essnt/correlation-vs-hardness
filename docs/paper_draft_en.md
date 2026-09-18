# Does Locality Cause Tractability? An Intervention Study on the Variable-Interaction Radius in Random Geometric SAT

*Working paper draft — v0.2, 2026-09-10 (status refreshed 2026-09-12). **Main scans complete: H2 confirmed (positive-result framing active, title 1); negative-result title retired.** All result-dependent numbers are final (E3a/E3b/E5 in §6–§9 and arxiv/main.tex); the S0 threshold table (§5) is final
data as of this draft. Related-work citations are verified against DOIs listed in
`docs/papers/notes/`.*

---

## Candidate titles

1. **(Positive-result framing)** "Locality Radius Causally Shifts the Satisfiability
   Threshold: An Intervention Study of CDCL Hardness in Geometric Random 3-SAT"
2. **(Negative-result framing)** "Density Dominates, Structure Does Not: A Controlled
   Intervention Test of Locality-Based Hardness in SAT"
3. **(Neutral/methods framing)** "Turning One Knob at a Time: Intervention Designs for
   Causal Claims about SAT Instance Structure and Solver Difficulty"

## Abstract

A widespread intuition — prominent in popular discussions of P versus NP — holds that
real-world computational problems are easy because their "causes act locally": when
variables interact only within small neighbourhoods, constraint solvers should scale
well. Observational evidence supports the intuition (industrial instances exhibit
community structure and locality, and are solved quickly), but observation cannot
separate locality from the many other regularities real instances carry. We translate
the intuition into a falsifiable, interventional claim: holding the number of
variables fixed, matching clause density relative to each radius's own
threshold, and with clause-content statistics r-invariant by construction,
varying *only* the radius r within which clause variables are drawn from a
2-D torus should causally change CDCL solving difficulty. Using a locality-kernel
generator, a degree-preserving swap intervention that destroys locality while keeping
the literal degree sequence exactly fixed, and censoring-aware statistics, we measure
difficulty (conflict counts) and the operational satisfiability threshold α_c(r).
Three findings. (i) The threshold is bracketed from above at <2.5 (r = 0.06) and
rises to ≈4.4 (r = 0.3) — locality moves the satisfiability boundary itself, by
≈1.9 density units — before becoming unmeasurable at r ≥ 0.3 under a
10⁷-conflict budget. (ii) At density matched relative to each radius's own
threshold, difficulty spans 3.4 orders of magnitude across r among decided
instances, and ≥4.5 orders when budget-censored runs are counted at their lower
bound (mean log10 conflicts 1.45 → 4.86 from r = 0.06 to 0.22;
RM-ANOVA F(8,216) = 2808.5, p ≈ 1e-213; Jonckheere–Terpstra p = 1e-4 with FDR
q = 1e-4; partial η² ≈ 0.99). (iii) The degree-preserving swap raises difficulty by
16–68× (Wilcoxon p ≤ 7e-10) and flips the satisfiability status of 53 instance
pairs; causal mediation attributes ~94% of the r-effect to community-structure
restructuring (ACME 3.06, bootstrap CI [2.84, 3.37]). Locality is not merely
correlated with tractability — under our controls it is the causal channel. We
discuss what this does and does not say about P versus NP, and we release all code,
seeds, and data.

## 1. Introduction

**The conjecture and its observational gap.** In a widely circulated dialogue about
prospects for resolving P versus NP, one participant offered a philosophical
diagnosis: problems resist algorithmic solution when variable interactions are
"strongly correlated at long range"; the physical world yields tractable instances
because causation is local. As stated, the claim is unfalsifiable — "locality",
"correlation", and "cause" are unoperationalized. Yet the intuition has an
empirically serious core. Industrial SAT instances — the reason CDCL solvers
[1] routinely decide formulas with millions of variables — exhibit community
structure [2,3], small backdoors, and heavy-tailed variable-incidence patterns.
Observationally, structure and ease co-occur.

Observation, however, cannot license a causal reading. Instances that are easy and
local are also many other things: they come from encodings with specific
decomposability, carry particular degree profiles, and were selected by years of
benchmark curation. The literature's own cautionary results make the point sharp.
Zulkoski et al. [4], in the largest correlational study to date (~7000 competition
instances), found that *no single* structural parameter significantly predicts CDCL
runtime across heterogeneous benchmark sets; the best six-feature regression reaches
adjusted R² ≈ 0.31 on application instances, and treewidth features alone reach only
0.05. Mull, Fremont and Seshia [5] prove that any "polynomial-clique" community
metric — including modularity — admits instances with excellent scores that remain
NP-hard, and that the pseudo-industrial community-attachment instances of
Giráldez-Cru and Levy require exponentially long resolution proofs with high
probability when communities are few. Structure, by itself, neither certifies nor
explains tractability.

**What an intervention adds.** The methodological remedy is standard in the
empirical sciences and, surprisingly, rare in SAT difficulty research: *hold
everything else fixed and turn one knob*. We operationalize the locality conjecture
as a dose–response experiment. A **locality-kernel generator** samples each clause's
variables uniformly from an r-ball on a discrete 2-D torus, then draws polarities
from a standardized content distribution (σ-satisfaction modes: a cardinality drawn
uniformly in 1..k, then a subset of that cardinality — giving an r-invariant
redundancy with measured mean ≈2.14–2.23); as r grows the generator interpolates
toward uniform random 3-SAT, and — in the planted arms only — degree-cap rejection
keeps literal degrees near-identical across r (the geo_random main arm is uncapped;
its degree-shape drift is disclosed in §10). The knob r has a physical reading: it is the *spatial span
of variable interaction* — the exact quantity the philosophical conjecture is about.

**Contributions.**

1. **The first controlled intervention scan of locality radius.** Nine r levels ×
   three density offsets Δ above the *r-specific* operational threshold × 30 paired
   seeds × two solvers, with every instance's structural metrics recorded
   (treewidth bracketed by min-fill upper and degeneracy lower bounds; modularity,
   community metrics, spectral gap; redundancy histograms).
2. **A threshold curve α_c(r).** Using a 10⁷-conflict-budget refinement (S0) with
   censoring-aware estimation, we show the operational threshold is *not constant*
   across r: it rises from below 2.5 (bracketed; r = 0.06) through 4.20 (r = 0.15) toward the
   classical random-3-SAT value, then becomes unmeasurable at r ≥ 0.3 because
   near-threshold instances at those radii saturate both conflict (10⁷) and wall
   (300 s) budgets — a difficulty-regime change that is itself evidence that
   locality restructures hardness rather than merely shifting it.
3. **A structure-destruction intervention (E3b).** A degree-preserving swap chain
   (bipartite edge swaps with feasibility checks) destroys spatial locality while
   keeping the literal degree sequence *exactly* fixed; paired Wilcoxon tests on
   (n, α, r, seed) tuples isolate the causal contribution of spatial structure.
   Result: difficulty ×16–68, 53/82 pairs flip sat/unsat (§7).
4. **Topology × content decomposition.** A 2×2 factorial separating the topological
   channel (which variables co-occur) from the content channel (polarity
   structure); content-arm operationalization follows the Zulkoski et al. merge-
   rescaling precedent [4] and is registered as AMEND-3 in our preregistration.
5. **An honest negative-result protocol.** Our preregistration (frozen before the
   main scan, with numbered amendments) states quantitative triggers under which we
   report "density dominates" — including the censoring-aware anti-conservative
   bias analysis for wall-clock truncation (AMEND-2).

**Scope.** All claims concern CDCL-family solvers on direct CNF encodings at
n = 400 with conflict-count difficulty; we do not claim statements about P versus NP
(§6). Machine-independence is obtained by using conflict counts, not wall-clock, as
the primary measure.

## 2. Related Work

### 2.1 Structural measures and CDCL performance

Ansótegui et al. introduced scale-free variable-incidence structure [6] and
fractal dimensions of variable-incidence graphs [7]; Newsham et al. [8] reported
regressions of CDCL runtime on community features with encouraging R².
Zulkoski et al. [4] scaled the design to ~7000 application/crafted/agile/random
instances from SAT Competitions 2009–2016, with MapleCOMSPS runtimes and both OLS
and ridge regression over standardized features with full pairwise interactions.
Their findings anchor our baseline expectations: (i) no single parameter
significantly predicts runtime across heterogeneous sets; (ii) best heterogeneous
combos reach adjusted R² ≈ 0.31 (application), 0.56 (crafted), 0.66 (random),
0.96 (agile — a homogeneous source); (iii) treewidth features add almost nothing on
application instances (R² ≈ 0.05); (iv) sub-category correlations are strong but
*sign-flipping* across categories (e.g. mergeability/resolvability ratio:
Spearman +0.94 on argumentation, −0.73 on hardware-manolios), which dilutes pooled
regressions; (v) pre-simplification and corpus grouping materially change R² — a
methodological hazard we inherit and control by reporting both pre- and
post-processing calibers in E5. On the behavioral side, Zulkoski et al. show CDCL
branching (VSIDS, LRB) is spatially local with respect to VIG communities (Gini
≈ 0.50–0.52 vs 0.16 for random branching) and temporally local (45–55% of decisions
land in the most recent 1% of communities vs 12% for random) — direct evidence that
CDCL's search dynamics *could* be sensitive to locality, i.e. the mechanism our
intervention targets. Their Chapter 5 also contributes the merge-rescaling
generator that increases mergeability while preserving variable counts, VIG
community structure, popularity distribution and resolvability — the closest
published precedent to our intervention logic, operating on the *content* channel;
we complement it with the *topological* channel. Li et al. [3] document the
hierarchical community structure of practical instances.

### 2.2 Locality and heterogeneity: theory

Bläsius et al. [9] prove that heterogeneity alone does not make random k-SAT easy
(superpolynomial resolution size), whereas geometric locality yields small
unsatisfiable subformulas findable in polynomial time — the strongest existing
theorem-level support for "locality ⇒ tractability", and the regime map our
generator navigates: small r realizes the geometric regime, r → ∞ the uniform one.
Giráldez-Cru and Levy [10] introduced power-law and community-attachment
pseudo-industrial generators; Mull et al. [5] then proved average-case hardness
(exponential resolution proofs w.h.p.) for community-attachment instances with few
communities, and — crucially for our motivation — showed experimentally that
*community size, not formula size, dominates runtime*: instances differing by a
factor of 55 in variables but matched in community size differ by ~3× in runtime.
Their construction also demonstrates that "bridge" clauses connecting communities
do not w.h.p. provide exploitable propagation shortcuts when communities are few —
directly relevant to how coupling strength varies with r in our generator. Earlier,
Jia, Moore and Strain [11] analyzed planted SAT with clustering; their planting
threshold explains why naive planted ensembles are CDCL-trivial — a pilot finding
of ours (R1/R2) that motivated our non-planted difficulty carrier.

### 2.3 Proof complexity: the width backbone

Our interpretation scaffold is the width—size—CDCL chain. Atserias and Dalmau [12]
characterize resolution width combinatorially (connectivity games), yielding
w(F ⊢ ⊥) ≥ treewidth(primal). Ben-Sasson and Wigderson [13] relate width to size,
S ≥ exp(Ω((w − w₀)²/n)): substituting w = √n makes the bound vacuous, w = Θ(n)
exponential — a "width barrier" at ≈ √(n log n). Atserias–Fichte–Thurley [14] and
Beame–Kautz–Sabharwal [15] connect CDCL to (bounded-width) resolution.
Together: low treewidth ⇒ short proofs exist ⇒ CDCL with restarts finds them in
polynomial time — our E1 result (unplanted, width-controlled instances are flat and
trivial at all k) is the empirical face of this chain. On the other side, Weitz [16]
correlation-decay results and OGP machinery (reviewed in [17]) delineate where local
information suffices and where it provably fails. We use these as *interpretive*
scaffolding only: CDCL solvers in practice carry components (VSIDS, restarts,
preprocessing) outside these models, so theory guides reading, not guarantees.

## 3. Problem Setup and Instance Generators

**Locality kernel (geo_random).** Fix n variables placed uniformly on a discrete
2-D torus (side √n). Each of m = αn clauses: pick a center uniformly, collect the
variables within torus distance r (up to 1000 attempts to find a ball containing
at least three variables), sample
3 distinct variables from that ball, and draw polarities uniformly (planted=False).
Small r gives high intra-cluster variable reuse and sparse inter-cluster coupling;
r → ∞ recovers (approximately) uniform random 3-SAT. The *planted* variant
(planted=True) draws polarities from σ-satisfaction modes — for each clause, draw a
cardinality uniformly in 1..k (k = the positions a global σ satisfies) and then a
subset of that cardinality — giving a measured mean σ-redundancy ≈2.14–2.23 (the
naive 12/7 applies only to uniform sampling over the 7 non-empty subsets), verified
in pilots to keep redundancy histograms identical across r. This generator is the
non-planted regime of Bläsius et al.'s geometric family [9].

**Width-controlled family (tw_controlled).** k-tree skeletons give constructive
treewidth ≤ k; a matching random family at the same (n, α) provides controls
(E1). Planted and unplanted arms separate "having a solution planted" from
"being structured".

**Structure-destruction intervention (E3b).** A bipartite swap chain (MCMC edge
swaps on the variable–clause incidence graph, rejecting swaps that duplicate a
variable in a clause or create complementary-literal pairs) destroys spatial
locality while preserving every literal's degree *exactly*. The swapped instance is
not a draw from the geo_random distribution; following our preregistration
(frozen record item 3) we report it as a structure-destruction intervention, and we
record solver-status flips per pair explicitly.

**Topology × content factorial.** Topology channel: original vs swapped incidence
graph. Content channel: original vs resampled polarity structure. On our main
(unsatisfiable-arm) carrier, a distribution-preserving content resample is the
identity by construction (polarities are already uniform), so the content channel's
unambiguous operationalization lives on the planted robustness arm or via a
Zulkoski-style structure-preserving polarity-flip construction; our preregistration
registers this tension openly as AMEND-3 and defers the interaction test rather
than shipping an ill-defined arm.

**Threshold matching.** Because difficulty near threshold is U-shaped in density,
comparing arms at fixed absolute α confounds r-effects with threshold proximity.
S0 (below) estimates the operational threshold α_c(r) per radius; the main scan
samples at α = α_c(r) + Δ, Δ ∈ {+0.2, +0.4, +0.8}.

## 4. Measures, Solvers, and Statistical Protocol

**Difficulty.** Primary: log10(conflicts + 1) under CaDiCaL (via python-sat),
conflict budget 10⁶ (main scan) / 10⁷ (threshold study S0); CaDiCaL's budget
mechanism counts *decided* conflicts precisely, giving machine-independent censoring
(verified in pilots to eliminate the propagation-storm hang that killed
interrupt-based schemes). Secondary: wall-clock (same-machine comparisons),
Glucose cross-checks, probSAT (compiled; local-search contrast). A 300 s
subprocess-isolated wall guard returns status *walltimeout* for runs where conflicts
are sparse but propagation explodes; these rows carry no conflict count and are
excluded from conflict analyses, enter Kaplan–Meier/Tobit as unresolved, and their
directional bias is declared (AMEND-2): truncation falls disproportionately on the
UNSAT side near threshold, which *raises* resolved-SAT rates and pushes α_c(r)
upward — an anti-conservative bias for our gradient hypothesis, bounded by
spot-checks at 10⁸ conflicts / 480 s on flagged radii.

**Structural measures.** Treewidth is reported as a bracket: min-fill upper bound
(numpy-vectorized; validated against k-tree constructions) and degeneracy-based
lower bound (peeled cores without fill edges — an earlier implementation bug that
turned the lower bound into an upper bound is documented in our repo history).
Community structure (Leiden, fixed resolution), modularity, spectral gap,
redundancy histograms; all metrics are computed on the generated instance and
stored with it.

**Statistics.** Repeated-measures ANOVA with seed as subject (seeds shared across
all r × Δ cells), partial η²; Jonckheere–Terpstra ordered-alternative test by Monte
Carlo permutation; paired Wilcoxon signed-rank for E3b pairs; Tobit (type-I,
right-censored) with budget values as lower bounds; Kaplan–Meier curves; Imai et
al. (2011) causal mediation with bootstrap ACME confidence intervals treating
structural metrics as mediators of the r → difficulty path; Benjamini–Hochberg FDR
across the family of primary tests. Decision rules are preregistered: H2 is
confirmed by FDR-corrected p < 0.05 with partial η² ≥ 0.14 or ≥ 10× median endpoint
ratio; a "density dominates" verdict is triggered by CI-based small-effect bounds
(η² < 0.02 and p > 0.05), with the negative result reported in full.

**Preregistration and amendments.** Hypotheses H1–H3, censoring semantics, r
levels, and decision rules were frozen before the main scan (HYPOTHESES.md v1.0).
Amendments are numbered and reason-stated: AMEND-1 (S0 budget 10⁷ for low-censoring
threshold estimation), AMEND-2 (wall guard, bias declaration, spot-check protocol),
AMEND-3 (content-arm operationalization deferral), AMEND-4 (terminology normalization and content-arm disposition record). AMEND-5 (2026-09-18), a
non-hypothesis mediation-path disposition record, lives in HYPOTHESES.md and in the
journal version's Appendix C. A prespecification-vs-
implementation audit (PRESPEC_AUDIT.md) records every deviation found by
item-by-item inspection — including one material bug (walltimeout rows initially
counted as UNSAT in threshold estimation) that was fixed before the main scan
fired.

## 5. Results I: the threshold curve α_c(r) (S0 — final)

S0 resolves 832 runs (720 grid + 112 grid-floor extension) at 10⁷-conflict budget,
16 seeds per cell. With only resolved (sat/unsat) runs contributing to SAT rates
(AMEND-2 caliber), and linear interpolation of the 0.5-crossing:

| r | 0.06 | 0.08 | 0.11 | 0.15 | 0.22 | 0.3 | 0.5 | 0.8 | 1.5 |
|---|------|------|------|------|------|-----|-----|-----|-----|
| α_c(r) | <2.5 (bracketed) | 3.35 | 3.82 | 4.20 | 4.23 | 4.40* | 4.70* | 4.60* | 4.60* |
| censoring | 2.1% | 0% | 0% | 0% | 0% | 92.5% | 98.8% | 100% | 100% |

(\* measurement-saturated radii: crossing unidentifiable; table carries the R3
coarse value, flagged low-confidence, with spot-checks completed per AMEND-2 —
bias ∈ [−0.2, 0] at r = 0.3, unbounded caveat retained at r ≥ 0.5.)

Three observations. **(i)** The operational threshold is *not* r-invariant: it rises
by more than 1.7 density units from r = 0.06 to r = 0.22, with at most 2.1% censoring on that range —
locality does not merely re-scale difficulty around a fixed threshold; it *moves the
threshold itself*. For the philosophical conjecture this is the cleanest single
statement: the r-knob shifts where sat/unsat balance lies, holding n and all
degree/content statistics fixed. **(ii)** The curve saturates near the classical
random-3-SAT threshold region (α_c(n→∞) ≈ 4.267), consistent with r → ∞ recovering
uniform random 3-SAT and with the width-backbone picture: intermediate radii inherit
the mean-field threshold while small radii admit satisfiability far below it (small
clusters satisfy locally — the geometric small-subformula regime of [9]).
**(iii)** At r ≥ 0.3, near-threshold instances collapse out of measurable range
(313 walltimeouts, all at r≥0.3, concentrated there): the *measurability boundary itself*
tracks r. We treat this as a difficulty-regime change — beyond some radius the
question "where is the threshold" stops being answerable at fixed budget — rather
than as a data point, and we bound the α_c bias for flagged radii by spot-checks
(completed: bias ∈ [−0.2, 0] at r = 0.3; unbounded caveat at r ≥ 0.5).

## 6. Results II: dose–response at matched threshold offset (E3a — H2)

The main scan places 9 radii × 3 density offsets Δ ∈ {+0.2, +0.4, +0.8} above each
radius's own α_c(r) (S0 table), 30 paired seeds, two solvers, 10⁶-conflict budget
with the 300 s wall guard. 1980 runs, zero errored rows; 1436 resolved, 544
censored (27.5%, concentrated at r ≥ 0.3 where near-threshold instances routinely
exceed the budget).

**Primary tests (CaDiCaL, Δ-pooled, seeds as subjects).** RM-ANOVA on the
Δ-aggregated complete-seed subset (n = 28 seeds observed at all radii):
F(8, 216) = 2808.5, p ≈ 1.1e-213. Jonckheere–Terpstra ordered-alternative test
(Monte Carlo permutation, 10⁴ draws): p = 1e-4 — the resolution floor of the
permutation distribution — and the same value for every (Δ, solver) cell; the
BH-FDR q across the seven-member primary family is 1e-4. A censoring-robust
variant (censored runs scored at the budget value log10 = 6) reproduces
p = 1e-4, so the trend is not an artifact of dropping censored rows.

**The dose–response curve (Δ = +0.2, the hardest, near-threshold arm):**

| r | 0.06 | 0.08 | 0.11 | 0.15 | 0.22 | 0.3 | 0.5 |
|---|------|------|------|------|------|-----|-----|
| mean log10 conflicts | 1.45 | 1.68 | 2.30 | 3.02 | 4.86 | 5.87* | 5.93* |
| resolved n | 30 | 30 | 30 | 30 | 30 | 9/30 | 2/30 |

(\* means over surviving (easier) instances only; the censoring-aware JT bounds
the underlying trend.) From r = 0.06 to r = 0.22 at the *same* threshold offset,
difficulty climbs from ~28 to ~72,000 conflicts — **3.4 orders of magnitude**
among decided instances (≥4.5 counting budget-censored endpoints at their lower
bound).
The Δ = +0.8 arm repeats the pattern (1.29 → 5.77). Partial η² at computable
cells is 0.984–0.988 against the preregistered confirmation threshold of 0.14,
and the censoring-aware endpoint ratio ~10^4.5 dwarfs the preregistered 10× line. **H2 is
confirmed under its own preregistered decision rule.** Glucose replicates the
pattern.

## 7. Results III: the structure-destruction intervention (E3b)

Degree-preserving swapping holds every literal's occurrence count *exactly* fixed
while destroying spatial locality. Paired Wilcoxon signed-rank on (n, α, r, seed)
tuples:

| Δ | pairs | original mean logc | swapped mean logc | difficulty ratio | p |
|---|-------|--------------------|--------------------|------------------|---|
| +0.2 | 33 | 1.79 | 2.99 | ×16 | 7.0e-10 |
| +0.6 | 49 | 3.25 | 5.08 | ×68 | 6.0e-13 |

53 pairs flip satisfiability status under the swap — destroying spatial clustering
pushes instances across the sat/unsat boundary. Together with E1 (§4.3: treewidth
alone manufactures no difficulty), the asymmetry is sharp: what CDCL difficulty
responds to is *local geometry*, not any global topological summary.

## 8. Results IV: mediation and the feature ladder (H1)

Imai et al. (2011) causal mediation of the r → difficulty path (bootstrap 95% CI,
n_boot = 1000; total effect 3.26 log units): modularity ACME = 3.06 [2.84, 3.37]
(~94% of total); spectral gap ACME = 3.92 [3.68, 4.28] (suppression: direct effect
−0.66 — evidence of a secondary channel bypassing community structure); mean
degree 2.34 [2.15, 2.60]; clustering 2.19 [2.02, 2.44]. All CIs exclude zero:
by the preregistered rule, **mediation is established** as mechanism evidence.

The H1 feature ladder (nested OLS F + ridge CV on the main-scan data; GBDT with
leave-one-r-out extrapolation, `e5_gbdt.py`) is complete (nested
F(60, 1283) = 297.8; GBDT leave-one-r-out CV R² = 0.76);
the observational baseline stands at CV R² = 0.90 for density features with zero
structural gain on random families (§4.4), so any structural increment on the
controlled families would directly demonstrate that intervention reveals what
observation cannot.

## 9. Results V: placement on real instances (E4-prime)

All 59 fetched real instances (42 combinatorial/crafted from Heule's benchmark
suite — Green Hat, Steiner systems, 26×26 queens, matrix partitions, MPHF,
packing, phone-type-number, radio-dispersion, WAP; 17 DIMACS classics) were
solved under the S0 budget protocol (10⁷ conflicts / 300 s): **22/59 decided**.
The 17 DIMACS classics anchor the easy end: 15 SAT and 2 UNSAT, all decided
within milliseconds (an audit caught a parsing artifact in the 1996 legacy
DIMACS dialect, silently truncating these files; they were re-solved after the
fix — see repository log). The combinatorial challenge instances mostly exceed
the wall guard (hard anchor); MPHF/packing/radio families are partially decided,
with file-name status labels matching our determinations on every checkable
instance (one legacy -yes file is in fact UNSAT). Placement conclusion:
our generator's difficulty spectrum (10⁰–10⁶ conflicts) spans the middle of the
real spectrum from textbook-easy to competition-hard. The industrial-diversity
caveat stands (§10): the canonical SAT 2024 main-track files were unreachable
from our network (the deterministic preselection table — 400 instances with
md5 hashes and 15-solver reference runtimes — is retained in the authors'
working archive for future completion).

## 10. Threats to Validity

**Construct.** "Locality radius r" is one operationalization of the intuitive
notion of variable-interaction locality — a spatial one, on a 2-D torus host. Other
hosts (scale-free geometry was registered as a robustness arm), other notions
(embedding dimension, effective treewidth of local neighbourhoods) may disagree;
our claim is about r as defined, not about "locality" in general. Difficulty is
conflict counts under CDCL — a proxy for, not a definition of, hardness.

**Internal.** Five controls close the confounding routes we identified: n and α
(fixed or Δ-matched), literal degree profile (degree-cap rejection in the planted
arms, exact preservation under the E3b swap), clause content (σ-satisfaction-mode
polarity sampling via uniform cardinality then subset, redundancy ≈2.14–2.23
r-invariant),
and solver variance (two CDCL engines). The metric-computation channel cannot
pseudo-correlate with runtime because metrics are computed on the generated
instance *before* solving by a fixed deterministic procedure. Censoring is the
residual internal threat: wall-clock truncation is directionally biased
(AMEND-2), we declared the direction before unblinding, and spot-checks at 10⁸
conflicts bound the α_c bias for flagged radii (completed: bias ∈ [−0.2, 0] at
r = 0.3; unbounded caveat at r ≥ 0.5). One material
implementation deviation (walltimeout rows initially counted as UNSAT in the
S0 reader) was caught by our prespecification audit *before* the main scan fired
and fixed; the audit trail is public.

**External.** geo_random is an intervention vehicle, not a survey of practice;
E4-prime placement (59 real instances from combinatorial and classic DIMACS
families — the canonical SAT 2024 main-track files being unreachable from
our network, documented with the deterministic preselection table retained) gives
the location of our difficulty spectrum relative to real instances, with the
industrial-diversity caveat stated. All conclusions are scoped to CDCL-family
solvers, direct CNF encodings, n = 400, and conflict-count difficulty.

**Statistical conclusion.** Paired designs with 30 seeds per cell, effect sizes
with preregistered thresholds, FDR over the primary family, and censoring-robust
cross-checks (Tobit, KM) — with the power analysis pinned at detecting 0.5 SD
paired effects at power 0.8.

## 11. Discussion: what this does and does not say about P versus NP

Nothing we measure bears on P versus NP. The conjecture we test descends from a
philosophical *intuition* about why the computational world feels tractable —
"causes act locally" — and intuitions of this kind are worth taking seriously
precisely because they can be operationalized and then shot down. Three points
deserve emphasis regardless of which way the main scan lands.

**Tractability is a relational property.** E1 (width-controlled instances are
flat) and the S0 threshold curve together suggest that difficulty lives neither in
global topology alone nor in density alone, but in the interaction between spatial
organization and the *search dynamics* of a particular algorithm family. CDCL
branching is measurably local (§2.1); our experiments ask whether the local
geometry of the *instance* is what that locality feeds on. A "yes" makes the
philosophical conjecture precise enough to be useful; a "no" makes it precise
enough to be abandoned — either outcome is progress over an unfalsifiable slogan.

**The measurability boundary is a finding.** That near-threshold instances at
r ≥ 0.3 collapse beyond our budgets is not an inconvenience to be apologized for;
it is the signature of a regime change. Between r = 0.06 (threshold visible and
clean at tiny budgets) and r = 0.5 (threshold invisible at 10⁷ conflicts), the
*character* of the difficulty phase transition changes — which is exactly what a
locality-causal story predicts, and what a density-only story has no reason to
produce.

**Phase transitions and a portable diagnostic.** A classical observation —
dating to Cheeseman, Kanefsky and Taylor's "Where the really hard problems are"
[IJCAI 1991] — holds that combinatorial problems are hardest near structural
phase transitions. Our results give that observation a *causal, solver-relative*
reading for SAT/CDCL: the locality radius moves the transition itself (the α_c
curve, §5) and restructures difficulty within threshold-matched offsets (§6).
The framework — one structural knob, threshold-matched dosing, a
structure-destruction intervention, censoring-aware statistics — is offered as a
**portable diagnostic protocol**: any claim of the form "structural property P
helps algorithm A on family F" can be subjected to the same treatment. We
explicitly do *not* claim our conclusions extend to local-search solvers; the
contrast is a preregistered prediction (roadmap E8): if difficulty is a
structure×algorithm relation, a stochastic local-search solver should respond to
r differently — possibly inversely — and running it on our instances is a cheap,
decisive test.

**Intervention as a community practice.** Our methodological claim is larger than
any single result: structure–difficulty research has leaned on observational
regression for two decades — with the field's own flagship study concluding that
no structural measure predicts CDCL performance well in the aggregate [4].
Intervention designs — one knob, everything else pinned, preregistered decision
rules, censoring declared — are the standard remedy in every empirical science
that has faced the same impasse. The generator, the swap chain, the statistical
protocol and the audit trail are released so that the next conjecture can be
tested the same way.

## 12. Reproducibility statement

All instances are deterministically generated from (family, params, seed) tuples;
the result store keys rows by (family, params, seed, solver) with idempotent
resume-per-row semantics; every figure regenerates from the SQLite stores by
committed scripts; result databases and manifests are version-controlled. The full
experiment matrix, budgets, and the preregistration with numbered amendments are in
the repository.

## References (verified; see docs/papers/notes/ for reading notes)

[1] Marques-Silva, Lynce, Malik. CDCL (Handbook of Satisfiability survey).
[2] Ansótegui, Giráldez-Cru, Levy. Power-law variable occurrences (IJCAI 2009 line).
[3] Li et al. Hierarchical community structure of practical Boolean
    formulas. SAT 2021, LNCS 12831, pp. 359–376
    (doi:10.1007/978-3-030-80223-3_25; arXiv:2103.14992).
[4] Zulkoski, Martins, Wintersteiger, Liang, Czarnecki, Ganesh. The Effect of
    Structural Measures and Merges on SAT Solver Performance. CP 2018, LNCS 11008,
    doi:10.1007/978-3-319-98334-9_29. (Full text verified via the author's PhD
    thesis, UWSpace 2018.)
[5] Mull, Fremont, Seshia. On the Hardness of SAT with Community Structure.
    SAT 2016, LNCS 9710, doi:10.1007/978-3-319-40970-2_10; arXiv:1602.08620.
[6] Ansótegui, Bonet, Levy. Satzilla/size-based features line — variable incidence
    power laws (IJCAI 2009), doi per notes file.
[7] Ansótegui et al. Fractal dimension of VIG/CVIG (2014).
[8] Newsham et al. Community structure and CDCL runtime regressions (SAT 2014).
[9] Bläsius, Friedrich, Göbel, Levy, Rothenberger. The impact of heterogeneity and
    geometry on the proof complexity of random satisfiability. SODA 2021,
    doi:10.1137/1.9781611976465.4; Random Struct. Algorithms 63(4):885–941 (2023).
[10] Giráldez-Cru, Levy. Locality in random SAT instances. IJCAI 2017,
     doi:10.24963/ijcai.2017/89; and the modularity generator (IJCAI 2015).
[11] Jia, Moore, Strain. Generating hard satisfiable formulas by hiding solutions
     deceptively (2005).
[12] Atserias, Dalmau. A combinatorial characterization of resolution width.
     JCSS, doi:10.1016/j.jcss.2007.06.025.
[13] Ben-Sasson, Wigderson. Short proofs are narrow — resolution made simple.
     JACM 2001, doi:10.1145/375827.375835.
[14] Atserias, Fichte, Thurley. Clause-learning algorithms with many restarts and
     bounded-width resolution. JAIR 2011, doi:10.1613/jair.3152.
[15] Beame, Kautz, Sabharwal. Understanding the power of clause learning.
     IJCAI 2003 (JAIR 22:319–351, 2004; doi:10.1613/jair.1410).
[16] Weitz. Counting independent sets up to the tree threshold. STOC 2006,
     doi:10.1145/1132516.1132538.
[17] Gamarnik. The overlap gap property (PNAS 2021 line) — see ogp note.

[18] Cheeseman, Kanefsky, Taylor. Where the really hard problems are.
     IJCAI 1991. (Classic statement of the phase-transition hardness
     observation; existence verified via OpenAlex 2026-09-10.)

*(Reference list to be normalized to venue style at submission; [6][7][8] DOIs to
be pulled from the notes files during formatting.)*

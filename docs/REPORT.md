# Does the "Locality Radius" of Variable Interactions Causally Determine SAT Solving Difficulty?
## — An Intervention-Based Empirical Study (Chinese In-Depth Report · M3 Draft)

> **Status marker**: v1.0 (2026-09-10) — all experiments (S0/E1/E2/E3a/E3b/E4/E5/E6) are
> complete and filled in with numbers; frozen content in §1–§4 is governed by HYPOTHESES
> v1.0-FROZEN + AMEND-1/2/3 + PRESPEC_AUDIT; the data and the decision chain are entirely
> in git history.
> This report is aimed at non-technical readers; technical details are carried in gray
> boxes/footnotes, and the "philosophical extensions" are concentrated in §12 and strictly
> separated from the empirical conclusions.

---

## 0. A Three-Sentence Guide (for Non-Technical Readers)

1. A widely circulated philosophical conjecture holds: **"causally, satisfiability problems
   from the physical world are easy to solve because 'causes' act locally"** — if the
   interactions between variables occur only within small nearby ranges, solvers find
   the problem easy; if the interactions span large ranges, the problem is hard.
2. Until now this conjecture had only **observational evidence** (real instances do
   carry local structure, and they are indeed easy to solve), but observational evidence
   cannot rule out confounding: real instances simultaneously carry many other good
   properties.
3. We built a **"structure-intervention machine"**: holding every statistical property of
   the problem fixed, we turn the single knob of the "locality radius r" and directly
   measure how solving difficulty changes. **Main result: the conjecture holds (within
   the scope of this experiment)** — turning r alone moves the satisfiability threshold
   by ≥1.7 density units, and difficulty among decided instances spans 3.4 orders of
   magnitude (≥4.5 as the censoring-aware lower bound; JT p≤10⁻⁴);
   destroying only the spatial entanglement while preserving the degree distribution
   raises difficulty by 16–68×.

---

## 1. Research Question: From Philosophical Conjecture to Falsifiable Experiment (Frozen)

### 1.1 Diagnosis of the Original Conjecture
The original conversation proposed "causation knows no absolute strong correlation": if no
strong long-range correlation exists among the variables of a combinatorial problem, the
problem will not be too hard. In its original form the conjecture is unfalsifiable —
"correlation", "locality", and "causation" are all unoperationalized. We translate it
into three testable propositions:

- **P1 (structural proposition)**: SAT instances possess a measurable
  "variable-interaction locality", continuously tunable through the parameter r (the
  generator parameter under which clause variables are sampled only within an r-ball on
  the 2-D torus host);
- **P2 (causal proposition)**: holding scale n, density α, the literal degree
  distribution, the clause-content distribution, and σ-satisfaction redundancy all
  unchanged, changing r alone systematically changes CDCL solving difficulty (conflict
  counts, across orders of magnitude) — a causal effect under the **interventional**
  definition;
- **P3 (mechanism proposition)**: the effect of r is mediated by the local dynamics of
  CDCL search (branching/learning hugging communities and clusters), not by density or
  treewidth.

### 1.2 Why Nobody Had Done This Experiment Before (Dedicated Collision-Check Findings, M0-3)
- Giráldez-Cru & Levy have locality generators (IJCAI 2017 power-law/CA models) — but
  these are **generative distributions**, not **single-parameter interventions**; and
  the CA model was proven by Mull-Fremont-Seshia (SAT 2016) to be w.h.p. exponentially
  hard when communities are few — that is, the model's "locality" does not produce
  "tractability".
- Zulkoski et al. (CP 2018), Chapter 5, did the closest thing: **structure-preserving
  interventions on mergeability (the content channel)** — proving the feasibility of the
  interventional paradigm, but without intervening on the topological channel (r).
- Bläsius et al. (SODA 2021) give theorem-level "locality ⇒ tractability" evidence, but
  their conclusion is existential (the geometric model admits small UNSAT subformulas),
  without a difficulty curve swept over r.
- **The novelty therefore narrows to**: the first empirical study to run a controlled
  intervention scan over the locality radius r and to orthogonally decompose the
  topological channel from the content channel (2×2). (HYPOTHESES v1.0 frozen record,
  item 3)

### 1.3 Hypotheses (Preregistered, Frozen)
- **H1** (scoped to the CDCL family): after controlling for density and scale, a
  combination of structural indicators explains significantly more variance in solving
  time than a single density indicator.
- **H2**: with n, α, the literal degree distribution, the clause-content distribution,
  and σ-satisfaction redundancy all controlled, varying r alone still produces a
  significant causal effect (paired + factorial design).
- **H3** (exploratory): the quality of LLM branch ordering improves as locality
  strengthens.
- **Negative-result adjudication** (quantified, frozen): if, in the 2×2 factorial, the
  confidence intervals of both the r main effect and the r×density interaction fall
  within the small-effect boundary (or p>0.05 with a negligible effect size) → adjudicate
  "density dominates", and the negative result enters the report.

---

## 2. Theoretical Spine (Convergent Conclusions from Eight Close-Reading Notes; Details in docs/papers/notes/)

### 2.1 Tractable Direction: Low Treewidth ⇒ Low Width ⇒ Polynomial CDCL (the Theorem-Level Explanation for E1)
Atserias–Dalmau (JCSS 2008) give the combinatorial characterization of resolution
width, implying w(F⊢⊥) ≥ treewidth; Ben-Sasson–Wigderson (JACM 2001) give the
size–width relation S ≥ exp(Ω((w−w₀)²/n)); Atserias–Fichte–Thurley (JAIR 2011) +
Beame–Kautz–Sabharwal (IJCAI 2003) establish the simulation relation between CDCL and
(bounded-width) resolution. Merged: **tw ≤ k ⇒ a width-O(k) refutation exists ⇒ a
polynomial-size proof exists ⇒ CDCL with restarts finds it in polynomial time**.
Substituting into the width barrier: w=√n ⇒ non-binding; w=n^0.6 ⇒ superpolynomial;
w=Θ(n) ⇒ exponential. (Note: width_decay_barrier.md)

### 2.2 Hardness Direction: The Combined Force of the Geometric Sweet Spot and the Width Barrier (Interpretive Framework for E2/E3a)
In the random 3-SAT threshold region, resolution width is Θ(n) w.h.p. ⇒ exponential
(B-W); in the 2-D geometric model, width ~√n **does not suffice** to trigger the
barrier, while Bläsius et al. (SODA 2021) prove that geometric locality ⇒ small UNSAT
subformulas exist that are discoverable in polynomial time ⇒ CDCL is fast. The two
theoretical tools concur in predicting tractability at "small r" and hardness at r→∞ —
precisely the dose–response skeleton E3a wanted. (Notes: blasius2023_geometry.md,
ogp_phase_transitions.md)

### 2.3 Upper Bounds on the Explanatory Power of Structural Measures (H1's Two Pincers)
- Worst case: Mull-Fremont-Seshia prove that any PCM-type community metric (including
  modularity) admits instances scored as "well-structured" that remain NP-hard — no
  single indicator can be a tractability certificate;
- Empirical case: Zulkoski et al. (CP 2018), on ~7000 competition instances: the best
  combination of structural features reaches only adjusted R² ≈0.31 on application
  instances, TW features only 0.05, with signs flipping across categories.
- **The question left for us**: after observational correlation has been capped, can an
  interventional design still measure the causal effect of r? (This is the division of
  labor between H1 and H2: H1 governs "explanation", H2 governs "intervention".)

### 2.4 CDCL Local Dynamics (Evidence for the P3 Mechanism Proposition)
Zulkoski Ch. 4: VSIDS/LRB branching decisions track VIG communities with Gini
coefficient 0.50–0.52 (random branching 0.16); temporal locality 45–55% vs 12%. Mull et
al. Fig. 1: **community size (not formula size) dominates runtime** — an observational
precedent for "the local working set determines difficulty"; we upgrade the observation
to an intervention. (Notes: zulkoski2018_structural.md, mull2016_community_hardness.md)

### 2.5 OGP and Correlation Decay (Constraints on the Long-Range Regime)
OGP (Gamarnik et al.) delineates the obstacles to local algorithms and stability in
high-dimensional/fully connected regimes; Weitz's (STOC 2006) correlation decay gives
positive algorithmic results when local information suffices. Mapped onto r: small r ⇒
akin to low-dimensional geometric models (decay/small-cluster regime), large r ⇒ akin to
mean-field (OGP regime). **Note**: this report does not claim that CDCL is a local
algorithm — the mapping is used only to partition regimes, not to prove solver behavior.
(Note: ogp_phase_transitions.md)

---

## 3. Methods (Frozen: HYPOTHESES v1.0 + AMEND-1/2/3)

### 3.1 Generators (src/cvh/generators.py)
- **geo_random(r)**: variables are sampled uniformly within an r-ball on the 2-D torus
  host and combined into 3-clauses, non-planted (planted=False); this is the main
  difficulty carrier (R1/R2 found the planted families trivial for CDCL).
- **tw_controlled(k)**: a k-tree skeleton, constructively guaranteeing treewidth ≤ k
  (used by E1).
- **σ-preserving polarity resampling**: σ-satisfaction-mode sampling + β-decoy
  constraint filling; content statistics are r-invariant by construction (pilots
  verified identical histograms across r; measured mean σ-redundancy ≈2.14–2.23,
  r-invariant). [2026-09-11 erratum] The earlier text's "constant 12/7" was wrong —
  12/7 is only the expected number of σ-satisfying positions under pure uniform-7
  sampling, not the redundancy caliber of this construction.
- **degree_preserving_randomize** (E3b): a bipartite swap chain that exactly preserves
  the literal degree sequence while destroying spatial locality — the
  "structure-destruction intervention".
- **2×2 factorial**: topology (preserved/destroyed) × content (original/resampled).

### 3.2 Measurements
- Primary difficulty measure: conflict count (log10(conflicts+1)); censoring: conflict
  budget (S0=10⁷, main scan=10⁶) + a 300s wall-clock guard (AMEND-2: pathological
  propagation-explosion cells, anti-conservative bias declared).
- Solvers: CaDiCaL (primary) + Glucose (robustness); subprocess isolation +
  conflict-budget truncation (infrastructure history in M2_LOG: interrupt deadlock →
  budget truncation → spawn isolation).
- Structural metrics (src/cvh/metrics.py): treewidth via a min-fill upper bound + a
  degeneracy lower bound (presented as a bracket; k serves as the upper bound on
  constructed families); communities (Leiden, fixed resolution); spectral gap;
  modularity; σ-redundancy histograms.

### 3.3 Statistics (src/cvh/analysis.py)
Tobit regression (self-implemented, handling censoring), Kaplan–Meier,
repeated-measures ANOVA, Jonckheere–Terpstra Monte Carlo permutation, paired Wilcoxon,
Imai et al. (2011) causal mediation (ACME bootstrap CI), Benjamini–Hochberg FDR.
Power: paired design at 0.5 SD / power 0.8.

---

## 4. Pilot and Control Experiment Results (Completed: R1–R3b, E1, E2)

### 4.1 R1/R2: Planted Constructions Are Trivial for CDCL (Difficulty-Carrier Erratum)
planted/JMS-style constructions yield all-zero conflicts for modern CDCL below the
planting threshold. **Erratum record**: our initial statement "JMS is trivial for modern
CDCL" went beyond the evidence — our implementation (decoy β/p_flip) is not the
original construction; it has been changed to "our planted variant is trivial".
(PILOT_FINDINGS.md)

### 4.2 R3b: Six-Order-of-Magnitude Signal + End-to-End Validation of the Statistical Pipeline
geo_random spans ~10⁶ in conflict counts over n=400, α∈[3.0,4.6], r∈[0.06,1.5];
RM-ANOVA F=1284 (p≈6e-69); JT trend test p≈2e-4; mediation ACME=2.14 (83% of the total
effect). (results/pilot_m1_r3b.db, figures/fig_r3b_moneyplot.png). [2026-09-12 caliber
note] The numbers in this section are preregistration-period session pipeline-validation
computations (no committed analysis script); blind-review recomputation under the
main-study specification could not reproduce them (the F magnitude matches; the
mediation-share caliber differs) — R3b is a pilot record superseded by the main study;
the main conclusions follow the committed pipeline of §5–§9.

### 4.3 E1: Treewidth Alone Does Not Produce Hardness (the "Negative" Half of the Structural Proposition)
The tw_controlled unplanted arm shows median conflict counts of 7–10, essentially
unchanged, across the six levels k∈{3,5,8,12,16,20} (the additional size tiers n=300 and
n=600 show the same pattern; the main battlefields S0/E3a/E2 are all n=400), consistent
with the theorem chain of §2.1 (low treewidth ⇒ narrow proofs ⇒ CDCL-easy); the planted
control arm is an all-zero plateau. **Treewidth by itself is not a sufficient source of
CDCL hardness ("good structure" is only one-way insurance for tractability)** — this
pushes the search space for the source of hardness from "global topology" toward "local
interaction structure" (the candidate channel for r). (M2_LOG c6879b0; data
results/m2_e1e2.db)

### 4.4 E2: Reproduction of the Textbook Phase-Transition Curve (Anchor)
Random 3-SAT α sweep (n=400): easy-hard-easy, with decided difficulty peaking at
α≈4.2–4.26 and then entering a censoring plateau (budget-capped at α≳4.4), consistent
with the classical threshold 4.267 (n→∞); the r=∞ anchor coincides with the difficulty
curve of independently generated random instances (anti-leakage protocol).
**Censoring-caliber warning**: in the near-threshold cells (α=4.2–4.4), the SAT share
of resolved rows is inflated by truncation (the UNSAT side is harder to decide) — the
directional bias declared under AMEND-2 is visible in E2 as well, so E2 serves only as a
qualitative anchor (peak position) and is not used for numerical threshold estimation
(threshold estimation is borne by S0 with its higher censoring budget). (M2_LOG
c6879b0)

---

## 5. S0: Precise Measurement of α_c(r) [Final Table]

All 720 S0 jobs are decided (0 errored rows) + 112 grid-floor extension rows at r=0.06
(revealing that the threshold reaches the original grid floor rather than lying near
2.9; the extension's clean crossing at 2.60 is a historical S0-stage value [2026-09-11
caliber correction]; from 2026-09-10 the final caliber is α_c(0.06)=<2.5 (bracketed) —
see the table below and Table 1 of the paper). Caliber: AMEND-2-compatible — only
resolved cells (sat/unsat) are counted, and wall-clock-truncated rows do not
participate; cells with decision rates <60% on both sides of the crossing are flagged
low-confidence.

| r | 0.06 | 0.08 | 0.11 | 0.15 | 0.22 | 0.3 | 0.5 | 0.8 | 1.5 |
|---|---|---|---|---|---|---|---|---|---|
| α_c | **<2.5†** | 3.35 | 3.82 | 4.20 | 4.23 | 4.40* | 4.70* | 4.60* | 4.60* |
| censoring rate | 2.1% | 0% | 0% | 0% | 0% | 92.5% | 98.8% | 100% | 100% |

(* = measurement saturation: the R3 coarse value is carried, flagged low-confidence,
and placed in the spot-check queue; the non-monotonicity among the coarse values (4.70
at 0.5 > 4.60 at 0.8) is precisely a manifestation of the low confidence — they take
part in no monotonicity reading and serve only as α placeholders for the large-r arm)

**Three findings**:
1. **The threshold is not r-invariant**: at r=0.06 the SAT rate declines from ~0.31 to
   ~0.13 over α∈[2.5,3.1] (the boundary is bracketed below 2.5, not pinpointed;
   censoring 2.1%); by r=0.22 it has already risen past 4.2 — **a displacement of at
   least 1.7 density units**. "Locality" does not merely rearrange difficulty around a
   fixed threshold — it **moves the threshold itself**. For the philosophical conjecture
   this is the cleanest single statement: with n, the degree distribution, and the
   content distribution all pinned down, turning r alone moves the
   satisfiable/unsatisfiable dividing line.
2. **The curve saturates near the classical value**: at r≥0.15, α_c is already close to
   the classical random 3-SAT threshold region (4.267 as n→∞), consistent with "r→∞
   degenerates to uniform random 3-SAT" and with the width-barrier regime map.
3. **The measurability boundary itself moves with r**: near-threshold instances at
   r≥0.3 are almost all undecidable within 10⁷ conflicts / 300s (the 313
   wall-clock-truncated rows concentrate here). We treat this as evidence of a
   "difficulty-regime change" rather than as a data point: beyond a certain range of the
   radius, the question "where is the threshold" loses answerability at fixed budget.
   The bias direction is declared (AMEND-2: censoring falls on the UNSAT side → α_c is
   systematically overestimated → anti-conservative for H2), and it has been
   empirically bounded by 10⁸-budget spot-checks (r=0.3 bias ∈[−0.2,0]; the r≥0.5
   boundary is robust) — see §11.3 for details.

Data and figures: results/s0_alpha_c.json, figures/fig_s0_alphac.png. The implementation
deviation fixed before ignition (walltimeout rows had been counted into the UNSAT
bucket) is documented in PRESPEC_AUDIT.md.

## 6. E3a: r×Δ Dose–Response [Main Result: H2 Confirmed]

Design: 9 r × 3 Δ{+0.2,+0.4,+0.8} × 30 seeds × {CaDiCaL, Glucose}, α = α_c(r)+Δ (S0
table), 10⁶ conflict budget + 300s guard. 1980 rows actually completed (0 errored rows;
120 original-arm E3b jobs idempotently merged with E3a under the same keys), 1436
resolved, 544 censored (27.5%, concentrated at r≥0.3).

**Primary tests (CaDiCaL, all Δ pooled, seeds paired)**:
- RM-ANOVA (complete-seed subset after Δ aggregation, n=28): **F(8,216)=2808.5,
  p≈1.1e-213**;
- Jonckheere–Terpstra trend (ordered alternative in r, Monte Carlo permutation with 10⁴
  draws): every primary test's p reaches the resolution floor of the permutation
  distribution (p≤10⁻⁴, no finer value possible with 10⁴ permutations), and after
  **BH-FDR, q≤10⁻⁴** (the 7 members of the primary-test family share the same value);
  the censoring-sensitive caliber (censored runs counted at the budget cap) gives the
  same p.

**Dose–response curve (Δ=+0.2, i.e., 0.2 above the threshold — the phase-transition
region; log10 conflicts)**:

| r | 0.06 | 0.08 | 0.11 | 0.15 | 0.22 | 0.3 | 0.5 |
|---|---|---|---|---|---|---|---|
| mean logc | 1.45 | 1.68 | 2.30 | 3.02 | 4.86 | 5.87* | 5.93* |
| (≈ conflicts, converted from the logc row above) | 28 | 48 | 199 | 1,047 | 72,400 | 741,000* | 850,000* |
| resolved n | 30 | 30 | 30 | 30 | 30 | 9/30 | 2/30 |

(* With few resolved instances, the means represent only "the easier instances that
survived to decision"; the true difficulty is higher — the censoring-sensitive-caliber
JT bound (censored runs counted at the budget cap of 10⁶) still gives p=1e-4, and the
trend is robust under censoring. The Δ=+0.8 arm likewise spans 4.5 orders of magnitude,
1.29→5.77, saturating into the budget band at r≥0.8. **Caliber note**: the "4.5 orders
of magnitude" in §0 and the abstract refers to the censoring-aware lower bound
(1.45→6.0) or to the Δ+0.8-arm endpoints (1.29→5.77); the Δ+0.2-arm span among decided
instances is 3.4.)

**Effect sizes vs the preregistered confirmation line**: partial η² = **0.984–0.988**
(taken from the Δ=+0.6/+0.8 cells — their complete-seed subsets with n≥17 include
large-r levels; the Δ=+0.2/+0.4 cells cannot be computed because heavy large-r
censoring leaves too few complete seeds, and the trend in those two cells is carried by
the dual-caliber JT) (preregistered line 0.14, exceeded 7-fold); the endpoint median
ratio ≈ **10^4.5×** (preregistered line 10×).
**H2 is confirmed under its preregistered decision rule**: with n, α (matched relative
to each radius's own threshold), the literal degree distribution, the content
distribution, and redundancy all controlled, variation of the locality radius r alone
swings CDCL difficulty across more than **4.5 orders of magnitude**. Glucose
cross-validation shows the same pattern (JT p=1e-4).

**The relation between Δ semantics and the α_c bias**: the α_c of low-confidence radii
(0.3–1.5, see §5) carries an already-bounded bias (§11), so the actual difficulty
offset of their Δ cells differs from the nominal value; but this affects only the
precise horizontal placement of the large-r cells, not the controlled comparison
structure of "across Δ within the same r, across r within the same Δ" — H2's gradient
evidence is defined within matched comparisons.

## 7. E3b: Structure-Destruction Intervention [Main Result: Surgical-Swap Evidence for the Causal Role of Locality]

Degree-preserving swapping (the literal degree sequence unchanged literal-by-literal;
only spatial locality is destroyed), paired by (n, α, r, seed), Wilcoxon signed-rank:

| Δ | pairs | original mean logc | swapped mean logc | difficulty change | p |
|---|---|---|---|---|---|
| +0.2 | 33 | 1.79 | 2.99 | **×16** | 7.0e-10 |
| +0.6 | 49 | 3.25 | 5.08 | **×68** | 6.0e-13 |

(Status flips: among the 82 resolved pairs, the satisfiability of **53 pairs** was
changed by the swap — once locality is destroyed, the instances cross the sat/unsat
boundary.)

**Interpretation**: the two instances have the same variables, and every literal's
occurrence count is identical literal-by-literal; under paired control, the only
difference is "whether the variables still cluster in space". Destroying the clusters
raises difficulty by 1.2–1.8 orders of magnitude. **Locality is not a third variable
co-occurring with difficulty; it is the causal channel itself.** Combined with E1
(treewidth alone does not produce hardness), this yields an asymmetric conclusion:
what matters is **local geometry**, not any single summary of global topology.

## 8. Mediation and the H1 Feature Ladder

**Imai (2011) causal mediation** (r → structural indicator → log10 conflicts, bootstrap
95% CI):

| mediator | ACME | 95% CI | total effect | mediated share |
|---|---|---|---|---|
| modularity | **3.06** | [2.84, 3.37] | 3.26 | ~94% |
| spectral gap | **3.92** | [3.68, 4.28] | 3.26 | >100% (direct effect -0.66, suppression) |
| mean degree | 2.34 | [2.15, 2.60] | 3.26 | ~72% |
| clustering | 2.19 | [2.02, 2.44] | 3.26 | ~67% |

No ACME confidence interval contains 0 — under the preregistered decision rule,
**mediation is established** (mechanism evidence, not proof): the bulk of r's effect is
transmitted to difficulty through the restructuring of "community/spectral structure";
the suppression pattern of the spectral gap suggests that r also has a secondary channel
bypassing community structure.

**H1 feature ladder**: the E5 baseline (Zulkoski specification) on the main-scan data —
the density ladder gives CV R²=0.664, + the structural ladder **0.976** (on controlled
families, structural features carry a ~0.31 increment; contrast: the purely random
family 0.90 with zero gain, consistent with Zulkoski's whole-corpus conclusion) — direct
evidence that **intervention can measure what observation cannot**. GBDT
leave-one-r-out extrapolation (9 folds, training never sees the target r): **CV
R²=0.76**. The full Tobit fit (excluding wall-clock rows per the AMEND-2 semantics, as
of 2026-09-17) converges well: loglik=−1721.7, σ=2.13, with coefficient
p-values ≈5.9e-194 and 8.9e-69 for r and Δ (the pre-fix version failed to
converge because wall-clock rows carried NaN into the likelihood; fixed and
regenerated with the analysis script); censoring sensitivity is carried by the
dual-caliber JT + KM, with consistent conclusions.

## 9. E5 Predictors and E4 Placement

**E5 (predictors)**: baseline (Zulkoski specification) on the main-scan data — the
density ladder gives CV R²=0.664, + the structural ladder **0.976** (on controlled
families, structural features carry a ~0.31 increment; contrast: the purely random family
shows zero gain). GBDT leave-one-r-out extrapolation (9 folds; training never sees any
instance of the target r): **CV R²=0.76** — structural features plus the parameter
extrapolate to difficulty at unseen locality levels. H1's "a combination of structural
indicators beats density alone" holds on the intervention families (nested-F details in
results/e5_baseline.json).

**E4-prime (placement, not entering the training set)**: 59 instances (42 Heule
combinatorial + 17 DIMACS classics, manifest QA all passed) were adjudicated under the
S0 budget (10⁷/300s): **22/59 decided**. Distribution: DIMACS classics 15 SAT + 2 UNSAT,
all decided at the millisecond scale (easy-end anchor) — [2026-09-12 erratum] the
initial version, due to a parsing defect in the 1996 legacy DIMACS dialect, truncated
the as/tm families to 1–21 clauses and misreported "all 17 SAT and decided in seconds";
after the parser was augmented with declaration self-validation, everything was
re-adjudicated: as9-no (the -no suffix marks UNSAT instances) and as1-yes (legacy label
inconsistent with the content) are in fact UNSAT; the re-run trail is in M2_LOG; the
Heule combinatorial challenge instances (26x26/Green/Steiner/matrix, etc.) hit
wall-clock truncation across the board (hard-end anchor); mphf/packing/radio partially
decided. Placement conclusion: this project's difficulty spectrum (10⁰–10⁶ conflicts)
covers the middle of the real spectrum from "textbook-easy" to
"combinatorial-challenge-hard"; the industrial-diversity gap remains declared as before
(source-switch decision in M2_LOG). Cross-checking the status self-declared in file
names against our determinations (mphf-SAT judged sat, etc.) passed a consistency spot
check (excluding the legacy as family, see the erratum above).

## 10. E6 (H3, Exploratory): LLM Branch Ordering — Pruned per the Preregistered Cut Line

Setup: planted geo_random n=50, guaranteed satisfiable, 3 r levels × 10 seeds × three
strategies (classical JW baseline / random / qwen3:8b taking over the first MAX-level
decisions with JW as fallback), comparing σ-match rate and decision count. Results: LLM
and JW nearly coincide at each r (σ-match 0.531/0.615/0.616 vs 0.534/0.605/0.611), with
no r-gradient signal exceeding the classical baseline — the preregistered cut line ("no
r-gradient signal") was hit. **H3 is adjudicated a negative result** (exploratory
evidence grade; it does not enter the conclusion-strength grading); E8 (the probSAT
contrast) is retained in the follow-up roadmap. Engineering note: qwen3 is a thinking
model; CPU inference requires think:false + a 300s timeout (it ran through after two
revisions of the timeout parameters).

## 11. Limitations and Threats to Validity (Frozen Framework + Post-Main-Result Refinement)
1. **CNF encoding effects**: the conclusions are limited to clause-level structure in
   direct CNF encodings; real application problems under Tseitin transformation may
   introduce channels beyond the VIG (the E4-prime spectrum leans toward combinatorial
   and classical DIMACS instances; the BNN source did not materialize, see M2_LOG).
2. **CDCL mechanism mediation**: the theoretical chain (BKSS/AFT) targets abstract CDCL
   models; the VSIDS/restarts/deletion of real solvers lie outside those models — what
   we measure is empirical conflict counts; theory serves as interpretation, not
   guarantee.
3. **Censoring and anti-conservative bias [bounded]**: for propagation-explosion cells,
   the 300s wall clock is a release (truncation), not a failure; AMEND-2 declares its
   directional bias (α_c systematically overestimated → anti-conservative for H2).
   Spot-checks (10⁸ budget / 480s wall clock, 4 fresh seeds × α_c±0.2 × 4 low-confidence
   radii) bounded it empirically: SAT instances appear at α_c−0.2 for r=0.3 ⇒ the
   overestimation of α_c(0.3) is confirmed, with bias ∈[−0.2, 0] density units; at r≥0.5
   the ±0.2 probes cannot bracket the threshold — on the α_c+0.2 side, 12/12 are all
   decided UNSAT; on the α_c−0.2 side, 12/12 all time out (10⁸/480s) ⇒ the
   measurability boundary is robust, and α_c keeps its "1e7 operational value" label
   together with an unbounded-bias declaration.
   **The H2 conclusion is unaffected**: the Δ-matched design defines the gradient within
   r, and an overall translation of α_c changes neither the direction nor the magnitude
   of the dose–response; the report is written under the "operational threshold"
   caliber (frozen record 6).
4. **Metric approximation**: treewidth is a bracket (min-fill upper bound + degeneracy
   lower bound); the cross-scale invariance of community resolution is limited (Leiden
   at fixed resolution, noted in the report).
5. **External validity**: the geo_random family ≠ the totality of industrial instances;
   the E4 placement claim is limited to the decidable band; the SAT 2024 main-track
   corpus was unreachable from this network, a standing declared gap.
6. **H1 limitations (test completed)**: the nested F-test of the structural ladder has
   landed (F(60,1283)=297.8, p≈0; committed production script experiments/e5_baseline.py,
   results in results/e5_baseline.json — [2026-09-12 status correction] this line's
   initial version read "awaiting completion of the main-data computation", a
   historical residue of §11 having been written before E5 was completed); the E5
   increment claim follows the committed ladder and nested test.

## 12. Philosophical Extensions (Gray Box: Strictly Separated from the Empirical Conclusions; for Discussion Only)

> **This section is not a claim about physical law, but "philosophical implications
> worth discussing if the E3a main result holds".**
>
> - **The experimental version of the "causation knows no absolute strong correlation"
>   conjecture**: we cannot intervene on the universe as a whole, but we can intervene
>   inside the microcosm of combinatorial problems. If the dose–response of "locality r
>   ⇒ tractability" holds, the conjecture gains its first controlled evidence — note
>   that it concerns the relation between **the structure of problem instances** and
>   **a particular solving paradigm (CDCL)**, not P vs NP.
> - **An arithmetical version of structural realism**: difficulty is not an intrinsic
>   property of the formula but a relational property of "structure × solver dynamics".
>   E1 (treewidth does not produce hardness) and R3b (locality does produce hardness)
>   together suggest that what matters is **the geometry of the local working set**,
>   not any single summary of global topology.
> - **The payoff of falsifiability**: compressing the philosophical conjecture into one
>   knob (r), one readout (conflict counts), and one set of controls (the topology ×
>   content 2×2) strips away the conjecture's metaphysical part and leaves propositions
>   that data can vote down — whichever direction the result takes, this is the price
>   the conjecture ought to pay.
> - **A causal sequel to the phase-transition lineage**: since Cheeseman–Kanefsky–Taylor
>   (IJCAI 1991, "Where the really hard problems are"), "combinatorial problems are
>   hardest near structural phase transitions" has been a classical observation of more
>   than thirty years; our contribution is to add the **causal and solver-relative**
>   link to this lineage — the locality radius does not merely drop problems into the
>   hard band, it moves the dividing line itself, and the effect is realized through
>   CDCL's search dynamics. The same protocol (single knob + threshold-matched dosing +
>   structure destruction + censoring bounding) can be ported as a general diagnostic
>   tool onto any claim of the form "structural property P × algorithm A × instance
>   family F"; but porting it to local-search solvers is a **preregistered prediction
>   (E8), not a conclusion** — if difficulty is a relational property of "structure ×
>   algorithm", local search should respond to r differently, even inversely.
> - **An analogy with reductionism (an analogy only)**: locality here plays a role
>   akin to "the domain of validity of an effective theory": at small r, instances are
>   decided by local evidence (small UNSAT subformulas are discoverable); at large r,
>   one enters the collective-phenomena regime (OGP/mean-field), where "local causes"
>   no longer provide a shortcut to the phenomenon.

---

## 13. Reproduction Guide (Frozen)
```bash
git clone <repo> && cd correlation-vs-hardness
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
bash scripts/status.sh                       # progress of all experiments (unified caliber)
.venv/bin/python -m pytest tests/ -q         # unit tests (incl. the probSAT wrapper)
.venv/bin/python experiments/m2_e3a_main.py  # E3a/E3b main scan (resumable, completed)
.venv/bin/python experiments/s0_ext_low.py   # S0 grid-floor extension (completed)
.venv/bin/python experiments/s0_alphac_extract.py  # α_c(r) extraction + figures
.venv/bin/python experiments/s0_spotcheck.py --workers 4  # AMEND-2 bounding (completed)
.venv/bin/python experiments/e3a_analysis.py # main analysis + dose–response figures
.venv/bin/python experiments/e4_status.py --workers 10    # E4 status adjudication (completed)
.venv/bin/python experiments/e5_baseline.py results/m2_main.db results/m2_e1e2.db  # H1 ladder (pass both DBs, otherwise the JSON is overwritten by the single-DB version)
.venv/bin/python experiments/e5_gbdt.py      # leave-one-r-out extrapolation
```
All experiments completed one pass on 2026-09-10; re-runs resume from checkpoints and
skip decided jobs. Determinism: every generator determines an instance by (family,
params, seed); the results store is SQLite with UNIQUE(family,params,seed,solver) and
idempotent resume; content-hash manifests live in data/external/.

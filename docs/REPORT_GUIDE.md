# Reader's Guide to the Report: Glossary · FAQ · How to Read It · Ten-Sentence Summary

A companion to *Does the "Locality Radius" of Variable Interaction Causally Determine SAT Hardness?* (docs/REPORT.md).
Written for non-technical readers: each term is first explained in plain language, then given its precise meaning "strictly speaking," so that the metaphors do not cause misreadings.

---

## I. Glossary (grouped by topic)

### A. Solvers and search

- **SAT (satisfiability)**: Given a large pile of conditions built from "or" propositions, can every variable be
  assigned true or false so that all the conditions hold at once? It was the first problem proven NP-complete.
  *In this project*: the "physical world" we use is SAT instances.
- **CDCL (conflict-driven clause learning)**: The standard algorithm of modern SAT solvers. Like a detective
  working a case: guess a variable assignment → hit a contradiction → distill "why this crash happened" into a
  new entry (a learned clause) and write it down → start over in a different direction. *In this project*: the
  hardness we study is "how many times CDCL crashes."
- **Conflicts**: The number of times CDCL crashes. On the same machine it is a highly correlated stand-in for
  stopwatch time, but it is **comparable across machines** (stopwatch time is affected by CPU speed).
  *In this project*: the primary hardness readout; all conclusions are built on it.
- **Propagation**: Once certain variables are fixed, the values of many other variables get determined "along
  the way" — like dominoes. *In this project*: large-r instances once showed "few conflicts but a propagation
  tsunami," which is why the wall-clock guardrail exists (AMEND-2).
- **VSIDS / LRB**: Two famous branching heuristics — the scoring rules that decide "which variable to guess
  next." *In this project*: Zulkoski proved that they "stick to the communities" when branching (Gini≈0.5 vs
  0.16 for random), evidence that CDCL behavior is local.
- **Restarts**: The strategy of tearing the case down midway and starting over. *In this project*: experiments
  show it has little effect on search locality.
- **probSAT**: A local-search-style solver (no reasoning; flips variables at random until it is satisfied).
  *In this project*: compiled and held in reserve, as the comparison from "another family of algorithms."

### B. Graphs and structure

- **VIG (variable interaction graph)**: The graph obtained by joining, pairwise, the variables that appear
  together in each clause (condition). *In this project*: the carrier of the instance's "structure"; community
  structure and treewidth are both computed on this graph.
- **Community structure / modularity**: How much the graph splits into small circles that are busy inside and
  quiet toward one another; modularity is its score (0–1; the higher, the more "cliquish"). Strictly speaking:
  modularity is the normalized sum of the difference between the number of edges actually inside the circles
  and the number of edges expected in a random graph.
- **Treewidth**: A measure of "how close the graph is to being a tree," like the minimum number of colors a
  map needs to guarantee that neighboring countries get different colors, minus one (strictly speaking: the
  capacity of the largest bag in a tree decomposition, minus one). *In this project*: E1 shows that by itself
  it does not create hardness — key evidence that structure ≠ hardness.
- **Degeneracy**: How many neighbors the "most clingy vertex" in the graph has; a cheap lower-bound
  approximation to treewidth.
- **Spectral gap**: The difference between the two largest eigenvalues of the graph Laplacian, reflecting the
  graph's "connectivity fault lines." *In this project*: one member of the ladder of structural indicators.
- **Degree distribution**: The distribution of how many clauses each variable appears in. *In this project*: a
  key controlled quantity — degree-preserving swaps (E3b) pin it down literal by literal.
- **Power law**: A "long-tail" distribution in which a few variables appear extremely often and most appear
  rarely — a typical feature of industrial instances.

### C. Locality and generators (terms coined by this project)

- **Locality radius r**: **The core knob of this project**. When generating a clause, variables are drawn only
  from within radius r of some center point on the two-dimensional torus. Small r = variables interact only
  with their neighbors; large r = the interaction range spreads out.
- **geo_random**: Our main hardness-carrier family — non-planted geometric random 3-SAT (the planted=False
  mode of the generator above). It inherits the geometric regime of Bläsius et al.
- **Planted instances (planted)**: First construct a satisfying assignment σ, then build clauses around it.
  *In this project*: R1/R2 found planted instances too easy for CDCL, and the family was demoted to a
  robustness arm.
- **σ-satisfaction pattern / redundancy**: The polarity pattern for building clauses around σ — first draw a
  cardinality uniformly from 1..k among the positions satisfied under σ, then draw a subset of that
  cardinality (not the 7 non-empty subsets with equal probability). Redundancy (the average number of
  literals per clause satisfied by σ) has a measured mean of ≈2.14–2.23, invariant in r. *In this project*:
  the means of pinning down the "content distribution" — ruling out one confound.
- **Degree-preserving swap (E3b)**: A shuffling technique that secretly swaps variables between two clauses
  while keeping the occurrence count of every literal **not one more, not one fewer**. Effect: spatial
  locality is destroyed while the degree sequence does not budge. *In this project*: the structure-destroying
  intervention — the "scalpel" of the causal test.
- **2×2 factorial**: The four-cell contrast design of topology {preserved, destroyed} × content {original,
  resampled}. (For the operationalization tension in the content arm, see AMEND-3.)

### D. Phase transition and complexity

- **Phase transition / threshold α_c**: With the number of variables fixed, the critical density at which
  instances jump from "almost all satisfiable" to "almost all unsatisfiable" as the clause density α grows
  from small to large. Strictly speaking: the interpolated crossing point where the SAT rate = 0.5 (the
  operational threshold at n=400, not the thermodynamic-limit value of 4.267). *In this project*: what S0
  measures throughout.
- **Width barrier**: When the "width" of a resolution proof exceeds the order of √(n log n), the shortest
  proof length is bound to explode (Ben-Sasson–Wigderson). *In this project*: one of the theoretical
  yardsticks explaining "why small r is easy and large r is hard."
- **Treewidth→width→CDCL chain**: Low treewidth ⇒ a narrow proof exists ⇒ a short proof exists ⇒ CDCL with
  restarts finds one in polynomial time. *In this project*: the theorem-level explanation of E1's flat result.
- **OGP (overlap gap property)**: The obstacle that "solutions are not similar enough to one another" in a
  high-dimensional random solution space, heralding the failure of local algorithms. *In this project*: the
  theoretical backdrop of the large-r regime (regime division only; no guarantees).
- **P vs NP**: This report does not attack it. Our conjecture grew out of popular discussions of it, but the
  conclusions are strictly limited to "CDCL + n=400 + direct CNF encoding."

### E. Statistics

- **Censoring**: An experiment that runs to its budget cap without producing a verdict — we know it is "at
  least this hard," but not its exact hardness. Like "a marathon runner who did not finish: all we know is
  that he ran more than 30 kilometers." *In this project*: two kinds — conflict-budget truncation (exact) and
  the 300 s wall clock (anti-tsunami).
- **Tobit regression**: A regression specialized for censored data — it uses "at least this hard" as
  truncation information instead of throwing it away.
- **Kaplan–Meier curve**: The classic plot of survival analysis, showing "how long an instance lived on
  without being solved."
- **Repeated-measures ANOVA**: The same batch of seeds measured repeatedly for hardness at different r (a
  paired design); the analysis of variance tests whether r truly causes differences. partial η² is the
  effect size (what proportion the difference accounts for).
- **Jonckheere–Terpstra (JT)**: A trend test for "hardness rises/falls monotonically with r," with Monte
  Carlo permutation used to compute the p-value.
- **Paired Wilcoxon**: The main test of E3b — the paired comparison of original vs shuffled, same seed.
- **Causal mediation (ACME)**: The Imai framework — how much of r's effect is transmitted "through the
  structural indicators." The bootstrap gives the confidence intervals.
- **BH-FDR**: Multiple-testing correction — controlling the "false discovery rate" when many tests are run at
  once.
- **Preregistration**: Freezing and publishing the hypotheses and decision criteria before the main experiment
  is run, to prevent "picking the good-looking results after the fact." *In this project*: HYPOTHESES.md v1.0
  + the AMEND-1–5 revision chain + the PRESPEC_AUDIT.md audit.

---

## II. Frequently asked questions (FAQ)

1. **Why the conflict count instead of the stopwatch?** Stopwatch time depends on CPU speed and machine load;
   the conflict count is a solver-internal counter, comparable across machines. Stopwatch time is kept as a
   same-machine reference.
2. **Isn't n=400 too small?** Yes — this is the main limitation (stated explicitly in the preregistration).
   But the benefit of the intervention design is precisely that it can measure causal direction cleanly even
   at small n; scaling up is on the roadmap as E7.
3. **Does cutting off at 300 seconds cut away the truth?** It introduces bias — but the direction is known
   (biased toward the UNSAT side → α_c is overestimated → anti-conservative for our hypothesis = an
   exaggerated gradient), and it is bounded by spot-checks with the 10⁸ budget (AMEND-2). This is "facing the
   bias honestly," not "pretending it away."
4. **Why can the threshold not be measured at large r after all?** Because at medium densities instance
   hardness collapses out of the measurement range (the wall-clock truncations of 314/720 rows concentrate at
   large r). This is itself a result: what locality changes is the "structure of hardness," not just the
   hardness values.
5. **Isn't treewidth the mathematical notion of "good structure" — so why doesn't it create hardness in E1?**
   Low treewidth ⇒ a short proof exists ⇒ CDCL can find it — so low treewidth **guarantees easiness**; but
   conversely, high treewidth **does not guarantee hardness**. E1 shows that the causal force of "treewidth
   alone," in this direction, is zero. Tractability is one-way insurance, not a two-way switch.
6. **What does it mean if the results support the philosophical conjecture?** That "locality causally affects
   CDCL hardness" holds under controlled conditions — note: limited to CDCL, n=400, and direct CNF. For the
   "causal locality" of the physical world it is only an analogical hint, not a proof.
7. **And if they do not?** A negative result is a contribution all the same: the preregistration spells out
   the quantitative trigger conditions for "density dominance"; once triggered, we report it truthfully and
   shift the research focus to the predictor narrative (E5). The value of a negative result is that it seals
   off a popular intuition and saves other people's time.
8. **How far is this from proving P=NP?** A whole Pacific Ocean apart. P vs NP is about *all* algorithms; we
   study the behavior of one class of algorithms (CDCL) on one family of instances (geometric random). It
   does not even count as an edge of that question, but it is the nearest coastline ordinary people can
   touch.
9. **Why not let ChatGPT solve SAT directly?** Language models are not SAT solvers; our E6 uses only a small
   model for the exploratory "branching-order suggestion" experiment (H3), and the kill criterion was
   preregistered (no signal means it gets cut).
10. **What is the difference between the censoring rate and "unmeasurable"?** Censored = no verdict within
    the budget (part of the information is retained); unmeasurable = every cell at a given r is censored
    (the threshold is not identifiable). In S0, r≥0.3 belongs to the latter, hence the coarse measured value
    + a low-confidence flag.
11. **Why σ-pattern sampling?** The literal positions of a 3-clause satisfied under σ have 7 non-empty
    combinations, but the implementation does not sample them with equal probability; it first draws a
    cardinality uniformly from 1..k, then a subset of that cardinality. The measured redundancy is
    ≈2.14–2.23, invariant across r — the content distribution is pinned down constructively and no longer
    depends on luck.
12. **Why is the degree-preserving swap a "scalpel"?** It only changes "who is spatially adjacent to whom,"
    never "how many times each literal appears." Any change in hardness can only be attributed to the
    former — this is the "all other conditions held equal" of causal inference.
13. **Has the preregistration been modified?** Yes, five times, all numbered and on the record
    (AMEND-1–5; AMEND-4/5 are non-hypothesis disposition records), the reasons public, the original text unalterable. The modifications were made to keep
    the experiment feasible or to correct a discovered bias, not to make the results look good — the bias
    corrected by AMEND-2 ran precisely against our own hypothesis.
14. **Are the 59 real E4 instances enough?** Not enough for the 200–500 target; they are a substitute source
    under network constraints, used only for "placement" (where our instance spectrum sits within the
    real-world spectrum), not for training. The gap has been declared.
15. **Can the code and data be trusted?** Every script can be rerun with one click; instances are generated
    deterministically by (family, parameters, seed); the results store is written to disk line by line and
    put under git version control; preregistration–implementation consistency is audited item by item
    (PRESPEC_AUDIT.md).

---

## III. How to read the report

```
§0 Overview (3 sentences) ──→ §1 How the conjecture became an experiment ──→ §2 Theoretical spine (skimmable)
                                                │
                                                ▼
        §3 Methods (generator/measurement/statistics) ──→ §4 Pilot results (R1-R3b/E1/E2)
                                                │
                                                ▼
     §5 S0 threshold curve ──→ §6 Main scan ──→ §7 E3b surgical swap ──→ §8 Mediation and H1
                                                │
                                                ▼
     §9 Placement (E4/E5) ──→ §10 E6 negative result ──→ §11 Limitations and validity threats
                                                │
                                                ▼
        §12 Philosophical extension (gray boxes: optional reading, isolated from the empirical conclusions)
```

- In a hurry: §0 → the table in §5 → the conclusion sentences in §6 → §11.
- Want to argue (welcome): §3 + §11 + PRESPEC_AUDIT.md.
- What the gray boxes are: the content of the gray callout boxes in the report is "the authors' opinions /
  philosophical discussion," clearly separated from the data-supported conclusions; readers may safely
  disagree with them.

---

## IV. Ten-sentence summary (main-results version)

1. We turned the philosophical conjecture "causal locality ⇒ problems are easy to solve" into an experimental
   machine with a twistable knob.
2. The knob is the locality radius r: variables entangle with one another only within radius r on the torus.
3. The readout is the conflict count: the number of times a modern solver crashes, comparable across
   machines.
4. The threshold boundary moves with r: from below 2.5 up to about 4.4 —
   **locality moves the satisfiable/unsatisfiable threshold boundary itself**.
5. Dose–response: with the density difference pinned down, moving r from 0.06 to 0.22 spans
   **3.4 orders of magnitude** of hardness (28 → 72,000 crashes); taking the censoring-aware lower bound
   into account, ≥4.5 orders of magnitude. JT p≤10⁻⁴.
6. The scalpel falls: destroying only the spatial entanglement while preserving the degree distribution,
   hardness immediately jumps 16–68-fold, and the satisfiability of 53 pairs of instances is flipped —
   **locality is the causal channel itself**.
7. Treewidth alone does not create hardness — what is at work is local geometry, not any single summary of
   global topology.
8. Mediation holds: roughly nine-tenths of r's effect is transmitted through the reorganization of
   community/spectral structure (the confidence interval does not contain 0).
9. This is not progress on P=NP; it is one clean measurement on one class of algorithms and one family of
   instances.
10. Preregistered throughout, bias measured and bounded in practice, code and data public — you may disagree
    with us, but you can reproduce us.

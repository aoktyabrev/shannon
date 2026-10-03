# PREREGISTRATION — Stage 2.1

Sealed 2026-10-03, **before the first computation of this stage**. Stage 2 found two 367-word
codes with nine and ten candidate private pairs and failed to find an auxiliary set for either.
This stage asks one cheap question before anyone builds a new search engine: **is there room for
367 words outside the forbidden region at all?** If a certified upper bound on
α(C₇^⊠5 ∖ F) falls below 367, the direction closes by arithmetic and no new machinery is needed.

## 0. The question, stated exactly

For a gadget with code I and t private pairs, with transversals P_H, P_V, the forbidden region is
F = N[P_H] ∩ N[P_V], and the auxiliary set X must be independent, disjoint from F, and as large
as possible. So the quantity is α(G_F) where G_F = C₇^⊠5 restricted to Z₇⁵ ∖ F. Known sizes of F
(Stage 2, `results/json/s2_frontier.json`): 956–984 at t = 8, 1098–1128 at t = 9, 1240–1268 at
t = 10, the range being over the proper 2-colourings.

## 1. What this stage will and will not do

* It computes **upper** bounds with certificates, and **lower** bounds by exhibiting verified sets.
* It does not build a search engine, and it does not report "not found" as "does not exist".
* The criterion is as the brief sets it: an upper bound below 367 at t = 9 closes the direction.

## 2. Predictions

Mine, with numbers, before any of it runs.

| # | prediction | confidence |
|---|---|---|
| P1 | no certificate available in an evening goes below 367. The valid cheap bounds are ϑ(C₇^⊠5) = 401 by induced-subgraph monotonicity, and a box-volume count that will land near 480–530; both are far above 367, so the brief's closing criterion will not be met | 95% |
| P2 | the informative side will be the **lower** one: Stage 2 already left verified independent sets avoiding F of 366 words at t = 9 and 365 at t = 10, so α(G_F) ≥ 366 and ≥ 365, and the gap to 367 is one or two words, not thirty-five | 90% |
| P3 | the 366-word set is maximal in G_F — no single allowed vertex can be added | 70% |
| P4 | a 2-opt step in G_F (remove one word, add two) does not reach 367 either | 60% |
| P5 | the verdict will therefore be: room exists formally, the search sits exactly on the feasibility boundary, and closing the direction needs a ϑ-strength bound on ~15.5·10³ vertices, which is an SDP and a separate stage | 85% |

**Architect's prediction, as given:** the upper bound at t = 9 will be ≥ 367, i.e. room exists
formally and the question is one of search (~60%).

P1 and the architect's prediction agree on the outcome; they differ in what is being claimed.
The architect expects a bound that is informative and lands above 367; I expect the available
bounds to be far above 367 and therefore uninformative, with the real information coming from
the constructions already in hand.

## 3. Calibration, mandatory

1. **The t = 8 control.** At t = 8 an auxiliary set of 367 words exists — the published gadget
   has one. Any upper bound that comes out below 367 there is wrong, and then nothing about
   t = 9, 10 counts.
2. **The empty-F control.** With F = ∅ the estimator must return a value in [367, 401]: at least
   the known lower bound and at most the Lovász bound. A bound that violates either end is
   rejected.
3. **The exhibited-set control.** Every lower bound is a file on disk that `scripts/verify`
   accepts and that is checked to be disjoint from F by a second code path.

## 4. Stopping

One evening of computation. The stage ends with the bounds table and the verdict; any further
search is a new stage with its own preregistration.

## 5. Outcomes, fixed in advance

* upper bound at t = 9 **< 367** → the private-pair line on these codes is closed with a
  certificate, and that is written up as a continuation of the note;
* upper bound **≥ 367** → the direction is alive on paper, and the honest report says how far the
  bound is from being informative and what it would cost to make it so;
* the estimator fails its calibration → the estimator is fixed first and nothing else is claimed.

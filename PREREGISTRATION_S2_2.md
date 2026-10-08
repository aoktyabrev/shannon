# PREREGISTRATION — Stage 2.2

Sealed 2026-10-08, **before the first computation of this stage**. Stage 2.1 closed with the
cheap upper bounds blind to F (all give 401) and the lower side one word short: verified sets of
366 words avoid F at t = 9 and 365 at t = 10, and both are 1-opt and 2-opt optimal inside G_F by
exact coverage counting. This stage asks whether **another nine-pair configuration** — another
code, another colouring — has a forbidden region small enough, or placed loosely enough, for 367
words to fit outside it. It is cheaper than an honest ϑ on fifteen thousand vertices, and unlike
ϑ it can move the obstruction rather than only explain it.

## 0. The question, stated exactly, and what actually varies

A configuration is a code I ⊆ Z₇⁵ (independent), its candidate private pairs (r_i, q_i)
— q_i ∉ I with N[q_i] ∩ I = {r_i} — all t of them used, and a proper 2-colouring of the q-conflict
graph Γ assigning each endpoint to P_H or P_V. Its forbidden region is
F = N[P_H] ∩ N[P_V]; the endpoints lie in F. The target is a configuration with **t ≥ 9 and an
explicit independent X, |X| = 367, X ∩ F = ∅**, accepted only after `scripts/verify` and a second
code path for the disjointness.

**Lemma (stated now, checked numerically in §3).** For g ∈ Aut(C₇^⊠5), the configuration
(gI, transported colouring) has forbidden region g·F, and α(C₇^⊠5 ∖ g·F) = α(C₇^⊠5 ∖ F).
*Proof.* g commutes with closed neighbourhoods, so it maps candidates of I to candidates of gI,
Γ to an isomorphic graph, colourings to colourings and F to gF; and g restricts to an isomorphism
G ∖ F → G ∖ gF. ∎

**Deviation from the brief, made before any run.** The brief lists "the automorphism applied to
the code" as a third variable and asks to sweep it while counting |F|. By the lemma that sweep
returns one number per (code, colouring) and cannot change the answer. The variables are therefore
**the code up to Aut, and the colouring.** Automorphisms keep the role they genuinely have: as the
images g·S of known 367-word sets S offered as auxiliary sets against a fixed F (the group sweep).
The invariance itself is run as a test (§3), so the claim is checked rather than assumed.

## 1. What the stage does

**S2.2.a — population.** Every d = 5 code in `sets/` (I₀, the eight pipeline codes, the reproduced
PS code, X Gao, our 10-candidate X, the o = 322 set, MO-350, linear 343, the 363/365/366 auxiliary
sets): candidates, distinct centres, |E(Γ)|, bipartiteness, number of proper colourings up to the
global swap, t\*, and for every colouring |F| and 16807 − |F|. Images under Aut are not listed as
separate rows — by the lemma they repeat a row. In addition, the decomposition of F by the
coordinate weight w of q_i − r_i, since |N[r] ∩ N[q]| = 3^(5−w)·2^w puts the pairs with large w
at a fraction of the cost.

**S2.2.b — where F is smaller.** For every code with t\* ≥ 9 and every colouring: |F|, then the
auxiliary-set attempt in this order:
1. group sweep (`scripts/s1_aux`) of a source pool of 367-word sets against F — exhaustive over
   (D₇)⁵ ⋊ S₅, minimum number of words in F;
2. exact repair of the near misses (`scripts/s2_repair.py` logic);
3. on the best set found: exact blocking count (1-opt, 2-opt) inside G_F as in Stage 2.1, and the
   "looseness" statistic — allowed vertices blocked by exactly one word.

**S2.2.c — new codes, if budget remains.** In order:
1. the **swap plateau**: a k-swap removes k words of a 367-word code and adds k words so that it
   stays independent; for k = 1 the moves are exactly the candidate pairs (I − r + q). Explored
   breadth-first from every 367-word code in `sets/`, exhaustive for k = 1 within a node cap,
   k = 2…4 around the codes with t\* ≥ 9. Objective: t\* ≥ 9 and min |F| below the current 1098;
2. every new code found joins both the population table and the source pool of step 1 in S2.2.b;
3. enumeration of maximal independent sets in a neighbourhood — only if 1–2 are exhausted.

Codes are deduplicated exactly as sets and, up to Aut, by an invariant fingerprint; a code is
called **new** only if its fingerprint differs from every code already held (different invariants
prove non-isomorphism; equal invariants are counted as *not new*).

**Not done:** no search for a 367-word code from a random start — the S2.1 gate of Stage 2 is
not passed and nothing here changes that.

## 2. Predictions

Mine, with numbers, before any of it runs.

| # | prediction | confidence |
|---|---|---|
| P1 | the automorphism part of the brief's spread is **exactly zero** (lemma); within one code the colourings alone spread |F| by 2–3.5% (Stage 2 already shows 1098–1128 and 1240–1268), so the brief's "≥ 5% within one code" fails | 85% |
| P2 | across distinct codes with the same t\* the spread of min |F| does reach ≥ 5% | 50% |
| P3 | the swap plateau yields at least one new code (by fingerprint) with t\* ≥ 9 | 80% |
| P4 | no configuration at t ≥ 9 reaches 367; the best exhibited stays 366 | 75% |
| P5 | min |F| over all t\* = 9 codes found stays ≥ 1000, i.e. no nine-pair code gets its forbidden region down to the t = 8 level | 70% |
| P6 | the best t = 9 sets remain 1-opt and 2-opt optimal in G_F, as in Stage 2.1 | 75% |

**Architect's predictions, as given:** spread of |F| over colourings and automorphisms of one code
≥ 5% (medium); no configuration at t = 9 gives 367 (~65%); at least one new nine-candidate code
besides X Gao (medium).

P1 disagrees with the first of these in substance, and for a stated reason (the lemma), not for a
difference in expectation. P4 and P3 agree with the architect's second and third.

## 3. Calibration, mandatory

1. **The published gadget, t = 8.** The candidate count and |F| on I₀ reproduce 8 candidates and
   956–984 over the 16 colourings, and the sweep-plus-repair pipeline run on I₀ reaches an
   admissible 367 (Stage 1: o = 322). If it does not, nothing it says about t ≥ 9 counts.
2. **Blocking count at t = 8** says the published X (367) is admissible and reports its
   1-/2-opt profile, as in Stage 2.1.
3. **Automorphism generator, anti-vacuum.** Every g used is checked to map all 16807·242 ordered
   adjacencies of C₇^⊠5 to adjacencies. The identity is refused as a test element (an invariance
   test on the identity is vacuous); a non-automorphism (x ↦ 2x in one coordinate) must be
   **rejected** by the same checker. The lemma is then tested on random non-identity g: |F| and
   the candidate count of gI must equal those of I.
4. **Swap moves.** Every code produced by a swap is re-verified by `scripts/verify`; a swap
   generator that ever emits a non-independent set is fixed before any count it produced is used.

## 4. Budget and stopping

| resource | ceiling |
|---|---|
| CPU (i7-13700F, 8 threads) | **40 core-hours** |
| GPU | 0 |
| wall-clock | 7 days from the first run |

The stage stops at the first of: a verified configuration with t ≥ 9 and |X| = 367 (then the
recursion is recomputed, a literature check is run on the day, and the decision to publish is
the author's); the budget exhausted; S2.2.c items 1–2 exhausted with nothing left that the brief
permits. No ceiling may be raised after seeing results.

## 5. Outcomes, fixed in advance

* 367 at t ≥ 9 found → recursion recomputed in exact integers, verifier, literature check, then
  a decision on publication; this would be a record;
* not found → the S2.2.a table is the result of the stage, together with the observation that
  the one-word gap holds over every configuration checked, with the count of configurations;
* budget exhausted → the ceiling in numbers, without extrapolation.

# PREREGISTRATION — Stage 1

Sealed 2026-09-25, at the end of Stage 0 and **before any search run**. Stage 0 contains no
search: it built the verifier, reproduced three published constructions, checked the record
chain and mapped the methods (`METHODS.md`). This file fixes what Stage 1 is allowed to claim,
what it will spend, and when it stops. It is committed on its own, and `RESULTS.md` refuses to
be generated if its SHA-256 no longer matches the one recorded at sealing time.

## 0. State of the art on the sealing date

Established in Stage 0 by a literature search (`results/json/litcheck.json`) and by exact
recomputation (`results/json/gadget.json`, `results/json/theta.json`):

| | Θ(C₇) ≥ | source |
|---|---|---|
| 2019 | 3.2578659667835159504124… (367^(1/5)) | Polak–Schrijver [PS19-1] |
| Jul 2026 | 3.2580207372932453595278… (134753^(1/10)) | Itty, Rosin, Carstensen, Reichman [IRCR26-1] |
| Jul 2026 | 3.2587891539086910161967650155206769… | Gao [G26-8] |
| Jul 2026 | 3.2588053698854655725829750306238067… | Buys–Polak–Zuiddam [BPZ26-1] |
| **Aug 2026** | **3.2588326203532663091215390518104754376053875943219…** | **Tandon [T26-2] — the record** |
| upper | ϑ(C₇) = 3.3176672073940953927332082980723813… | Lovász, via [PS19-2] |

**The premise the project started from was out of date: arXiv:2607.21517 is not the record.**
It is three papers behind. Everything below is set against Tandon's number.

## 1. What Stage 1 tries to beat, and by which route

The lever is **not** the dimension. Gao proves the recursion saturates [G26-10] and our own
dynamic programme run to 160 blocks agrees: over k ≤ 160 the maximum is attained exactly at
k = 40, dimension 200. The lever is the **five-dimensional base gadget**.

Evaluating the published recursion [G26-7] at hypothetical base profiles
(`results/json/gadget.json`, `profile_sensitivity`; s = 367 throughout) gives:

| base profile (a,t,s,o) | Θ(C₇) ≥ | vs the record |
|---|---|---|
| (367, 8, 367, 321) — Gao | 3.25878915390869101619 | −4.3·10⁻⁵ |
| (367, 8, 367, 322) — BPZ | 3.25880536988546557258 | −2.7·10⁻⁵ |
| (367, 8, 367, 323) | 3.25882217860319960218 | −1.0·10⁻⁵ |
| **(367, 8, 367, 324)** | **3.25883961327270001873** | **+7.0·10⁻⁶** |
| **(367, 9, 367, 321)** | **3.25900620077385213058** | **+1.7·10⁻⁴** |
| (367, 10, 367, 321) | 3.25923957517750550186 | +4.1·10⁻⁴ |
| (368, 8, 367, 321) | 3.26007331140805895515 | +1.2·10⁻³ |

One extra private pair is worth about ten times one extra auxiliary word in class O. That sets
the target.

**Primary goal (S1-P).** Exhibit a gadget in C₇^⊠5 whose profile, fed into the *homogeneous*
recursion of [G26-7] at k = 40, gives

        Θ(C₇) > 3.2588326203532663091215390518104754376053875943219

i.e. strictly greater than Tandon's bound [T26-2]. On the table above this needs t ≥ 9 (at
s = 367, o ≥ 321), or t = 8 with o ≥ 324.

**Secondary goal (S1-S), declared now so that it cannot be invented afterwards.** If S1-P is
not reached, Stage 1 still reports, as its result, the **exact maximum number of private pairs
t\*** admissible on the Polak–Schrijver 367-set, together with the best (o, h, v) achievable at
that t\*. A proof that t\* = 8 for that code is a publishable negative result and is accepted as
the outcome of Stage 1; it is not a failure and will not be relabelled as one.

**Explicitly not a goal.** Beating Tandon through his own heterogeneous framework [T26-7]. That
framework is not reproduced in Stage 0 and will not be reimplemented under the Stage 1 budget.
If a base gadget good enough for S1-P is found, the claim made will be the one that follows
from the *homogeneous* recursion only, which we can and do check exactly.

## 2. The search space, fixed in advance

Ordered; Stage 1 works down the list and stops at the budget.

* **A. Private pairs on a fixed code.** Take I one of the two 367-word codes in `sets/`
  (`C7_d5_367_polak_schrijver.txt`, `C7_d5_367_reproduced.txt`). Enumerate every candidate
  private pair exactly: all q ∈ Z₇⁵ \ I with |N({q}) ∩ I| = 1. Then find the maximum set of
  pairs with disjoint endpoints admitting two independent complementary transversals — an
  exact combinatorial problem on a small structure, to be solved exactly, not heuristically.
* **B. The auxiliary set, given the pairs.** For the best pair systems from A, maximise o (and
  then s) over independent X with X ∩ N(P_H) ∩ N(P_V) = ∅. Exact where it fits, otherwise
  branch and bound with a proved bound.
* **C. Other codes of size 367.** Generate further 367-word independent sets (the
  Polak–Schrijver pipeline admits 71-vertex extension graphs with several maximum independent
  sets; our reproduction already differs from the printed set in two words) and repeat A–B.
* **D. Codes of size ≠ 367.** A gadget's code need not be maximum. Smaller codes with far more
  private pairs are admissible and the table above does not cover that trade-off. This branch
  is entered only if A–C leave budget.

## 3. Budget

| resource | ceiling |
|---|---|
| GPU (RTX 4070 Ti, 12 GiB) | **20 GPU-hours** |
| CPU (i7-13700F, 8 cores) | **100 core-hours** |
| wall-clock from the first search run | **14 days** |

Whichever binds first ends Stage 1. Measured from the S0.4 numbers
(`results/json/bench.json`): the verifier sweeps 9.1·10⁸ box cells/s on one CPU core and
3.3·10¹⁰ on the GPU, so verification is not what the budget is for — the budget is for the
combinatorial search in §2.

## 4. Stopping criterion

Stage 1 stops at the first of:

1. S1-P met **and** fully verified under §5;
2. S1-S settled — t\* proved exactly for both 367-codes, with the corresponding (o,h,v);
3. any budget ceiling in §3 reached;
4. a newer paper appears that supersedes the target (a fresh literature search is mandatory on
   the day of any claim, see §6).

No extension of the budget is permitted after seeing results. If the budget is raised, that is
a new stage with a new preregistration.

## 5. What counts as a result

A found object counts only after **all** of:

1. every explicit set of vertices is INDEPENDENT according to `scripts/verify` (exact box
   packing, no floating point), on the file as committed, with its SHA-256 recorded;
2. its cardinality is recounted by a second, independent code path — not by the program that
   produced it;
3. every clause of the gadget definition [G26-1] is re-checked by `scripts/gadget.py`
   (independence of I and X, the private-pair property for every pair, independence of both
   transversals, disjointness from the endpoints, and the o/h/v split with nothing confusable
   with both transversals);
4. the resulting bound is computed in exact integer arithmetic (`int_nth_root`, no floats) and
   compared with the record as an integer comparison, not a decimal one;
5. the anti-vacuum calibration of `scripts/calibrate.py`, including the mutant-verifier test,
   passes on the same commit.

Additionally, as a calibration of the search itself: **the search procedure must re-find the
known t = 8 gadget from scratch** before any claim of t ≥ 9 is entertained. A search that
cannot rediscover the known answer is not evidence about a better one.

## 6. Claims discipline

* No improvement is announced without re-running `scripts/litcheck.py` on the day of the claim
  and recording its output. Stage 0 found the starting premise three papers out of date; the
  field is moving in weeks.
* Θ(C₇) bounds are quoted with the number of digits our own exact arithmetic supports, and with
  the dimension and the base profile they came from.
* If the outcome is negative, `RESULTS.md` says so in the same place and with the same
  prominence as a positive one would have.

## 7. What Stage 1 will not do

* No search in Stage 0 — already binding, recorded here for the audit trail.
* No claim of an improved α(C₇^⊠d) for any d from a set our own verifier has not checked.
* No reimplementation of Tandon's heterogeneous framework (§1).
* No carrying over of code or dependencies from other projects. Stage 0 needs only a C
  compiler, nvcc and a bare Python 3; Stage 1 keeps that.

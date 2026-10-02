# PREREGISTRATION — Stage 2

Sealed 2026-10-02, **before any search run of Stage 2**. Stage 1 proved t\*(I₀) = 8 for the
printed Polak–Schrijver code and showed the count is a property of the individual code; Stage 2W
wrote that up (note submitted to Information Processing Letters as IPL-D-26-00415, preprint
10.5281/zenodo.22979509). This file fixes what Stage 2 may claim, what it will spend, when it
stops, and what it predicts. It is committed on its own; `RESULTS.md` refuses to be generated if
its SHA-256 no longer matches the one recorded at sealing time.

## 0. State of the art on the sealing date

From `results/json/s2_litcheck.json` (search of 2026-10-02, label `stage2-start`, 59 distinct
hits) and from the dumps:

* the record is unchanged: Θ(C₇) ≥ 3.2588326203532663091215390518104754376053875943219… [T26-2].
  Twelve arXiv items carry a later identifier; none is about Shannon capacity, odd cycles, strong
  products or zero-error coding;
* **no 367-word code outside the Polak–Schrijver construction is published.** FunSearch recovered
  the *bound* [BPZ26-4] but its repository carries no such set (checked 2026-10-02). The eight
  codes of our own pipeline enumeration are the only family whose candidate counts are known —
  and no paper reports a candidate count for any code at all;
* Polak and Schrijver swept the parameters of their own steps (ii)–(iii) and a 3-opt neighbourhood
  of R, **for size** [PS19-11, PS19-12]. Stage 2's objective is different, so that ground is not
  taken;
* the only published upper bound on α(C₇^⊠5) is ϑ(C₇)⁵, recomputed here at 60 digits as
  401.9426585010706501209115…, so 367 ≤ α(C₇^⊠5) ≤ 401 and 368 is open [PS19-13].

## 1. What Stage 2 tries to beat, and by which route

The lever is the **individual code**, not its size and not the dimension. From the sensitivity
table of the note (`results/json/s1_anchor.json`), a base gadget whose code has a candidates
with a bipartite conflict graph gives, through the homogeneous recursion at k = 40:

| profile (a, t, s, o) | Θ(C₇) ≥ | vs the record |
|---|---|---|
| (367, 8, 367, 322) — the published base | 3.2588053698854655725829… | −2.725·10⁻⁵ |
| **(367, 9, 367, 321)** | **3.2590062007738521305802…** | **+1.736·10⁻⁴** |
| (367, 10, 367, 321) | 3.2592395751775055018694… | +4.070·10⁻⁴ |

**Primary goal (S2-P).** A code I ⊆ Z₇⁵, independent, with
t\*(I) ≥ 9 at |I| = 367 — or the equivalent price elsewhere on the curve:
**13 pairs at 366, 16 at 365, 23 at 360** (`branch_D_break_even`). t\* is computed as in the
note: candidates are the vertices outside I with exactly one I-neighbour, and t\* is the largest
subset of them with distinct centres whose confusability graph is bipartite.

**Secondary goal (S2-S), declared now.** If S2-P is not reached, Stage 2 reports, as its result,
**the distribution of the candidate count over the codes it found**, by code size — a statistic
that exists nowhere in the literature, together with the ceiling the search reached. This is
accepted in advance as the outcome, and will not be relabelled a failure.

## 2. The gate, and what happens if it fails

**S2.1.** From a random start, with no information from the Polak–Schrijver construction, the
search stack must reach an independent set of size **≥ 350** in C₇^⊠5 — the Mathew–Östergård
value [MO17-1] — inside the budget of §3. Report: size reached, method, number of starts,
seconds.

If the gate fails, Stage 2 **does not start**: the method is changed first. Stage 1's lesson is
recorded here as the reason — a generic solver could not even settle d = 3, while a
problem-specific engine did it in 42 s.

## 3. Budget

| resource | ceiling | why this number |
|---|---|---|
| CPU (i7-13700F, 8 threads) | **200 core-hours** | Stage 1 spent ≈18.7 on structures of size 10¹–10⁸; Stage 2 searches a 16807-vertex independent-set landscape, which is a different order of work |
| GPU (RTX 4070 Ti) | **0 — none requested** | measured, not assumed: at d = 5 the GPU verifier is **0.2×** the speed of one CPU core (`results/json/bench.json`), because the kernel launch costs more than the sweep. The architect's suggestion of 30 GPU-hours is declined on that measurement; if a GPU search kernel is ever written, that is a new stage with a new budget |
| wall-clock from the first search run | **14 days** | as proposed |

Whichever binds first ends Stage 2. No ceiling may be raised after seeing results; a raise is a
new stage with a new preregistration.

## 4. Stopping criterion

Stage 2 stops at the first of:

1. a code meeting S2-P, **after** full verification under §5;
2. the budget in §3 exhausted — then S2-S is written up;
3. a newer paper supersedes the target (a fresh literature check is mandatory on the day of any
   claim, and at the end of the budget).

## 5. What counts as a result

A code counts only after all of:

1. `scripts/verify` says INDEPENDENT on the file as committed, SHA-256 recorded;
2. its size is recounted by a second code path, not the one that produced it;
3. its candidate list is recomputed by the Stage 1 enumerator (`scripts/s1_pairs.py` /
   `scripts/w_theorem.py`), and the bipartiteness of the conflict graph checked explicitly;
4. for any claim of a bound: the full gadget definition [G26-1] re-checked by `scripts/gadget.py`
   (an auxiliary set X has to exist too — a code with nine candidates is not yet a gadget), and
   the bound computed in exact integer arithmetic;
5. the anti-vacuum calibration passes on the same commit, including the mutant verifier;
6. **the search must re-find a known answer first**: the gate of §2, and, for the perturbation
   direction, the recovery of the known count 8 on I₀ itself.

## 6. Predictions

Numbers, so that they can be wrong. Mine first, then the architect's as given.

**Executor's predictions (2026-10-02).**

| # | prediction | confidence |
|---|---|---|
| E1 | the gate is passed, but **not** by free local search from a random start: free search plateaus at **≤ 352** and prescribed symmetry (translation of order 7, 50 orbits) is what reaches 350 | high |
| E2 | no translation-invariant code of size 357 = 51·7 exists to be found — the symmetric search stops at 350 | medium-high |
| E3 | k-opt around I₀ for k ≤ 6 finds no code with 9 candidates; the best count it sees is 8, and it reproduces counts 5–8 many times over | medium-high |
| E4 | the candidate count rises with code size: codes of size ≤ 350 have **0–2** candidates typically and codes of size ≤ 343 usually **0**; the 5–8 band is a feature of being within a few words of maximum | medium |
| E5 | across every direction, the maximum count found at size 367 is **8**, i.e. S2-P is not reached | 85% |
| E6 | at least one code of size 367 outside the PS pipeline **is** found (new code, old count) | medium |

**Architect's predictions, as stated in the brief.**

| # | prediction | confidence as given |
|---|---|---|
| A1 | S2.1 passed, but without reaching 367 from a random start | high |
| A2 | perturbing I₀ at k ≤ 6 does not give nine candidates | medium |
| A3 | the distribution of counts over found codes is concentrated on 5–8 rather than spread | medium-low |
| A4 | the goal of the stage is not reached | ~75% |

A1 and E1 differ in what they measure: A1 says a random start will not reach 367, E1 says it will
not even reach 350 without prescribed symmetry. Both are recorded; the run decides.

## 7. Claims discipline

* Every number in `RESULTS.md` comes from `results/json`; the file is generated, never edited.
* A code found by search is "found", not "constructed"; a count obtained by enumeration over all
  of Z₇⁵ is "exact", and anything from a time-limited search says how long it ran.
* "Not found in T seconds" never becomes "does not exist".
* Negative outcomes are reported in the same place and with the same prominence as positive ones.

## 8. What Stage 2 will not do

* no GPU budget, for the measured reason in §3;
* no reimplementation of Tandon's heterogeneous framework — it changes what a *given* base gadget
  is worth, not whether a better code exists, and it is already quoted as the thing any future
  claim must be measured against;
* no claim about α(C₇^⊠5) itself (a 368th word) unless one is found in passing and verified; the
  stage is about the candidate count at a fixed size.

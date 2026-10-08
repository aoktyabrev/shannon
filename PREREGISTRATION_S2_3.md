# PREREGISTRATION — Stage 2.3

Sealed 2026-10-08, **before the first computation of this stage**. Stage 2.2 found that every
nine-pair code within reach has the same sixteen forbidden regions at t = 9, and that every
candidate of every 367-word code has a difference q − r with exactly two non-zero coordinates.
This stage asks the combinatorial question behind that: **which shapes of q − r can a private
pair have at all, what does each shape cost in forbidden vertices, and how large can a code be
that carries a pair of a given shape.** No search run of the stochastic kind is made; everything
below is an exact count or an exhaustive enumeration.

## 0. Definitions, taken from the code, not from memory

F is defined in `scripts/s1_aux.c` (and every later script) as N[P_H] ∩ N[P_V] with **closed**
neighbourhoods of 3⁵ = 243 vertices. A pair (r, q) has its endpoints in opposite transversals, so
it contributes A(r, q) = N[r] ∩ N[q] to F on its own; F of a family is the union of these plus the
cross terms N[x] ∩ N[y] for x ∈ P_H, y ∈ P_V from different pairs.

The **shape** of a pair is d = q − r ∈ {0, ±1}⁵ ∖ {0}; k is its number of non-zero coordinates.

## 1. What I expect before computing, and why

**The cost of one pair is a closed formula.** Per coordinate, the closed neighbourhoods
{a−1, a, a+1} and {a+δ−1, a+δ, a+δ+1} in C₇ meet in 3 points if δ = 0 and in 2 if δ = ±1, so

  |A(r, q)| = 3^(5−k) · 2^k = 162, 108, 72, 48, 32 for k = 1, 2, 3, 4, 5.

**It falls with k.** The shape with two coordinates is in the middle, not at the minimum, and
the shape the brief suspects impossible (k = 1) is the most expensive one. **k = 1 private pairs
exist**: all seven candidates of the Mathew–Östergård 350-word set have k = 1 (Stage 2.2 table).

**Consequently arithmetic cannot close the direction, it opens it.** Nine pairs placed so that no
two endpoints of different pairs share a neighbour (some coordinate at circular distance 3) have
no cross terms and |F| = 9·|A|: 972 for k = 2 (already below 1000; the 1098 of Stage 2.2 is the
cross terms of the plateau's geometry), 648 for k = 3, 288 for k = 5. Overlaps only lower it. So
the answer to S2.3.b is decided by **existence**, which is S2.3.c.

**A geometric reading that S2.3.c rests on.** A word w occupies the box w + {0,1}⁵ of 32 cells and
two vertices are non-adjacent exactly when their boxes are disjoint. q with unique neighbour r
therefore has a box meeting the code's boxes only in box(r), in 2^(5−k) cells: a pair of shape k
needs 32 − 2^(5−k) = 16, 24, 28, 30, 31 uncovered cells in one box. A 367-word code leaves
16807 − 32·367 = 5063 cells uncovered, whatever its structure. Shape k is a statement about how
deep the deepest hole of the code is.

## 2. What the stage computes

**S2.3.a.** For every d ∈ {0,±1}⁵ ∖ {0}: |A(r, r+d)| counted directly on Z₇⁵ (not from the formula);
the orbits of the 242 shapes under the stabiliser of a vertex in Aut(C₇^⊠5), computed with the
group of `scripts/s2_2_aut.c`; and realisability, reported as **the largest independent set we
can exhibit carrying a private pair of each shape**, by the exhaustive local construction below.
For every code in `sets/` the histogram of candidate shapes and the histogram of covered cells per
box, c(v) = |box(v) ∩ ⋃ box(I)| (a candidate of shape k has c = 2^(5−k)).

**Local construction (exhaustive, exact).** For each of the 51 Aut-classes of 367-word codes from
Stage 2.2 and the codes of other sizes in `sets/`, for every word r and every shape d: put
q = r + d, delete the other words adjacent to q, then add back a maximum independent set of the
freed vertices that are not adjacent to q (exact branch and bound; freed vertices lie next to the
deleted words, since the codes are maximal). The result keeps (r, q) private. The maximum size per
k is the realisability figure; every set it rests on goes through `scripts/verify`, and its pair is
re-checked to be private by a second code path.

**S2.3.b.** For each k: 9·|A| (no cross terms), and the measured |F| of the nine-pair regions of
Stage 2.2 split into the per-pair part and the cross terms, so that the 1098 is accounted for.

**S2.3.c.** Only the necessary conditions the above gives (sizes reached with one cheap pair; how
the hole depth of known 367-word codes compares with what shape k needs). A search for a 367-word
code with nine pairs of shape k ≥ 3 is **not** run here; if warranted it is a separate stage.

## 3. Predictions

| # | prediction | confidence |
|---|---|---|
| P1 | the direct count gives 162, 108, 72, 48, 32, and 108 at k = 2 (the calibration) | 99% |
| P2 | orbit sizes under the vertex stabiliser are C(5,k)·2^k = 10, 40, 80, 80, 32 | 95% |
| P3 | k = 1 is realisable — at 350 by MO, and by the local construction at ≥ 366 | 80% |
| P4 | no known 367-word code has a candidate of shape k ≠ 2 (Stage 2.2 says so for the plateau; the population adds nothing) | 95% |
| P5 | the local construction does **not** reach 367 for any k ≥ 3; it reaches 366 for k = 3 | 55% for the pair of statements; 85% for "not 367 for k ≥ 3" |
| P6 | the arithmetic verdict: |F| below 1000 is possible for nine pairs of every shape k ≥ 2, so the direction is not closed by arithmetic, and the stage ends on existence, not on cost | 95% |

**Architect's predictions, as given:** no k = 1 private pairs (medium-high); cost grows with k,
so two coordinates is already minimal (~60%); the direction closes by arithmetic (~55%).

All three disagree with mine, and the first two for a stated reason: the closed formula and the
MO set, both on record before this file. They are kept as given and will be scored.

## 4. Calibration and anti-vacuum

1. The direct count must give 108 at k = 2 (the number Stage 2.2 measured), else nothing counts.
2. Stage 2.2's 1098 must be reproduced as per-pair part plus cross terms by the decomposition.
3. The local construction must reproduce 367 for k = 2 (the known candidates are such pairs), and
   must **not** report a private pair when the pair is not private: every output is re-checked by
   counting the I-neighbours of q in Python.
4. The orbit computation must give 242 shapes in total and reject a non-automorphism as above.

## 5. Budget and stopping

One evening of computation, ceiling **4 core-hours**. No ceiling raised after seeing results.

## 6. Outcomes, fixed in advance

* a shape with smaller |A| realisable at 367 → S2.3.c becomes the brief of a separate search stage;
* realisable only below 367 → the price is stated in words of code size, and the direction is
  open on cost, open on existence, with the measured gap;
* the count fails its calibration → the count is fixed first.

# METHODS — how the known bounds on Θ(C₇) were obtained, and where each method stops

Stage 0, item S0.3. This is a map, not an implementation, and it makes no choice for Stage 1;
the choice is made in the preregistration. Every number here carries a tag into `SOURCES.md`,
where it is backed by a verbatim quotation from a dumped source.

The target. Θ(C₇) = sup_d α(C₇^⊠d)^(1/d), bracketed by

    3.2588326203532663…  ≤  Θ(C₇)  ≤  ϑ(C₇) = 3.3176672073940953…
    [T26-2]                             [PS19-2, recomputed in results/json/theta.json]

The upper bound has not moved since Lovász 1979. Everything below is about the lower bound.

---

## 1. Exact independence numbers (exhaustive search)

**What it gives.** The only exactly known values for C₇ are α(C₇) = 3, α(C₇^⊠2) = 10 and
α(C₇^⊠3) = 33 [PS19-4]; the second follows from the closed form ⌊(n²−n)/4⌋ of Baumert et al.
[PS19-4], the third from exhaustive search by the same authors [MO17-4].

**What it costs.** A maximum independent set in C₇^⊠d over 7^d vertices. `scripts/mis` proves
α(C₇) = 3 and α(C₇^⊠2) = 10 in milliseconds, and reproduces the d = 2 row of [MO17-3] for
n = 5, 9, 11, 13 (5, 18, 27, 39) in at most 1.3 s.

**Where it stops.** At d = 3 for n = 7. Our own run on C₇^⊠3 (343 vertices) is reported in
`RESULTS.md`; **α(C₇^⊠4) is not known at all**, only 108 ≤ α(C₇^⊠4) ≤ 115 [IRCR26-3, PS19-4,
PS19-9]. Nothing in this line will produce a capacity bound: even the exact value 33 gives
only 33^(1/3) ≈ 3.2075.

## 2. Linear and Cayley constructions over Z_n

**What it gives.** α(C₇^⊠5) ≥ 7³ = 343, Baumert et al. 1971 [PS19-3].

**Why it is cheap.** A linear code is closed under subtraction, so independence collapses from
a statement about pairs to a statement about single codewords: every nonzero codeword must have
a coordinate at circular distance ≥ 2 from 0. `scripts/construct_c7_d5_343.py` finds such a
3-dimensional code over Z₇ by a deterministic lexicographic sweep in under a second, and the
two proofs of its independence — the algebraic one and the verifier's — are required to agree.

**Where it stops.** Rigidity. The best unstructured set in the same dimension has 367 elements
[PS19-1], 7% more, and the algebraic ansatz cannot express it. Linear constructions are a floor,
not a frontier.

## 3. Circular graphs and homomorphisms (Polak–Schrijver, 2019)

**What it gives.** α(C₇^⊠5) ≥ 367, and with it Θ(C₇) ≥ 367^(1/5) > 3.2578 [PS19-1]. This was
the record for seven years and is still the base of everything in §6 and §7.

**The idea.** Work in the circular graph C_{k,n} (vertex set Z_n, adjacency at distance < k)
where a one-parameter family is available: S = {t·(1,q,q²,q³,q⁴) : t ∈ Z_n} [PS19-5]. Since
ᾱ(C_{k',n'}) → ᾱ(C_{k,n}) exactly when n'/k' ≤ n/k, an independent set in C_{k,n}^⊠d folds into
one in C_⌈2n/k⌉^⊠d by i ↦ ⌊2i/k⌋. For n = 382, k = 108 the ratio 382/108 is just above 7/2, so
the fold is lossy and has to be repaired [PS19-6].

**What needs computing.** (a) the minimum distance k(n,d,q) of the one-parameter family, over a
range of (n,d,q) — this is the search that found (382, 5, 7); (b) after folding, a maximum
independent set in the small "extension graph" of words that may still be added — 71 vertices
and 85 edges here, α = 40, solved by Gurobi in the paper [PS19-6].

**Reproduced here.** `scripts/construct_c7_d5_ps.py` runs steps (i)–(v) from the circular graph
and lands on 327 + 40 = 367, with the extension graph coming out at exactly 71 vertices and 85
edges. The maximum independent set of that graph is not unique, so the set obtained differs
from the printed one in two words.

**Where it stops.** The authors report that no 368 was found over many choices of translation
and division factor, and that R is not extendable even after removing any three words
[PS19-8]. The same family does give new bounds elsewhere — α(C₁₁^⊠5) ≥ 4009 from
(n,d,q) = (4009, 5, 27) [PS19-10] — but not for C₇ beyond 367.

## 4. Stochastic search with prescribed symmetry

**What it gives.** α(C₇^⊠4) ≥ 108 by simulated annealing (Vesel–Žerovnik 2002) [MO17-4, T26-4];
α(C₇^⊠5) ≥ 350 by stochastic local search with prescribed symmetries (Mathew–Östergård 2017)
[MO17-1, MO17-5, PS19-3].

**What needs computing.** Long local-search runs on 7^d vertices. Prescribing a symmetry group
shrinks the search space to orbits and is what makes d = 5 reachable at all [MO17-5]; the cost
is that the method can only find packings that actually have the prescribed symmetry.

**Where it stops.** It was overtaken in its own dimension: 350 → 367 by a structural argument
[PS19-3]. In 2026 Itty et al. report that their own simulated annealing, and an LLM-designed
local search (CPro1), failed for more than three months to reach the bounds they eventually
obtained another way [IRCR26-7]. Plain local search is not where the remaining headroom is.

## 5. Upper bounds and the asymptotic spectrum

**What it gives.** ϑ(C₇) < 3.3177 [PS19-3, MO17-2], recomputed here to 3.3176672073940953…;
per-dimension ceilings α(C₇^⊠d) ≤ ϑ(C₇)^d [PS19-9] (401 at d = 5) and the recursive ceiling
α(C_n^⊠d) ≤ α(C_n^⊠(d−1))·n/2 [PS19-9] (115 at d = 4).

**Where it stops.** For the lower-bound programme these matter only as a ceiling: the gap
between 3.2588 and 3.3177 is where all the room is, and no upper-bound method has closed it.
Whether Θ(G) > threshold is even decidable is open (Alon–Lubetzky, cited in [IRCR26] §2).

## 6. LLM-driven search (2024–2026)

**What it gives.** FunSearch rediscovered 367 and improved α(C₁₁^⊠4) to 754 [IRCR26-6]; a later
system improved α(C₁₅^⊠5) to 19946 [IRCR26-6]. Neither improved a *capacity*. Then Itty, Rosin,
Carstensen and Reichman obtained 134753 in C₇^⊠10, 21909 in C₁₁^⊠6, 62530 in C₁₃^⊠6 and
8076974 in C₁₅^⊠8 through the ChatGPT web interface, specifying cycle length, dimension, the
best known construction and the target cardinality [IRCR26-1, IRCR26-5].

**What it costs.** Wall-clock interaction, not compute on our side; the model wrote and ran the
search programs. The authors verified the resulting sets themselves [IRCR26 §1].

**What actually happened, structurally.** The C₇^⊠10 set is *not* an unstructured find. It is
R × R with eight words deleted from each factor and the lost mass replaced by two families
built around eight private pairs: 359² + 2·8·367 = 134753 [IRCR26-2, T26-5]. Gao's reading of
it (§7) makes this explicit. **This is the lesson of the 2026 episode: the gain came from
exploiting the structure of the 367-set, not from searching a 7^10-vertex graph.**

## 7. Recursive gadget products (Gao 2026; Buys–Polak–Zuiddam; Tandon) — the current frontier

**The object.** A *gadget* in a graph G is a code I (an independent set, |I| = a), t private
pairs (r_i, q_i) with N({q_i}) ∩ I = {r_i}, two complementary independent transversals P_H, P_V
of the 2t endpoints, and an independent auxiliary set X of size s that meets N(P_H) ∩ N(P_V)
nowhere; X splits as o + h + v according to which transversal it can see. The parameter tuple
is (a, t, s, o, h, v) [G26-1].

**The engine.** Two gadgets multiply into one, in the strong product of their graphs, with

    a₁₂ = (a₁−t₁)(a₂−t₂) + t₁s₂ + s₁t₂,   t₁₂ = t₁o₂ + o₁t₂,   s₁₂ = s₁s₂,
    o₁₂ = o₁o₂ + (h₁+v₁)(h₂+v₂),          h₁₂ = h₁o₂ + o₁v₂,   v₁₂ = v₁o₂ + o₁h₂   [G26-2]

and the whole construction becomes a dynamic programme over split trees on integers [G26-7].
The five-dimensional base gadget is the Polak–Schrijver set with the eight pairs of Itty et al.:
(a,t,s,o,h,v) = (367, 8, 367, 321, 26, 20) [G26-3]. Two copies of it give exactly the set of
Itty et al.: (367−8)² + 2·8·367 = 134753 [G26-5].

**What needs computing.** Almost nothing, at the top. The recursion is integer arithmetic;
`scripts/gadget.py` reproduces Gao's M₄₀ — a 103-digit integer — and the bound
3.2587891539086910161967650155206769… in well under a second, and the Buys–Polak–Zuiddam value
3.2588053698854655725829750306… from their stronger base profile (367, 8, 367, 322, 26, 19)
[BPZ26-2, T26-6]. The **only** expensive part is finding a better base gadget in low dimension.

**The ceiling is not the number of blocks.** Gao proves that the balanced product converges to
≈ 3.2586163193818… — *below* his own theorem — and that continuing from the 200-dimensional
gadget strictly loses (3.2587703784… at dimension 400) [G26-10]. Our dynamic programme run to
160 blocks agrees: the maximum over k is attained exactly at k = 40, dimension 200
(`results/json/gadget.json`, `saturation`). **Adding dimensions is not a lever.**

**What the last two papers changed.** Buys–Polak–Zuiddam moved one number of the base profile,
o from 321 to 322 (equivalently v from 20 to 19), and gained 1.6·10⁻⁵ [BPZ26-3, T26-6]; they
also formalised the whole chain in Lean [BPZ26-1]. Tandon observed that different occurrences
of an intermediate gadget inside the recursion need not use the same representation —
*heterogeneous* refinement — and gained again, to 3.2588326203532663… in dimension 500
[T26-7, T26-2].

**Where it stops.** Nobody knows. The three published gains since July 2026 are each in the
fifth decimal place, and all three came from the *structure carried by the gadget*, not from
its code size. Tandon's closing remark is that recursive zero-error construction should be
treated as multi-objective rather than as a sequence of locally optimal choices [T26-7].

---

## What this map says about where compute would go

| method | the expensive object | size of that object | verifiable by us? |
|---|---|---|---|
| exact α | C₇^⊠d, d ≤ 3 | 343 vertices | yes, `scripts/mis` |
| linear codes | subspaces of Z₇^5 | 10⁵ | yes, seconds |
| circular graphs | (n,d,q) sweep + a small MIS | 71-vertex graph | yes, seconds |
| stochastic search | C₇^⊠5 … C₇^⊠10 | 10⁴ … 10⁸ vertices | sets: yes, up to d ≈ 12 |
| gadget recursion | **a base gadget in d = 5** | 16807 vertices | yes, exactly |
| gadget recursion | the resulting code | 10¹⁰³ words at d = 200 | **no — never materialised** |

The last two rows are the whole point. The record now lives in an object of 10¹⁰³ words that
nobody will ever write down, but it is *generated* by a gadget on 16807 vertices that fits in
a few kilobytes and that `scripts/gadget.py` checks exactly. A Stage 1 that searched for large
independent sets in high dimensions would be aiming at the wrong object.

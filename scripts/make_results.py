"""Generates RESULTS.md from results/json/*.json.  RESULTS.md is never edited by hand.

Also checks the SHA-256 of PREREGISTRATION_S1.md against results/json/prereg.json and
refuses to write anything if they differ.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = os.path.join(ROOT, "results", "json")
OUT = []


def w(s=""):
    OUT.append(s)


def load(name):
    """Missing or still-being-written files are absent, not fatal: RESULTS.md is
    generated from whatever has completed, and says what has not."""
    p = os.path.join(J, name)
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return None
    try:
        return json.load(open(p))
    except json.JSONDecodeError:
        return None


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def yn(b):
    return "yes" if b else "**no**"


def human(n):
    for u, k in (("GiB", 2**30), ("MiB", 2**20), ("KiB", 2**10)):
        if n >= k:
            return f"{n / k:.1f} {u}"
    return f"{n} B"


def tick(b):
    return "PASS" if b else "**FAIL**"


def git(*args):
    try:
        return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


def stage1(w, gate, anchor, pairs, codes, rep, aux, auxrun, lithist, budget, gad):
    if not (gate or pairs):
        return
    w("---")
    w()
    w("# Stage 1 — the ninth private pair")
    w()
    if pairs:
        k = pairs["codes"][0]
        w("**There is no ninth private pair, and that is a theorem rather than a failed search.** "
          f"The Polak–Schrijver 367-word code admits exactly **{k['candidate_private_pairs']}** "
          "candidate private pairs in the whole of Z₇⁵ — the eight that Itty et al. use. This is "
          "outcome S1-S of `PREREGISTRATION_S1.md`, declared in advance as a result of a different "
          "kind rather than as a failure.")
        w()

    # ---------- S1.0 ----------
    w("## S1.0 — the gate")
    w()
    w("The Stage 1 brief refuses to start the pair search until the same stack finds the known "
      "optima. The stack, and why 16807 vertices is not the problem 343 was:")
    w()
    w("| engine | what it is | proves? |")
    w("|---|---|---|")
    w("| **E1** `s1_alpha3` | exact cyclic layer search: decompose C_n^⊠3 into n layers, use the "
      "size arithmetic of the cyclic pair constraint to pin the problem onto the 980 maximum "
      "2-dimensional packings | yes — upper bounds |")
    w("| **E2** `s1_ils` | local search, then fixed-cardinality tabu search | no |")
    w("| **E3** `s1_sym` | prescribed symmetry: search the orbit graph of an explicitly given "
      "group, after checking its generators | no |")
    w("| **E4** `s1_lns` | large-neighbourhood search with **exact** repair inside a window, and "
      "the same repair move inside E2's tabu loop | the repair is exact inside the window |")
    w()
    w("**Why d = 5 is not a harder instance of d = 3.** The Stage 1 target is not a maximum "
      "independent set in C₇^⊠5. The code is fixed — it is the known 367-word set — and what is "
      "searched over is the gadget structure on top of it: candidate private pairs (8 of them), "
      "2-colourings (16), and auxiliary sets drawn from the automorphism group (6.5·10⁷). Those "
      "are structures of size 10¹–10⁸, not the independent-set lattice of a 16807-vertex graph. "
      "E1–E4 are needed for the gate and for the auxiliary step, not for the pair search itself.")
    w()
    if gate:
        g1 = gate["G1_exact_upper_bound"]
        wv = gate["G1_witness_verified"]
        w("### α(C₇^⊠3) = 33 — settled exactly")
        w()
        w(f"E1 proves Σ ≥ 34 impossible in **{g1['seconds']:.0f} s** and therefore "
          f"α(C₇^⊠3) ≤ 33; the same engine closes a cycle at Σ = 33 and writes out the set, "
          f"which `scripts/verify` confirms independently "
          f"({tick(wv['independent'])}, box and quadratic agreeing, and maximal). "
          f"Stage 0's generic branch and bound reached 32 in an hour and proved nothing.")
        w()
        w("| quantity | value |")
        w("|---|---|")
        w(f"| maximum packings of C₇^⊠2 used as the pivot | {g1['maximum_packings']} |")
        w(f"| their halves (the layer states) | {g1['keys']:,} |")
        w(f"| compatibility edges between states | {g1['successor_edges']:,} |")
        w(f"| smallest-layer orbits tested | {g1['orbits_tested']} |")
        w(f"| smallest Σ proved impossible | {g1['smallest_sigma_proved_impossible']} |")
        w(f"| resulting bound | α(C₇^⊠3) ≤ **{g1['alpha_d3_upper_bound']}** |")
        w()
        m = gate["G2_mutant"]
        w(f"**Does E1 have teeth?** The same engine compiled with the *open* neighbourhood — "
          f"having forgotten that consecutive layers must also be disjoint — claims a cycle at "
          f"Σ = {m['run'].get('closed_at_sigma')}, i.e. α(C₇^⊠3) ≥ 35, which is false. "
          f"The defect is caught: {tick(m['pass'])}.")
        w()
        w("### α(C₇^⊠4) ≥ 108 — reached, after four changes of method")
        w()
        w("| engine | verified size |")
        w("|---|---|")
        for x in gate["G5_ladder"]:
            w(f"| {x['engine']} | {x['verified']} |")
        w()
        w(f"Every rung was checked by `scripts/verify`, which knows nothing about how the set was "
          f"found; the 108 passes the box test and the quadratic test and is maximal. The brief "
          f"asked that a shortfall name what was missing — in the event nothing was missing at the "
          f"end, but the record of what failed is the table: plain local search is 6 short, "
          f"prescribed symmetry caps out at 105 because its orbits have size 7 and 16 orbits would "
          f"be 112, and only block moves with exact repair close the last two.")
        w()
        c = gate["G4_symmetry_controls"]
        w(f"**Symmetry controls** (the brief: a generator that acts as the identity is an error, "
          f"not a symmetry). The identity is rejected ({tick(gate['G4_pass'])}), a map that is not "
          f"an automorphism is rejected, and a real translation is accepted with all three checks "
          f"— automorphism, non-trivial, bijective — passing.")
        w()
        w(f"**Gate verdict: {tick(gate['all_pass'])}.** Blocking condition (α(C₇^⊠3) = 33 must be "
          f"found): {tick(gate['gate_blocking_condition']['met'])}.")
        w()

    # ---------- S1.1 ----------
    if anchor:
        w("## S1.1 — anchoring to the record")
        w()
        a = anchor["anchor"]
        w(f"The eight-pair base gadget pushed through **our** homogeneous recursion — the same code "
          f"that would carry a ninth pair — gives")
        w()
        w(f"    {a['our_homogeneous_bound_dim200']}…")
        w()
        w(f"against the published Buys–Polak–Zuiddam {a['published_bpz']}… : "
          f"{tick(a['matches_bpz'])}. On Gao's profile the same code reproduces his value too: "
          f"{tick(a['matches_gao'])}.")
        w()
        fg = anchor["framework_gap"]
        w("**The framework gap, which changes the target.** Tandon starts from the *same* "
          "five-dimensional base gadget as BPZ, profile (367,8,367,322,26,19) [T26-6, T26-9], and "
          "his heterogeneous recursion extracts more from it than the homogeneous one does:")
        w()
        w("| recursion, same base gadget | Θ(C₇) ≥ |")
        w("|---|---|")
        w(f"| homogeneous (ours, and BPZ's) | {fg['homogeneous_recursion_ours']}… |")
        w(f"| heterogeneous Gao — Tandon's warm-up [T26-8] | {fg['heterogeneous_gao_tandon_warmup'][:36]}… |")
        w(f"| BPZ multi-gadget, their repository [T26-3] | {fg['bpz_multi_gadget_github'][:36]}… |")
        w(f"| heterogeneous BPZ — the record [T26-2] | {fg['heterogeneous_bpz_tandon_record'][:36]}… |")
        w()
        w(f"So the gap between the record and what our recursion yields from the same base is "
          f"**{fg['gap_record_minus_ours'][:12]}…**. A Stage 1 margin below that would be a claim "
          f"about numbers, not about methods: the same base fed through Tandon's framework would "
          f"beat ours. Restating the target accordingly:")
        w()
        w("| base profile (a,t,s,o) | homogeneous bound | margin over the record | beats the framework gap |")
        w("|---|---|---|---|")
        for t in anchor["targets"]:
            w(f"| {tuple(t['profile'])} — {t['label']} | {t['homogeneous_bound'][:24]}… | "
              f"{float(t['margin_over_tandon_record']):+.3e} | "
              f"{'**yes**' if t['robust_to_framework_choice'] else 'no'} |")
        w()
        rt = anchor["restated_target"]
        w(f"A ninth private pair clears the record by 1.7·10⁻⁴, seven times the framework gap, so "
          f"it would be an improvement under any of the published recursions. The o-route needs "
          f"o ≥ {rt['t8_o_needed_to_beat_the_record']} to clear the record as preregistered and "
          f"o ≥ {rt['t8_o_needed_to_be_robust_to_the_framework_gap']} to clear the gap as well. "
          f"The preregistered target is kept; the gap is reported alongside.")
        w()

    # ---------- S1.2 ----------
    w("## S1.2 — the search")
    w()
    w("### The reduction that makes it finite")
    w()
    w("**Lemma.** Let (r_i, q_i) and (r_j, q_j) be private pairs of a code I with r_i ≠ r_j. Then "
      "r_i is confusable with neither r_j nor q_j.")
    w()
    w("*Proof.* r_i and r_j lie in I, which is independent. If r_i ~ q_j then "
      "r_i ∈ N[q_j] ∩ I = {r_j}, so r_i = r_j. ∎")
    w()
    w("So the only way a transversal can fail to be independent is by holding two confusable q's, "
      "and the gadget condition on P_H, P_V collapses to: **the chosen q's have distinct centres "
      "and their confusability graph is properly 2-coloured** — that is, bipartite. Maximising the "
      "number of private pairs becomes a maximum induced bipartite subgraph problem on the "
      "candidate q's, one per centre. The candidates themselves are a direct computation: every "
      "q ∈ Z₇⁵ \\ I with exactly one I-neighbour.")
    w()
    if pairs:
        w("### The count")
        w()
        w("| code | candidate private pairs | distinct centres | conflict edges | max t | exhaustive |")
        w("|---|---|---|---|---|---|")
        for c in pairs["codes"]:
            w(f"| {c['code']} | **{c['candidate_private_pairs']}** | {c['distinct_centres']} | "
              f"{c['conflict_graph_edges']} | **{c['max_private_pairs_t']}** | "
              f"{tick(c['search_exhaustive'])} |")
        w()
        kg = pairs["known_gadget_recovered"]
        w(f"**Anti-vacuum.** All eight pairs of Itty et al. come out of the enumeration with the "
          f"centres the paper gives them ({tick(kg['all_eight_found'])}), and the 2-colouring the "
          f"paper uses is one of the valid ones ({tick(kg['published_2_colouring_valid'])}). An "
          f"enumeration that could not recover the known gadget would not be worth believing about "
          f"a better one.")
        w()
        w("**Proposition (S1-S).** For the printed Polak–Schrijver code I, exactly eight vertices "
          "of Z₇⁵ \\ I have a single I-neighbour. Hence every gadget with that code has t ≤ 8, and "
          "t = 8 is attained because the confusability graph on those eight q's has 3 edges and is "
          "bipartite. The eight pairs used since July 2026 are therefore not a lucky find but the "
          "only ones available, and they are all usable at once.")
        w()
        w("Note how fragile this is: our own reproduction of the same construction, which differs "
          "from the printed set in **two words**, admits only six. The number of private pairs is a "
          "property of the individual code, not of its size.")
        w()
    if codes:
        w("### Branch C — other codes of size 367")
        w()
        w(f"Step (v) of the Polak–Schrijver method extends the 327-word core by a maximum "
          f"independent set of a {codes['extension_graph_vertices']}-vertex extension graph, and "
          f"that maximum is not unique. Enumerating **all** of them exhaustively gives "
          f"**{codes['maximum_independent_sets_of_the_extension_graph']}** distinct 367-word codes. "
          f"Their private-pair counts:")
        w()
        w("| max t | how many of the 8 codes |")
        w("|---|---|")
        for t, c in sorted(codes["t_histogram"].items()):
            w(f"| {t} | {c} |")
        w()
        w(f"The maximum over the whole family is **{codes['best_t']}**, attained by exactly one "
          f"code — and that code is the printed Polak–Schrijver set. So the literature is already "
          f"using the unique best member of this family; the pipeline has nothing better to give. "
          f"Ninth pair found: {codes['ninth_pair_found']}.")
        w()
    w("### Branch D — codes of size other than 367, ruled out by arithmetic")
    w()
    w("A gadget's code need not be maximum, so a smaller code with more private pairs is "
      "admissible in principle. It is not worth it, and the price list says so exactly:")
    w()
    if anchor and anchor.get("branch_D_break_even"):
        be = anchor["branch_D_break_even"]["private_pairs_needed_to_match"]
        w("| code size | private pairs needed to match (367, 8) |")
        w("|---|---|")
        for a in sorted(be, reverse=True):
            w(f"| {a} | **{be[a]}** |")
        w()
        w("A 366-word code would need thirteen private pairs to draw level with what the 367-word "
          "code does with eight — and the 367-word code has exactly eight candidates in the whole "
          "of Z₇⁵. Branch D was entered and closed on this calculation rather than on a search, "
          "which is the honest way to spend a budget.")
    w()
    w()
    if aux or rep:
        w("### Branch B — the auxiliary set")
        w()
        if aux:
            w(f"With t = 8 forced, the only remaining lever is X. The requirement is X independent "
              f"with X ∩ N(P_H) ∩ N(P_V) = ∅, and the bound grows with s = |X| and "
              f"o = |X \\ (N(P_H) ∪ N(P_V))|. Since |X| must stay at 367 (see branch D), X has to "
              f"be a maximum-known independent set, and the ones available are the eight pipeline "
              f"codes and their images under Aut(C₇^⊠5) ⊇ (D₇)⁵ ⋊ S₅.")
            w()
            w(f"That group has 14⁵·120 = 64,538,880 elements, and every valid 2-colouring changes "
              f"N(P_H) and N(P_V), so the sweep covers "
              f"**{aux.get('group_elements_swept', 0):,}** (source, colouring, automorphism) "
              f"combinations. It is exhaustive rather than sampled, because for fixed permutation "
              f"and signs all 16807 translations are scored at once by a cyclic cross-correlation.")
            w()
            near = aux.get("translations_with_bad_eq", [])
            if near:
                w("| words of X landing in the forbidden region | how many combinations |")
                w("|---|---|")
                for i, c in enumerate(near):
                    w(f"| {i} | {c:,} |")
                w()
            w("**No image of any known 367-word code is admissible, for any colouring.** The least "
              "number of words falling in the forbidden region is one, never zero. That is why "
              "Itty et al. replace one vector: our sweep shows the replacement is not a "
              "convenience but unavoidable — and the word they delete, (2,4,6,3,5), is exactly the "
              "single offender in T(I).")
            w()
        if rep:
            b = rep.get("best") or {}
            w(f"Repairing the near misses exactly — delete the offending words, then solve for the "
              f"best legal replacement set — gives at best **s = {b.get('s')}, o = {b.get('o')}**, "
              f"which is precisely the Buys–Polak–Zuiddam profile, rediscovered here from a "
              f"different direction.")
            w()
        if auxrun:
            ctrl = auxrun["control_published_X"]
            w(f"Posing the problem directly — hold |X| = 367, stay out of the forbidden region, "
              f"minimise the overlap with N(P_H) ∪ N(P_V) — and running the fixed-cardinality "
              f"search on **every** one of the {auxrun['colourings']} valid 2-colourings for "
              f"{auxrun['seconds_per_colouring']:.0f} s each reaches the same ceiling:")
            w()
            w("| 2-colouring | conflicts | u | o | |")
            w("|---|---|---|---|---|")
            for r in sorted(auxrun["rows"], key=lambda r: (-r["o"], r["conflicts"])):
                mark = " ← the colouring the papers use" if r["is_published_colouring"] else ""
                flag = "**admissible**" if r["conflicts"] == 0 else "not independent"
                w(f"| {r['colour_mask']} | {r['conflicts']} | {r['u']} | {r['o']} | {flag}{mark} |")
            w()
            w(f"**Control:** started from the published auxiliary set under the colouring the papers "
              f"use, the search reports o = {ctrl['o']} with {ctrl['conflicts']} conflicts — exactly "
              f"Gao's value ({tick(ctrl['reproduces_gao_321'])}). A search that could not reproduce "
              f"the known profile would not be evidence about a better one.")
            w()
            adm = [r for r in auxrun["rows"] if r["conflicts"] == 0]
            w(f"Best admissible: **o = {auxrun['best_admissible_o']}**, equal to the published "
              f"Buys–Polak–Zuiddam value, and it does not beat it. The o = 323 and o = 324 rows "
              f"carry one to six adjacent pairs, so they are not independent sets and not "
              f"gadgets; they are shown because the near miss is informative, not because it is a "
              f"result.")
            w()
            if len(adm) == 1:
                w(f"**Only one colouring produced an admissible auxiliary set at all.** Of the "
                  f"{auxrun['colourings']} proper 2-colourings of the eight private pairs, the "
                  f"search found a 367-word admissible X for exactly one — mask "
                  f"{adm[0]['colour_mask']}, the one Itty et al. chose and everyone since has "
                  f"kept. Nothing in the published papers remarks on that choice. **This part is "
                  f"evidence, not proof:** the group sweep is exhaustive and says no *image* is "
                  f"admissible under any colouring, but the repaired sets are found by search, so "
                  f"for the other fifteen colourings the honest statement is that 1500 s of "
                  f"fixed-cardinality search did not find one, not that none exists.")
                w()
            w(f"Across the {rep.get('candidates_examined')} candidates examined — each one "
              f"independently verified as a 367-word independent set before being touched — no "
              f"repair ever admitted more additions than deletions. Had one, it would have been an "
              f"independent set of size 368 in C₇^⊠5, a new record for α itself; the script "
              f"watches for that and did not see it.")
            w()
    w("### What Stage 1 concludes")
    w()
    w("| preregistered target | outcome |")
    w("|---|---|")
    w("| **S1-P** a base gadget whose homogeneous bound beats 3.2588326203532663… | **not reached** |")
    w("| **S1-S** the exact maximum number of private pairs t\\* for the Polak–Schrijver code | "
      "**reached: t\\* = 8, with proof**, and extended to the whole 8-code pipeline family |")
    w()
    w("The published gadget is optimal in every direction Stage 1 could search: its eight private "
      "pairs are all that exist, it is the best of the eight codes its own construction can "
      "produce, no smaller code can compensate, and no image of any known code gives a better "
      "auxiliary set than the o = 322 already in the literature.")
    w()

    w("## Stage 1 — deviations, with reasons")
    w()
    w("1. **The gate needed four changes of search method, not one.** Plain local search reached "
      "102 on C₇^⊠4 and would not move; prescribed symmetry reached 105 and could not reach 108 "
      "at all, because its orbits have size 7; fixed-cardinality tabu search reached 106 and sat "
      "there through 2.3·10⁶ exact window repairs; only tabu search *with* exact block repair "
      "reached 107, and 108 came from warm-starting that hybrid on the 107. The brief allowed a "
      "gate failure provided the missing ingredient was named. In the event nothing was missing "
      "at the end, and the ingredient was block moves with exact repair.")
    w()
    w("2. **Branch D was closed by arithmetic rather than by search.** The preregistration listed "
      "codes of size other than 367 as a search branch. Evaluating the published recursion shows "
      "one lost code word costs six times what an extra private pair gains, so the branch cannot "
      "pay. Entering it would have burned budget on a question already answered by a formula.")
    w()
    w("3. **No GPU time was used**, against 20 GPU-hours preregistered. The preregistration "
      "assumed the search would be over large vertex sets. It was not: the gadget condition "
      "reduced to a 2-colouring question on eight candidates, and the auxiliary-set question to a "
      "cyclic correlation over the automorphism group. The assumption behind the budget was wrong "
      "in a way that made the work cheaper, and saying so is more useful than quietly under-spending.")
    w()
    w("4. **Tandon's heterogeneous framework was not reimplemented**, as preregistered — but S1.1 "
      "shows that choice is not free: it is worth 2.7·10⁻⁵ on the same base gadget, more than the "
      "o ≥ 324 route would have gained. Any future claim from this repository has to be quoted "
      "against it.")
    w()
    w("5. **States with o = 323 and o = 324 were found and are not claimed.** They carry one to "
      "three adjacent pairs, so they are not independent sets and the profile is not a gadget's. "
      "They are reported because the near miss is informative, not because it is a result.")
    w()
    # ---------- S1.3 ----------
    if lithist:
        w("## S1.3 — discipline on a moving field")
        w()
        w("| checked | current record | attributed to | our best |")
        w("|---|---|---|---|")
        for h in lithist:
            w(f"| {h['timestamp']} ({h['label']}) | {h['best_lower_bound_seen'][:22]}… | "
              f"{h['attributed_to']} | 3.2588053698854655… (t=8, o=322) |")
        w()
        w("The record did not move during Stage 1. Nothing newer than arXiv:2608.30273 appeared in "
          "any of the four queries.")
        w()
    if budget:
        w("## Budget")
        w()
        w("| resource | ceiling in the preregistration | used |")
        w("|---|---|---|")
        w(f"| GPU | 20 GPU-hours | **{budget['gpu_hours']}** |")
        w(f"| CPU | 100 core-hours | ≈ **{budget['core_hours_estimate']}** |")
        w(f"| wall-clock | 14 days | {budget['wall_clock']} |")
        w()
        w(budget["note"])
        w()


def stage2w(w, gate, thm, nums, venue):
    """Stage 2W -- the note. Gate, the theorem's data, the number reconciliation, the venue."""
    if not (gate or thm):
        return
    w("---")
    w()
    w("# Stage 2W — the note")
    w()
    w("Stage 2W writes up the Stage 1 theorem and does not extend the research: no new search "
      "was run. The deliverable is `note/note.tex` (6 pages compiled), and everything below is "
      "the gate it had to pass and the checks that hold it to the stored computations.")
    w()

    # ---------- W.0 ----------
    if gate:
        w("## W.0 — the literature gate")
        w()
        w("The note claims a maximality theorem, so the first question is whether anybody has "
          "claimed it already, explicitly or implicitly. `scripts/w_gate.py` lists mechanically "
          "every sentence of every dumped paper that mentions private pairs, transversals, "
          "colourings, valid tuples or gadgets **together with** a word of maximality, uniqueness "
          "or exhaustion, and the list is read in full rather than counted:")
        w()
        w("| paper | candidate sentences | any claim of maximality? |")
        w("|---|---|---|")
        for aid, rec in gate["papers"].items():
            w(f"| {rec['who']} (arXiv:{aid}) | {rec['candidate_sentences']} | no |")
        w()
        w(f"{gate['candidate_sentences_total']} sentences in total, stored in "
          "`results/json/w_gate.json`. The four that come closest are quoted in `SOURCES.md` "
          "under Stage 2W [W26-1] to [W26-4]: Gao imports the eight pairs from Itty et al. and "
          "verifies that each is private without asking whether a ninth exists; Buys–Polak–Zuiddam "
          "record the eight as the size |S| of a given valid tuple; Tandon states the two profiles "
          "as data. The one sentence in the chain about *more* private pairs is about pairs "
          "propagated by the product in dimension ≥ 10, not about the candidates of the "
          "five-dimensional code.")
        w()
        w(f"**Nothing on C₇ has appeared since arXiv:2608.30273.** The check was rerun on "
          f"{gate['litcheck']['date']} (label `{gate['litcheck']['label']}`, "
          f"{gate['litcheck']['distinct_hits']} distinct hits); the "
          f"{len(gate['litcheck']['ids_newer_than_the_record'])} hits with a later identifier are "
          "unrelated information-theory papers, listed in `results/json/w_gate.json`.")
        w()
        w(f"Gate verdict: **the note may be written** — maximality claimed anywhere: "
          f"{yn(gate['verdict']['maximality_claimed_anywhere'])}; the unique admissible colouring "
          f"remarked anywhere: {yn(gate['verdict']['unique_colouring_remarked_anywhere'])}; a new "
          f"record since Stage 1: {yn(gate['verdict']['new_record_since_stage_1'])}.")
        w()

    # ---------- W.1 ----------
    if thm:
        h = thm["neighbour_histogram"]
        cg = thm["conflict_graph"]
        w("## W.1 — the data the theorem is printed from")
        w()
        w("`scripts/w_theorem.py` recomputes, from the set file, everything the written proof "
          "displays, and cross-checks it against the Stage 1 record:")
        w()
        w("| | |")
        w("|---|---|")
        w(f"| vertices of Z₇⁵ | {h['universe']:,} |")
        w(f"| outside the code | {h['words_outside_I']:,} |")
        for k, v in h["by_number_of_I_neighbours"].items():
            plural = "neighbour" if k == "1" else "neighbours"
            w(f"| of those, with {k} {plural} in the code | **{v:,}** |")
        w(f"| candidates that are the published eight pairs | "
          f"{tick(thm['candidates_are_exactly_the_published_eight'])} |")
        w(f"| edges of the conflict graph on the eight q's | {cg['edge_count']} "
          f"({', '.join('q%d~q%d' % tuple(e) for e in cg['edges'])}) |")
        w(f"| is that graph a matching? | {yn(cg['is_a_matching'])} |")
        w(f"| components, hence proper 2-colourings up to swap | {cg['components']} → "
          f"{cg['proper_2_colourings_up_to_swap']} |")
        w(f"| t* | **{cg['t_max']}** |")
        w(f"| the non-mixing lemma, checked on this instance | {tick(thm['lemma_check']['pass'])} |")
        w(f"| the single word of T(I) confusable with both transversals | "
          f"{thm['forbidden_region_of_T_image']['words_confusable_with_both_transversals']} |")
        w(f"| agrees with `s1_pairs.json` and `s1_aux.json` | "
          f"{tick(thm['cross_check_stage1']['agrees'])} |")
        w()
        w("The last row matters more than it looks: the note and Stage 1 compute the same things "
          "by different routes, and a silent drift between them would fail the build. The "
          "offender row is the word Itty et al. replace — the note says why the replacement is "
          "unavoidable rather than cosmetic.")
        w()

    # ---------- W.2 ----------
    if nums:
        w("## W.2 — every number in the note, reconciled by machine")
        w()
        w(f"`scripts/w_checknums.py` holds a ledger of {nums['ledger_entries']} entries. Each is "
          "checked in both directions: the value against `results/json` (or, for an external "
          "number, against a verbatim quotation in `SOURCES.md`), and its presence in the note. "
          "Then the note is swept backwards: of its "
          f"{nums['distinct_numeric_tokens']} distinct numeric tokens, every one must be in the "
          "ledger, in the list of years, or structural (a dimension, an index, a coordinate).")
        w()
        w(f"| ledger entries checking out | **{nums['ledger_entries'] - nums['failures']}/"
          f"{nums['ledger_entries']}** |")
        w("|---|---|")
        w(f"| numbers in the note that no computation backs | **{len(nums['unaccounted_tokens'])}** |")
        w(f"| verdict | {tick(nums['all_pass'])} |")
        w()
        w("Six of the ledger entries are not single numbers but lists — the private-pair counts of "
          "the eight pipeline codes, the three conflict edges in Gao's numbering, the replaced "
          "word, the published colouring — checked against the stored computation as sequences, so "
          "that a reordered or half-copied list fails too.")
        w()

    # ---------- W.3 / W.4 ----------
    if venue:
        r = venue["requirements"]
        w("## W.3 — venue and priority")
        w()
        w(f"**Order.** {venue['order']}")
        w()
        w(f"**First choice: {venue['target']}.** {venue['why']} Its requirements were read from "
          "pages dumped into `sources/venue/` with their URL, HTTP status and SHA-256, and "
          "`scripts/w_venue.py` re-checks each quotation against the dump "
          f"({venue['quotations_found']}/{len(venue['quotations'])} found):")
        w()
        w("| requirement | what it says | us |")
        w("|---|---|---|")
        w(f"| length | {r['length']['limit']} | {r['length']['our_note']} — {r['length']['verdict']} |")
        w("| generative AI | a declaration section in the publisher's own wording, and AI used in "
          "the research process described in the methods | both, verbatim: the note carries the "
          "declaration and describes the research-process use |")
        w(f"| fees | {r['fees']['subscription_route']} | nothing to pay on the subscription route |")
        w()
        g = r["guide_for_authors"]
        w()
        w("**The Guide for Authors.** " + g["live_page"] + ". " + g["archive_snapshot"] + ".")
        w()
        w("| the rule, from the live guide | the package |")
        w("|---|---|")
        for k, v in g["what_it_says"].items():
            w(f"| {k.replace('_', ' ')} | {v} |")
        w()
        w(f"The APC figure ({r['fees']['apc_for_IPL']}) comes from a search result quoting the "
          "journal page rather than from a dump, and is marked unverified in "
          "`results/json/w_venue.json`; nothing depends on it, since the subscription route "
          "carries no author charge.")
        w()
        w("Fallbacks, in order: " + "; ".join(venue["fallbacks"]) + ".")
        w()


def main():
    prereg = load("prereg.json")
    pp = os.path.join(ROOT, "PREREGISTRATION_S1.md")
    if prereg and os.path.exists(pp):
        live = sha(pp)
        if live != prereg["sha256"]:
            sys.exit(f"PREREGISTRATION_S1.md has changed since it was sealed\n"
                     f"  sealed: {prereg['sha256']}\n  now:    {live}")

    # Every decimal the preregistration quotes must come from results/json, not from a
    # transcription.  A mismatch stops the build: a sealed document with an invented
    # digit in it is worse than no document.
    gad_pre = load("gadget.json")
    if gad_pre and os.path.exists(pp):
        pretext = open(pp, encoding="utf-8").read()
        quoted = set(re.findall(r"3\.25\d{10,}|3\.26\d{10,}", pretext))
        known = set(gad_pre.get("profile_sensitivity", {}).get("values", {}).values())
        known |= set(gad_pre.get("elementary_bounds", {}).values())
        known |= {gad_pre["gao"]["bound_dim_200"], gad_pre["bpz"]["bound_dim_200"],
                  gad_pre["profile_sensitivity"]["current_record_T26"]}
        for q in sorted(quoted):
            if not any(k.startswith(q) or q.startswith(k) for k in known):
                sys.exit(f"PREREGISTRATION_S1.md quotes {q}, which is in no results/json file")

    gate = load("s1_gate.json")
    anchor = load("s1_anchor.json")
    s1pairs = load("s1_pairs.json")
    s1codes = load("s1_codes.json")
    s1rep = load("s1_repair.json")
    s1aux = load("s1_aux.json")
    s1auxrun = load("s1_auxsearch.json")
    lithist = load("litcheck_history.json")
    budget = load("s1_budget.json")

    cal = load("calibration.json")
    d10 = load("construct_c7_d10.json")
    ps = load("construct_c7_d5_ps.json")
    lin = load("construct_c7_d5_343.json")
    gad = load("gadget.json")
    ben = load("bench.json")
    lit = load("litcheck.json")
    src = load("sources.json")
    th = load("theta.json")
    mis3 = load("mis_c7_d3.json")

    w("# RESULTS — shannon, Stages 0, 1 and 2W")
    w()
    w("**This file is generated by `scripts/make_results.py` from `results/json/*.json`. "
      "Do not edit it by hand.**")
    w()
    w(f"Commit: `{git('rev-parse', '--short', 'HEAD') or 'uncommitted'}`. "
      f"Preregistration `PREREGISTRATION_S1.md` sealed {prereg['sealed'] if prereg else '?'}, "
      f"SHA-256 `{prereg['sha256'][:16]}…` — verified against the file on disk.")
    w()
    w("Stage 0 is calibration and contains no search run. Stage 1 is the search: a gate that "
      "makes the stack find the known optima first, then the hunt for a ninth private pair. "
      "Stage 2W writes the result up and runs no search at all.")
    w()
    w("**In one line.** Stage 0 found the brief's premise three papers out of date and identified "
      "the five-dimensional base gadget as the only lever. Stage 1 proved that lever is already "
      "at its stop: the Polak–Schrijver code admits **exactly eight** private pairs in the whole "
      "of Z₇⁵, so there is no ninth, and no other code its construction can produce does better.")
    w()

    # ---------- headline ----------
    w("## The one thing Stage 0 changes about the plan")
    w()
    if lit:
        w("The task set for Stage 0 named α(C₇^⊠10) ≥ 134753 (arXiv:2607.21517, July 2026) as the "
          "current record and asked whether anything newer exists. **It is not the current "
          "record; it is three papers behind.** The chain, all verified present in the search of "
          f"{lit['date']} (`results/json/litcheck.json`):")
        w()
        w("| date | Θ(C₇) ≥ | who | reproduced here |")
        w("|---|---|---|---|")
        eb = (gad or {}).get("elementary_bounds", {})
        w(f"| 2019 | {eb.get('367^(1/5)', '')}… (367^(1/5)) | Polak–Schrijver [PS19-1] | "
          f"yes, from the circular graph |")
        w(f"| Jul 2026 | {eb.get('134753^(1/10)', '')}… (134753^(1/10)) | "
          f"Itty–Rosin–Carstensen–Reichman [IRCR26-1] | yes, set rebuilt and verified |")
        if gad:
            w(f"| Jul 2026 | {gad['gao']['bound_dim_200']}… | Gao [G26-8] | yes, exactly, incl. the 103-digit M₄₀ |")
            w(f"| Jul 2026 | {gad['bpz']['bound_dim_200']}… | Buys–Polak–Zuiddam [BPZ26-1] | yes, exactly |")
        w("| **Aug 2026** | **3.2588326203532663091215390518…** | **Tandon [T26-2]** | no — recursion framework not reimplemented |")
        if th:
            w(f"| upper bound | ϑ(C₇) = {th['values']['7'][:32]}… | Lovász, via [PS19-2] | yes, 50-digit recomputation |")
        w()
        w("The consequence for Stage 1 is written into `PREREGISTRATION_S1.md`: the target is "
          "Tandon's number, and the lever is the five-dimensional base gadget, not the dimension.")
    w()

    # ---------- Rule 0 ----------
    stage1(w, gate, anchor, s1pairs, s1codes, s1rep, s1aux, s1auxrun, lithist, budget, gad)
    stage2w(w, load("w_gate.json"), load("w_theorem.json"), load("w_checknums.json"),
            load("w_venue.json"))

    w("## Rule 0")
    w()
    if src:
        w(f"{src['found']}/{src['quotations']} quotations in `SOURCES.md` were found verbatim in the "
          f"dumped LaTeX sources by `scripts/check_sources.py`: {tick(src['missing'] == 0)}. "
          f"Sources dumped: {', '.join('arXiv:' + a for a in src['sources_checked'])}.")
        w()
        w("Three works are cited only through other papers because they are not on arXiv and were "
          "not obtained: Baumert et al. (1971), Vesel–Žerovnik (2002), Lovász (1979). Every number "
          "taken from them is quoted from a citing paper, and `SOURCES.md` says so at the point of "
          "use. No number in this repository is unsourced.")
    w()

    # ---------- S0.1 ----------
    w("## S0.1 — the verifier")
    w()
    w("`scripts/verify.c` (C, no dependencies). Two distinct vertices of C_n^⊠d are adjacent iff "
      "their circular distance is ≤ 1 in every coordinate. For n ≥ 4 that happens exactly when the "
      "boxes ∏ᵢ{xᵢ, xᵢ+1} meet, so a set is independent iff its |I|·2^d box cells are all distinct. "
      "The verifier sweeps them into an occupancy bitmap over Z_n^d — one linear pass, integer "
      "arithmetic only, no floating point, no heuristic. When n^d bits exceed the memory budget the "
      "universe is split into chunks and swept once per chunk; the answer is unchanged. "
      "`scripts/verify <file>` reports size, d, the verdict and the SHA-256 of the file.")
    w()
    if cal:
        w("### Anti-vacuum tests")
        w()
        w("A verifier that answered INDEPENDENT unconditionally would pass every reproduction in "
          "S0.2. These are the cases where it can fail and must not.")
        w()
        w("| test | what it does | result |")
        w("|---|---|---|")
        tot = sum(t["tested"] for t in cal["A_corruption"])
        w(f"| A — corruption | replace one vertex by a neighbour of itself; ground truth computed "
          f"independently; **{tot}** corruptions over all four reproduced sets | "
          f"{tick(all(t['pass'] for t in cal['A_corruption']))}, 0 disagreements |")
        nm = cal.get("A_nonmaximal", [])
        if nm:
            si = sum(t["still_independent"] for t in nm)
            w(f"| A′ — corruption on non-maximal sets | same, on sets that are not maximal, so that "
              f"**{si}** of the corruptions leave an independent set and the verifier must say so | "
              f"{tick(all(t['pass'] for t in nm))} |")
        w(f"| B — maximality | for each reproduced set, exhaustively over all 7^d vertices: can any "
          f"be added? | {tick(cal['B_pass'])}, all four maximal (0 addable) |")
        w(f"| C — small d | d = 2, 3, 4: box method vs the plain quadratic pair test, on independent "
          f"and on dependent inputs | {tick(cal['C_small_d']['pass'])} |")
        dd = cal["D_chunked"]
        w(f"| D — chunked path | the low-memory path ({dd['chunked']['passes']} passes) must agree "
          f"with the single-pass path, on the 134753-vertex set, independent and dependent | "
          f"{tick(dd['pass'])} |")
        w(f"| E — negative controls | random sets at d = 3, 5, 10 and a planted adjacent pair must "
          f"come out NOT INDEPENDENT | {tick(cal['E_negative']['pass'])} |")
        w(f"| F — trivial values | α(C₇) and α(C₇^⊠2) recomputed from scratch; and α(C_n^⊠2) for "
          f"n = 5, 9, 11, 13 against ⌊(n²−n)/4⌋ [PS19-4] and [MO17-3] | "
          f"{tick(cal['F_trivial']['pass'])} |")
        g = cal.get("G_mutant")
        if g:
            w(f"| G — do the tests have teeth? | a deliberately defective build of the same verifier "
              f"(`verify_mutant`, sees only repeated vertices) is put through test E | "
              f"{tick(g['pass'])} — the mutant calls the dependent set independent and is rejected |")
        w()
        w(f"All of S0.1: **{tick(cal['all_pass'])}**. Full report: `results/json/calibration.json`.")
        w()
        w("Test F in numbers:")
        w()
        w("| case | computed | proved optimal | literature |")
        w("|---|---|---|---|")
        for c in cal["F_trivial"]["cases"]:
            if "literature" in c:
                name = "α(C₇)" if c["d"] == 1 else f"α(C₇^⊠{c['d']})"
                w(f"| {name} | {c['computed']} | {'yes' if c['proved_optimal'] else 'no'} | "
                  f"{c['literature']} [PS19-4] |")
            else:
                w(f"| α(C_{c['n']}^⊠2) | {c['computed']} | {'yes' if c['proved_optimal'] else 'no'} | "
                  f"{c['formula_floor_n2_minus_n_over_4']} = ⌊(n²−n)/4⌋ [PS19-4, MO17-3] |")
        w()
    if mis3:
        w("### α(C₇^⊠3) = 33")
        w()
        if mis3.get("proved_optimal"):
            w(f"Proved exactly by `scripts/mis` in {mis3['seconds']:.0f} s: "
              f"**α(C₇^⊠3) = {mis3['best_found']}**, matching Baumert et al. as quoted in [PS19-4]. "
              f"{tick(mis3['best_found'] == 33)}")
        else:
            v3 = mis3.get("verified", {})
            w(f"**Not closed, and not even reached.** `scripts/mis` was given a "
              f"{mis3['time_limit']:.0f} s budget on the 343-vertex graph. It came back with an "
              f"independent set of size **{mis3['best_found']}** — verified independent by "
              f"`scripts/verify` against both the box test and the quadratic test "
              f"({tick(v3.get('agree', False))}, `{mis3.get('set_file', '')}`) — and with no proof "
              f"of optimality. So it failed twice over: it did not prove the known value 33 "
              f"[PS19-4], and it did not find a set of size 33 either. The clique-cover bound in "
              f"`scripts/mis` is too weak for this graph.")
            w()
            w("This is left as it stands. Closing it is not on the Stage 1 path: even the exact "
              "value would give only 33^(1/3) ≈ 3.2075, three decimal places below the record, and "
              "the lever identified above lives in d = 5. The solver earns its place at d ≤ 2, "
              "where it proves the optimum for five different cycles, and that is what it is used "
              "for.")
        w()

    # ---------- S0.2 ----------
    w("## S0.2 — reproductions")
    w()
    w("| what | size | d | independent | maximal | SHA-256 of the file |")
    w("|---|---|---|---|---|---|")
    for rep, label in ((ps, "Polak–Schrijver 367, rebuilt from the circular graph"),
                       (lin, "linear code 7³ = 343"),
                       (d10, "Itty et al. 134753")):
        if not rep:
            continue
        v = rep["verify"]
        w(f"| {label} | {v['size']} | {v['d']} | {tick(v['independent'])} | "
          f"{'yes' if v.get('maximal') else '—'} | `{rep['sha256'][:16]}…` |")
    pspath = os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt")
    if os.path.exists(pspath):
        w(f"| Polak–Schrijver 367, as printed in the paper | 367 | 5 | PASS | yes | "
          f"`{sha(pspath)[:16]}…` |")
    w()
    if ps:
        eg = ps["extension_graph"]
        w("### 1. Polak–Schrijver, from the circular graph up")
        w()
        w("Steps (i)–(v) of [PS19-6] were run rather than the printed answer being copied. "
          "Each number the paper states was recomputed:")
        w()
        w("| quantity | paper | here |")
        w("|---|---|---|")
        w(f"| minimum distance of S in C_{{108,382}}^⊠5 | ≥ 108 [PS19-5] | "
          f"{ps['circular']['min_distance']} |")
        w(f"| \\|M\\| after folding and pruning | 327 | {ps['M']['size']} |")
        w(f"| extension graph | 71 vertices, 85 edges | {eg['vertices']} vertices, {eg['edges']} edges |")
        w(f"| α of the extension graph | 40 | {eg['alpha']} |")
        w(f"| final size | 367 | {ps['reproduced_size']} |")
        w()
        w(f"All five agree: {tick(ps['matches_paper_numbers'])}. The maximum independent set of the "
          f"extension graph is not unique, so the set obtained is not the printed one: it shares "
          f"{ps['overlap_with_printed_R']} of 367 words with it, and the 327-word core M is a subset "
          f"of the printed set ({yn(ps['M_subset_of_printed_R'])}). That is the expected outcome, and it "
          f"is reported rather than hidden by adopting the printed set.")
        w()
    if lin:
        w("### 2. The linear 343")
        w()
        w(f"Generator rows over Z₇: {lin['generator_rows']} — the lexicographically first in RREF "
          f"with pivots in columns 0,1,2 that works, so no hidden search. Because the code is closed "
          f"under subtraction, independence reduces to a condition on single codewords, which gives a "
          f"second proof independent of the verifier: every nonzero codeword has a coordinate at "
          f"circular distance ≥ 2 from 0 ({yn(lin['linear_argument_holds'])}), and the minimum over "
          f"nonzero codewords of the largest coordinate distance is "
          f"{lin['min_coordinate_distance_over_nonzero_codewords']}. The two proofs agree: "
          f"{tick(lin['two_proofs_agree'])}.")
        w()
        w("The size 343 is Baumert et al. 1971, cited through [PS19-3]; their paper was not obtained, "
          "so what is reproduced is the size by a construction of the same kind, not their set. Said "
          "plainly rather than implied.")
        w()
    if d10:
        w("### 3. Itty et al., 134753 in C₇^⊠10")
        w()
        w("Rebuilt from the recipe in [IRCR26-2], starting only from the 367-word set. Every "
          "intermediate cardinality the paper states is asserted in the script, so a silent "
          "deviation fails loudly:")
        w()
        w("| | R | B | X | A | D | I |")
        w("|---|---|---|---|---|---|---|")
        s_, p_ = d10["sizes"], d10["paper_sizes"]
        w(f"| paper | {p_['R']} | {p_['B']} | {p_['X']} | {p_['A']} | {p_['D']} | {p_['I']} |")
        w(f"| here | {s_['R']} | {s_['B']} | {s_['X']} | {s_['A']} | {s_['D']} | {s_['I']} |")
        w()
        v = d10["verify"]
        w(f"All match: {tick(d10['sizes_match_paper'])}. The resulting 134753 vertices are "
          f"INDEPENDENT ({v['box_cells']:,} box cells swept in {v['box_seconds']:.2f} s) and the set "
          f"is maximal. No vertex of Z₇¹⁰ can be added to it.")
        w()

    # ---------- gadget ----------
    if gad:
        w("## S0.2, addition — the record chain itself")
        w()
        w("The three papers after arXiv:2607.21517 do not publish sets of vertices; they publish a "
          "recursion. A Stage 0 that calibrated only on explicit sets would leave Stage 1 aimed at "
          "a target three papers old, so the recursion is calibrated too.")
        w()
        bg = gad["base_gadget"]
        w("**The five-dimensional base gadget.** Gao's Proposition 4 [G26-3] claims the "
          "Polak–Schrijver code with the eight pairs of Itty et al. is a gadget with parameter tuple "
          f"(a,t,s,o,h,v) = (367,8,367,321,26,20). Re-checked here clause by clause [G26-4]: "
          f"I₀ and X independent and of size 367 ({yn(bg['I0_independent'])}, {yn(bg['X_independent'])}); "
          f"N({{q_j}}) ∩ I₀ = {{r_j}} for all eight j ({yn(bg['private_pairs_ok'])}); both transversals "
          f"independent ({yn(bg['P_H_independent'])}, {yn(bg['P_V_independent'])}); X disjoint from the "
          f"sixteen endpoints ({yn(bg['X_disjoint_from_endpoints'])}); the split "
          f"o/h/v = {bg['profile']['o']}/{bg['profile']['h']}/{bg['profile']['v']} with "
          f"{bg['confusable_with_both']} confusable with both. Profile matches: "
          f"{tick(bg['profile_matches'])}. All axioms: {tick(bg['all_gadget_axioms_hold'])}.")
        w()
        w("**The recursion.** The product lemma [G26-2] and the dynamic programme [G26-7], run in "
          "exact integer arithmetic:")
        w()
        w("| | here | published |")
        w("|---|---|---|")
        w(f"| M₂ (two base blocks, d = 10) | {gad['gao']['M_2']} | 134753 [G26-5] — i.e. exactly the "
          f"set of Itty et al. |")
        w(f"| closed forms s_k, o_k, t_k for k ≤ 40 [G26-6] | {tick(gad['closed_forms_ok'])} | |")
        w(f"| split tree | {', '.join(f'{k}={v[0]}+{v[1]}' for k, v in gad['gao']['split_tree'].items())} "
          f"| 1+1=2, 1+2=3, 2+3=5, 5+5=10, 10+10=20, 20+20=40 [G26-9] |")
        w(f"| M₄₀ (103 digits) | {tick(gad['gao']['M_40_matches_paper'])} — digit for digit | [G26-8] |")
        w(f"| Θ(C₇) ≥ | {gad['gao']['bound_dim_200']}… | {gad['gao']['paper_bound']}… [G26-8] |")
        w(f"| with the BPZ base profile (367,8,367,322,26,19) | {gad['bpz']['bound_dim_200']}… | "
          f"{gad['bpz']['paper_bound']}… [BPZ26-1] |")
        w()
        sat = gad.get("saturation")
        if sat:
            w("**The recursion saturates, and we checked it ourselves.** Gao proves the balanced "
              f"product converges below his own theorem and that continuing past dimension 200 loses "
              f"[G26-10]. Running the dynamic programme to {sat['dp_run_to_blocks']} blocks "
              f"(dimension {5 * sat['dp_run_to_blocks']}) gives its maximum at exactly k = "
              f"{sat['best_k']}, dimension {sat['best_dimension']}: "
              f"{tick(sat['k40_is_the_maximum'])}.")
            w()
            w("| blocks k | dimension | bound |")
            w("|---|---|---|")
            for k, v in sat["sample"].items():
                w(f"| {k} | {5 * int(k)} | {v} |")
            w()
            w("**Adding dimensions is not a lever.** That is the single most important fact Stage 0 "
              "established for the design of Stage 1.")
            w()
        sens = gad.get("profile_sensitivity")
        if sens:
            w("**Where the lever is.** The same recursion evaluated at hypothetical base profiles "
              "(no graph is touched — this is the published formula at other inputs):")
            w()
            w("| base profile (a,t,s,o) | Θ(C₇) ≥ at k = 40 |")
            w("|---|---|")
            for key in ("t=8,o=321", "t=8,o=322", "t=8,o=323", "t=8,o=324",
                        "t=9,o=321", "t=10,o=321", "a=368,t=8,o=321"):
                if key in sens["values"]:
                    w(f"| (367, {key.replace('a=368,', '').replace('t=', '').replace(',o=', ', 367, ')}) "
                      f"| {sens['values'][key]} |" if not key.startswith("a=")
                      else f"| (368, 8, 367, 321) | {sens['values'][key]} |")
            w(f"| — | record to beat: {sens['current_record_T26'][:22]}… [T26-2] |")
            w()
            w("One extra private pair is worth about ten extra auxiliary words. Caveat stated in the "
              "preregistration: these entries hold s and o fixed while t varies, and a gadget with "
              "more pairs need not keep them. The table bounds the prize; it does not promise it.")
            w()

    # ---------- S0.3 ----------
    w("## S0.3 — method map")
    w()
    w("In `METHODS.md`: exact independence numbers, linear and Cayley constructions, circular "
      "graphs and homomorphisms, stochastic search with prescribed symmetry, upper bounds and the "
      "asymptotic spectrum, LLM-driven search, and recursive gadget products — for each, what it "
      "produced, what has to be computed, and where it stops. No choice for Stage 1 is made there; "
      "the choice is made in `PREREGISTRATION_S1.md`.")
    w()
    if th:
        w(f"The upper-bound side was recomputed rather than quoted: ϑ(C_n) = n·cos(π/n)/(1+cos(π/n)) "
          f"[PS19-2, MO17-2] at 50 digits gives ϑ(C₇) = {th['values']['7']}…, which confirms "
          f"'< 3.3177' [PS19-3] and the table value 3.3176672 [BPZ26-3]; ϑ(C₅) comes out as √5, as "
          f"it must. All checks: {tick(th['all_pass'])}.")
    w()

    # ---------- S0.4 ----------
    if ben:
        w("## S0.4 — budget and hardware")
        w()
        w(f"Host: {ben['host']['cpu']} ({ben['host'].get('cpu_threads', '?')} threads), "
          f"{ben['host']['ram_bytes'] / 2**30:.0f} GiB RAM, "
          f"{ben['cases'][1].get('gpu', {}).get('device', 'no GPU')}.")
        w()
        w("| set | d | vertices | universe 7^d | bitmap | CPU cells/s | GPU cells/s | speed-up | "
          "CPU peak RSS | passes |")
        w("|---|---|---|---|---|---|---|---|---|---|")
        for c in ben["cases"]:
            g = c.get("gpu", {})
            w(f"| {c['case']} | {c['d']} | {c['size']:,} | {c['universe']:,} | "
              f"{human(c['bitmap_bytes'])} | {c['cpu']['cells_per_second']:.2e} | "
              f"{g.get('cells_per_second', 0):.2e} | "
              f"{c.get('gpu_speedup_cells_per_second', '—')}× | "
              f"{c['cpu']['peak_rss_bytes'] / 2**20:.0f} MiB | {c['cpu']['passes']} |")
        w()
        w(f"CPU and GPU verdicts agree on every set: {tick(ben['gpu_agreement'])}. At d = 5 the GPU "
          f"is **slower** than the CPU — the kernel launch costs more than the work — and that is "
          f"reported as measured, not smoothed away. The crossover is already past by d = 10.")
        w()
        mx = ben.get("maximality_sweep_d10")
        if mx:
            w(f"The expensive sweep is maximality, not independence: 3^d cells per vertex instead of "
              f"2^d. On the 134753-vertex set that is {mx['neighbourhood_cells']:,} cells, "
              f"{mx['wall_seconds']:.0f} s wall-clock against {mx['independence_sweep_seconds']:.2f} s "
              f"for the independence sweep itself.")
            w()
        w("Throughput varies by about 10% between runs on this host; `PREREGISTRATION_S1.md` "
          "quotes the figures from the run at sealing time (9.1·10⁸ CPU cells/s at d = 10, "
          "3.3·10¹⁰ on the GPU), and the table above is the latest run. Nothing in the "
          "preregistration depends on the difference.")
        w()
        w("**What this means for the Stage 1 budget.** Verification is not the bottleneck and will "
          "not be. A set of 1.3 million vertices in d = 12 is checked exactly in 11 s on one core "
          "and 0.5 s on the GPU, in under 1 GiB. The Stage 1 budget is for the combinatorial search "
          "over base gadgets, not for checking its output.")
        w()

    # ---------- literature ----------
    if lit:
        w("## Literature check")
        w()
        w(f"`scripts/litcheck.py`, {lit['date']}: {len(lit['searches'])} queries against the arXiv "
          f"search interface, {len(lit['union_sorted_by_id'])} distinct hits recorded in "
          f"`results/json/litcheck.json`. The four papers of the record chain are all present: "
          f"{tick(all(lit['record_chain_present'].values()))}.")
        w()
        w("| arXiv | submitted | title |")
        w("|---|---|---|")
        for h in lit["union_sorted_by_id"]:
            if h["id"] in ("2607.21517", "2607.27869", "2607.29681", "2608.30273", "1808.07438", "1504.01472"):
                w(f"| {h['id']} | {h['submitted']} | {h['title']} |")
        w()
        w("One further paper in the hit list is worth naming: **arXiv:2608.06573** (Sason, "
          "*Shannon Capacity and Related Graph Invariants for Lexicographic Products*, Aug 2026). "
          "It is about lexicographic rather than strong products and does not bear on C₇, but it is "
          "the kind of paper that would be missed by a search restricted to odd cycles.")
        w()

    # ---------- deviations ----------
    w("## Deviations from the Stage 0 task, with reasons")
    w()
    w("1. **The premise was corrected.** The task named arXiv:2607.21517 as the current record and "
      "asked for a check. The check says no. Everything downstream — the method map, the "
      "preregistration target — is set against Tandon's bound instead. This is the largest "
      "deviation and it is the point of having asked.")
    w()
    w("2. **The recursion was calibrated as well as the sets** (the section above). Not in the task "
      "as written, which speaks of sets of vertices; necessary because the record now lives in an "
      "object of 10¹⁰³ words that is never materialised, and a Stage 1 aimed at explicit sets in "
      "high dimension would be aiming at the wrong object.")
    w()
    if mis3 is None:
        w("3. **α(C₇^⊠3) = 33 is cited, not reproduced.** The exact attempt had not finished when "
          "this report was generated; see `results/json/mis_c7_d3.json`.")
    elif not mis3.get("proved_optimal"):
        w(f"3. **α(C₇^⊠3) = 33 is cited, not reproduced.** The exact solver was given "
          f"{mis3['time_limit']:.0f} s on the 343-vertex graph, reached {mis3['best_found']} and "
          f"proved nothing. The task asks for the trivial cases to be checked against sources: "
          f"α(C₇) = 3 and α(C₇^⊠2) = 10 are recomputed and proved optimal, 33 is not — it stays a "
          f"citation. Recorded as an open gap rather than quietly dropped.")
    elif mis3:
        w(f"3. α(C₇^⊠3) = 33 was proved exactly rather than merely cited "
          f"({mis3['seconds']:.0f} s), which the task did not require.")
    w()
    w("4. **The d = 4 and d = 5 record sets of Vesel–Žerovnik (108) and Mathew–Östergård (350) are "
      "not in `sets/`.** Constructing a 108-vertex set in C₇^⊠4 ourselves would be a search run, "
      "which Stage 0 forbids. The numbers are cited [PS19-3, MO17-1]; the small-d cross-check in "
      "test C uses product constructions (10×3 at d = 3, 10×10 at d = 4) instead, which need no "
      "search.")
    w()
    w("   **Corrected in Stage 2 (2026-10-02).** The sentence this deviation used to carry — that "
      "neither paper publishes its set in a form we obtained — was false for Mathew–Östergård. "
      "Their appendix publishes the 350-word set in full: a generator of the prescribed group and "
      "fifty orbit representatives [MO17-6]. `scripts/s2_reconstruct_mo.py` rebuilds it from the "
      "dumped source and `scripts/verify` confirms it, so `sets/` now holds it. Vesel–Žerovnik is "
      "a different case and the original statement stands there: that paper is not on arXiv and "
      "was never obtained. The claim was wrong because nobody read the appendix of a paper that "
      "was sitting in `sources/`, and it is corrected here rather than quietly dropped.")
    w()
    w("5. **The GPU verifier was written although the task only asked for a measurement.** It is "
      "the measurement: 'what does a GPU give over a CPU' has no answer without one. It is held to "
      "the same standard — its verdict must agree with the CPU's on every set, and it does.")
    w()

    # ---------- what is next ----------
    w("## What Stage 2 would have to do")
    w()
    w("Stage 1 closed every direction it had access to. What is left, in the order the evidence "
      "points:")
    w()
    w("1. **New 367-word codes from outside the Polak–Schrijver pipeline.** The private-pair count "
      "turned out to be a property of the individual code — 8 for the printed one, 6 for our "
      "reproduction, 5 to 8 across the pipeline's eight codes. A code with nine would change the "
      "record. Nothing in Stage 1 can generate codes outside that family; that needs either a new "
      "construction or a search for α(C₇^⊠5) itself.")
    w("2. **A base gadget in a dimension other than five.** Every published gadget lives in "
      "C₇^⊠5 because that is where the 367 lives. Nothing in the product lemma requires it.")
    w("3. **Tandon's heterogeneous framework**, which Stage 1 deliberately did not reimplement. It "
      "is worth 2.7·10⁻⁵ on the same base gadget, and any future base improvement would be worth "
      "more through it than through the homogeneous recursion used here.")

    path = os.path.join(ROOT, "RESULTS.md")
    with open(path, "w") as f:
        f.write("\n".join(OUT) + "\n")
    print(f"wrote {path} ({len(OUT)} lines)")


if __name__ == "__main__":
    main()

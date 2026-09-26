"""Stage 2W -- the data behind the theorem, recomputed so the note can quote it.

The note states one theorem: the printed Polak-Schrijver 367-word code admits
exactly eight candidate private pairs in the whole of Z_7^5, and all eight are
simultaneously usable.  s1_pairs.json already records the counts; this script
recomputes them from the set file and adds what a written proof has to display:

  * the neighbour histogram over all of Z_7^5 \\ I, which is where "exactly
    eight" comes from -- 16440 words outside I, and the number of them with
    exactly one I-neighbour;
  * the eight candidates in the numbering of Gao's table, with their centres;
  * the conflict graph on the eight q's: its edge list, its components, its
    bipartition, and the count of proper 2-colourings up to global swap;
  * a machine check of the non-mixing lemma used in the proof (for i != j,
    r_i is confusable with neither r_j nor q_j) -- the lemma is proved by hand
    in the note, and this is the anti-vacuum control on the proof;
  * cross-checks against s1_pairs.json and s1_aux.json, so the note and the
    Stage 1 record cannot drift apart silently.
"""
import json
import os
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, confusable, read_set, sha256, verify  # noqa: E402

N = 7
D = 5
# Gao's table, SOURCES.md [G26-3]; j is the paper's numbering
RQ = [
    ((1, 3, 4, 4, 6), (2, 3, 5, 4, 6)), ((3, 4, 0, 3, 5), (2, 4, 6, 3, 5)),
    ((5, 3, 1, 3, 4), (5, 3, 2, 3, 5)), ((4, 4, 6, 1, 6), (5, 4, 6, 0, 6)),
    ((6, 0, 6, 4, 5), (6, 1, 6, 5, 5)), ((0, 3, 5, 6, 5), (6, 3, 5, 0, 5)),
    ((6, 4, 3, 4, 0), (6, 4, 2, 4, 6)), ((6, 4, 5, 3, 2), (6, 5, 5, 3, 1)),
]
J0, J1 = {0, 5, 6}, {1, 2, 3, 4, 7}


def neighbour_histogram(I):
    """For every q outside I, how many I-neighbours it has."""
    Iset = set(I)
    hist = {}
    ones = []
    for q in product(range(N), repeat=D):
        if q in Iset:
            continue
        cnt = 0
        hit = None
        for r in I:
            if confusable(q, r, N):
                cnt += 1
                hit = r
                if cnt > 2:
                    break
        hist[cnt] = hist.get(cnt, 0) + 1
        if cnt == 1:
            ones.append((hit, q))
    return hist, ones


def components(n, edges):
    par = list(range(n))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            par[ra] = rb
    return sorted({find(i) for i in range(n)})


def main():
    path = os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt")
    n, d, I = read_set(path)
    assert (n, d) == (N, D)
    out = {
        "code": {
            "file": "sets/C7_d5_367_polak_schrijver.txt",
            "sha256": sha256(path),
            "size": len(I),
            "verifier": verify(path),
        }
    }

    hist, ones = neighbour_histogram(I)
    out["neighbour_histogram"] = {
        "universe": N ** D,
        "words_outside_I": N ** D - len(I),
        "by_number_of_I_neighbours": {("3+" if k >= 3 else str(k)): hist[k]
                                      for k in sorted(hist)},
        "note": "the count stops at 3, so the last bucket is '3 or more'.",
        "exactly_one": hist.get(1, 0),
        "zero": hist.get(0, 0),
    }

    # the candidates, in Gao's numbering
    known = {q: j for j, (r, q) in enumerate(RQ)}
    cand = []
    for r, q in sorted(ones, key=lambda rq: known.get(rq[1], 99)):
        cand.append({"j": known.get(q), "r": list(r), "q": list(q)})
    out["candidates"] = cand
    out["candidates_are_exactly_the_published_eight"] = (
        sorted(q for _, q in ones) == sorted(q for _, q in RQ)
        and all({q: r for r, q in ones}[q] == r for r, q in RQ)
    )

    # the conflict graph on the eight q's
    qs = [tuple(c["q"]) for c in cand]
    edges = [(i, j) for i in range(len(qs)) for j in range(i + 1, len(qs))
             if confusable(qs[i], qs[j], N)]
    comp = components(len(qs), edges)
    colour = {}

    def paint(i, c, adj):
        colour[i] = c
        for k in adj[i]:
            if k not in colour:
                if not paint(k, 1 - c, adj):
                    return False
            elif colour[k] == c:
                return False
        return True
    adj = {i: [] for i in range(len(qs))}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    bipartite = all(paint(i, 0, adj) for i in range(len(qs)) if i not in colour)
    out["conflict_graph"] = {
        "vertices": len(qs),
        "edges": [[cand[a]["j"], cand[b]["j"]] for a, b in edges],
        "edge_count": len(edges),
        "is_a_matching": all(sum(1 for e in edges if i in e) <= 1 for i in range(len(qs))),
        "components": len(comp),
        "bipartite": bipartite,
        "proper_2_colourings_up_to_swap": 2 ** (len(comp) - 1),
        "t_max": len(qs) if bipartite else None,
    }

    # the published colouring, in the same numbering
    published = {j: ("V" if j in J0 else "H") for j in range(8)}
    bad = [[a, b] for a, b in edges
           if published[cand[a]["j"]] == published[cand[b]["j"]]]
    out["published_colouring"] = {
        "q_transversal": {str(j): published[j] for j in range(8)},
        "J0": sorted(J0), "J1": sorted(J1),
        "monochromatic_conflict_edges": bad,
        "valid": not bad,
    }

    # the lemma, checked by machine on this instance
    viol = []
    for a in range(8):
        for b in range(8):
            if a == b:
                continue
            ra = tuple(cand[a]["r"])
            if confusable(ra, tuple(cand[b]["r"]), N):
                viol.append(["r-r", cand[a]["j"], cand[b]["j"]])
            if confusable(ra, tuple(cand[b]["q"]), N):
                viol.append(["r-q", cand[a]["j"], cand[b]["j"]])
    out["lemma_check"] = {
        "checked": "for i != j: r_i confusable with neither r_j nor q_j",
        "violations": viol,
        "pass": not viol,
    }

    # why Itty et al. have to replace one word: the offender in T(I)
    # Gao's automorphism, SOURCES.md [T26-6] / [G26-4]: T(w) = (2-w1, w3, w0, 2-w2, w4)
    def T(w):
        return ((2 - w[1]) % N, w[3], w[0], (2 - w[2]) % N, w[4])
    PH = [tuple(cand[i]["r"]) if published[cand[i]["j"]] == "V" else tuple(cand[i]["q"])
          for i in range(8)]
    PV = [tuple(cand[i]["q"]) if published[cand[i]["j"]] == "V" else tuple(cand[i]["r"])
          for i in range(8)]
    TI = [T(w) for w in I]
    both = [list(w) for w in TI
            if any(confusable(w, p, N) for p in PH) and any(confusable(w, p, N) for p in PV)]
    out["forbidden_region_of_T_image"] = {
        "automorphism": "T(w) = (2 - w_1, w_3, w_0, 2 - w_2, w_4)",
        "image_size": len(set(TI)),
        "words_confusable_with_both_transversals": both,
        "count": len(both),
        "matches_the_word_itty_et_al_replace": both == [[2, 4, 6, 3, 5]],
        "note": ("Gao's X is T(I) with this word replaced by (1,5,6,3,5); the sweep in "
                 "s1_aux.json shows no image of any known code has an empty forbidden "
                 "intersection, and here the single offender is exhibited."),
    }

    # cross-checks against the Stage 1 record
    p = json.load(open(os.path.join(ROOT, "results", "json", "s1_pairs.json")))
    printed = [c for c in p["codes"] if c["code"].endswith("as printed")][0]
    aux = json.load(open(os.path.join(ROOT, "results", "json", "s1_aux.json")))
    out["cross_check_stage1"] = {
        "s1_pairs_candidates": printed["candidate_private_pairs"],
        "s1_pairs_edges": printed["conflict_graph_edges"],
        "s1_pairs_t": printed["max_private_pairs_t"],
        "s1_aux_colourings": aux["proper_2_colourings_up_to_swap"],
        "agrees": (printed["candidate_private_pairs"] == len(qs)
                   and printed["conflict_graph_edges"] == len(edges)
                   and printed["max_private_pairs_t"] == len(qs)
                   and aux["proper_2_colourings_up_to_swap"] == 2 ** (len(comp) - 1)),
    }
    out["all_pass"] = bool(
        out["candidates_are_exactly_the_published_eight"]
        and out["conflict_graph"]["bipartite"]
        and out["published_colouring"]["valid"]
        and out["lemma_check"]["pass"]
        and out["forbidden_region_of_T_image"]["matches_the_word_itty_et_al_replace"]
        and out["cross_check_stage1"]["agrees"]
        and out["code"]["verifier"]["independent"]
    )
    with open(os.path.join(ROOT, "results", "json", "w_theorem.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps({
        "words_outside_I": out["neighbour_histogram"]["words_outside_I"],
        "histogram": out["neighbour_histogram"]["by_number_of_I_neighbours"],
        "candidates": len(cand),
        "edges": out["conflict_graph"]["edges"],
        "components": out["conflict_graph"]["components"],
        "colourings_up_to_swap": out["conflict_graph"]["proper_2_colourings_up_to_swap"],
        "candidates_are_the_published_eight": out["candidates_are_exactly_the_published_eight"],
        "lemma_pass": out["lemma_check"]["pass"],
        "offender_in_T_image": out["forbidden_region_of_T_image"]["words_confusable_with_both_transversals"],
        "cross_check": out["cross_check_stage1"]["agrees"],
        "all_pass": out["all_pass"],
    }, indent=2))


if __name__ == "__main__":
    main()

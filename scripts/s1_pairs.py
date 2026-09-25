"""S1.2 -- the search for a ninth private pair, run on the gadget structure rather
than on the 16807-vertex graph.

Setting (Gao's definition, SOURCES.md [G26-1]).  A gadget over a code I needs t
*private pairs* (r_i, q_i): r_i in I, q_i not in I, and N[q_i] cap I = {r_i}; the
endpoint sets must be pairwise disjoint; and the two complementary transversals
P_H, P_V must both be independent.

Two observations collapse the transversal condition to something finite and small.

  * If i != j then r_i is never confusable with q_j.  For r_i in I and
    N[q_j] cap I = {r_j}, so r_i ~ q_j would force r_i = r_j, and the centres are
    distinct.  And r_i is never confusable with r_j, because I is independent.
  * Therefore the only way a transversal can fail to be independent is by holding
    two confusable q's.

So, writing sigma(i) in {H,V} for the transversal that q_i goes to, the gadget
condition is exactly:

    the chosen q's have pairwise distinct centres, and the graph on them induced
    by confusability is properly 2-coloured by sigma -- that is, bipartite.

The maximum number of private pairs is then a maximum induced bipartite subgraph
of the candidate-q conflict graph, subject to one q per centre.  The candidate q's
are all of Z_7^5 \\ I with exactly one I-neighbour, which is a direct computation,
not a search.  The maximisation is solved exactly by branch and bound over the
labelling {unused, H, V}.

Anti-vacuum: the eight pairs of Itty et al. must come out of the enumeration with
the centres the paper gives them, and the 2-colouring the paper uses (J_0 to one
transversal, J_1 to the other) must be one of the valid ones.  If the enumeration
cannot recover the known gadget it is not to be trusted about a better one.
"""
import json
import os
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, confusable, read_set  # noqa: E402

N = 7
RQ = [
    ((1, 3, 4, 4, 6), (2, 3, 5, 4, 6)), ((3, 4, 0, 3, 5), (2, 4, 6, 3, 5)),
    ((5, 3, 1, 3, 4), (5, 3, 2, 3, 5)), ((4, 4, 6, 1, 6), (5, 4, 6, 0, 6)),
    ((6, 0, 6, 4, 5), (6, 1, 6, 5, 5)), ((0, 3, 5, 6, 5), (6, 3, 5, 0, 5)),
    ((6, 4, 3, 4, 0), (6, 4, 2, 4, 6)), ((6, 4, 5, 3, 2), (6, 5, 5, 3, 1)),
]
J0, J1 = {0, 5, 6}, {1, 2, 3, 4, 7}


def candidate_pairs(I):
    """Every q outside I with exactly one I-neighbour, and that neighbour."""
    Iset = set(I)
    out = []
    for q in product(range(N), repeat=5):
        if q in Iset:
            continue
        hit = None
        cnt = 0
        for r in I:
            if confusable(q, r, N):
                cnt += 1
                if cnt > 1:
                    break
                hit = r
        if cnt == 1:
            out.append((hit, q))
    return out


def max_pairs(pairs, time_budget_nodes=200_000_000):
    """Largest set of pairs with distinct centres whose q-conflict graph is bipartite.

    Exact branch and bound: label each candidate H, V or unused; prune on the
    number of centres still reachable."""
    n = len(pairs)
    centres = sorted({r for r, _ in pairs})
    cidx = {r: i for i, r in enumerate(centres)}
    cen = [cidx[r] for r, _ in pairs]
    conflict = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if confusable(pairs[i][1], pairs[j][1], N):
                conflict[i][j] = conflict[j][i] = True
    # group candidates by centre: at most one per centre may be used
    by_centre = {}
    for i, c in enumerate(cen):
        by_centre.setdefault(c, []).append(i)
    groups = [v for _, v in sorted(by_centre.items())]

    best = {"size": 0, "assign": None, "nodes": 0, "exhausted": True}
    cur = {}

    def rec(gi):
        best["nodes"] += 1
        if best["nodes"] > time_budget_nodes:
            best["exhausted"] = False
            return
        if gi == len(groups):
            if len(cur) > best["size"]:
                best["size"] = len(cur)
                best["assign"] = dict(cur)
            return
        if len(cur) + (len(groups) - gi) <= best["size"]:
            return
        for i in groups[gi]:
            for lab in ("H", "V"):
                ok = True
                for j, lj in cur.items():
                    if lj == lab and conflict[i][j]:
                        ok = False
                        break
                if ok:
                    cur[i] = lab
                    rec(gi + 1)
                    del cur[i]
        rec(gi + 1)          # this centre unused

    rec(0)
    return best, pairs, conflict, cen


def describe(I, label):
    pairs = candidate_pairs(I)
    best, pairs, conflict, cen = max_pairs(pairs)
    n = len(pairs)
    deg = [sum(conflict[i]) for i in range(n)]
    centres = len({c for c in cen})
    rep = {
        "code": label,
        "code_size": len(I),
        "candidate_private_pairs": n,
        "distinct_centres": centres,
        "conflict_graph_edges": sum(deg) // 2,
        "max_private_pairs_t": best["size"],
        "search_exhaustive": best["exhausted"],
        "nodes": best["nodes"],
    }
    if best["assign"] is not None:
        chosen = sorted(best["assign"])
        rep["witness"] = [{"r": list(pairs[i][0]), "q": list(pairs[i][1]),
                           "transversal_of_q": best["assign"][i]} for i in chosen]
    return rep, pairs, best


def main():
    out = {}
    # --- anti-vacuum: recover the published eight pairs from the enumeration ---
    n, d, R = read_set(os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt"))
    pairs = candidate_pairs(R)
    pairset = {(r, q) for r, q in pairs}
    known = [(RQ[j][0], RQ[j][1]) for j in range(8)]
    out["known_gadget_recovered"] = {
        "published_pairs_found_in_enumeration": [list(q) for r, q in known if (r, q) in pairset],
        "all_eight_found": all(p in pairset for p in known),
        "candidates_total": len(pairs),
    }
    # the published 2-colouring must be a valid one
    idx = {q: i for i, (r, q) in enumerate(pairs)}
    lab = {}
    for j in range(8):
        lab[idx[RQ[j][1]]] = "V" if j in J0 else "H"   # J_0 puts r in P_H, so q goes to P_V
    ok = True
    for i, li in lab.items():
        for j, lj in lab.items():
            if i < j and li == lj and confusable(pairs[i][1], pairs[j][1], N):
                ok = False
    out["known_gadget_recovered"]["published_2_colouring_valid"] = ok

    results = []
    for f, label in (("C7_d5_367_polak_schrijver.txt", "Polak-Schrijver 367, as printed"),
                     ("C7_d5_367_reproduced.txt", "Polak-Schrijver 367, our reproduction"),
                     ("C7_d5_343_linear.txt", "the linear 343 code")):
        _, _, I = read_set(os.path.join(ROOT, "sets", f))
        rep, _, _ = describe(I, label)
        rep["file"] = "sets/" + f
        results.append(rep)
        print(json.dumps({k: rep[k] for k in
                          ("code", "candidate_private_pairs", "distinct_centres",
                           "conflict_graph_edges", "max_private_pairs_t", "search_exhaustive")}))
    out["codes"] = results
    with open(os.path.join(ROOT, "results", "json", "s1_pairs.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print()
    print("known gadget recovered:", out["known_gadget_recovered"]["all_eight_found"],
          "| published 2-colouring valid:", out["known_gadget_recovered"]["published_2_colouring_valid"])


if __name__ == "__main__":
    main()

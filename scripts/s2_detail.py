"""The candidate structure of one code, recomputed twice by different means.

Stage 2's preregistration (§5) requires any claim to be recounted by a code path other
than the one that produced it. So this script does not call the Stage 1 enumerator: it
counts I-neighbours by sweeping the 3^5 box around each vertex (not by scanning the
code), builds the conflict graph, and decides t* by brute force over all 2^t colourings
rather than by branch and bound. Both routes must agree, and the disagreement, if any,
is printed rather than hidden.
"""
import json
import os
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, confusable, read_set, sha256, verify  # noqa: E402
from s1_pairs import candidate_pairs, max_pairs  # noqa: E402

N, D = 7, 5


def neighbours_by_box(I):
    """For every vertex outside I, its I-neighbours, found from the box around it."""
    Iset = set(I)
    offs = list(product((-1, 0, 1), repeat=D))
    out = {}
    for q in product(range(N), repeat=D):
        if q in Iset:
            continue
        hits = [tuple((q[i] + o[i]) % N for i in range(D)) for o in offs]
        nb = [h for h in set(hits) if h in Iset]
        if nb:
            out[q] = sorted(nb)
    return out


def brute_t_star(qs, centres):
    """Largest subset with distinct centres and a properly 2-colourable conflict graph."""
    t = len(qs)
    conflict = [[confusable(qs[i], qs[j], N) for j in range(t)] for i in range(t)]
    best = (0, None)
    for mask in range(1 << t):
        chosen = [i for i in range(t) if mask >> i & 1]
        if len(chosen) <= best[0]:
            continue
        if len({centres[i] for i in chosen}) != len(chosen):
            continue
        ok = False
        for colouring in range(1 << len(chosen)):
            good = True
            for a in range(len(chosen)):
                for b in range(a + 1, len(chosen)):
                    if conflict[chosen[a]][chosen[b]] and \
                       ((colouring >> a & 1) == (colouring >> b & 1)):
                        good = False
                        break
                if not good:
                    break
            if good:
                ok = True
                col = colouring
                break
        if ok:
            best = (len(chosen), {"indices": chosen,
                                  "colouring": [("H" if col >> k & 1 else "V")
                                                for k in range(len(chosen))]})
    return best


def main():
    path = sys.argv[1]
    n, d, I = read_set(path)
    assert (n, d) == (N, D), (n, d)
    out = {"file": os.path.relpath(os.path.abspath(path), ROOT), "sha256": sha256(path),
           "size": len(I), "verifier": verify(path, extra=("--quadratic",))}

    # --- route A: the box sweep, this script ---
    nb = neighbours_by_box(I)
    ones = {q: v[0] for q, v in nb.items() if len(v) == 1}
    hist = {}
    for q, v in nb.items():
        k = str(min(len(v), 3)) + ("+" if len(v) >= 3 else "")
        hist[k] = hist.get(k, 0) + 1
    out["route_A_box_sweep"] = {"outside": N ** D - len(I), "with_one_neighbour": len(ones),
                               "neighbour_histogram": {k: hist[k] for k in sorted(hist)}}

    # --- route B: the Stage 1 enumerator ---
    pairsB = candidate_pairs(I)
    out["route_B_stage1_enumerator"] = {"candidates": len(pairsB)}
    out["routes_agree_on_the_candidate_set"] = (
        sorted((r, q) for q, r in ones.items()) == sorted(pairsB))

    qs = [q for _, q in pairsB]
    centres = [r for r, _ in pairsB]
    edges = [[i, j] for i in range(len(qs)) for j in range(i + 1, len(qs))
             if confusable(qs[i], qs[j], N)]
    out["conflict_graph"] = {
        "vertices": len(qs), "edges": edges, "edge_count": len(edges),
        "distinct_centres": len(set(centres)),
    }
    bb, _, _, _ = max_pairs(list(pairsB))
    brute = brute_t_star(qs, centres)
    out["t_star_branch_and_bound"] = bb["size"]
    out["t_star_brute_force"] = brute[0]
    out["t_star_methods_agree"] = bb["size"] == brute[0]
    out["witness"] = None
    if brute[1]:
        out["witness"] = [{"r": list(centres[i]), "q": list(qs[i]), "q_goes_to": c}
                          for i, c in zip(brute[1]["indices"], brute[1]["colouring"])]
        # the witness has to satisfy the gadget's transversal condition outright
        PH = [tuple(w["r"]) if w["q_goes_to"] == "V" else tuple(w["q"]) for w in out["witness"]]
        PV = [tuple(w["q"]) if w["q_goes_to"] == "V" else tuple(w["r"]) for w in out["witness"]]
        def indep(S):
            return all(not confusable(a, b, N) for i, a in enumerate(S) for b in S[i + 1:])
        out["transversals"] = {"P_H_independent": indep(PH), "P_V_independent": indep(PV),
                               "endpoints_disjoint": len(set(PH) | set(PV)) == 2 * len(out["witness"])}
    out["all_pass"] = bool(out["routes_agree_on_the_candidate_set"]
                           and out["t_star_methods_agree"]
                           and out["verifier"]["independent"]
                           and (not out["witness"] or all(out["transversals"].values())))
    name = os.path.splitext(os.path.basename(path))[0]
    with open(os.path.join(ROOT, "results", "json", f"s2_detail_{name}.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("size", "route_A_box_sweep", "route_B_stage1_enumerator",
                       "routes_agree_on_the_candidate_set", "t_star_branch_and_bound",
                       "t_star_brute_force", "t_star_methods_agree", "all_pass")}, indent=2))
    print("conflict edges:", out["conflict_graph"]["edges"])
    if out["witness"]:
        print("transversals:", out["transversals"])
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

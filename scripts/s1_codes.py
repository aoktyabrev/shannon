"""S1.2, branch C of the preregistration: other codes of size 367.

Stage 1 found that the printed Polak-Schrijver code admits exactly eight
candidate private pairs in the whole of Z_7^5, so no ninth pair exists *for that
code*.  The number is a property of the code, not of its size: our own
reproduction of the same construction, which differs from the printed set in two
words, admits only six.

So the question becomes: over the codes the Polak-Schrijver pipeline can produce,
how large can the number of candidate private pairs get?  Step (v) of their
method [SOURCES.md PS19-6] extends the 327-word core M by a maximum independent
set of a 71-vertex "extension graph", and that maximum is not unique.  Every one
of its maximum independent sets gives a 367-word code.  They are enumerated here
exhaustively, and each resulting code is put through the private-pair count of
scripts/s1_pairs.py.

This is an exhaustive search over a finite, explicitly described family, not a
heuristic one.  What it cannot do is reach codes outside that family.
"""
import json
import os
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, confusable, write_set, sha256, verify  # noqa: E402
from s1_pairs import candidate_pairs, max_pairs  # noqa: E402

N = 7
NC, KC = 382, 108


def build_M_and_extension():
    """Steps (i)-(v) of arXiv:1808.07438 Section 3, stopping before the choice in (v)."""
    g = (1, 7, 7 ** 2, 7 ** 3, 7 ** 4)
    S = [tuple((t * c) % NC for c in g) for t in range(NC)]
    shift = (40, 123, 40, 123, 40)
    S2 = [tuple((a + b) % NC for a, b in zip(w, shift)) for w in S]
    Sp = sorted({tuple((2 * a) // 109 for a in w) for w in S2})
    M = [u for u in Sp if not any(v != u and confusable(u, v, N) for v in Sp)]
    Mset = set(M)
    cand = [x for x in product(range(N), repeat=5)
            if x not in Mset and not any(confusable(x, m, N) for m in M)]
    nv = len(cand)
    adj = [0] * nv
    for i in range(nv):
        for j in range(i + 1, nv):
            if confusable(cand[i], cand[j], N):
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    return M, cand, adj


def all_maximum_independent_sets(nv, adj, alpha):
    """Every independent set of size exactly alpha, by branch and bound with the
    same clique-free bound used to prove the optimum."""
    out = []
    chosen = []

    def rec(cand_mask, start):
        k = bin(cand_mask).count("1")
        if len(chosen) + k < alpha:
            return
        if len(chosen) == alpha:
            out.append(tuple(chosen))
            return
        if cand_mask == 0:
            return
        v = (cand_mask & -cand_mask).bit_length() - 1
        # branch: v in, or v out
        chosen.append(v)
        rec(cand_mask & ~(adj[v] | (1 << v)), v + 1)
        chosen.pop()
        rec(cand_mask & ~(1 << v), v + 1)

    rec((1 << nv) - 1, 0)
    return out


def main():
    M, cand, adj = build_M_and_extension()
    nv = len(cand)
    rep = {"core_M": len(M), "extension_graph_vertices": nv,
           "extension_graph_edges": sum(bin(a).count("1") for a in adj) // 2}
    mis = all_maximum_independent_sets(nv, adj, 40)
    rep["maximum_independent_sets_of_the_extension_graph"] = len(mis)
    rep["codes_of_size_367_from_the_pipeline"] = len(mis)

    os.makedirs(os.path.join(ROOT, "sets", "pipeline_codes"), exist_ok=True)
    best = {"t": -1}
    hist = {}
    per_code = []
    for k, sel in enumerate(mis):
        code = sorted(set(M) | {cand[i] for i in sel})
        assert len(code) == 367
        pairs = candidate_pairs(code)
        b, _, _, _ = max_pairs(pairs)
        t = b["size"]
        hist[t] = hist.get(t, 0) + 1
        per_code.append({"index": k, "candidates": len(pairs), "t": t})
        cf = os.path.join(ROOT, "sets", "pipeline_codes", "C7_d5_367_pipeline_%02d.txt" % k)
        write_set(cf, N, code, [
            "Independent set of size 367 in C_7^{boxtimes 5}: Polak-Schrijver pipeline",
            "(arXiv:1808.07438 Sec. 3) with extension-graph maximum independent set #%d." % k,
            "Candidate private pairs: %d; maximum admissible t = %d." % (len(pairs), t),
        ])
        per_code[-1]["file"] = os.path.relpath(cf, ROOT)
        per_code[-1]["sha256"] = sha256(cf)
        v = verify(cf, ["--maximal"])
        per_code[-1]["verified_independent"] = v["independent"]
        per_code[-1]["verified_size"] = v["size"]
        per_code[-1]["maximal"] = v["maximal"]
        assert v["independent"] and v["size"] == 367
        if t > best["t"]:
            best = {"t": t, "index": k, "code": code, "candidates": len(pairs),
                    "assign": b["assign"], "pairs": pairs}
    rep["per_code"] = per_code
    rep["all_codes_verified"] = all(c.get("verified_independent") and c.get("verified_size") == 367
                                    for c in per_code)
    rep["t_histogram"] = {str(a): b for a, b in sorted(hist.items())}
    rep["best_t"] = best["t"]
    rep["best_index"] = best["index"]
    rep["ninth_pair_found"] = best["t"] >= 9

    if best["t"] >= 0:
        out = os.path.join(ROOT, "sets", "C7_d5_367_best_t_from_pipeline.txt")
        write_set(out, N, best["code"], [
            "Independent set of size 367 in C_7^{boxtimes 5} from the Polak-Schrijver",
            "pipeline (arXiv:1808.07438 Sec. 3), using extension-graph maximum independent",
            "set #%d of %d.  Candidate private pairs: %d; maximum admissible t = %d."
            % (best["index"], len(mis), best["candidates"], best["t"]),
            "Built by scripts/s1_codes.py.",
        ])
        rep["best_code_file"] = os.path.relpath(out, ROOT)
        rep["best_code_sha256"] = sha256(out)
        rep["best_code_verified"] = verify(out, ["--maximal"])

    with open(os.path.join(ROOT, "results", "json", "s1_codes.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps({k: v for k, v in rep.items() if k != "best_code_verified"}, indent=2)[:1800])


if __name__ == "__main__":
    main()

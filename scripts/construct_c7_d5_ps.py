"""S0.2(1): reproduce the Polak-Schrijver construction of an independent set of
size 367 in C_7^{boxtimes 5} (arXiv:1808.07438, Sections 2 and 3), starting from
the circular graph C_{108,382} rather than from their printed answer.

Steps (i)-(v) of their Section 3 are followed literally:
  (i)   S = {t*(1,7,7^2,7^3,7^4) : t in Z_382}, independent in C_{108,382}^5;
  (ii)  add (40,123,40,123,40) mod 382 to every word;
  (iii) map every letter i (as an integer in [0,381]) to floor(i/54.5) in Z_7;
  (iv)  drop every word that is confusable with another surviving word -> M;
  (v)   extend M by a maximum independent set of the graph of addable words.

The paper states |M| = 327, that the extension graph has 71 vertices and 85 edges
and that its independence number is 40, giving 327 + 40 = 367.  Each of those five
numbers is recomputed here and compared.  Step (v) has more than one optimum in
general, so the set produced here need not equal the printed set R; what has to
agree is the size.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, confusable, read_set, sha256, verify, write_set  # noqa: E402

NC, KC, D = 382, 108, 5      # circular graph C_{108,382}
N = 7


def circ_dist(a, b, n):
    t = (a - b) % n
    return min(t, n - t)


def min_distance(words, n):
    """Exact minimum over pairs of the largest coordinatewise circular distance."""
    best = None
    w = list(words)
    for i in range(len(w)):
        for j in range(i + 1, len(w)):
            m = max(circ_dist(a, b, n) for a, b in zip(w[i], w[j]))
            if best is None or m < best:
                best = m
    return best


def max_independent_set(nv, adj):
    """Exact maximum independent set by branch and bound on bitmasks.
    nv <= 64 here (the extension graph has 71 vertices, so Python ints are used)."""
    best = [0, 0]   # size, mask

    def expand(cand, cur, cursize):
        if cand == 0:
            if cursize > best[0]:
                best[0], best[1] = cursize, cur
            return
        if cursize + bin(cand).count("1") <= best[0]:
            return
        # branch on the candidate vertex of highest degree inside `cand`
        vs = [v for v in range(nv) if cand >> v & 1]
        piv = max(vs, key=lambda v: bin(adj[v] & cand).count("1"))
        # either piv is in the set ...
        expand(cand & ~(adj[piv] | 1 << piv), cur | 1 << piv, cursize + 1)
        # ... or it is not
        expand(cand & ~(1 << piv), cur, cursize)

    expand((1 << nv) - 1, 0, 0)
    return best[0], [v for v in range(nv) if best[1] >> v & 1]


def main():
    rep = {}

    # (i) the circular-graph independent set
    g = (1, 7, 7 ** 2, 7 ** 3, 7 ** 4)
    S = [tuple((t * c) % NC for c in g) for t in range(NC)]
    assert len(set(S)) == NC
    dmin = min_distance(S, NC)
    rep["circular"] = {"n": NC, "k": KC, "d": D, "size": len(S), "min_distance": dmin,
                       "independent_in_C_108_382": dmin >= KC}
    assert dmin >= KC, f"minimum distance {dmin} < {KC}: S is not independent in C_{{108,382}}^5"

    # (ii) translate
    shift = (40, 123, 40, 123, 40)
    S2 = [tuple((a + b) % NC for a, b in zip(w, shift)) for w in S]

    # (iii) fold Z_382 -> Z_7 by i |-> floor(i/54.5) = floor(2i/109)
    Sp = sorted({tuple((2 * a) // 109 for a in w) for w in S2})
    assert all(0 <= c <= 6 for w in Sp for c in w)
    rep["folded"] = {"divisor": "54.5 (exactly: floor(2i/109))", "size_S_prime": len(Sp)}

    # (iv) drop every word confusable with another survivor
    M = [u for u in Sp if not any(v != u and confusable(u, v, N) for v in Sp)]
    rep["M"] = {"size": len(M), "paper": 327}

    # (v) extension graph: words x such that M + {x} stays independent
    Mset = set(M)
    cand = [x for x in ((a, b, c, d, e)
                        for a in range(N) for b in range(N) for c in range(N)
                        for d in range(N) for e in range(N))
            if x not in Mset and not any(confusable(x, m, N) for m in M)]
    nv = len(cand)
    adj = [0] * nv
    edges = 0
    for i in range(nv):
        for j in range(i + 1, nv):
            if confusable(cand[i], cand[j], N):
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                edges += 1
    alpha, chosen = max_independent_set(nv, adj)
    rep["extension_graph"] = {"vertices": nv, "edges": edges, "alpha": alpha,
                              "paper": {"vertices": 71, "edges": 85, "alpha": 40}}

    R2 = sorted(Mset | {cand[i] for i in chosen})
    rep["reproduced_size"] = len(R2)
    rep["matches_paper_numbers"] = (
        len(M) == 327 and nv == 71 and edges == 85 and alpha == 40 and len(R2) == 367)

    out = os.path.join(ROOT, "sets", "C7_d5_367_reproduced.txt")
    write_set(out, N, R2, [
        "Independent set of size 367 in C_7^{boxtimes 5}, rebuilt from scratch by",
        "scripts/construct_c7_d5_ps.py following steps (i)-(v) of arXiv:1808.07438, Section 3.",
        "Step (v) picks one maximum independent set of the 71-vertex extension graph; that",
        "optimum is not unique, so this set may differ from the set R printed in the paper.",
    ])
    rep["out"] = os.path.relpath(out, ROOT)
    rep["sha256"] = sha256(out)
    rep["verify"] = verify(out, ["--maximal"])

    # how does it relate to the printed set R?
    _, _, R = read_set(os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt"))
    rep["M_subset_of_printed_R"] = Mset <= set(R)
    rep["equals_printed_R"] = set(R2) == set(R)
    rep["overlap_with_printed_R"] = len(set(R2) & set(R))

    with open(os.path.join(ROOT, "results", "json", "construct_c7_d5_ps.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()

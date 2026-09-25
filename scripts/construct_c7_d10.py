"""S0.2(2): reconstruct the independent set of size 134753 in C_7^{boxtimes 10}
of Itty, Rosin, Carstensen, Reichman (arXiv:2607.21517), Section 3.1, from the
recipe in the paper.  The only external input is the 367-word set R of Polak and
Schrijver, which the paper cites and which lives in
sets/C7_d5_367_polak_schrijver.txt.

Every intermediate cardinality the paper states (|B| = 359, |A| = 20, |D| = 26,
|I| = 134753) is asserted here, so a silent deviation from the recipe fails loudly
instead of producing a smaller or larger set.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, confusable, read_set, sha256, verify, write_set  # noqa: E402

N = 7

# Section 3.1, table of r_j and q_j.
RQ = [
    ((1, 3, 4, 4, 6), (2, 3, 5, 4, 6)),
    ((3, 4, 0, 3, 5), (2, 4, 6, 3, 5)),
    ((5, 3, 1, 3, 4), (5, 3, 2, 3, 5)),
    ((4, 4, 6, 1, 6), (5, 4, 6, 0, 6)),
    ((6, 0, 6, 4, 5), (6, 1, 6, 5, 5)),
    ((0, 3, 5, 6, 5), (6, 3, 5, 0, 5)),
    ((6, 4, 3, 4, 0), (6, 4, 2, 4, 6)),
    ((6, 4, 5, 3, 2), (6, 5, 5, 3, 1)),
]
J0 = {0, 5, 6}
J1 = {1, 2, 3, 4, 7}


def main():
    src = os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt")
    n, d, R = read_set(src)
    assert (n, d, len(R)) == (7, 5, 367)
    Rset = set(R)
    rep = {}

    r = [RQ[j][0] for j in range(8)]
    q = [RQ[j][1] for j in range(8)]
    assert all(x in Rset for x in r), "some r_j is not in R"
    assert all(x not in Rset for x in q), "some q_j lies in R"

    # B = R \ {r_j}
    B = sorted(Rset - set(r))
    assert len(B) == 359, len(B)

    # X_0 = {(2-w1, w3, w0, 2-w2, w4)}, then one vector replaced.
    X0 = {((2 - w[1]) % N, w[3], w[0], (2 - w[2]) % N, w[4]) for w in R}
    assert len(X0) == 367
    assert (2, 4, 6, 3, 5) in X0
    X = sorted((X0 - {(2, 4, 6, 3, 5)}) | {(1, 5, 6, 3, 5)})
    assert len(X) == 367, len(X)

    P_H = [r[j] for j in sorted(J0)] + [q[j] for j in sorted(J1)]
    P_V = [q[j] for j in sorted(J0)] + [r[j] for j in sorted(J1)]

    A = [x for x in X if any(confusable(x, y, N) for y in P_V)]
    D = [x for x in X if any(confusable(x, y, N) for y in P_H)]
    assert len(A) == 20, f"|A| = {len(A)}, the paper says 20"
    assert len(D) == 26, f"|D| = {len(D)}, the paper says 26"
    assert not (set(A) & set(D)), "A and D overlap; the paper's h_j/v_j would be ambiguous"
    Aset, Dset = set(A), set(D)

    def h(j, x):
        return q[j] if ((j in J0 and x in Aset) or (j in J1 and x in Dset)) else r[j]

    def v(j, x):
        return q[j] if ((j in J0 and x in Dset) or (j in J1 and x in Aset)) else r[j]

    I = set()
    for b1 in B:
        for b2 in B:
            I.add(b1 + b2)
    assert len(I) == 359 * 359
    for x in X:
        for j in range(8):
            I.add(h(j, x) + x)
            I.add(x + v(j, x))
    assert len(I) == 359 * 359 + 8 * 367 + 8 * 367 == 134753, len(I)

    out = os.path.join(ROOT, "sets", "C7_d10_134753_itty_et_al.txt")
    write_set(out, N, sorted(I), [
        "Independent set of size 134753 in C_7^{boxtimes 10}.",
        "Source: N. Itty, C.D. Rosin, C. Carstensen, D. Reichman,",
        "        'Improved lower bounds for the Shannon capacity of odd cycles',",
        "        arXiv:2607.21517, Section 3.1.",
        "Rebuilt from the recipe in the paper by scripts/construct_c7_d10.py,",
        "starting from the 367-word set of arXiv:1808.07438.  Rows sorted lexicographically.",
    ])
    rep["out"] = os.path.relpath(out, ROOT)
    rep["sha256"] = sha256(out)
    rep["sizes"] = {"R": len(R), "B": len(B), "X": len(X), "A": len(A), "D": len(D), "I": len(I)}
    rep["paper_sizes"] = {"R": 367, "B": 359, "X": 367, "A": 20, "D": 26, "I": 134753}
    rep["sizes_match_paper"] = rep["sizes"] == rep["paper_sizes"]
    rep["verify"] = verify(out, ["--maximal"])   # ~30 s: 3^10 cells per vertex
    os.makedirs(os.path.join(ROOT, "results", "json"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "json", "construct_c7_d10.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()

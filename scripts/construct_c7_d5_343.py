"""S0.2(3): the cheap extra calibration -- an independent set of size 7^3 = 343 in
C_7^{boxtimes 5}.

The number 343 is due to Baumert, McEliece, Rodemich, Rumsey, Stanley and Taylor
(1971); that volume was not obtained, so the claim is carried here through the
quotation from Polak-Schrijver in SOURCES.md, and what is reproduced is the size,
by a linear (Cayley) construction over Z_7, not necessarily their set.

A linear code C <= Z_7^5 is closed under subtraction, so the independent-set
condition collapses to a statement about single codewords:

    C is independent in C_7^{boxtimes 5}  <=>  every nonzero c in C has a
    coordinate outside {0,1,6}  (i.e. at circular distance >= 2 from 0).

That gives a second, structurally different proof of independence for this set,
which is used here to cross-check the verifier: the two must agree.

The generator matrix is the lexicographically first one in reduced row echelon
form with pivots in columns 0,1,2 that satisfies the condition, so the choice is
deterministic and carries no hidden search.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, sha256, verify, write_set  # noqa: E402

N = 7
NEAR = {0, 1, N - 1}


def good(v):
    return any(c not in NEAR for c in v)


def search_generator():
    for a, b in itertools.product(range(N), repeat=2):
        r1 = (1, 0, 0, a, b)
        for c, d in itertools.product(range(N), repeat=2):
            r2 = (0, 1, 0, c, d)
            for e, f in itertools.product(range(N), repeat=2):
                r3 = (0, 0, 1, e, f)
                rows = (r1, r2, r3)
                if all(good(comb) for comb in span(rows) if any(comb)):
                    return rows
    return None


def span(rows):
    for k in itertools.product(range(N), repeat=len(rows)):
        yield tuple(sum(ki * r[i] for ki, r in zip(k, rows)) % N for i in range(5))


def main():
    rows = search_generator()
    assert rows is not None
    code = sorted(set(span(rows)))
    assert len(code) == N ** 3 == 343, len(code)

    # structural proof, independent of the verifier
    nonzero_all_good = all(good(c) for c in code if any(c))
    minimum_reached = min(
        max(min((a - b) % N, (b - a) % N) for a, b in zip(c, (0,) * 5)) for c in code if any(c))

    out = os.path.join(ROOT, "sets", "C7_d5_343_linear.txt")
    write_set(out, N, code, [
        "Independent set of size 7^3 = 343 in C_7^{boxtimes 5}: the linear code over Z_7",
        "with generator rows " + "; ".join(str(r) for r in rows) + ".",
        "Reproduces the size 343 attributed to Baumert, McEliece, Rodemich, Rumsey, Stanley",
        "and Taylor (1971) (cited through arXiv:1808.07438, see SOURCES.md [PS19-4]).",
        "Built by scripts/construct_c7_d5_343.py; the generator is the lexicographically",
        "first one in RREF with pivots in columns 0,1,2 that works.",
    ])
    rep = {
        "generator_rows": [list(r) for r in rows],
        "size": len(code),
        "expected_size": 343,
        "linear_argument_holds": nonzero_all_good,
        "min_coordinate_distance_over_nonzero_codewords": minimum_reached,
        "out": os.path.relpath(out, ROOT),
        "sha256": sha256(out),
    }
    rep["verify"] = verify(out, ["--both", "--maximal"])
    rep["two_proofs_agree"] = (rep["verify"]["independent"] is True) == nonzero_all_good
    with open(os.path.join(ROOT, "results", "json", "construct_c7_d5_343.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()

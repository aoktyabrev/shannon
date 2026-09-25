"""Addition to S0.2, made necessary by S0.3: the record for Theta(C_7) has moved
past arXiv:2607.21517, and the papers that moved it do not publish a set of
vertices at all -- they publish a recursion.  So the calibration has to cover the
recursion too, or Stage 1 would be aimed at a target that is already three papers
old.

Two things are checked here.

1. The base gadget.  Gao (arXiv:2607.27869, Prop. 4) claims that the 367-word set
   of Polak-Schrijver, together with the eight pairs (r_j,q_j), the transversals
   P_H, P_V and the auxiliary set X of Itty et al., is a gadget with parameter
   tuple (a,t,s,o,h,v) = (367,8,367,321,26,20).  Every clause of the gadget
   definition is re-checked here from the 367 vectors, exactly.

2. The recursion.  The product lemma turns two gadgets into one, with the code
   size and the parameters given by closed formulas.  The dynamic programme over
   split trees is integer arithmetic only; it is run here to k = 40 blocks
   (dimension 200) and the resulting M_40 is compared digit for digit with the
   value printed by Gao, and the bound with the value printed by Buys-Polak-Zuiddam
   (arXiv:2607.29681) for their stronger base gadget.

Nothing here is a search.  It is the check that our understanding of the current
record is right.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, confusable, read_set, verify, write_set  # noqa: E402

N = 7
RQ = [
    ((1, 3, 4, 4, 6), (2, 3, 5, 4, 6)), ((3, 4, 0, 3, 5), (2, 4, 6, 3, 5)),
    ((5, 3, 1, 3, 4), (5, 3, 2, 3, 5)), ((4, 4, 6, 1, 6), (5, 4, 6, 0, 6)),
    ((6, 0, 6, 4, 5), (6, 1, 6, 5, 5)), ((0, 3, 5, 6, 5), (6, 3, 5, 0, 5)),
    ((6, 4, 3, 4, 0), (6, 4, 2, 4, 6)), ((6, 4, 5, 3, 2), (6, 5, 5, 3, 1)),
]
J0, J1 = {0, 5, 6}, {1, 2, 3, 4, 7}

# Gao, arXiv:2607.27869, Section 5: M_40, printed in full.
GAO_M40 = int(
    "4085567963379990282748597333793399773399910167372462112610203714626938509773125898252337545387866277249")
GAO_BOUND_DIGITS = "3.2587891539086910161967650155206769"   # Gao, Theorem 1 [G26-8]
BPZ_BOUND_DIGITS = "3.258805369885"                       # Buys-Polak-Zuiddam, abstract


def int_nth_root(x, n):
    """Exact floor(x^(1/n)) for integers, by Newton's method."""
    if x == 0:
        return 0
    r = 1 << ((x.bit_length() + n - 1) // n + 1)
    while True:
        nr = ((n - 1) * r + x // r ** (n - 1)) // n
        if nr >= r:
            break
        r = nr
    while r ** n > x:
        r -= 1
    while (r + 1) ** n <= x:
        r += 1
    return r


def bound_digits(a, dim, digits=34):
    """floor(a^(1/dim) * 10^digits) / 10^digits, exactly, as a decimal string."""
    scaled = int_nth_root(a * 10 ** (dim * digits), dim)
    s = str(scaled)
    return s[:-digits] + "." + s[-digits:]


def check_base_gadget():
    n, d, R = read_set(os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt"))
    Rset = set(R)
    r = [RQ[j][0] for j in range(8)]
    q = [RQ[j][1] for j in range(8)]
    X0 = {((2 - w[1]) % N, w[3], w[0], (2 - w[2]) % N, w[4]) for w in R}
    X = sorted((X0 - {(2, 4, 6, 3, 5)}) | {(1, 5, 6, 3, 5)})
    P_H = [r[j] for j in sorted(J0)] + [q[j] for j in sorted(J1)]
    P_V = [q[j] for j in sorted(J0)] + [r[j] for j in sorted(J1)]

    xp = write_set(os.path.join(ROOT, "sets", "C7_d5_367_auxiliary_X.txt"), N, X, [
        "The auxiliary set X of the five-dimensional base gadget, 367 vectors in C_7^{boxtimes 5}.",
        "X = T(R) with the vector (2,4,6,3,5) replaced by (1,5,6,3,5), T(w) = (2-w1, w3, w0, 2-w2, w4);",
        "arXiv:2607.21517 Sec. 3.1 / arXiv:2607.27869 Sec. 4.  Built by scripts/gadget.py.",
    ])
    out = {}
    out["I0_independent"] = verify(os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt"))["independent"]
    out["X_independent"] = verify(xp)["independent"]
    out["sizes"] = {"I0": len(R), "X": len(X)}
    # (2) private pairs: N({q_j}) cap I_0 = {r_j}
    priv = []
    for j in range(8):
        nb = [x for x in R if confusable(q[j], x, N)]
        priv.append({"j": j, "neighbours_in_I0": [list(x) for x in nb], "is_private_pair": nb == [r[j]]})
    out["private_pairs"] = priv
    out["private_pairs_ok"] = all(p["is_private_pair"] for p in priv)
    out["q_not_in_I0"] = all(x not in Rset for x in q)
    # (3) transversals independent
    def indep(lst):
        return all(not confusable(lst[i], lst[j], N) for i in range(len(lst)) for j in range(i + 1, len(lst)))
    out["P_H_independent"] = indep(P_H)
    out["P_V_independent"] = indep(P_V)
    # (4) X disjoint from the sixteen endpoints
    out["X_disjoint_from_endpoints"] = not (set(X) & (set(r) | set(q)))
    # (5) the o/h/v split
    h = [x for x in X if any(confusable(x, y, N) for y in P_H)]
    v = [x for x in X if any(confusable(x, y, N) for y in P_V)]
    both = set(h) & set(v)
    o = [x for x in X if x not in set(h) and x not in set(v)]
    out["profile"] = {"a": len(R), "t": 8, "s": len(X), "o": len(o), "h": len(h), "v": len(v)}
    out["profile_claimed_by_gao"] = {"a": 367, "t": 8, "s": 367, "o": 321, "h": 26, "v": 20}
    out["confusable_with_both"] = len(both)
    out["profile_matches"] = (out["profile"] == out["profile_claimed_by_gao"] and not both)
    out["all_gadget_axioms_hold"] = bool(
        out["I0_independent"] and out["X_independent"] and out["private_pairs_ok"]
        and out["q_not_in_I0"] and out["P_H_independent"] and out["P_V_independent"]
        and out["X_disjoint_from_endpoints"] and out["profile_matches"])
    return out


def recursion(a1, t1, s1, o1, kmax=40):
    """Gao's dynamic programme, exact integers.  s,o,t depend only on the number of
    blocks; the code size a depends on the split tree and is maximised."""
    s = {1: s1}
    o = {1: o1}
    t = {1: t1}
    M = {1: a1}
    split = {1: None}
    for k in range(2, kmax + 1):
        s[k] = s1 ** k
        # delta = 2o - s is multiplicative; t_{i+j} = t_i o_j + o_i t_j
        delta = (2 * o1 - s1) ** k
        o[k] = (s[k] + delta) // 2
        assert 2 * o[k] == s[k] + delta
        i = 1
        t[k] = t[i] * o[k - i] + o[i] * t[k - i]
        bestv, besti = None, None
        for i in range(1, k // 2 + 1):
            j = k - i
            assert t[i] * o[j] + o[i] * t[j] == t[k], "t_k depends on the split -- formula wrong"
            val = (M[i] - t[i]) * (M[j] - t[j]) + t[i] * s[j] + s[i] * t[j]
            if bestv is None or val > bestv:
                bestv, besti = val, i
        M[k] = bestv
        split[k] = (besti, k - besti)
    return M, t, s, o, split


def main():
    rep = {"base_gadget": check_base_gadget()}

    # Gao's base gadget
    M, t, s, o, split = recursion(367, 8, 367, 321, 40)
    rep["closed_forms_ok"] = all(
        s[k] == 367 ** k and 2 * o[k] == 367 ** k + 275 ** k and 23 * t[k] == 2 * (367 ** k - 275 ** k)
        for k in range(1, 41))
    rep["gao"] = {
        "M_2": M[2], "M_2_is_itty_et_al_134753": M[2] == 134753,
        "M_40": str(M[40]), "M_40_matches_paper": M[40] == GAO_M40,
        "split_tree": {k: split[k] for k in (2, 3, 5, 10, 20, 40)},
        "bound_dim_200": bound_digits(M[40], 200),
        "paper_bound": GAO_BOUND_DIGITS,
        "bound_matches_paper": bound_digits(M[40], 200).startswith(GAO_BOUND_DIGITS),
    }

    # Buys-Polak-Zuiddam: same recursion, stronger base gadget (o = 322, v = 19)
    Mb, tb, sb, ob, splitb = recursion(367, 8, 367, 322, 40)
    rep["bpz"] = {
        "base_profile": [367, 8, 367, 322, 26, 19],
        "M_40": str(Mb[40]),
        "bound_dim_200": bound_digits(Mb[40], 200),
        "paper_bound": BPZ_BOUND_DIGITS,
        "bound_matches_paper": bound_digits(Mb[40], 200).startswith(BPZ_BOUND_DIGITS),
    }

    # How the bound behaves as the number of blocks grows.  Gao stops the dynamic
    # programme at k = 40; this runs it further, to see whether the ceiling is the
    # paper's choice or the method's.  Our own computation, not a published claim.
    rep["trend"] = {str(k): bound_digits(M[k], 5 * k, 15) for k in (1, 2, 3, 5, 10, 20, 40)}
    Mlong, _, _, _, _ = recursion(367, 8, 367, 321, 160)
    roots = {k: bound_digits(Mlong[k], 5 * k, 30) for k in range(1, 161)}
    kbest = max(roots, key=lambda k: roots[k])
    rep["saturation"] = {
        "dp_run_to_blocks": 160,
        "best_k": kbest, "best_dimension": 5 * kbest, "best_bound": roots[kbest],
        "bound_at_k40": roots[40],
        "k40_is_the_maximum": kbest == 40,
        "sample": {str(k): roots[k] for k in (40, 41, 50, 80, 120, 160)},
        "gao_balanced_limit_quoted": "3.2586163193818009407725377551",
        "note": ("Gao proves the balanced product converges to a value below his Theorem 1 "
                 "and that continuing from the 200-dimensional gadget only loses; this is the "
                 "same statement seen from the dynamic programme."),
    }
    # Sensitivity of the published recursion to the base profile.  This is an
    # evaluation of the formula of [G26-7] at hypothetical inputs, not a search:
    # no graph is touched.  It exists to make the Stage 1 target a number rather
    # than an aspiration.  Caveat, stated here and in the preregistration: the
    # entries hold s and o fixed while t varies, and a gadget with more private
    # pairs need not keep s = 367 and o = 321 -- more pairs mean more forbidden
    # territory for X.  The table bounds the prize, it does not promise it.
    sens = {}
    for t in (8, 9, 10, 12, 16):
        for o in range(321, 329):
            Ms, _, _, _, _ = recursion(367, t, 367, o, 40)
            sens[f"t={t},o={o}"] = bound_digits(Ms[40], 200, 20)
    for a in (368, 370, 375):
        Ms, _, _, _, _ = recursion(a, 8, 367, 321, 40)
        sens[f"a={a},t=8,o=321"] = bound_digits(Ms[40], 200, 20)
    rep["elementary_bounds"] = {
        "367^(1/5)": bound_digits(367, 5, 22),
        "134753^(1/10)": bound_digits(134753, 10, 22),
        "343^(1/5)": bound_digits(343, 5, 22),
        "33^(1/3)": bound_digits(33, 3, 22),
        "108^(1/4)": bound_digits(108, 4, 22),
        "350^(1/5)": bound_digits(350, 5, 22),
    }
    rep["profile_sensitivity"] = {
        "note": ("bound at k=40 blocks (dimension 200) through the homogeneous recursion of "
                 "[G26-7], as a function of the base profile; s=367 throughout unless stated"),
        "reference_gao_t8_o321": bound_digits(M[40], 200, 20),
        "current_record_T26": "3.2588326203532663091215390518104754376053875943219",
        "values": sens,
    }

    rep["all_pass"] = bool(rep["base_gadget"]["all_gadget_axioms_hold"] and rep["closed_forms_ok"]
                           and rep["gao"]["M_40_matches_paper"] and rep["gao"]["bound_matches_paper"]
                           and rep["bpz"]["bound_matches_paper"] and rep["gao"]["M_2_is_itty_et_al_134753"])
    with open(os.path.join(ROOT, "results", "json", "gadget.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps({k: v for k, v in rep.items() if k != "base_gadget"}, indent=2)[:3000])
    print("base gadget axioms hold:", rep["base_gadget"]["all_gadget_axioms_hold"],
          rep["base_gadget"]["profile"])


if __name__ == "__main__":
    main()

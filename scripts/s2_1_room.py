"""S2.1.a-c -- is there room for 367 words outside the forbidden region?

For a gadget with t private pairs the auxiliary set must avoid F = N[P_H] cap N[P_V],
so the question is alpha(G_F), G_F being C_7^{boxtimes 5} restricted to Z_7^5 \\ F.

Upper bounds, each with its certificate:

  * Lovasz: an independent set of G_F is independent in the whole graph, so
    alpha(G_F) <= alpha(C_7^5) <= floor(theta(C_7)^5) = 401. Certificate: the formula
    theta(C_n) = n cos(pi/n)/(1+cos(pi/n)) [PS19-2], recomputed at 60 digits.
  * box volume: a word occupies the 2^5 cells of its box and the boxes of an
    independent set are disjoint, so |X| <= (number of cells that some allowed word
    can cover)/32. A cell is coverable only if at least one of its 32 owners is
    allowed; cells whose owners all lie in F are dead. Exact count.
  * layers: the 7 layers of a fixed coordinate each carry an independent set of
    C_7^{boxtimes 4}, so |X| <= 7 * 115 [PS19-4, PS19-9]. Weak, kept as a sanity rail.

Lower bounds are exhibited sets: files that scripts/verify accepts and that a second
code path checks to be disjoint from F.

And the test that decides how hard the remaining search is: are those sets 1-opt and
2-opt optimal inside G_F -- can one allowed word be added, or one removed and two put
back? Both are answered exactly, by coverage counting rather than by search.
"""
import json
import os
import sys
from decimal import Decimal, getcontext
from itertools import product

getcontext().prec = 60
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s1_pairs import candidate_pairs  # noqa: E402
from setio import ROOT, confusable, read_set, sha256, verify  # noqa: E402

N, D = 7, 5
NV = N ** D
BOX = 2 ** D
ALPHA_C7_4_UPPER = 115          # [PS19-4] table, key b: alpha(C_n^d) <= alpha(C_n^{d-1}) n/2


def closed_nbhd(S):
    out = set()
    for v in S:
        for off in product((-1, 0, 1), repeat=D):
            out.add(tuple((v[i] + off[i]) % N for i in range(D)))
    return out


def colourings(qs):
    t = len(qs)
    conf = [[i != j and confusable(qs[i], qs[j], N) for j in range(t)] for i in range(t)]
    return [m for m in range(1 << t) if not (m & 1) and
            all(not (conf[i][j] and ((m >> i & 1) == (m >> j & 1)))
                for i in range(t) for j in range(i + 1, t))]


def regions(code_path):
    """Every proper colouring's forbidden region, smallest first."""
    _, _, I = read_set(code_path)
    pairs = candidate_pairs(I)
    rs = [r for r, _ in pairs]
    qs = [q for _, q in pairs]
    out = []
    for m in colourings(qs):
        PH = [qs[i] if (m >> i & 1) else rs[i] for i in range(len(qs))]
        PV = [rs[i] if (m >> i & 1) else qs[i] for i in range(len(qs))]
        NH, NV_ = closed_nbhd(PH), closed_nbhd(PV)
        out.append({"mask": m, "F": NH & NV_, "U": NH | NV_})
    out.sort(key=lambda r: len(r["F"]))
    return len(pairs), out


def box_cells(v):
    return [tuple((v[i] + o[i]) % N for i in range(D)) for o in product((0, 1), repeat=D)]


def owners(cell):
    """The 32 vertices whose box contains this cell."""
    return [tuple((cell[i] - o[i]) % N for i in range(D)) for o in product((0, 1), repeat=D)]


def volume_bound(F):
    dead = 0
    for cell in product(range(N), repeat=D):
        if all(o in F for o in owners(cell)):
            dead += 1
    return {"dead_cells": dead, "bound": (NV - dead) // BOX}


def opt_tests(S, F):
    """Exact 1-opt and 2-opt inside G_F, by coverage counting."""
    Sset = set(S)
    cover = {}            # allowed vertex -> list of set-words confusable with it
    for v in product(range(N), repeat=D):
        if v in Sset or v in F:
            continue
        blockers = [w for w in S if confusable(v, w, N)]
        if len(blockers) <= 2:
            cover[v] = blockers
    addable = [v for v, b in cover.items() if not b]
    singles = {}
    for v, b in cover.items():
        if len(b) == 1:
            singles.setdefault(b[0], []).append(v)
    two_opt = []
    for w, vs in singles.items():
        for i in range(len(vs)):
            for j in range(i + 1, len(vs)):
                if not confusable(vs[i], vs[j], N):
                    two_opt.append({"remove": list(w), "add": [list(vs[i]), list(vs[j])]})
    hist = {}
    for v, b in cover.items():
        hist[str(len(b))] = hist.get(str(len(b)), 0) + 1
    return {"blockers_histogram_up_to_two": {k: hist[k] for k in sorted(hist)},
            "addable_without_removing": [list(v) for v in addable],
            "one_opt_improves": bool(addable),
            "removals_that_free_a_single_word": len(singles),
            "two_opt_improvements": two_opt[:5],
            "two_opt_improves": bool(two_opt)}


def main():
    th = Decimal(json.load(open(os.path.join(ROOT, "results", "json", "theta.json")))
                 ["values"]["7"])
    lovasz = int(th ** 5)
    cases = [
        {"name": "t = 8, the published gadget", "code": "sets/C7_d5_367_polak_schrijver.txt",
         "exhibited": "sets/C7_d5_367_auxiliary_X.txt"},
        {"name": "t = 9, the published auxiliary set as a code",
         "code": "sets/C7_d5_367_auxiliary_X.txt", "exhibited": "sets/C7_d5_366_aux_for_t9.txt"},
        {"name": "t = 10, the set Stage 1 repaired",
         "code": "sets/C7_d5_367_auxiliary_X_best.txt",
         "exhibited": "sets/C7_d5_365_aux_for_t10.txt"},
    ]
    out = {"lovasz_bound": lovasz, "theta_to_the_fifth": str(th ** 5),
           "box_size": BOX, "universe": NV, "cases": []}

    # control: empty forbidden region
    empty = volume_bound(set())
    out["control_empty_F"] = {
        "volume_bound": empty["bound"], "lovasz_bound": lovasz,
        "known_lower_bound": 367,
        "in_range": 367 <= lovasz and empty["bound"] >= 367,
        "note": ("with no forbidden region the estimators must admit the known 367 and must not "
                 "beat the Lovasz bound; the volume bound is weaker than Lovasz, as expected"),
    }

    for c in cases:
        t, regs = regions(os.path.join(ROOT, c["code"]))
        smallest = regs[0]
        F = smallest["F"]
        vb = volume_bound(F)
        ex_path = os.path.join(ROOT, c["exhibited"])
        _, _, S = read_set(ex_path)
        disjoint = not (set(S) & F)
        row = {
            "case": c["name"], "t": t, "code": c["code"],
            "colourings": len(regs),
            "F_size_min": len(regs[0]["F"]), "F_size_max": len(regs[-1]["F"]),
            "colouring_used": smallest["mask"],
            "upper_bounds": {
                "lovasz_theta_fifth": lovasz,
                "box_volume": vb["bound"], "dead_cells": vb["dead_cells"],
                "layers_7_times_alpha_c7_4": 7 * ALPHA_C7_4_UPPER,
                "best": min(lovasz, vb["bound"], 7 * ALPHA_C7_4_UPPER),
            },
            "exhibited": {
                "file": c["exhibited"], "size": len(S), "sha256": sha256(ex_path)[:16],
                "verifier": {k: verify(ex_path)[k] for k in ("independent", "size")},
                "disjoint_from_F_second_path": disjoint,
            },
        }
        if disjoint:
            row["opt_tests"] = opt_tests(S, F)
        row["room_for_367"] = row["upper_bounds"]["best"] >= 367
        row["gap_upper_minus_367"] = row["upper_bounds"]["best"] - 367
        row["gap_367_minus_exhibited"] = 367 - len(S)
        out["cases"].append(row)

    pub = out["cases"][0]
    out["calibration"] = {
        "t8_exhibited_is_367": pub["exhibited"]["size"] == 367,
        "t8_upper_bound_at_least_367": pub["upper_bounds"]["best"] >= 367,
        "empty_F_in_range": out["control_empty_F"]["in_range"],
        "passed": bool(pub["exhibited"]["size"] == 367 and pub["upper_bounds"]["best"] >= 367
                       and out["control_empty_F"]["in_range"]),
    }
    t9 = next(c for c in out["cases"] if c["t"] == 9)
    out["verdict"] = {
        "criterion": "an upper bound below 367 at t = 9 would close the direction",
        "upper_bound_at_t9": t9["upper_bounds"]["best"],
        "direction_closed_by_arithmetic": t9["upper_bounds"]["best"] < 367,
        "reading": ("The cheap certificates are far above 367, so they cannot close anything: the "
                    "Lovasz bound does not see F at all and the volume bound is weaker still. What "
                    "is informative is the other side -- a verified independent set avoiding F of "
                    "366 words at t = 9 and 365 at t = 10 -- so the search is one or two words from "
                    "feasibility, not thirty-five."),
    }
    with open(os.path.join(ROOT, "results", "json", "s2_1_room.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"Lovasz bound floor(theta^5) = {lovasz}; control on empty F: "
          f"volume {out['control_empty_F']['volume_bound']}, in range "
          f"{out['control_empty_F']['in_range']}")
    print()
    print(f"{'case':38} {'t':>3} {'|F|':>6} {'upper':>6} {'exhibited':>10} {'1-opt':>6} {'2-opt':>6}")
    for r in out["cases"]:
        ot = r.get("opt_tests", {})
        print(f"{r['case'][:38]:38} {r['t']:>3} {r['F_size_min']:>6} "
              f"{r['upper_bounds']['best']:>6} {r['exhibited']['size']:>10} "
              f"{str(ot.get('one_opt_improves')):>6} {str(ot.get('two_opt_improves')):>6}")
    print()
    print("calibration:", out["calibration"])
    print("verdict:", out["verdict"]["direction_closed_by_arithmetic"],
          "| upper bound at t=9:", out["verdict"]["upper_bound_at_t9"])
    return 0 if out["calibration"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

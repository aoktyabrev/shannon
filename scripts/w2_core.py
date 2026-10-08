"""W2.1 -- the proved core of the second note, checked before it is written.

1. Definitions.  Our code computes F = N[P_H] cap N[P_V] and U = N[P_H] cup N[P_V] with
   closed neighbourhoods (scripts/s1_aux.c, closed_nbhd: all 3^5 offsets in {-1,0,1}^5).
   Gao and Tandon define N(S) as the closed neighbourhood [G26-10, T26-7], and the gadget
   conditions X cap N(P_H) cap N(P_V) = {} and O = X minus (N(P_H) cup N(P_V)) [G26-1] are
   exactly F and U.  For one pair, F = A cap B and U = A cup B with A = N[r], B = N[q].

2. The identity.  |A cap B| + |A cup B| = |A| + |B| = 2 * 3^d whenever |N[v]| = 3^d, which
   holds in C_n^d for every n >= 3.  For a family, |F| + |U| = |N[P_H]| + |N[P_V]|, which
   equals 2 t 3^d only when the closed neighbourhoods inside each transversal are pairwise
   disjoint.  Both checked numerically: every shape for d = 3, 4, 5 and n = 3, 4, 5, 7, 9; and
   every t = 8 and t = 9 configuration of I_0 and X Gao.

3. The second 486.  The Stage 2.2 swap plateau has 486 codes.  This checks, constructively,
   whether that is the same 2 * 3^5: the component of the ten-candidate code is rebuilt as
   five commuting three-state switches, the order-5 stabiliser is examined, and the two
   components are related by an automorphism.
"""
import json
import os
import subprocess
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, confusable, read_set  # noqa: E402

BIN = os.path.join(ROOT, "scripts")
TMP = os.environ.get("SHANNON_TMP", "/tmp/shannon-w2")


def run(a):
    r = subprocess.run([str(x) for x in a], capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        raise RuntimeError(r.stderr[-1000:])
    return r.stdout


def cnbhd(v, n):
    return {tuple((v[i] + o[i]) % n for i in range(len(v))) for o in product((-1, 0, 1), repeat=len(v))}


def identity_checks():
    rows = []
    for d in (3, 4, 5):
        for n in (3, 4, 5, 7, 9):
            if n ** d > 60000:
                continue
            r = (0,) * d
            A = cnbhd(r, n)
            by_k = {}
            ok_sum = True
            for dv in product((-1, 0, 1), repeat=d):
                if not any(dv):
                    continue
                q = tuple(x % n for x in dv)
                B = cnbhd(q, n)
                k = sum(1 for x in dv if x)
                inter, uni = len(A & B), len(A | B)
                ok_sum &= inter + uni == 2 * 3 ** d
                by_k.setdefault(k, set()).add(inter)
            rows.append({"d": d, "n": n, "closed_nbhd": len(A), "is_3_pow_d": len(A) == 3 ** d,
                         "sum_equals_2_3_pow_d_for_every_shape": ok_sum,
                         "forbidden_by_shape": {str(k): sorted(v) for k, v in sorted(by_k.items())},
                         "shape_formula_3_pow_d_minus_k_2_pow_k": all(v == {3 ** (d - k) * 2 ** k} for k, v in by_k.items())})
    return rows


def family_checks():
    out = []
    for code, tmin in (("sets/C7_d5_367_polak_schrijver.txt", 8), ("sets/C7_d5_367_auxiliary_X.txt", 9)):
        st = json.loads(run([BIN + "/s2_2_conf", "stats", code, "--tmin", tmin]))
        pairs = [(tuple(r), tuple(q)) for r, q in st["pairs"]]
        for line in run([BIN + "/s2_2_conf", "list", code, "--tmin", tmin]).split("\n"):
            if not line.strip():
                continue
            t, fam, col, fsize = map(int, line.split())
            if t != len(pairs):
                continue
            PH = [pairs[j][1] if (col >> j & 1) else pairs[j][0] for j in range(t)]
            PV = [pairs[j][0] if (col >> j & 1) else pairs[j][1] for j in range(t)]
            NH = set().union(*(cnbhd(v, 7) for v in PH))
            NV = set().union(*(cnbhd(v, 7) for v in PV))
            F, U = NH & NV, NH | NV
            out.append({"code": code, "t": t, "colouring": col, "F": len(F), "U": len(U),
                        "N_PH": len(NH), "N_PV": len(NV), "F_plus_U": len(F) + len(U),
                        "equals_N_PH_plus_N_PV": len(F) + len(U) == len(NH) + len(NV),
                        "two_t_3_pow_5": 2 * t * 243, "F_matches_C": len(F) == fsize})
    return {"rows": out,
            "identity_holds_on_every_configuration": all(r["equals_N_PH_plus_N_PV"] and r["F_matches_C"] for r in out),
            "F_plus_U_range_by_t": {str(t): [min(r["F_plus_U"] for r in out if r["t"] == t),
                                             max(r["F_plus_U"] for r in out if r["t"] == t)] for t in (8, 9)},
            "two_t_3_pow_5_by_t": {"8": 3888, "9": 4374}}


def plateau_structure():
    os.makedirs(TMP, exist_ok=True)
    pd = os.path.join(TMP, "plateau")
    if not os.path.isdir(pd):
        os.makedirs(pd)
    for f in os.listdir(pd):
        os.remove(os.path.join(pd, f))
    starts = []
    for base in ("sets", "sets/pipeline_codes"):
        for f in sorted(os.listdir(os.path.join(ROOT, base))):
            p = os.path.join(ROOT, base, f)
            if f.endswith(".txt") and os.path.isfile(p):
                n, d, I = read_set(p)
                if (n, d) == (7, 5) and len(I) == 367:
                    starts.append(p)
    run([BIN + "/s2_2_conf", "plateau", *starts, "--nodes", 200000, "--tmin", 99, "--out", pd, "--write-all"])
    files = sorted(os.path.join(pd, f) for f in os.listdir(pd))
    codes = [frozenset(read_set(f)[2]) for f in files]
    index = {c: i for i, c in enumerate(codes)}
    moves = []
    for f in files:
        st = json.loads(run([BIN + "/s2_2_conf", "stats", f, "--tmin", 99]))
        moves.append([(tuple(r), tuple(q)) for r, q in st["pairs"]])
    # the 1-swap graph
    adj = [set() for _ in codes]
    for i, c in enumerate(codes):
        for r, q in moves[i]:
            j = index.get(frozenset((c - {r}) | {q}))
            if j is None:
                raise RuntimeError("a 1-swap left the plateau")
            adj[i].add(j)
    comp = [-1] * len(codes)
    nc = 0
    for s in range(len(codes)):
        if comp[s] >= 0:
            continue
        stack = [s]
        comp[s] = nc
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if comp[v] < 0:
                    comp[v] = nc
                    stack.append(v)
        nc += 1
    edges = sum(len(a) for a in adj) // 2
    # rebuild the component of the ten-candidate code from five commuting switches
    m = max(range(len(codes)), key=lambda i: len(moves[i]))
    M = codes[m]
    nb = [(r, q) for r, q in moves[m]]
    # two moves of M belong to the same switch iff after one of them the other is gone
    def after(c, mv):
        r, q = mv
        return frozenset((c - {r}) | {q})
    same = {}
    for a in range(len(nb)):
        ca = after(M, nb[a])
        ia = index[ca]
        avail = set(moves[ia])
        for b in range(len(nb)):
            if a != b and nb[b] not in avail:
                same.setdefault(a, set()).add(b)
    switches = []
    seen = set()
    for a in range(len(nb)):
        if a in seen:
            continue
        grp = {a} | same.get(a, set())
        seen |= grp
        switches.append(sorted(grp))
    built = set()
    ok_build = all(len(s) == 2 for s in switches) and len(switches) == 5
    if ok_build:
        for states in product((0, 1, 2), repeat=5):     # 1 = the middle state of M
            c = M
            for s, st in zip(switches, states):
                if st == 1:
                    continue
                c = after(c, nb[s[0] if st == 0 else s[1]])
            built.add(c)
    comp_m = {codes[i] for i in range(len(codes)) if comp[i] == comp[m]}
    # the stabiliser of M, and how it acts on coordinates and on the switches
    mf = files[m]
    stab = run([BIN + "/s2_2_aut", "stab", mf]).split("\n")
    elems = [list(map(int, l.split())) for l in stab[1:] if l.strip()]

    def g(v, e):
        p, sg, c = e[:5], e[5], e[6:]
        return tuple(((((7 - v[p[i]]) % 7) if (sg >> i & 1) else v[p[i]]) + c[i]) % 7 for i in range(5))
    cycle_types = []
    for e in elems:
        p = e[:5]
        seenp, lens = set(), []
        for i in range(5):
            if i in seenp:
                continue
            L, j = 0, i
            while j not in seenp:
                seenp.add(j)
                j = p[j]
                L += 1
            lens.append(L)
        cycle_types.append(sorted(lens))
    sw_of = {}
    for si, s in enumerate(switches):
        for a in s:
            sw_of[nb[a]] = si
    perm_on_switches = []
    for e in elems:
        img = []
        for si, s in enumerate(switches):
            r, q = nb[s[0]]
            gr, gq = g(r, e), g(q, e)
            img.append(sw_of.get((gr, gq), sw_of.get((gq, gr))))
        perm_on_switches.append(img)
    # the two components: does the automorphism T of [IRCR26]/[G26] exchange them?
    T = lambda w: ((2 - w[1]) % 7, w[3], w[0], (2 - w[2]) % 7, w[4])
    i0 = index.get(frozenset(read_set(os.path.join(ROOT, "sets/C7_d5_367_polak_schrijver.txt"))[2]))
    ti0 = index.get(frozenset(T(w) for w in codes[i0]))
    t_maps_component = None
    if ti0 is not None:
        img_comp = {comp[index[frozenset(T(w) for w in codes[i])]] for i in range(len(codes))
                    if comp[i] == comp[i0] and frozenset(T(w) for w in codes[i]) in index}
        t_maps_component = sorted(img_comp)
    degs = {}
    for i in range(len(codes)):
        if comp[i] == comp[m]:
            degs[len(adj[i])] = degs.get(len(adj[i]), 0) + 1
    return {"codes": len(codes), "components": nc, "component_sizes": sorted({sum(1 for x in comp if x == k) for k in range(nc)}),
            "one_swap_edges": edges, "edges_of_two_copies_of_P3_box_5": 2 * 5 * 2 * 3 ** 4,
            "degree_hist_in_component": dict(sorted(degs.items())),
            "P3_box_5_degree_hist": {str(5 + k): __import__("math").comb(5, k) * 2 ** (5 - k) for k in range(6)},
            "switches_found": len(switches), "moves_per_switch": [len(s) for s in switches],
            "component_rebuilt_from_switches": ok_build and built == comp_m,
            "shapes_of_switch_moves": [[sum(1 for i in range(5) if nb[a][0][i] != nb[a][1][i]) for a in s] for s in switches],
            "coordinates_moved_per_switch": [sorted({i for a in s for i in range(5) if nb[a][0][i] != nb[a][1][i]}) for s in switches],
            "stabiliser_order": len(elems), "stabiliser_coordinate_cycle_types": cycle_types,
            "stabiliser_action_on_switches": perm_on_switches,
            "I0_component": comp[i0] if i0 is not None else None,
            "T_of_I0_in_plateau": ti0 is not None, "T_of_I0_component": comp[ti0] if ti0 is not None else None,
            "T_maps_I0_component_to": t_maps_component}


def main():
    out = {"definitions": {
        "ours": "F = N[P_H] cap N[P_V], U = N[P_H] cup N[P_V], closed neighbourhoods of 3^5 vertices (scripts/s1_aux.c)",
        "gao": "N(S) is the closed neighborhood of S [G26-10]; gadget condition X cap N(P_H) cap N(P_V) = {} and O = X minus (N(P_H) cup N(P_V)) [G26-1]",
        "tandon": "N(S) denotes the closed neighborhood of S [T26-7]",
        "same": True,
        "one_pair": "for t = 1, F = N[r] cap N[q] and U = N[r] cup N[q]",
        "family": "|F| + |U| = |N[P_H]| + |N[P_V]| <= 2 t 3^d, equality iff the neighbourhoods within each transversal are pairwise disjoint"}}
    out["identity"] = identity_checks()
    out["identity_all_pass"] = all(r["is_3_pow_d"] and r["sum_equals_2_3_pow_d_for_every_shape"] for r in out["identity"])
    out["shape_formula_holds_for_n_ge_4"] = all(r["shape_formula_3_pow_d_minus_k_2_pow_k"] for r in out["identity"] if r["n"] >= 4)
    out["shape_formula_fails_for_n_3"] = not any(r["shape_formula_3_pow_d_minus_k_2_pow_k"] for r in out["identity"] if r["n"] == 3)
    out["family"] = family_checks()
    out["plateau"] = plateau_structure()
    txt = json.dumps(out, indent=2).replace(os.path.abspath(TMP), "$SHANNON_TMP")
    open(os.path.join(ROOT, "results", "json", "w2_core.json"), "w").write(txt)
    p = out["plateau"]
    print(json.dumps({"identity_all_pass": out["identity_all_pass"],
                      "shape_formula_n_ge_4": out["shape_formula_holds_for_n_ge_4"],
                      "shape_formula_fails_n_3": out["shape_formula_fails_for_n_3"],
                      "family_identity": out["family"]["identity_holds_on_every_configuration"],
                      "F_plus_U_by_t": out["family"]["F_plus_U_range_by_t"],
                      "plateau": {k: v for k, v in p.items() if k not in ("stabiliser_action_on_switches",)}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

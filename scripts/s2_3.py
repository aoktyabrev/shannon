"""Stage 2.3 -- which shapes a private pair can have, what each costs, and how large a code
carrying it can be.  Writes results/json/s2_3.json; scripts/make_results.py prints it.

  S2.3.a  the 242 shapes d = q - r, their orbits under the stabiliser of a vertex, and the
          forbidden and penalised vertices of one pair, all counted directly
          (scripts/s2_3_shapes costs); the candidate shapes and box coverage of every code;
          the largest code carrying a private pair of each shape, by the exhaustive exact
          local construction (scripts/s2_3_shapes local) over every code in sets/ and every
          code of the Stage 2.2 swap plateau
  S2.3.b  the nine-pair regions of Stage 2.2 split into per-pair part and cross terms; the
          per-pair invariant |F| + |U| = 486; the price of each shape in o
  S2.3.c  the price in code size: o needed to clear the record at a = 367 .. 364, against the
          best ratio of u to its random expectation that any auxiliary set has achieved
"""
import json
import os
import resource
import shutil
import subprocess
import sys
import time
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gadget import bound_digits, recursion  # noqa: E402
from setio import ROOT, confusable, read_set, sha256, verify, write_set  # noqa: E402

N, D, NV = 7, 5, 7 ** 5
TMP = os.environ.get("SHANNON_TMP", "/tmp/shannon-s2_3")
BIN = os.path.join(ROOT, "scripts")
RECORD = "3.2588326203532663091215390518104754376053875943219"


def run(args):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        raise RuntimeError(f"{args[0]}: {r.stderr[-1500:]}")
    return r.stdout


def runj(args):
    return json.loads(run(args))


def rel(p):
    return os.path.relpath(os.path.abspath(p), ROOT)


def nbhd(v):
    return {tuple((v[i] + o[i]) % N for i in range(D)) for o in product((-1, 0, 1), repeat=D)}


def d5_codes():
    out = []
    for base in (os.path.join(ROOT, "sets"), os.path.join(ROOT, "sets", "pipeline_codes")):
        for f in sorted(os.listdir(base)):
            p = os.path.join(base, f)
            if f.endswith(".txt") and os.path.isfile(p) and read_set(p)[:2] == (N, D):
                out.append(p)
    return out


def private_pair_second_path(path):
    """Read r, q from the header and count q's neighbours in the set, in Python."""
    r = q = None
    for line in open(path):
        if line.startswith("# r ="):
            a = line.split()
            r, q = tuple(map(int, a[3:8])), tuple(map(int, a[10:15]))
    _, _, S = read_set(path)
    nb = [w for w in S if confusable(q, w, N)]
    k = sum(1 for i in range(D) if r[i] != q[i])
    return {"r": list(r), "q": list(q), "k": k, "q_in_set": q in set(S),
            "q_neighbours_in_set": [list(w) for w in nb], "private": nb == [r] and q not in set(S)}


def decomposition():
    """Stage 2.2's nine-pair regions on X Gao: per-pair union and cross terms, every colouring."""
    code = "sets/C7_d5_367_auxiliary_X.txt"
    st = runj([BIN + "/s2_2_conf", "stats", code, "--tmin", 9])
    pairs = [(tuple(r), tuple(q)) for r, q in st["pairs"]]
    lines = run([BIN + "/s2_2_conf", "list", code, "--tmin", 9]).split("\n")
    rows = []
    for l in lines:
        if not l.strip():
            continue
        t, fam, col, fsize = map(int, l.split())
        PH = [pairs[j][1] if (col >> j & 1) else pairs[j][0] for j in range(len(pairs)) if fam >> j & 1]
        PV = [pairs[j][0] if (col >> j & 1) else pairs[j][1] for j in range(len(pairs)) if fam >> j & 1]
        NH, NVv = set().union(*map(nbhd, PH)), set().union(*map(nbhd, PV))
        F, U = NH & NVv, NH | NVv
        per = set().union(*(nbhd(r) & nbhd(q) for r, q in pairs))
        rows.append({"colouring": col, "F": len(F), "F_from_C": fsize, "per_pair_union": len(per),
                     "per_pair_sum": sum(len(nbhd(r) & nbhd(q)) for r, q in pairs),
                     "cross_terms": len(F - per), "U": len(U)})
    return {"code": code, "rows": rows,
            "F_matches_C_count": all(r["F"] == r["F_from_C"] for r in rows),
            "per_pair_sum": rows[0]["per_pair_sum"],
            "per_pair_union": sorted({r["per_pair_union"] for r in rows}),
            "cross_terms_min": min(r["cross_terms"] for r in rows), "cross_terms_max": max(r["cross_terms"] for r in rows),
            "F_min": min(r["F"] for r in rows), "F_max": max(r["F"] for r in rows),
            "U_min": min(r["U"] for r in rows), "U_max": max(r["U"] for r in rows)}


def achieved_ratio():
    """The best auxiliary set on record: the published X at t = 8 under its colouring, and the
    o = 322 set. u against its random expectation 367 |U| / 16807."""
    code = "sets/C7_d5_367_polak_schrijver.txt"
    st = runj([BIN + "/s2_2_conf", "stats", code, "--tmin", 8])
    pairs = [(tuple(r), tuple(q)) for r, q in st["pairs"]]
    out = []
    for xf in ("sets/C7_d5_367_auxiliary_X.txt", "sets/C7_d5_367_auxiliary_X_o322.txt"):
        _, _, X = read_set(os.path.join(ROOT, xf))
        Xs = set(X)
        best = None
        for l in run([BIN + "/s2_2_conf", "list", code, "--tmin", 8]).split("\n"):
            if not l.strip():
                continue
            t, fam, col, fsize = map(int, l.split())
            PH = [pairs[j][1] if (col >> j & 1) else pairs[j][0] for j in range(8)]
            PV = [pairs[j][0] if (col >> j & 1) else pairs[j][1] for j in range(8)]
            NH, NVv = set().union(*map(nbhd, PH)), set().union(*map(nbhd, PV))
            if Xs & (NH & NVv):
                continue
            U = NH | NVv
            u = len(Xs & U)
            rec = {"aux_set": xf, "U": len(U), "u": u, "o": len(X) - u,
                   "u_random_expectation": round(len(X) * len(U) / NV, 2),
                   "ratio": round(u / (len(X) * len(U) / NV), 4)}
            if best is None or rec["o"] > best["o"]:
                best = rec
        out.append(best)
    return out


def o_needed(a, t, s=367):
    lo, hi = 0, s + 1
    while lo < hi:
        mid = (lo + hi) // 2
        if mid > s:
            return None
        if bound_digits(recursion(a, t, s, mid, 40)[0][40], 200, 34) > RECORD[:36]:
            hi = mid
        else:
            lo = mid + 1
    return lo if lo <= s else None


def main():
    os.makedirs(TMP, exist_ok=True)
    ru0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    t0 = time.time()
    out = {}
    costs = runj([BIN + "/s2_3_shapes", "costs"])
    by_k = {o["k"]: o for o in costs["orbits"]}
    out["shapes"] = {"total": costs["shapes"], "orbits": sorted(costs["orbits"], key=lambda o: o["k"]),
                     "formula_3_pow_5_minus_k_times_2_pow_k": all(o["forbidden_by_one_pair"] == 3 ** (5 - o["k"]) * 2 ** o["k"]
                                                                  for o in costs["orbits"]),
                     "F_plus_U_per_pair": sorted({o["forbidden_by_one_pair"] + o["penalised_by_one_pair"] for o in costs["orbits"]})}
    out["calibration"] = {"k2_gives_108": by_k[2]["forbidden_by_one_pair"] == 108,
                          "shapes_total_242": costs["shapes"] == 242,
                          "orbit_sizes": [by_k[k]["size"] for k in range(1, 6)],
                          "constant_on_orbits": all(o["constant_on_orbit"] for o in costs["orbits"])}
    # every code in sets/, and every code of the swap plateau, rebuilt here
    pd = os.path.join(TMP, "plateau")
    shutil.rmtree(pd, ignore_errors=True)
    os.makedirs(pd)
    starts = [p for p in d5_codes() if len(read_set(p)[2]) == 367]
    run([BIN + "/s2_2_conf", "plateau", *starts, "--nodes", 200000, "--tmin", 99, "--out", pd, "--write-all"])
    plateau = sorted(os.path.join(pd, f) for f in os.listdir(pd))
    pop = []
    for p in d5_codes():
        c = runj([BIN + "/s2_3_shapes", "cells", p])
        h = c["covered_cells_in_box_hist"]
        pop.append({"file": rel(p), "size": c["size"], "uncovered_cells": c["uncovered_cells"],
                    "addable_vertices": c["addable_vertices"], "candidate_shapes_by_k": c["candidate_shapes_by_k"],
                    "fewest_covered_cells_in_a_box_outside_the_code": next(i for i, x in enumerate(h) if x)})
    out["population"] = sorted(pop, key=lambda r: (r["size"], r["file"]))
    pl_shapes = [0] * 5
    pl_minc = 32
    for p in plateau:
        c = runj([BIN + "/s2_3_shapes", "cells", p])
        pl_shapes = [a + b for a, b in zip(pl_shapes, c["candidate_shapes_by_k"])]
        pl_minc = min(pl_minc, next(i for i, x in enumerate(c["covered_cells_in_box_hist"]) if x))
    out["plateau_cells"] = {"codes": len(plateau), "candidate_shapes_by_k_summed": pl_shapes,
                            "fewest_covered_cells_in_a_box": pl_minc}
    # the local construction
    ld = os.path.join(TMP, "local")
    shutil.rmtree(ld, ignore_errors=True)
    os.makedirs(ld)
    best = {k: {"size": 0} for k in range(1, 6)}
    srcs = d5_codes() + plateau
    for i, p in enumerate(srcs):
        o = os.path.join(ld, "src%04d" % i)
        os.makedirs(o)
        r = runj([BIN + "/s2_3_shapes", "local", p, "--out", o])
        for b in r["by_k"]:
            if b["best_size"] > best[b["k"]]["size"]:
                best[b["k"]] = {"size": b["best_size"], "source": rel(p) if not p.startswith(TMP) else "plateau",
                                "source_size": r["size"], "words_deleted": b["words_deleted_at_best"],
                                "file": os.path.join(o, "best_k%d.txt" % b["k"])}
            if r["freed_sets_over_cap"]:
                best[b["k"]].setdefault("capped_runs", 0)
    rows = []
    for k in range(1, 6):
        b = best[k]
        v = verify(b["file"])
        pp = private_pair_second_path(b["file"])
        cells = runj([BIN + "/s2_3_shapes", "cells", b["file"]])
        dst = os.path.join(ROOT, "sets", "C7_d5_%d_private_pair_k%d.txt" % (b["size"], k))
        _, _, S = read_set(b["file"])
        hdr = [l[2:].rstrip("\n") for l in open(b["file"]) if l.startswith("# ")]
        write_set(dst, N, S, hdr + ["Stage 2.3, scripts/s2_3.py: the largest set found carrying a private pair of this shape."])
        rows.append({"k": k, "largest_size": b["size"], "source": b["source"], "source_size": b["source_size"],
                     "words_deleted": b["words_deleted"], "file": rel(dst), "sha256": sha256(dst)[:16],
                     "independent": v["independent"], "verified_size": v["size"], "pair_private_second_path": pp["private"],
                     "pair_k_second_path": pp["k"], "candidate_shapes_of_the_set": cells["candidate_shapes_by_k"]})
    out["realisability"] = rows
    out["realisability_checked"] = all(r["independent"] and r["pair_private_second_path"] and r["pair_k_second_path"] == r["k"]
                                       and r["verified_size"] == r["largest_size"] for r in rows)
    out["calibration"]["local_construction_reaches_367_at_k2"] = best[2]["size"] == 367
    out["decomposition"] = decomposition()
    out["calibration"]["decomposition_reproduces_1098"] = (out["decomposition"]["F_min"] == 1098
                                                           and out["decomposition"]["F_matches_C_count"])
    out["achieved_ratio"] = achieved_ratio()
    # the price
    price = []
    for a in (367, 366, 365, 364):
        for t in range(8, 17):
            on = o_needed(a, t)
            price.append({"a": a, "t": t, "o_needed": on, "u_allowed": (367 - on) if on is not None else None})
    out["price"] = price
    ratio = min(r["ratio"] for r in out["achieved_ratio"])
    model = []
    for k in range(1, 6):
        for a in (367, 366, 365):
            for t in (9, 13, 16):
                on = o_needed(a, t)
                if on is None:
                    continue
                U = t * by_k[k]["penalised_by_one_pair"]          # no overlaps: an upper bound on |U|
                exp_u = 367 * U / NV
                model.append({"k": k, "a": a, "t": t, "F_no_cross_terms": t * by_k[k]["forbidden_by_one_pair"],
                              "U_no_overlaps": U, "u_allowed": 367 - on, "u_random": round(exp_u, 1),
                              "ratio_needed": round((367 - on) / exp_u, 3)})
    out["price_model"] = {"best_ratio_on_record": ratio, "rows": model,
                          "note": ("ratio = u / (367 |U| / 16807); a ratio below the best ever achieved "
                                   "is not a proof of impossibility, it is the distance to the best known search")}
    out["calibration"]["passed"] = all(v for k, v in out["calibration"].items() if isinstance(v, bool))
    ru1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (ru1.ru_utime - ru0.ru_utime) + (ru1.ru_stime - ru0.ru_stime)
    out["budget"] = {"ceiling_core_hours": 4, "core_seconds": round(cpu + (time.process_time()), 1),
                     "wall_seconds": round(time.time() - t0, 1)}
    txt = json.dumps(out, indent=2).replace(os.path.abspath(TMP), "$SHANNON_TMP")
    open(os.path.join(ROOT, "results", "json", "s2_3.json"), "w").write(txt)
    print(json.dumps({"calibration": out["calibration"], "realisability": [(r["k"], r["largest_size"]) for r in rows],
                      "budget": out["budget"]}, indent=1))
    return 0 if out["calibration"]["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

"""S0.1: the anti-vacuum calibration of the verifier.

A verifier that answers INDEPENDENT unconditionally would pass every test in
S0.2, so each test below is a case where the verifier can fail and is required
not to.  Nothing here searches for new bounds.

  A  single-vertex corruption, on every reproduced construction; the ground truth
     is computed independently (a linear scan of the one changed vertex against
     the rest, which is exact because the rest is untouched), and the verifier has
     to agree with it vertex by vertex -- including the corruptions that happen to
     leave an independent set, where a verifier that shouted FAIL at every change
     would be wrong;
  B  maximality: for the maximal sets, no vertex of the whole of Z_n^d can be
     added; checked exhaustively over the universe, not by sampling;
  C  small d (2,3,4): the box method is compared with the plain quadratic pair
     test on the same file, on independent and on dependent inputs;
  D  the chunked low-memory path must give the same answer as the single-pass
     path, on the largest set we have;
  E  negative controls: random sets and a deliberately planted adjacent pair must
     be reported as NOT independent;
  F  the trivial values alpha(C_7) = 3 and alpha(C_7^2) = 10 are recomputed from
     scratch by the exact solver and compared with the literature;
  G  the tests are shown to have teeth: a deliberately defective build of the same
     verifier (scripts/verify_mutant, which only notices repeated vertices) is run
     through them and must be rejected.
"""
import json
import os
import random
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, VERIFY, confusable, read_set, verify, write_set  # noqa: E402

TMP = os.environ.get("SHANNON_TMP", "/tmp/shannon-calib")
MIS = os.path.join(ROOT, "scripts", "mis")
os.makedirs(TMP, exist_ok=True)

SETS = [
    "sets/C7_d5_367_polak_schrijver.txt",
    "sets/C7_d5_367_reproduced.txt",
    "sets/C7_d5_343_linear.txt",
    "sets/C7_d10_134753_itty_et_al.txt",
]


def tmp_set(name, n, rows):
    return write_set(os.path.join(TMP, name), n, rows, ["temporary set for calibration"])


def test_A_corruption(rel, sample, seed=12345):
    """Replace one vertex by a neighbour of itself and require the verifier to match truth."""
    path = os.path.join(ROOT, rel)
    n, d, rows = read_set(path)
    rowset = set(rows)
    idx = list(range(len(rows)))
    if sample is not None and sample < len(idx):
        random.Random(seed).shuffle(idx)
        idx = sorted(idx[:sample])
    out = {"set": rel, "n": n, "d": d, "size": len(rows), "tested": 0, "skipped_in_set": 0,
           "broke_independence": 0, "still_independent": 0, "disagreements": []}
    for k, i in enumerate(idx):
        v = rows[i]
        c = i % d
        v2 = tuple((x + 1) % n if j == c else x for j, x in enumerate(v))
        if v2 in rowset:
            out["skipped_in_set"] += 1
            continue
        rest = rows[:i] + rows[i + 1:]
        truth = not any(confusable(v2, u, n) for u in rest)
        p = tmp_set(f"corrupt_{k}.txt", n, rest + [v2])
        got = verify(p)["independent"]
        out["tested"] += 1
        if truth:
            out["still_independent"] += 1
        else:
            out["broke_independence"] += 1
        if got != truth:
            out["disagreements"].append({"vertex_index": i, "vertex": list(v), "replacement": list(v2),
                                         "verifier": got, "truth": truth})
        os.remove(p)
    out["pass"] = not out["disagreements"] and out["tested"] > 0
    return out


def test_A_nonmaximal(seed=99):
    """The same corruption test on sets that are NOT maximal, so that some corruptions
    leave an independent set.  A verifier that answered NOT INDEPENDENT to every change
    would pass test A above and fail here."""
    out = []
    n, d, rows = read_set(os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt"))
    rng = random.Random(seed)
    shrunk = sorted(rng.sample(rows, 300))            # a proper subset of the 367-set
    a2 = json.loads(subprocess.run([MIS, "7", "2", "60", "--json"], capture_output=True,
                                   text=True).stdout)
    s2 = [tuple(x) for x in a2["set"]]
    prod3 = product_set(7, s2, [(0,), (2,), (4,)])    # 30 vertices in C_7^3, alpha = 33
    for name, nn, rs in (("subset300_d5", 7, shrunk), ("product30_d3", 7, prod3)):
        rset = set(rs)
        res = {"set": name, "d": len(rs[0]), "size": len(rs), "tested": 0,
               "broke_independence": 0, "still_independent": 0, "disagreements": []}
        for i, v in enumerate(rs):
            c = i % len(v)
            v2 = tuple((x + 1) % nn if j == c else x for j, x in enumerate(v))
            if v2 in rset:
                continue
            rest = rs[:i] + rs[i + 1:]
            truth = not any(confusable(v2, u, nn) for u in rest)
            p = tmp_set(f"nm_{name}_{i}.txt", nn, rest + [v2])
            got = verify(p)["independent"]
            os.remove(p)
            res["tested"] += 1
            res["still_independent" if truth else "broke_independence"] += 1
            if got != truth:
                res["disagreements"].append({"i": i, "verifier": got, "truth": truth})
        res["pass"] = not res["disagreements"] and res["still_independent"] > 0
        out.append(res)
    return out


def test_G_mutant():
    """Run the defective build through the sharpest of the tests above.  It has to fail."""
    mutant = os.path.join(ROOT, "scripts", "verify_mutant")
    if not os.path.exists(mutant):
        return {"skipped": "scripts/verify_mutant not built", "pass": False}
    n, d, rows = read_set(os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt"))
    v = rows[0]
    v2 = tuple((x + 1) % n if j == 0 else x for j, x in enumerate(v))
    p = tmp_set("mutant_case.txt", n, rows + [v2])
    def run(binary, path, extra=()):
        out = subprocess.run([binary, path, "--json", *extra], capture_output=True, text=True)
        return json.loads(out.stdout)
    good = run(VERIFY, p)
    bad = run(mutant, p)
    os.remove(p)
    return {"case": "the 367-set plus one adjacent vertex",
            "honest_verifier_says_independent": good["independent"],
            "mutant_says_independent": bad["independent"],
            "mutant_is_rejected": bad["independent"] is True and good["independent"] is False,
            "pass": bad["independent"] is True and good["independent"] is False}


def test_B_maximality(rel):
    path = os.path.join(ROOT, rel)
    r = verify(path, ["--maximal"])
    return {"set": rel, "addable_vertices": r["addable_vertices"], "maximal": r["maximal"],
            "independent": r["independent"]}


def product_set(n, a, b):
    return [x + y for x in a for y in b]


def test_C_small_d():
    """d = 2, 3, 4: box test vs the plain quadratic pair test, both ways round."""
    res = []
    a1 = [(0,), (2,), (4,)]                       # alpha(C_7) = 3
    a2 = json.loads(subprocess.run([MIS, "7", "2", "60", "--json"], capture_output=True,
                                   text=True).stdout)
    s2 = [tuple(x) for x in a2["set"]]
    cases = {
        2: s2,                                    # exact optimum, 10 vertices
        3: product_set(7, s2, a1),                # 30 vertices, product construction
        4: product_set(7, s2, s2),                # 100 vertices, product construction
    }
    for d, rows in cases.items():
        p = tmp_set(f"small_d{d}.txt", 7, rows)
        r = verify(p, ["--both"])
        res.append({"d": d, "size": len(rows), "independent": r["independent"],
                    "quadratic_independent": r["quadratic_independent"], "agree": r["agree"],
                    "case": "independent"})
        # and a dependent version of the same file: append a neighbour of the first vertex
        v = rows[0]
        v2 = tuple((x + 1) % 7 if j == 0 else x for j, x in enumerate(v))
        if v2 not in set(rows):
            p2 = tmp_set(f"small_d{d}_bad.txt", 7, rows + [v2])
            r2 = verify(p2, ["--both"])
            res.append({"d": d, "size": len(rows) + 1, "independent": r2["independent"],
                        "quadratic_independent": r2["quadratic_independent"], "agree": r2["agree"],
                        "case": "dependent"})
            os.remove(p2)
        os.remove(p)
    ok = all(c["agree"] for c in res) and all(
        c["independent"] == (c["case"] == "independent") for c in res)
    return {"cases": res, "pass": ok}


def test_D_chunked():
    """The low-memory path (many passes) must agree with the single-pass path."""
    rel = "sets/C7_d10_134753_itty_et_al.txt"
    path = os.path.join(ROOT, rel)
    n, d, rows = read_set(path)
    full = verify(path)
    chunked = verify(path, ["--mem-mb", "1"])
    v = rows[0]
    v2 = tuple((x + 1) % n if j == 0 else x for j, x in enumerate(v))
    assert v2 not in set(rows)
    bad = tmp_set("d10_bad.txt", n, rows + [v2])
    bad_full = verify(bad)
    bad_chunked = verify(bad, ["--mem-mb", "1"])
    os.remove(bad)
    return {"set": rel,
            "single_pass": {"passes": full["box_passes"], "independent": full["independent"]},
            "chunked": {"passes": chunked["box_passes"], "independent": chunked["independent"]},
            "dependent_single_pass": {"passes": bad_full["box_passes"], "independent": bad_full["independent"]},
            "dependent_chunked": {"passes": bad_chunked["box_passes"], "independent": bad_chunked["independent"]},
            "pass": (full["independent"] == chunked["independent"] is True
                     and bad_full["independent"] == bad_chunked["independent"] is False
                     and chunked["box_passes"] > 1)}


def test_E_negative_controls(seed=7):
    rng = random.Random(seed)
    res = []
    for d, size in ((3, 40), (5, 400), (10, 2000)):
        rows = set()
        while len(rows) < size:
            rows.add(tuple(rng.randrange(7) for _ in range(d)))
        rows = sorted(rows)
        p = tmp_set(f"random_d{d}.txt", 7, rows)
        r = verify(p, ["--both"] if d <= 5 else [])
        truth = all(not confusable(rows[i], rows[j], 7)
                    for i in range(len(rows)) for j in range(i + 1, len(rows)))
        res.append({"d": d, "size": size, "verifier": r["independent"], "truth": truth,
                    "ok": r["independent"] == truth})
        os.remove(p)
    # a planted adjacent pair inside an otherwise independent set
    n, d, rows = read_set(os.path.join(ROOT, "sets/C7_d5_367_polak_schrijver.txt"))
    v = rows[100]
    v2 = tuple((x + 1) % n for x in v)
    p = tmp_set("planted.txt", n, rows + [v2])
    r = verify(p, ["--both"])
    res.append({"case": "planted adjacent pair in the 367-set", "verifier": r["independent"],
                "truth": False, "ok": r["independent"] is False, "agree": r["agree"]})
    os.remove(p)
    return {"cases": res, "pass": all(c["ok"] for c in res)}


def test_F_trivial_values():
    lit = {1: 3, 2: 10}
    out = []
    for d, want in lit.items():
        r = json.loads(subprocess.run([MIS, "7", str(d), "120", "--json"],
                                      capture_output=True, text=True).stdout)
        out.append({"d": d, "computed": r["best_found"], "proved_optimal": r["proved_optimal"],
                    "literature": want, "match": r["best_found"] == want and r["proved_optimal"]})
    # the same solver on other cycles, against the closed formula floor((n^2-n)/4) of Baumert et al.
    for n in (5, 9, 11, 13):
        r = json.loads(subprocess.run([MIS, str(n), "2", "300", "--json"],
                                      capture_output=True, text=True).stdout)
        out.append({"n": n, "d": 2, "computed": r["best_found"], "proved_optimal": r["proved_optimal"],
                    "formula_floor_n2_minus_n_over_4": (n * n - n) // 4,
                    "match": r["best_found"] == (n * n - n) // 4 and r["proved_optimal"]})
    return {"cases": out, "pass": all(c["match"] for c in out)}


def main():
    rep = {}
    rep["A_corruption"] = [
        test_A_corruption(SETS[0], None),
        test_A_corruption(SETS[1], None),
        test_A_corruption(SETS[2], None),
        test_A_corruption(SETS[3], 100),
    ]
    rep["A_nonmaximal"] = test_A_nonmaximal()
    rep["A_pass"] = (all(t["pass"] for t in rep["A_corruption"])
                     and all(t["pass"] for t in rep["A_nonmaximal"]))
    rep["B_maximality"] = [test_B_maximality(s) for s in SETS]
    rep["B_pass"] = all(t["maximal"] for t in rep["B_maximality"])
    rep["C_small_d"] = test_C_small_d()
    rep["D_chunked"] = test_D_chunked()
    rep["E_negative"] = test_E_negative_controls()
    rep["F_trivial"] = test_F_trivial_values()
    rep["G_mutant"] = test_G_mutant()
    rep["all_pass"] = (rep["A_pass"] and rep["B_pass"] and rep["C_small_d"]["pass"]
                       and rep["D_chunked"]["pass"] and rep["E_negative"]["pass"]
                       and rep["F_trivial"]["pass"] and rep["G_mutant"]["pass"])
    with open(os.path.join(ROOT, "results", "json", "calibration.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps({k: v for k, v in rep.items() if k.endswith("pass")}, indent=2))
    print("full report: results/json/calibration.json")


if __name__ == "__main__":
    main()

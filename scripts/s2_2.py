"""Stage 2.2 -- nine-pair codes with a different forbidden region.

The driver for the whole stage, run once from a clean state; it writes
results/json/s2_2.json, from which scripts/make_results.py prints the Stage 2.2
section.  Order, as in PREREGISTRATION_S2_2.md:

  controls   the automorphism generator (anti-vacuum), the invariance lemma on random
             non-identity g, the t = 8 counts, the sweep histogram of Stage 1 reproduced
             exactly and 367 reached at t = 8, and k-opt recovering 367 from planted sets
  S2.2.a     every d = 5 code in sets/: candidates, conflict graph, colourings, |F|
  S2.2.c.1   the swap plateau around every 367-word code: 1-swaps (exhaustive), 2-swaps,
             window 3-swaps from every Aut-class, window 4-swaps around the t* >= 9 classes
  S2.2.b     every forbidden region with t >= 9, up to Aut; the group sweep of every
             source class against each, with exact repair; exact k-opt inside G_F on the
             best sets; the looseness statistic

Heavy lifting is in C: scripts/s2_2_conf (configurations, plateau, k-swaps),
scripts/s2_2_aut (the group), scripts/s2_2_sweep (sweep + repair).  Every set that a
claim rests on is passed through scripts/verify and, where F matters, checked disjoint
from F by a second code path here.

CPU time is measured with getrusage over the children, not estimated.
"""
import json
import os
import random
import re
import resource
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, read_set, sha256, verify, write_set  # noqa: E402

N, D, NV = 7, 5, 7 ** 5
TMP = os.environ.get("SHANNON_TMP", "/tmp/shannon-s2_2")
BIN = os.path.join(ROOT, "scripts")
K4_SECONDS = float(os.environ.get("S2_2_K4_SECONDS", "3600"))
JOBS = 8
OUT = {}


def run(args, **kw):
    r = subprocess.run([str(a) for a in args], capture_output=True, text=True, cwd=ROOT, **kw)
    if r.returncode not in (0,):
        raise RuntimeError(f"{args[0]} exited {r.returncode}: {r.stderr[-2000:]}")
    return r.stdout


def runj(args):
    return json.loads(run(args))


def rel(p):
    return os.path.relpath(os.path.abspath(p), ROOT)


def enc(c):
    return sum(c[i] * 7 ** i for i in range(D))


def read_F(path):
    return {int(x) for x in open(path).read().split()}


def F_as_code(path, dst):
    L = sorted(read_F(path))
    with open(dst, "w") as f:
        f.write(f"{N} {D} {len(L)}\n")
        for v in L:
            f.write(" ".join(str((v // 7 ** i) % 7) for i in range(D)) + "\n")
    return dst


def disjoint_second_path(set_path, F_path):
    """Disjointness from F checked here, in Python, not by the C code that built the set."""
    _, _, X = read_set(set_path)
    F = read_F(F_path)
    return not any(enc(x) in F for x in X)


def d5_codes():
    out = []
    for base in (os.path.join(ROOT, "sets"), os.path.join(ROOT, "sets", "pipeline_codes")):
        for f in sorted(os.listdir(base)):
            p = os.path.join(base, f)
            if f.endswith(".txt") and os.path.isfile(p):
                n, d, _ = read_set(p)
                if (n, d) == (N, D):
                    out.append(p)
    return out


def stats(path, tmin=1):
    return runj([BIN + "/s2_2_conf", "stats", path, "--tmin", tmin])


def compact(st):
    ts = str(st["t_star"])
    bt = st["by_t"].get(ts, {})
    return {"candidates": st["candidates"], "distinct_centres": st["distinct_centres"],
            "conflict_edges": st["conflict_edges"], "t_star": st["t_star"],
            "configurations_at_t_star": bt.get("configurations", 0),
            "F_min": bt.get("F_min"), "F_max": bt.get("F_max"),
            "weight_hist": st["weight_hist"], "fingerprint": st["fingerprint"]}


def bipartite(pairs):
    qs = [tuple(p[1]) for p in pairs]
    n = len(qs)
    adj = [[j for j in range(n) if j != i and all(min((qs[i][k] - qs[j][k]) % N, (qs[j][k] - qs[i][k]) % N) <= 1
                                                  for k in range(D))] for i in range(n)]
    col = [-1] * n
    comps = 0
    for s in range(n):
        if col[s] >= 0:
            continue
        comps += 1
        col[s] = 0
        st = [s]
        while st:
            u = st.pop()
            for v in adj[u]:
                if col[v] < 0:
                    col[v] = 1 - col[u]
                    st.append(v)
                elif col[v] == col[u]:
                    return False, comps
    return True, comps


# ---------------------------------------------------------------- controls
def controls():
    c = {}
    c["automorphism_generator"] = runj([BIN + "/s2_2_aut", "check"])
    # the lemma on random non-identity elements
    rng = random.Random(20261008)
    lemma = []
    for code in ("sets/C7_d5_367_polak_schrijver.txt", "sets/C7_d5_367_auxiliary_X.txt"):
        base = compact(stats(os.path.join(ROOT, code)))
        # the argmin fields are indices into the candidate list, whose order is not invariant;
        # what the lemma claims is about the numbers
        inv = lambda bt: {t: (v["configurations"], v["F_min"], v["F_max"]) for t, v in bt.items()}
        base_full = inv(stats(os.path.join(ROOT, code))["by_t"])
        for trial in range(3):
            while True:
                p = list(range(D))
                rng.shuffle(p)
                sg = rng.randrange(32)
                sh = [rng.randrange(N) for _ in range(D)]
                if not (p == list(range(D)) and sg == 0 and sh == [0] * D):
                    break
            img = os.path.join(TMP, f"lemma_{os.path.basename(code)}_{trial}.txt")
            run([BIN + "/s2_2_aut", "apply", code, *p, sg, *sh, img])
            st = stats(img)
            same_class = runj([BIN + "/s2_2_aut", "classes", code, img])["classes"] == 1
            lemma.append({"code": code, "g": {"perm": p, "signs": sg, "shift": sh},
                          "image_independent": verify(img)["independent"],
                          "image_differs_from_code": set(read_set(img)[2]) != set(read_set(os.path.join(ROOT, code))[2]),
                          "stats_equal": inv(st["by_t"]) == base_full and compact(st)["candidates"] == base["candidates"],
                          "classified_isomorphic": same_class})
    c["lemma_on_random_g"] = lemma
    c["lemma_passed"] = all(r["stats_equal"] and r["classified_isomorphic"] and r["image_independent"]
                            and r["image_differs_from_code"] for r in lemma)
    # non-isomorphism must be detected too: I0 against X Gao
    c["iso_negative_control"] = runj([BIN + "/s2_2_aut", "classes", "sets/C7_d5_367_polak_schrijver.txt",
                                      "sets/C7_d5_367_auxiliary_X.txt"])["classes"] == 2
    # t = 8 counts
    i0 = compact(stats(os.path.join(ROOT, "sets/C7_d5_367_polak_schrijver.txt")))
    c["t8_counts"] = i0
    c["t8_counts_match_stage2"] = (i0["candidates"] == 8 and i0["t_star"] == 8
                                   and (i0["F_min"], i0["F_max"]) == (956, 984))
    return c


def sweep_calibration(c):
    d = os.path.join(TMP, "F_I0")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    run([BIN + "/s2_2_conf", "list", "sets/C7_d5_367_polak_schrijver.txt", "--tmin", 8, "--out", d])
    Fs = sorted(os.path.join(d, f) for f in os.listdir(d))
    srcs = sorted(os.path.join(ROOT, "sets", "pipeline_codes", f) for f in os.listdir(os.path.join(ROOT, "sets", "pipeline_codes")))
    adm = os.path.join(TMP, "adm_I0")
    shutil.rmtree(adm, ignore_errors=True)
    os.makedirs(adm)
    args = [BIN + "/s2_2_sweep", "--repair", 2, "--out", adm, "--keep", 0]
    for f in Fs:
        args += ["--F", f]
    for s in srcs:
        args += ["--src", s]
    r = runj(args)
    stage1 = json.load(open(os.path.join(ROOT, "results", "json", "s1_aux.json")))["translations_with_bad_eq"]
    files = sorted(f for f in os.listdir(adm) if f.startswith("admissible"))
    ex = None
    if files:
        p = os.path.join(adm, files[0])
        fi = int(re.search(r"_F(\d+)_", files[0]).group(1))
        ex = {"size": verify(p)["size"], "independent": verify(p)["independent"],
              "disjoint_from_F_second_path": disjoint_second_path(p, Fs[fi])}
    c["sweep_t8"] = {"histogram": r["grand_hist"], "stage1_histogram": stage1,
                     "histogram_reproduced": r["grand_hist"] == stage1,
                     "best_repaired_size": r["grand_best_repaired_size"],
                     "admissible_367_images": r["admissible_full_size"], "example_admissible": ex,
                     "seconds": r["seconds"]}
    # the colouring under which the published auxiliary set is admissible, for the k-opt control
    _, _, X = read_set(os.path.join(ROOT, "sets/C7_d5_367_auxiliary_X.txt"))
    xs = {enc(x) for x in X}
    pub = [f for f in Fs if not (read_F(f) & xs)]
    return pub[0]


def kopt_controls(c, F_pub):
    rows = []
    for k in (2, 3):
        planted = os.path.join(TMP, f"planted{k}.txt")
        out = run([sys.executable, BIN + "/s2_2_plant.py", "sets/C7_d5_367_auxiliary_X.txt", F_pub, planted, k])
        v = verify(planted)
        d = os.path.join(TMP, f"kopt_ctrl{k}")
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        s = json.loads(run([BIN + "/s2_2_conf", "kswap", planted, "--k", k, "--forbid", F_pub, "--out", d]).strip().split("\n")[-1])
        imp = sorted(os.listdir(d))
        rec = None
        if imp:
            p = os.path.join(d, imp[0])
            vv = verify(p)
            rec = {"size": vv["size"], "independent": vv["independent"],
                   "disjoint_from_F_second_path": disjoint_second_path(p, F_pub)}
        rows.append({"planted_k": k, "planting": out.strip(), "planted_size": v["size"],
                     "planted_independent": v["independent"], "window_k": k,
                     "improving_windows": s["windows_admitting_more_than_k"], "recovered": rec})
    c["kopt_planted"] = rows
    c["kopt_passed"] = all(r["recovered"] and r["recovered"]["size"] == 367 and r["recovered"]["independent"]
                           and r["recovered"]["disjoint_from_F_second_path"] for r in rows)


# ---------------------------------------------------------------- S2.2.a
def population():
    rows = []
    for p in d5_codes():
        st = stats(p)
        v = verify(p)
        bip, comps = bipartite(st["pairs"])
        row = {"file": rel(p), "size": st["size"], "independent": v["independent"], "sha256": sha256(p)[:16]}
        row.update(compact(st))
        row["conflict_graph_bipartite"] = bip
        row["conflict_graph_components"] = comps
        row["allowed_vertices_min"] = NV - row["F_max"] if row["F_max"] else NV
        row["allowed_vertices_max"] = NV - row["F_min"] if row["F_min"] else NV
        row["F_spread_percent"] = (round(100.0 * (row["F_max"] - row["F_min"]) / row["F_min"], 2)
                                   if row["F_min"] else None)
        rows.append(row)
    rows.sort(key=lambda r: (r["size"], r["t_star"], r["file"]))
    return rows


# ---------------------------------------------------------------- S2.2.c.1
def plateau():
    starts = [p for p in d5_codes() if read_set(p)[2] and len(read_set(p)[2]) == 367]
    d = os.path.join(TMP, "plateau")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    r1 = runj([BIN + "/s2_2_conf", "plateau", *starts, "--nodes", 200000, "--tmin", 9, "--out", d, "--write-all"])
    r2 = runj([BIN + "/s2_2_conf", "plateau", *starts, "--nodes", 200000, "--tmin", 9, "--k2"])
    allf = sorted(os.path.join(d, f) for f in os.listdir(d) if f.startswith("all_"))
    bad = [f for f in allf if not verify(f)["independent"]]
    cl = runj([BIN + "/s2_2_aut", "classes", *allf])
    reps = {}
    for f, k in cl["rows"]:
        reps.setdefault(k, f)
    classes = []
    for k in sorted(reps):
        st = compact(stats(reps[k]))
        members = sum(1 for _, kk in cl["rows"] if kk == k)
        classes.append({"class": k, "representative": reps[k], "members_in_plateau": members,
                        "stabiliser_order": cl["stabiliser_orders"][k], **st})
    # where the published and known codes sit
    known = {}
    for p in starts:
        _, _, I = read_set(p)
        S = set(I)
        for f in allf:
            if set(read_set(f)[2]) == S:
                known[rel(p)] = dict(cl["rows"])[f]
                break
    hist = {}
    for c in classes:
        hist[str(c["t_star"])] = hist.get(str(c["t_star"]), 0) + 1
    res = {"starts": [rel(p) for p in starts],
           "one_swaps": {k: r1[k] for k in ("visited", "exhausted", "t_star_hist", "distinct_fingerprints")},
           "two_swaps": {k: r2[k] for k in ("visited", "exhausted", "k2_moves", "k2_new")},
           "codes_written": len(allf), "codes_not_independent": len(bad),
           "aut_classes": cl["classes"], "classes_by_t_star": dict(sorted(hist.items(), key=lambda kv: int(kv[0]))),
           "class_table": classes, "known_codes_class": known}
    return res, [c["representative"] for c in classes], classes, allf


def kswaps(reps, classes, allf):
    d3 = os.path.join(TMP, "k3")
    shutil.rmtree(d3, ignore_errors=True)
    os.makedirs(d3)
    chunks = [reps[i::JOBS] for i in range(JOBS)]

    def k3(i):
        o = os.path.join(d3, "chunk%d" % i)
        os.makedirs(o, exist_ok=True)
        ls = run([BIN + "/s2_2_conf", "kswap", *chunks[i], "--k", 3, "--tmin", 9, "--out", o, "--nodes", 100000]).strip().split("\n")
        return json.loads(ls[-1]), [json.loads(l) for l in ls[:-1]]
    with ThreadPoolExecutor(max_workers=JOBS) as ex:
        parts = list(ex.map(k3, range(JOBS)))
    s3 = {"codes": sum(p[0]["codes"] for p in parts),
          "windows": [sum(p[0]["windows"][i] for p in parts) for i in range(5)],
          "moves": sum(p[0]["moves"] for p in parts), "new_codes": sum(p[0]["new_codes"] for p in parts),
          "windows_admitting_more_than_k": sum(p[0]["windows_admitting_more_than_k"] for p in parts),
          "seconds": max(p[0]["seconds"] for p in parts)}
    new3 = [r for p in parts for r in p[1]]
    plateau_sets = {frozenset(read_set(f)[2]) for f in allf}
    outside = [r for r in new3 if "file" in r and frozenset(read_set(r["file"])[2]) not in plateau_sets]
    t9 = [p for p, c in zip(reps, classes) if c["t_star"] >= 9]
    d4 = os.path.join(TMP, "k4")
    shutil.rmtree(d4, ignore_errors=True)
    os.makedirs(d4)
    per = K4_SECONDS / max(1, len(t9))

    def k4(p):
        o = os.path.join(d4, os.path.basename(p)[:-4])
        os.makedirs(o, exist_ok=True)
        ls = run([BIN + "/s2_2_conf", "kswap", p, "--k", 4, "--tmin", 9, "--out", o, "--nodes", 100000,
                  "--seconds", per]).strip().split("\n")
        return p, json.loads(ls[-1]), [json.loads(l) for l in ls[:-1]], o
    with ThreadPoolExecutor(max_workers=JOBS) as ex:
        res4 = list(ex.map(k4, t9))
    out4, outside4 = [], []
    for p, s, rows, o in res4:
        out4.append({"code": rel(p), **{k: s[k] for k in ("windows", "moves", "new_codes", "exhausted", "seconds",
                                                           "windows_admitting_more_than_k")},
                     "new_t_star_hist": hist_of(rows)})
        outside4 += [r for r in rows if "file" in r and frozenset(read_set(r["file"])[2]) not in plateau_sets]
    newcodes = outside + outside4
    # are any of the codes outside the plateau new up to Aut, and what do they give?
    cls_new = None
    if newcodes:
        files = reps + [r["file"] for r in newcodes]
        cl = runj([BIN + "/s2_2_aut", "classes", *files])
        k_of = dict(cl["rows"])
        new_classes = sorted({k_of[r["file"]] for r in newcodes} - {k_of[p] for p in reps})
        rows = []
        for k in new_classes:
            f = next(r["file"] for r in newcodes if k_of[r["file"]] == k)
            rows.append({"representative": f, "independent": verify(f)["independent"], **compact(stats(f))})
        cls_new = {"classes_outside_plateau": len(new_classes), "rows": rows}
    return {"k3": {k: s3[k] for k in ("codes", "windows", "moves", "new_codes", "windows_admitting_more_than_k", "seconds")},
            "k3_new_t_star_hist": hist_of(new3), "k3_codes_outside_plateau": len(outside),
            "k4": out4, "k4_codes_outside_plateau": len(outside4), "outside_plateau_classes": cls_new}


def hist_of(rows):
    h = {}
    for r in rows:
        h[str(r["t_star"])] = h.get(str(r["t_star"]), 0) + 1
    return dict(sorted(h.items(), key=lambda kv: int(kv[0])))


# ---------------------------------------------------------------- S2.2.b
def regions(classes):
    t9 = [c for c in classes if c["t_star"] >= 9]
    allF = []
    for c in t9:
        d = os.path.join(TMP, "F_class%d" % c["class"])
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        run([BIN + "/s2_2_conf", "list", c["representative"], "--tmin", 9, "--out", d])
        for f in sorted(os.listdir(d)):
            allF.append((c["class"], os.path.join(d, f)))
    dc = os.path.join(TMP, "F_as_codes")
    shutil.rmtree(dc, ignore_errors=True)
    os.makedirs(dc)
    codes = [F_as_code(f, os.path.join(dc, "c%d_%s" % (k, os.path.basename(f)))) for k, f in allF]
    cl = runj([BIN + "/s2_2_aut_big", "classes", *codes])
    k_of = dict(cl["rows"])
    reps, table = {}, {}
    for (cc, f), code in zip(allF, codes):
        k = k_of[code]
        t = int(re.search(r"F_t(\d+)_", f).group(1))
        reps.setdefault(k, f)
        e = table.setdefault(k, {"F_class": k, "t": t, "F_size": len(read_F(f)), "from_code_classes": {}})
        e["from_code_classes"][str(cc)] = e["from_code_classes"].get(str(cc), 0) + 1
    summary = {"configurations_listed": len(allF), "code_classes_with_t_star_ge_9": [c["class"] for c in t9],
               "F_classes": cl["classes"], "table": [table[k] for k in sorted(table)]}
    by_t = {}
    for e in summary["table"]:
        by_t.setdefault(str(e["t"]), []).append(e["F_size"])
    summary["F_classes_by_t"] = {t: {"classes": len(v), "F_min": min(v), "F_max": max(v)} for t, v in by_t.items()}
    return summary, reps


def sweep(Freps, srcs):
    near = os.path.join(TMP, "near")
    shutil.rmtree(near, ignore_errors=True)
    os.makedirs(near)
    args = [BIN + "/s2_2_sweep", "--repair", 3, "--slack", 1, "--keep", 2, "--out", near]
    keys = sorted(Freps)
    for k in keys:
        args += ["--F", Freps[k]]
    for s in srcs:
        args += ["--src", s]
    r = runj(args)
    per = []
    for i, k in enumerate(keys):
        rows = [x for x in r["rows"] if x["F"] == Freps[k]]
        per.append({"F_class": k, "F_size": rows[0]["F_size"], "min_hits": min(x["min_hits"] for x in rows),
                    "best_repaired_size": max(x["best_repaired_size"] for x in rows),
                    "sources_reaching_best": sum(1 for x in rows if x["best_repaired_size"] == max(y["best_repaired_size"] for y in rows)),
                    "admissible_full_size": sum(x["admissible_full_size"] for x in rows),
                    "hist": [sum(x["hist"][h] for x in rows) for h in range(8)]})
    files = sorted(os.listdir(near))
    adm = [f for f in files if f.startswith("admissible")]
    checked = []
    for f in adm:
        p = os.path.join(near, f)
        fi = int(re.search(r"_F(\d+)_", f).group(1))
        v = verify(p)
        checked.append({"file": f, "size": v["size"], "independent": v["independent"],
                        "disjoint_from_F_second_path": disjoint_second_path(p, Freps[keys[fi]])})
    return {"pairs": r["pairs"], "group_elements_per_pair": r["group_elements_per_pair"],
            "images_scored": r["pairs"] * r["group_elements_per_pair"], "grand_hist": r["grand_hist"],
            "grand_min_hits": r["grand_min_hits"], "grand_best_repaired_size": r["grand_best_repaired_size"],
            "admissible_full_size": r["admissible_full_size"], "admissible_checked": checked,
            "per_F_class": per, "seconds": r["seconds"]}, near, keys


def kopt(near, Freps, keys):
    jobs = []
    for f in sorted(os.listdir(near)):
        if not f.startswith("near_s366"):
            continue
        fi = int(re.search(r"_F(\d+)_", f).group(1))
        jobs.append((os.path.join(near, f), Freps[keys[fi]], keys[fi]))
    d = os.path.join(TMP, "kopt")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)

    def one(j):
        p, F, k = j
        o = os.path.join(d, os.path.basename(p)[:-4])
        os.makedirs(o, exist_ok=True)
        v = verify(p)
        dis = disjoint_second_path(p, F)
        s = json.loads(run([BIN + "/s2_2_conf", "kswap", p, "--k", 3, "--forbid", F, "--out", o]).strip().split("\n")[-1])
        imp = sorted(os.listdir(o))
        return {"set": os.path.basename(p), "F_class": k, "size": v["size"], "independent": v["independent"],
                "disjoint_from_F_second_path": dis, "windows": s["windows"][:2],
                "improving_windows": s["windows_admitting_more_than_k"], "improved_files": imp}
    with ThreadPoolExecutor(max_workers=JOBS) as ex:
        rows = list(ex.map(one, jobs))
    return {"sets": len(rows), "all_verified_366_outside_F": all(r["size"] == 366 and r["independent"]
                                                                and r["disjoint_from_F_second_path"] for r in rows),
            "sets_with_an_improving_window": sum(1 for r in rows if r["improving_windows"]),
            "by_F_class": {str(k): sum(1 for r in rows if r["F_class"] == k) for k in sorted({r["F_class"] for r in rows})},
            "rows": rows}, jobs


def looseness(jobs):
    """The Stage 2.1 statistic on one 366-set per F class, and on the t = 8 control."""
    from s2_1_room import opt_tests
    out = []
    seen = set()
    for p, F, k in jobs:
        if k in seen:
            continue
        seen.add(k)
        _, _, S = read_set(p)
        Fv = {tuple((v // 7 ** i) % 7 for i in range(D)) for v in read_F(F)}
        t = opt_tests(S, Fv)
        out.append({"F_class": k, "set": os.path.basename(p), "blockers_histogram_up_to_two": t["blockers_histogram_up_to_two"],
                    "one_opt_improves": t["one_opt_improves"], "two_opt_improves": t["two_opt_improves"]})
    return out


def dump():
    """The report names working files relative to $SHANNON_TMP, so it does not depend on where
    the run was made."""
    txt = json.dumps(OUT, indent=2).replace(os.path.abspath(TMP), "$SHANNON_TMP")
    open(os.path.join(ROOT, "results", "json", "s2_2.json"), "w").write(txt)


def main():
    os.makedirs(TMP, exist_ok=True)
    t_wall = time.time()
    ru0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    ctrl = controls()
    F_pub = sweep_calibration(ctrl)
    kopt_controls(ctrl, F_pub)
    ctrl["passed"] = bool(ctrl["automorphism_generator"]["passed"] and ctrl["lemma_passed"] and ctrl["iso_negative_control"]
                          and ctrl["t8_counts_match_stage2"] and ctrl["sweep_t8"]["histogram_reproduced"]
                          and ctrl["sweep_t8"]["best_repaired_size"] == 367 and ctrl["kopt_passed"])
    OUT["controls"] = ctrl
    print("controls passed:", ctrl["passed"], flush=True)
    if not ctrl["passed"]:
        dump()
        return 1
    OUT["population"] = population()
    print("population:", len(OUT["population"]), flush=True)
    pl, reps, classes, allf = plateau()
    OUT["plateau"] = pl
    print("plateau classes:", pl["aut_classes"], flush=True)
    OUT["kswaps"] = kswaps(reps, classes, allf)
    print("k-swaps done", flush=True)
    OUT["regions"], Freps = regions(classes)
    print("F classes:", OUT["regions"]["F_classes"], flush=True)
    OUT["sweep"], near, keys = sweep(Freps, reps)
    print("sweep best:", OUT["sweep"]["grand_best_repaired_size"], flush=True)
    OUT["kopt"], jobs = kopt(near, Freps, keys)
    OUT["looseness"] = looseness(jobs)
    # the second t* = 9 class, kept as a set: it is new by the exact isomorphism test
    t9 = [c for c in classes if c["t_star"] == 9]
    known = set(OUT["plateau"]["known_codes_class"].values())
    newt9 = [c for c in t9 if c["class"] not in known]
    if newt9:
        dst = os.path.join(ROOT, "sets", "C7_d5_367_t9_second_class.txt")
        _, _, I = read_set(newt9[0]["representative"])
        write_set(dst, N, I, ["A 367-word independent set of C_7^5 with nine candidate private pairs,",
                              "not isomorphic under (D_7)^5 sd S_5 to the published auxiliary set (the other",
                              "t* = 9 class). Found on the 1-swap plateau by scripts/s2_2.py (Stage 2.2)."])
        v = verify(dst)
        OUT["new_t9_code"] = {"file": rel(dst), "sha256": sha256(dst), "independent": v["independent"], "size": v["size"],
                              "class": newt9[0]["class"]}
    ru1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (ru1.ru_utime - ru0.ru_utime) + (ru1.ru_stime - ru0.ru_stime)
    OUT["budget"] = {"ceiling_core_hours": 40, "core_seconds_this_run": round(cpu, 1),
                     "core_hours_this_run": round(cpu / 3600, 2), "wall_seconds_this_run": round(time.time() - t_wall, 1)}
    dump()
    print(json.dumps(OUT["budget"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

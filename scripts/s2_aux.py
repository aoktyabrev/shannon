"""S2.2 -- does a code with nine or ten candidate pairs carry a gadget?

A code with t* >= 9 is not yet a bound: Gao's definition also needs an auxiliary
independent set X with X cap N(P_H) cap N(P_V) = empty, and the bound grows with
|X| and with o = |X \\ (N(P_H) cup N(P_V))|. Exact thresholds, from the published
recursion at k = 40 against Tandon's record: at |X| = 367 a code with t = 9 needs
o >= 311 and one with t = 10 needs o >= 296.

This driver takes any code file, recomputes its candidates, enumerates every proper
2-colouring of their conflict graph (which transversal each private neighbour goes
to -- it changes both regions), and for each colouring runs scripts/s1_auxsearch at
fixed cardinality: stay out of the forbidden region, minimise the overlap with the
penalised one. Every admissible result is handed to scripts/verify, which knows
nothing about gadgets.

Usage: s2_aux.py <code file> [--seconds S] [--workers W] [--start FILE]
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, confusable, read_set, sha256, verify  # noqa: E402
from s1_pairs import candidate_pairs  # noqa: E402

N, D = 7, 5
TMP = os.environ.get("SHANNON_TMP", "/tmp/shannon-s2")
os.makedirs(TMP, exist_ok=True)


def encode(v):
    return sum(c * 7 ** i for i, c in enumerate(v))


def closed_nbhd(verts):
    out = set()
    for v in verts:
        for off in product((-1, 0, 1), repeat=D):
            out.add(tuple((v[i] + off[i]) % N for i in range(D)))
    return out


def proper_colourings(qs):
    """Every proper 2-colouring of the conflict graph, pair 0 fixed to kill the swap."""
    n = len(qs)
    conf = [[i != j and confusable(qs[i], qs[j], N) for j in range(n)] for i in range(n)]
    out = []
    for m in range(1 << n):
        if m & 1:
            continue
        if all(not (conf[i][j] and ((m >> i & 1) == (m >> j & 1)))
               for i in range(n) for j in range(i + 1, n)):
            out.append(m)
    return out


def main():
    code = sys.argv[1]
    seconds = float(next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--seconds"), 900))
    workers = int(next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--workers"), 4))
    start = next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--start"),
                 os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt"))

    n, d, I = read_set(code)
    pairs = candidate_pairs(I)
    rs = [r for r, _ in pairs]
    qs = [q for _, q in pairs]
    masks = proper_colourings(qs)
    out = {"code": os.path.relpath(os.path.abspath(code), ROOT), "code_sha256": sha256(code),
           "code_size": len(I), "candidates": len(pairs),
           "proper_2_colourings_up_to_swap": len(masks),
           "start_set": os.path.relpath(os.path.abspath(start), ROOT),
           "seconds_per_colouring": seconds,
           "o_needed_to_beat_the_record": {"9": 311, "10": 296}.get(str(len(pairs))),
           }

    regions = {}
    for m in masks:
        PH = [qs[i] if (m >> i & 1) else rs[i] for i in range(len(qs))]
        PV = [rs[i] if (m >> i & 1) else qs[i] for i in range(len(qs))]
        NH, NV = closed_nbhd(PH), closed_nbhd(PV)
        B, U = NH & NV, NH | NV
        bp = os.path.join(TMP, "B_%s_%d.txt" % (os.path.basename(code)[:12], m))
        up = os.path.join(TMP, "U_%s_%d.txt" % (os.path.basename(code)[:12], m))
        open(bp, "w").write("\n".join(str(encode(v)) for v in sorted(B)))
        open(up, "w").write("\n".join(str(encode(v)) for v in sorted(U)))
        regions[m] = (bp, up, len(B), len(U))

    exe = os.path.join(ROOT, "scripts", "s1_auxsearch")

    def job(m):
        bp, up, nb, nu = regions[m]
        o = os.path.join(TMP, "X_%s_%d.txt" % (os.path.basename(code)[:12], m))
        r = json.loads(subprocess.run(
            [exe, "--forbid", bp, "--penal", up, "--start", start,
             "--seconds", str(seconds), "--seed", "41", "--out", o, "--json"],
            capture_output=True, text=True).stdout)
        r["colour_mask"] = m
        r["forbidden_region"] = nb
        r["penalised_region"] = nu
        if r.get("conflicts") == 0 and os.path.exists(o):
            r["verified"] = verify(o, ["--both"])
            r["file"] = o
        return r

    with ThreadPoolExecutor(max_workers=workers) as ex:
        rows = list(ex.map(job, masks))
    rows.sort(key=lambda r: (-r.get("o", -1), r.get("conflicts", 99)))
    admissible = [r for r in rows if r.get("conflicts") == 0]
    best = max(admissible, key=lambda r: r["o"]) if admissible else None
    out["rows"] = rows
    out["admissible"] = len(admissible)
    out["best_o"] = best["o"] if best else None
    out["best_colouring"] = best["colour_mask"] if best else None
    need = out["o_needed_to_beat_the_record"]
    out["beats_the_record"] = bool(best and need and best["o"] >= need)
    with open(os.path.join(ROOT, "results", "json",
                           "s2_aux_%s.json" % os.path.basename(code).replace(".txt", "")), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("code", "code_size", "candidates", "proper_2_colourings_up_to_swap",
                       "o_needed_to_beat_the_record", "admissible", "best_o",
                       "beats_the_record")}, indent=2))
    print("top rows (o, conflicts, colouring):",
          [(r.get("o"), r.get("conflicts"), r["colour_mask"]) for r in rows[:6]])
    return 0


if __name__ == "__main__":
    sys.exit(main())

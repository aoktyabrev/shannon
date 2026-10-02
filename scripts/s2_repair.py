"""S2.2, repair step: make an auxiliary set for a code that the sweep nearly fits.

The group sweep (scripts/s1_aux) reports, for every image of every known 367-word
code and every proper 2-colouring, how many of its words land in the forbidden
region N(P_H) cap N(P_V). For the ten-candidate code the minimum is two, never
zero, so an admissible auxiliary set has to be repaired: delete the offending words
and add back as many legal replacements as possible -- legal meaning outside the
forbidden region and not confusable with what remains.

This generalises scripts/s1_repair.py, which is wired to the published code and its
eight pairs, to any code file: the pairs and the colourings are recomputed from the
code itself. The repaired set is written out and handed to scripts/verify, and the
resulting profile is pushed through the published recursion in exact integer
arithmetic to see whether it clears the record.

Usage: s2_repair.py <code file> <near-miss dump from s1_aux> [--max-rows R]
"""
import json
import os
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gadget import bound_digits, recursion  # noqa: E402
from s1_pairs import candidate_pairs  # noqa: E402
from s1_repair import best_repair, closed_nbhd, decode, encode, image  # noqa: E402
from setio import ROOT, confusable, read_set, sha256, verify, write_set  # noqa: E402

N = 7
RECORD = "3.2588326203532663091215390518104754376053875943219"


def proper_colourings(qs):
    n = len(qs)
    conf = [[i != j and confusable(qs[i], qs[j], N) for j in range(n)] for i in range(n)]
    return [m for m in range(1 << n) if not (m & 1) and
            all(not (conf[i][j] and ((m >> i & 1) == (m >> j & 1)))
                for i in range(n) for j in range(i + 1, n))]


def main():
    code_file, dump = sys.argv[1], sys.argv[2]
    max_rows = int(next((sys.argv[i + 1] for i, a in enumerate(sys.argv)
                         if a == "--max-rows"), 400))
    n, d, I = read_set(code_file)
    pairs = candidate_pairs(I)
    rs = [r for r, _ in pairs]
    qs = [q for _, q in pairs]
    t = len(pairs)
    masks = proper_colourings(qs)

    regions = {}
    for m in masks:
        PH = [qs[i] if (m >> i & 1) else rs[i] for i in range(t)]
        PV = [rs[i] if (m >> i & 1) else qs[i] for i in range(t)]
        NH, NV = closed_nbhd(PH), closed_nbhd(PV)
        regions[m] = (NH & NV, NH | NV)

    rows, best = [], None
    seen = 0
    for line in open(dump):
        if line.startswith("#"):
            continue
        f = line.split()
        if len(f) < 7:
            continue
        src_i, cmask, perm, sign_mask, shift, bad_n, u = (
            int(f[0]), int(f[1]), tuple(int(x) for x in f[2].split(",")),
            int(f[3]), int(f[4]), int(f[5]), int(f[6]))
        if cmask not in regions:
            continue
        seen += 1
        if seen > max_rows:
            break
        src_files = sorted(os.listdir(os.path.join(ROOT, "sets", "pipeline_codes")))
        # the dump's source index is the order the sweep was given its --source list;
        # it is recorded in results/json/s2_sweep_sources.json by the caller
        srcs = json.load(open(os.path.join(ROOT, "results", "json",
                                           "s2_sweep_sources.json")))["sources"]
        _, _, S = read_set(os.path.join(ROOT, srcs[src_i]))
        X = image(S, perm, sign_mask, shift)
        B, U = regions[cmask]
        badw = [w for w in X if w in B]
        if len(badw) != bad_n:
            rows.append({"row": seen, "mismatch": True, "bad_in_dump": bad_n,
                         "bad_recomputed": len(badw)})
            continue
        Xp, cand, add = best_repair(X, set(badw), B, U)
        Xnew = sorted(set(Xp) | set(add))
        s_new = len(Xnew)
        o_new = sum(1 for w in Xnew if w not in U)
        M = recursion(367, t, s_new, o_new, 40)[0]
        b = bound_digits(M[40], 200, 34)
        row = {"row": seen, "source": srcs[src_i], "colour_mask": cmask,
               "bad": len(badw), "deleted": len(badw), "added": len(add),
               "replacements_available": len(cand),
               "s": s_new, "o": o_new, "profile": [367, t, s_new, o_new],
               "bound": b, "beats_record": b > RECORD[:len(b)],
               "alpha_368_found": len(add) > len(badw)}
        rows.append(row)
        if best is None or (row["s"], row["o"]) > (best["s"], best["o"]):
            best = dict(row, words=Xnew)
    out = {"code": os.path.relpath(os.path.abspath(code_file), ROOT),
           "code_sha256": sha256(code_file), "candidates": t,
           "colourings": len(masks), "rows_examined": len([r for r in rows if "s" in r]),
           "best": {k: v for k, v in (best or {}).items() if k != "words"},
           "record": RECORD}
    if best:
        p = os.path.join(ROOT, "sets", "C7_d5_%d_aux_for_t%d.txt" % (best["s"], t))
        write_set(p, N, sorted(best["words"]), header_lines=[
            "Auxiliary set for the %d-candidate 367-word code" % t,
            "produced by scripts/s2_repair.py from a near miss of the group sweep.",
        ])
        out["best_file"] = os.path.relpath(p, ROOT)
        out["best_sha256"] = sha256(p)
        out["best_verified"] = verify(p, ["--both"])
        out["best_beats_record"] = best["beats_record"]
    with open(os.path.join(ROOT, "results", "json", "s2_repair_t%d.json" % t), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in out if k not in ("rows",)}, indent=2)[:1200])
    return 0


if __name__ == "__main__":
    sys.exit(main())

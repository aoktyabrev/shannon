"""S2.2 -- the candidate count of every code we hold, in one table.

The statistic Stage 2 is after does not exist in the literature: no paper reports how
many vertices outside a code have exactly one neighbour in it. This script computes it
for every d = 5 set in sets/ (and for any file given on the command line), together
with the conflict graph of those candidates and t* -- the largest subfamily with
distinct centres whose conflict graph is bipartite, which by the lemma of the note is
the maximum number of private pairs a gadget over that code can have.

Each number is exact: the candidates are found by one pass over all of Z_7^5, and t*
by exhaustive branch and bound. Independence of each file is re-checked by
scripts/verify, not assumed, because a count on a non-independent set means nothing.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, confusable, read_set, sha256, verify  # noqa: E402
from s1_pairs import candidate_pairs, max_pairs  # noqa: E402

N, D = 7, 5


def describe(path):
    n, d, I = read_set(path)
    if (n, d) != (N, D):
        return None
    v = verify(path)
    pairs = candidate_pairs(I)
    best, pairs, conflict, cen = max_pairs(pairs)
    qs = [q for _, q in pairs]
    edges = [[i, j] for i in range(len(qs)) for j in range(i + 1, len(qs))
             if confusable(qs[i], qs[j], N)]
    return {
        "file": os.path.relpath(path, ROOT),
        "sha256": sha256(path)[:16],
        "size": len(I),
        "independent": v["independent"],
        "maximal": v.get("maximal"),
        "candidates": len(pairs),
        "distinct_centres": len({c for c in cen}),
        "conflict_edges": len(edges),
        "t_star": best["size"],
        "exhaustive": best["exhausted"],
    }


def main():
    paths = sys.argv[1:]
    if not paths:
        base = os.path.join(ROOT, "sets")
        paths = [os.path.join(base, f) for f in sorted(os.listdir(base)) if f.endswith(".txt")]
        pc = os.path.join(base, "pipeline_codes")
        if os.path.isdir(pc):
            paths += [os.path.join(pc, f) for f in sorted(os.listdir(pc)) if f.endswith(".txt")]
    rows = [r for r in (describe(p) for p in paths) if r]
    rows.sort(key=lambda r: (r["size"], r["candidates"]))
    hist = {}
    for r in rows:
        hist.setdefault(str(r["candidates"]), 0)
        hist[str(r["candidates"])] += 1
    by_size = {}
    for r in rows:
        by_size.setdefault(str(r["size"]), []).append(r["candidates"])
    out = {
        "codes": rows,
        "count_histogram": {k: hist[k] for k in sorted(hist, key=int)},
        "counts_by_size": {k: sorted(v) for k, v in sorted(by_size.items(), key=lambda kv: int(kv[0]))},
        "best_t_star": max(r["t_star"] for r in rows) if rows else None,
        "target_t_star_at_367": 9,
        "target_met": any(r["size"] == 367 and r["t_star"] >= 9 for r in rows),
        "all_independent": all(r["independent"] for r in rows),
    }
    with open(os.path.join(ROOT, "results", "json", "s2_counts.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"{'file':44} {'size':>5} {'cand':>5} {'edges':>6} {'t*':>3} {'max?':>5}")
    for r in rows:
        print(f"{r['file'][:44]:44} {r['size']:>5} {r['candidates']:>5} "
              f"{r['conflict_edges']:>6} {r['t_star']:>3} {str(r['maximal']):>5}")
    print()
    print("counts by size:", out["counts_by_size"])
    print("target (367 with t* >= 9) met:", out["target_met"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

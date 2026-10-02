"""S2-S: the frontier nobody has drawn -- how many private pairs a code can have,
and what that costs the auxiliary set.

Stage 1 asked one question of one code. Stage 2's secondary goal is the statistic
behind it: for every code we hold, the candidate count t*, and then the price of
those candidates -- because the transversals of t pairs occupy 2t endpoints, and the
forbidden region N(P_H) cap N(P_V) that an auxiliary set must avoid grows with them.
If t and o trade against each other, buying a ninth pair need not buy a better bound,
and that is exactly what the search is finding.

For each code and each proper 2-colouring of its candidates this records the sizes of
the forbidden and penalised regions, which bound o from above before any search is
run: o <= |X| - |X cap U|, and no auxiliary set can contain a word of the forbidden
region at all.
"""
import json
import os
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gadget import bound_digits, recursion  # noqa: E402
from s1_pairs import candidate_pairs, max_pairs  # noqa: E402
from setio import ROOT, confusable, read_set  # noqa: E402

N, D = 7, 5
RECORD = "3.2588326203532663091215390518104754376053875943219"


def closed_nbhd(S):
    out = set()
    for v in S:
        for off in product((-1, 0, 1), repeat=D):
            out.add(tuple((v[i] + off[i]) % N for i in range(D)))
    return out


def proper_colourings(qs):
    n = len(qs)
    conf = [[i != j and confusable(qs[i], qs[j], N) for j in range(n)] for i in range(n)]
    return [m for m in range(1 << n) if not (m & 1) and
            all(not (conf[i][j] and ((m >> i & 1) == (m >> j & 1)))
                for i in range(n) for j in range(i + 1, n))]


def o_needed(t, s=367, a=367):
    """Smallest o at which the published recursion clears the record."""
    lo, hi = 0, s
    while lo < hi:
        mid = (lo + hi) // 2
        M = recursion(a, t, s, mid, 40)[0]
        if bound_digits(M[40], 200, 34) > RECORD[:34 + 2]:
            hi = mid
        else:
            lo = mid + 1
    return lo


def main():
    files = sys.argv[1:] or [
        "sets/C7_d5_343_linear.txt",
        "sets/C7_d5_350_mathew_ostergard.txt",
        "sets/C7_d5_367_reproduced.txt",
        "sets/C7_d5_367_polak_schrijver.txt",
        "sets/C7_d5_367_auxiliary_X.txt",
        "sets/C7_d5_367_auxiliary_X_best.txt",
    ] + ["sets/pipeline_codes/C7_d5_367_pipeline_0%d.txt" % i for i in range(8)]
    rows = []
    for rel in files:
        path = os.path.join(ROOT, rel)
        n, d, I = read_set(path)
        pairs = candidate_pairs(I)
        rs = [r for r, _ in pairs]
        qs = [q for _, q in pairs]
        best, _, _, _ = max_pairs(list(pairs))
        t = best["size"]
        row = {"file": rel, "size": len(I), "candidates": len(pairs), "t_star": t}
        if t:
            masks = proper_colourings(qs)
            sizes = []
            for m in masks:
                PH = [qs[i] if (m >> i & 1) else rs[i] for i in range(len(qs))]
                PV = [rs[i] if (m >> i & 1) else qs[i] for i in range(len(qs))]
                NH, NV = closed_nbhd(PH), closed_nbhd(PV)
                sizes.append((len(NH & NV), len(NH | NV)))
            row["colourings"] = len(masks)
            row["forbidden_region"] = {"min": min(s[0] for s in sizes),
                                       "max": max(s[0] for s in sizes)}
            row["penalised_region"] = {"min": min(s[1] for s in sizes),
                                       "max": max(s[1] for s in sizes)}
            row["endpoints"] = 2 * t
            row["o_needed_at_s_367"] = o_needed(t)
        rows.append(row)
    rows.sort(key=lambda r: (r["size"], r["t_star"]))
    out = {
        "rows": rows,
        "record": RECORD,
        "reading": ("The forbidden region is what an auxiliary set may not touch, and it grows "
                    "with the number of pairs: more candidates mean more endpoints and a larger "
                    "N(P_H) cap N(P_V). So t and o trade against each other, and a ninth pair is "
                    "not automatically worth its price."),
    }
    with open(os.path.join(ROOT, "results", "json", "s2_frontier.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"{'file':42} {'size':>5} {'t*':>3} {'ends':>5} {'forbid':>12} {'penal':>12} {'o needed':>9}")
    for r in rows:
        fr = f"{r['forbidden_region']['min']}-{r['forbidden_region']['max']}" if r["t_star"] else "-"
        pe = f"{r['penalised_region']['min']}-{r['penalised_region']['max']}" if r["t_star"] else "-"
        print(f"{r['file'][-42:]:42} {r['size']:>5} {r['t_star']:>3} "
              f"{r.get('endpoints', 0):>5} {fr:>12} {pe:>12} {r.get('o_needed_at_s_367', '-'):>9}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

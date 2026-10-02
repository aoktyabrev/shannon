"""How large can an auxiliary set for a nine- or ten-candidate code be at all?

The bound needs |X| close to 367 and o above a threshold that depends on t (296 at
t = 10, 311 at t = 9, both at |X| = 367). Every search so far failed at |X| = 367,
so the question becomes: what is the largest cardinality at which an independent set
avoiding the forbidden region exists? This walks the cardinality down, running the
fixed-cardinality engine at each step, and prints the cardinality against the o it
achieves and the o it would need. Where the two curves cross -- if they cross -- is
whether the code can pay for its extra pairs.

Usage: s2_ladder.py <code file> [--seconds S] [--sizes 367,366,...]
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gadget import bound_digits, recursion  # noqa: E402
from s1_pairs import candidate_pairs  # noqa: E402
from setio import ROOT, confusable, read_set, verify, write_set  # noqa: E402

N, D = 7, 5
RECORD = "3.2588326203532663091215390518104754376053875943219"
TMP = os.environ.get("SHANNON_TMP", "/tmp/shannon-s2")
os.makedirs(TMP, exist_ok=True)


def encode(v):
    return sum(c * 7 ** i for i, c in enumerate(v))


def closed_nbhd(S):
    out = set()
    for v in S:
        for off in product((-1, 0, 1), repeat=D):
            out.add(tuple((v[i] + off[i]) % N for i in range(D)))
    return out


def o_needed(t, s):
    lo, hi = 0, s
    while lo < hi:
        mid = (lo + hi) // 2
        M = recursion(367, t, s, mid, 40)[0]
        if bound_digits(M[40], 200, 34) > RECORD[:36]:
            hi = mid
        else:
            lo = mid + 1
    return lo


def main():
    code = sys.argv[1]
    seconds = float(next((sys.argv[i + 1] for i, a in enumerate(sys.argv)
                          if a == "--seconds"), 300))
    sizes = [int(x) for x in next((sys.argv[i + 1] for i, a in enumerate(sys.argv)
                                   if a == "--sizes"), "367,366,365,364,362,360").split(",")]
    n, d, I = read_set(code)
    pairs = candidate_pairs(I)
    rs = [r for r, _ in pairs]
    qs = [q for _, q in pairs]
    t = len(pairs)

    # the colouring with the smallest forbidden region gives the search its best chance
    best_mask, best_B, best_U = None, None, None
    full = (1 << t) - 1
    for m in range(1 << t):
        if m & 1:
            continue
        if any(confusable(qs[i], qs[j], N) and ((m >> i & 1) == (m >> j & 1))
               for i in range(t) for j in range(i + 1, t) if i != j):
            continue
        PH = [qs[i] if (m >> i & 1) else rs[i] for i in range(t)]
        PV = [rs[i] if (m >> i & 1) else qs[i] for i in range(t)]
        NH, NV = closed_nbhd(PH), closed_nbhd(PV)
        B, U = NH & NV, NH | NV
        if best_B is None or len(B) < len(best_B):
            best_mask, best_B, best_U = m, B, U
    bp = os.path.join(TMP, "ladder_B_%d.txt" % t)
    up = os.path.join(TMP, "ladder_U_%d.txt" % t)
    open(bp, "w").write("\n".join(str(encode(v)) for v in sorted(best_B)))
    open(up, "w").write("\n".join(str(encode(v)) for v in sorted(best_U)))

    base = os.path.join(ROOT, "sets", "C7_d5_367_polak_schrijver.txt")
    _, _, B367 = read_set(base)
    exe = os.path.join(ROOT, "scripts", "s1_auxsearch")

    def job(s):
        start = os.path.join(TMP, "start_%d.txt" % s)
        write_set(start, N, sorted(B367)[:s])
        out = os.path.join(TMP, "ladder_X_%d_%d.txt" % (t, s))
        r = json.loads(subprocess.run(
            [exe, "--forbid", bp, "--penal", up, "--start", start,
             "--seconds", str(seconds), "--seed", "53", "--out", out, "--json"],
            capture_output=True, text=True).stdout)
        r["s_requested"] = s
        r["o_needed"] = o_needed(t, s)
        r["admissible"] = r.get("conflicts") == 0
        if r["admissible"]:
            r["verified"] = verify(out, ["--both"])
            M = recursion(367, t, s, r["o"], 40)[0]
            r["bound"] = bound_digits(M[40], 200, 34)
            r["beats_record"] = r["bound"] > RECORD[:36]
        return r

    with ThreadPoolExecutor(max_workers=min(6, len(sizes))) as ex:
        rows = list(ex.map(job, sizes))
    out = {"code": os.path.relpath(os.path.abspath(code), ROOT), "candidates": t,
           "colouring_with_smallest_forbidden_region": best_mask,
           "forbidden_region": len(best_B), "penalised_region": len(best_U),
           "seconds_per_size": seconds, "rows": rows,
           "any_beats_record": any(r.get("beats_record") for r in rows)}
    with open(os.path.join(ROOT, "results", "json", "s2_ladder_t%d.json" % t), "w") as f:
        json.dump(out, f, indent=2)
    print(f"code with t = {t}: forbidden region {len(best_B)}, penalised {len(best_U)}")
    print(f"{'|X|':>5} {'conflicts':>10} {'o':>5} {'o needed':>9} {'admissible':>11} {'beats':>6}")
    for r in sorted(rows, key=lambda r: -r["s_requested"]):
        print(f"{r['s_requested']:>5} {r.get('conflicts', -1):>10} {r.get('o', -1):>5} "
              f"{r['o_needed']:>9} {str(r['admissible']):>11} {str(r.get('beats_record', False)):>6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

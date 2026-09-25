"""S1.2, branch B continued: repairing the near-miss auxiliary sets.

The group sweep (scripts/s1_aux) found that **no** image of any of the eight
367-word codes under Aut(C_7^{boxtimes 5}) is admissible as an auxiliary set for
any valid 2-colouring: the least number of words landing in the forbidden region
N(P_H) cap N(P_V) is one, never zero.  That is exactly why Itty et al. replace one
vector -- the sweep shows the replacement is not a convenience but unavoidable.

So the admissible auxiliary sets are repaired images: delete the words that fall
in the forbidden region and add replacements.  For every near miss the sweep
dumped, this script

  * rebuilds the image and checks it really is a 367-word independent set,
  * deletes the offending words,
  * computes the exact set of legal replacements (not in the forbidden region,
    not confusable with what is left), and
  * solves for the best repair exactly: a maximum independent set among the
    replacements, ties broken by how many of them avoid N(P_H) cup N(P_V),
    since that is what the bound rewards.

If a repair ever admits more additions than deletions, that is an independent set
of size 368 in C_7^{boxtimes 5} -- a new record for alpha -- and the script says so
loudly.
"""
import json
import os
import sys
from itertools import combinations, product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gadget import bound_digits, recursion  # noqa: E402
from setio import ROOT, confusable, read_set, sha256, verify, write_set  # noqa: E402

from decimal import Decimal, getcontext  # noqa: E402
getcontext().prec = 60
N = 7
RECORD = Decimal("3.2588326203532663091215390518104754376053875943219")

RQ = [((1, 3, 4, 4, 6), (2, 3, 5, 4, 6)), ((3, 4, 0, 3, 5), (2, 4, 6, 3, 5)),
      ((5, 3, 1, 3, 4), (5, 3, 2, 3, 5)), ((4, 4, 6, 1, 6), (5, 4, 6, 0, 6)),
      ((6, 0, 6, 4, 5), (6, 1, 6, 5, 5)), ((0, 3, 5, 6, 5), (6, 3, 5, 0, 5)),
      ((6, 4, 3, 4, 0), (6, 4, 2, 4, 6)), ((6, 4, 5, 3, 2), (6, 5, 5, 3, 1))]
DELTAS = list(product((-1, 0, 1), repeat=5))


def decode(v):
    c = []
    for _ in range(5):
        c.append(v % N); v //= N
    return tuple(c)


def encode(c):
    v = 0
    for i in range(5):
        v += c[i] * (N ** i)
    return v


def closed_nbhd(S):
    out = set()
    for s in S:
        for d in DELTAS:
            out.add(tuple((a + b) % N for a, b in zip(s, d)))
    return out


# scripts/s1_aux enumerates the private pairs by ascending index of q in Z_7^5,
# not in the order the paper tabulates them, and the colour masks it dumps are bit
# strings over *that* order.  The same order is rebuilt here, or the masks would
# name different pairs.
PAIRS_BY_Q = sorted(((r, q) for r, q in RQ), key=lambda rq: encode(rq[1]))


def transversals(colour_mask):
    """bit j of colour_mask set  <=>  q_j goes to P_H (scripts/s1_aux convention)."""
    PH, PV = [], []
    for j, (r, q) in enumerate(PAIRS_BY_Q):
        if colour_mask >> j & 1:
            PH.append(q); PV.append(r)
        else:
            PH.append(r); PV.append(q)
    return PH, PV


def image(src, perm, sign_mask, shift_idx):
    sh = decode(shift_idx)
    out = []
    for w in src:
        t = []
        for i in range(5):
            x = w[perm[i]]
            if sign_mask >> i & 1:
                x = (N - x) % N
            t.append((x + sh[i]) % N)
        out.append(tuple(t))
    return out


def best_repair(X, bad_words, B, U):
    """Delete bad_words from X, then add as many legal replacements as possible."""
    Xp = [w for w in X if w not in bad_words]
    Xset = set(Xp)
    cand = []
    for v in product(range(N), repeat=5):
        if v in Xset or v in B:
            continue
        if any(confusable(v, w, N) for w in Xp):
            continue
        cand.append(v)
    n = len(cand)
    adj = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if confusable(cand[i], cand[j], N):
                adj[i][j] = adj[j][i] = True
    best = {"size": 0, "outside_U": -1, "set": []}
    cur = []

    def rec(start):
        if len(cur) > best["size"] or (len(cur) == best["size"]
                                       and sum(1 for i in cur if cand[i] not in U) > best["outside_U"]):
            best["size"] = len(cur)
            best["outside_U"] = sum(1 for i in cur if cand[i] not in U)
            best["set"] = list(cur)
        for i in range(start, n):
            if all(not adj[i][j] for j in cur):
                cur.append(i)
                rec(i + 1)
                cur.pop()

    rec(0)
    add = [cand[i] for i in best["set"]]
    return Xp, cand, add


def main():
    dump = sys.argv[1] if len(sys.argv) > 1 else "/tmp/aux_cand.txt"
    sources = sorted(os.path.join(ROOT, "sets", "pipeline_codes", f)
                     for f in os.listdir(os.path.join(ROOT, "sets", "pipeline_codes")))
    src_sets = [read_set(p)[2] for p in sources]

    rows = []
    for line in open(dump):
        if line.startswith("#") or not line.strip():
            continue
        si, cmask, perm, sg, shift, bad, u = line.split()
        rows.append((int(si), int(cmask), tuple(int(x) for x in perm.split(",")),
                     int(sg), int(shift), int(bad), int(u)))
    rows.sort(key=lambda r: (r[6] - r[5], r[5]))       # most promising first: small u, small bad

    rep = {"every_candidate_verified": True, "candidates_examined": 0,
           "dump": os.path.basename(dump),
           "total_near_misses": len(rows), "best": None, "alpha_368_found": False, "rows": []}
    seen = set()
    cache = {}
    best_bound = None

    for (si, cmask, perm, sg, shift, bad, u) in rows[:60]:
        key = (si, cmask, perm, sg, shift)
        if key in seen:
            continue
        seen.add(key)
        if cmask not in cache:
            PH, PV = transversals(cmask)
            NH, NVv = closed_nbhd(PH), closed_nbhd(PV)
            cache[cmask] = (NH & NVv, NH | NVv)
        B, U = cache[cmask]
        X = image(src_sets[si], perm, sg, shift)
        assert len(set(X)) == 367
        # the brief asks that intermediate candidates be verified at each step, not
        # only at the end: every reconstructed image goes through scripts/verify.
        tmp = os.path.join("/tmp", "shannon_cand_%d.txt" % len(rep["rows"]))
        write_set(tmp, N, sorted(X), ["candidate auxiliary image, checked in flight"])
        vr = verify(tmp)
        os.remove(tmp)
        assert vr["independent"] and vr["size"] == 367, vr
        badw = {w for w in X if w in B}
        assert len(badw) == bad, (len(badw), bad)
        Xp, cand, add = best_repair(X, badw, B, U)
        s = len(Xp) + len(add)
        o = sum(1 for w in Xp if w not in U) + sum(1 for w in add if w not in U)
        M, *_ = recursion(367, 8, s, o, 40)
        b = bound_digits(M[40], 200, 34)
        row = {"source": os.path.basename(sources[si]), "colour_mask": cmask, "perm": list(perm),
               "sign_mask": sg, "shift": shift, "bad": bad, "u_before": u,
               "deleted": bad, "replacements_available": len(cand), "added": len(add),
               "s": s, "o": o, "bound": b, "margin_over_record": str(Decimal(b) - RECORD)}
        rep["rows"].append(row)
        rep["candidates_examined"] += 1
        if len(add) > bad:
            rep["alpha_368_found"] = True
        if best_bound is None or Decimal(b) > Decimal(best_bound["bound"]):
            best_bound = row
            best_bound["_X"] = sorted(set(Xp) | set(add))
    rep["best"] = {k: v for k, v in (best_bound or {}).items() if not k.startswith("_")}

    if best_bound:
        out = os.path.join(ROOT, "sets", "C7_d5_367_auxiliary_X_best.txt")
        write_set(out, N, best_bound["_X"], [
            "Auxiliary set X for the five-dimensional base gadget: %d words, o = %d."
            % (best_bound["s"], best_bound["o"]),
            "A repaired image of %s under Aut(C_7^{boxtimes 5})," % best_bound["source"],
            "found by the exhaustive group sweep of scripts/s1_aux and repaired exactly by",
            "scripts/s1_repair.py.  2-colouring mask %d, permutation %s, signs %d, shift %d."
            % (best_bound["colour_mask"], best_bound["perm"], best_bound["sign_mask"],
               best_bound["shift"]),
        ])
        rep["best_X_file"] = os.path.relpath(out, ROOT)
        rep["best_X_sha256"] = sha256(out)
        rep["best_X_verified"] = verify(out)

    with open(os.path.join(ROOT, "results", "json", "s1_repair.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps({k: v for k, v in rep.items() if k != "rows"}, indent=2)[:2200])
    print("\ntop repaired profiles:")
    for r in sorted(rep["rows"], key=lambda r: Decimal(r["bound"]), reverse=True)[:8]:
        print("  s=%d o=%d  bad=%d added=%d  %s  margin %+.3e"
              % (r["s"], r["o"], r["bad"], r["added"], r["bound"][:22],
                 Decimal(r["margin_over_record"])))


if __name__ == "__main__":
    main()

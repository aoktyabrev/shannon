"""Driver for S1.2 branch B: the auxiliary-set search, over every valid
2-colouring of the eight private pairs.

For each colouring it writes the forbidden region B = N(P_H) cap N(P_V) and the
penalised region U = N(P_H) cup N(P_V), then runs scripts/s1_auxsearch, which
holds |X| = 367, keeps X out of B, and minimises |X cap U|.

The control that matters: started from the published auxiliary set under the
colouring the paper uses, the search must report o = 321 exactly, Gao's value.
A search that could not reproduce the known profile would not be evidence about
a better one.
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s1_repair import PAIRS_BY_Q, RQ, closed_nbhd, encode, transversals  # noqa: E402
from setio import ROOT, verify  # noqa: E402

TMP = os.environ.get("SHANNON_TMP", "/tmp/shannon-aux")
SECONDS = float(os.environ.get("S1_AUX_SECONDS", "1500"))
os.makedirs(TMP, exist_ok=True)


def valid_colourings():
    """Every proper 2-colouring of the q-conflict graph, fixing pair 0 to kill the
    global H<->V swap (which leaves s and o unchanged)."""
    from setio import confusable
    qs = [q for _, q in PAIRS_BY_Q]
    n = len(qs)
    conf = [[confusable(qs[i], qs[j], 7) and i != j for j in range(n)] for i in range(n)]
    out = []
    for m in range(1 << n):
        if m & 1:
            continue
        if all(not (conf[i][j] and ((m >> i & 1) == (m >> j & 1)))
               for i in range(n) for j in range(i + 1, n)):
            out.append(m)
    return out


def main():
    published = 0
    J0 = {0, 5, 6}
    for j, (r, q) in enumerate(PAIRS_BY_Q):
        orig = [k for k in range(8) if RQ[k][1] == q][0]
        if orig not in J0:
            published |= 1 << j
    # valid_colourings() fixes pair 0 to one transversal to kill the global H<->V
    # swap, which leaves s and o unchanged; normalise the published colouring the
    # same way (61 and 194 are the same colouring seen from the two sides).
    published_raw = published
    if published & 1:
        published ^= (1 << len(PAIRS_BY_Q)) - 1
    masks = valid_colourings()
    assert published in masks, (published_raw, published, masks)

    regions = {}
    for m in masks:
        PH, PV = transversals(m)
        NH, NVv = closed_nbhd(PH), closed_nbhd(PV)
        B, U = NH & NVv, NH | NVv
        bp, up = os.path.join(TMP, "B_%d.txt" % m), os.path.join(TMP, "U_%d.txt" % m)
        open(bp, "w").write("\n".join(str(encode(v)) for v in B))
        open(up, "w").write("\n".join(str(encode(v)) for v in U))
        regions[m] = (bp, up, len(B), len(U))

    exe = os.path.join(ROOT, "scripts", "s1_auxsearch")
    start_best = os.path.join(ROOT, "sets", "C7_d5_367_auxiliary_X_best.txt")
    published_X = os.path.join(ROOT, "sets", "C7_d5_367_auxiliary_X.txt")

    def run(args):
        out = subprocess.run(args, capture_output=True, text=True).stdout
        return json.loads(out)

    # control: the published X under the published colouring must give o = 321
    bp, up, _, _ = regions[published]
    control = run([exe, "--forbid", bp, "--penal", up, "--start", published_X,
                   "--seconds", "3", "--seed", "1", "--json"])

    def job(m):
        bp, up, nb, nu = regions[m]
        o = os.path.join(TMP, "X_%d.txt" % m)
        r = run([exe, "--forbid", bp, "--penal", up, "--start", start_best,
                 "--seconds", str(SECONDS), "--seed", "31", "--out", o, "--json"])
        r["colour_mask"] = m
        r["is_published_colouring"] = (m == published)
        if r["conflicts"] == 0 and os.path.exists(o):
            r["verified"] = verify(o, ["--both"])
        return r

    with ThreadPoolExecutor(max_workers=min(8, len(masks))) as ex:
        rows = list(ex.map(job, masks))

    admissible = [r for r in rows if r["conflicts"] == 0]
    best = max(admissible, key=lambda r: r["o"]) if admissible else None
    rep = {
        "seconds_per_colouring": SECONDS,
        "colourings": len(masks),
        "published_colouring_mask": published,
        "published_colouring_mask_as_written": published_raw,
        "control_published_X": {"o": control["o"], "u": control["u"],
                                "conflicts": control["conflicts"],
                                "reproduces_gao_321": control["o"] == 321 and control["conflicts"] == 0},
        "rows": rows,
        "best_admissible_o": best["o"] if best else None,
        "bpz_o": 322,
        "beats_bpz": bool(best and best["o"] > 322),
    }
    if best and os.path.exists(os.path.join(TMP, "X_%d.txt" % best["colour_mask"])):
        import shutil
        dst = os.path.join(ROOT, "sets", "C7_d5_367_auxiliary_X_o%d.txt" % best["o"])
        shutil.copy(os.path.join(TMP, "X_%d.txt" % best["colour_mask"]), dst)
        rep["best_file"] = os.path.relpath(dst, ROOT)
        rep["best_verified"] = verify(dst, ["--both"])
    with open(os.path.join(ROOT, "results", "json", "s1_auxsearch.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps({k: v for k, v in rep.items() if k != "rows"}, indent=2))
    for r in sorted(rows, key=lambda r: (-r["o"], r["conflicts"])):
        print("  mask=%-4d conflicts=%d u=%-3d o=%-4d %s" %
              (r["colour_mask"], r["conflicts"], r["u"], r["o"],
               "<- published colouring" if r["is_published_colouring"] else ""))


if __name__ == "__main__":
    main()

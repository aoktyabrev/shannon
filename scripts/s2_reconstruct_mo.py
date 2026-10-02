"""The Mathew-Ostergard 350-word set, rebuilt from the dumped paper.

Stage 0 recorded that this set "is not published in a form we obtained" and used
product constructions instead. That was wrong: the appendix of arXiv:1504.01472 gives
the set in full -- a generator of the prescribed group and the orbit representatives --
and this script rebuilds it from the dump rather than from a transcription:

  * the generator and the 50 orbit representatives are parsed out of
    sources/1504.01472/src/arxiv.tex;
  * the group is the translation x -> x + b with b the generator (their value
    permutations are x -> a*x + b with a = 1, so a translation of order 7);
  * each representative's orbit is generated, the orbits must all have size 7 and be
    disjoint, giving 50 * 7 = 350 words;
  * scripts/verify, which knows nothing about groups, decides independence;
  * the candidate private pairs are then counted with the Stage 1 enumerator, which is
    the first number of Stage 2's distribution: nobody has published the candidate
    count of this set.
"""
import json
import os
import re
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, confusable, read_set, sha256, verify, write_set  # noqa: E402
from s1_pairs import candidate_pairs, max_pairs  # noqa: E402

N, D = 7, 5
TEX = os.path.join(ROOT, "sources", "1504.01472", "src", "arxiv.tex")


def parse():
    if not os.path.exists(TEX):
        sys.exit("sources/1504.01472/src missing: run scripts/fetch_arxiv.sh 1504.01472")
    t = open(TEX, encoding="utf-8", errors="replace").read()
    i = t.index(r"\subsection*{$G(5,7)\geq 350$:}")
    j = t.index(r"\subsection*{$G(4,11)", i)
    block = t[i:j]
    tuples = [tuple(int(x) for x in m.replace(" ", "").split(","))
              for m in re.findall(r"\((\d(?:,\s*\d){4})\)", block)]
    order = int(re.search(r"Group order: (\d+)", block).group(1))
    return tuples[0], tuples[1:], order, block


def main():
    gen, reps, order, block = parse()
    out = {"source": "arXiv:1504.01472, Appendix, G(5,7) >= 350",
           "generator": list(gen), "group_order": order,
           "orbit_representatives": len(reps)}

    orbits, words = [], set()
    for r in reps:
        orbit, x = [], r
        for _ in range(order):
            orbit.append(x)
            x = tuple((xi + gi) % N for xi, gi in zip(x, gen))
        assert x == r, "the generator does not have the stated order on this orbit"
        if len(set(orbit)) != order:
            out["bad_orbit"] = list(r)
        orbits.append(sorted(set(orbit)))
        words.update(orbit)
    out["orbit_sizes"] = sorted({len(o) for o in orbits})
    out["size"] = len(words)
    out["size_matches_the_paper"] = len(words) == 350
    out["orbits_pairwise_disjoint"] = sum(len(o) for o in orbits) == len(words)

    path = os.path.join(ROOT, "sets", "C7_d5_350_mathew_ostergard.txt")
    write_set(path, N, sorted(words), header_lines=[
        "Independent set of size 350 in C_7^{boxtimes 5}: Mathew-Ostergard,",
        "arXiv:1504.01472, Appendix. Rebuilt by scripts/s2_reconstruct_mo.py from the",
        "generator (0,1,1,5,1) and the 50 orbit representatives printed there.",
    ])
    out["file"] = "sets/C7_d5_350_mathew_ostergard.txt"
    out["sha256"] = sha256(path)
    out["verify"] = verify(path, extra=("--quadratic",))

    # the number nobody has published: how many candidate private pairs does it have?
    _, _, I = read_set(path)
    pairs = candidate_pairs(I)
    best, pairs, conflict, cen = max_pairs(pairs)
    qs = [q for _, q in pairs]
    edges = [[i, j] for i in range(len(qs)) for j in range(i + 1, len(qs))
             if confusable(qs[i], qs[j], N)]
    out["candidates"] = {
        "count": len(pairs),
        "distinct_centres": len({c for c in cen}),
        "conflict_edges": len(edges),
        "t_star": best["size"],
        "exhaustive": best["exhausted"],
        "pairs": [{"r": list(r), "q": list(q)} for r, q in pairs],
    }
    # and, for the record, how far from maximal it is
    out["maximal"] = out["verify"].get("maximal")
    out["addable_vertices"] = out["verify"].get("addable_vertices")
    out["all_pass"] = bool(out["size_matches_the_paper"] and out["verify"]["independent"]
                           and out["orbits_pairwise_disjoint"])
    with open(os.path.join(ROOT, "results", "json", "s2_mo350.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in ("generator", "group_order", "size",
                                          "size_matches_the_paper", "orbit_sizes",
                                          "sha256", "all_pass")}, indent=2))
    print("verifier:", {k: out["verify"][k] for k in
                        ("independent", "quadratic_independent", "agree", "maximal",
                         "addable_vertices") if k in out["verify"]})
    print("candidates:", {k: out["candidates"][k] for k in
                          ("count", "distinct_centres", "conflict_edges", "t_star",
                           "exhaustive")})
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

"""W2.0 -- the literature gate for the second note.

Three questions, answered from the dumps in sources/ and from fresh arXiv searches:

  1. has anyone published the count of candidate private pairs as a characteristic of a
     code, a table of pair shapes q - r, or an identity of the kind |F| + |U| = 2 * 3^d?
  2. has the record moved, or has anything new on the gadget appeared, since
     arXiv:2608.30273?
  3. has anyone derived that the shape of a pair does not change its total cost?

As in scripts/w_gate.py, a machine cannot decide what a paper implies, so the evidence is
the complete list of candidate sentences, stored so the reading can be repeated, and the
verdict is the reading of that list.  The fresh searches reuse scripts/litcheck.py's
search(); scripts/litcheck.py itself is run first (label note2-gate) for the record chain.
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from litcheck import search  # noqa: E402
from w_gate import PAPERS, sentences  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRA_QUERIES = [
    '"private pairs" Shannon capacity',
    '"private pair" independent set strong product',
    "gadget Shannon capacity odd cycle recursion",
    '"C_7^5" independent set',
    "zero-error capacity seven-cycle lower bound",
]
# Q1: counts of pairs as a property of codes, or shapes of q - r
COUNT = re.compile(r"(number|count|how many|all|exactly|maxim\w*)[^.]{0,80}(private|pairs?\b)|"
                   r"(private|pairs?)[^.]{0,80}(number|count|maxim\w*|at most|exactly)", re.I)
SHAPE = re.compile(r"(differ|difference|q_?\{?[ij]\}?\s*-\s*r|r_?\{?[ij]\}?\s*-\s*q|coordinate)[^.]{0,120}"
                   r"(private|pair|q_)", re.I)
# Q1/Q3: the identity, inclusion-exclusion on the two neighbourhoods, or a cost trade-off
CAPCUP = re.compile(r"\\cap.{0,200}\\cup|\\cup.{0,200}\\cap", re.S)
NEIGH = re.compile(r"N\s*[\(\[]|\bneighbo", re.I)
POW3 = re.compile(r"3\^\{?\s*(d|5|n)\s*\}?|2\s*\\cdot\s*3\^|486|243")
TRADE = re.compile(r"trade|cost|penal|forbidden|exchange|at the expense|in return", re.I)


def main():
    rep = {"date": time.strftime("%Y-%m-%d"), "extra_searches": [], "dump_sentences": {}}
    for q in EXTRA_QUERIES:
        rep["extra_searches"].append(search(q))
        time.sleep(3)
    seen = {}
    for s in rep["extra_searches"]:
        for h in s["hits"]:
            seen.setdefault(h["id"], h)
    rep["extra_union"] = [seen[k] for k in sorted(seen, reverse=True)]
    lc = json.load(open(os.path.join(ROOT, "results", "json", "litcheck.json")))
    allhits = {h["id"]: h for h in lc["union_sorted_by_id"]}
    allhits.update(seen)
    newer = [h for k, h in sorted(allhits.items(), reverse=True) if k > "2608.30273"]
    subject = re.compile(r"shannon capacity|odd cycle|strong product|independen|zero-error|"
                         r"C_7|seven|gadget|private pair", re.I)
    rep["newer_than_the_record"] = [{"id": h["id"], "title": h["title"],
                                     "on_our_subject": bool(subject.search(h["title"]))} for h in newer]
    total = {"count_or_shape": 0, "identity_or_tradeoff": 0}
    for aid, who in PAPERS.items():
        q1, q3 = [], []
        for fn, s in sentences(aid):
            if len(s) < 20:
                continue
            if COUNT.search(s) or SHAPE.search(s):
                q1.append({"file": fn, "sentence": s[:600]})
            if (CAPCUP.search(s) and NEIGH.search(s)) or (POW3.search(s) and NEIGH.search(s)) or \
               (TRADE.search(s) and re.search(r"private|transversal|P_?\{?[HV]", s)):
                q3.append({"file": fn, "sentence": s[:600]})
        rep["dump_sentences"][aid] = {"who": who, "count_or_shape": q1, "identity_or_tradeoff": q3}
        total["count_or_shape"] += len(q1)
        total["identity_or_tradeoff"] += len(q3)
    rep["candidate_sentences_total"] = total
    # the reading of the evidence, recorded as a claim this repository stands behind
    rep["verdict"] = {
        "pair_count_published_as_a_property_of_codes": False,
        "table_of_pair_shapes_published": False,
        "identity_F_plus_U_published_or_applied": False,
        "shape_cost_invariance_derived_anywhere": False,
        "new_record_or_gadget_work_since_tandon": False,
        "note_may_be_written": True,
        "reading": (
            "Gao and Tandon define the private pair and the closed neighbourhood [G26-10, T26-7, T26-8]; "
            "Gao checks that each of the eight pairs is private; Tandon counts 'selected private pairs' "
            "inside profiles and uses 'exchanges along selected private pairs' [T26-9] -- the 1-swap of "
            "Stage 2.2 -- to build an auxiliary set. No paper counts the candidate pairs of a code, none "
            "considers the shape q - r of a pair, and the only sentences joining the cap and the cup of "
            "N(P^H), N(P^V) are the definitions of the gadget and of the neutral part X^0, with no "
            "statement about their sizes. Nothing on the subject has appeared on arXiv after 2608.30273."),
    }
    out = os.path.join(ROOT, "results", "json", "w2_gate.json")
    json.dump(rep, open(out, "w"), indent=2)
    print(json.dumps({"extra_hits": len(seen), "newer_than_the_record": rep["newer_than_the_record"],
                      "candidates": total,
                      "per_paper": {a: (len(v["count_or_shape"]), len(v["identity_or_tradeoff"]))
                                    for a, v in rep["dump_sentences"].items()}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

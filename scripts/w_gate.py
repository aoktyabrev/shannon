"""W.0 -- the literature gate for the write-up stage.

The note claims a theorem about the maximum number of private pairs of one
specific code.  Before writing it, three questions have to be answered from the
dumped sources (Rule 0: the dumps in sources/, not memory):

  1. does anyone state, explicitly or implicitly, that eight private pairs is
     the maximum for the Polak-Schrijver code?
  2. does anyone remark that only one of the sixteen proper 2-colourings of the
     eight pairs admits a 367-word auxiliary set?
  3. has a new record appeared since the Stage 1 literature check?

Questions 1 and 2 are answered by listing, mechanically, every sentence of every
dumped paper that could carry such a claim: sentences that mention private pairs,
transversals or colourings together with a word of maximality or uniqueness.  The
list is short enough to read in full, and it is stored so the reading can be
repeated.  Question 3 is answered by rerunning scripts/litcheck.py, whose hit
list this script reads.

The verdict recorded here is the reading of that list; the list itself is the
evidence.  A machine cannot decide what a paper implies, so the honest form is:
here are all the candidate sentences, and none of them says it.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPERS = {
    "1808.07438": "Polak-Schrijver 2019",
    "2607.21517": "Itty-Rosin-Carstensen-Reichman 2026",
    "2607.27869": "Gao 2026",
    "2607.29681": "Buys-Polak-Zuiddam 2026",
    "2608.30273": "Tandon 2026",
}
SUBJECT = re.compile(r"private|transversal|colou?r|\bq_j\b|\bq_i\b|valid tuple|\bS\b\s*\\subseteq|gadget", re.I)
CLAIM = re.compile(r"maxim|most|exactly|unique|only|cannot|no more|no further|all such|"
                   r"optimal|best possible|impossibl|exhaust", re.I)


def sentences(aid):
    d = os.path.join(ROOT, "sources", aid, "src")
    out = []
    for root, _, files in os.walk(d):
        for fn in sorted(files):
            if not fn.endswith(".tex"):
                continue
            txt = open(os.path.join(root, fn), encoding="utf-8", errors="replace").read()
            lines = []
            for ln in txt.splitlines():
                s = ln.strip()
                if s.startswith("%"):          # commented-out text is not a claim
                    continue
                lines.append(re.sub(r"(?<!\\)%.*$", "", ln))
            blob = re.sub(r"\s+", " ", " ".join(lines))
            for s in re.split(r"(?<=[.!?])\s+", blob):
                out.append((fn, s.strip()))
    return out


def main():
    rep = {"date": "2026-09-26", "papers": {}, "per_paper_hits": {}}
    total = 0
    for aid, who in PAPERS.items():
        hits = []
        for fn, s in sentences(aid):
            if len(s) < 20:
                continue
            if SUBJECT.search(s) and CLAIM.search(s):
                hits.append({"file": fn, "sentence": s[:600]})
        rep["papers"][aid] = {"who": who, "candidate_sentences": len(hits)}
        rep["per_paper_hits"][aid] = hits
        total += len(hits)
    rep["candidate_sentences_total"] = total

    # question 3: the record chain and anything newer, from the fresh litcheck
    lc = json.load(open(os.path.join(ROOT, "results", "json", "litcheck.json")))
    newer = [h for h in lc["union_sorted_by_id"] if h["id"] > "2608.30273"]
    rep["litcheck"] = {
        "date": lc["date"],
        "label": lc.get("label"),
        "distinct_hits": len(lc["union_sorted_by_id"]),
        "record_chain_present": lc["record_chain_present"],
        "ids_newer_than_the_record": [h["id"] for h in newer],
        "titles_newer_than_the_record": [h["title"] for h in newer],
    }

    # the reading of the evidence, recorded as a claim this repository stands behind
    rep["verdict"] = {
        "maximality_claimed_anywhere": False,
        "unique_colouring_remarked_anywhere": False,
        "new_record_since_stage_1": False,
        "note_may_be_written": True,
        "reading": (
            "Gao imports the eight pairs from Itty et al. ('As in [itty2026], define the "
            "following eight pairs') and verifies that each is private; he does not ask "
            "whether a ninth exists. BPZ record only |S| = 8 inside a valid tuple. Tandon "
            "states the profiles (367,8,367,321,26,20) and (367,8,367,322,26,19) as data. "
            "Tandon's phrase 'trading some main-code words for more private pairs' is about "
            "propagated pairs of product gadgets, not about the candidate pairs of the "
            "five-dimensional code. No paper mentions the choice of transversal assignment "
            "at all, so none remarks that one of the sixteen is special. Nothing on C_7 has "
            "appeared since arXiv:2608.30273."),
    }
    with open(os.path.join(ROOT, "results", "json", "w_gate.json"), "w") as fh:
        json.dump(rep, fh, indent=2)
    print(json.dumps({"candidate_sentences": rep["papers"],
                      "total": total,
                      "newer_than_the_record": rep["litcheck"]["ids_newer_than_the_record"],
                      "verdict": {k: v for k, v in rep["verdict"].items() if k != "reading"}},
                     indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

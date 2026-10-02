"""S2.0 -- the gate before Stage 2 does any arithmetic.

Three questions, answered from the dumps and from a fresh arXiv search rather than
from memory:

  1. has the record moved since arXiv:2608.30273, and is there anything new on
     alpha(C_7^5) or on private pairs?
  2. has anyone exhibited a 367-word independent set in C_7^5 outside the
     Polak-Schrijver construction, or enumerated other 367-codes?
  3. what is known about the upper bound on alpha(C_7^5) -- is 368 still open?

The answers decide whether Stage 2 has a target at all. Question 2 matters most: the
whole premise is that the private-pair count is a property of the individual code, so
a second published 367-code would be a free data point -- and if someone has already
collected such codes, Stage 2 would be re-treading their ground.
"""
import json
import os
import re
import subprocess
import sys
from decimal import Decimal, getcontext

getcontext().prec = 60
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = os.path.join(ROOT, "results", "json")


def dumps_text(aid):
    d = os.path.join(ROOT, "sources", aid, "src")
    if not os.path.isdir(d):
        sys.exit(f"sources/{aid}/src missing: run scripts/fetch_arxiv.sh {aid}")
    blob = []
    for root, _, files in os.walk(d):
        for fn in sorted(files):
            if fn.endswith(".tex"):
                blob.append(open(os.path.join(root, fn), encoding="utf-8",
                                 errors="replace").read())
    return re.sub(r"\s+", " ", " ".join(blob))


def main():
    out = {"date": "2026-10-02", "label": "stage2-start"}

    # --- 1. the record, from the fresh search -------------------------------------
    lc = json.load(open(os.path.join(J, "litcheck.json")))
    newer = [h for h in lc["union_sorted_by_id"] if h["id"] > "2608.30273"]
    on_c7 = [h for h in newer if re.search(r"shannon capacity|odd cycle|strong product|"
                                           r"independen|zero-error", h["title"], re.I)]
    out["record"] = {
        "search_date": lc["date"], "label": lc.get("label"),
        "distinct_hits": len(lc["union_sorted_by_id"]),
        "record_chain_present": lc["record_chain_present"],
        "ids_after_the_record": [h["id"] for h in newer],
        "of_those_on_our_subject": [h["title"] for h in on_c7],
        "record_unchanged": not on_c7,
        "current_record": "3.2588326203532663091215390518104754376053875943219... [T26-2]",
    }

    # --- 2. other 367-codes -------------------------------------------------------
    ps = dumps_text("1808.07438")
    tried = ("In steps (ii) and (iii), many possibilities for adding a constant word and for "
             "the division factor were tried, but no independent set of size~$368$ or larger "
             "was found.")
    three_opt = ("A local search was performed, showing that there exists no triple of words "
                 "from~$R$ such that if one removes these three words from~$R$, four words can "
                 "be added to obtain an independent set of size~$368$ in~$C_7^5$.")
    not_extendable = "the independent set~$R$ of size~$367$ did not seem to be easily extendable"
    bpz = dumps_text("2607.29681")
    funsearch = ("A size $367$ independent set in $C_7^{\\boxtimes 5}$ which improved the lower "
                 "bound was discovered by")
    out["other_367_codes"] = {
        "polak_schrijver_searched_the_same_family": re.sub(r"\s+", " ", tried) in ps,
        "their_3_opt_result_is_about_size_not_pairs": re.sub(r"\s+", " ", three_opt) in ps,
        "they_say_R_is_not_easily_extendable": re.sub(r"\s+", " ", not_extendable) in ps,
        "funsearch_recovered_the_bound": re.sub(r"\s+", " ", funsearch) in bpz,
        "funsearch_set_published": False,
        "funsearch_repository_checked":
            "https://api.github.com/repos/google-deepmind/funsearch/git/trees/main?recursive=1"
            " -- 37 files, none on Shannon capacity or independent sets in cycle powers",
        "verdict": ("No 367-word code outside the Polak-Schrijver construction is available in "
                    "the literature. PS themselves swept the parameters of their steps (ii)-(iii) "
                    "and a 3-opt neighbourhood of R, but only for SIZE -- no paper reports the "
                    "number of candidate private pairs of any code, so the statistic Stage 2 is "
                    "after does not exist yet. The eight codes of our own pipeline enumeration "
                    "(results/json/s1_codes.json) remain the only family whose counts are known."),
    }

    # --- 3. the upper bound -------------------------------------------------------
    th = Decimal(json.load(open(os.path.join(J, "theta.json")))["values"]["7"])
    bound = int(th ** 5)
    table = "$\\alpha(C_7^d)$ & 3 & $10^a$ & $33^d$ & $108^e$--$115^b$ & $367^f$--$401^c$"
    lovasz_key = "$^c$ $\\alpha(G^d) \\leq \\vartheta(G)^d$ by Lov\\'asz"
    out["upper_bound"] = {
        "theta_c7": str(th),
        "theta_c7_to_the_fifth": str(th ** 5),
        "floor": bound,
        "published_table_row_found_in_dump": re.sub(r"\s+", " ", table) in ps,
        "lovasz_key_found_in_dump": re.sub(r"\s+", " ", lovasz_key) in ps,
        "alpha_c7_5_known_interval": [367, bound],
        "368_still_open": 367 < bound,
        "note": ("The only published upper bound on alpha(C_7^5) is theta^5 = 401.94..., so every "
                 "value from 368 to 401 is open. Stage 2 does not need 368: at a = 367 it needs a "
                 "ninth candidate pair, which is a different question from a 368th word."),
    }

    out["what_this_means_for_stage_2"] = (
        "The target is intact and the ground is not taken: the record has not moved, no second "
        "367-code is published, and no paper reports candidate-pair counts at all. Stage 2's "
        "cheapest direction (perturbing I_0) is not subsumed by the 3-opt result of [PS19], "
        "because that search was for a 368th word and ours is for a ninth private pair.")
    out["all_pass"] = bool(out["record"]["record_unchanged"]
                           and out["other_367_codes"]["polak_schrijver_searched_the_same_family"]
                           and out["upper_bound"]["368_still_open"])
    with open(os.path.join(J, "s2_litcheck.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({
        "record_unchanged": out["record"]["record_unchanged"],
        "hits_after_the_record": len(out["record"]["ids_after_the_record"]),
        "of_those_on_our_subject": out["record"]["of_those_on_our_subject"],
        "other_367_codes_published": False,
        "funsearch_set_published": out["other_367_codes"]["funsearch_set_published"],
        "alpha_c7_5_interval": out["upper_bound"]["alpha_c7_5_known_interval"],
        "368_open": out["upper_bound"]["368_still_open"],
        "quotes_found_in_dumps": {k: v for k, v in out["other_367_codes"].items()
                                  if isinstance(v, bool)},
        "gate": out["all_pass"],
    }, indent=2))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

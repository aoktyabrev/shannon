"""Every number printed in the second note, reconciled by machine against results/json.

The same two directions as scripts/w_checknums.py: forward, each ledger entry is recomputed
from the stored results and must appear in the text; backward, every numeric token of the
text must be covered by the ledger, the structural allowlist or the years.  Small numbers
that carry a claim (seven candidates, sixteen regions, ...) are checked as claims: a value
from results/json and a pattern that must occur in the text.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w_checknums import STRUCTURAL, body  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = os.path.join(ROOT, "results", "json")
TEXT = [os.path.join(ROOT, "note2", "note2-abstract.tex"), os.path.join(ROOT, "note2", "note2-content.tex")]
WRAPPER = os.path.join(ROOT, "note2", "note2.tex")
L = {f: json.load(open(os.path.join(J, f))) for f in ("s2_1_room.json", "s2_2.json", "s2_3.json", "w2_core.json")}
s21, s22, s23, core = L["s2_1_room.json"], L["s2_2.json"], L["s2_3.json"], L["w2_core.json"]
orb = {o["k"]: o for o in s23["shapes"]["orbits"]}
real = {r["k"]: r["largest_size"] for r in s23["realisability"]}
pop = {r["file"]: r for r in s22["population"]}
pm = s23["price_model"]["rows"]
ratio = lambda a, t, k: next(r["ratio_needed"] for r in pm if (r["a"], r["t"], r["k"]) == (a, t, k))
per = s22["sweep"]["per_F_class"]
tof = {e["F_class"]: e["t"] for e in s22["regions"]["table"]}
best_t = lambda t: max(p["best_repaired_size"] for p in per if tof[p["F_class"]] == t)
c367 = [r for r in s22["population"] if r["size"] == 367]
fb = s22["regions"]["F_classes_by_t"]

# (printed, computed value as a string, what it is)
LEDGER = [
    ("367", str(pop["sets/C7_d5_367_polak_schrijver.txt"]["size"]), "size of the code"),
    ("486", str(s23["shapes"]["F_plus_U_per_pair"][0]), "|F| + |U| for one pair in C_7^5"),
    ("486", str(s22["plateau"]["one_swaps"]["visited"]), "codes of the Stage 2.2 plateau"),
    ("243", str(core["plateau"]["component_sizes"][0]), "codes per component, 3^5"),
    ("242", str(s23["shapes"]["total"]), "shapes in C_7^5"),
    ("4050", str(core["family"]["F_plus_U_range_by_t"]["9"][0]), "|F|+|U|, nine pairs, least"),
    ("4080", str(core["family"]["F_plus_U_range_by_t"]["9"][1]), "|F|+|U|, nine pairs, most"),
    ("4374", str(2 * 9 * 3 ** 5), "2 * 9 * 3^5"),
    ("162", str(orb[1]["forbidden_by_one_pair"]), "forbidden, k = 1"),
    ("108", str(orb[2]["forbidden_by_one_pair"]), "forbidden, k = 2"),
    ("72", str(orb[3]["forbidden_by_one_pair"]), "forbidden, k = 3"),
    ("48", str(orb[4]["forbidden_by_one_pair"]), "forbidden, k = 4"),
    ("32", str(orb[5]["forbidden_by_one_pair"]), "forbidden, k = 5"),
    ("32", str(orb[5]["size"]), "shapes with k = 5"),
    ("32", str(2 ** 5), "cells of a box"),
    ("324", str(orb[1]["penalised_by_one_pair"]), "penalised, k = 1"),
    ("378", str(orb[2]["penalised_by_one_pair"]), "penalised, k = 2"),
    ("414", str(orb[3]["penalised_by_one_pair"]), "penalised, k = 3"),
    ("438", str(orb[4]["penalised_by_one_pair"]), "penalised, k = 4"),
    ("454", str(orb[5]["penalised_by_one_pair"]), "penalised, k = 5"),
    ("10", str(orb[1]["size"]), "shapes with k = 1"),
    ("40", str(orb[2]["size"]), "shapes with k = 2"),
    ("80", str(orb[3]["size"]), "shapes with k = 3"),
    ("80", str(orb[4]["size"]), "shapes with k = 4"),
    ("366", str(real[1]), "largest set with a k = 1 pair"),
    ("367", str(real[2]), "largest set with a k = 2 pair"),
    ("366", str(real[3]), "largest set with a k = 3 pair"),
    ("366", str(real[4]), "largest set with a k = 4 pair"),
    ("366", str(real[5]), "largest set with a k = 5 pair"),
    ("343", str(pop["sets/C7_d5_343_linear.txt"]["size"]), "the linear code"),
    ("350", str(pop["sets/C7_d5_350_mathew_ostergard.txt"]["size"]), "the Mathew-Ostergard set"),
    ("3.21", str(max(r["F_spread_percent"] for r in c367)), "largest spread of |F| over colourings, 367-word codes"),
    ("51", str(s22["plateau"]["aut_classes"]), "Aut-classes of the plateau"),
    ("208", str(s22["regions"]["configurations_listed"]), "configurations with t >= 9"),
    ("1098", str(fb["9"]["F_min"]), "|F| at t = 9, least"),
    ("1128", str(fb["9"]["F_max"]), "|F| at t = 9, most"),
    ("1240", str(fb["10"]["F_min"]), "|F| at t = 10, least"),
    ("1268", str(fb["10"]["F_max"]), "|F| at t = 10, most"),
    ("972", str(s23["decomposition"]["per_pair_sum"]), "per-pair part of the nine-pair regions"),
    ("126", str(s23["decomposition"]["cross_terms_min"]), "cross terms, least"),
    ("156", str(s23["decomposition"]["cross_terms_max"]), "cross terms, most"),
    ("64538880", str(s22["sweep"]["group_elements_per_pair"]), "group elements per pair"),
    ("65829657600", str(s22["sweep"]["images_scored"]), "images scored"),
    ("366", str(best_t(9)), "best repaired at t = 9"),
    ("365", str(best_t(10)), "best repaired at t = 10"),
    ("108", str(s22["kopt"]["sets"]), "repaired 366-word sets tested for 3-opt"),
    ("401", str(s21["lovasz_bound"]), "the Lovasz bound on alpha(C_7^5)"),
    ("15679", str(16807 - fb["9"]["F_max"]), "allowed vertices, least"),
    ("15709", str(16807 - fb["9"]["F_min"]), "allowed vertices, most"),
    ("0.879", str(ratio(367, 9, 1)), "ratio needed, k = 1"),
    ("0.754", str(ratio(367, 9, 2)), "ratio needed, k = 2"),
    ("0.688", str(ratio(367, 9, 3)), "ratio needed, k = 3"),
    ("0.651", str(ratio(367, 9, 4)), "ratio needed, k = 4"),
    ("0.628", str(ratio(367, 9, 5)), "ratio needed, k = 5"),
    ("0.7678", str(s23["price_model"]["best_ratio_on_record"]), "best ratio on record"),
    ("0.68", str(max(r["ratio_needed"] for r in pm if r["a"] == 366)), "largest ratio at 366 words"),
]
# small numbers that carry a claim: (value from results, expected, pattern in the text)
CLAIMS = [
    (pop["sets/C7_d5_350_mathew_ostergard.txt"]["candidates"], 7, r"has\s+seven"),
    (s23["population"][1]["candidate_shapes_by_k"][0], 7, r"all seven\s+candidates"),
    (pop["sets/C7_d5_343_linear.txt"]["candidates"], 0, r"code \\cite\{baumert1971\} has none"),
    (pop["sets/C7_d5_367_reproduced.txt"]["candidates"], 6, r"differs in two words has six"),
    (pop["sets/C7_d5_367_polak_schrijver.txt"]["candidates"], 8, r"code has eight"),
    (min(r["candidates"] for r in c367), 5, r"run from\s+\$5\$"),
    (max(r["candidates"] for r in c367), 10, r"to \$10\$"),
    (all(sum(r["candidate_shapes_by_k"]) == r["candidate_shapes_by_k"][1]
         for r in s23["population"] if r["size"] == 367), True, r"every candidate has shape \$k=2\$"),
    (s22["plateau"]["classes_by_t_star"]["9"], 2, r"Two classes have nine candidates"),
    (s22["plateau"]["classes_by_t_star"]["10"], 1, r"one class has ten"),
    (fb["9"]["classes"], 16, r"exactly \$16\$ forbidden regions at \$t=9\$"),
    (fb["10"]["classes"], 4, r"\$4\$ at \$t=10\$"),
    (s22["sweep"]["grand_min_hits"], 1, r"in \$F\$ is \$1\$"),
    (s22["kopt"]["sets_with_an_improving_window"], 0, r"exactly \$3\$-opt optimal"),
    (sorted({l["blockers_histogram_up_to_two"]["1"] for l in s22["looseness"]}), [2, 3], r"Only \$2\$ or \$3\$"),
    (s23["plateau_cells"]["fewest_covered_cells_in_a_box"], 5, r"has at least \$5\$"),
    (core["plateau"]["switches_found"], 5, r"five independent three-state switches"),
    (core["plateau"]["component_rebuilt_from_switches"], True, r"product of\s+five independent"),
    (sorted(core["plateau"]["coordinates_moved_per_switch"]), [[0, 1], [0, 4], [1, 2], [2, 3], [3, 4]],
     r"cyclically adjacent pairs of coordinates"),
    (core["plateau"]["stabiliser_order"], 5, r"automorphism\s+of order \$5\$"),
    (sorted(core["plateau"]["stabiliser_coordinate_cycle_types"][1:]), [[5]] * 4, r"cycles\s+the coordinates"),
    (core["plateau"]["components"], 3, r"a third start adds a third"),
    (core["identity_all_pass"], True, r"checked by direct count for every shape"),
    (core["shape_formula_fails_for_n_3"], True, r"not\s+Lemma~\\ref\{lem:shape\}"),
    (s22["sweep"]["admissible_full_size"], 0, r"No image avoids any region"),
    (s22["controls"]["sweep_t8"]["histogram_reproduced"], True, r"reproduces the histogram"),
    (s22["controls"]["sweep_t8"]["best_repaired_size"], 367, r"reaches \$367\$ at \$t=8\$"),
    (s22["controls"]["kopt_passed"], True, r"recovers \$367\$ from deliberately damaged sets"),
    (s22["controls"]["automorphism_generator"]["mutant_2x_rejected"], True, r"rejects a non-automorphism"),
]
YEARS = {"2026"}


def main():
    w = open(WRAPPER, encoding="utf-8").read()
    for part in ("note2-abstract", "note2-content"):
        if part not in w:
            sys.exit(f"note2/note2.tex does not include {part}")
    raw = "\n".join(open(p, encoding="utf-8").read() for p in TEXT)
    txt = "\n".join(body(open(p, encoding="utf-8").read()) for p in TEXT)
    tokens = re.findall(r"\d+(?:\.\d+)?", txt)
    rows, bad = [], 0
    for printed, computed, what in LEDGER:
        ok = printed == computed
        inn = printed in tokens
        rows.append({"printed": printed, "computed": computed, "what": what, "value_agrees": ok, "appears_in_note": inn})
        bad += not (ok and inn)
    crow = []
    for got, exp, rx in CLAIMS:
        ok = got == exp
        inn = re.search(rx, raw, re.S) is not None
        crow.append({"pattern": rx, "computed": str(got), "expected": str(exp), "value_agrees": ok, "appears_in_note": inn})
        bad += not (ok and inn)
    covered = {p for p, _, _ in LEDGER} | YEARS | STRUCTURAL
    unacc = sorted({t for t in tokens if t not in covered}, key=lambda t: (len(t), t))
    out = {"text_files": [os.path.relpath(p, ROOT) for p in TEXT], "ledger_entries": len(LEDGER), "claims": len(CLAIMS),
           "failures": bad, "distinct_numeric_tokens": len(set(tokens)), "unaccounted_tokens": unacc,
           "rows": rows, "claim_rows": crow, "all_pass": bad == 0 and not unacc}
    json.dump(out, open(os.path.join(J, "w2_checknums.json"), "w"), indent=2)
    print(f"{len(LEDGER) + len(CLAIMS) - bad}/{len(LEDGER) + len(CLAIMS)} entries check out; "
          f"{len(set(tokens))} distinct numeric tokens, {len(unacc)} unaccounted")
    for r in rows + crow:
        if not (r["value_agrees"] and r["appears_in_note"]):
            print("  FAIL", r)
    if unacc:
        print("  UNACCOUNTED:", unacc)
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

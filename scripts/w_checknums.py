"""Every number printed in note/note.tex, reconciled by machine against results/json.

Two directions, because either alone is easy to fool:

  forward  -- each entry of the ledger below is checked against the stored
              computation (or, for an external number, against a verbatim
              quotation in SOURCES.md), and must appear in the note;
  backward -- every numeric token in the body of the note must be covered by the
              ledger, by the small-structural allowlist (dimensions, indices,
              coordinates) or by the list of years.  A number in the note that
              nobody sourced is a failure, not a footnote.

Run it after every edit of the note.  Exit code 1 means the note and the
computations disagree.
"""
import json
import os
import re
import sys
from decimal import Decimal, getcontext

getcontext().prec = 80
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The text lives in two shared files; note/note.tex (standalone, archived with the Zenodo
# record) and submission/ipl/note_ipl.tex (elsarticle, for submission) both include them, so
# there is one place where a number can be wrong.  The submission's cover letter is swept too.
TEXT = [os.path.join(ROOT, "note", "note-abstract.tex"),
        os.path.join(ROOT, "note", "note-content.tex"),
        os.path.join(ROOT, "submission", "ipl", "cover_letter.md")]
WRAPPERS = [os.path.join(ROOT, "note", "note.tex"),
            os.path.join(ROOT, "submission", "ipl", "ipl-body.tex")]
J = os.path.join(ROOT, "results", "json")

_cache = {}


def jget(path):
    """'file.json:a.b.c' or with [i] indices."""
    fn, _, rest = path.partition(":")
    if fn not in _cache:
        _cache[fn] = json.load(open(os.path.join(J, fn)))
    cur = _cache[fn]
    for part in rest.split("."):
        m = re.fullmatch(r"([^\[\]]*)\[(\d+)\]", part)
        if m:
            if m.group(1):
                cur = cur[m.group(1)]
            cur = cur[int(m.group(2))]
        else:
            cur = cur[part]
    return cur


# (printed token, rule, spec, what it is)
LEDGER = [
    # --- the theorem ---
    ("367", "json_int", "w_theorem.json:code.size", "size of the Polak-Schrijver code"),
    ("16807", "json_int", "w_theorem.json:neighbour_histogram.universe", "|Z_7^5|"),
    ("16440", "json_int", "w_theorem.json:neighbour_histogram.words_outside_I", "words outside I"),
    ("8", "json_int", "w_theorem.json:neighbour_histogram.by_number_of_I_neighbours.1",
     "words with exactly one I-neighbour"),
    ("254", "json_int", "w_theorem.json:neighbour_histogram.by_number_of_I_neighbours.2",
     "words with two I-neighbours"),
    ("16178", "json_int", "w_theorem.json:neighbour_histogram.by_number_of_I_neighbours.3+",
     "words with three or more"),
    ("5", "json_int", "w_theorem.json:conflict_graph.components", "components of the conflict graph"),
    ("3", "json_int", "w_theorem.json:conflict_graph.edge_count", "edges of the conflict graph"),
    ("16", "derived", ("2**(comp-1)", {"comp": "w_theorem.json:conflict_graph.components"}),
     "proper 2-colourings up to swap"),
    # --- the recursion's numbers ---
    ("3.2587891539086910161967650155206769", "json_str", "gadget.json:gao.bound_dim_200",
     "Gao's bound, reproduced"),
    ("3.2588053698854655725829750306238067", "json_str", "s1_anchor.json:anchor.our_homogeneous_bound_dim200",
     "the BPZ profile through our homogeneous recursion"),
    ("3.2588326203532663091215390518104754", "json_prefix",
     "s1_anchor.json:framework_gap.heterogeneous_bpz_tandon_record", "the current record [T26]"),
    ("3.2590062007738521305802", "json_prefix", "s1_anchor.json:targets[6].homogeneous_bound",
     "what a ninth private pair would give"),
    ("3.3176672073940953927", "json_prefix", "theta.json:values.7", "the Lovasz upper bound"),
    ("1.736", "sci", ("s1_anchor.json:targets[6].margin_over_tandon_record", -4),
     "margin of a ninth pair over the record"),
    ("1.7", "sci", ("s1_anchor.json:targets[6].margin_over_tandon_record", -4),
     "the same margin, to two digits"),
    ("6.993", "sci", ("s1_anchor.json:targets[3].margin_over_tandon_record", -6),
     "margin of (367,8,367,324)"),
    ("2.725", "sci", ("s1_anchor.json:framework_gap.gap_record_minus_ours", -5),
     "the framework gap"),
    ("3.2578659667835159504124", "root", (367, 5), "367^(1/5)"),
    ("3.2580207372932453595278", "root", (134753, 10), "134753^(1/10)"),
    ("134753", "json_int", "construct_c7_d10.json:sizes.I", "the Itty et al. set"),
    # --- the published profiles ---
    ("321", "json_int", "gadget.json:base_gadget.profile.o", "Gao's o"),
    ("26", "json_int", "gadget.json:base_gadget.profile.h", "Gao's h"),
    ("20", "json_int", "gadget.json:base_gadget.profile.v", "Gao's v"),
    ("322", "json_int", "gadget.json:bpz.base_profile[3]", "BPZ's o"),
    ("19", "json_int", "gadget.json:bpz.base_profile[5]", "BPZ's v"),
    # --- the pipeline family ---
    ("327", "json_int", "s1_codes.json:core_M", "the core M"),
    ("71", "json_int", "s1_codes.json:extension_graph_vertices", "extension graph vertices"),
    ("85", "json_int", "s1_codes.json:extension_graph_edges", "extension graph edges"),
    ("40", "json_int", "construct_c7_d5_ps.json:extension_graph.alpha", "its independence number"),
    ("8", "json_int", "s1_codes.json:codes_of_size_367_from_the_pipeline", "codes of size 367"),
    # --- branch D ---
    ("13", "json_int", "s1_anchor.json:branch_D_break_even.private_pairs_needed_to_match.366",
     "pairs needed at a = 366"),
    ("16", "json_int", "s1_anchor.json:branch_D_break_even.private_pairs_needed_to_match.365",
     "pairs needed at a = 365"),
    ("23", "json_int", "s1_anchor.json:branch_D_break_even.private_pairs_needed_to_match.360",
     "pairs needed at a = 360"),
    ("366", "literal", 366, "code size in the break-even table"),
    ("365", "json_int", "construct_c7_d5_ps.json:overlap_with_printed_R",
     "also: words shared by our rebuild and the printed set"),
    ("360", "literal", 360, "code size in the break-even table"),
    # --- the group sweep ---
    ("120", "literal", 120, "|S_5|"),
    ("14", "literal", 14, "|D_7|"),
    ("64538880", "derived", ("14**5*120", {}), "|(D_7)^5 rtimes S_5|"),
    ("8260976640", "json_int", "s1_aux.json:group_elements_swept", "triples swept"),
    ("4", "json_int", "s1_aux.json:translations_with_bad_eq[1]", "triples with 1 forbidden word"),
    ("33", "json_int", "s1_aux.json:translations_with_bad_eq[2]", "with 2"),
    ("101", "json_int", "s1_aux.json:translations_with_bad_eq[3]", "with 3"),
    ("209", "json_int", "s1_aux.json:translations_with_bad_eq[4]", "with 4"),
    ("358", "json_int", "s1_aux.json:translations_with_bad_eq[5]", "with 5"),
    ("965", "json_int", "s1_aux.json:translations_with_bad_eq[6]", "with 6"),
    ("6060", "json_int", "s1_aux.json:translations_with_bad_eq[7]", "with 7"),
    ("663.9", "json_round", ("s1_aux.json:seconds", 1), "seconds of the sweep"),
    # --- repair and auxiliary search ---
    ("60", "json_int", "s1_repair.json:candidates_examined", "repaired candidates"),
    ("368", "derived", ("367+1", {}), "the record for alpha that a bigger repair would have given"),
    ("324", "json_int", "s1_anchor.json:targets[3].profile[3]",
     "the o that would be needed to clear the record"),
    ("1500", "json_round", ("s1_auxsearch.json:seconds_per_colouring", 0), "seconds per colouring"),
    # --- reproducibility ---
    ("11744", "json_int", "w_theorem.json:code.verifier.box_cells", "box cells of a 367-word set"),
    ("137987072", "json_int", "construct_c7_d10.json:verify.box_cells", "box cells at d = 10"),
    ("0.47", "json_round", ("construct_c7_d10.json:verify.box_seconds", 2), "seconds for that sweep"),
    ("1177", "derived",
     ("sum(c['tested'] for c in calib)", {"calib": "calibration.json:A_corruption"}),
     "single-vertex corruptions tested"),
    ("18", "derived",
     ("sum(c['still_independent'] for c in nm)", {"nm": "calibration.json:A_nonmaximal"}),
     "corruptions that leave an independent set"),
    ("18.7", "json_round", ("s1_budget.json:core_hours_estimate", 1), "core-hours used"),
    # --- claims that are lists rather than single numbers ---
    ("t-histogram", "claim",
     ("sorted(c['t'] for c in per)", {"per": "s1_codes.json:per_code"},
      "[5, 6, 6, 6, 7, 7, 7, 8]", r"5,\\;6,\\;6,\\;6,\\;7,\\;7,\\;7,\\;8"),
     "the private-pair counts of the eight pipeline codes"),
    ("conflict-edges", "claim",
     ("e", {"e": "w_theorem.json:conflict_graph.edges"}, "[[0, 1], [2, 6], [3, 5]]",
      r"q_0\\sim q_1.*q_2\\sim q_6.*q_3\\sim q_5"),
     "the three edges, in Gao's numbering"),
    ("offender", "claim",
     ("w", {"w": "w_theorem.json:forbidden_region_of_T_image.words_confusable_with_both_transversals"},
      "[[2, 4, 6, 3, 5]]", r"\(2,4,6,3,5\)"),
     "the single word of T(I) confusable with both transversals"),
    ("published-colouring", "claim",
     ("[j0, j1]", {"j0": "w_theorem.json:published_colouring.J0",
                   "j1": "w_theorem.json:published_colouring.J1"},
      "[[0, 5, 6], [1, 2, 3, 4, 7]]", r"J_0=\\\{0,5,6\\\}"),
     "the transversal assignment the literature uses"),
    ("t-max", "claim",
     ("t", {"t": "w_theorem.json:conflict_graph.t_max"}, "8", r"t\^\*\(I_0\)=8"),
     "the theorem's value"),
    # --- the journal reference of the code's paper, from the dumped abstract page ---
    ("143", "absdump", ("1808.07438", "Information Processing Letters, 143 (2019), 37-40"),
     "volume of Polak-Schrijver, quoted in the cover letter"),
    ("37", "absdump", ("1808.07438", "Information Processing Letters, 143 (2019), 37-40"),
     "its first page"),
    # --- external numbers, Rule 0 ---
    ("343", "sources", "343", "Baumert et al., quoted in SOURCES.md"),
    ("350", "sources", "350", "Mathew-Ostergard, quoted in SOURCES.md"),
]

YEARS = {"1956", "1971", "1979", "2002", "2015", "2017", "2019", "2026"}
# dimensions, coordinates, small indices and exponents; every one of them is
# structural (7 for C_7, 5 for the fifth power, the words (2,4,6,3,5), ...)
STRUCTURAL = {str(i) for i in range(0, 21)}


def body(tex):
    s = re.sub(r"(?<!\\)%.*", "", tex)
    s = re.sub(r"\\texttt\{[^}]*\}", " ", s)            # file names and checksums
    s = re.sub(r"\\(cite|ref|label)\{[^}]*\}", " ", s)
    s = re.sub(r"\\href\{[^}]*\}", " ", s)
    s = re.sub(r"SHA-256|SHA256SUMS", " ", s)            # the name of a hash, not a number
    s = re.sub(r"10\.5281/zenodo\.[A-Za-z0-9.]+", " ", s)   # the DOI of the archive
    s = re.sub(r"\b\d{4}-\d{4}-\d{4}-\d{4}\b", " ", s)      # the author's ORCID
    s = re.sub(r"\{,\}", "", s)                          # 8{,}260{,}976{,}640 -> one number
    return s


def check(rule, spec, printed):
    if rule == "json_int":
        return str(jget(spec)) == printed, str(jget(spec))
    if rule == "json_str":
        return str(jget(spec)) == printed, str(jget(spec))
    if rule == "json_prefix":
        v = str(jget(spec))
        return v.startswith(printed), v
    if rule == "json_round":
        path, nd = spec
        v = float(jget(path))
        return f"%.{nd}f" % v == printed, repr(v)
    if rule == "sci":
        path, exp = spec
        v = Decimal(str(jget(path)))
        m = v / Decimal(10) ** exp
        sig = len(printed.split(".")[1]) + 1
        return round(m, sig - 1) == Decimal(printed), f"{m}e{exp}"
    if rule == "root":
        x, k = spec
        digits = printed.replace(".", "")
        p = len(printed.split(".")[1])
        lo = int(digits)
        return lo ** k <= x * 10 ** (k * p) < (lo + 1) ** k, f"{x}^(1/{k})"
    if rule == "derived":
        expr, paths = spec
        env = {k: jget(v) for k, v in paths.items()}
        return str(eval(expr, {"sum": sum}, env)).find(printed) >= 0, str(eval(expr, {"sum": sum}, env))
    if rule == "literal":
        return printed == str(spec), str(spec)
    if rule == "claim":
        expr, paths, expected, rx = spec
        env = {k: jget(v) for k, v in paths.items()}
        got = str(eval(expr, {"sum": sum, "sorted": sorted}, env))
        return got == expected, got
    if rule == "absdump":
        aid, line = spec
        import html as _html
        raw = open(os.path.join(ROOT, "sources", aid, "abs.html"),
                   encoding="utf-8", errors="replace").read()
        txt = _html.unescape(re.sub(r"<[^>]+>", " ", raw))
        txt = re.sub(r"\s+", " ", txt)
        return (line in txt) and (printed in line), line
    if rule == "sources":
        src = open(os.path.join(ROOT, "SOURCES.md"), encoding="utf-8").read()
        quotes = [ln for ln in src.splitlines() if ln.startswith("> ")]
        return any(spec in q for q in quotes), "quoted in SOURCES.md"
    raise AssertionError(rule)


def main():
    missing = [p for p in TEXT + WRAPPERS if not os.path.exists(p)]
    if missing:
        sys.exit("missing: " + ", ".join(missing))
    txt = "\n".join(body(open(p, encoding="utf-8").read()) for p in TEXT)
    # both wrappers must actually include the shared text, or the sweep proves nothing
    for wp in WRAPPERS:
        w = open(wp, encoding="utf-8").read()
        for part in ("note-abstract", "note-content"):
            if part not in w:
                sys.exit(f"{os.path.relpath(wp, ROOT)} does not include {part}")
    tokens = re.findall(r"\d+(?:\.\d+)?", txt)

    rows, bad = [], 0
    for printed, rule, spec, what in LEDGER:
        ok_value, got = check(rule, spec, printed)
        if rule == "claim":
            in_note = re.search(spec[3], txt, re.S) is not None
        else:
            in_note = printed in tokens
        rows.append({"printed": printed, "rule": rule, "what": what,
                     "source": spec if isinstance(spec, str) else str(spec),
                     "computed": got,
                     "value_agrees": bool(ok_value), "appears_in_note": bool(in_note)})
        if not (ok_value and in_note):
            bad += 1

    covered = {p for p, r, *_ in LEDGER if r != "claim"} | YEARS | STRUCTURAL
    unaccounted = sorted({t for t in tokens if t not in covered},
                         key=lambda t: (len(t), t))
    out = {
        "text_files": [os.path.relpath(p, ROOT) for p in TEXT],
        "wrappers": [os.path.relpath(p, ROOT) for p in WRAPPERS],
        "ledger_entries": len(LEDGER),
        "failures": bad,
        "numeric_tokens_in_body": len(tokens),
        "distinct_numeric_tokens": len(set(tokens)),
        "unaccounted_tokens": unaccounted,
        "rows": rows,
        "all_pass": bad == 0 and not unaccounted,
    }
    with open(os.path.join(J, "w_checknums.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"{len(LEDGER) - bad}/{len(LEDGER)} ledger entries check out; "
          f"{len(set(tokens))} distinct numeric tokens in the text, "
          f"{len(unaccounted)} unaccounted")
    for r in rows:
        if not (r["value_agrees"] and r["appears_in_note"]):
            print("  FAIL", r["printed"], r["rule"], r["source"],
                  "value_agrees" if r["value_agrees"] else "VALUE",
                  "in_note" if r["appears_in_note"] else "NOT-IN-NOTE")
    if unaccounted:
        print("  UNACCOUNTED:", ", ".join(unaccounted))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

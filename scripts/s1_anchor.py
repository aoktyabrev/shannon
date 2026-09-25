"""S1.1 -- anchoring Stage 1 to the record before anything is searched for.

Three things, in the order the Stage 1 brief asks for them.

1. The eight-pair base gadget is pushed through *our* homogeneous recursion --
   the same code that would carry a nine-pair gadget -- and must land exactly on
   the published Buys-Polak-Zuiddam bound.  If it did not, every later number
   from the same code would be worthless.

2. The margin of a hypothetical nine-pair result is written against **Tandon's**
   record, not against the previous bound.

3. The frameworks are compared on identical input.  Tandon starts from the same
   five-dimensional base gadget as BPZ, profile (367,8,367,322,26,19) [T26-6,
   quoted at SOURCES.md], and his heterogeneous recursion extracts more from it
   than the homogeneous one does.  That difference is the *framework gap*, and a
   margin smaller than it would mean only "our number beats their number", while
   their method on our base would beat ours.  The gap is computed here and the
   Stage 1 target is restated against it.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gadget import bound_digits, recursion  # noqa: E402
from setio import ROOT  # noqa: E402

from decimal import Decimal, getcontext  # noqa: E402
getcontext().prec = 60

# Published numbers, all quoted verbatim in SOURCES.md.
BPZ_HOMOGENEOUS = "3.258805369885"                                    # [BPZ26-1]
TANDON_WARMUP = "3.2588236744275819433344360437765093813959865800495343"   # [T26-8]
BPZ_GITHUB = "3.258827985920007034526478965794221"                    # [T26-3]
TANDON_RECORD = "3.2588326203532663091215390518104754376053875943219"  # [T26-2]


def main():
    rep = {}

    # --- 1. the eight-pair case through our own recursion ---
    M8, t8, s8, o8, split8 = recursion(367, 8, 367, 322, 40)
    ours = bound_digits(M8[40], 200, 34)
    rep["anchor"] = {
        "base_profile": [367, 8, 367, 322, 26, 19],
        "our_homogeneous_bound_dim200": ours,
        "published_bpz": BPZ_HOMOGENEOUS,
        "matches_bpz": ours.startswith(BPZ_HOMOGENEOUS),
        "split_tree": {str(k): list(split8[k]) for k in (2, 3, 5, 10, 20, 40)},
        "M40_digits": len(str(M8[40])),
    }
    # the same code on Gao's profile, as a second anchor
    MG, *_ = recursion(367, 8, 367, 321, 40)
    rep["anchor"]["gao_profile_bound"] = bound_digits(MG[40], 200, 34)
    rep["anchor"]["matches_gao"] = rep["anchor"]["gao_profile_bound"].startswith(
        "3.2587891539086910161967650155206769")

    # --- 3. the framework gap, on identical input ---
    ours_d = Decimal(ours)
    rec_d = Decimal(TANDON_RECORD)
    gap = rec_d - ours_d
    rep["framework_gap"] = {
        "same_base_profile": [367, 8, 367, 322, 26, 19],
        "homogeneous_recursion_ours": ours,
        "heterogeneous_gao_tandon_warmup": TANDON_WARMUP,
        "bpz_multi_gadget_github": BPZ_GITHUB,
        "heterogeneous_bpz_tandon_record": TANDON_RECORD,
        "gap_record_minus_ours": str(gap),
        "note": ("Tandon's recursion is strictly stronger than ours on the same base gadget. "
                 "A Stage 1 margin below this gap would be a claim about numbers, not about "
                 "methods: the same base fed through his framework would beat ours."),
    }

    # --- 2. what each hypothetical base profile would be worth, against the record ---
    rows = []
    for (a, t, s, o, label) in [
        (367, 8, 367, 321, "Gao base"),
        (367, 8, 367, 322, "BPZ base (current)"),
        (367, 8, 367, 323, "one extra O word"),
        (367, 8, 367, 324, "two extra O words"),
        (367, 8, 367, 325, "three extra O words"),
        (367, 8, 367, 326, "four extra O words"),
        (367, 9, 367, 321, "a ninth private pair"),
        (367, 9, 367, 322, "ninth pair, BPZ auxiliary split"),
        (367, 10, 367, 321, "a tenth private pair"),
    ]:
        M, *_ = recursion(a, t, s, o, 40)
        b = bound_digits(M[40], 200, 34)
        m = Decimal(b) - rec_d
        rows.append({
            "profile": [a, t, s, o], "label": label,
            "homogeneous_bound": b,
            "margin_over_tandon_record": str(m),
            "beats_record": m > 0,
            "robust_to_framework_choice": m > gap,
        })
    rep["targets"] = rows

    # the smallest o, at t = 8, that clears the gap as well as the record
    o_needed_record = o_needed_robust = None
    for o in range(321, 368):
        M, *_ = recursion(367, 8, 367, o, 40)
        m = Decimal(bound_digits(M[40], 200, 34)) - rec_d
        if o_needed_record is None and m > 0:
            o_needed_record = o
        if o_needed_robust is None and m > gap:
            o_needed_robust = o
            break
    rep["restated_target"] = {
        "preregistered_S1P": "homogeneous bound > " + TANDON_RECORD,
        "t8_o_needed_to_beat_the_record": o_needed_record,
        "t8_o_needed_to_be_robust_to_the_framework_gap": o_needed_robust,
        "t9_already_robust": rows[6]["robust_to_framework_choice"],
        "conclusion": ("A ninth private pair clears the record by 1.7e-4, far above the 2.7e-5 "
                       "framework gap, so it would be an improvement under any of the published "
                       "recursions. The o >= %d route clears the record as preregistered but not "
                       "the gap; o >= %d would clear both. Stage 1 keeps the preregistered target "
                       "and reports the gap alongside any claim."
                       % (o_needed_record, o_needed_robust)),
    }
    # Branch D of the preregistration: a gadget's code need not be maximum, so a
    # smaller code with more private pairs is admissible in principle.  This is the
    # price list.  It is a calculation, not a search, and it closes the branch.
    ref = Decimal(bound_digits(recursion(367, 8, 367, 321, 40)[0][40], 200, 30))
    be = {}
    for a in (366, 365, 360):
        t = 8
        while t < 400:
            t += 1
            v = Decimal(bound_digits(recursion(a, t, 367, 321, 40)[0][40], 200, 30))
            if v > ref:
                break
        be[str(a)] = t
    rep["branch_D_break_even"] = {
        "reference": "(367, 8, 367, 321) = " + str(ref),
        "private_pairs_needed_to_match": be,
        "note": ("A code of size 366 would need 13 private pairs to match what the 367-word code "
                 "achieves with 8, and 365 would need 16. The 367-word code has exactly 8 "
                 "candidates in the whole of Z_7^5, so this is not a promising direction; the "
                 "branch is closed on the calculation rather than on a search."),
    }

    # Why the auxiliary set must keep all 367 words: trading size for O-words loses.
    ss = []
    for (a, t, sz, o) in [(367, 8, 367, 321), (367, 8, 367, 322), (367, 8, 366, 330),
                          (367, 8, 365, 333), (367, 8, 360, 340), (367, 8, 350, 340)]:
        M, *_ = recursion(a, t, sz, o, 40)
        ss.append({"profile": [a, t, sz, o],
                   "bound": bound_digits(M[40], 200, 30)})
    rep["auxiliary_size_sensitivity"] = {
        "rows": ss,
        "note": ("The exact repair of the best near miss yields (367, 8, 365, 333): two words "
                 "short but twelve O-words richer than the published gadget. It scores below "
                 "(367, 8, 367, 321) all the same. |X| = 367 is not negotiable."),
    }

    rep["all_pass"] = bool(rep["anchor"]["matches_bpz"] and rep["anchor"]["matches_gao"])
    with open(os.path.join(ROOT, "results", "json", "s1_anchor.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()

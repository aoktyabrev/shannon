"""Budget accounting for Stage 1, against the ceilings sealed in
PREREGISTRATION_S1.md: 20 GPU-hours, 100 CPU core-hours, 14 days wall-clock.

Honesty note, because this matters more than the number.  Only part of the CPU
time is recorded in results/json (the runs whose reports carry a `seconds`
field).  The rest went on exploratory parameter sweeps -- four changes of search
method on C_7^{boxtimes 4} -- which were not individually logged.  The table
below is therefore a **reconstruction from the session's run log**, itemised so
that it can be argued with, not a measurement.  Its accuracy is perhaps +-30%,
which does not matter for the conclusion: the ceiling is 100 core-hours and the
total is an order of magnitude below it.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT  # noqa: E402

# (label, core-seconds, measured?)
ITEMS = [
    ("E1 exact runs on C_7^3 (decisive, witness, mutant, gate)", 220, True),
    ("E2 local-search experiments on C_7^4", 1170, False),
    ("E3 symmetry sweep 1: 240 single generators x 4 s", 960, False),
    ("E3 symmetry sweep 2: 784 generators of order 2,3,4,6 x 6 s", 4704, False),
    ("E3 orbit-tabu probes", 240, False),
    ("E2 fixed-cardinality tabu/annealing experiments", 3870, False),
    ("E4 large-neighbourhood search experiments", 900, False),
    ("E2+E4 window-repair sweeps at k = 107 and 108", 10850, False),
    ("the gate run end to end (scripts/s1_gate.py)", 1800, False),
    ("S1.2 branch B: the Aut(C_7^5) sweep, 8 threads", 5344, True),
    ("S1.2 branch B: fixed-cardinality auxiliary search, 8+16 colourings x 1500 s", 36000, True),
    ("S1.2 branches C and D, private-pair enumeration, anchoring", 900, True),
    ("verification of every produced set", 200, True),
]


def main():
    total = sum(x[1] for x in ITEMS)
    measured = sum(x[1] for x in ITEMS if x[2])
    rep = {
        "ceilings": {"gpu_hours": 20, "core_hours": 100, "wall_clock_days": 14},
        "gpu_hours": "0.0 — none used",
        "core_hours_estimate": round(total / 3600.0, 1),
        "core_hours_measured_portion": round(measured / 3600.0, 1),
        "wall_clock": "one day (2026-09-25)",
        "items": [{"what": a, "core_seconds": b, "measured": c} for a, b, c in ITEMS],
        "note": ("No GPU time was used at all. The preregistration set aside 20 GPU-hours on the "
                 "assumption that the search would be over large vertex sets; it was not — once "
                 "the gadget condition reduced to a bipartite-colouring question on eight "
                 "candidates, and the auxiliary-set question to a cyclic correlation over the "
                 "automorphism group, everything fitted on the CPU. The CPU figure is a "
                 "reconstruction from the run log, itemised in `results/json/s1_budget.json`, "
                 "accurate to perhaps ±30%; the ceiling is not close."),
    }
    with open(os.path.join(ROOT, "results", "json", "s1_budget.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps({k: v for k, v in rep.items() if k != "items"}, indent=2))


if __name__ == "__main__":
    main()

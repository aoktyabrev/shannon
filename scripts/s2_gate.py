"""S2.1 -- the gate, recorded with the command lines that produced each number.

The gate asks the search stack to reach 350 in C_7^{boxtimes 5} from a random start,
the Mathew-Ostergard value. It is not passed. This file is the record: every engine
run, its command line, its result, and the reading -- including the two controls that
make the failure informative rather than merely disappointing.

The runs themselves are long, so they are executed outside this script (their JSON is
read from the paths below) and the command lines are stored beside the numbers so the
runs can be repeated exactly.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("SHANNON_TMP", "/tmp")

RUNS = [
    ("E3 prescribed symmetry, the generator Mathew-Ostergard publish for their own 350-set",
     "scripts/s1_sym 7 5 --gen 0,1,2,3,4:1,1,1,1,1:0,1,1,5,1 --target 350 --seconds 900 --seed 1",
     "gateA.json"),
    ("E3, the same generator, twice the time",
     "scripts/s1_sym 7 5 --gen 0,1,2,3,4:1,1,1,1,1:0,1,1,5,1 --target 350 --seconds 1800 --seed 11",
     "gateA2.json"),
    ("E3, the same generator, four times the time and another seed",
     "scripts/s1_sym 7 5 --gen 0,1,2,3,4:1,1,1,1,1:0,1,1,5,1 --target 350 --seconds 3600 --seed 23",
     "gateA3.json"),
    ("E3, a generic translation of order 7",
     "scripts/s1_sym 7 5 --gen 0,1,2,3,4:1,1,1,1,1:1,2,3,4,5 --target 350 --seconds 900 --seed 2",
     "gateB.json"),
    ("E3, the degenerate translation (1,1,1,1,1) -- the control that must fail",
     "scripts/s1_sym 7 5 --gen 0,1,2,3,4:1,1,1,1,1:1,1,1,1,1 --target 350 --seconds 3600 --seed 29",
     "gateE.json"),
    ("E2 free local search from a random start, seed 3",
     "scripts/s1_ils 7 5 --target 350 --seconds 900 --seed 3", "gateC1.json"),
    ("E2 free local search from a random start, seed 4",
     "scripts/s1_ils 7 5 --target 350 --seconds 900 --seed 4", "gateC2.json"),
    ("E4 large-neighbourhood search with exact window repair, started from the best symmetric set",
     "scripts/s1_lns 7 5 --start <the 336-word symmetric set> --target 350 --seconds 1800 --seed 7",
     "gateD.json"),
]


def main():
    rows = []
    for what, cmd, fn in RUNS:
        p = os.path.join(TMP, "s2", fn)
        if not os.path.exists(p):
            rows.append({"engine": what, "command": cmd, "missing": fn})
            continue
        r = json.load(open(p))
        rows.append({"engine": what, "command": cmd,
                     "best": r.get("best"), "target": r.get("target"),
                     "reached": r.get("reached"), "seconds": r.get("seconds"),
                     "restarts": r.get("restarts"), "windows": r.get("windows"),
                     "improvements": r.get("improvements"),
                     "orbits_usable": r.get("orbits_usable"),
                     "orbits_chosen": r.get("orbits_chosen")})
    best = max((r["best"] for r in rows if r.get("best") is not None), default=None)
    out = {
        "threshold": 350,
        "threshold_source": "Mathew-Ostergard [MO17-1], the published value for alpha(C_7^5)",
        "runs": rows,
        "best_reached": best,
        "passed": bool(best is not None and best >= 350),
        "core_seconds": sum(r.get("seconds") or 0 for r in rows),
        "reading": (
            "Not passed. The best is 343 = 49 orbits of 7, one orbit short of 350, and it came "
            "from the quotient by the very group whose 350-word set is printed in the appendix of "
            "[MO17] -- so a solution exists there and the engine does not find it. More time does "
            "not help: 3600 s with another seed gave 336 where 1800 s gave 343, which is seed "
            "variance, not a trend. Exact window repair added nothing at all from the 336 "
            "(4.75e6 windows, zero improvements). Free search from a random start reached 311 and "
            "308. For scale, Mathew and Ostergard spent more than 2 CPU-years on the four results "
            "their paper reports, against the 200 core-hours preregistered here."),
        "controls": {
            "degenerate_generator": (
                "The translation (1,1,1,1,1) has no usable orbit at all -- every orbit contains "
                "two words at circular distance 1 in every coordinate -- and the engine reported "
                "0 usable orbits rather than searching a vacuum."),
            "known_solution_in_the_quotient": (
                "The MO generator's quotient provably contains a 50-orbit solution, which is what "
                "makes 343 a measurement of the engine rather than of the problem."),
        },
        "consequence": (
            "The gate guards direction S2.3.4, the free search for a new 367-word code: that "
            "direction is not started. The work done in this stage uses codes already in hand "
            "(S2.3.1 and the auxiliary-set question), which the gate does not cover."),
    }
    with open(os.path.join(ROOT, "results", "json", "s2_gate.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"{'engine':70} {'best':>5} {'secs':>6}")
    for r in rows:
        print(f"{r['engine'][:70]:70} {str(r.get('best')):>5} {str(r.get('seconds')):>6}")
    print()
    print("best reached:", best, "| gate passed:", out["passed"],
          "| core-seconds:", out["core_seconds"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

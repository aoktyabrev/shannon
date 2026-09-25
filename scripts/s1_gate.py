"""S1.0 -- the gate.  The search stack has to find the known optima before it is
pointed at an unknown one.

Targets set by the Stage 1 brief: alpha(C_7^{boxtimes 3}) = 33, which Stage 0's
generic branch and bound missed (32, no proof), and alpha(C_7^{boxtimes 4}) >= 108.
Both must be confirmed by scripts/verify, which knows nothing about how the sets
were found.

The stack, named here because the brief asks which search model is used and why it
suits 16807 vertices when 343 was hard:

  E1  exact cyclic layer search (scripts/s1_alpha3).  Decomposes C_n^{boxtimes 3}
      into n layers and uses the size arithmetic of the cyclic pair constraint to
      pin the problem onto the 980 maximum 2-dimensional packings.  Exact; proves
      upper bounds.
  E2  local search and fixed-cardinality tabu search (scripts/s1_ils).  Finds
      sets; proves nothing.
  E3  prescribed symmetry (scripts/s1_sym).  Moves the search to the orbit graph
      of an explicitly given group, after checking that the generators really are
      automorphisms and really are not the identity.
  E4  large-neighbourhood search with exact repair (scripts/s1_lns), and the same
      repair move inside E2's tabu loop.

Why 16807 vertices is not the problem 343 was: the Stage 1 target is not a maximum
independent set in C_7^{boxtimes 5}.  The code is fixed -- it is the known 367-word
set -- and what is searched over is the gadget structure on top of it: candidate
private pairs, a 2-colouring, and an auxiliary set drawn from the automorphism
group.  Those live in structures of size 10^2 to 10^7, not in the independent-set
lattice of a 16807-vertex graph.  E1-E4 are needed for the gate and for the
auxiliary-set step, not for the pair search itself.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, verify  # noqa: E402

S = lambda *a: os.path.join(ROOT, *a)
SETS = S("sets")


def run(cmd, env=None):
    e = dict(os.environ)
    if env:
        e.update({k: str(v) for k, v in env.items()})
    out = subprocess.run(cmd, capture_output=True, text=True, env=e)
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return {"stdout": out.stdout.strip(), "stderr": out.stderr.strip()[-400:],
                "returncode": out.returncode}


def main():
    rep = {}

    # ---- G1: the exact upper bound, and the positive control ----
    rep["G1_exact_upper_bound"] = run([S("scripts", "s1_alpha3"), "--json"])
    wit = S("sets", "C7_d3_33_layer_search.txt")
    rep["G1_witness_run"] = run([S("scripts", "s1_alpha3"), "--m0", "3", "--witness", wit, "--json"])
    rep["G1_witness_verified"] = verify(wit, ["--both", "--maximal"])
    g1 = rep["G1_exact_upper_bound"]
    rep["G1_pass"] = bool(g1.get("smallest_sigma_proved_impossible") == 34
                          and g1.get("alpha_d3_upper_bound") == 33
                          and rep["G1_witness_verified"]["independent"]
                          and rep["G1_witness_verified"]["size"] == 33)

    # ---- G2: the same engine, deliberately broken, must be wrong ----
    mut = run([S("scripts", "s1_alpha3"), "--open-nbhd", "--json"])
    rep["G2_mutant"] = {
        "run": mut,
        "claims_sigma_35_attainable": mut.get("cycle_closed") and mut.get("closed_at_sigma") == 35,
        "truth": "alpha(C_7^3) = 33, so 35 is false",
        "pass": bool(mut.get("cycle_closed") and mut.get("closed_at_sigma", 0) >= 34),
    }

    # ---- G3: the stochastic engines find 33 too ----
    p33t = S("sets", "C7_d3_33_tabu.txt")
    rep["G3_tabu_33"] = run([S("scripts", "s1_ils"), "7", "3", "--anneal", "33",
                             "--seconds", "60", "--seed", "1", "--out", p33t, "--json"])
    rep["G3_tabu_33_verified"] = verify(p33t, ["--both"])
    p33l = "/tmp/shannon_s1_lns33.txt"
    rep["G3_lns_33"] = run([S("scripts", "s1_lns"), "7", "3", "--target", "33",
                            "--seconds", "60", "--seed", "1", "--out", p33l, "--json"])
    rep["G3_lns_33_verified"] = verify(p33l, ["--both"]) if os.path.exists(p33l) else None
    rep["G3_pass"] = bool(rep["G3_tabu_33_verified"]["independent"]
                          and rep["G3_tabu_33_verified"]["size"] == 33
                          and rep["G3_lns_33_verified"]
                          and rep["G3_lns_33_verified"]["size"] == 33)

    # ---- G4: the symmetry engine checks its own generators ----
    real = "0,1,2,3:1,1,1,1:1,2,3,4"
    rep["G4_symmetry_controls"] = {
        "identity_rejected": run([S("scripts", "s1_sym"), "7", "4", "--gen",
                                  "0,1,2,3:1,1,1,1:0,0,0,0", "--json"]),
        "non_automorphism_rejected": run([S("scripts", "s1_sym"), "7", "4", "--gen", real,
                                          "--fake-gen", "--json"]),
        "real_symmetry_accepted": run([S("scripts", "s1_sym"), "7", "4", "--gen", real,
                                       "--seconds", "10", "--json"]),
    }
    c = rep["G4_symmetry_controls"]
    rep["G4_pass"] = bool(c["identity_rejected"].get("rejected")
                          and c["identity_rejected"].get("generators_nontrivial") is False
                          and c["non_automorphism_rejected"].get("rejected")
                          and c["non_automorphism_rejected"].get("generators_are_automorphisms") is False
                          and c["real_symmetry_accepted"].get("generators_are_automorphisms") is True)

    # ---- G5: the ladder on C_7^4 ----
    ladder = []
    p = "/tmp/shannon_s1_e2.txt"
    r = run([S("scripts", "s1_ils"), "7", "4", "--target", "200", "--seconds", "60",
             "--seed", "1", "--out", p, "--json"])
    ladder.append({"engine": "E2 local search", "best": r.get("best"), "file": p,
                   "verified": verify(p)["size"] if os.path.exists(p) else None})
    p = S("sets", "C7_d4_105_symmetric.txt")
    r = run([S("scripts", "s1_sym"), "7", "4", "--gen", real, "--seconds", "30",
             "--out", p, "--json"])
    ladder.append({"engine": "E3 prescribed symmetry (translation by (1,2,3,4), orbits of size 7)",
                   "best": r.get("best"), "file": os.path.relpath(p, ROOT),
                   "verified": verify(p)["size"] if os.path.exists(p) else None})
    p = "/tmp/shannon_s1_tabu106.txt"
    r = run([S("scripts", "s1_ils"), "7", "4", "--anneal", "106", "--seconds", "120",
             "--seed", "3", "--out", p, "--json"])
    ladder.append({"engine": "E2 fixed-cardinality tabu", "best": 106 if r.get("reached") else None,
                   "file": p, "verified": verify(p)["size"] if os.path.exists(p) else None})
    p107 = S("sets", "C7_d4_107_tabu_window.txt")
    r = run([S("scripts", "s1_ils"), "7", "4", "--anneal", "107", "--seconds", "300",
             "--seed", "9", "--out", p107, "--json"], env={"WREP": 200, "WLO": 4, "WHI": 5})
    ladder.append({"engine": "E2 tabu + E4 exact window repair", "best": 107 if r.get("reached") else None,
                   "file": os.path.relpath(p107, ROOT),
                   "verified": verify(p107)["size"] if os.path.exists(p107) else None})
    p108 = S("sets", "C7_d4_108_tabu_window.txt")
    r108, seeds_used = None, []
    for sd in (2, 3, 4, 6, 7, 11, 12):
        seeds_used.append(sd)
        r108 = run([S("scripts", "s1_ils"), "7", "4", "--anneal", "108", "--seconds", "300",
                    "--seed", str(sd), "--start", p107, "--out", p108, "--json"],
                   env={"WREP": 500, "WLO": 4, "WHI": 5})
        if r108.get("reached"):
            break
    ladder.append({"engine": "E2 tabu + E4, warm started from the 107", "best": 108 if r108.get("reached") else None,
                   "conflicts_left": r108.get("conflicts_left"), "seeds_tried": seeds_used,
                   "file": os.path.relpath(p108, ROOT) if os.path.exists(p108) else None,
                   "verified": verify(p108, ["--both", "--maximal"])["size"] if os.path.exists(p108) else None})
    rep["G5_ladder"] = ladder
    best4 = max([x["verified"] for x in ladder if x.get("verified")] or [0])
    rep["G5_best_verified_alpha_C7_d4"] = best4
    rep["G5_target"] = 108
    rep["G5_pass"] = best4 >= 108

    rep["gate_blocking_condition"] = {
        "requirement": "alpha(C_7^3) = 33 must be found, else Stage 1 does not begin",
        "met": rep["G1_pass"] and rep["G3_pass"],
    }
    rep["all_pass"] = bool(rep["G1_pass"] and rep["G2_mutant"]["pass"] and rep["G3_pass"]
                           and rep["G4_pass"] and rep["G5_pass"])
    with open(S("results", "json", "s1_gate.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps({k: v for k, v in rep.items()
                      if k.endswith("pass") or k.startswith("G5_best") or k == "gate_blocking_condition"},
                     indent=2))


if __name__ == "__main__":
    main()

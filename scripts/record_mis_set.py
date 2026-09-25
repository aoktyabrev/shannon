"""The set that `scripts/mis` returns for C_7^3 is put through the verifier like any
other set, and the verdict is recorded next to the solver's own claim.  A solver that
reported a size its output does not support would be caught here."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from setio import ROOT, verify, write_set  # noqa: E402

p = os.path.join(ROOT, "results", "json", "mis_c7_d3.json")
d = json.load(open(p))
out = write_set(os.path.join(ROOT, "sets", "C7_d3_%d_mis.txt" % d["best_found"]), d["n"],
                [tuple(x) for x in d["set"]], [
                    "Independent set of size %d in C_7^{boxtimes 3}, found by scripts/mis under a"
                    % d["best_found"],
                    "%.0f s ceiling.  Optimality NOT proved: the literature value is"
                    % d["time_limit"],
                    "alpha(C_7^{boxtimes 3}) = 33 (Baumert et al., cited through SOURCES.md PS19-4).",
                    "Kept as the honest record of an attempt that did not close.",
                ])
d["set_file"] = os.path.relpath(out, ROOT)
d["verified"] = verify(out, ["--both"])
d["reaches_literature_value_33"] = d["best_found"] == 33
json.dump(d, open(p, "w"), indent=2)
print(json.dumps({k: v for k, v in d.items() if k != "set"}, indent=2))

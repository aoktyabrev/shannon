"""Write the data tables of the merged paper from results/json, so that no number in a table
is typed by hand.  scripts/j_checknums.py re-runs this and requires the files to be unchanged."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
J = os.path.join(os.path.dirname(HERE), "results", "json")
s22 = json.load(open(os.path.join(J, "s2_2.json")))
s23 = json.load(open(os.path.join(J, "s2_3.json")))

NAMES = {
    "sets/C7_d5_343_linear.txt": "linear code \\cite{baumert1971}",
    "sets/C7_d5_350_mathew_ostergard.txt": "Mathew--\\\"Osterg{\\aa}rd \\cite{mathew2017}",
    "sets/C7_d5_363_aux_for_t9.txt": "auxiliary-set search, $t=9$",
    "sets/C7_d5_365_aux_for_t10.txt": "repaired auxiliary set, $t=10$",
    "sets/C7_d5_366_aux_for_t9.txt": "repaired auxiliary set, $t=9$",
    "sets/C7_d5_367_polak_schrijver.txt": "$I_0$, as printed \\cite{polak2019}",
    "sets/C7_d5_367_reproduced.txt": "$I_0$, our rebuild",
    "sets/C7_d5_367_best_t_from_pipeline.txt": "pipeline, best",
    "sets/C7_d5_367_auxiliary_X.txt": "$X$ of \\cite{gao2026}, as a code",
    "sets/C7_d5_367_auxiliary_X_best.txt": "ten-candidate code",
    "sets/C7_d5_367_auxiliary_X_o322.txt": "$o=322$ auxiliary set",
}


def name(f):
    if f in NAMES:
        return NAMES[f]
    if "pipeline_0" in f:
        return "pipeline code " + f.split("pipeline_0")[1][0]
    return f


def codes():
    rows = []
    for r in s22["population"]:
        wh = ", ".join(f"{n}" for n in r["weight_hist"][1:])
        fr = f"{r['F_min']}--{r['F_max']}" if r["F_min"] else "--"
        rows.append(f"{name(r['file'])} & {r['size']} & {r['candidates']} & {r['t_star']} & "
                    f"{r['configurations_at_t_star']} & {fr} & {wh} \\\\")
    return ("\\begin{table}[t]\n\\centering\\footnotesize\\setlength{\\tabcolsep}{3pt}\n\\begin{tabular}{@{}lrrrrrl@{}}\n\\toprule\n"
            "code & size & cand. & $t^*$ & colourings & $|F|$ at $t^*$ & by $k=1,\\dots,5$ \\\\\n"
            "\\midrule\n" + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n"
            "\\caption{The candidate count of every code we hold in $C_7^{\\boxtimes 5}$. Candidates are the "
            "vertices with exactly one neighbour in the code; $t^*$ is the largest usable family "
            "(Corollary~\\ref{cor:bip}); colourings are counted up to exchanging $\\PH$ and $\\PV$; $|F|$ "
            "ranges over them. Exhaustive for each file.}\n\\label{tab:codes}\n\\end{table}\n")


def shapes():
    real = {r["k"]: r["largest_size"] for r in s23["realisability"]}
    rows = []
    for o in sorted(s23["shapes"]["orbits"], key=lambda o: o["k"]):
        k = o["k"]
        rows.append(f"{k} & {o['size']} & {o['forbidden_by_one_pair']} & {o['penalised_by_one_pair']} & "
                    f"{2 ** (5 - k)} & {real[k]} \\\\")
    return ("\\begin{table}[t]\n\\centering\\small\n\\begin{tabular}{@{}crrrrr@{}}\n\\toprule\n"
            "$k$ & shapes & $|N(r)\\cap N(q)|$ & $|N(r)\\cup N(q)|$ & covered cells & largest set \\\\\n"
            " & & (forbidden) & (penalised) & in box$(q)$ & found \\\\\n\\midrule\n"
            + "\n".join(rows) + "\n\\bottomrule\n\\end{tabular}\n"
            "\\caption{The five shapes of a private pair in $C_7^{\\boxtimes 5}$, by the number $k$ of "
            "non-zero coordinates of $q-r$. The first four columns are counted directly; the last is the "
            "largest independent set the exhaustive local construction of Section~\\ref{sec:shapes} "
            "produced carrying a private pair of that shape.}\n\\label{tab:shapes}\n\\end{table}\n")


def main():
    out = {"tab-codes.tex": codes(), "tab-shapes.tex": shapes()}
    check = "--check" in sys.argv
    bad = 0
    for fn, txt in out.items():
        p = os.path.join(HERE, fn)
        if check:
            same = os.path.exists(p) and open(p).read() == txt
            print(("ok      " if same else "DIFFERS ") + fn)
            bad += not same
        else:
            open(p, "w").write(txt)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

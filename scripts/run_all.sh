#!/usr/bin/env bash
# Full reproduction of Stage 0, from an empty checkout.  No search runs.
# Requirements: gcc, python3 (no packages), curl; nvcc optional (S0.4 GPU column).
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-python3}

scripts/build.sh

# Rule 0: dump the sources, then check every quotation in SOURCES.md against them.
for id in 1808.07438 1504.01472 2607.21517 2607.27869 2607.29681 2608.30273; do
    scripts/fetch_arxiv.sh "$id" > /dev/null
done
$PY scripts/check_sources.py

# S0.2 -- reproductions (each verifies its own output and fails loudly on a mismatch)
$PY scripts/construct_c7_d5_ps.py   > /dev/null   # 367 from the circular graph, ~3 s
$PY scripts/construct_c7_d5_343.py  > /dev/null   # linear 7^3 = 343, ~5 s
$PY scripts/construct_c7_d10.py     > /dev/null   # 134753 in C_7^10, ~1 s
$PY scripts/gadget.py               > /dev/null   # base gadget + the record recursion, ~20 s

# S0.1 -- anti-vacuum calibration of the verifier (~3.5 min)
$PY scripts/calibrate.py

# alpha(C_7^3): exact attempt with a one-hour ceiling; reports honestly if it does not close
scripts/mis 7 3 3600 --json > results/json/mis_c7_d3.json || true
$PY scripts/record_mis_set.py > /dev/null

# S0.3 -- the upper-bound side, recomputed
$PY scripts/theta.py > /dev/null

# S0.4 -- budget and hardware (~3 min; writes its benchmark sets to $SHANNON_TMP)
$PY scripts/bench.py > /dev/null

# is the record still where we think it is?
$PY scripts/litcheck.py

# ---- Stage 1 ----------------------------------------------------------------
# The gate first: the stack must find alpha(C_7^3) = 33 and alpha(C_7^4) >= 108
# before it is pointed at the ninth private pair.  ~25 min.
$PY scripts/s1_gate.py

# S1.1 anchoring: our recursion must reproduce the published bound exactly, and
# the framework gap against Tandon is computed here.
$PY scripts/s1_anchor.py > /dev/null

# S1.2 the search itself.
$PY scripts/s1_pairs.py > /dev/null          # candidate private pairs, exact maximum t
$PY scripts/s1_codes.py > /dev/null          # branch C: every 367-code the pipeline gives (~5 min)
AUXSRC=""; for f in sets/pipeline_codes/*.txt; do AUXSRC="$AUXSRC --source $f"; done
scripts/s1_aux sets/C7_d5_367_polak_schrijver.txt $AUXSRC \
    --dump "${SHANNON_TMP:-/tmp/shannon-aux}/near_misses.txt" --dump-max 4 --json \
    > results/json/s1_aux.json                # branch B: 8.3e9 group elements (~10 min, 8 threads)
$PY scripts/s1_repair.py "${SHANNON_TMP:-/tmp/shannon-aux}/near_misses.txt" > /dev/null
S1_AUX_SECONDS=${S1_AUX_SECONDS:-1500} $PY scripts/s1_auxrun.py > /dev/null   # ~25 min

$PY scripts/litcheck.py stage1-end > /dev/null
$PY scripts/s1_budget.py > /dev/null

# ---- Stage 2W: the note -----------------------------------------------------
# No search here.  The gate, the data the note prints, the venue's rules, and the
# reconciliation of every number in the note against results/json.
$PY scripts/litcheck.py writeup-gate > /dev/null
scripts/fetch_venue.sh > /dev/null
$PY scripts/w_gate.py    > /dev/null
$PY scripts/w_theorem.py > /dev/null
$PY scripts/w_venue.py   > /dev/null
if command -v pdflatex > /dev/null; then
    (cd note && pdflatex -interaction=nonstopmode note.tex > /dev/null \
             && pdflatex -interaction=nonstopmode note.tex > /dev/null)
else
    echo "pdflatex not found: note/note.pdf not rebuilt (nothing else depends on it)"
fi
$PY scripts/w_checknums.py

(cd sets && sha256sum *.txt > SHA256SUMS)
$PY scripts/make_results.py

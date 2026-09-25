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

# S0.3 -- the upper-bound side, recomputed
$PY scripts/theta.py > /dev/null

# S0.4 -- budget and hardware (~3 min; writes its benchmark sets to $SHANNON_TMP)
$PY scripts/bench.py > /dev/null

# is the record still where we think it is?
$PY scripts/litcheck.py

$PY scripts/make_results.py

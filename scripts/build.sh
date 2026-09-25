#!/usr/bin/env bash
# Everything this project needs: a C compiler, nvcc (optional, for S0.4 only) and a
# bare Python 3.  No packages are installed, nothing is carried over from other projects.
set -euo pipefail
cd "$(dirname "$0")"
CC=${CC:-gcc}
$CC -O2 -march=native -o verify verify.c
$CC -O2 -march=native -DMUTANT_DUPLICATES_ONLY -o verify_mutant verify.c
$CC -O2 -march=native -o mis mis.c
if command -v nvcc >/dev/null 2>&1; then
    nvcc -O3 -o verify_gpu verify_gpu.cu
else
    echo "nvcc not found: skipping verify_gpu (S0.4 will report the CPU numbers only)" >&2
fi
echo "built: verify verify_mutant mis $( [ -x verify_gpu ] && echo verify_gpu )"

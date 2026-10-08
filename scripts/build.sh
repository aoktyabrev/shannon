#!/usr/bin/env bash
# Everything this project needs: a C compiler, nvcc (optional, for S0.4 only) and a
# bare Python 3.  No packages are installed, nothing is carried over from other projects.
set -euo pipefail
cd "$(dirname "$0")"
CC=${CC:-gcc}
$CC -O2 -march=native -o verify verify.c
$CC -O2 -march=native -DMUTANT_DUPLICATES_ONLY -o verify_mutant verify.c
$CC -O2 -march=native -o mis mis.c
# Stage 1 search stack
$CC -O2 -march=native -o s1_alpha3 s1_alpha3.c
$CC -O2 -march=native -o s1_ils s1_ils.c -lm
$CC -O2 -march=native -o s1_sym s1_sym.c
$CC -O2 -march=native -o s1_lns s1_lns.c
$CC -O2 -march=native -fopenmp -o s1_aux s1_aux.c
$CC -O2 -march=native -o s1_auxsearch s1_auxsearch.c
# Stage 2.2
$CC -O2 -march=native -o s2_2_conf s2_2_conf.c
$CC -O2 -march=native -fopenmp -o s2_2_aut s2_2_aut.c
$CC -O2 -march=native -fopenmp -DMAXI=2048 -o s2_2_aut_big s2_2_aut.c
$CC -O2 -march=native -fopenmp -o s2_2_sweep s2_2_sweep.c
if command -v nvcc >/dev/null 2>&1; then
    nvcc -O3 -o verify_gpu verify_gpu.cu
else
    echo "nvcc not found: skipping verify_gpu (S0.4 will report the CPU numbers only)" >&2
fi
echo "built: verify verify_mutant mis s1_alpha3 s1_ils s1_sym s1_lns s1_aux s1_auxsearch s2_2_conf s2_2_aut s2_2_aut_big s2_2_sweep$( [ -x verify_gpu ] && echo ' verify_gpu' )"

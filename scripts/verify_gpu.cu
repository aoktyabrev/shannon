/*
 * S0.4: the same exact box-packing sweep as scripts/verify.c, on the GPU.
 *
 * One thread per vertex; each thread walks the 2^d cells of its box in Gray-code
 * order and claims them with atomicOr on a bitmap in global memory.  A cell that
 * was already claimed increments a collision counter.  Atomics make this exactly
 * as exact as the CPU version -- the two must return the same verdict, and
 * scripts/bench.py requires that they do.
 *
 * Build: nvcc -O3 -o verify_gpu verify_gpu.cu
 */
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <ctime>

#define MAXD 40
#define CUDA_OK(x) do { cudaError_t e = (x); if (e != cudaSuccess) { \
    fprintf(stderr, "cuda error %s at line %d\n", cudaGetErrorString(e), __LINE__); exit(2);} } while (0)

static double now() { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

__global__ void sweep(const unsigned char *v, long long size, int n, int d,
                      const unsigned long long *pw, unsigned int *bits,
                      unsigned long long *collisions) {
    long long k = blockIdx.x * (long long)blockDim.x + threadIdx.x;
    if (k >= size) return;
    const unsigned char *x = v + k * d;
    unsigned long long base = 0;
    long long up[MAXD];
    for (int i = 0; i < d; i++) {
        base += (unsigned long long)x[i] * pw[i];
        up[i] = (x[i] == n - 1) ? -(long long)(n - 1) * (long long)pw[i] : (long long)pw[i];
    }
    unsigned long long cur = base, g = 0, mask = 1ULL << d;
    for (unsigned long long m = 0; m < mask; m++) {
        if (m) {
            unsigned long long ng = m ^ (m >> 1), diff = ng ^ g;
            int bit = __ffsll((long long)diff) - 1;
            cur = (ng & diff) ? cur + up[bit] : cur - up[bit];
            g = ng;
        }
        unsigned int word = (unsigned int)(cur >> 5);
        unsigned int bm = 1u << (cur & 31);
        unsigned int old = atomicOr(&bits[word], bm);
        if (old & bm) atomicAdd(collisions, 1ULL);
    }
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: verify_gpu <file> [--json] [--repeat R]\n"); return 2; }
    int as_json = 0, repeat = 1;
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--json")) as_json = 1;
        else if (!strcmp(argv[i], "--repeat") && i + 1 < argc) repeat = atoi(argv[++i]);
    }
    FILE *f = fopen(argv[1], "r");
    if (!f) { fprintf(stderr, "cannot open %s\n", argv[1]); return 2; }
    char line[1 << 16];
    int n = 0, d = 0, have = 0; long long size = 0, got = 0;
    unsigned char *v = NULL;
    while (fgets(line, sizeof line, f)) {
        char *p = line; while (*p == ' ' || *p == '\t') p++;
        if (*p == '#' || *p == '\n' || *p == '\r' || !*p) continue;
        if (!have) { sscanf(p, "%d %d %lld", &n, &d, &size); v = (unsigned char *)malloc((size_t)size * d); have = 1; continue; }
        for (int i = 0; i < d; i++) { while (*p == ' ') p++; v[(size_t)got * d + i] = (unsigned char)strtol(p, &p, 10); }
        got++;
    }
    fclose(f);
    if (got != size) { fprintf(stderr, "size mismatch\n"); return 2; }

    unsigned long long pw[MAXD], U = 1;
    for (int i = 0; i < d; i++) { pw[i] = U; U *= (unsigned)n; }

    cudaDeviceProp prop; CUDA_OK(cudaGetDeviceProperties(&prop, 0));
    size_t words = (size_t)((U + 31) / 32);
    unsigned char *dv; unsigned long long *dpw, *dcol; unsigned int *dbits;
    CUDA_OK(cudaMalloc(&dv, (size_t)size * d));
    CUDA_OK(cudaMalloc(&dpw, sizeof pw));
    CUDA_OK(cudaMalloc(&dcol, 8));
    CUDA_OK(cudaMalloc(&dbits, words * 4));
    CUDA_OK(cudaMemcpy(dv, v, (size_t)size * d, cudaMemcpyHostToDevice));
    CUDA_OK(cudaMemcpy(dpw, pw, sizeof pw, cudaMemcpyHostToDevice));

    double best = 1e30; unsigned long long col = 0;
    for (int r = 0; r < repeat; r++) {
        CUDA_OK(cudaMemset(dbits, 0, words * 4));
        CUDA_OK(cudaMemset(dcol, 0, 8));
        CUDA_OK(cudaDeviceSynchronize());
        double t0 = now();
        int threads = 256;
        long long blocks = (size + threads - 1) / threads;
        sweep<<<(int)blocks, threads>>>(dv, size, n, d, dpw, dbits, dcol);
        CUDA_OK(cudaDeviceSynchronize());
        double el = now() - t0;
        if (el < best) best = el;
        CUDA_OK(cudaMemcpy(&col, dcol, 8, cudaMemcpyDeviceToHost));
    }
    long long cells = size << d;
    if (as_json) {
        printf("{\"device\":\"%s\",\"n\":%d,\"d\":%d,\"size\":%lld,\"universe\":%llu,"
               "\"bitmap_bytes\":%zu,\"independent\":%s,\"collisions\":%llu,"
               "\"kernel_seconds\":%.6f,\"cells\":%lld,\"cells_per_second\":%.0f,"
               "\"vertices_per_second\":%.0f}\n",
               prop.name, n, d, size, U, words * 4, col == 0 ? "true" : "false", col,
               best, cells, cells / best, size / best);
    } else {
        printf("device     : %s\n", prop.name);
        printf("graph      : C_%d^%d, %lld vertices, bitmap %.1f MiB\n", n, d, size, words * 4 / 1048576.0);
        printf("result     : %s (%llu collisions)\n", col == 0 ? "INDEPENDENT" : "NOT INDEPENDENT", col);
        printf("kernel     : %.4f s, %.3g cells/s\n", best, cells / best);
    }
    return col == 0 ? 0 : 1;
}

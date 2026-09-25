/*
 * Exact independence number of C_n^{boxtimes d} by branch and bound.
 *
 * Used only for the trivial calibration cases (d = 1, 2 and an attempt at d = 3).
 * This is NOT a search tool for new bounds: it either proves the exact optimum or
 * it is stopped by the time limit and reports that it did not finish.
 *
 * Bound: a greedy clique cover of the candidate set.  Cliques of C_n^{boxtimes d}
 * are the 2^d boxes prod_i {x_i, x_i+1}, so a partition of the candidates into
 * cliques bounds how many of them a single independent set can contain.
 *
 * Build: cc -O2 -o mis mis.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

static int N, D, NV, W;
static uint64_t *adj;          /* NV x W closed-neighbourhood bitsets (excluding self) */
static int best;
static int *bestset, *cur, curn;
static double t_start, t_limit;
static int timed_out;

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+1e-9*t.tv_nsec; }
#define BIT(v) (1ULL << ((v) & 63))
#define WRD(v) ((v) >> 6)

static int popcnt(const uint64_t *a) { int c = 0; for (int i = 0; i < W; i++) c += __builtin_popcountll(a[i]); return c; }

/* greedy clique cover of `cand`; returns the number of cliques used */
static int bound_clique_cover(const uint64_t *cand, uint64_t *scratch) {
    memcpy(scratch, cand, (size_t)W * 8);
    int cliques = 0;
    for (;;) {
        int v = -1;
        for (int i = 0; i < W && v < 0; i++) if (scratch[i]) v = i * 64 + __builtin_ctzll(scratch[i]);
        if (v < 0) break;
        cliques++;
        /* grow a clique greedily inside scratch starting at v */
        uint64_t *common = scratch + W;   /* caller gives 2*W words */
        for (int i = 0; i < W; i++) common[i] = scratch[i] & adj[(size_t)v * W + i];
        scratch[WRD(v)] &= ~BIT(v);
        for (;;) {
            int u = -1;
            for (int i = 0; i < W && u < 0; i++) if (common[i]) u = i * 64 + __builtin_ctzll(common[i]);
            if (u < 0) break;
            scratch[WRD(u)] &= ~BIT(u);
            for (int i = 0; i < W; i++) common[i] &= adj[(size_t)u * W + i];
        }
    }
    return cliques;
}

static void expand(uint64_t *cand, int depth) {
    if (timed_out) return;
    if ((depth & 15) == 0 && now() - t_start > t_limit) { timed_out = 1; return; }
    int nc = popcnt(cand);
    if (nc == 0) {
        if (curn > best) { best = curn; memcpy(bestset, cur, sizeof(int) * curn); }
        return;
    }
    uint64_t *scratch = malloc((size_t)W * 8 * 2);
    int ub = bound_clique_cover(cand, scratch);
    free(scratch);
    if (curn + ub <= best) return;

    /* branch on the candidate with the most candidate neighbours */
    int piv = -1, pd = -1;
    for (int i = 0; i < W; i++) {
        uint64_t m = cand[i];
        while (m) {
            int v = i * 64 + __builtin_ctzll(m); m &= m - 1;
            int dg = 0;
            for (int j = 0; j < W; j++) dg += __builtin_popcountll(cand[j] & adj[(size_t)v * W + j]);
            if (dg > pd) { pd = dg; piv = v; }
        }
    }
    uint64_t *sub = malloc((size_t)W * 8);
    /* take piv */
    for (int i = 0; i < W; i++) sub[i] = cand[i] & ~adj[(size_t)piv * W + i];
    sub[WRD(piv)] &= ~BIT(piv);
    cur[curn++] = piv;
    expand(sub, depth + 1);
    curn--;
    /* drop piv */
    memcpy(sub, cand, (size_t)W * 8);
    sub[WRD(piv)] &= ~BIT(piv);
    expand(sub, depth + 1);
    free(sub);
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: mis n d [seconds] [--json]\n"); return 2; }
    N = atoi(argv[1]); D = atoi(argv[2]);
    t_limit = argc > 3 ? atof(argv[3]) : 600.0;
    int as_json = 0;
    for (int i = 3; i < argc; i++) if (!strcmp(argv[i], "--json")) as_json = 1;
    NV = 1; for (int i = 0; i < D; i++) NV *= N;
    W = (NV + 63) / 64;
    adj = calloc((size_t)NV * W, 8);
    int *co = malloc(sizeof(int) * D);
    for (int u = 0; u < NV; u++) {
        int t = u; for (int i = 0; i < D; i++) { co[i] = t % N; t /= N; }
        for (int v = 0; v < NV; v++) {
            if (v == u) continue;
            int t2 = v, ok = 1;
            for (int i = 0; i < D && ok; i++) {
                int c = t2 % N; t2 /= N;
                int dd = c - co[i]; if (dd < 0) dd = -dd; if (dd > N - dd) dd = N - dd;
                if (dd > 1) ok = 0;
            }
            if (ok) adj[(size_t)u * W + WRD(v)] |= BIT(v);
        }
    }
    bestset = malloc(sizeof(int) * NV); cur = malloc(sizeof(int) * NV);
    uint64_t *cand = calloc(W, 8);
    for (int v = 0; v < NV; v++) cand[WRD(v)] |= BIT(v);
    best = 0; curn = 0; timed_out = 0; t_start = now();
    expand(cand, 0);
    double el = now() - t_start;
    if (as_json) {
        printf("{\"n\":%d,\"d\":%d,\"vertices\":%d,\"best_found\":%d,\"proved_optimal\":%s,"
               "\"seconds\":%.3f,\"time_limit\":%.1f,\"set\":[", N, D, NV, best,
               timed_out ? "false" : "true", el, t_limit);
        for (int i = 0; i < best; i++) {
            int t = bestset[i];
            printf("%s[", i ? "," : "");
            for (int j = 0; j < D; j++) { printf("%s%d", j ? "," : "", t % N); t /= N; }
            printf("]");
        }
        printf("]}\n");
    } else {
        printf("C_%d^%d: %d vertices, best found %d, %s, %.3f s\n",
               N, D, NV, best, timed_out ? "TIME LIMIT (not proved optimal)" : "proved optimal", el);
    }
    return 0;
}

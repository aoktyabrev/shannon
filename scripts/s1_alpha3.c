/*
 * Engine E1 of the Stage 1 search stack: exact cyclic layer search for
 * alpha(C_n^{boxtimes 3}).  Stage 0's generic branch and bound reached 32 on this
 * graph in an hour and proved nothing; this engine settles it in seconds.
 *
 * Decomposition.  Write a vertex as (u,i), u in Z_n^2, i in Z_n, and let L_i be
 * the i-th layer.  Vertices in layers i and j are adjacent iff |i-j| <= 1 (mod n)
 * and they are adjacent-or-equal in C_n^{boxtimes 2}.  So I is independent iff
 *
 *     L_i union L_{i+1} is independent in C_n^{boxtimes 2},  cyclically,
 *
 * hence m_i + m_{i+1} <= A, where A = alpha(C_n^{boxtimes 2}) and m_i = |L_i|.
 *
 * Size arithmetic.  Cutting the cycle at any index i leaves P = (n-1)/2 disjoint
 * consecutive pairs, so Sigma <= m_i + P*A for every i, i.e. m_i >= Sigma - P*A;
 * and min_i m_i <= floor(Sigma/n).  When
 *
 *     Sigma - P*A  ==  floor(Sigma/n)                              (*)
 *
 * the smallest layer is pinned to exactly that value and, at its index, the P
 * remaining pairs each sum to exactly A -- that is, each is a *maximum*
 * independent set of C_n^{boxtimes 2}.  There are few of those (980 for n = 7),
 * so every layer but the smallest is a half of a maximum 2-dimensional packing,
 * and the existence question becomes pure reachability round the cycle.
 *
 * (*) is checked, not assumed.  When it fails for a given Sigma the engine says so
 * and claims nothing: finding a cycle still proves alpha >= Sigma, but failing to
 * find one proves nothing.  That asymmetry is what the positive control uses.
 *
 * --open-nbhd compiles the same search with the *open* neighbourhood, i.e. having
 * forgotten that consecutive layers must also be disjoint.  That is a defect, and
 * scripts/s1_gate.py requires it to produce a wrong answer.
 *
 * Build: cc -O2 -o s1_alpha3 s1_alpha3.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

static int N = 7, NC, OPEN_NBHD = 0;
static uint64_t clos[64];

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+1e-9*t.tv_nsec; }
static int pc(uint64_t m) { return __builtin_popcountll(m); }
static uint64_t nbhd(uint64_t s) {
    uint64_t r = 0;
    while (s) { int v = __builtin_ctzll(s); s &= s-1; r |= clos[v]; }
    if (OPEN_NBHD) r &= ~s;                    /* the defect: see the header */
    return r;
}
static uint64_t nbhd_of_set(uint64_t s) {
    uint64_t r = 0, t = s;
    while (t) { int v = __builtin_ctzll(t); t &= t-1; r |= clos[v]; }
    if (OPEN_NBHD) r &= ~s;
    return r;
}

static uint64_t *maxis; static long n_maxis, cap_maxis;
static void rec_max(int start, uint64_t avail, uint64_t cur, int size, int target) {
    if (size == target) {
        if (n_maxis == cap_maxis) { cap_maxis = cap_maxis ? cap_maxis*2 : 1024; maxis = realloc(maxis, cap_maxis*8); }
        maxis[n_maxis++] = cur; return;
    }
    if (size + pc(avail) < target) return;
    uint64_t m = avail >> start;
    for (int v = start; m; m >>= 1, v++)
        if (m & 1) rec_max(v+1, avail & ~clos[v], cur | (1ULL<<v), size+1, target);
}

static uint64_t *isk; static long n_isk, cap_isk;
static void rec_isk(int start, uint64_t avail, uint64_t cur, int size, int target) {
    if (size == target) {
        if (n_isk == cap_isk) { cap_isk = cap_isk ? cap_isk*2 : 1024; isk = realloc(isk, cap_isk*8); }
        isk[n_isk++] = cur; return;
    }
    if (size + pc(avail) < target) return;
    uint64_t m = avail >> start;
    for (int v = start; m; m >>= 1, v++)
        if (m & 1) rec_isk(v+1, avail & ~clos[v], cur | (1ULL<<v), size+1, target);
}

static uint64_t *key; static int32_t n_key;
static uint64_t *keyN;
static int32_t *comp_off, *comp_val, *succ_off, *succ_val;

static int cmp64(const void *a, const void *b) {
    uint64_t x = *(const uint64_t*)a, y = *(const uint64_t*)b;
    return x < y ? -1 : x > y ? 1 : 0;
}
static int32_t key_find(uint64_t m) {
    int32_t lo = 0, hi = n_key-1;
    while (lo <= hi) { int32_t mid = (lo+hi)/2;
        if (key[mid] == m) return mid;
        if (key[mid] < m) lo = mid+1; else hi = mid-1; }
    return -1;
}

static int (*perm)[64]; static int n_perm;
static void build_perms(void) {
    n_perm = 0; perm = malloc(sizeof(int[64]) * 2*2*N*2*N);
    for (int sw = 0; sw < 2; sw++)
      for (int rx = 0; rx < 2; rx++) for (int tx = 0; tx < N; tx++)
        for (int ry = 0; ry < 2; ry++) for (int ty = 0; ty < N; ty++) {
            int *p = perm[n_perm];
            for (int x = 0; x < N; x++) for (int y = 0; y < N; y++) {
                int a = (((rx ? -x : x) % N) + N + tx) % N;
                int b = (((ry ? -y : y) % N) + N + ty) % N;
                p[x*N+y] = sw ? b*N+a : a*N+b;
            }
            n_perm++;
        }
}
static uint64_t canon(uint64_t s) {
    uint64_t best = ~0ULL;
    for (int i = 0; i < n_perm; i++) {
        uint64_t r = 0, t = s;
        while (t) { int v = __builtin_ctzll(t); t &= t-1; r |= 1ULL << perm[i][v]; }
        if (r < best) best = r;
    }
    return best;
}

static uint8_t *inS, *inT;
static int P_PAIRS;
static uint64_t cyc[32];

/* depth-first reconstruction of an actual cycle, used once reachability says one exists */
static int dfs_cycle(int block, uint64_t prev_tail, uint64_t F0) {
    if (block == P_PAIRS) return !(prev_tail & F0) || block == 0;
    uint64_t Fp = nbhd_of_set(prev_tail);
    for (int32_t j = 0; j < n_key; j++) {
        if (key[j] & Fp) continue;
        for (int32_t c = comp_off[j]; c < comp_off[j+1]; c++) {
            uint64_t tail = key[comp_val[c]];
            if (block == P_PAIRS-1 && (tail & F0)) continue;
            cyc[2*block+1] = key[j]; cyc[2*block+2] = tail;
            if (dfs_cycle(block+1, tail, F0)) return 1;
        }
    }
    return 0;
}

int main(int argc, char **argv) {
    int as_json = 0, want_m0 = -1, emit_witness = 0;
    const char *witness_file = NULL;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--json")) as_json = 1;
        else if (!strcmp(argv[i], "--n") && i+1 < argc) N = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--m0") && i+1 < argc) want_m0 = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--open-nbhd")) OPEN_NBHD = 1;
        else if (!strcmp(argv[i], "--witness") && i+1 < argc) { emit_witness = 1; witness_file = argv[++i]; }
    }
    NC = N*N; P_PAIRS = (N-1)/2;
    if (NC > 64) { fprintf(stderr, "layer too large\n"); return 2; }
    for (int x = 0; x < N; x++) for (int y = 0; y < N; y++) {
        uint64_t m = 0;
        for (int dx = -1; dx <= 1; dx++) for (int dy = -1; dy <= 1; dy++)
            m |= 1ULL << ((((x+dx)%N+N)%N)*N + (((y+dy)%N+N)%N));
        clos[x*N+y] = m;
    }
    double t0 = now();
    int A = 0;
    for (int k = NC; k >= 1; k--) { n_maxis = 0; rec_max(0, (~0ULL)>>(64-NC), 0, 0, k); if (n_maxis) { A = k; break; } }
    long n_max_packings = n_maxis;

    int lo_sz = 1, hi_sz = A-1;
    if (want_m0 >= 0) { lo_sz = 1; hi_sz = A-1; }
    long capk = 1<<20; uint64_t *raw = malloc(capk*8); long n_raw = 0;
    for (long i = 0; i < n_maxis; i++) {
        uint64_t M = maxis[i]; int cells[32], nc = 0; uint64_t s = M;
        while (s) { cells[nc++] = __builtin_ctzll(s); s &= s-1; }
        for (uint32_t sub = 1; sub < (1u<<nc)-1; sub++) {
            int k = __builtin_popcount(sub);
            if (k < lo_sz || k > hi_sz) continue;
            uint64_t m = 0;
            for (int b = 0; b < nc; b++) if (sub>>b&1) m |= 1ULL<<cells[b];
            if (n_raw == capk) { capk *= 2; raw = realloc(raw, capk*8); }
            raw[n_raw++] = m;
        }
    }
    qsort(raw, n_raw, 8, cmp64);
    key = malloc(n_raw*8); n_key = 0;
    for (long i = 0; i < n_raw; i++) if (!i || raw[i] != raw[i-1]) key[n_key++] = raw[i];
    free(raw);
    keyN = malloc((size_t)n_key*8);
    for (int32_t i = 0; i < n_key; i++) keyN[i] = nbhd(key[i]);

    int32_t *cnt = calloc(n_key,4);
    for (int pass = 0; pass < 2; pass++) {
        if (pass) {
            comp_off = malloc(((size_t)n_key+1)*4); comp_off[0] = 0;
            for (int32_t i = 0; i < n_key; i++) comp_off[i+1] = comp_off[i] + cnt[i];
            comp_val = malloc((size_t)comp_off[n_key]*4);
            memset(cnt, 0, (size_t)n_key*4);
        }
        for (long i = 0; i < n_maxis; i++) {
            uint64_t M = maxis[i]; int cells[32], nc = 0; uint64_t s = M;
            while (s) { cells[nc++] = __builtin_ctzll(s); s &= s-1; }
            for (uint32_t sub = 1; sub < (1u<<nc)-1; sub++) {
                int k = __builtin_popcount(sub);
                if (k < lo_sz || k > hi_sz) continue;
                uint64_t m = 0;
                for (int b = 0; b < nc; b++) if (sub>>b&1) m |= 1ULL<<cells[b];
                int32_t ki = key_find(m);
                if (!pass) cnt[ki]++;
                else comp_val[comp_off[ki] + cnt[ki]++] = key_find(M & ~m);
            }
        }
    }
    long n_comp = comp_off[n_key];
    free(cnt);

    int32_t *sc = calloc(n_key,4);
    for (int32_t i = 0; i < n_key; i++) {
        uint64_t F = keyN[i]; int32_t c = 0;
        for (int32_t j = 0; j < n_key; j++) if (!(key[j] & F)) c++;
        sc[i] = c;
    }
    succ_off = malloc(((size_t)n_key+1)*4); succ_off[0] = 0;
    for (int32_t i = 0; i < n_key; i++) succ_off[i+1] = succ_off[i] + sc[i];
    long n_succ = succ_off[n_key];
    succ_val = malloc((size_t)n_succ*4);
    for (int32_t i = 0; i < n_key; i++) {
        uint64_t F = keyN[i]; int32_t c = succ_off[i];
        for (int32_t j = 0; j < n_key; j++) if (!(key[j] & F)) succ_val[c++] = j;
    }
    free(sc);
    build_perms();
    inS = malloc(n_key); inT = malloc(n_key);

    int m0_hi = 0;                       /* largest m0 with (*) satisfiable */
    for (int m = 0; m <= A; m++) { int S = m + P_PAIRS*A; if (m <= S/N) m0_hi = m; }
    int m0_from = want_m0 >= 0 ? want_m0 : m0_hi, m0_to = want_m0 >= 0 ? want_m0 : 0;

    long tested = 0, closed = 0; int closed_m0 = -1; uint64_t closed_L0 = 0;
    int decisive_floor = -1;             /* smallest Sigma proved impossible */
    for (int m0 = m0_from; m0 >= m0_to; m0--) {
        int Sigma = m0 + P_PAIRS*A;
        int decisive = (m0 == Sigma/N);
        n_isk = 0; rec_isk(0, (~0ULL)>>(64-NC), 0, 0, m0);
        uint64_t *canv = malloc((size_t)(n_isk?n_isk:1)*8);
        for (long i = 0; i < n_isk; i++) canv[i] = canon(isk[i]);
        qsort(canv, n_isk, 8, cmp64);
        uint64_t *rep = malloc((size_t)(n_isk?n_isk:1)*8); long n_rep = 0;
        for (long i = 0; i < n_isk; i++) if (!i || canv[i] != canv[i-1]) rep[n_rep++] = canv[i];
        free(canv);
        if (!as_json) fprintf(stderr, "m0 = %d (Sigma = %d, %s): %ld sets, %ld orbits\n",
                              m0, Sigma, decisive ? "decisive" : "NOT decisive", n_isk, n_rep);
        int found_here = 0;
        for (long r = 0; r < n_rep && !found_here; r++) {
            uint64_t L0 = rep[r], F0 = nbhd_of_set(L0);
            tested++;
            memset(inS, 0, n_key);
            for (int32_t j = 0; j < n_key; j++)
                if (!(key[j] & F0))
                    for (int32_t c = comp_off[j]; c < comp_off[j+1]; c++) inS[comp_val[c]] = 1;
            for (int step = 0; step < P_PAIRS-1; step++) {
                memset(inT, 0, n_key);
                for (int32_t i = 0; i < n_key; i++) if (inS[i])
                    for (int32_t e = succ_off[i]; e < succ_off[i+1]; e++) {
                        int32_t j = succ_val[e];
                        for (int32_t c = comp_off[j]; c < comp_off[j+1]; c++) inT[comp_val[c]] = 1;
                    }
                memcpy(inS, inT, n_key);
            }
            for (int32_t i = 0; i < n_key; i++)
                if (inS[i] && !(key[i] & F0)) { found_here = 1; closed++; closed_m0 = m0; closed_L0 = L0; break; }
        }
        free(rep);
        if (found_here) break;
        if (decisive) decisive_floor = Sigma;
    }
    double el = now() - t0;

    int witness_size = 0;
    if (closed_m0 >= 0 && emit_witness) {
        cyc[0] = closed_L0;
        if (dfs_cycle(0, closed_L0, nbhd_of_set(closed_L0))) {
            FILE *f = fopen(witness_file, "w");
            int tot = 0; for (int i = 0; i < N; i++) tot += pc(cyc[i]);
            fprintf(f, "# Independent set of size %d in C_%d^{boxtimes 3}, produced by the cyclic\n", tot, N);
            fprintf(f, "# layer search of scripts/s1_alpha3 (engine E1) as a positive control.\n");
            fprintf(f, "%d 3 %d\n", N, tot);
            for (int i = 0; i < N; i++) {
                uint64_t s = cyc[i];
                while (s) { int v = __builtin_ctzll(s); s &= s-1; fprintf(f, "%d %d %d\n", v/N, v%N, i); }
            }
            fclose(f);
            witness_size = tot;
        }
    }

    if (as_json)
        printf("{\"n\":%d,\"alpha_layer\":%d,\"maximum_packings\":%ld,\"keys\":%d,"
               "\"successor_edges\":%ld,\"complement_entries\":%ld,\"pairs\":%d,"
               "\"orbits_tested\":%ld,\"cycle_closed\":%s,\"closed_at_m0\":%d,"
               "\"closed_at_sigma\":%d,\"smallest_sigma_proved_impossible\":%d,"
               "\"alpha_d3_upper_bound\":%d,\"witness_size\":%d,\"open_nbhd_defect\":%s,"
               "\"seconds\":%.2f}\n",
               N, A, n_max_packings, n_key, n_succ, n_comp, P_PAIRS, tested,
               closed ? "true" : "false", closed_m0,
               closed_m0 >= 0 ? closed_m0 + P_PAIRS*A : -1,
               decisive_floor, decisive_floor > 0 ? decisive_floor - 1 : -1, witness_size,
               OPEN_NBHD ? "true" : "false", el);
    else {
        printf("alpha(C_%d^2) = %d, %ld maximum packings, %d keys, %ld successor edges\n",
               N, A, n_max_packings, n_key, n_succ);
        if (closed_m0 >= 0) printf("cycle closes at m0 = %d, Sigma = %d%s\n", closed_m0,
                                   closed_m0 + P_PAIRS*A, witness_size ? " (witness written)" : "");
        if (decisive_floor > 0) printf("Sigma >= %d proved impossible, so alpha(C_%d^3) <= %d\n",
                                       decisive_floor, N, decisive_floor - 1);
        printf("time: %.2f s\n", el);
    }
    return 0;
}

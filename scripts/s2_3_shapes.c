/*
 * Stage 2.3 -- the shapes a private pair can have.
 *
 *   s2_3_shapes costs                 for every d in {0,+-1}^5 \ {0}: |N[0] cap N[d]| counted
 *                                     on Z_7^5, and the orbits of the 242 shapes under the
 *                                     stabiliser of 0 in (D_7)^5 sd S_5 (perm and signs)
 *   s2_3_shapes cells CODE            shapes of the code's candidates, and the histogram of
 *                                     c(v) = covered cells in the box of v, v outside the code
 *   s2_3_shapes local CODE [--out DIR]
 *        for every word r and shape d, q = r + d: delete the other words adjacent to q, then
 *        add back a maximum independent set of the freed vertices not adjacent to q.  The
 *        pair (r, q) is then private.  Reports the largest size reached per k, and writes the
 *        first set reaching it.  Exact: the freed vertices of a maximal code lie next to the
 *        deleted words; vertices already free in a non-maximal code are included too.
 *
 * Build: cc -O2 -march=native -o s2_3_shapes s2_3_shapes.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define N 7
#define D 5
#define NV 16807
#define NB 243
#define MAXI 512
#define MAXF 256

static int pw[D] = {1, 7, 49, 343, 2401};
static int dig[NV][D], nbr[NV][NB];
static int enc(const int *c) { int v = 0; for (int i = 0; i < D; i++) v += c[i] * pw[i]; return v; }
static int adj_or_eq(int a, int b) {
    for (int i = 0; i < D; i++) { int t = (dig[a][i] - dig[b][i] + N) % N; if (t > 1 && t < N - 1) return 0; }
    return 1;
}
static int addv(int a, int b) { int c[D]; for (int i = 0; i < D; i++) c[i] = (dig[a][i] + dig[b][i]) % N; return enc(c); }
static int read_code(const char *path, int *out) {
    FILE *f = fopen(path, "r"); if (!f) return -1;
    char line[4096]; int have = 0, n = 0;
    while (fgets(line, sizeof line, f)) {
        char *p = line; while (*p == ' ' || *p == '\t') p++;
        if (*p == '#' || *p == '\n' || *p == '\r' || !*p) continue;
        if (!have) { have = 1; continue; }
        int c[D]; for (int i = 0; i < D; i++) c[i] = (int)strtol(p, &p, 10);
        out[n++] = enc(c);
    }
    fclose(f); return n;
}
/* shapes: d with coordinates in {0,1,6}, d != 0 */
static int shapes[242], kof[242], nsh;
static void make_shapes(void) {
    nsh = 0;
    for (int m = 0; m < NB; m++) { int mm = m, c[D], k = 0;
        for (int i = 0; i < D; i++) { int t = mm % 3 - 1; mm /= 3; c[i] = (t + N) % N; k += t != 0; }
        if (!k) continue; shapes[nsh] = enc(c); kof[nsh] = k; nsh++; }
}

/* exact maximum independent set on <= 256 vertices, bitsets */
static uint64_t madj[MAXF][4];
static int mbest, mcur[MAXF], mbestset[MAXF];
static int popc(const uint64_t *P) { return __builtin_popcountll(P[0]) + __builtin_popcountll(P[1]) + __builtin_popcountll(P[2]) + __builtin_popcountll(P[3]); }
static void mrec(uint64_t *P, int sz) {
    int c = popc(P);
    if (!c) { if (sz > mbest) { mbest = sz; memcpy(mbestset, mcur, sz * sizeof(int)); } return; }
    if (sz + c <= mbest) return;
    int v = -1; for (int b = 0; b < 4 && v < 0; b++) if (P[b]) v = b * 64 + __builtin_ctzll(P[b]);
    uint64_t Q[4]; for (int b = 0; b < 4; b++) Q[b] = P[b] & ~madj[v][b]; Q[v >> 6] &= ~(1ULL << (v & 63));
    mcur[sz] = v; mrec(Q, sz + 1);
    P[v >> 6] &= ~(1ULL << (v & 63)); mrec(P, sz); P[v >> 6] |= 1ULL << (v & 63);
}

int main(int argc, char **argv) {
    for (int v = 0; v < NV; v++) { int x = v; for (int i = 0; i < D; i++) { dig[v][i] = x % N; x /= N; } }
    for (int v = 0; v < NV; v++) for (int m = 0; m < NB; m++) { int mm = m, u[D];
        for (int i = 0; i < D; i++) { u[i] = (dig[v][i] + mm % 3 - 1 + N) % N; mm /= 3; } nbr[v][m] = enc(u); }
    make_shapes();
    if (argc < 2) return 2;
    if (!strcmp(argv[1], "costs")) {
        /* direct count, no formula */
        static uint8_t in0[NV]; for (int m = 0; m < NB; m++) in0[nbr[0][m]] = 1;
        int perms[120][D], np = 0, a[D] = {0, 1, 2, 3, 4}, c[D] = {0};
        memcpy(perms[np++], a, sizeof a);
        for (int i = 0; i < D;) { if (c[i] < i) { int k = (i % 2 == 0) ? 0 : c[i]; int t = a[k]; a[k] = a[i]; a[i] = t;
                memcpy(perms[np++], a, sizeof a); c[i]++; i = 0; } else { c[i] = 0; i++; } }
        int orbit[242]; for (int s = 0; s < nsh; s++) orbit[s] = -1;
        int norb = 0, osize[242] = {0}, ok_orb[242] = {0};
        for (int s = 0; s < nsh; s++) {
            if (orbit[s] >= 0) continue;
            for (int pi = 0; pi < np; pi++) for (int sg = 0; sg < 32; sg++) {
                int o[D]; for (int i = 0; i < D; i++) { int x = dig[shapes[s]][perms[pi][i]]; o[i] = ((sg >> i) & 1) ? (N - x) % N : x; }
                int e = enc(o);
                for (int t = 0; t < nsh; t++) if (shapes[t] == e && orbit[t] < 0) { orbit[t] = norb; osize[norb]++; }
            }
            ok_orb[norb] = kof[s]; norb++;
        }
        printf("{\"shapes\":%d,\"orbits\":[", nsh);
        for (int o = 0; o < norb; o++) {
            int rep = -1; for (int s = 0; s < nsh && rep < 0; s++) if (orbit[s] == o) rep = s;
            int cnt = 0; for (int m = 0; m < NB; m++) cnt += in0[nbr[shapes[rep]][m]];
            int uni = NB + NB - cnt;   /* counted below, not taken from this line */
            { static uint8_t u[NV]; memset(u, 0, NV); uni = 0;
              for (int m = 0; m < NB; m++) { u[nbr[0][m]] = 1; u[nbr[shapes[rep]][m]] = 1; }
              for (int v = 0; v < NV; v++) uni += u[v]; }
            /* every member of the orbit must give the same count */
            int same = 1; for (int s = 0; s < nsh; s++) if (orbit[s] == o) { int c2 = 0; for (int m = 0; m < NB; m++) c2 += in0[nbr[shapes[s]][m]]; if (c2 != cnt) same = 0; }
            int dd[D]; for (int i = 0; i < D; i++) { int x = dig[shapes[rep]][i]; dd[i] = x == 6 ? -1 : x; }
            printf("%s{\"k\":%d,\"size\":%d,\"representative\":[%d,%d,%d,%d,%d],\"forbidden_by_one_pair\":%d,\"penalised_by_one_pair\":%d,\"constant_on_orbit\":%s}",
                   o ? "," : "", ok_orb[o], osize[o], dd[0], dd[1], dd[2], dd[3], dd[4], cnt, uni, same ? "true" : "false");
        }
        printf("]}\n");
        return 0;
    }
    static int I[MAXI]; int n = read_code(argv[2], I);
    if (n <= 0) { fprintf(stderr, "cannot read %s\n", argv[2]); return 2; }
    static uint8_t in[NV], cnt[NV], cov[NV];
    for (int k = 0; k < n; k++) { in[I[k]] = 1; for (int m = 0; m < NB; m++) cnt[nbr[I[k]][m]]++; }
    for (int k = 0; k < n; k++) if (cnt[I[k]] != 1) { fprintf(stderr, "not independent\n"); return 3; }
    /* boxes: word w covers w + {0,1}^5 */
    for (int k = 0; k < n; k++) for (int b = 0; b < 32; b++) { int c[D]; for (int i = 0; i < D; i++) c[i] = (dig[I[k]][i] + ((b >> i) & 1)) % N; cov[enc(c)]++; }
    int zero = 0; for (int v = 0; v < NV; v++) zero += !in[v] && cnt[v] == 0;
    if (!strcmp(argv[1], "cells")) {
        int h[33] = {0}, shape[6] = {0}, cmax = 0;
        for (int v = 0; v < NV; v++) if (cov[v] > cmax) cmax = cov[v];
        for (int v = 0; v < NV; v++) { if (in[v]) continue; int c = 0;
            for (int b = 0; b < 32; b++) { int cc[D]; for (int i = 0; i < D; i++) cc[i] = (dig[v][i] + ((b >> i) & 1)) % N; c += cov[enc(cc)] > 0; }
            h[c]++;
            if (cnt[v] == 1) { int r = -1; for (int m = 0; m < NB; m++) if (in[nbr[v][m]]) r = nbr[v][m];
                int k = 0; for (int i = 0; i < D; i++) k += dig[v][i] != dig[r][i]; shape[k]++; } }
        int covered = 0; for (int v = 0; v < NV; v++) covered += cov[v] > 0;
        printf("{\"code\":\"%s\",\"size\":%d,\"max_cover_multiplicity\":%d,\"covered_cells\":%d,\"uncovered_cells\":%d,"
               "\"addable_vertices\":%d,\"candidate_shapes_by_k\":[%d,%d,%d,%d,%d],\"covered_cells_in_box_hist\":[",
               argv[2], n, cmax, covered, NV - covered, zero, shape[1], shape[2], shape[3], shape[4], shape[5]);
        for (int c = 0; c <= 32; c++) printf("%s%d", c ? "," : "", h[c]);
        printf("]}\n");
        return 0;
    }
    if (strcmp(argv[1], "local")) return 2;
    const char *outdir = NULL; for (int i = 3; i < argc; i++) if (!strcmp(argv[i], "--out")) outdir = argv[++i];
    static int Z[NV]; int nz = 0; for (int v = 0; v < NV; v++) if (!in[v] && cnt[v] == 0) Z[nz++] = v;
    int best[6] = {0}; long tried[6] = {0}, priv0[6] = {0}, exact[6] = {0}, capped = 0; int bestdel[6] = {0};
    static uint8_t inq[NV], mk[NV];
    for (int a = 0; a < n; a++) {
        int r = I[a];
        for (int s = 0; s < nsh; s++) {
            int q = addv(r, shapes[s]), k = kof[s]; tried[k]++;
            int del[64], nd = 0;
            for (int m = 0; m < NB; m++) { int u = nbr[q][m]; if (in[u] && u != r && nd < 64) del[nd++] = u; }
            if (!nd) priv0[k]++;
            /* already beaten: even adding every freed vertex could not exceed best */
            for (int m = 0; m < NB; m++) inq[nbr[q][m]] = 1;
            for (int j = 0; j < nd; j++) for (int m = 0; m < NB; m++) cnt[nbr[del[j]][m]]--;
            for (int j = 0; j < nd; j++) in[del[j]] = 0;
            int F[MAXF + 1], nf = 0, over = 0;
            for (int j = 0; j < nd; j++) for (int m = 0; m < NB; m++) { int v = nbr[del[j]][m];
                if (in[v] || cnt[v] || inq[v] || mk[v]) continue; mk[v] = 1; if (nf < MAXF) F[nf++] = v; else over = 1; }
            for (int z = 0; z < nz; z++) { int v = Z[z]; if (inq[v] || mk[v]) continue; mk[v] = 1; if (nf < MAXF) F[nf++] = v; else over = 1; }
            for (int i = 0; i < nf; i++) mk[F[i]] = 0;
            int base = n - nd, size = base;
            if (base + nf > best[k] || (base + nf == best[k] && 0)) {
                if (over) capped++;
                for (int i = 0; i < nf; i++) { memset(madj[i], 0, sizeof madj[i]);
                    for (int j = 0; j < nf; j++) if (i != j && adj_or_eq(F[i], F[j])) madj[i][j >> 6] |= 1ULL << (j & 63); }
                uint64_t P[4] = {0}; for (int i = 0; i < nf; i++) P[i >> 6] |= 1ULL << (i & 63);
                mbest = 0; mrec(P, 0); size = base + mbest; exact[k]++;
                if (size > best[k]) {
                    best[k] = size; bestdel[k] = nd;
                    if (outdir) {
                        char p[1024]; snprintf(p, sizeof p, "%s/best_k%d.txt", outdir, k);
                        FILE *o = fopen(p, "w");
                        fprintf(o, "# independent set with a private pair of shape k = %d, scripts/s2_3_shapes.c local on %s\n", k, argv[2]);
                        { int dr[D], dq[D]; for (int i = 0; i < D; i++) { dr[i] = dig[r][i]; dq[i] = dig[q][i]; }
                          fprintf(o, "# r = %d %d %d %d %d   q = %d %d %d %d %d\n", dr[0], dr[1], dr[2], dr[3], dr[4], dq[0], dq[1], dq[2], dq[3], dq[4]); }
                        fprintf(o, "%d %d %d\n", N, D, size);
                        for (int b = 0; b < n; b++) if (in[I[b]]) fprintf(o, "%d %d %d %d %d\n", dig[I[b]][0], dig[I[b]][1], dig[I[b]][2], dig[I[b]][3], dig[I[b]][4]);
                        for (int i = 0; i < mbest; i++) { int v = F[mbestset[i]]; fprintf(o, "%d %d %d %d %d\n", dig[v][0], dig[v][1], dig[v][2], dig[v][3], dig[v][4]); }
                        fclose(o);
                    }
                }
            }
            for (int j = 0; j < nd; j++) in[del[j]] = 1;
            for (int j = 0; j < nd; j++) for (int m = 0; m < NB; m++) cnt[nbr[del[j]][m]]++;
            for (int m = 0; m < NB; m++) inq[nbr[q][m]] = 0;
        }
    }
    printf("{\"code\":\"%s\",\"size\":%d,\"addable_vertices\":%d,\"by_k\":[", argv[2], n, zero);
    for (int k = 1; k <= 5; k++)
        printf("%s{\"k\":%d,\"pairs_tried\":%ld,\"already_private\":%ld,\"exact_repairs\":%ld,\"best_size\":%d,\"words_deleted_at_best\":%d}",
               k > 1 ? "," : "", k, tried[k], priv0[k], exact[k], best[k], bestdel[k]);
    printf("],\"freed_sets_over_cap\":%ld}\n", capped);
    return 0;
}

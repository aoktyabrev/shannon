/*
 * Stage 2.2 -- the group sweep of auxiliary sources against forbidden regions, with
 * the exact repair of every near miss done in the same pass.
 *
 * For each forbidden region F (a file of vertex indices) and each source S (a 367-word
 * independent set), every image gS, g in (D_7)^5 sd S_5, is scored by |gS cap F|.  For
 * a fixed linear part all 16807 translations are scored at once by scattering the
 * differences f - x (the cross-correlation of scripts/s1_aux.c, without the penalised
 * region, which feasibility does not need).  Each image with at most R words in F is
 * repaired exactly: those words are deleted, the vertices that are outside F and not
 * confusable with the rest are collected, and a maximum independent set of them is
 * added back by exhaustive search.  A repaired set of the source's size is an
 * admissible auxiliary set; it is written out for scripts/verify.
 *
 * Usage: s2_2_sweep --F f1 [--F f2 ...] --src s1 [--src s2 ...] [--repair R] [--out DIR]
 * Build: cc -O2 -march=native -fopenmp -o s2_2_sweep s2_2_sweep.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#ifdef _OPENMP
#include <omp.h>
#endif

#define N 7
#define D 5
#define NV 16807
#define MAXI 512
#define MAXF 4096
#define HB 8

static int pw[D] = {1, 7, 49, 343, 2401};
static int dig[NV][D];
static int nbr[NV][243];
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
static int enc(const int *c) { int v = 0; for (int i = 0; i < D; i++) v += c[i] * pw[i]; return v; }
static int adj_or_eq(int a, int b) {
    for (int i = 0; i < D; i++) { int t = (dig[a][i] - dig[b][i] + N) % N; if (t > 1 && t < N - 1) return 0; }
    return 1;
}
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
static int read_list(const char *path, int *out) {
    FILE *f = fopen(path, "r"); if (!f) return -1; int n = 0, v;
    while (fscanf(f, "%d", &v) == 1) out[n++] = v; fclose(f); return n;
}
static int perms[120][D], nperm;
static void make_perms(void) {
    int a[D] = {0, 1, 2, 3, 4}, c[D] = {0};
    nperm = 0; memcpy(perms[nperm++], a, sizeof a);
    for (int i = 0; i < D;) {
        if (c[i] < i) { int k = (i % 2 == 0) ? 0 : c[i]; int t = a[k]; a[k] = a[i]; a[i] = t;
            memcpy(perms[nperm++], a, sizeof a); c[i]++; i = 0; }
        else { c[i] = 0; i++; }
    }
}
static int DT[D][N][N];   /* DT[i][a][b] = ((a - b) mod 7) * 7^i */

/* exact maximum independent set among cand (small), by branch and bound */
static int mis_best, mis_cur[64], mis_bestset[64];
static uint64_t mis_adj[64];
static void mis_rec(uint64_t P, int sz, int nc) {
    if (!P) { if (sz > mis_best) { mis_best = sz; memcpy(mis_bestset, mis_cur, sz * sizeof(int)); } return; }
    if (sz + __builtin_popcountll(P) <= mis_best) return;
    int v = __builtin_ctzll(P);
    mis_cur[sz] = v; mis_rec(P & ~mis_adj[v] & ~(1ULL << v), sz + 1, nc);
    mis_rec(P & ~(1ULL << v), sz, nc);
}

int main(int argc, char **argv) {
    for (int v = 0; v < NV; v++) { int x = v; for (int i = 0; i < D; i++) { dig[v][i] = x % N; x /= N; } }
    for (int v = 0; v < NV; v++) for (int m = 0; m < 243; m++) { int mm = m, u[D];
        for (int i = 0; i < D; i++) { u[i] = (dig[v][i] + mm % 3 - 1 + N) % N; mm /= 3; } nbr[v][m] = enc(u); }
    for (int i = 0; i < D; i++) for (int a = 0; a < N; a++) for (int b = 0; b < N; b++) DT[i][a][b] = ((a - b + N) % N) * pw[i];
    make_perms();
    const char *Ff[512], *Sf[512], *outdir = NULL; int nF = 0, nS = 0, R = 2, slack = 0, keep = 4;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--F")) Ff[nF++] = argv[++i];
        else if (!strcmp(argv[i], "--src")) Sf[nS++] = argv[++i];
        else if (!strcmp(argv[i], "--repair")) R = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--out")) outdir = argv[++i];
        else if (!strcmp(argv[i], "--slack")) slack = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--keep")) keep = atoi(argv[++i]);
    }
    static int S[512][MAXI], nSz[512];
    for (int s = 0; s < nS; s++) { nSz[s] = read_code(Sf[s], S[s]); if (nSz[s] <= 0) { fprintf(stderr, "bad src %s\n", Sf[s]); return 2; } }
    double t0 = now();
    long grand_hist[HB] = {0}; int grand_best_s = 0, grand_min = 1 << 30; long success = 0;
    printf("{\"rows\":[\n");
    for (int fi = 0; fi < nF; fi++) {
        static int Fl[MAXF]; int nf = read_list(Ff[fi], Fl);
        static uint8_t inF[NV]; memset(inF, 0, NV); for (int k = 0; k < nf; k++) inF[Fl[k]] = 1;
        for (int si = 0; si < nS; si++) {
            long hist[HB] = {0}; int minhit = 1 << 30, best_s = 0; long nrep = 0, nsucc = 0, written_pair = 0;
            #pragma omp parallel for schedule(dynamic)
            for (int lp = 0; lp < nperm * 32; lp++) {
                int pi = lp / 32, sg = lp % 32;
                int img[MAXI], n = nSz[si];
                for (int k = 0; k < n; k++) { int o[D];
                    for (int i = 0; i < D; i++) { int c = dig[S[si][k]][perms[pi][i]]; o[i] = ((sg >> i) & 1) ? (N - c) % N : c; }
                    img[k] = enc(o); }
                uint16_t cnt[NV]; memset(cnt, 0, sizeof cnt);
                for (int a = 0; a < nf; a++) { const int *fd = dig[Fl[a]];
                    const int *r0 = DT[0][fd[0]], *r1 = DT[1][fd[1]], *r2 = DT[2][fd[2]], *r3 = DT[3][fd[3]], *r4 = DT[4][fd[4]];
                    for (int k = 0; k < n; k++) { const int *xd = dig[img[k]];
                        cnt[r0[xd[0]] + r1[xd[1]] + r2[xd[2]] + r3[xd[3]] + r4[xd[4]]]++; } }
                long lh[HB] = {0}; int lmin = 1 << 30, lbest = 0; long lrep = 0, lsucc = 0;
                for (int c = 0; c < NV; c++) {
                    int h = cnt[c]; if (h < HB) lh[h]++; if (h < lmin) lmin = h;
                    if (h > R) continue;
                    /* the image translated by c: x + c */
                    int X[MAXI], nx = 0, bad[16], nb = 0;
                    for (int k = 0; k < n; k++) { int o[D];
                        for (int i = 0; i < D; i++) o[i] = (dig[img[k]][i] + dig[c][i]) % N;
                        int w = enc(o); if (inF[w]) bad[nb++] = w; else X[nx++] = w; }
                    /* legal replacements: outside F, not in X, not confusable with X */
                    uint8_t blocked[NV]; memset(blocked, 0, NV);
                    for (int k = 0; k < nx; k++) for (int m = 0; m < 243; m++) blocked[nbr[X[k]][m]] = 1;
                    int cand[64], ncand = 0;
                    for (int b = 0; b < nb; b++) for (int m = 0; m < 243; m++) { int v = nbr[bad[b]][m];
                        /* any replacement must lie next to a deleted word, else the image was not maximal-in-F */
                        if (blocked[v] || inF[v]) continue; int dup = 0;
                        for (int z = 0; z < ncand; z++) if (cand[z] == v) dup = 1;
                        if (!dup) { if (ncand < 64) cand[ncand++] = v; else fprintf(stderr, "WARNING: more than 64 replacement candidates, truncated\n"); } }
                    int added = 0, addset[64];
                    #pragma omp critical(mis)
                    {
                        for (int a2 = 0; a2 < ncand; a2++) { mis_adj[a2] = 0;
                            for (int b2 = 0; b2 < ncand; b2++) if (a2 != b2 && adj_or_eq(cand[a2], cand[b2])) mis_adj[a2] |= 1ULL << b2; }
                        mis_best = 0; mis_rec(ncand == 64 ? ~0ULL : ((1ULL << ncand) - 1), 0, ncand);
                        added = mis_best; for (int z = 0; z < added; z++) addset[z] = cand[mis_bestset[z]];
                    }
                    int s = nx + added; lrep++;
                    if (s > lbest) lbest = s;
                    if (s >= n) lsucc++;
                    if (s >= n - slack) {
                        if (outdir) {
                            #pragma omp critical(out)
                            if (written_pair < keep || s >= n) { written_pair++;
                              char p[1024]; snprintf(p, sizeof p, "%s/%s_s%d_F%d_S%d_%ld.txt", outdir, s >= n ? "admissible" : "near", s, fi, si, written_pair);
                              FILE *o = fopen(p, "w"); fprintf(o, "# repaired image outside F (%s), scripts/s2_2_sweep.c, F=%s src=%s\n%d %d %d\n", s >= n ? "full size" : "short of full size", Ff[fi], Sf[si], N, D, s);
                              for (int k = 0; k < nx; k++) fprintf(o, "%d %d %d %d %d\n", dig[X[k]][0], dig[X[k]][1], dig[X[k]][2], dig[X[k]][3], dig[X[k]][4]);
                              for (int k = 0; k < added; k++) fprintf(o, "%d %d %d %d %d\n", dig[addset[k]][0], dig[addset[k]][1], dig[addset[k]][2], dig[addset[k]][3], dig[addset[k]][4]);
                              fclose(o); }
                        }
                    }
                }
                #pragma omp critical(acc)
                { for (int h = 0; h < HB; h++) hist[h] += lh[h]; if (lmin < minhit) minhit = lmin; if (lbest > best_s) best_s = lbest; nrep += lrep; nsucc += lsucc; }
            }
            for (int h = 0; h < HB; h++) grand_hist[h] += hist[h];
            if (minhit < grand_min) grand_min = minhit; if (best_s > grand_best_s) grand_best_s = best_s; success += nsucc;
            printf("%s{\"F\":\"%s\",\"F_size\":%d,\"src\":\"%s\",\"min_hits\":%d,\"hist\":[%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld],"
                   "\"repaired\":%ld,\"best_repaired_size\":%d,\"admissible_full_size\":%ld}",
                   (fi || si) ? ",\n" : "", Ff[fi], nf, Sf[si], minhit, hist[0], hist[1], hist[2], hist[3], hist[4], hist[5], hist[6], hist[7],
                   nrep, best_s, nsucc);
            fflush(stdout);
        }
    }
    printf("\n],\"group_elements_per_pair\":%d,\"pairs\":%d,\"grand_hist\":[%ld,%ld,%ld,%ld,%ld,%ld,%ld,%ld],"
           "\"grand_min_hits\":%d,\"grand_best_repaired_size\":%d,\"admissible_full_size\":%ld,\"repair_threshold\":%d,\"seconds\":%.1f}\n",
           nperm * 32 * NV, nF * nS, grand_hist[0], grand_hist[1], grand_hist[2], grand_hist[3], grand_hist[4], grand_hist[5], grand_hist[6], grand_hist[7],
           grand_min, grand_best_s, success, R, now() - t0);
    return 0;
}

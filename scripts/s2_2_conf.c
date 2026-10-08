/*
 * Stage 2.2 -- configurations of a code and the swap plateau around it.
 *
 * A configuration is (code I, a family of t candidate private pairs with distinct
 * centres, a proper 2-colouring of their q-conflict graph).  Its forbidden region is
 * F = N[P_H] cap N[P_V].  By the lemma of PREREGISTRATION_S2_2.md an automorphism of
 * C_7^5 moves F to gF and changes nothing else, so the variables are the code (up to
 * Aut), the family and the colouring.  This program enumerates every family of size
 * >= TMIN and every colouring of it, exactly, and reports |F| for each.
 *
 * Modes
 *   s2_2_conf stats  CODE [--tmin T] [--dump-F DIR]     one code, JSON on stdout
 *   s2_2_conf plateau CODE... [--nodes M] [--tmin T] [--out DIR] [--k2]
 *        breadth-first walk over 1-swaps I -> I - r + q (q a candidate of centre r),
 *        which keep |I| and independence by construction; with --k2 also 2-swaps
 *        (remove w1,w2, add two non-adjacent v1,v2 whose code-neighbours lie in
 *        {w1,w2}).  Every code visited is reported by fingerprint; codes with
 *        t* >= TMIN are written to OUT.
 *
 * Every set written is re-verified by scripts/verify before any number about it is used.
 *
 * Build: cc -O2 -march=native -o s2_2_conf s2_2_conf.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define N 7
#define D 5
#define NV 16807
#define NB 243            /* closed neighbourhood size */
#define MAXC 64           /* candidates handled */
#define MAXI 400

static int pw[D] = {1, 7, 49, 343, 2401};
static int nbr[NV][NB];   /* closed neighbourhoods, nbr[v][121] == v */
static uint64_t zob[NV];

static void dec(int v, int *c) { for (int i = 0; i < D; i++) { c[i] = v % N; v /= N; } }
static int enc(const int *c) { int v = 0; for (int i = 0; i < D; i++) v += c[i] * pw[i]; return v; }
static int adj_or_eq(int a, int b) {
    int ca[D], cb[D]; dec(a, ca); dec(b, cb);
    for (int i = 0; i < D; i++) { int t = (ca[i] - cb[i] + N) % N; if (t > 1 && t < N - 1) return 0; }
    return 1;
}
static int weight(int a, int b) {
    int ca[D], cb[D], w = 0; dec(a, ca); dec(b, cb);
    for (int i = 0; i < D; i++) w += ca[i] != cb[i];
    return w;
}
static uint64_t sm(uint64_t *s) { uint64_t z = (*s += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL; return z ^ (z >> 31); }
static void init(void) {
    for (int v = 0; v < NV; v++) {
        int c[D]; dec(v, c);
        for (int m = 0; m < NB; m++) { int mm = m, u[D];
            for (int i = 0; i < D; i++) { u[i] = (c[i] + mm % 3 - 1 + N) % N; mm /= 3; }
            nbr[v][m] = enc(u); }
    }
    uint64_t s = 20261008; for (int v = 0; v < NV; v++) zob[v] = sm(&s);
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
static int cmpint(const void *a, const void *b) { return *(const int *)a - *(const int *)b; }
static void write_code(const char *path, const int *I, int n, const char *hdr) {
    int s[MAXI]; memcpy(s, I, n * sizeof(int)); qsort(s, n, sizeof(int), cmpint);
    FILE *f = fopen(path, "w");
    fprintf(f, "# %s\n%d %d %d\n", hdr, N, D, n);
    for (int k = 0; k < n; k++) { int c[D]; dec(s[k], c); fprintf(f, "%d %d %d %d %d\n", c[0], c[1], c[2], c[3], c[4]); }
    fclose(f);
}

/* ---- the state of one code -------------------------------------------------- */
typedef struct {
    int n, I[MAXI];
    uint8_t in[NV];
    uint8_t cnt[NV];             /* |N[v] cap I| */
    int nc, r[MAXC], q[MAXC];    /* candidates (r = centre) */
    uint64_t hash;
} Code;

static void code_load(Code *C, const int *I, int n) {
    memset(C, 0, sizeof *C); C->n = n; memcpy(C->I, I, n * sizeof(int));
    for (int k = 0; k < n; k++) { C->in[I[k]] = 1; C->hash ^= zob[I[k]];
        for (int m = 0; m < NB; m++) C->cnt[nbr[I[k]][m]]++; }
}
static int code_independent(const Code *C) {
    for (int k = 0; k < C->n; k++) if (C->cnt[C->I[k]] != 1) return 0;
    return 1;
}
static int centre_of(const Code *C, int v) {
    for (int m = 0; m < NB; m++) if (C->in[nbr[v][m]]) return nbr[v][m];
    return -1;
}
static void code_candidates(Code *C) {
    C->nc = 0;
    for (int v = 0; v < NV; v++) if (!C->in[v] && C->cnt[v] == 1) {
        if (C->nc < MAXC) { C->q[C->nc] = v; C->r[C->nc] = centre_of(C, v); }
        C->nc++;
    }
}
static void code_swap(Code *C, int out, int inn) {
    int k; for (k = 0; C->I[k] != out; k++);
    C->I[k] = inn; C->in[out] = 0; C->in[inn] = 1; C->hash ^= zob[out] ^ zob[inn];
    for (int m = 0; m < NB; m++) { C->cnt[nbr[out][m]]--; C->cnt[nbr[inn][m]]++; }
}

/* ---- configurations: families of size >= tmin, all proper colourings -------- */
typedef struct {
    int tstar;                   /* largest family with distinct centres, bipartite */
    long nconf[MAXC + 1];        /* configurations by t (colourings up to swap)       */
    int fmin[MAXC + 1], fmax[MAXC + 1];
    uint64_t best_fam[MAXC + 1], best_col[MAXC + 1];   /* argmin |F| per t */
    long nodes;
} Conf;

static const Code *gC; static int gtmin; static Conf *gR;
static uint64_t conflict[MAXC];
static int lab[MAXC];            /* 0 unused, 1 H (q to P_H), 2 V */

static int forbidden_size(const Code *C, uint64_t fam, uint64_t col, uint8_t *mark /* NV, out: 1 H, 2 V */) {
    static uint8_t m[NV]; uint8_t *M = mark ? mark : m;
    memset(M, 0, NV);
    for (int j = 0; j < C->nc && j < MAXC; j++) if (fam >> j & 1) {
        int qH = (int)(col >> j & 1);      /* 1: q goes to P_H, r to P_V */
        int hv = qH ? C->q[j] : C->r[j], vv = qH ? C->r[j] : C->q[j];
        for (int k = 0; k < NB; k++) { M[nbr[hv][k]] |= 1; M[nbr[vv][k]] |= 2; }
    }
    int f = 0; for (int v = 0; v < NV; v++) f += M[v] == 3;
    return f;
}

static void rec(int j, int used) {
    gR->nodes++;
    const Code *C = gC; int nc = C->nc < MAXC ? C->nc : MAXC;
    if (used + (nc - j) < gtmin) return;
    if (j == nc) {
        uint64_t fam = 0, col = 0;
        for (int i = 0; i < nc; i++) if (lab[i]) { fam |= 1ULL << i; if (lab[i] == 1) col |= 1ULL << i; }
        if (used > gR->tstar) gR->tstar = used;
        int f = forbidden_size(C, fam, col, NULL);
        gR->nconf[used]++;
        if (!gR->fmin[used] || f < gR->fmin[used]) { gR->fmin[used] = f; gR->best_fam[used] = fam; gR->best_col[used] = col; }
        if (f > gR->fmax[used]) gR->fmax[used] = f;
        return;
    }
    rec(j + 1, used);                                    /* candidate j unused */
    for (int i = 0; i < j; i++) if (lab[i] && C->r[i] == C->r[j]) return;   /* centre taken */
    int first = 1; for (int i = 0; i < j; i++) if (lab[i]) first = 0;
    for (int l = 1; l <= 2; l++) {
        if (first && l == 2) break;                      /* first used pair to H: kills the global swap */
        int ok = 1;
        for (int i = 0; i < j && ok; i++) if (lab[i] == l && (conflict[j] >> i & 1)) ok = 0;
        if (!ok) continue;
        lab[j] = l; rec(j + 1, used + 1); lab[j] = 0;
    }
}

/* t* alone, cheaply: branch and bound with no colouring bookkeeping beyond feasibility */
static int bb_best;
static void bb(const Code *C, int j, int used) {
    int nc = C->nc < MAXC ? C->nc : MAXC;
    if (used + (nc - j) <= bb_best) return;
    if (j == nc) { bb_best = used; return; }
    int taken = 0; for (int i = 0; i < j; i++) if (lab[i] && C->r[i] == C->r[j]) taken = 1;
    if (!taken) for (int l = 1; l <= 2; l++) {
        int ok = 1;
        for (int i = 0; i < j && ok; i++) if (lab[i] == l && (conflict[j] >> i & 1)) ok = 0;
        if (ok) { lab[j] = l; bb(C, j + 1, used + 1); lab[j] = 0; }
    }
    bb(C, j + 1, used);
}
static void build_conflict(const Code *C) {
    int nc = C->nc < MAXC ? C->nc : MAXC;
    memset(conflict, 0, sizeof conflict);
    for (int i = 0; i < nc; i++) for (int j = i + 1; j < nc; j++)
        if (adj_or_eq(C->q[i], C->q[j])) { conflict[i] |= 1ULL << j; conflict[j] |= 1ULL << i; }
}
static int tstar(const Code *C) {
    build_conflict(C); memset(lab, 0, sizeof lab); bb_best = 0; bb(C, 0, 0); return bb_best;
}
static void configurations(const Code *C, int tmin, Conf *R) {
    memset(R, 0, sizeof *R); build_conflict(C); memset(lab, 0, sizeof lab);
    gC = C; gtmin = tmin; gR = R; rec(0, 0);
}

/* Aut-invariant fingerprint: histogram of cnt over non-code vertices, the sorted
 * multiset of per-word counts of exclusive neighbours, and the candidate count.
 * Different fingerprints prove non-isomorphism; equal ones prove nothing. */
static uint64_t fingerprint(const Code *C, char *txt, size_t tl) {
    int h[NB + 1] = {0}; int ex[MAXI];
    for (int v = 0; v < NV; v++) if (!C->in[v]) h[C->cnt[v]]++;
    for (int k = 0; k < C->n; k++) { int e = 0, w = C->I[k];
        for (int m = 0; m < NB; m++) { int v = nbr[w][m]; if (v != w && C->cnt[v] == 1) e++; }
        ex[k] = e; }
    qsort(ex, C->n, sizeof(int), cmpint);
    uint64_t f = 1469598103934665603ULL;
    for (int i = 0; i <= 32; i++) { f ^= (uint64_t)h[i] + 0x100000ULL * i; f *= 1099511628211ULL; }
    for (int k = 0; k < C->n; k++) { f ^= (uint64_t)ex[k] + 0x9000ULL; f *= 1099511628211ULL; }
    if (txt) { size_t p = 0; p += snprintf(txt + p, tl - p, "cnt");
        for (int i = 0; i <= 12; i++) p += snprintf(txt + p, tl - p, "%s%d", i ? "," : ":", h[i]); }
    return f;
}

static void print_stats(const Code *C, int tmin, const char *dumpdir, const char *label) {
    Conf R; configurations(C, tmin, &R);
    int nc = C->nc < MAXC ? C->nc : MAXC;
    int edges = 0; for (int i = 0; i < nc; i++) edges += __builtin_popcountll(conflict[i]);
    edges /= 2;
    int cen[MAXC], ncen = 0;
    for (int i = 0; i < nc; i++) { int s = 0; for (int k = 0; k < ncen; k++) if (cen[k] == C->r[i]) s = 1; if (!s) cen[ncen++] = C->r[i]; }
    int wh[D + 1] = {0}; for (int i = 0; i < nc; i++) wh[weight(C->r[i], C->q[i])]++;
    char fp[256]; uint64_t f = fingerprint(C, fp, sizeof fp);
    int ts = tstar(C);
    printf("{\"code\":\"%s\",\"size\":%d,\"independent\":%s,\"candidates\":%d,\"distinct_centres\":%d,"
           "\"conflict_edges\":%d,\"t_star\":%d,\"fingerprint\":\"%016llx\",\"fp_text\":\"%s\","
           "\"weight_hist\":[%d,%d,%d,%d,%d,%d],\"pairs\":[",
           label, C->n, code_independent(C) ? "true" : "false", C->nc, ncen, edges, ts,
           (unsigned long long)f, fp, wh[0], wh[1], wh[2], wh[3], wh[4], wh[5]);
    for (int i = 0; i < nc; i++) { int a[D], b[D]; dec(C->r[i], a); dec(C->q[i], b);
        printf("%s[[%d,%d,%d,%d,%d],[%d,%d,%d,%d,%d]]", i ? "," : "", a[0], a[1], a[2], a[3], a[4], b[0], b[1], b[2], b[3], b[4]); }
    printf("],\"by_t\":{");
    int firstp = 1;
    for (int t = MAXC; t >= 0; t--) if (R.nconf[t]) {
        printf("%s\"%d\":{\"configurations\":%ld,\"F_min\":%d,\"F_max\":%d,\"argmin_family\":%llu,\"argmin_colouring\":%llu}",
               firstp ? "" : ",", t, R.nconf[t], R.fmin[t], R.fmax[t],
               (unsigned long long)R.best_fam[t], (unsigned long long)R.best_col[t]);
        firstp = 0;
        if (dumpdir) {
            static uint8_t M[NV]; forbidden_size(C, R.best_fam[t], R.best_col[t], M);
            char p[1024]; snprintf(p, sizeof p, "%s/F_t%d.txt", dumpdir, t);
            FILE *o = fopen(p, "w"); for (int v = 0; v < NV; v++) if (M[v] == 3) fprintf(o, "%d\n", v); fclose(o);
        }
    }
    printf("},\"enum_nodes\":%ld}\n", R.nodes);
}

/* every configuration of size >= tmin as a line: t fam col |F| (for the sweep driver) */
static const Code *lC; static FILE *lout; static const char *ldir;
static void lrec(int j, int used, int tmin) {
    const Code *C = lC; int nc = C->nc < MAXC ? C->nc : MAXC;
    if (used + (nc - j) < tmin) return;
    if (j == nc) { uint64_t fam = 0, col = 0;
        for (int i = 0; i < nc; i++) if (lab[i]) { fam |= 1ULL << i; if (lab[i] == 1) col |= 1ULL << i; }
        static uint8_t M[NV]; int fs = forbidden_size(C, fam, col, M);
        fprintf(lout, "%d %llu %llu %d\n", used, (unsigned long long)fam, (unsigned long long)col, fs);
        if (ldir) { char p[1024]; snprintf(p, sizeof p, "%s/F_t%d_fam%llu_col%llu.txt", ldir, used, (unsigned long long)fam, (unsigned long long)col);
            FILE *o = fopen(p, "w"); for (int v = 0; v < NV; v++) if (M[v] == 3) fprintf(o, "%d\n", v); fclose(o); }
        return; }
    lrec(j + 1, used, tmin);
    for (int i = 0; i < j; i++) if (lab[i] && C->r[i] == C->r[j]) return;
    int first = 1; for (int i = 0; i < j; i++) if (lab[i]) first = 0;
    for (int l = 1; l <= 2; l++) { if (first && l == 2) break;
        int ok = 1; for (int i = 0; i < j && ok; i++) if (lab[i] == l && (conflict[j] >> i & 1)) ok = 0;
        if (ok) { lab[j] = l; lrec(j + 1, used + 1, tmin); lab[j] = 0; } }
}

/* ---- plateau --------------------------------------------------------------- */
typedef struct { uint64_t *k; size_t cap, n; } HSet;
static int hs_add(HSet *h, uint64_t x) {
    if (!x) x = 1;
    if (h->n * 2 >= h->cap) { size_t oc = h->cap; uint64_t *ok = h->k; h->cap = oc ? oc * 2 : 1 << 16;
        h->k = calloc(h->cap, 8); h->n = 0; for (size_t i = 0; i < oc; i++) if (ok[i]) hs_add(h, ok[i]); free(ok); }
    size_t i = x & (h->cap - 1);
    while (h->k[i]) { if (h->k[i] == x) return 0; i = (i + 1) & (h->cap - 1); }
    h->k[i] = x; h->n++; return 1;
}

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

/* ---- window k-swaps --------------------------------------------------------
 * A window W is a set of k code words connected in the "share a neighbour" graph
 * (circular distance <= 2 in every coordinate); windows that are not connected
 * decompose into smaller swaps.  Removing W frees the vertices whose code-neighbours
 * all lie in W; every independent k-subset Y != W of (freed + W) gives the code
 * I - W + Y.  An independent (k+1)-subset would be a 368-word independent set of
 * C_7^5, and is reported as such rather than silently used.  Windows are enumerated
 * once each by the ESU scheme (Wernicke 2006). */
static double kdeadline = 0, kt0; static int ktimed_out; static long ktick;
static Code KC; static int kclose[MAXI][128], knclose[MAXI], kidx[NV];
static int kK, kSub[8], kns; static long kwin[8], kmoves, knew, k368;
static HSet kseen; static int ktmin; static uint8_t kF[NV]; static int kuseF; static const char *kout; static long kwritten, kmaxout;
static int close2(int a, int b) {
    int ca[D], cb[D]; dec(a, ca); dec(b, cb);
    for (int i = 0; i < D; i++) { int t = (ca[i] - cb[i] + N) % N; if (t > 2 && t < N - 2) return 0; }
    return 1;
}
static int kY[8], kVall[256], knv;
static uint64_t kadj[256][4];
static void ksubsets(int start, int sz, int k, const int *W) {
    if (sz == k) {
        int same = 1; for (int i = 0; i < k && same; i++) { int f = 0; for (int j = 0; j < k; j++) if (kVall[kY[i]] == W[j]) f = 1; if (!f) same = 0; }
        if (same) return;
        kmoves++;
        uint64_t h = KC.hash; for (int i = 0; i < k; i++) h ^= zob[W[i]] ^ zob[kVall[kY[i]]];
        if (!hs_add(&kseen, h)) return;
        knew++;
        Code T = KC;
        for (int i = 0; i < k; i++) { int w = W[i], keep = 0; for (int j = 0; j < k; j++) if (kVall[kY[j]] == w) keep = 1;
            if (!keep) { T.in[w] = 0; for (int m = 0; m < NB; m++) T.cnt[nbr[w][m]]--; } }
        for (int j = 0; j < k; j++) { int v = kVall[kY[j]]; if (T.in[v]) continue; T.in[v] = 1; for (int m = 0; m < NB; m++) T.cnt[nbr[v][m]]++; }
        int n = 0; for (int v = 0; v < NV; v++) if (T.in[v]) T.I[n++] = v; T.n = n;
        if (!code_independent(&T) || n != KC.n) { fprintf(stderr, "BUG: k-swap produced a bad code\n"); exit(4); }
        code_candidates(&T); int ts = tstar(&T);
        int fmin = -1;
        if (ts >= ktmin) { Conf R; configurations(&T, ktmin, &R); fmin = R.fmin[ktmin]; }
        printf("{\"k\":%d,\"candidates\":%d,\"t_star\":%d,\"F_min_at_tmin\":%d", k, T.nc, ts, fmin);
        if (kout && kwritten < kmaxout) { char p[1024]; snprintf(p, sizeof p, "%s/kswap_%06ld_t%d.txt", kout, kwritten, ts);
            write_code(p, T.I, T.n, "Stage 2.2 window k-swap code, scripts/s2_2_conf.c"); printf(",\"file\":\"%s\"", p); kwritten++; }
        printf("}\n"); fflush(stdout);
        return;
    }
    for (int i = start; i < knv; i++) {
        int ok = 1; for (int j = 0; j < sz && ok; j++) if (kadj[i][kY[j] >> 6] >> (kY[j] & 63) & 1) ok = 0;
        if (!ok) continue;
        kY[sz] = i; ksubsets(i + 1, sz + 1, k, W);
    }
}
static int kmis(uint64_t *P, int sz) {          /* maximum independent set size in the window, small */
    int best = sz, v = -1;
    for (int b = 0; b < 4 && v < 0; b++) if (P[b]) v = b * 64 + __builtin_ctzll(P[b]);
    if (v < 0) return sz;
    int cnt = 0; for (int b = 0; b < 4; b++) cnt += __builtin_popcountll(P[b]);
    if (sz + cnt <= sz) return sz;
    uint64_t Q[4]; for (int b = 0; b < 4; b++) Q[b] = P[b] & ~kadj[v][b]; Q[v >> 6] &= ~(1ULL << (v & 63));
    int a = kmis(Q, sz + 1); if (a > best) best = a;
    P[v >> 6] &= ~(1ULL << (v & 63));
    int c = kmis(P, sz); P[v >> 6] |= 1ULL << (v & 63);
    return a > c ? a : c;
}
static void kwindow(void) {
    int k = kns; kwin[k]++;
    int W[8]; for (int i = 0; i < k; i++) W[i] = KC.I[kSub[i]];
    static uint8_t mk[NV]; static int touched[8 * NB]; int nt = 0; knv = 0;
    for (int i = 0; i < k; i++) kVall[knv++] = W[i];
    for (int i = 0; i < k; i++) for (int m = 0; m < NB; m++) { int v = nbr[W[i]][m];
        if (KC.in[v] || mk[v]) continue; mk[v] = 1; touched[nt++] = v;
        if (kuseF && kF[v]) continue;
        int inside = 0; for (int j = 0; j < k; j++) inside += adj_or_eq(v, W[j]);
        if (inside == KC.cnt[v] && knv < 256) kVall[knv++] = v; }
    for (int i = 0; i < nt; i++) mk[touched[i]] = 0;
    if (knv <= k) return;
    for (int i = 0; i < knv; i++) { memset(kadj[i], 0, sizeof kadj[i]);
        for (int j = 0; j < knv; j++) if (i != j && adj_or_eq(kVall[i], kVall[j])) kadj[i][j >> 6] |= 1ULL << (j & 63); }
    uint64_t P[4] = {0}; for (int i = 0; i < knv; i++) P[i >> 6] |= 1ULL << (i & 63);
    int m = kmis(P, 0);
    if (m > k) { k368++;
        fprintf(stderr, "ALERT: window of %d admits %d -- an independent set larger than the input%s\n", k, m, kuseF ? " inside G_F" : "");
        if (kuseF && kout) { /* write the improved set: I - W + MIS */
            int best[64], nb = 0; uint64_t P2[4] = {0}; for (int i = 0; i < knv; i++) P2[i >> 6] |= 1ULL << (i & 63);
            /* greedy-exact: rerun the search keeping the set */
            for (int i = 0; i < knv && nb < m; i++) { int ok = (P2[i >> 6] >> (i & 63)) & 1; if (!ok) continue;
                uint64_t Q[4]; for (int b = 0; b < 4; b++) Q[b] = P2[b] & ~kadj[i][b]; Q[i >> 6] &= ~(1ULL << (i & 63));
                if (1 + kmis(Q, 0) == kmis(P2, 0)) { best[nb++] = i; for (int b = 0; b < 4; b++) P2[b] = Q[b]; }
                else P2[i >> 6] &= ~(1ULL << (i & 63)); }
            char p[1024]; snprintf(p, sizeof p, "%s/improved_%ld.txt", kout, k368);
            int out[MAXI + 64], no = 0;
            for (int a = 0; a < KC.n; a++) { int w = KC.I[a], inW = 0; for (int j = 0; j < k; j++) if (W[j] == w) inW = 1; if (!inW) out[no++] = w; }
            for (int i = 0; i < nb; i++) out[no++] = kVall[best[i]];
            write_code(p, out, no, "Stage 2.2 k-opt improvement inside G_F, scripts/s2_2_conf.c"); }
    }
    if (m >= k && !kuseF) ksubsets(0, 0, k, W);
}
static int kin_sub(int u) { for (int i = 0; i < kns; i++) if (kSub[i] == u) return 1; return 0; }
static int kadj_sub(int u) { for (int i = 0; i < kns; i++) { int s = kSub[i];
        for (int j = 0; j < knclose[s]; j++) if (kclose[s][j] == u) return 1; } return 0; }
static void kextend(int *ext, int next, int v) {
    if (ktimed_out) return;
    if (kdeadline > 0 && (++ktick & 4095) == 0 && now() - kt0 > kdeadline) { ktimed_out = 1; return; }
    if (kns >= 2) kwindow();
    if (kns == kK) return;
    int e[1024]; int ne = next; memcpy(e, ext, next * sizeof(int));
    while (ne > 0) {
        int w = e[--ne];
        int e2[1024]; int n2 = ne; memcpy(e2, e, ne * sizeof(int));
        for (int j = 0; j < knclose[w]; j++) { int u = kclose[w][j];
            if (u > v && !kin_sub(u) && !kadj_sub(u)) { int dup = 0; for (int z = 0; z < n2; z++) if (e2[z] == u) dup = 1; if (!dup && n2 < 1024) e2[n2++] = u; } }
        kSub[kns++] = w; kextend(e2, n2, v); kns--;
    }
}
static const char *kforbid;
static int kswap_main(const char **codes, int ncodes, int K, int tmin, const char *outdir, long maxout) {
    static int buf[MAXI];
    kK = K; ktmin = tmin; kout = outdir; kmaxout = maxout;
    if (kforbid) { FILE *f = fopen(kforbid, "r"); int v; kuseF = 1; while (fscanf(f, "%d", &v) == 1) kF[v] = 1; fclose(f); }
    double t0 = now(); kt0 = t0;
    for (int c = 0; c < ncodes; c++) {
        int n = read_code(codes[c], buf); code_load(&KC, buf, n);
        if (!code_independent(&KC)) { fprintf(stderr, "not independent: %s\n", codes[c]); return 3; }
        hs_add(&kseen, KC.hash);
        if (kuseF) { int bad = 0, free0 = 0; for (int a = 0; a < n; a++) bad += kF[KC.I[a]];
            for (int v = 0; v < NV; v++) free0 += !KC.in[v] && !kF[v] && KC.cnt[v] == 0;
            fprintf(stderr, "input %s: %d words in F, %d allowed vertices addable outright\n", codes[c], bad, free0);
            if (bad) return 5; }
        for (int a = 0; a < n; a++) { knclose[a] = 0; kidx[KC.I[a]] = a;
            for (int b = 0; b < n; b++) if (a != b && close2(KC.I[a], KC.I[b]) && knclose[a] < 128) kclose[a][knclose[a]++] = b; }
        for (int v = 0; v < n; v++) {
            kns = 1; kSub[0] = v;
            int ext[1024], ne = 0; for (int j = 0; j < knclose[v]; j++) if (kclose[v][j] > v) ext[ne++] = kclose[v][j];
            kextend(ext, ne, v);
        }
    }
    printf("{\"summary\":true,\"codes\":%d,\"kmax\":%d,\"windows\":[%ld,%ld,%ld,%ld,%ld],\"moves\":%ld,\"new_codes\":%ld,"
           "\"windows_admitting_more_than_k\":%ld,\"inside_G_F\":%s,\"exhausted\":%s,\"seconds\":%.1f}\n", ncodes, K, kwin[2], kwin[3], kwin[4], kwin[5], kwin[6],
           kmoves, knew, k368, kuseF ? "true" : "false", ktimed_out ? "false" : "true", now() - t0);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s stats|list|plateau CODE... [opts]\n", argv[0]); return 2; }
    init();
    int tmin = 9; long maxnodes = 100000; const char *outdir = NULL, *dumpF = NULL; int k2 = 0, wall = 0, kmax = 3;
    const char *codes[64]; int ncodes = 0;
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--tmin")) tmin = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--nodes")) maxnodes = atol(argv[++i]);
        else if (!strcmp(argv[i], "--out")) outdir = argv[++i];
        else if (!strcmp(argv[i], "--dump-F")) dumpF = argv[++i];
        else if (!strcmp(argv[i], "--k2")) k2 = 1;
        else if (!strcmp(argv[i], "--write-all")) wall = 1;
        else if (!strcmp(argv[i], "--k")) kmax = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--forbid")) kforbid = argv[++i];
        else if (!strcmp(argv[i], "--seconds")) kdeadline = atof(argv[++i]);
        else if (ncodes < 64) codes[ncodes++] = argv[i];
    }
    static int buf[MAXI];
    static Code C;
    if (!strcmp(argv[1], "stats") || !strcmp(argv[1], "list")) {
        int n = read_code(codes[0], buf); if (n < 0) { fprintf(stderr, "cannot read\n"); return 2; }
        code_load(&C, buf, n); code_candidates(&C);
        if (!strcmp(argv[1], "stats")) print_stats(&C, tmin, dumpF, codes[0]);
        else { build_conflict(&C); memset(lab, 0, sizeof lab); lC = &C; lout = stdout; ldir = outdir; lrec(0, 0, tmin); }
        return 0;
    }
    if (!strcmp(argv[1], "kswap")) return kswap_main(codes, ncodes, kmax, tmin, outdir, maxnodes);
    if (strcmp(argv[1], "plateau")) return 2;

    /* breadth-first over swaps; the queue stores codes explicitly */
    size_t qcap = maxnodes + 16; int (*Q)[MAXI] = malloc(qcap * sizeof *Q); int *Qn = malloc(qcap * sizeof(int));
    int *Qdepth = malloc(qcap * sizeof(int));
    size_t qh = 0, qt = 0; HSet seen = {0}, fps = {0};
    for (int c = 0; c < ncodes; c++) {
        int n = read_code(codes[c], buf); code_load(&C, buf, n);
        if (!code_independent(&C)) { fprintf(stderr, "start %s not independent\n", codes[c]); return 3; }
        if (hs_add(&seen, C.hash)) { memcpy(Q[qt], buf, n * sizeof(int)); Qn[qt] = n; Qdepth[qt] = 0; qt++; }
    }
    double t0 = now(); long written = 0, hist_t[MAXC + 1] = {0}; int fbest = 1 << 30, best_t = 0;
    long fpnew = 0, k2moves = 0, k2new = 0;
    printf("{\"rows\":[\n"); int firstrow = 1;
    while (qh < qt) {
        int n = Qn[qh], depth = Qdepth[qh]; code_load(&C, Q[qh], n); qh++;
        if (!code_independent(&C)) { fprintf(stderr, "BUG: non-independent code in plateau\n"); return 4; }
        code_candidates(&C);
        int ts = tstar(&C); hist_t[ts]++;
        char fpt[256]; uint64_t fp = fingerprint(&C, fpt, sizeof fpt);
        int isnewfp = hs_add(&fps, fp ^ ((uint64_t)C.nc << 56)); fpnew += isnewfp;
        int fmin = -1;
        if (ts >= tmin) {
            Conf R; configurations(&C, tmin, &R);
            fmin = R.fmin[ts];
            if (fmin < fbest || ts > best_t) { if (ts >= best_t) { fbest = fmin; best_t = ts; } }
            int tf9 = R.nconf[tmin] ? R.fmin[tmin] : -1;
            if (outdir) { char p[1024]; snprintf(p, sizeof p, "%s/plateau_%06ld_t%d.txt", outdir, written, ts);
                write_code(p, C.I, C.n, "Stage 2.2 swap plateau code, scripts/s2_2_conf.c"); written++; }
            printf("%s{\"node\":%zu,\"depth\":%d,\"candidates\":%d,\"t_star\":%d,\"F_min_at_tstar\":%d,"
                   "\"F_min_at_tmin\":%d,\"fingerprint\":\"%016llx\",\"fp_text\":\"%s\",\"file_index\":%ld}",
                   firstrow ? "" : ",\n", qh - 1, depth, C.nc, ts, fmin, tf9, (unsigned long long)fp, fpt, outdir ? written - 1 : -1);
            firstrow = 0;
        }
        if (wall && outdir) { char p[1024]; snprintf(p, sizeof p, "%s/all_%06zu_t%d.txt", outdir, qh - 1, ts);
            write_code(p, C.I, C.n, "Stage 2.2 swap plateau code (all), scripts/s2_2_conf.c"); }
        if (qt >= (size_t)maxnodes) continue;
        /* 1-swaps */
        int nc = C.nc < MAXC ? C.nc : MAXC; int rr[MAXC], qq[MAXC];
        memcpy(rr, C.r, sizeof rr); memcpy(qq, C.q, sizeof qq);
        for (int j = 0; j < nc && qt < (size_t)maxnodes; j++) {
            uint64_t h = C.hash ^ zob[rr[j]] ^ zob[qq[j]];
            if (!hs_add(&seen, h)) continue;
            code_swap(&C, rr[j], qq[j]);
            memcpy(Q[qt], C.I, n * sizeof(int)); Qn[qt] = n; Qdepth[qt] = depth + 1; qt++;
            code_swap(&C, qq[j], rr[j]);
        }
        if (!k2) continue;
        /* 2-swaps: words w1 != w2 sharing a non-code vertex v with cnt 2 and N[v] cap I = {w1,w2};
           the vertices that can enter are those whose code-neighbours lie in {w1,w2} */
        for (int a = 0; a < n && qt < (size_t)maxnodes; a++) {
            int w1 = C.I[a];
            /* partners: words at distance <= 2 from w1 */
            static int part[1024]; int np = 0;
            static uint8_t mark[NV]; memset(mark, 0, NV);
            for (int m = 0; m < NB; m++) { int v = nbr[w1][m];
                for (int m2 = 0; m2 < NB; m2++) { int u = nbr[v][m2]; if (C.in[u] && u > w1 && !mark[u]) { mark[u] = 1; part[np++] = u; } } }
            for (int b = 0; b < np && qt < (size_t)maxnodes; b++) {
                int w2 = part[b];
                int V[1024], nv = 0;
                /* vertices v not in I with N[v] cap I subset of {w1,w2}, and v adjacent to at least one */
                static uint8_t mk[NV]; static int touched[2 * NB]; int nt = 0;
                for (int s = 0; s < 2; s++) { int w = s ? w2 : w1;
                    for (int m = 0; m < NB; m++) { int v = nbr[w][m]; if (C.in[v] || mk[v]) continue; mk[v] = 1; touched[nt++] = v;
                        int c = C.cnt[v], inside = adj_or_eq(v, w1) + adj_or_eq(v, w2);
                        if (c == inside) V[nv++] = v; } }
                for (int k = 0; k < nt; k++) mk[touched[k]] = 0;
                for (int x = 0; x < nv && qt < (size_t)maxnodes; x++) for (int y = x + 1; y < nv && qt < (size_t)maxnodes; y++) {
                    if (adj_or_eq(V[x], V[y])) continue;
                    k2moves++;
                    uint64_t h = C.hash ^ zob[w1] ^ zob[w2] ^ zob[V[x]] ^ zob[V[y]];
                    if (!hs_add(&seen, h)) continue;
                    k2new++;
                    code_swap(&C, w1, V[x]); code_swap(&C, w2, V[y]);
                    memcpy(Q[qt], C.I, n * sizeof(int)); Qn[qt] = n; Qdepth[qt] = depth + 1; qt++;
                    code_swap(&C, V[y], w2); code_swap(&C, V[x], w1);
                }
            }
        }
    }
    printf("\n],\"visited\":%zu,\"queued\":%zu,\"distinct_fingerprints\":%ld,\"written\":%ld,\"t_star_hist\":{", qh, qt, fpnew, written);
    int fr = 1; for (int t = 0; t <= MAXC; t++) if (hist_t[t]) { printf("%s\"%d\":%ld", fr ? "" : ",", t, hist_t[t]); fr = 0; }
    printf("},\"exhausted\":%s,\"k2\":%s,\"k2_moves\":%ld,\"k2_new\":%ld,\"seconds\":%.1f}\n", qt < (size_t)maxnodes ? "true" : "false", k2 ? "true" : "false", k2moves, k2new, now() - t0);
    return 0;
}

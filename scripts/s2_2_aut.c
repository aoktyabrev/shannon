/*
 * Stage 2.2 -- the automorphism group (D_7)^5 sd S_5 of C_7^5, used three ways.
 *
 *   s2_2_aut check                       anti-vacuum test of the generator itself
 *   s2_2_aut classes CODE...             exact isomorphism classes of codes under the
 *                                        group, with the order of each stabiliser
 *   s2_2_aut stab CODE                   every g with gI = I, one per line (perm signs shift)
 *   s2_2_aut apply CODE p0..p4 sg c0..c4 OUT   write g(I)
 *
 * An element is g(x)_i = s_i * x_{p(i)} + c_i (mod 7), s_i = +-1.  Isomorphism A -> B is
 * decided exactly: for each of the 3840 (p, s), the translation is forced by where one
 * fixed word a0 of A goes, so there are |B| translations to try, each refuted at the
 * first word that misses.
 *
 * Build: cc -O2 -march=native -fopenmp -o s2_2_aut s2_2_aut.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define N 7
#define D 5
#define NV 16807
#ifndef MAXI
#define MAXI 512
#endif

static int pw[D] = {1, 7, 49, 343, 2401};
static void dec(int v, int *c) { for (int i = 0; i < D; i++) { c[i] = v % N; v /= N; } }
static int enc(const int *c) { int v = 0; for (int i = 0; i < D; i++) v += c[i] * pw[i]; return v; }
static int adj_or_eq(int a, int b) {
    int ca[D], cb[D]; dec(a, ca); dec(b, cb);
    for (int i = 0; i < D; i++) { int t = (ca[i] - cb[i] + N) % N; if (t > 1 && t < N - 1) return 0; }
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
/* linear part (perm, signs) then translation */
static int lin(int v, const int *p, int sg) {
    int c[D], o[D]; dec(v, c);
    for (int i = 0; i < D; i++) o[i] = ((sg >> i) & 1) ? (N - c[p[i]]) % N : c[p[i]];
    return enc(o);
}
static int add(int v, int c) {
    int a[D], b[D]; dec(v, a); dec(c, b);
    for (int i = 0; i < D; i++) a[i] = (a[i] + b[i]) % N;
    return enc(a);
}
static int sub(int v, int c) {
    int a[D], b[D]; dec(v, a); dec(c, b);
    for (int i = 0; i < D; i++) a[i] = (a[i] - b[i] + N) % N;
    return enc(a);
}
static int gmap(int v, const int *p, int sg, int c) { return add(lin(v, p, sg), c); }

/* all g with gA = B; returns count, stores up to maxout of them */
typedef struct { int p, sg, c; } G;
static long isos(const int *A, int nA, const int *B, int nB, G *out, long maxout, int first_only) {
    if (nA != nB) return 0;
    uint8_t inB[NV]; memset(inB, 0, NV);
    for (int k = 0; k < nB; k++) inB[B[k]] = 1;
    long cnt = 0;
    int L[MAXI];
    for (int pi = 0; pi < nperm; pi++) for (int sg = 0; sg < 32; sg++) {
        for (int k = 0; k < nA; k++) L[k] = lin(A[k], perms[pi], sg);
        for (int b = 0; b < nB; b++) {
            int c = sub(B[b], L[0]);
            int ok = 1;
            for (int k = 1; k < nA && ok; k++) if (!inB[add(L[k], c)]) ok = 0;
            if (ok) { if (cnt < maxout) { out[cnt].p = pi; out[cnt].sg = sg; out[cnt].c = c; } cnt++;
                if (first_only) return cnt; }
        }
    }
    return cnt;
}

/* is the map v -> M[v] an automorphism: a bijection preserving adjacency, all 16807*242 pairs */
static int is_automorphism(const int *M) {
    static uint8_t hit[NV]; memset(hit, 0, NV);
    for (int v = 0; v < NV; v++) { if (M[v] < 0 || M[v] >= NV || hit[M[v]]) return 0; hit[M[v]] = 1; }
    for (int v = 0; v < NV; v++) {
        int c[D]; dec(v, c);
        for (int m = 0; m < 243; m++) { int mm = m, u[D];
            for (int i = 0; i < D; i++) { u[i] = (c[i] + mm % 3 - 1 + N) % N; mm /= 3; }
            int w = enc(u); if (w == v) continue;
            if (!adj_or_eq(M[v], M[w]) || M[v] == M[w]) return 0; }
    }
    return 1;
}

int main(int argc, char **argv) {
    make_perms();
    if (argc < 2) { fprintf(stderr, "usage\n"); return 2; }
    if (!strcmp(argv[1], "check")) {
        static int M[NV];
        int ident = 1, p[D] = {3, 0, 4, 1, 2}, sg = 0x15, c = enc((int[]){2, 5, 0, 6, 1});
        for (int v = 0; v < NV; v++) M[v] = gmap(v, p, sg, c);
        for (int v = 0; v < NV; v++) if (M[v] != v) ident = 0;
        int ok_g = is_automorphism(M);
        /* every element of the group, linear parts only (translations are clearly automorphisms) */
        int all = 1;
        for (int pi = 0; pi < nperm && all; pi += 7) for (int s = 0; s < 32 && all; s += 5) {
            for (int v = 0; v < NV; v++) M[v] = gmap(v, perms[pi], s, 0);
            all = is_automorphism(M); }
        /* the mutant x_0 -> 2 x_0 is a bijection but not an automorphism of C_7 */
        for (int v = 0; v < NV; v++) { int a[D]; dec(v, a); a[0] = (2 * a[0]) % N; M[v] = enc(a); }
        int mutant_rejected = !is_automorphism(M);
        /* a non-bijection must be rejected too */
        for (int v = 0; v < NV; v++) { int a[D]; dec(v, a); a[1] = a[1] / 2; M[v] = enc(a); }
        int collapse_rejected = !is_automorphism(M);
        printf("{\"test_element_is_identity\":%s,\"test_element_accepted\":%s,"
               "\"sampled_linear_parts_accepted\":%s,\"mutant_2x_rejected\":%s,\"collapse_rejected\":%s,"
               "\"passed\":%s}\n", ident ? "true" : "false", ok_g ? "true" : "false", all ? "true" : "false",
               mutant_rejected ? "true" : "false", collapse_rejected ? "true" : "false",
               (!ident && ok_g && all && mutant_rejected && collapse_rejected) ? "true" : "false");
        return 0;
    }
    if (!strcmp(argv[1], "apply")) {
        static int I[MAXI]; int n = read_code(argv[2], I);
        int p[D]; for (int i = 0; i < D; i++) p[i] = atoi(argv[3 + i]);
        int sg = atoi(argv[8]); int cc[D]; for (int i = 0; i < D; i++) cc[i] = atoi(argv[9 + i]);
        int c = enc(cc);
        FILE *f = fopen(argv[14], "w");
        fprintf(f, "# image of %s under x_i -> s_i x_{p(i)} + c_i, scripts/s2_2_aut.c\n%d %d %d\n", argv[2], N, D, n);
        for (int k = 0; k < n; k++) { int a[D]; dec(gmap(I[k], p, sg, c), a);
            fprintf(f, "%d %d %d %d %d\n", a[0], a[1], a[2], a[3], a[4]); }
        fclose(f); return 0;
    }
    if (!strcmp(argv[1], "stab")) {
        static int I[MAXI]; int n = read_code(argv[2], I);
        static G g[200000]; long k = isos(I, n, I, n, g, 200000, 0);
        printf("%ld\n", k);
        for (long i = 0; i < k && i < 200000; i++) { int *p = perms[g[i].p], c[D]; dec(g[i].c, c);
            printf("%d %d %d %d %d %d %d %d %d %d %d\n", p[0], p[1], p[2], p[3], p[4], g[i].sg, c[0], c[1], c[2], c[3], c[4]); }
        return 0;
    }
    if (!strcmp(argv[1], "classes")) {
        int nf = argc - 2;
        int (*S)[MAXI] = malloc(sizeof(int[MAXI]) * nf); int *ns = malloc(sizeof(int) * nf);
        int *cls = malloc(sizeof(int) * nf); int *rep = malloc(sizeof(int) * nf); int nrep = 0;
        for (int i = 0; i < nf; i++) ns[i] = read_code(argv[2 + i], S[i]);
        static G g1[1];
        for (int i = 0; i < nf; i++) {
            cls[i] = -1;
            int found = -1;
            #pragma omp parallel for schedule(dynamic)
            for (int r = 0; r < nrep; r++) {
                if (found >= 0) continue;
                G gg[1];
                if (isos(S[rep[r]], ns[rep[r]], S[i], ns[i], gg, 1, 1)) {
                    #pragma omp critical
                    if (found < 0 || r < found) found = r;
                }
            }
            if (found >= 0) cls[i] = found; else { cls[i] = nrep; rep[nrep++] = i; }
        }
        (void)g1;
        printf("{\"files\":%d,\"classes\":%d,\"rows\":[", nf, nrep);
        for (int i = 0; i < nf; i++) printf("%s[\"%s\",%d]", i ? "," : "", argv[2 + i], cls[i]);
        printf("],\"stabiliser_orders\":[");
        static G gs[200000];
        for (int r = 0; r < nrep; r++) printf("%s%ld", r ? "," : "", isos(S[rep[r]], ns[rep[r]], S[rep[r]], ns[rep[r]], gs, 0, 0));
        printf("]}\n");
        return 0;
    }
    return 2;
}

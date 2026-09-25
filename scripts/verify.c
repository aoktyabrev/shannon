/*
 * Exact independence verifier for strong powers of cycles, C_n^{boxtimes d}.
 *
 * Vertices are vectors in Z_n^d; two distinct vertices are adjacent iff in every
 * coordinate the circular distance is at most 1.  The verifier is exact: it uses
 * integer arithmetic only, never floating point.
 *
 * Method (cube packing).  For x in Z_n^d put  box(x) = prod_i {x_i, x_i+1 mod n}.
 * For n >= 4 and every coordinate,  {a,a+1} meets {b,b+1}  iff  b-a in {-1,0,1},
 * so two distinct vertices are adjacent iff their boxes meet.  Hence
 *
 *     I is independent  <=>  the |I| boxes are pairwise disjoint
 *                       <=>  the |I| * 2^d cells they occupy are all distinct.
 *
 * That turns the quadratic pair test into one linear sweep with an occupancy
 * bitmap over Z_n^d.  When n^d bits exceed the memory budget the universe is
 * split into chunks and swept once per chunk -- still exact, just more passes.
 * The quadratic test is kept as --quadratic and is used to calibrate the fast
 * path on small d, where both are affordable.
 *
 * Build: cc -O2 -o verify verify.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include "sha256.h"

#define MAXD 40

static double now(void) {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + 1e-9 * t.tv_nsec;
}

typedef struct {
    int n, d;
    long long size;
    unsigned char *v;      /* size*d coordinates */
    char sha[65];
    char path[4096];
} Set;

static void die(const char *m) { fprintf(stderr, "error: %s\n", m); exit(2); }

/* ---------- reading ---------- */

/* File format: comment lines start with '#'.  First non-comment line is "n d size",
   then `size` lines of d integers in [0,n). */
static void set_read(Set *s, const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "error: cannot open %s\n", path); exit(2); }
    snprintf(s->path, sizeof s->path, "%s", path);
    if (sha256_file(path, s->sha) != 0) die("sha256 failed");
    char line[1 << 16];
    int have_header = 0;
    long long got = 0;
    while (fgets(line, sizeof line, f)) {
        char *p = line;
        while (*p == ' ' || *p == '\t') p++;
        if (*p == '#' || *p == '\n' || *p == '\r' || *p == 0) continue;
        if (!have_header) {
            long long sz;
            if (sscanf(p, "%d %d %lld", &s->n, &s->d, &sz) != 3) die("bad header, expected: n d size");
            if (s->n < 4) die("n < 4 not supported (the box criterion needs n >= 4)");
            if (s->d < 1 || s->d > MAXD) die("d out of range");
            if (sz < 0) die("negative size");
            s->size = sz;
            s->v = malloc((size_t)sz * s->d);
            if (!s->v && sz) die("out of memory for the set");
            have_header = 1;
            continue;
        }
        if (got >= s->size) die("more vertices in the file than the header announces");
        for (int i = 0; i < s->d; i++) {
            while (*p == ' ' || *p == '\t') p++;
            if (*p < '0' || *p > '9') die("bad coordinate");
            long val = strtol(p, &p, 10);
            if (val < 0 || val >= s->n) die("coordinate out of [0,n)");
            s->v[(size_t)got * s->d + i] = (unsigned char)val;
        }
        got++;
    }
    fclose(f);
    if (!have_header) die("empty file");
    if (got != s->size) die("fewer vertices in the file than the header announces");
}

/* ---------- indexing ---------- */

static uint64_t g_pw[MAXD + 1];

static int universe(int n, int d, uint64_t *U) {
    unsigned __int128 u = 1;
    for (int i = 0; i < d; i++) {
        g_pw[i] = (uint64_t)u;
        u *= (unsigned)n;
        if (u > ((unsigned __int128)1 << 62)) return -1;
    }
    *U = (uint64_t)u;
    return 0;
}

static uint64_t vidx(const Set *s, long long k) {
    const unsigned char *x = s->v + (size_t)k * s->d;
    uint64_t r = 0;
    for (int i = 0; i < s->d; i++) r += (uint64_t)x[i] * g_pw[i];
    return r;
}

/* ---------- exact independence, box packing ---------- */

typedef struct {
    int independent;
    long long collisions;      /* occupied cells claimed twice */
    long long wit_a, wit_b;    /* a witnessing pair of vertex ids, -1 if none */
    double seconds;
    long long cells;           /* |I| * 2^d */
    int passes;
} IndepResult;

static void box_witness(const Set *s, uint64_t cell, long long *a, long long *b) {
    /* Which vertices own this cell?  Recomputed on demand, so the sweep itself
       needs no per-cell owner table. */
    *a = *b = -1;
    int d = s->d, n = s->n;
    uint64_t mask = (uint64_t)1 << d;
    for (long long k = 0; k < s->size; k++) {
        uint64_t base = vidx(s, k);
        int64_t up[MAXD];
        const unsigned char *x = s->v + (size_t)k * d;
        for (int i = 0; i < d; i++)
            up[i] = (x[i] == n - 1) ? -(int64_t)(n - 1) * (int64_t)g_pw[i] : (int64_t)g_pw[i];
        uint64_t cur = base, g = 0;
        if (cur == cell) { if (*a < 0) *a = k; else { *b = k; return; } }
        for (uint64_t m = 1; m < mask; m++) {
            uint64_t ng = m ^ (m >> 1), diff = ng ^ g;
            int bit = __builtin_ctzll(diff);
            cur = (ng & diff) ? cur + up[bit] : cur - up[bit];
            g = ng;
            if (cur == cell) { if (*a < 0) *a = k; else { *b = k; return; } }
        }
    }
}

static IndepResult check_independent(const Set *s, uint64_t budget_bytes, int verbose) {
    IndepResult r = {1, 0, -1, -1, 0, 0, 0};
    double t0 = now();
    int d = s->d, n = s->n;
    uint64_t U;
    if (universe(n, d, &U) != 0) die("n^d does not fit in 62 bits; this verifier cannot index that universe");
    if (d > 30) die("2^d too large");
    r.cells = s->size << d;

    uint64_t bytes_full = (U + 7) / 8;
    int passes = 1;
    uint64_t chunk = U;
    if (bytes_full > budget_bytes) {
        passes = (int)((bytes_full + budget_bytes - 1) / budget_bytes);
        chunk = (U + passes - 1) / passes;
    }
    r.passes = passes;
    uint64_t cb = (chunk + 7) / 8 + 8;
    uint8_t *bits = calloc(cb, 1);
    if (!bits) die("out of memory for the occupancy bitmap");

    uint64_t first_dup = 0;
    int have_dup = 0;
    uint64_t mask = (uint64_t)1 << d;
#ifdef MUTANT_DUPLICATES_ONLY
    /* Deliberate defect, compiled only into scripts/verify_mutant: the box shrinks to a
       single cell, so the sweep detects repeated vertices and nothing else.  It exists
       so that the calibration suite can be shown to have teeth -- see scripts/calibrate.py,
       test G.  It is never used to certify anything. */
    mask = 1;
#endif
    for (int p = 0; p < passes; p++) {
        uint64_t lo = (uint64_t)p * chunk, hi = lo + chunk;
        if (hi > U) hi = U;
        if (p) memset(bits, 0, cb);
        for (long long k = 0; k < s->size; k++) {
            const unsigned char *x = s->v + (size_t)k * d;
            uint64_t base = 0;
            int64_t up[MAXD];
            for (int i = 0; i < d; i++) {
                base += (uint64_t)x[i] * g_pw[i];
                up[i] = (x[i] == n - 1) ? -(int64_t)(n - 1) * (int64_t)g_pw[i] : (int64_t)g_pw[i];
            }
            uint64_t cur = base, g = 0;
            for (uint64_t m = 0; m < mask; m++) {
                if (m) {
                    uint64_t ng = m ^ (m >> 1), diff = ng ^ g;
                    int bit = __builtin_ctzll(diff);
                    cur = (ng & diff) ? cur + up[bit] : cur - up[bit];
                    g = ng;
                }
                if (cur < lo || cur >= hi) continue;
                uint64_t o = cur - lo;
                uint8_t *by = bits + (o >> 3);
                uint8_t bm = (uint8_t)(1u << (o & 7));
                if (*by & bm) {
                    r.collisions++;
                    if (!have_dup) { have_dup = 1; first_dup = cur; }
                } else *by |= bm;
            }
        }
        if (verbose && passes > 1) fprintf(stderr, "  pass %d/%d done\n", p + 1, passes);
    }
    free(bits);
    if (have_dup) {
        r.independent = 0;
        box_witness(s, first_dup, &r.wit_a, &r.wit_b);
    }
    r.seconds = now() - t0;
    return r;
}

/* ---------- reference check: plain quadratic pair test ---------- */

static int adjacent(const Set *s, long long i, long long j) {
    const unsigned char *a = s->v + (size_t)i * s->d, *b = s->v + (size_t)j * s->d;
    int n = s->n;
    for (int c = 0; c < s->d; c++) {
        int t = a[c] - b[c]; if (t < 0) t = -t;
        if (t > n - t) t = n - t;          /* circular distance */
        if (t > 1) return 0;
    }
    return 1;
}

static IndepResult check_quadratic(const Set *s) {
    IndepResult r = {1, 0, -1, -1, 0, 0, 1};
    double t0 = now();
    for (long long i = 0; i < s->size; i++)
        for (long long j = i + 1; j < s->size; j++)
            if (adjacent(s, i, j)) {
                r.collisions++;
                if (r.wit_a < 0) { r.wit_a = i; r.wit_b = j; r.independent = 0; }
            }
    r.seconds = now() - t0;
    return r;
}

/* ---------- maximality: is every vertex of Z_n^d confusable with the set? ---------- */

static void mark_nbhd(const Set *s, uint8_t *bits, uint64_t lo, uint64_t hi,
                      long long k, int coord, uint64_t cur) {
    if (coord == s->d) {
        if (cur >= lo && cur < hi) { uint64_t o = cur - lo; bits[o >> 3] |= (uint8_t)(1u << (o & 7)); }
        return;
    }
    int n = s->n;
    int xi = s->v[(size_t)k * s->d + coord];
    for (int t = -1; t <= 1; t++) {
        int c = xi + t; if (c < 0) c += n; if (c >= n) c -= n;
        mark_nbhd(s, bits, lo, hi, k, coord + 1, cur + (uint64_t)c * g_pw[coord]);
    }
}

/* Returns the number of vertices of Z_n^d that could be added to the set, and one of them. */
static long long count_addable(const Set *s, uint64_t budget_bytes, unsigned char *witness) {
    int d = s->d, n = s->n;
    uint64_t U;
    if (universe(n, d, &U) != 0) die("universe too large");
    uint64_t bytes_full = (U + 7) / 8;
    int passes = 1; uint64_t chunk = U;
    if (bytes_full > budget_bytes) {
        passes = (int)((bytes_full + budget_bytes - 1) / budget_bytes);
        chunk = (U + passes - 1) / passes;
    }
    uint64_t cb = (chunk + 7) / 8 + 8;
    uint8_t *bits = calloc(cb, 1);
    if (!bits) die("out of memory");
    long long free_cells = 0;
    uint64_t first_free = 0; int have = 0;
    for (int p = 0; p < passes; p++) {
        uint64_t lo = (uint64_t)p * chunk, hi = lo + chunk;
        if (hi > U) hi = U;
        if (p) memset(bits, 0, cb);
        for (long long k = 0; k < s->size; k++) mark_nbhd(s, bits, lo, hi, k, 0, 0);
        for (uint64_t o = 0; o < hi - lo; o++)
            if (!(bits[o >> 3] & (1u << (o & 7)))) {
                free_cells++;
                if (!have) { have = 1; first_free = lo + o; }
            }
    }
    free(bits);
    if (have && witness) {
        uint64_t z = first_free;
        for (int i = 0; i < d; i++) { witness[i] = (unsigned char)(z % (unsigned)n); z /= (unsigned)n; }
    }
    return free_cells;
}

/* ---------- output ---------- */

static void print_vec(FILE *f, const Set *s, long long k) {
    for (int i = 0; i < s->d; i++) fprintf(f, "%s%d", i ? "," : "", s->v[(size_t)k * s->d + i]);
}

static void usage(void) {
    fprintf(stderr,
        "usage: verify <file> [--quadratic] [--both] [--maximal] [--mem-mb M] [--json] [--repeat R]\n"
        "  file format: '# comments', then a line 'n d size', then size lines of d integers\n");
    exit(2);
}

int main(int argc, char **argv) {
    if (argc < 2) usage();
    const char *path = argv[1];
    int want_quad = 0, want_both = 0, want_max = 0, as_json = 0, repeat = 1;
    uint64_t budget = (uint64_t)1024 * 1024 * 1024;   /* 1 GiB default */
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--quadratic")) want_quad = 1;
        else if (!strcmp(argv[i], "--both")) want_both = 1;
        else if (!strcmp(argv[i], "--maximal")) want_max = 1;
        else if (!strcmp(argv[i], "--json")) as_json = 1;
        else if (!strcmp(argv[i], "--mem-mb") && i + 1 < argc) budget = (uint64_t)atoll(argv[++i]) * 1024 * 1024;
        else if (!strcmp(argv[i], "--repeat") && i + 1 < argc) repeat = atoi(argv[++i]);
        else usage();
    }
    Set s;
    set_read(&s, path);
    uint64_t U;
    if (universe(s.n, s.d, &U) != 0) die("n^d too large to index");

    IndepResult fast = {0}, quad = {0};
    int did_fast = 0, did_quad = 0;
    if (!want_quad || want_both) {
        for (int i = 0; i < repeat; i++) fast = check_independent(&s, budget, !as_json);
        did_fast = 1;
    }
    if (want_quad || want_both) { quad = check_quadratic(&s); did_quad = 1; }

    long long addable = -1;
    unsigned char wit[MAXD];
    if (want_max) addable = count_addable(&s, budget, wit);

    int indep = did_fast ? fast.independent : quad.independent;
    if (did_fast && did_quad && fast.independent != quad.independent)
        die("box test and quadratic test disagree -- verifier is broken");

    if (as_json) {
        printf("{\n");
        printf("  \"file\": \"%s\",\n", s.path);
        printf("  \"sha256\": \"%s\",\n", s.sha);
        printf("  \"n\": %d,\n  \"d\": %d,\n  \"size\": %lld,\n", s.n, s.d, s.size);
        printf("  \"universe\": %llu,\n", (unsigned long long)U);
        printf("  \"independent\": %s,\n", indep ? "true" : "false");
        if (did_fast) {
            printf("  \"box_collisions\": %lld,\n", fast.collisions);
            printf("  \"box_cells\": %lld,\n", fast.cells);
            printf("  \"box_passes\": %d,\n", fast.passes);
            printf("  \"box_seconds\": %.6f,\n", fast.seconds / (repeat ? repeat : 1));
            printf("  \"cells_per_second\": %.0f,\n", fast.cells * (double)(repeat ? repeat : 1) / (fast.seconds > 0 ? fast.seconds : 1e-9));
            printf("  \"vertices_per_second\": %.0f,\n", s.size * (double)(repeat ? repeat : 1) / (fast.seconds > 0 ? fast.seconds : 1e-9));
        }
        if (did_quad) {
            printf("  \"quadratic_run\": true,\n");
            printf("  \"quadratic_independent\": %s,\n", quad.independent ? "true" : "false");
            printf("  \"quadratic_seconds\": %.6f,\n", quad.seconds);
            printf("  \"agree\": %s,\n", (!did_fast || fast.independent == quad.independent) ? "true" : "false");
        } else printf("  \"quadratic_run\": false,\n");
        if (want_max) {
            printf("  \"addable_vertices\": %lld,\n", addable);
            printf("  \"maximal\": %s,\n", addable == 0 ? "true" : "false");
        }
        long long wa = did_fast ? fast.wit_a : quad.wit_a, wb = did_fast ? fast.wit_b : quad.wit_b;
        printf("  \"witness_pair\": ");
        if (wa >= 0 && wb >= 0) {
            printf("[["); for (int i = 0; i < s.d; i++) printf("%s%d", i?",":"", s.v[(size_t)wa*s.d+i]);
            printf("],["); for (int i = 0; i < s.d; i++) printf("%s%d", i?",":"", s.v[(size_t)wb*s.d+i]);
            printf("]]\n");
        } else printf("null\n");
        printf("}\n");
    } else {
        printf("file       : %s\n", s.path);
        printf("sha256     : %s\n", s.sha);
        printf("graph      : C_%d^%d   (universe %llu vertices)\n", s.n, s.d, (unsigned long long)U);
        printf("size       : %lld\n", s.size);
        if (did_fast) {
            printf("box test   : %s  (%lld cells, %d pass(es), %.3f s, %.3g cells/s)\n",
                   fast.independent ? "INDEPENDENT" : "NOT INDEPENDENT",
                   fast.cells, fast.passes, fast.seconds, fast.cells / (fast.seconds > 0 ? fast.seconds : 1e-9));
            if (!fast.independent) printf("collisions : %lld occupied cells claimed twice\n", fast.collisions);
        }
        if (did_quad)
            printf("quadratic  : %s  (%.3f s)%s\n", quad.independent ? "INDEPENDENT" : "NOT INDEPENDENT",
                   quad.seconds, did_fast ? (fast.independent == quad.independent ? "  [agrees]" : "  [DISAGREES]") : "");
        if (want_max) {
            printf("maximality : %s", addable == 0 ? "MAXIMAL (no vertex can be added)" : "NOT MAXIMAL");
            if (addable > 0) {
                printf(" -- %lld vertices could be added, e.g. (", addable);
                for (int i = 0; i < s.d; i++) printf("%s%d", i ? "," : "", wit[i]);
                printf(")");
            }
            printf("\n");
        }
        long long wa = did_fast ? fast.wit_a : quad.wit_a, wb = did_fast ? fast.wit_b : quad.wit_b;
        if (wa >= 0 && wb >= 0) {
            printf("witness    : ("); print_vec(stdout, &s, wa);
            printf(") ~ ("); print_vec(stdout, &s, wb); printf(")\n");
        }
        printf("result     : %s\n", indep ? "PASS" : "FAIL");
    }
    return indep ? 0 : 1;
}

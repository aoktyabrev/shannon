/*
 * Engine E2 of the Stage 1 search stack: iterated local search for large
 * independent sets in C_n^{boxtimes d}.
 *
 * Neighbourhood, in the standard form used for maximum independent set
 * (Andrade-Resende-Werneck): maintain an independent set S and the tightness
 * t(u) = |N(u) cap S| of every vertex outside it.
 *   - a free vertex (t = 0) is inserted, which always improves;
 *   - a (1,2)-swap removes one v in S and inserts two non-adjacent 1-tight
 *     neighbours of v, which improves by one;
 *   - a (1,1)-swap moves sideways across a plateau;
 *   - when nothing improves, a forced insertion perturbs the solution.
 * Adjacency is never stored: a neighbour of v is v + delta for delta in
 * {-1,0,1}^d \ {0}, computed per coordinate, which is what makes d = 5 (16807
 * vertices, degree 242) as cheap as d = 3.
 *
 * This engine proves nothing.  It finds sets, and every set it finds is written
 * out and handed to scripts/verify, which does not trust it.
 *
 * Build: cc -O2 -o s1_ils s1_ils.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <math.h>

static int N, D, NV, DEG;
static int *pw;
static int *nbuf;             /* scratch for the neighbours of one vertex */
static uint8_t *inS, *tight;
static int *Slist, *Spos, Ssize;

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+1e-9*t.tv_nsec; }

static uint64_t rs;
static uint32_t rnd(void) { rs ^= rs<<13; rs ^= rs>>7; rs ^= rs<<17; return (uint32_t)(rs>>32); }

/* neighbours of v (excluding v): write into out, return the count */
static int neighbours(int v, int *out) {
    int co[16], t = v;
    for (int i = 0; i < D; i++) { co[i] = t % N; t /= N; }
    int n = 0;
    for (int m = 0; m < DEG + 1; m++) {
        int mm = m, u = 0, all0 = 1;
        for (int i = 0; i < D; i++) {
            int dd = mm % 3 - 1; mm /= 3;
            if (dd) all0 = 0;
            int c = co[i] + dd; if (c < 0) c += N; if (c >= N) c -= N;
            u += c * pw[i];
        }
        if (!all0) out[n++] = u;
    }
    return n;
}

static void add(int v) {
    inS[v] = 1; Spos[v] = Ssize; Slist[Ssize++] = v;
    int nb[512], k = neighbours(v, nb);
    for (int i = 0; i < k; i++) tight[nb[i]]++;
}
static void del(int v) {
    inS[v] = 0;
    int p = Spos[v], last = Slist[--Ssize];
    Slist[p] = last; Spos[last] = p;
    int nb[512], k = neighbours(v, nb);
    for (int i = 0; i < k; i++) tight[nb[i]]--;
}

static int adjacent(int a, int b) {
    int ta = a, tb = b;
    for (int i = 0; i < D; i++) {
        int x = ta % N, y = tb % N; ta /= N; tb /= N;
        int dd = x - y; if (dd < 0) dd = -dd; if (dd > N - dd) dd = N - dd;
        if (dd > 1) return 0;
    }
    return 1;
}

/* insert every free vertex, in random order */
static void greedy_fill(void) {
    int moved = 1;
    while (moved) {
        moved = 0;
        int start = rnd() % NV;
        for (int i = 0; i < NV; i++) {
            int v = (start + i) % NV;
            if (!inS[v] && tight[v] == 0) { add(v); moved = 1; }
        }
    }
}

/* one pass of (1,2)-swaps; returns the number of improvements */
static int two_improve(void) {
    int gain = 0;
    for (int si = 0; si < Ssize; si++) {
        int v = Slist[si];
        int cand[512], nc = 0;
        int k = neighbours(v, nbuf);
        for (int i = 0; i < k; i++) { int u = nbuf[i]; if (!inS[u] && tight[u] == 1) cand[nc++] = u; }
        if (nc < 2) continue;
        int found = 0, a = 0, b = 0;
        for (int i = 0; i < nc && !found; i++)
            for (int j = i+1; j < nc; j++)
                if (!adjacent(cand[i], cand[j])) { a = cand[i]; b = cand[j]; found = 1; break; }
        if (found) { del(v); add(a); add(b); gain++; si = -1; }
    }
    return gain;
}

/* plateau: swap one out, one in */
static void one_swap_random(void) {
    if (!Ssize) return;
    int v = Slist[rnd() % Ssize];
    int k = neighbours(v, nbuf);
    int cand[512], nc = 0;
    for (int i = 0; i < k; i++) { int u = nbuf[i]; if (!inS[u] && tight[u] == 1) cand[nc++] = u; }
    if (!nc) return;
    int u = cand[rnd() % nc];
    del(v); add(u);
}

static void force_insert(int v) {
    int k = neighbours(v, nbuf);
    int rem[512], nr = 0;
    for (int i = 0; i < k; i++) if (inS[nbuf[i]]) rem[nr++] = nbuf[i];
    for (int i = 0; i < nr; i++) del(rem[i]);
    if (!inS[v]) add(v);
}

/* ---------------------------------------------------------------------------
 * Fixed-cardinality annealing.  Instead of growing an independent set, hold
 * exactly K vertices and minimise the number of adjacent pairs among them,
 * moving one vertex at a time.  Cost 0 means an independent set of size K.
 * This is the formulation under which Vesel and Zerovnik reached 108 on
 * C_7^{boxtimes 4} with simulated annealing [SOURCES.md MO17-4]; the local
 * search above stalls at 102 there.
 * ------------------------------------------------------------------------- */
static int *conf;                 /* conf[v] = |N(v) cap S| */
static int *Sarr; static int K;

static long cost_now;

static void sa_add(int v) {
    inS[v] = 1; cost_now += conf[v];
    int k = neighbours(v, nbuf);
    for (int i = 0; i < k; i++) conf[nbuf[i]]++;
}
static void sa_del(int v) {
    inS[v] = 0; cost_now -= conf[v];
    int k = neighbours(v, nbuf);
    for (int i = 0; i < k; i++) conf[nbuf[i]]--;
}


/* ---------------------------------------------------------------------------
 * Exact window repair on a fixed-cardinality state (engines E2 and E4 joined).
 * Take a box window that contains a conflicted vertex, delete every chosen
 * vertex inside it, and solve maximum independent set on the freed cells
 * exactly.  If the window can host as many vertices as were deleted, every
 * conflict with an endpoint inside the window disappears at once -- a move no
 * sequence of single swaps can make.  Unlike the same move on a conflict-free
 * state, success is not automatic here: the deleted vertices were not
 * independent, so the exact answer can be smaller than what was removed.
 * ------------------------------------------------------------------------- */
#define FW 12
#define FMAX 768
static uint64_t (*fadj)[FW];
static int fbest, *fcur, *fbestset, fcurn, fn;
static long fnodes, fnodecap = 3000000;

static int fpc(const uint64_t*a){int c=0;for(int i=0;i<FW;i++)c+=__builtin_popcountll(a[i]);return c;}
static int clique_cover(const uint64_t *cand){
    uint64_t rem[FW]; memcpy(rem,cand,sizeof rem); int cl=0;
    for(;;){ int v=-1;
        for(int i=0;i<FW&&v<0;i++) if(rem[i]) v=i*64+__builtin_ctzll(rem[i]);
        if(v<0) break; cl++;
        uint64_t com[FW]; for(int i=0;i<FW;i++) com[i]=rem[i]&fadj[v][i];
        rem[v>>6]&=~(1ULL<<(v&63));
        for(;;){ int u=-1;
            for(int i=0;i<FW&&u<0;i++) if(com[i]) u=i*64+__builtin_ctzll(com[i]);
            if(u<0) break;
            rem[u>>6]&=~(1ULL<<(u&63));
            for(int i=0;i<FW;i++) com[i]&=fadj[u][i]; } }
    return cl;
}
static void fexpand(uint64_t *cand){
    if(++fnodes>fnodecap) return;
    if(fpc(cand)==0){ if(fcurn>fbest){fbest=fcurn;memcpy(fbestset,fcur,sizeof(int)*fcurn);} return; }
    if(fcurn+clique_cover(cand)<=fbest) return;
    int piv=-1,pd=-1;
    for(int i=0;i<FW;i++){ uint64_t m=cand[i];
        while(m){int v=i*64+__builtin_ctzll(m);m&=m-1;int dg=0;
            for(int j=0;j<FW;j++) dg+=__builtin_popcountll(cand[j]&fadj[v][j]);
            if(dg>pd){pd=dg;piv=v;} } }
    uint64_t sub[FW];
    for(int i=0;i<FW;i++) sub[i]=cand[i]&~fadj[piv][i];
    sub[piv>>6]&=~(1ULL<<(piv&63));
    fcur[fcurn++]=piv; fexpand(sub); fcurn--;
    memcpy(sub,cand,sizeof sub); sub[piv>>6]&=~(1ULL<<(piv&63));
    fexpand(sub);
}

/* returns 1 if the state changed */
static int window_repair(int *Sa, int Kc, int wlo, int whi) {
    /* centre the window on a conflicted member */
    int v = -1;
    for (int t = 0; t < 400 && v < 0; t++) { int j = rnd()%Kc; if (conf[Sa[j]] > 0) v = Sa[j]; }
    if (v < 0) return 0;
    int co[16], lo[16], w[16], cells = 1;
    { int tv = v; for (int i=0;i<D;i++){ co[i]=tv%N; tv/=N; } }
    for (int i=0;i<D;i++){ w[i]=wlo+rnd()%(whi-wlo+1); lo[i]=(co[i]-rnd()%w[i]+N)%N; cells*=w[i]; }
    if (cells > 4096) return 0;
    static int win[4096]; int nw=0;
    for (int m=0;m<cells;m++){ int mm=m,u=0;
        for(int i=0;i<D;i++){ int off=mm%w[i]; mm/=w[i]; u += ((lo[i]+off)%N)*pw[i]; }
        win[nw++]=u; }
    int idx[512], nr=0;
    for (int i=0;i<nw;i++) if (inS[win[i]]) { if (nr>=512) return 0; idx[nr++]=win[i]; }
    if (nr == 0) return 0;
    long cost_before = cost_now;
    for (int i=0;i<nr;i++) sa_del(idx[i]);
    static int freev[FMAX]; fn = 0;
    for (int i=0;i<nw && fn<FMAX;i++){ int u=win[i];
        if (inS[u] || conf[u]) continue;          /* blocked by something outside */
        freev[fn++]=u; }
    if (fn < nr) { for (int i=0;i<nr;i++) sa_add(idx[i]); return 0; }
    memset(fadj,0,sizeof(uint64_t)*(size_t)fn*FW);
    for (int i=0;i<fn;i++) for (int j=i+1;j<fn;j++)
        if (adjacent(freev[i],freev[j])) { fadj[i][j>>6]|=1ULL<<(j&63); fadj[j][i>>6]|=1ULL<<(i&63); }
    uint64_t cand[FW]; memset(cand,0,sizeof cand);
    for (int i=0;i<fn;i++) cand[i>>6]|=1ULL<<(i&63);
    fbest=0; fcurn=0; fnodes=0;
    fexpand(cand);
    if (fbest >= nr) {
        int k = 0;
        for (int i=0;i<nr;i++) { int u = freev[fbestset[k++]]; sa_add(u);
            for (int j=0;j<Kc;j++) if (Sa[j]==idx[i]) { Sa[j]=u; break; } }
        if (cost_now < cost_before) return 1;
        return 1;
    }
    for (int i=0;i<nr;i++) sa_add(idx[i]);
    return 0;
}

static const char *ANNEAL_START = NULL;

static int anneal(int k_target, double limit, int *outset, long *restarts) {
    /* Min-conflicts tabu search on a fixed-cardinality state.
     * A move takes a conflicted vertex out of S and puts a vertex of minimum
     * conflict count in; the vertex that left is tabu for a short random spell,
     * with the usual aspiration when a move would finish the job.  Choosing the
     * incoming vertex by a full scan rather than at random is what separates this
     * from the annealing first tried here, which stalled around 50 conflicts. */
    K = k_target;
    Sarr = malloc(sizeof(int)*K);
    conf = calloc(NV, sizeof(int));
    long *tabu = calloc(NV, sizeof(long));
    memset(inS, 0, NV);
    cost_now = 0;
    int n = 0;
    if (ANNEAL_START) {        /* warm start from a smaller verified set, topped up at random */
        FILE *f = fopen(ANNEAL_START, "r");
        if (!f) { fprintf(stderr, "cannot open %s\n", ANNEAL_START); exit(2); }
        char line[4096]; int have = 0, n2, d2; long sz;
        while (fgets(line, sizeof line, f) && n < K) {
            char *p2 = line; while (*p2==' '||*p2=='\t') p2++;
            if (*p2=='#'||*p2=='\n'||*p2=='\r'||!*p2) continue;
            if (!have) { sscanf(p2, "%d %d %ld", &n2, &d2, &sz); have = 1; continue; }
            int v = 0;
            for (int i = 0; i < D; i++) { while (*p2==' ') p2++; v += (int)strtol(p2,&p2,10) * pw[i]; }
            if (!inS[v]) { sa_add(v); Sarr[n++] = v; }
        }
        fclose(f);
    }
    while (n < K) { int v = rnd() % NV; if (!inS[v]) { sa_add(v); Sarr[n++] = v; } }
    double t0 = now();
    long best = cost_now, iter = 0, since = 0;
    int WREP = getenv("WREP") ? atoi(getenv("WREP")) : 0;   /* 1 window repair per WREP moves */
    int WLO = getenv("WLO") ? atoi(getenv("WLO")) : 3;
    int WHI = getenv("WHI") ? atoi(getenv("WHI")) : 4;
    if (WREP) { fadj = malloc(sizeof(uint64_t)*FMAX*FW); fcur = malloc(sizeof(int)*FMAX);
                fbestset = malloc(sizeof(int)*FMAX); }
    int TEN_B = getenv("TEN_B") ? atoi(getenv("TEN_B")) : 4;
    int TEN_R = getenv("TEN_R") ? atoi(getenv("TEN_R")) : 12;
    int STAG  = getenv("STAG")  ? atoi(getenv("STAG"))  : 60000;
    int KICKD = getenv("KICKD") ? atoi(getenv("KICKD")) : 6;
    int PNC   = getenv("PNC")   ? atoi(getenv("PNC"))   : 0;   /* % chance to move a clean vertex */
    int *bestset = malloc(sizeof(int)*K);
    memcpy(bestset, Sarr, sizeof(int)*K);
    *restarts = 0;
    while (cost_now > 0 && now() - t0 < limit) {
        iter++; since++;
        /* a conflicted member of S */
        int pi = -1;
        if (PNC && (int)(rnd() % 100) < PNC) pi = rnd() % K;
        for (int tries = 0; pi < 0 && tries < 200; tries++) {
            int j = rnd() % K;
            if (conf[Sarr[j]] > 0) { pi = j; break; }
        }
        if (pi < 0) { for (int j = 0; j < K; j++) if (conf[Sarr[j]] > 0) { pi = j; break; } }
        if (pi < 0) break;
        int v = Sarr[pi];
        long bd = 1L<<40; int bu = -1, ties = 0;
        for (int u = 0; u < NV; u++) {
            if (inS[u]) continue;
            long delta = (long)conf[u] - (adjacent(u,v) ? 1 : 0) - (long)conf[v];
            int is_tabu = tabu[u] > iter;
            if (is_tabu && cost_now + delta > 0) continue;      /* aspiration */
            if (delta < bd) { bd = delta; bu = u; ties = 1; }
            else if (delta == bd && (rnd() % ++ties) == 0) bu = u;
        }
        if (bu < 0) { tabu[v] = 0; continue; }
        sa_del(v); sa_add(bu); Sarr[pi] = bu;
        tabu[v] = iter + TEN_B + rnd() % (TEN_R ? TEN_R : 1);
        if (WREP && (iter % WREP) == 0) {
            if (window_repair(Sarr, K, WLO, WHI) && cost_now < best) {
                best = cost_now; memcpy(bestset, Sarr, sizeof(int)*K); since = 0;
            }
        }
        if (cost_now < best) { best = cost_now; memcpy(bestset, Sarr, sizeof(int)*K); since = 0; }
        if (since > STAG) {                                     /* stagnation: kick */
            (*restarts)++;
            since = 0;
            for (int i = 0; i < K/(KICKD ? KICKD : 6); i++) {
                int j = rnd() % K, w;
                do { w = rnd() % NV; } while (inS[w]);
                sa_del(Sarr[j]); sa_add(w); Sarr[j] = w;
            }
        }
    }
    int ok = (cost_now == 0);
    memcpy(outset, ok ? Sarr : bestset, sizeof(int)*K);
    return ok ? 0 : (int)best;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: s1_ils n d [--target T] [--seconds S] [--seed X] [--out FILE] [--json]\n"); return 2; }
    N = atoi(argv[1]); D = atoi(argv[2]);
    int target = 1 << 30; double limit = 60.0; int as_json = 0, anneal_k = 0;
    const char *out = NULL, *start = NULL;
    rs = 88172645463325252ULL;
    for (int i = 3; i < argc; i++) {
        if (!strcmp(argv[i], "--target") && i+1 < argc) target = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--seconds") && i+1 < argc) limit = atof(argv[++i]);
        else if (!strcmp(argv[i], "--seed") && i+1 < argc) rs = (uint64_t)atoll(argv[++i]) * 2862933555777941757ULL + 3037000493ULL;
        else if (!strcmp(argv[i], "--out") && i+1 < argc) out = argv[++i];
        else if (!strcmp(argv[i], "--start") && i+1 < argc) start = argv[++i];
        else if (!strcmp(argv[i], "--anneal") && i+1 < argc) anneal_k = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--json")) as_json = 1;
    }
    NV = 1; DEG = 1;
    pw = malloc(sizeof(int) * (D+1));
    for (int i = 0; i < D; i++) { pw[i] = NV; NV *= N; DEG *= 3; }
    DEG -= 1;
    nbuf = malloc(sizeof(int) * (DEG + 2));
    inS = calloc(NV,1); tight = calloc(NV,1);
    Slist = malloc(sizeof(int)*NV); Spos = malloc(sizeof(int)*NV); Ssize = 0;

    int *best = malloc(sizeof(int)*NV); int bestn = 0;
    double t0 = now(); long iters = 0;
    if (anneal_k) {
        ANNEAL_START = start;
        long rst = 0;
        int residual = anneal(anneal_k, limit, best, &rst);
        double ela = now() - t0;
        if (residual == 0) bestn = anneal_k;
        if (out && residual == 0) {
            FILE *f = fopen(out, "w");
            fprintf(f, "# Independent set of size %d in C_%d^{boxtimes %d}.\n", anneal_k, N, D);
            fprintf(f, "# Found by scripts/s1_ils --anneal (engine E2, fixed-cardinality annealing),\n");
            fprintf(f, "# %.1f s, %ld cooling runs.  Independence is NOT asserted here: see scripts/verify.\n", ela, rst);
            fprintf(f, "%d %d %d\n", N, D, anneal_k);
            for (int i = 1; i < anneal_k; i++) { int x = best[i], j = i-1;
                while (j >= 0 && best[j] > x) { best[j+1] = best[j]; j--; } best[j+1] = x; }
            for (int i = 0; i < anneal_k; i++) { int t = best[i];
                for (int j = 0; j < D; j++) { fprintf(f, "%s%d", j?" ":"", t % N); t /= N; }
                fprintf(f, "\n"); }
            fclose(f);
        }
        if (as_json)
            printf("{\"n\":%d,\"d\":%d,\"mode\":\"anneal\",\"k\":%d,\"conflicts_left\":%d,"
                   "\"reached\":%s,\"seconds\":%.2f,\"cooling_runs\":%ld,\"out\":%s%s%s}\n",
                   N, D, anneal_k, residual, residual==0?"true":"false", ela, rst,
                   out?"\"":"", out?out:"null", out?"\"":"");
        else
            printf("C_%d^%d anneal k=%d: %s (%d conflicts left) in %.1f s, %ld cooling runs\n",
                   N, D, anneal_k, residual==0?"INDEPENDENT SET FOUND":"failed", residual, ela, rst);
        return residual == 0 ? 0 : 1;
    }
    if (start) {          /* warm start: continue from a set someone else found */
        FILE *f = fopen(start, "r");
        if (!f) { fprintf(stderr, "cannot open %s\n", start); return 2; }
        char line[4096]; int have = 0, n2, d2; long sz;
        while (fgets(line, sizeof line, f)) {
            char *p2 = line; while (*p2==' '||*p2=='\t') p2++;
            if (*p2=='#'||*p2=='\n'||*p2=='\r'||!*p2) continue;
            if (!have) { sscanf(p2, "%d %d %ld", &n2, &d2, &sz); have = 1;
                         if (n2!=N||d2!=D) { fprintf(stderr,"start set has the wrong shape\n"); return 2; }
                         continue; }
            int v = 0;
            for (int i = 0; i < D; i++) { while (*p2==' ') p2++; v += (int)strtol(p2,&p2,10) * pw[i]; }
            if (!inS[v] && tight[v]==0) add(v);
        }
        fclose(f);
        bestn = Ssize; memcpy(best, Slist, sizeof(int)*Ssize);
    }
    greedy_fill();
    while (now() - t0 < limit) {
        iters++;
        greedy_fill();
        while (two_improve()) greedy_fill();
        if (Ssize > bestn) {
            bestn = Ssize; memcpy(best, Slist, sizeof(int)*Ssize);
            if (bestn >= target) break;
        }
        /* perturb: a few plateau moves, then a forced insertion */
        int p = 1 + rnd() % 3;
        for (int i = 0; i < p; i++) one_swap_random();
        force_insert(rnd() % NV);
    }
    double el = now() - t0;

    if (out) {
        FILE *f = fopen(out, "w");
        fprintf(f, "# Independent set of size %d in C_%d^{boxtimes %d}.\n", bestn, N, D);
        fprintf(f, "# Found by scripts/s1_ils (engine E2, iterated local search), seed-driven,\n");
        fprintf(f, "# %.1f s, %ld restarts.  Independence is NOT asserted here: see scripts/verify.\n", el, iters);
        fprintf(f, "%d %d %d\n", N, D, bestn);
        /* sort for a deterministic file */
        for (int i = 1; i < bestn; i++) { int x = best[i], j = i-1;
            while (j >= 0 && best[j] > x) { best[j+1] = best[j]; j--; } best[j+1] = x; }
        for (int i = 0; i < bestn; i++) {
            int t = best[i];
            for (int j = 0; j < D; j++) { fprintf(f, "%s%d", j?" ":"", t % N); t /= N; }
            fprintf(f, "\n");
        }
        fclose(f);
    }
    if (as_json)
        printf("{\"n\":%d,\"d\":%d,\"vertices\":%d,\"best\":%d,\"target\":%d,\"reached\":%s,"
               "\"seconds\":%.2f,\"restarts\":%ld,\"out\":%s%s%s}\n",
               N, D, NV, bestn, target == (1<<30) ? -1 : target,
               bestn >= target ? "true" : "false", el, iters,
               out ? "\"" : "", out ? out : "null", out ? "\"" : "");
    else
        printf("C_%d^%d: best %d (target %d) in %.1f s, %ld restarts%s%s\n",
               N, D, bestn, target == (1<<30) ? -1 : target, el, iters,
               out ? " -> " : "", out ? out : "");
    return bestn >= target ? 0 : 1;
}

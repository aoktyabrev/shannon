/*
 * Engine E3 of the Stage 1 search stack: prescribed-symmetry search.
 *
 * Plain local search (engine E2) stalls at 102 on C_7^{boxtimes 4}, well short of
 * the published 108.  That is the wall the literature describes: Mathew and
 * Ostergard reach d = 5 only by "prescribing symmetries of packings"
 * [SOURCES.md MO17-5], and Itty et al. report their own simulated annealing
 * failing for months [IRCR26-7].  So the search is moved to the quotient.
 *
 * A group G <= Aut(C_n^{boxtimes d}) is given by explicit generators
 *
 *     g(x)_i = s_i * x_{p_i} + c_i   (mod n),    s_i in {+1,-1},
 *
 * which preserve circular distance in every coordinate and are therefore
 * automorphisms.  Both facts are checked here, not assumed: every generator is
 * tested against every edge, and a generator that acts as the identity is
 * rejected as an error rather than accepted as a symmetry.
 *
 * G-invariant independent sets correspond exactly to independent sets of the
 * orbit graph -- orbits that are internally independent, pairwise non-adjacent --
 * weighted by orbit size.  That graph is |G| times smaller, which is the whole
 * point.  The weighted search on it is the same ARW local search as E2.
 *
 * The result is still only a candidate: it is written out and handed to
 * scripts/verify, which knows nothing about groups.
 *
 * Build: cc -O2 -o s1_sym s1_sym.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXD 8
#define MAXG 8

static int N, D, NV, DEG, *pw;
static int n_gen;
static int gp[MAXG][MAXD], gs[MAXG][MAXD], gc[MAXG][MAXD];

static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+1e-9*t.tv_nsec;}
static uint64_t rs = 88172645463325252ULL;
static uint32_t rnd(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)(rs>>32);}

static void decode(int v, int *co){ for (int i=0;i<D;i++){ co[i]=v%N; v/=N; } }
static int encode(const int *co){ int v=0; for(int i=0;i<D;i++) v+=co[i]*pw[i]; return v; }

static int FAKE_GEN = 0;   /* installs a non-automorphism, so that the check can be shown to bite */

static int apply_gen(int g, int v) {
    if (FAKE_GEN) return (v + 1) % NV;    /* a shift of the vertex INDEX: not a graph map */
    int co[MAXD], out[MAXD];
    decode(v, co);
    for (int i = 0; i < D; i++) {
        int t = gs[g][i] * co[gp[g][i]] + gc[g][i];
        t %= N; if (t < 0) t += N;
        out[i] = t;
    }
    return encode(out);
}
static int adjacent(int a, int b) {
    if (a == b) return 0;
    int ca[MAXD], cb[MAXD]; decode(a,ca); decode(b,cb);
    for (int i = 0; i < D; i++) {
        int t = ca[i]-cb[i]; if (t<0) t=-t; if (t>N-t) t=N-t;
        if (t > 1) return 0;
    }
    return 1;
}
static int neighbours(int v, int *out) {
    int co[MAXD]; decode(v, co);
    int n = 0, tot = 1;
    for (int i = 0; i < D; i++) tot *= 3;
    for (int m = 0; m < tot; m++) {
        int mm = m, u = 0, all0 = 1;
        for (int i = 0; i < D; i++) {
            int dd = mm%3 - 1; mm /= 3;
            if (dd) all0 = 0;
            int c = co[i]+dd; if (c<0) c+=N; if (c>=N) c-=N;
            u += c*pw[i];
        }
        if (!all0) out[n++] = u;
    }
    return n;
}

/* ---------- union-find over orbits ---------- */
static int *uf;
static int find(int x){ while(uf[x]!=x){ uf[x]=uf[uf[x]]; x=uf[x]; } return x; }
static void uni(int a,int b){ a=find(a); b=find(b); if(a!=b) uf[a]=b; }

/* ---------- weighted local search on the orbit graph ---------- */
static int on;                       /* orbit-graph vertices */
static int *ow;                      /* weight = orbit size */
static int **oadj, *odeg;
static uint8_t *inS; static int *tight;
static int *Slist,*Spos,Ssize; static long Sw;

static void oadd(int v){ inS[v]=1; Spos[v]=Ssize; Slist[Ssize++]=v; Sw+=ow[v];
    for(int i=0;i<odeg[v];i++) tight[oadj[v][i]]++; }
static void odel(int v){ inS[v]=0; Sw-=ow[v]; int p=Spos[v],last=Slist[--Ssize];
    Slist[p]=last; Spos[last]=p; for(int i=0;i<odeg[v];i++) tight[oadj[v][i]]--; }
static int oadjacent(int a,int b){ for(int i=0;i<odeg[a];i++) if(oadj[a][i]==b) return 1; return 0; }

static void greedy(void){
    int moved=1;
    while(moved){ moved=0; int st=rnd()%on;
        for(int k=0;k<on;k++){ int v=(st+k)%on; if(!inS[v]&&tight[v]==0){ oadd(v); moved=1; } } }
}
static int improve(void){
    int gain=0;
    for(int si=0; si<Ssize; si++){
        int v=Slist[si], cand[256], nc=0;
        for(int i=0;i<odeg[v] && nc<256;i++){ int u=oadj[v][i]; if(!inS[u]&&tight[u]==1) cand[nc++]=u; }
        if(nc<2) continue;
        /* best independent pair among the 1-tight neighbours */
        int ba=-1,bb=-1; long bw=ow[v];
        for(int i=0;i<nc;i++) for(int j=i+1;j<nc;j++)
            if(!oadjacent(cand[i],cand[j]) && (long)ow[cand[i]]+ow[cand[j]]>bw){
                bw=(long)ow[cand[i]]+ow[cand[j]]; ba=cand[i]; bb=cand[j]; }
        if(ba>=0){ odel(v); oadd(ba); oadd(bb); gain++; si=-1; }
    }
    return gain;
}
static void plateau(void){
    if(!Ssize) return;
    int v=Slist[rnd()%Ssize], cand[256], nc=0;
    for(int i=0;i<odeg[v]&&nc<256;i++){ int u=oadj[v][i]; if(!inS[u]&&tight[u]==1&&ow[u]>=ow[v]) cand[nc++]=u; }
    if(!nc) return;
    int u=cand[rnd()%nc]; odel(v); oadd(u);
}
static void force(int v){
    int rem[256], nr=0;
    for(int i=0;i<odeg[v];i++) if(inS[oadj[v][i]] && nr<256) rem[nr++]=oadj[v][i];
    for(int i=0;i<nr;i++) odel(rem[i]);
    if(!inS[v]) oadd(v);
}

/* ---------------------------------------------------------------------------
 * Fixed-cardinality tabu search on the orbit graph.  Pick exactly K orbits, all
 * of the same size, and minimise the number of adjacent orbit pairs among them.
 * Cost 0 gives a G-invariant independent set of |G|*K vertices.  This is the same
 * move as scripts/s1_ils --anneal, run on a graph that the symmetry has made
 * |G| times smaller.
 * ------------------------------------------------------------------------- */
static int *oconf;
static long ocost;
static void t_add(int v){ inS[v]=1; ocost += oconf[v]; for(int i=0;i<odeg[v];i++) oconf[oadj[v][i]]++; }
static void t_del(int v){ inS[v]=0; ocost -= oconf[v]; for(int i=0;i<odeg[v];i++) oconf[oadj[v][i]]--; }

static int orbit_tabu(int K, double limit, int *pool, int npool, int *outset, long *kicks) {
    oconf = calloc(on, sizeof(int));
    long *tabu = calloc(on, sizeof(long));
    int *cur = malloc(sizeof(int)*K);
    memset(inS, 0, on);
    ocost = 0;
    if (npool < K) return -1;
    for (int i = 0; i < K; i++) { int v; do { v = pool[rnd()%npool]; } while (inS[v]); t_add(v); cur[i]=v; }
    double t0 = now();
    long best = ocost, iter = 0, since = 0;
    int *bestset = malloc(sizeof(int)*K); memcpy(bestset, cur, sizeof(int)*K);
    *kicks = 0;
    while (ocost > 0 && now()-t0 < limit) {
        iter++; since++;
        int pi = -1;
        for (int t = 0; t < 200 && pi < 0; t++) { int j = rnd()%K; if (oconf[cur[j]] > 0) pi = j; }
        if (pi < 0) { for (int j = 0; j < K; j++) if (oconf[cur[j]]>0) { pi=j; break; } }
        if (pi < 0) break;
        int v = cur[pi];
        long bd = 1L<<40; int bu = -1, ties = 0;
        for (int q = 0; q < npool; q++) {
            int u = pool[q];
            if (inS[u]) continue;
            int adj = 0;
            for (int i = 0; i < odeg[u]; i++) if (oadj[u][i]==v) { adj = 1; break; }
            long delta = (long)oconf[u] - adj - (long)oconf[v];
            if (tabu[u] > iter && ocost + delta > 0) continue;
            if (delta < bd) { bd = delta; bu = u; ties = 1; }
            else if (delta == bd && (rnd() % ++ties) == 0) bu = u;
        }
        if (bu < 0) { tabu[v] = 0; continue; }
        t_del(v); t_add(bu); cur[pi] = bu;
        tabu[v] = iter + 4 + rnd()%12;
        if (ocost < best) { best = ocost; memcpy(bestset, cur, sizeof(int)*K); since = 0; }
        if (since > 40000) {
            (*kicks)++; since = 0;
            for (int i = 0; i < K/6 + 1; i++) {
                int j = rnd()%K, w; int guard=0;
                do { w = pool[rnd()%npool]; } while (inS[w] && ++guard < 200);
                if (inS[w]) continue;
                t_del(cur[j]); t_add(w); cur[j]=w;
            }
        }
    }
    int ok = (ocost == 0);
    memcpy(outset, ok ? cur : bestset, sizeof(int)*K);
    return ok ? 0 : (int)best;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr,
        "usage: s1_sym n d --gen p0,..,pd-1:s0,..:c0,.. [--gen ...] [--seconds S] [--seed X] [--target T] [--out F] [--json]\n"); return 2; }
    N = atoi(argv[1]); D = atoi(argv[2]);
    double limit = 30.0; int target = 1<<30, as_json = 0, want_orbits = 0; const char *out = NULL;
    for (int i = 3; i < argc; i++) {
        if (!strcmp(argv[i],"--gen") && i+1<argc) {
            char buf[256]; snprintf(buf,sizeof buf,"%s",argv[++i]);
            char *parts[3] = {0,0,0}; int np=0;
            for (char *t = strtok(buf,":"); t && np<3; t = strtok(NULL,":")) parts[np++]=t;
            if (np!=3) { fprintf(stderr,"bad --gen\n"); return 2; }
            for (int f=0; f<3; f++) {
                int k=0; char *save=NULL;
                for (char *t=strtok_r(parts[f],",",&save); t && k<D; t=strtok_r(NULL,",",&save)) {
                    int val=atoi(t);
                    if (f==0) gp[n_gen][k]=val; else if (f==1) gs[n_gen][k]=val; else gc[n_gen][k]=val;
                    k++;
                }
                if (k!=D) { fprintf(stderr,"bad --gen field length\n"); return 2; }
            }
            n_gen++;
        }
        else if (!strcmp(argv[i],"--seconds")&&i+1<argc) limit=atof(argv[++i]);
        else if (!strcmp(argv[i],"--seed")&&i+1<argc) rs=(uint64_t)atoll(argv[++i])*2862933555777941757ULL+3037000493ULL;
        else if (!strcmp(argv[i],"--target")&&i+1<argc) target=atoi(argv[++i]);
        else if (!strcmp(argv[i],"--out")&&i+1<argc) out=argv[++i];
        else if (!strcmp(argv[i],"--json")) as_json=1;
        else if (!strcmp(argv[i],"--orbits") && i+1<argc) want_orbits = atoi(argv[++i]);
        else if (!strcmp(argv[i],"--fake-gen")) FAKE_GEN = 1;
    }
    NV=1; pw=malloc(sizeof(int)*(D+1)); DEG=1;
    for (int i=0;i<D;i++){ pw[i]=NV; NV*=N; DEG*=3; } DEG-=1;

    /* --- the generators are checked, not trusted --- */
    int gen_ok = 1, gen_nontrivial = 1, gen_bijective = 1;
    int *img = malloc(sizeof(int)*NV), *seen = malloc(sizeof(int)*NV);
    int *nb = malloc(sizeof(int)*(DEG+2));
    for (int g = 0; g < n_gen; g++) {
        int moves = 0;
        memset(seen,0,sizeof(int)*NV);
        for (int v=0; v<NV; v++) { img[v]=apply_gen(g,v); if (img[v]!=v) moves++; seen[img[v]]++; }
        for (int v=0; v<NV; v++) if (seen[v]!=1) gen_bijective = 0;
        if (!moves) gen_nontrivial = 0;                    /* identity is a bug, not a symmetry */
        for (int v=0; v<NV && gen_ok; v++) {
            int k = neighbours(v, nb);
            for (int i=0;i<k;i++) if (!adjacent(img[v], img[nb[i]])) { gen_ok = 0; break; }
        }
    }
    if (n_gen && (!gen_ok || !gen_nontrivial || !gen_bijective)) {
        if (as_json) printf("{\"generators_are_automorphisms\":%s,\"generators_nontrivial\":%s,"
                            "\"generators_bijective\":%s,\"rejected\":true}\n",
                            gen_ok?"true":"false", gen_nontrivial?"true":"false", gen_bijective?"true":"false");
        else fprintf(stderr, "generator rejected: automorphism=%d nontrivial=%d bijective=%d\n",
                     gen_ok, gen_nontrivial, gen_bijective);
        return 3;
    }

    /* --- orbits --- */
    uf = malloc(sizeof(int)*NV);
    for (int v=0; v<NV; v++) uf[v]=v;
    for (int g=0; g<n_gen; g++) for (int v=0; v<NV; v++) uni(v, apply_gen(g,v));
    int *orb = malloc(sizeof(int)*NV), *rep = malloc(sizeof(int)*NV);
    on = 0;
    for (int v=0; v<NV; v++) rep[v]=-1;
    for (int v=0; v<NV; v++) { int r=find(v); if (rep[r]<0) rep[r]=on++; orb[v]=rep[r]; }
    ow = calloc(on,sizeof(int));
    for (int v=0; v<NV; v++) ow[orb[v]]++;

    /* --- orbit graph --- */
    uint8_t *bad = calloc(on,1);
    odeg = calloc(on,sizeof(int));
    int64_t *pairs = NULL; long np_=0, cap=1<<20; pairs = malloc(cap*8);
    for (int v=0; v<NV; v++) {
        int k = neighbours(v, nb);
        for (int i=0;i<k;i++) {
            int a=orb[v], b=orb[nb[i]];
            if (a==b) { bad[a]=1; continue; }
            if (a>b) { int t=a; a=b; b=t; }
            if (np_==cap){ cap*=2; pairs=realloc(pairs,cap*8); }
            pairs[np_++] = ((int64_t)a<<32) | (uint32_t)b;
        }
    }
    /* unique pairs */
    int cmp(const void*x,const void*y){ int64_t a=*(const int64_t*)x,b=*(const int64_t*)y; return a<b?-1:a>b; }
    qsort(pairs,np_,8,cmp);
    long nu=0;
    for (long i=0;i<np_;i++) if (!i||pairs[i]!=pairs[i-1]) pairs[nu++]=pairs[i];
    for (long i=0;i<nu;i++){ int a=pairs[i]>>32, b=(int)pairs[i]; odeg[a]++; odeg[b]++; }
    oadj = malloc(sizeof(int*)*on);
    for (int i=0;i<on;i++){ oadj[i]=malloc(sizeof(int)*(odeg[i]?odeg[i]:1)); odeg[i]=0; }
    for (long i=0;i<nu;i++){ int a=pairs[i]>>32, b=(int)pairs[i];
        oadj[a][odeg[a]++]=b; oadj[b][odeg[b]++]=a; }

    /* orbits that are not internally independent can never be used */
    int usable=0; long usable_w=0;
    for (int i=0;i<on;i++) if(!bad[i]){ usable++; usable_w+=ow[i]; }

    inS=calloc(on,1); tight=calloc(on,sizeof(int));
    Slist=malloc(sizeof(int)*on); Spos=malloc(sizeof(int)*on); Ssize=0; Sw=0;
    for (int i=0;i<on;i++) if (bad[i]) tight[i]=1<<20;      /* never insertable */

    int *best=malloc(sizeof(int)*on); int bestn=0; long bestw=0;
    double t0=now(); long iters=0;
    if (want_orbits) {
        /* fixed-cardinality tabu over the orbits of one common size */
        int sz = 0; for (int i=0;i<on;i++) if(!bad[i] && ow[i]>sz) sz=ow[i];
        int *pool = malloc(sizeof(int)*on), np2 = 0;
        for (int i=0;i<on;i++) if (!bad[i] && ow[i]==sz) pool[np2++]=i;
        int *sel = malloc(sizeof(int)*want_orbits); long kicks=0;
        int residual = orbit_tabu(want_orbits, limit, pool, np2, sel, &kicks);
        double ela = now()-t0;
        if (residual == 0) { bestn = want_orbits; bestw = (long)want_orbits*sz;
                             memcpy(best, sel, sizeof(int)*want_orbits); }
        if (as_json)
            printf("{\"n\":%d,\"d\":%d,\"mode\":\"orbit-tabu\",\"orbits\":%d,"
                   "\"orbit_size\":%d,\"pool\":%d,\"want_orbits\":%d,\"conflicts_left\":%d,"
                   "\"best\":%ld,\"reached\":%s,\"seconds\":%.2f,\"kicks\":%ld}\n",
                   N,D,on,sz,np2,want_orbits,residual,bestw,residual==0?"true":"false",ela,kicks);
        if (residual != 0) return 1;
        goto emit;
    }
    greedy();
    while (now()-t0 < limit) {
        iters++;
        greedy();
        while (improve()) greedy();
        if (Sw > bestw) { bestw=Sw; bestn=Ssize; memcpy(best,Slist,sizeof(int)*Ssize);
                          if (bestw >= target) break; }
        int p=1+rnd()%3;
        for (int i=0;i<p;i++) plateau();
        int v; int guard=0;
        do { v = rnd()%on; } while (bad[v] && ++guard < 100);
        if (!bad[v]) force(v);
    }
    double el=now()-t0;
    (void)el;
emit:
    if (out && bestw) {
        int *vs = malloc(sizeof(int)*NV); int nvs=0;
        uint8_t *chosen = calloc(on,1);
        for (int i=0;i<bestn;i++) chosen[best[i]]=1;
        for (int v=0; v<NV; v++) if (chosen[orb[v]]) vs[nvs++]=v;
        FILE *f=fopen(out,"w");
        fprintf(f,"# Independent set of size %d in C_%d^{boxtimes %d}, invariant under the group\n",nvs,N,D);
        for (int g=0; g<n_gen; g++) {
            fprintf(f,"#   generator %d:  x -> (", g);
            for (int i=0;i<D;i++) fprintf(f,"%s%sx_%d%+d", i?", ":"", gs[g][i]<0?"-":"", gp[g][i], gc[g][i]);
            fprintf(f,")  mod %d\n", N);
        }
        fprintf(f,"# %d orbits chosen out of %d usable; engine E3, scripts/s1_sym, %.1f s.\n", bestn, usable, el);
        fprintf(f,"# Independence is NOT asserted here: see scripts/verify.\n");
        fprintf(f,"%d %d %d\n",N,D,nvs);
        for (int i=0;i<nvs;i++){ int co[MAXD]; decode(vs[i],co);
            for(int j=0;j<D;j++) fprintf(f,"%s%d",j?" ":"",co[j]); fprintf(f,"\n"); }
        fclose(f);
    }
    if (as_json && !want_orbits)
        printf("{\"n\":%d,\"d\":%d,\"vertices\":%d,\"generators\":%d,"
               "\"generators_are_automorphisms\":%s,\"generators_nontrivial\":%s,"
               "\"generators_bijective\":%s,\"orbits\":%d,\"orbits_usable\":%d,"
               "\"vertices_in_usable_orbits\":%ld,\"best\":%ld,\"orbits_chosen\":%d,"
               "\"target\":%d,\"reached\":%s,\"seconds\":%.2f,\"restarts\":%ld,\"out\":%s%s%s}\n",
               N,D,NV,n_gen, gen_ok?"true":"false", gen_nontrivial?"true":"false",
               gen_bijective?"true":"false", on, usable, usable_w, bestw, bestn,
               target==(1<<30)?-1:target, bestw>=target?"true":"false", el, iters,
               out?"\"":"", out?out:"null", out?"\"":"");
    else if (!want_orbits)
        printf("C_%d^%d, %d orbits (%d usable): best %ld vertices in %.1f s\n", N,D,on,usable,bestw,el);
    return bestw >= target ? 0 : 1;
}

/*
 * Engine E4 of the Stage 1 search stack: large-neighbourhood search with exact
 * repair, for independent sets in C_n^{boxtimes d}.
 *
 * Local search (E2) stalls at 102 on C_7^{boxtimes 4}; prescribed symmetry (E3)
 * caps out at 105 because its orbits are size 7 and 16 orbits would be 112; the
 * fixed-cardinality tabu search reaches 106 and then sits at two conflicts.  All
 * three move in steps of one or two vertices.  This engine moves in blocks:
 *
 *   - pick a box window in the torus,
 *   - delete every chosen vertex inside it,
 *   - compute the free region F (cells of the window that nothing outside the
 *     window forbids),
 *   - solve maximum independent set on F *exactly*, by branch and bound with a
 *     greedy clique-cover bound,
 *   - keep the repair if it is at least as large as what was deleted.
 *
 * The repair being exact is the point: within a window the engine cannot do
 * better, so every failure to improve is informative rather than a tuning
 * artefact.
 *
 * Build: cc -O2 -o s1_lns s1_lns.c
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#define MAXD 8
#define FW 12                     /* 12*64 = 768 vertices in a window, at most */
#define FMAX 768

static int N, D, NV, *pw;
static uint8_t *inS;
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+1e-9*t.tv_nsec;}
static uint64_t rs = 88172645463325252ULL;
static uint32_t rnd(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)(rs>>32);}

static void decode(int v,int*c){for(int i=0;i<D;i++){c[i]=v%N;v/=N;}}
static int adjacent(int a,int b){
    if(a==b) return 0;
    int ca[MAXD],cb[MAXD];decode(a,ca);decode(b,cb);
    for(int i=0;i<D;i++){int t=ca[i]-cb[i];if(t<0)t=-t;if(t>N-t)t=N-t;if(t>1)return 0;}
    return 1;
}
static int neighbours(int v,int*out){
    int co[MAXD];decode(v,co);int n=0,tot=1;
    for(int i=0;i<D;i++) tot*=3;
    for(int m=0;m<tot;m++){int mm=m,u=0,z=1;
        for(int i=0;i<D;i++){int dd=mm%3-1;mm/=3;if(dd)z=0;int c=co[i]+dd;if(c<0)c+=N;if(c>=N)c-=N;u+=c*pw[i];}
        if(!z) out[n++]=u;}
    return n;
}

/* ---------- exact maximum independent set on a small induced subgraph ---------- */
static int fn;                    /* number of vertices in the window graph */
static uint64_t fadj[FMAX][FW];
static int fbest, fcur[FMAX], fbestset[FMAX], fcurn;
static long fnodes, fnodecap;

static int fpc(const uint64_t*a){int c=0;for(int i=0;i<FW;i++)c+=__builtin_popcountll(a[i]);return c;}

static int clique_cover(const uint64_t *cand) {
    uint64_t rem[FW]; memcpy(rem,cand,sizeof rem);
    int cl = 0;
    for (;;) {
        int v = -1;
        for (int i=0;i<FW&&v<0;i++) if (rem[i]) v = i*64+__builtin_ctzll(rem[i]);
        if (v < 0) break;
        cl++;
        uint64_t com[FW];
        for (int i=0;i<FW;i++) com[i] = rem[i] & fadj[v][i];
        rem[v>>6] &= ~(1ULL<<(v&63));
        for (;;) {
            int u = -1;
            for (int i=0;i<FW&&u<0;i++) if (com[i]) u = i*64+__builtin_ctzll(com[i]);
            if (u < 0) break;
            rem[u>>6] &= ~(1ULL<<(u&63));
            for (int i=0;i<FW;i++) com[i] &= fadj[u][i];
        }
    }
    return cl;
}
static void fexpand(uint64_t *cand) {
    if (++fnodes > fnodecap) return;
    int nc = fpc(cand);
    if (nc == 0) { if (fcurn > fbest) { fbest = fcurn; memcpy(fbestset,fcur,sizeof(int)*fcurn); } return; }
    if (fcurn + clique_cover(cand) <= fbest) return;
    int piv = -1, pd = -1;
    for (int i=0;i<FW;i++){ uint64_t m=cand[i];
        while(m){int v=i*64+__builtin_ctzll(m);m&=m-1;
            int dg=0; for(int j=0;j<FW;j++) dg+=__builtin_popcountll(cand[j]&fadj[v][j]);
            if(dg>pd){pd=dg;piv=v;} } }
    uint64_t sub[FW];
    for (int i=0;i<FW;i++) sub[i] = cand[i] & ~fadj[piv][i];
    sub[piv>>6] &= ~(1ULL<<(piv&63));
    fcur[fcurn++] = piv; fexpand(sub); fcurn--;
    memcpy(sub,cand,sizeof sub); sub[piv>>6] &= ~(1ULL<<(piv&63));
    fexpand(sub);
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr,"usage: s1_lns n d --start F [--seconds S] [--seed X] [--target T] [--out F] [--json]\n"); return 2; }
    N = atoi(argv[1]); D = atoi(argv[2]);
    double limit = 60.0; int target = 1<<30, as_json = 0;
    const char *out = NULL, *start = NULL;
    fnodecap = 4000000;
    int WLO = getenv("WLO") ? atoi(getenv("WLO")) : 2;
    int WHI = getenv("WHI") ? atoi(getenv("WHI")) : 4;
    if (getenv("NODECAP")) fnodecap = atoll(getenv("NODECAP"));
    int SLAB = getenv("SLAB") ? atoi(getenv("SLAB")) : 0;   /* % of windows that are slabs */
    int SHAKE = getenv("SHAKE") ? atoi(getenv("SHAKE")) : 0; /* 1-in-SHAKE rounds, drop a vertex */
    for (int i=3;i<argc;i++){
        if(!strcmp(argv[i],"--seconds")&&i+1<argc) limit=atof(argv[++i]);
        else if(!strcmp(argv[i],"--seed")&&i+1<argc) rs=(uint64_t)atoll(argv[++i])*2862933555777941757ULL+3037000493ULL;
        else if(!strcmp(argv[i],"--target")&&i+1<argc) target=atoi(argv[++i]);
        else if(!strcmp(argv[i],"--out")&&i+1<argc) out=argv[++i];
        else if(!strcmp(argv[i],"--start")&&i+1<argc) start=argv[++i];
        else if(!strcmp(argv[i],"--json")) as_json=1;
    }
    NV=1; pw=malloc(sizeof(int)*(D+1));
    for(int i=0;i<D;i++){pw[i]=NV;NV*=N;}
    inS = calloc(NV,1);
    int *nb = malloc(sizeof(int)*1024);

    int size = 0;
    if (start) {
        FILE *f=fopen(start,"r"); if(!f){fprintf(stderr,"cannot open %s\n",start);return 2;}
        char line[4096]; int have=0,n2,d2; long sz;
        while(fgets(line,sizeof line,f)){
            char*p=line; while(*p==' '||*p=='\t')p++;
            if(*p=='#'||*p=='\n'||*p=='\r'||!*p) continue;
            if(!have){sscanf(p,"%d %d %ld",&n2,&d2,&sz);have=1;
                      if(n2!=N||d2!=D){fprintf(stderr,"start set has the wrong shape\n");return 2;}continue;}
            int v=0; for(int i=0;i<D;i++){while(*p==' ')p++; v+=(int)strtol(p,&p,10)*pw[i];}
            if(!inS[v]){inS[v]=1;size++;}
        }
        fclose(f);
    } else {
        for (int v=0; v<NV; v++) { int ok=1; int k=neighbours(v,nb);
            for(int i=0;i<k;i++) if(inS[nb[i]]) {ok=0;break;}
            if(ok){inS[v]=1;size++;} }
    }
    int best_size = size;
    uint8_t *bestS = malloc(NV); memcpy(bestS,inS,NV);

    double t0=now(); long rounds=0, improved=0, exact_windows=0, skipped=0;
    int co[MAXD], lo[MAXD], w[MAXD];
    int *win = malloc(sizeof(int)*4096);
    while (now()-t0 < limit && best_size < target) {
        rounds++;
        int c = rnd()%NV; decode(c,co);
        int cells = 1, nw = 0;
        int use_slab = (SLAB && (int)(rnd()%100) < SLAB);
        if (use_slab) {
            /* a slab window: one coordinate pinned to one or two consecutive values.
               This re-optimises a whole layer of the torus at once, which no box
               window can do, and is the move that the layer decomposition of E1
               suggests. */
            int ax = rnd()%D, a0 = rnd()%N, thick = 1 + (rnd()%2);
            for (int v=0; v<NV && nw<4096; v++) {
                int cv[MAXD]; decode(v,cv);
                int off = (cv[ax]-a0+N)%N;
                if (off < thick) win[nw++]=v;
            }
        } else {
            for (int i=0;i<D;i++){ w[i] = WLO + rnd()%(WHI-WLO+1); lo[i]=co[i]; cells *= w[i]; }
            if (cells > 4096) { skipped++; continue; }
            for (int m=0;m<cells;m++){
                int mm=m,v=0;
                for(int i=0;i<D;i++){ int off=mm%w[i]; mm/=w[i]; v += ((lo[i]+off)%N)*pw[i]; }
                win[nw++]=v;
            }
        }
        /* delete the chosen vertices inside the window */
        int removed = 0;
        for (int i=0;i<nw;i++) if (inS[win[i]]) { inS[win[i]]=0; removed++; }
        if (removed == 0) { continue; }
        /* free region: window cells blocked by nothing outside */
        fn = 0;
        int freev[FMAX];
        for (int i=0;i<nw && fn<FMAX;i++){
            int v=win[i]; if(inS[v]) continue;
            int k=neighbours(v,nb), ok=1;
            for(int j=0;j<k;j++) if(inS[nb[j]]) {ok=0;break;}
            if(ok) freev[fn++]=v;
        }

        memset(fadj,0,sizeof(uint64_t)*(size_t)fn*FW);
        for(int i=0;i<fn;i++) for(int j=i+1;j<fn;j++)
            if(adjacent(freev[i],freev[j])){ fadj[i][j>>6]|=1ULL<<(j&63); fadj[j][i>>6]|=1ULL<<(i&63); }
        uint64_t cand[FW]; memset(cand,0,sizeof cand);
        for(int i=0;i<fn;i++) cand[i>>6]|=1ULL<<(i&63);
        fbest=0; fcurn=0; fnodes=0;
        fexpand(cand);
        int exact = (fnodes <= fnodecap);
        if (exact) exact_windows++;
        if (fbest >= removed) {
            for(int i=0;i<fbest;i++) inS[freev[fbestset[i]]]=1;
            size += fbest - removed;
            if (size > best_size) { best_size = size; memcpy(bestS,inS,NV); improved++; }
        } else {
            /* undo: restore the best solution rather than a damaged one */
            memcpy(inS,bestS,NV); size = best_size;
        }
        if (SHAKE && (int)(rnd()%SHAKE)==0 && size > 0) {
            int v; do { v = rnd()%NV; } while (!inS[v]);
            inS[v]=0; size--;
        }
    }
    double el = now()-t0;

    if (out) {
        FILE *f=fopen(out,"w");
        fprintf(f,"# Independent set of size %d in C_%d^{boxtimes %d}.\n",best_size,N,D);
        fprintf(f,"# Found by scripts/s1_lns (engine E4, large-neighbourhood search with exact\n");
        fprintf(f,"# repair), %.1f s, %ld windows, %ld improvements.\n",el,rounds,improved);
        fprintf(f,"# Independence is NOT asserted here: see scripts/verify.\n");
        fprintf(f,"%d %d %d\n",N,D,best_size);
        for(int v=0;v<NV;v++) if(bestS[v]){ int cc[MAXD]; decode(v,cc);
            for(int j=0;j<D;j++) fprintf(f,"%s%d",j?" ":"",cc[j]); fprintf(f,"\n"); }
        fclose(f);
    }
    if (as_json)
        printf("{\"n\":%d,\"d\":%d,\"start_size\":%d,\"best\":%d,\"target\":%d,\"reached\":%s,"
               "\"seconds\":%.2f,\"windows\":%ld,\"exact_windows\":%ld,\"improvements\":%ld,\"out\":%s%s%s}\n",
               N,D,size,best_size,target==(1<<30)?-1:target,best_size>=target?"true":"false",
               el,rounds,exact_windows,improved,out?"\"":"",out?out:"null",out?"\"":"");
    else
        printf("C_%d^%d LNS: best %d in %.1f s (%ld windows, %ld exact, %ld improvements)\n",
               N,D,best_size,el,rounds,exact_windows,improved);
    return best_size >= target ? 0 : 1;
}

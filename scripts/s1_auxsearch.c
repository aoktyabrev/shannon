/*
 * S1.2, branch B, final step: search for an auxiliary set with o >= 324.
 *
 * The group sweep plus exact repair reaches o = 322, which is the
 * Buys-Polak-Zuiddam profile, rediscovered here independently.  Getting past it
 * means leaving the orbit of the known codes, so the problem is posed directly:
 *
 *     find an independent set X of C_7^{boxtimes 5} with |X| = 367,
 *     avoiding the forbidden region B = N(P_H) cap N(P_V),
 *     minimising u = |X cap U|, U = N(P_H) cup N(P_V),
 *
 * since the profile is (367, 8, 367, 367-u) and the bound grows as u falls.
 * Dropping |X| below 367 is never worth it: one word costs about 1.0e-3 of the
 * bound, while the whole of u = 46 -> 0 would be worth 3.1e-3.
 *
 * This is the fixed-cardinality tabu search of engine E2, with the single
 * objective  cost = W * (adjacent pairs) + u,  W large, so that independence is
 * settled first and u is minimised among independent sets.  It is warm-started
 * from a known 367-word set, because finding one from scratch is the open
 * problem this whole project sits inside.
 *
 * Build: cc -O2 -o s1_auxsearch s1_auxsearch.c
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
#define WCONF 100000L

static int pw[D] = {1,7,49,343,2401};
static uint8_t forb[NV], pen[NV], inS[NV];
static int conf[NV], Sarr[512], K;
static long cost_now, u_now;
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+1e-9*t.tv_nsec;}
static uint64_t rs=88172645463325252ULL;
static uint32_t rnd(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)(rs>>32);}
static void dec(int v,int*c){for(int i=0;i<D;i++){c[i]=v%N;v/=N;}}
static int enc(const int*c){int v=0;for(int i=0;i<D;i++)v+=c[i]*pw[i];return v;}
static int nbs(int v,int*out){int c[D];dec(v,c);int n=0;
    for(int m=0;m<243;m++){int mm=m,u=0,z=1;
        for(int i=0;i<D;i++){int dd=mm%3-1;mm/=3;if(dd)z=0;int x=c[i]+dd;if(x<0)x+=N;if(x>=N)x-=N;u+=x*pw[i];}
        if(!z) out[n++]=u;}
    return n;}
static int adjacent(int a,int b){if(a==b)return 0;int ca[D],cb[D];dec(a,ca);dec(b,cb);
    for(int i=0;i<D;i++){int t=ca[i]-cb[i];if(t<0)t=-t;if(t>N-t)t=N-t;if(t>1)return 0;}return 1;}
static int nbuf[256];
static void S_add(int v){inS[v]=1;cost_now+=WCONF*conf[v];u_now+=pen[v];
    int k=nbs(v,nbuf);for(int i=0;i<k;i++)conf[nbuf[i]]++;}
static void S_del(int v){inS[v]=0;cost_now-=WCONF*conf[v];u_now-=pen[v];
    int k=nbs(v,nbuf);for(int i=0;i<k;i++)conf[nbuf[i]]--;}

static int read_list(const char*p,uint8_t*mark){FILE*f=fopen(p,"r");if(!f)return -1;
    int v,n=0;while(fscanf(f,"%d",&v)==1){mark[v]=1;n++;}fclose(f);return n;}
static int read_set_file(const char*p,int*out){FILE*f=fopen(p,"r");if(!f)return -1;
    char line[4096];int have=0,n2,d2;long sz;int n=0;
    while(fgets(line,sizeof line,f)){char*q=line;while(*q==' '||*q=='\t')q++;
        if(*q=='#'||*q=='\n'||*q=='\r'||!*q)continue;
        if(!have){sscanf(q,"%d %d %ld",&n2,&d2,&sz);have=1;continue;}
        int c[D];for(int i=0;i<D;i++){while(*q==' ')q++;c[i]=(int)strtol(q,&q,10);}
        out[n++]=enc(c);}
    fclose(f);return n;}

int main(int argc,char**argv){
    const char *fb=NULL,*pn=NULL,*st=NULL,*out=NULL; double limit=60; int as_json=0;
    K=367;
    for(int i=1;i<argc;i++){
        if(!strcmp(argv[i],"--forbid")&&i+1<argc) fb=argv[++i];
        else if(!strcmp(argv[i],"--penal")&&i+1<argc) pn=argv[++i];
        else if(!strcmp(argv[i],"--start")&&i+1<argc) st=argv[++i];
        else if(!strcmp(argv[i],"--out")&&i+1<argc) out=argv[++i];
        else if(!strcmp(argv[i],"--k")&&i+1<argc) K=atoi(argv[++i]);
        else if(!strcmp(argv[i],"--seconds")&&i+1<argc) limit=atof(argv[++i]);
        else if(!strcmp(argv[i],"--seed")&&i+1<argc) rs=(uint64_t)atoll(argv[++i])*2862933555777941757ULL+3037000493ULL;
        else if(!strcmp(argv[i],"--json")) as_json=1;
    }
    int nB = fb ? read_list(fb,forb) : 0;
    int nU = pn ? read_list(pn,pen) : 0;
    int n0 = 0;
    if (st) { n0 = read_set_file(st,Sarr); if(n0<0){fprintf(stderr,"cannot read start\n");return 2;} }
    int n = 0;
    for (int i=0;i<n0 && n<K;i++) if(!inS[Sarr[i]] && !forb[Sarr[i]]) { int v=Sarr[i]; Sarr[n]=v; S_add(v); n++; }
    while (n<K) { int v=rnd()%NV; if(!inS[v]&&!forb[v]){ Sarr[n++]=v; S_add(v); } }

    long *tabu = calloc(NV,sizeof(long));
    double t0=now(); long iter=0, since=0;
    long best = cost_now; long best_u = u_now; int bestS[512]; memcpy(bestS,Sarr,sizeof(int)*K);
    int best_conf = (int)(cost_now/WCONF);
    while (now()-t0 < limit) {
        iter++; since++;
        int pi=-1;
        if (cost_now >= WCONF) {                  /* fix independence first */
            for(int t=0;t<300&&pi<0;t++){int j=rnd()%K;if(conf[Sarr[j]]>0)pi=j;}
            if(pi<0) for(int j=0;j<K;j++) if(conf[Sarr[j]]>0){pi=j;break;}
        } else {                                   /* then chip away at u */
            for(int t=0;t<300&&pi<0;t++){int j=rnd()%K;if(pen[Sarr[j]])pi=j;}
            if(pi<0) pi=rnd()%K;
        }
        if(pi<0) break;
        int v=Sarr[pi];
        long bd=1L<<50; int bu=-1,ties=0;
        for(int u2=0;u2<NV;u2++){
            if(inS[u2]||forb[u2]) continue;
            long delta = WCONF*((long)conf[u2]-(adjacent(u2,v)?1:0)-(long)conf[v]) + (long)pen[u2]-(long)pen[v];
            if(tabu[u2]>iter && cost_now+delta >= best) continue;
            if(delta<bd){bd=delta;bu=u2;ties=1;}
            else if(delta==bd && (rnd()%++ties)==0) bu=u2;
        }
        if(bu<0){ tabu[v]=0; continue; }
        S_del(v); S_add(bu); Sarr[pi]=bu;
        tabu[v]=iter+6+rnd()%14;
        if(cost_now<best){ best=cost_now; best_u=u_now; best_conf=(int)(cost_now/WCONF);
                           memcpy(bestS,Sarr,sizeof(int)*K); since=0; }
        if(since>80000){ since=0;
            for(int i=0;i<K/8;i++){int j=rnd()%K,w;int g=0;
                do{w=rnd()%NV;}while((inS[w]||forb[w])&&++g<300);
                if(inS[w]||forb[w])continue; S_del(Sarr[j]); S_add(w); Sarr[j]=w;} }
    }
    double el=now()-t0;
    int o = K - (int)best_u;
    if (out && best_conf==0) {
        FILE*f=fopen(out,"w");
        fprintf(f,"# Auxiliary set X: %d words, u = %ld, o = %d.\n",K,best_u,o);
        fprintf(f,"# Found by scripts/s1_auxsearch in %.1f s.  Independence is NOT asserted\n",el);
        fprintf(f,"# here: see scripts/verify.\n");
        fprintf(f,"%d %d %d\n",N,D,K);
        for(int i=1;i<K;i++){int x=bestS[i],j=i-1;while(j>=0&&bestS[j]>x){bestS[j+1]=bestS[j];j--;}bestS[j+1]=x;}
        for(int i=0;i<K;i++){int c[D];dec(bestS[i],c);
            for(int j=0;j<D;j++)fprintf(f,"%s%d",j?" ":"",c[j]); fprintf(f,"\n");}
        fclose(f);
    }
    if(as_json)
        printf("{\"k\":%d,\"forbidden\":%d,\"penalised\":%d,\"conflicts\":%d,\"u\":%ld,\"o\":%d,"
               "\"seconds\":%.1f,\"iterations\":%ld,\"out\":%s%s%s}\n",
               K,nB,nU,best_conf,best_u,o,el,iter,out&&best_conf==0?"\"":"",
               out&&best_conf==0?out:"null",out&&best_conf==0?"\"":"");
    else printf("k=%d conflicts=%d u=%ld o=%d in %.1f s (%ld iterations)\n",K,best_conf,best_u,o,el,iter);
    return best_conf==0?0:1;
}

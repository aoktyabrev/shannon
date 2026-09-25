/*
 * S1.2, branch B of the preregistration: the auxiliary set of the gadget.
 *
 * With the code fixed to the printed Polak-Schrijver 367-word set, whose eight
 * private pairs Stage 1 proved to be all that exist, the only remaining lever on
 * the bound is the auxiliary set X.  The gadget asks for X independent with
 * X cap N(P_H) cap N(P_V) = empty, and the bound grows with
 *
 *     s = |X|   and   o = |X \ (N(P_H) cup N(P_V))|.
 *
 * Dropping s below 367 is never worth it -- one word costs about 1.0e-3 of the
 * bound while a whole extra private pair is worth 1.7e-4 -- so X must itself be a
 * 367-word independent set.  The ones we have are the eight codes the
 * Polak-Schrijver pipeline produces, and their images under
 *
 *     Aut(C_7^{boxtimes 5})  >=  (D_7)^5 sd S_5,   14^5 * 120 = 64538880 elements.
 *
 * Sweeping that group is not a heuristic search: for a fixed coordinate
 * permutation and sign pattern, the 16807 translations can all be scored at once,
 * because
 *
 *     |(I' + c) cap B|  =  sum over b in B of [ b - c in I' ]
 *
 * is a cyclic cross-correlation over Z_7^5.  So the whole group is covered in one
 * pass per (source set, permutation, signs, 2-colouring).  Every valid
 * 2-colouring of the private pairs is tried too: which endpoint goes to which
 * transversal changes N(P_H) and N(P_V), and nobody has reported sweeping it.
 *
 * Build: cc -O2 -fopenmp -o s1_aux s1_aux.c
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

static int pw[D] = {1, 7, 49, 343, 2401};
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+1e-9*t.tv_nsec;}

static void dec(int v,int*c){for(int i=0;i<D;i++){c[i]=v%N;v/=N;}}
static int enc(const int*c){int v=0;for(int i=0;i<D;i++)v+=c[i]*pw[i];return v;}
static int adj_or_eq(int a,int b){
    int ca[D],cb[D];dec(a,ca);dec(b,cb);
    for(int i=0;i<D;i++){int t=ca[i]-cb[i];if(t<0)t=-t;if(t>N-t)t=N-t;if(t>1)return 0;}
    return 1;
}
static void closed_nbhd(int v, uint8_t *mark) {
    int c[D];dec(v,c);
    for(int m=0;m<243;m++){int mm=m,u=0;
        for(int i=0;i<D;i++){int dd=mm%3-1;mm/=3;int x=c[i]+dd;if(x<0)x+=N;if(x>=N)x-=N;u+=x*pw[i];}
        mark[u]=1;}
}

static int read_code(const char *path, int *out) {
    FILE *f=fopen(path,"r"); if(!f) return -1;
    char line[4096]; int have=0,n2,d2; long sz; int n=0;
    while(fgets(line,sizeof line,f)){
        char*p=line;while(*p==' '||*p=='\t')p++;
        if(*p=='#'||*p=='\n'||*p=='\r'||!*p)continue;
        if(!have){sscanf(p,"%d %d %ld",&n2,&d2,&sz);have=1;continue;}
        int c[D];for(int i=0;i<D;i++){while(*p==' ')p++;c[i]=(int)strtol(p,&p,10);}
        out[n++]=enc(c);
    }
    fclose(f); return n;
}

int main(int argc, char **argv) {
    const char *code_file = argc>1 ? argv[1] : "sets/C7_d5_367_polak_schrijver.txt";
    int as_json = 0; int n_src = 0; const char *src[16]; const char *dump = NULL; int dump_max = 4;
    for (int i=2;i<argc;i++){
        if(!strcmp(argv[i],"--json")) as_json=1;
        else if(!strcmp(argv[i],"--source")&&i+1<argc&&n_src<16) src[n_src++]=argv[++i];
        else if(!strcmp(argv[i],"--dump")&&i+1<argc) dump=argv[++i];
        else if(!strcmp(argv[i],"--dump-max")&&i+1<argc) dump_max=atoi(argv[++i]);
    }
    if (!n_src) src[n_src++] = code_file;

    static int I[512]; int nI = read_code(code_file, I);
    if (nI < 0) { fprintf(stderr,"cannot read %s\n", code_file); return 2; }
    static uint8_t inI[NV]; memset(inI,0,NV);
    for (int i=0;i<nI;i++) inI[I[i]]=1;

    /* private pairs: q outside I with exactly one I-neighbour */
    int rr[64], qq[64], npair=0;
    for (int q=0;q<NV;q++){
        if(inI[q]) continue;
        int cnt=0, hit=-1;
        for(int i=0;i<nI;i++) if(adj_or_eq(q,I[i])){ if(++cnt>1) break; hit=I[i]; }
        if(cnt==1 && npair<64){ rr[npair]=hit; qq[npair]=q; npair++; }
    }
    /* conflict graph on the q's */
    uint64_t cmask[64]; memset(cmask,0,sizeof cmask);
    for(int i=0;i<npair;i++) for(int j=i+1;j<npair;j++)
        if(adj_or_eq(qq[i],qq[j])){ cmask[i]|=1ULL<<j; cmask[j]|=1ULL<<i; }

    /* proper 2-colourings, up to the global swap */
    int ncol=0; static uint32_t cols[512];
    for (uint32_t m=0; m<(1u<<npair); m++) {
        if (m & 1) continue;                       /* fix pair 0 to H: kills the global swap */
        int ok=1;
        for(int i=0;i<npair&&ok;i++) for(int j=i+1;j<npair;j++)
            if((cmask[i]>>j&1) && (((m>>i)&1)==((m>>j)&1))) { ok=0; break; }
        if(ok && ncol<512) cols[ncol++]=m;
    }

    /* the automorphism group's permutation and sign parts */
    int perms[120][D], nperm=0;
    int idxs[D]={0,1,2,3,4};
    /* Heap's algorithm, written out */
    int cc[D]={0,0,0,0,0};
    memcpy(perms[nperm++], idxs, sizeof idxs);
    for (int i=0;i<D;) {
        if (cc[i] < i) {
            int a = (i%2==0)?0:cc[i];
            int t=idxs[a]; idxs[a]=idxs[i]; idxs[i]=t;
            memcpy(perms[nperm++], idxs, sizeof idxs);
            cc[i]++; i=0;
        } else { cc[i]=0; i++; }
    }

    FILE *dp = NULL;
    if (dump) { dp = fopen(dump,"w");
        fprintf(dp,"# source colouring_mask perm0,perm1,perm2,perm3,perm4 sign_mask shift bad u\n"); }
    double t0 = now();
    int best_o = -1, best_col = -1, best_perm = -1, best_sgn = -1, best_shift = -1, best_src = -1;
    long total_group_elements = 0;
    int near[8]; memset(near,0,sizeof near);

    for (int ci = 0; ci < ncol; ci++) {
        static uint8_t NH[NV], NVv[NV];
        memset(NH,0,NV); memset(NVv,0,NV);
        for (int j=0;j<npair;j++) {
            int to_v = (cols[ci]>>j)&1;            /* 1 = q_j goes to P_V */
            closed_nbhd(to_v ? qq[j] : rr[j], NH);
            closed_nbhd(to_v ? rr[j] : qq[j], NVv);
        }
        int Bl[8192], nB=0, Ul[8192], nU=0;
        for (int v=0;v<NV;v++){ if(NH[v]&&NVv[v]) Bl[nB++]=v; if(NH[v]||NVv[v]) Ul[nU++]=v; }

        for (int si = 0; si < n_src; si++) {
            static int X0[16][512]; static int nX[16];
            if (ci == 0) { nX[si] = read_code(src[si], X0[si]); }
            if (nX[si] <= 0) continue;
            #pragma omp parallel for schedule(dynamic)
            for (int pi = 0; pi < nperm; pi++) {
                int bcnt[NV], ucnt[NV];
                int img[512];
                for (int sg = 0; sg < (1<<D); sg++) {
                    for (int k=0;k<nX[si];k++) {
                        int c[D], o[D]; dec(X0[si][k], c);
                        for (int i=0;i<D;i++) { int t = ((sg>>i)&1) ? (N - c[perms[pi][i]]) % N : c[perms[pi][i]]; o[i]=t; }
                        img[k]=enc(o);
                    }
                    memset(bcnt,0,sizeof bcnt); memset(ucnt,0,sizeof ucnt);
                    for (int k=0;k<nX[si];k++) {
                        int xc[D]; dec(img[k], xc);
                        for (int b=0;b<nB;b++) { int bc[D]; dec(Bl[b],bc);
                            int t=0; for(int i=0;i<D;i++){int z=bc[i]-xc[i]; if(z<0)z+=N; t+=z*pw[i];} bcnt[t]++; }
                        for (int u=0;u<nU;u++) { int uc[D]; dec(Ul[u],uc);
                            int t=0; for(int i=0;i<D;i++){int z=uc[i]-xc[i]; if(z<0)z+=N; t+=z*pw[i];} ucnt[t]++; }
                    }
                    for (int c2=0;c2<NV;c2++) {
                        if (bcnt[c2] < 8) near[bcnt[c2]]++;
                        if (dp && bcnt[c2] <= dump_max) {
                            #pragma omp critical
                            fprintf(dp,"%d %u %d,%d,%d,%d,%d %d %d %d %d\n", si, cols[ci],
                                    perms[pi][0],perms[pi][1],perms[pi][2],perms[pi][3],perms[pi][4],
                                    sg, c2, bcnt[c2], ucnt[c2]);
                        }
                        if (bcnt[c2]) continue;
                        int o = nX[si] - ucnt[c2];
                        #pragma omp critical
                        if (o > best_o) { best_o=o; best_col=ci; best_perm=pi; best_sgn=sg; best_shift=c2; best_src=si; }
                    }
                }
            }
            total_group_elements += (long)nperm * (1<<D) * NV;
        }
    }
    double el = now()-t0;
    if (dp) fclose(dp);

    if (as_json) {
        printf("{\"code\":\"%s\",\"code_size\":%d,\"candidate_private_pairs\":%d,"
               "\"proper_2_colourings_up_to_swap\":%d,\"sources\":%d,"
               "\"group_elements_swept\":%ld,\"best_o\":%d,\"best_s\":367,"
               "\"best_colouring\":%d,\"best_perm_index\":%d,\"best_sign_mask\":%d,"
               "\"best_shift_index\":%d,\"best_source\":%d,\"seconds\":%.1f,"
               "\"translations_with_bad_eq\":[",
               code_file, nI, npair, ncol, n_src, total_group_elements, best_o,
               best_col, best_perm, best_sgn, best_shift, best_src, el);
        for (int i=0;i<8;i++) printf("%s%d", i?",":"", near[i]);
        printf("]}\n");
    } else {
        printf("code %s: %d words, %d private pairs, %d proper 2-colourings\n", code_file, nI, npair, ncol);
        printf("swept %ld group elements over %d source sets in %.1f s\n", total_group_elements, n_src, el);
        printf("best admissible auxiliary set: s = 367, o = %d\n", best_o);
        printf("translations by number of forbidden hits: ");
        for (int i=0;i<8;i++) printf("%d:%d ", i, near[i]);
        printf("\n");
    }
    return 0;
}

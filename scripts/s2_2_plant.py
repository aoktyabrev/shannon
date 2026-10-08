#!/usr/bin/env python3
"""Anti-vacuum for k-opt inside G_F. From the admissible t = 8 set X (367 words outside F)
delete k words w_1..w_k and insert k-1 allowed vertices that together touch every freed
allowed vertex -- a 366-word set that is maximal in G_F (1-opt cannot help) but from
which a window search must recover 367. k = 2 and k = 3."""
import sys, itertools
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from setio import read_set, write_set, confusable
N = 7
_, _, X = read_set(sys.argv[1]); F = set(int(l) for l in open(sys.argv[2])); K = int(sys.argv[4])
enc = lambda c: sum(c[i] * 7 ** i for i in range(5))
Xs = set(X)
nbX = {}
for v in itertools.product(range(N), repeat=5):
    if v in Xs or enc(v) in F: continue
    ws = [x for x in X if confusable(v, x, N)]
    if len(ws) <= K: nbX[v] = frozenset(ws)
assert all(len(s) > 0 for s in nbX.values()), "X not maximal in G_F"
for v, ws in nbX.items():
    if len(ws) != K: continue
    freed = [u for u, s in nbX.items() if s <= ws]
    others = [u for u in freed if u != v and not confusable(u, v, N)]
    # choose k-2 further inserts among the freed so that everything freed is touched
    for extra in itertools.combinations(others, K - 2):
        Y = (v,) + extra
        if any(confusable(a, b, N) for a, b in itertools.combinations(Y, 2)): continue
        if all(any(confusable(u, y, N) for y in Y) for u in freed + list(ws)):
            Xp = (Xs - ws) | set(Y)
            write_set(sys.argv[3], N, sorted(Xp), [f"planted {len(Xp)}: {K} words replaced by {K-1} that block every freed vertex; a window search must recover 367"])
            print("deleted", sorted(ws), "inserted", Y, "size", len(Xp)); sys.exit(0)
print("no plant"); sys.exit(1)

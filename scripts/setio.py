"""Reading and writing sets of vertices of C_n^{boxtimes d}, and the exact
confusability predicate.  Pure Python, no dependencies: these scripts only build
the sets, every independence claim is made by scripts/verify (C, exact)."""
import hashlib
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERIFY = os.path.join(ROOT, "scripts", "verify")


def read_set(path):
    n = d = size = None
    rows = []
    for line in open(path):
        t = line.strip()
        if not t or t.startswith("#"):
            continue
        if n is None:
            n, d, size = (int(x) for x in t.split())
            continue
        rows.append(tuple(int(x) for x in t.split()))
    assert len(rows) == size, (len(rows), size)
    assert all(len(r) == d for r in rows)
    return n, d, rows


def write_set(path, n, rows, header_lines=()):
    rows = sorted(rows)
    d = len(rows[0])
    assert all(len(r) == d for r in rows)
    assert len(set(rows)) == len(rows), "duplicate vertices"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for h in header_lines:
            f.write("# " + h + "\n")
        f.write(f"{n} {d} {len(rows)}\n")
        for r in rows:
            f.write(" ".join(map(str, r)) + "\n")
    return path


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def confusable(x, y, n):
    """x ~ y: circular distance at most 1 in every coordinate (x == y included)."""
    for a, b in zip(x, y):
        t = (a - b) % n
        if t > 1 and t < n - 1:
            return False
    return True


def verify(path, extra=()):
    """Run the C verifier and return its JSON report.  The path is made relative to the
    repository root and the verifier is run from there, so the report does not depend on
    where the checkout lives."""
    import json
    rel = os.path.relpath(os.path.abspath(path), ROOT)
    out = subprocess.run([VERIFY, rel, "--json", *extra], capture_output=True, text=True, cwd=ROOT)
    if out.returncode not in (0, 1):
        raise RuntimeError(out.stderr or out.stdout)
    return json.loads(out.stdout)

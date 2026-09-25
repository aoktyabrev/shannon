"""Rule 0, enforced mechanically.

Every line of every blockquote in SOURCES.md must occur verbatim in the dumped
LaTeX source of the arXiv identifier named in the section heading.  Whitespace is
normalised (LaTeX line-wrapping is not content), nothing else is.  A quotation
that cannot be found is reported and the script exits non-zero -- a citation that
has drifted from its source is treated as a broken build, not as a footnote.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def source_text(arxiv_id):
    d = os.path.join(ROOT, "sources", arxiv_id, "src")
    blob = []
    for root, _, files in os.walk(d):
        for fn in files:
            if fn.endswith((".tex", ".bib")):
                blob.append(open(os.path.join(root, fn), encoding="utf-8", errors="replace").read())
    return norm(" ".join(blob))


def main():
    text = open(os.path.join(ROOT, "SOURCES.md"), encoding="utf-8").read()
    sections = re.split(r"^#{2,3} ", text, flags=re.M)[1:]
    cache, report = {}, []
    bad = 0
    for sec in sections:
        head = sec.splitlines()[0]
        m = re.search(r"arXiv:(\d{4}\.\d{4,5})", head)
        if not m:
            continue
        aid = m.group(1)
        if aid not in cache:
            cache[aid] = source_text(aid)
        body = cache[aid]
        quotes = [ln[2:] for ln in sec.splitlines() if ln.startswith("> ")]
        for q in quotes:
            qn = norm(q)
            if not qn:
                continue
            ok = qn in body
            if not ok:
                bad += 1
            report.append({"source": aid, "found": ok, "quote": qn[:160]})
    found = sum(1 for r in report if r["found"])
    out = {"quotations": len(report), "found": found, "missing": bad,
           "sources_checked": sorted(cache), "misses": [r for r in report if not r["found"]]}
    os.makedirs(os.path.join(ROOT, "results", "json"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "json", "sources.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"{found}/{len(report)} quotations found verbatim in the dumps "
          f"({', '.join(sorted(cache))})")
    for r in out["misses"]:
        print("  MISSING", r["source"], ":", r["quote"])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

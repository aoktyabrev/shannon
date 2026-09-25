"""Is arXiv:2607.21517 still the record?  (Stage 0 asks the question explicitly.)

Runs three searches against arXiv, newest first, and records every hit.  The API
endpoint export.arxiv.org/api/query answers HTTP 406 from this host, so the HTML
search interface is used and parsed.  The output is a list, not a judgement; the
reading of it is in RESULTS.md and in SOURCES.md.
"""
import html
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUERIES = [
    "Shannon capacity",
    '"C_7" Shannon capacity',
    "odd cycles independent set strong product",
    "independence number strong product cycle",
]


def search(q):
    url = ("https://arxiv.org/search/?searchtype=all&query="
           + q.replace('"', "%22").replace(" ", "+")
           + "&start=0&sortBy=submitted_date&sortOrder=descending")
    out = subprocess.run(["curl", "-sL", "--max-time", "60", url], capture_output=True, text=True)
    t = out.stdout
    hits = []
    for it in re.findall(r'<li class="arxiv-result">(.*?)</li>', t, re.S):
        aid = re.search(r"arxiv\.org/abs/([0-9.]+)", it)
        ti = re.search(r'<p class="title is-5 mathjax">(.*?)</p>', it, re.S)
        dt = re.search(r"Submitted</span>\s*([^;<]*)", it)
        if not aid:
            continue
        hits.append({
            "id": aid.group(1),
            "title": " ".join(html.unescape(re.sub("<[^>]+>", "", ti.group(1))).split()) if ti else "",
            "submitted": dt.group(1).strip() if dt else "",
        })
    return {"query": q, "url": url, "hits": hits}


def main():
    rep = {"date": time.strftime("%Y-%m-%d"), "searches": []}
    for q in QUERIES:
        rep["searches"].append(search(q))
        time.sleep(3)
    seen = {}
    for s in rep["searches"]:
        for h in s["hits"]:
            seen.setdefault(h["id"], h)
    rep["union_sorted_by_id"] = [seen[k] for k in sorted(seen, reverse=True)]
    # the ones this project treats as the record chain
    chain = ["2607.21517", "2607.27869", "2607.29681", "2608.30273"]
    rep["record_chain_present"] = {c: c in seen for c in chain}
    rep["newest_hit_id"] = max(seen) if seen else None
    with open(os.path.join(ROOT, "results", "json", "litcheck.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps({"date": rep["date"], "queries": len(QUERIES),
                      "distinct_hits": len(seen),
                      "record_chain_present": rep["record_chain_present"],
                      "newest_hit_id": rep["newest_hit_id"]}, indent=2))


if __name__ == "__main__":
    sys.exit(main())

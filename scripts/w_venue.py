"""W.4 -- the venue requirements, quoted from dumped pages rather than from memory.

Rule 0 applies to the publisher's rules as much as to the mathematics: every
requirement the note is shaped by has to be a verbatim quotation from a page that
is stored in sources/venue/, with its URL, HTTP status and SHA-256.  This script
re-checks that each quotation is still present in the stored page and writes
results/json/w_venue.json.

One requirement could not be dumped: the Guide for Authors itself is served only
from sciencedirect.com, which answers 403 with a captcha to any non-browser
client from this host (the dump is kept, with its 403, as evidence).  Everything
taken from it is marked unverified and left for a check in a real browser.
"""
import hashlib
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VEN = os.path.join(ROOT, "sources", "venue")

QUOTES = [
    ("ipl_journal_page", "length limit",
     "manuscripts are generally limited in length to nine pages when they appear in print"),
    ("elsevier_generative_ai_policy", "declaration required",
     "Authors should disclose the use of AI tools for manuscript preparation in a separate AI "
     "declaration statement included in their manuscript upon submission."),
    ("elsevier_generative_ai_policy", "section title",
     "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"),
    ("elsevier_generative_ai_policy", "required wording",
     "During the preparation of this work, the author(s) used [NAME OF TOOL / SERVICE] in order to "
     "[REASON]. After using this tool/service, the author(s) reviewed and edited the content as "
     "needed and take(s) full responsibility for the content of the published article."),
    ("elsevier_generative_ai_policy", "AI in the research process, not the writing",
     "Where AI tools are used as part of the research process rather than manuscript preparation, "
     "this use should be described in detail in the Methods section."),
    ("elsevier_generative_ai_policy", "no AI authorship",
     "Authors should not list AI tools as an author or co-author, nor cite AI tools as an author."),
    ("elsevier_pricing_policy", "what an APC is for",
     "Open access articles funded by payments for publishing made by authors, their institution or "
     "funding bodies, commonly known as Article Publishing Charges (APCs)"),
    ("elsevier_pricing_policy", "the APC range",
     "fees range between approximately $200 and $11,400 US Dollars, excluding tax"),
]


def text(name):
    p = os.path.join(VEN, name + ".html")
    if not os.path.exists(p):
        sys.exit(f"{p} is missing: run scripts/fetch_venue.sh (the publisher pages are not "
                 f"committed; their URL, HTTP status and SHA-256 are)")
    t = open(p, encoding="utf-8", errors="replace").read()
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t)


def sha(name):
    h = hashlib.sha256()
    with open(os.path.join(VEN, name + ".html"), "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def main():
    pages = {}
    for fn in sorted(os.listdir(VEN)):
        if not fn.endswith(".url"):
            continue
        name = fn[:-4]
        pages[name] = {
            "url": open(os.path.join(VEN, fn)).read().strip(),
            "http_status": int(open(os.path.join(VEN, name + ".http")).read().strip()),
            "sha256": sha(name),
            "dumped": "2026-09-26",
        }
    rows, bad = [], 0
    for name, what, q in QUOTES:
        found = re.sub(r"\s+", " ", q) in text(name)
        rows.append({"page": name, "what": what, "quote": q, "found_in_dump": found})
        if not found:
            bad += 1
    out = {
        "date": "2026-09-26",
        "target": "Information Processing Letters (Elsevier), ISSN 0020-0190",
        "why": ("Polak-Schrijver, the paper whose code the theorem is about, appeared there "
                "(IPL 143 (2019) 37-40), and a short note is the journal's own format."),
        "pages": pages,
        "quotations": rows,
        "quotations_found": len(rows) - bad,
        "requirements": {
            "length": {"limit": "nine printed pages", "our_note": "6 pages in article class, 11pt",
                       "verdict": "within the limit, with room for the journal's own layout",
                       "source": "ipl_journal_page"},
            "generative_ai": {
                "required": "a declaration section in the manuscript, in the publisher's wording",
                "our_action": ("the note carries the section 'Declaration of generative AI and "
                               "AI-assisted technologies in the manuscript preparation process' in "
                               "exactly that wording, naming Claude and Claude Code, plus the fuller "
                               "disclosure this project has used since its first stage; the use of AI "
                               "in the research process itself is described in the reproducibility "
                               "section, as the policy requires"),
                "source": "elsevier_generative_ai_policy"},
            "fees": {
                "subscription_route": "no author charge; APCs apply to open access articles only",
                "apc_for_IPL": "USD 2,880 excluding tax",
                "apc_verified_from_a_dump": False,
                "caveat": ("the APC figure comes from a search result quoting the journal's "
                           "ScienceDirect page, which cannot be fetched from this host (403 with a "
                           "captcha; the 403 is dumped). It must be re-read in a browser before any "
                           "decision that depends on it. Nothing in the submission plan does: the "
                           "subscription route is free of charge."),
                "source": "elsevier_pricing_policy"},
            "unverified_from_this_host": [
                "Guide for Authors itself (format, cover letter, LaTeX template, referee "
                "suggestions): sciencedirect.com answers 403 to every non-browser client here",
            ],
        },
        "fallbacks": ["Discrete Applied Mathematics (Elsevier)",
                      "Experimental Mathematics (Taylor & Francis)"],
        "order": ("Zenodo record with a DOI first, then submission: the field moved three times in "
                  "two months and arXiv is not available to this author, so the timestamp has to be "
                  "our own."),
        "all_pass": bad == 0,
    }
    with open(os.path.join(ROOT, "results", "json", "w_venue.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"{out['quotations_found']}/{len(rows)} venue quotations found in the dumped pages")
    for r in rows:
        if not r["found_in_dump"]:
            print("  MISSING", r["page"], ":", r["quote"][:80])
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())

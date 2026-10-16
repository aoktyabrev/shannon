"""J.0 -- the requirements of Discrete Applied Mathematics, quoted from dumped pages.

As scripts/w_venue.py did for IPL: every rule the merged paper is shaped by is a verbatim
quotation from a page in sources/venue/ (URL, HTTP status and SHA-256 kept beside it), and
this script re-checks each one and writes results/json/j_venue.json.  The live Guide for
Authors answers 403 to this host, as it did for IPL; the newest Internet Archive copy is from
2024-01-08, and everything taken from it is dated evidence, marked so, to be confirmed in a
browser before submission.  What could not be found at all is listed as UNVERIFIED.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from w_venue import sha, text  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VEN = os.path.join(ROOT, "sources", "venue")
G = "dam_guide_for_authors_wayback2024"
QUOTES = [
    ("dam_journal_page", "what the journal takes",
     "Contributions presented to the journal can be research papers, short notes, surveys, and possibly research problems."),
    (G, "article type for a long paper", "Contribution - Full length original research article of more than 10 pages."),
    (G, "article type for a short paper", "Note - A short self-contained original research article of 10 pages or less"),
    (G, "Communications go through a board member",
     "Please note that Communications should be sent directly to a member of the Editorial Board chosen by the author."),
    (G, "the LaTeX class", "You are recommended to use the Elsevier article class elsarticle.cls to prepare your manuscript and BibTeX to generate your bibliography."),
    (G, "first submission may be a single PDF",
     "You may choose to submit your manuscript as a single Word or PDF file to be used in the refereeing process."),
    (G, "sources are needed for typesetting", "Editable files (e.g., Word, LaTeX) are required to typeset your article for final publication."),
    (G, "a preprint is not prior publication", "Sharing your preprints e.g. on a preprint server will not count as prior publication"),
    (G, "not under consideration elsewhere", "that it is not under consideration for publication elsewhere"),
    (G, "hybrid journal", "Supports open access"),
    (G, "highlights", "include 3 to 5 bullet points (maximum 85 characters, including spaces, per bullet point)"),
    (G, "AI in writing, 2024 wording (stricter than the live policy)",
     "authors should only use these technologies to improve readability and language"),
    (G, "AI declaration: placement", "by adding a statement at the end of their manuscript in the core manuscript file, before the References list"),
    ("elsevier_generative_ai_policy", "the policy's date", "Policy updated June 2026."),
    ("elsevier_generative_ai_policy", "drafting is allowed, substitution is not",
     "AI tools may support drafting or improving clarity, but they must not replace your intellectual contribution."),
    ("elsevier_generative_ai_policy", "AI in the research process goes in Methods",
     "Where AI tools are used as part of the research process rather than manuscript preparation, this use should be described in detail in the Methods section."),
    ("elsevier_generative_ai_policy", "declaration required",
     "Authors should disclose the use of AI tools for manuscript preparation in a separate AI declaration statement included in their manuscript upon submission."),
    ("elsevier_generative_ai_policy", "section title",
     "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"),
    ("elsevier_generative_ai_policy", "keep records of the use",
     "This may include retaining logs provided by the tool, saving prompts and generated outputs"),
    ("elsevier_pricing_policy", "the subscription route is free in a hybrid journal",
     "Authors publishing in hybrid journals can publish under the subscription model at no cost"),
    ("elsevier_pricing_policy", "the APC range, for reference",
     "fees range between approximately $200 and $11,400 US Dollars, excluding tax"),
]
UNVERIFIED = [
    ("the live Guide for Authors", "sciencedirect.com answers 403 to this host (dump kept); the 2024-01-08 archive copy is used, dated"),
    ("the APC of Discrete Applied Mathematics itself", "shown only on sciencedirect.com and in Elsevier's APC list, neither reachable; only the Elsevier-wide range is quoted"),
    ("a limit on the number of submissions, or a rule on resubmission after rejection",
     "the 2024 guide says nothing on either (searched for resubmi, appeal, rejected); the live page could not be read"),
]


def main():
    rows, bad = [], 0
    for page, what, q in QUOTES:
        http = open(os.path.join(VEN, page + ".http")).read().strip()
        ok = q in text(page)
        in_sources = ("> " + q) in open(os.path.join(ROOT, "SOURCES.md"), encoding="utf-8").read()
        ok = ok and in_sources
        rows.append({"page": page, "url": open(os.path.join(VEN, page + ".url")).read().strip(), "http": http,
                     "sha256": sha(page)[:16], "what": what, "quote": q, "found": ok,
                     "dated_archive_copy": page == G})
        bad += not ok
    out = {"venue": "Discrete Applied Mathematics (Elsevier)", "quotes": rows, "missing": bad,
           "unverified": [{"item": a, "why": b} for a, b in UNVERIFIED],
           "reading": {
               "article_type": "Contribution (more than 10 pages); a 12-18 page paper is a Contribution, not a Note or a Communication",
               "format": "elsarticle and BibTeX recommended; a single PDF suffices at first submission, editable sources at revision",
               "preprints": "the two Zenodo preprints do not count as prior publication",
               "fees": "hybrid journal: the subscription route costs nothing; the journal's own APC is UNVERIFIED",
               "ai": ("the live policy (June 2026) allows AI support in drafting but not as a substitute for the authors' "
                      "contribution, asks for a declaration section, and puts AI used in the research itself into Methods; "
                      "the 2024 guide's 'only readability and language' is older and stricter, and the paper follows the live "
                      "policy while saying plainly what the tools did"),
               "resubmission": "UNVERIFIED"},
           "all_found": bad == 0}
    json.dump(out, open(os.path.join(ROOT, "results", "json", "j_venue.json"), "w"), indent=2)
    print(f"{len(QUOTES) - bad}/{len(QUOTES)} quotations found; {len(UNVERIFIED)} items UNVERIFIED")
    for r in rows:
        if not r["found"]:
            print("  MISSING", r["page"], ":", r["quote"][:90])
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

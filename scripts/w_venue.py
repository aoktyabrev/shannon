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
    ("ipl_guide_for_authors_wayback2024", "length limit, with the editors' discretion",
     "manuscripts are generally limited in length to nine pages when they appear in print. The "
     "editors have the authority to make exceptions to this limit"),
    ("ipl_guide_for_authors_wayback2024", "where submission happens",
     "All contributions must be submitted through the Editorial Manager site at "
     "https://www.editorialmanager.com/ipl/default.aspx"),
    ("ipl_guide_for_authors_wayback2024", "one shot only",
     "In IPL all rejection decisions are final, independently of the basis for the rejection, and "
     "resubmissions of rejected papers is not allowed."),
    ("ipl_guide_for_authors_wayback2024", "the expected LaTeX class",
     "You are recommended to use the Elsevier article class elsarticle.cls to prepare your "
     "manuscript and BibTeX to generate your bibliography."),
    ("ipl_guide_for_authors_wayback2024", "the accessible introduction the journal asks for",
     "the introductory part of the paper must contain a clear explanation, in relatively "
     "accessible language, of the merits and context of its scientific contribution"),
    ("ipl_guide_for_authors_wayback2024", "gen-AI section title, the journal's 2024 wording",
     "The statement should be placed in a new section entitled"),
    ("ipl_guide_for_authors_wayback2024", "gen-AI placement",
     "adding a statement at the end of their manuscript in the core manuscript file, before the "
     "References list"),
    ("ipl_guide_for_authors_wayback2024", "a competing-interest statement is required either way",
     "A competing interests statement is provided, even if the authors have no competing interests "
     "to declare"),
    ("ipl_guide_for_authors_wayback2024", "and it is uploaded as a separate file",
     "Corresponding authors should then use this tool to create a shared statement and upload to "
     "the submission system at the Attach Files step."),
    ("ipl_guide_for_authors_wayback2024", "referee suggestions are part of the checklist",
     "Referee suggestions and contact details provided, based on journal requirements"),
    ("ipl_guide_for_authors_wayback2024", "a preprint is not prior publication",
     "preprints can be shared anywhere at any time, in line with Elsevier"),
    ("ipl_guide_for_authors_wayback2024", "the data statement",
     "we require you to state the availability of your data in your submission"),
    ("ipl_guide_for_authors_wayback2024", "data and software must be cited like literature",
     "you are expected to cite the data in your manuscript and reference list"),
    ("ipl_guide_for_authors_wayback2024", "reference style",
     "Indicate references by number(s) in square brackets in line with the text."),
    ("ipl_guide_for_authors_wayback2024", "postal address and e-mail of the corresponding author",
     "Provide the full postal address of each affiliation, including the country name"),
    # --- the live Guide for Authors, read in a browser by the author on 2026-09-26 and pasted
    # --- into sources/venue/ (the page itself cannot be fetched from this host)
    ("ipl_guide_for_authors_live_2026-09-26", "length", "manuscripts are generally limited in length to nine pages when they appear in print"),
    ("ipl_guide_for_authors_live_2026-09-26", "review and appeal", "Only one appeal per submission will be considered and the appeal decision will be final."),
    ("ipl_guide_for_authors_live_2026-09-26", "a preprint is not prior publication", "Sharing preprints, such as on a preprint server, will not count as prior publication."),
    ("ipl_guide_for_authors_live_2026-09-26", "competing interests via their tool", "Authors with no competing interests to declare should select the option \"I have nothing to declare\"."),
    ("ipl_guide_for_authors_live_2026-09-26", "the funding sentence to use when there is none", "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."),
    ("ipl_guide_for_authors_live_2026-09-26", "AI declaration: placement", "adding a statement at the end of the manuscript when the paper is first submitted"),
    ("ipl_guide_for_authors_live_2026-09-26", "AI declaration: the section title, live wording", "Title of new section: Declaration of generative AI and AI-assisted technologies in the manuscript preparation process."),
    ("ipl_guide_for_authors_live_2026-09-26", "AI declaration: the statement, live wording", "During the preparation of this work the author(s) used [NAME OF TOOL / SERVICE] in order to [REASON]. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article."),
    ("ipl_guide_for_authors_live_2026-09-26", "source files, not a PDF", "A PDF is not an acceptable source file."),
    ("ipl_guide_for_authors_live_2026-09-26", "postal address required", "Ensure that you provide the full name and postal address of each affiliation, including the country name."),
    ("ipl_guide_for_authors_live_2026-09-26", "abstract limit", "concise and factual abstract which does not exceed 250 words"),
    ("ipl_guide_for_authors_live_2026-09-26", "highlights are required", "You are required to provide article highlights at submission."),
    ("ipl_guide_for_authors_live_2026-09-26", "highlights: form and size", "Highlights should consist of 3 to 5 bullet points, each a maximum of 85 characters, including spaces."),
    ("ipl_guide_for_authors_live_2026-09-26", "CRediT is required", "Corresponding authors are required to acknowledge co-author contributions using CRediT"),
    ("ipl_guide_for_authors_live_2026-09-26", "research data: option C", "Deposit your research data in a relevant data repository."),
    ("ipl_guide_for_authors_live_2026-09-26", "data statement", "you are required to state the availability of any data at submission"),
    ("ipl_guide_for_authors_live_2026-09-26", "reference style", "Abbreviate journal names according to the List of Title Word Abbreviations (LTWA)."),
    ("ipl_guide_for_authors_live_2026-09-26", "the [dataset] marker", "Add [dataset] immediately before your reference."),
]


def text(name):
    p = os.path.join(VEN, name + ".txt")
    if os.path.exists(p):
        return re.sub(r"\s+", " ", open(p, encoding="utf-8").read())
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
    ext = ".txt" if os.path.exists(os.path.join(VEN, name + ".txt")) else ".html"
    with open(os.path.join(VEN, name + ext), "rb") as f:
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
            "length": {"limit": "nine printed pages", "our_note": "six pages standalone; five in the journal's own print layout, measured",
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
            "guide_for_authors": {
                "live_page": ("Read in a browser by the author on 2026-09-26 and pasted into "
                              "sources/venue/ipl_guide_for_authors_live_2026-09-26.txt; this host "
                              "cannot fetch it (403 with a captcha, dumped as evidence)"),
                "archive_snapshot": ("The 2024-04-24 Internet Archive copy is kept as well; where "
                                     "the two differ the live text wins, and the differences are "
                                     "listed below"),
                "what_it_says": {
                    "length": "nine printed pages; ours is five",
                    "review": ("single anonymized; one formal appeal per submission is possible "
                               "and its decision is final. The 2024 snapshot instead said "
                               "resubmission of a rejected paper is not allowed -- that sentence "
                               "is not in the live text, so it is not claimed here"),
                    "source_files": ("editable source is required and 'A PDF is not an acceptable "
                                     "source file': the package ships the self-contained .tex, "
                                     "refs.bib and .bbl next to the PDF"),
                    "latex": "their elsarticle template is what the package uses",
                    "abstract": "at most 250 words; ours is 162",
                    "keywords": "1 to 7; ours is 6, none of them a phrase with 'and' or 'of'",
                    "highlights": ("**required**, 3 to 5 bullets of at most 85 characters, as a "
                                   "separate editable file with 'highlights' in its name: "
                                   "highlights.txt, four bullets, 74-80 characters"),
                    "competing_interest": ("the declarations tool always, 'I have nothing to "
                                           "declare' when there is nothing, and the .docx it "
                                           "produces uploaded at the attach-files step; the "
                                           "manuscript also carries the statement"),
                    "funding": ("their recommended sentence for unfunded work is in the "
                                "manuscript verbatim"),
                    "credit": "a CRediT contribution statement is required; it is in the manuscript",
                    "generative_ai": ("a new section at the end, before the references, with their "
                                      "section title and statement: the note matches the live "
                                      "wording word for word, which settles the discrepancy the "
                                      "2024 snapshot had left open"),
                    "research_data": ("Option C: deposit in a repository, cite and link the "
                                      "dataset -- the Zenodo archive is a [dataset] reference with "
                                      "repository and version, as their example formats it"),
                    "data_statement": "required at submission; answered with the Zenodo DOI",
                    "references": ("numbered in order of appearance, journal names abbreviated per "
                                   "LTWA, DOIs where available: elsarticle-num with refs.bib"),
                    "title_page": ("full postal address of the affiliation and the corresponding "
                                   "author's e-mail -- the postal address is the only field the "
                                   "repository cannot fill"),
                },
            },
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

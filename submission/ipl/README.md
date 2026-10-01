# submission/ipl — the Information Processing Letters package

Nothing here is a second version of the note. The text lives once, in
`../../note/note-abstract.tex` and `../../note/note-content.tex`; every file here includes those,
so a correction cannot land in one copy and miss the other, and `scripts/w_checknums.py`
re-checks the numbers in that one place (68 ledger entries, 0 unaccounted tokens) and refuses to
run if a wrapper stops including the shared text.

| file | what it is |
|---|---|
| `note_ipl.tex` | the submission file: `elsarticle` with `[review,12pt]` — double spaced, line numbered, 14 pages |
| `note_ipl_print.tex` | the same text in the journal's print layout (`[final,3p,times,twocolumn]`) — **5 pages**, against the journal's limit of nine |
| `ipl-body.tex` | shared preamble, front matter and the two `\input`s |
| `refs.bib` | symlink to `../../note/refs.bib`, through `elsarticle-num`, journal names abbreviated as the guide asks |
| `cover_letter.md` | the letter; the referee table at the end goes into the submission form, not into the letter |
| `highlights.txt` | required by the journal: four bullets, 74–80 characters of the 85 allowed |
| `competing_interest.txt` | **a note to self, never uploaded.** In the form, Elsevier's declarations tool produces the .docx after "I have nothing to declare" is selected; the declaration itself is in the manuscript |

Build: `pdflatex note_ipl && bibtex note_ipl && pdflatex note_ipl && pdflatex note_ipl`
(and the same for `note_ipl_print`, which exists only to measure the printed length).

**The preamble loads `cmap`, `fontenc` and `lmodern` on purpose.** Without them the Type 1 fonts
carry no ToUnicode map and the PDF's text layer is mush: a copy-paste returns `ve-dimensional` for
"five-dimensional", `nite` for "finite" and a control character for the en dash — which is what
publisher screening tools read. `scripts/w_package.py` checks the finished PDF for exactly that
damage; the check needs `pypdf`, which this repository does not depend on, so it runs when pypdf is
importable and says plainly when it is not:

```
python3 -m venv /tmp/pdfvenv && /tmp/pdfvenv/bin/pip install pypdf
/tmp/pdfvenv/bin/python scripts/w_package.py     # text layer: PASS
```

## The journal's rules, and where the package stands against each

The live Guide for Authors cannot be fetched from this host (`sciencedirect.com` answers 403 with
a captcha, and the 403 is dumped as evidence), so **the author read it in a browser on 2026-09-26
and pasted it in**; the passages the package is built against are kept in
`sources/venue/ipl_guide_for_authors_live_2026-09-26.txt` and re-checked quotation by quotation by
`scripts/w_venue.py` — 41/41 across all venue sources. The 2024-04-24 Internet Archive snapshot is
kept too, and where the two differ the live text wins.

| the rule, from the live guide | us |
|---|---|
| nine printed pages | five in the journal's print layout |
| abstract at most 250 words | 162 |
| 1–7 keywords, no phrases with "and"/"of" | six |
| **highlights are required**: 3–5 bullets, ≤85 characters, separate editable file with "highlights" in the name | `highlights.txt`, four bullets, 74–80 characters |
| editable source required; **"A PDF is not an acceptable source file"** | the self-contained `.tex`, `refs.bib` and `.bbl` ship beside the PDF |
| their `elsarticle` LaTeX template | what the package uses |
| full postal address of the affiliation, corresponding author's e-mail on the title page | e-mail yes; affiliation **Independent researcher, Ukraine** — the author's own standing line, as used on the manuscript he submitted to Experimental Mathematics (his decision of 2026-09-10, recorded in `QUADC5/EXPMATH_FORMAT_REPORT_2026-09-10.md`). If the form insists on street-level detail, pass `--addressline`, `--city`, `--postcode` to `scripts/w_package.py` |
| competing interests through the declarations tool, "I have nothing to declare", .docx uploaded at the attach-files step | `competing_interest.txt` says exactly that; the statement is also in the manuscript |
| the funding sentence for unfunded work | in the manuscript, verbatim |
| CRediT contribution statement | in the manuscript |
| generative-AI declaration: new section at the end, before the references, with their section title and statement | **word for word** — this settles the discrepancy the 2024 snapshot had left open, and nothing needs swapping |
| research data Option C: deposit, cite and link the dataset | the Zenodo archive is a `[dataset]` reference with repository and version, in their example's shape |
| data statement at submission | answer with `10.5281/zenodo.22979509` |
| references numbered in order, journal names abbreviated per LTWA, DOIs where available | `elsarticle-num` with `refs.bib`; the Polak–Schrijver DOI verified against the dumped arXiv page |
| preprint references must name the server **and** carry the preprint DOI | the four 2026 preprints read "arXiv preprint … doi:10.48550/arXiv.…", each DOI checked to resolve to the right abstract page |
| single anonymized review; one formal appeal per submission, its decision final | worth getting right first time, but not the one-shot-and-out that the 2024 snapshot suggested |

A correction to what the 2024 snapshot said: it stated that resubmission of a rejected paper is
not allowed. **That sentence is not in the live guide**, which instead describes a formal appeal
procedure, one appeal per submission. The package is unchanged by this; only the note about how
much a mistake would cost is.

## The upload set

`scripts/w_package.py` assembles what the form asks for, from the same sources — a
self-contained `elsarticle` manuscript with the two shared text files inlined, its PDF, `refs.bib`
and `.bbl`, the letter as plain text with the referee table split out, the referee list, the
competing-interest text, the highlights, and a `MANIFEST.txt` saying which file goes into which
field. It refuses to pretend: it checks that the flattened manuscript contains the shared text verbatim
and comes out the same length as the ordinary build, and it will not call the zip final while a
placeholder remains. As it stands the set is **final** — `ipl-submission.zip`, nine files — because
the affiliation is the author's own standing line rather than something the repository had to
invent. Rebuild it any time, and add street-level address fields if the form asks for them:

```
python3 scripts/w_package.py                                  # as submitted
python3 scripts/w_package.py --addressline '...' --city '...' --postcode '...'
```

## What only you can do

1. **Open the live Guide for Authors** and walk the table above if anything has moved since
   2026-09-26; the package is built against what it said that day.
2. **Submit through Editorial Manager**, `https://www.editorialmanager.com/ipl/default.aspx`
   (the guide's own address — ScholarOne is a different journal's system), following
   `MANIFEST.txt` in the zip: manuscript PDF, source files if the form wants them, cover letter
   pasted, referees entered, competing-interest file attached, highlights if offered, and the data
   statement answered with `10.5281/zenodo.22979509`.
3. **Decide about SSRN.** The form offers to post the manuscript as a preprint on SSRN once it
   enters review. There is already a timestamped preprint on Zenodo, so this is optional; saying
   yes costs nothing and the guide states it has no effect on the editorial outcome.
4. **Record the submission** in `~/SUBMISSIONS.md`: date, manuscript number, status.

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
| `highlights.txt` | optional, four bullets with their character counts |
| `competing_interest.txt` | the statement the journal wants as a separate uploaded file |

Build: `pdflatex note_ipl && bibtex note_ipl && pdflatex note_ipl && pdflatex note_ipl`
(and the same for `note_ipl_print`, which exists only to measure the printed length).

## The journal's rules, and where the package stands against each

The live Guide for Authors cannot be read from this host — `sciencedirect.com` answers 403 with a
captcha — so the rules below are quoted from the **Internet Archive snapshot of 2024-04-24**, the
last readable copy, dumped by `scripts/fetch_venue.sh` and re-checked quotation by quotation by
`scripts/w_venue.py` (23/23 found). **That snapshot is two years older than this note: confirm
each line against the live page in a browser before sending.**

| the rule | us |
|---|---|
| nine printed pages, editors may allow more | five in the journal's print layout |
| `elsarticle.cls` with BibTeX is recommended | exactly what is used |
| the introduction must explain the merits and context in relatively accessible language | section 1 is written that way, and gives the numbers that make the question worth asking |
| references numbered in square brackets, DOIs encouraged, journal names abbreviated | `elsarticle-num`; the Polak–Schrijver DOI is in `refs.bib`, verified against the dumped arXiv page |
| data must be cited in the manuscript **and** in the reference list | the Zenodo archive is a `[dataset]` reference, cited from the data-availability paragraph |
| a competing-interest statement is required even when there is nothing to declare, uploaded as its own file | the sentence is in the manuscript before the references, and the text for the separate file is in `competing_interest.txt` |
| the generative-AI declaration goes in its own section at the end of the manuscript, before the references | it is there — see the caveat below |
| referee suggestions with contact details | six names in `cover_letter.md`, each with the address printed in the paper of theirs that this note cites |
| full postal address of the affiliation, e-mail of the corresponding author | e-mail yes; **the postal address is a placeholder in `ipl-body.tex` and only you can fill it** |
| single blind review; **all rejections are final and resubmission is not allowed** | one attempt, so the checks above are worth the time they cost |

**The one discrepancy, deliberately left visible.** The 2024 guide words the AI section heading
"…in the writing process" and ends the sentence "…the content of the publication". The live
Elsevier policy page, dumped today (HTTP 200), words the heading "…in the manuscript preparation
process" and ends "…the content of the published article". The note follows the live policy page.
If the live guide still prescribes the 2024 wording, swap the heading and that one clause — it is
two edits in `../../note/note-content.tex`, and nothing else depends on them.

## The upload set

`scripts/w_package.py` assembles what the form asks for, from the same sources — a
self-contained `elsarticle` manuscript with the two shared text files inlined, its PDF, `refs.bib`
and `.bbl`, the letter as plain text with the referee table split out, the referee list, the
competing-interest text, the highlights, and a `MANIFEST.txt` saying which file goes into which
field. It refuses to pretend: it checks that the flattened manuscript contains the shared text
verbatim and comes out the same length as the ordinary build, and while the address is a
placeholder the zip is named `ipl-submission-DRAFT-fill-the-address.zip` and `MANIFEST.txt` says
DRAFT. With the address given it writes `ipl-submission.zip` and says FINAL:

```
python3 scripts/w_package.py --addressline '...' --city '...' --postcode '...' --country '...'
```

## What only you can do

1. **Run the line above with your postal address.** That is the only missing field; it produces
   the final zip, and nothing else needs editing by hand.
2. **Open the live Guide for Authors** and walk the table above; fix anything that has moved.
3. **Submit through Editorial Manager**, `https://www.editorialmanager.com/ipl/default.aspx`
   (the guide's own address — ScholarOne is a different journal's system), following
   `MANIFEST.txt` in the zip: manuscript PDF, source files if the form wants them, cover letter
   pasted, referees entered, competing-interest file attached, highlights if offered, and the data
   statement answered with `10.5281/zenodo.22979509`.
4. **Decide about SSRN.** The form offers to post the manuscript as a preprint on SSRN once it
   enters review. There is already a timestamped preprint on Zenodo, so this is optional; saying
   yes costs nothing and the guide states it has no effect on the editorial outcome.
5. **Record the submission** in `~/SUBMISSIONS.md`: date, manuscript number, status.

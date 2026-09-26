# submission/ipl — the Information Processing Letters package

Nothing here is a second version of the note. The text lives once, in
`../../note/note-abstract.tex` and `../../note/note-content.tex`; every file here includes those,
so a correction cannot land in one copy and miss the other, and `scripts/w_checknums.py`
re-checks the numbers in that one place (68 ledger entries, 0 unaccounted tokens).

| file | what it is |
|---|---|
| `note_ipl.tex` | the submission file: `elsarticle` with `[review,12pt]` — double spaced, line numbered, 13 pages |
| `note_ipl_print.tex` | the same text in the journal's print layout (`[final,3p,times,twocolumn]`) — **5 pages**, against the journal's limit of nine |
| `ipl-body.tex` | shared preamble, front matter and the two `\input`s |
| `refs.bib` | symlink to `../../note/refs.bib`, used through `elsarticle-num` |
| `cover_letter.md` | the cover letter; the last paragraph is a note to self and is deleted before sending |

Build:

```
pdflatex note_ipl && bibtex note_ipl && pdflatex note_ipl && pdflatex note_ipl
pdflatex note_ipl_print && bibtex note_ipl_print && pdflatex note_ipl_print   # length check only
```

## Before sending — what could not be checked from here

`sciencedirect.com` answers 403 with a captcha to every non-browser client on this host, so the
Guide for Authors itself was never read; what is quoted in `results/json/w_venue.json` comes from
pages that could be dumped (`sources/venue/`). Open the guide in a browser and confirm:

1. the submission system and whether a separate title page, highlights or a graphical abstract
   are wanted;
2. whether `elsarticle` with `review` is the expected form, and whether line numbering is wanted;
3. whether suggested referees are requested (a list is at the end of the cover letter);
4. the declarations the form asks for beyond the ones already in the manuscript (competing
   interests, funding, data availability, generative AI);
5. the open-access options page, if that route is ever taken — the article publishing charge
   quoted in `w_venue.json` is from a search result, not from a dump, and is marked unverified.
   Nothing here depends on it: the subscription route carries no author charge.

The nine-printed-page limit is quoted verbatim from a page that *was* dumped
(`sources/venue/ipl_journal_page.html`, HTTP 200, 2026-09-26).

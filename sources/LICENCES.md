# Licences of the dumped e-prints

`scripts/fetch_arxiv.sh <id>` fetches these; **they are not committed and not published with
this repository.** Two of the six are under arXiv's non-exclusive distribution licence, which
grants arXiv the right to distribute them and grants us nothing of the kind, so redistributing
any of the dumps — even the four that would allow it — is not something this repository does.
The licence of each, as the dumped abstract page states it:

| arXiv | licence, from `sources/<id>/abs.html` | redistribution by us |
|---|---|---|
| 1504.01472 Mathew–Ostergard | arXiv perpetual non-exclusive (`licenses/nonexclusive-distrib/1.0/`) | no |
| 1808.07438 Polak–Schrijver | arXiv perpetual non-exclusive (`licenses/nonexclusive-distrib/1.0/`) | no |
| 2607.21517 Itty et al. | CC BY 4.0 (`licenses/by/4.0/`) | would be allowed, not done |
| 2607.27869 Gao | CC BY-NC-SA 4.0 (`licenses/by-nc-sa/4.0/`) | would be allowed, not done |
| 2607.29681 Buys–Polak–Zuiddam | CC BY 4.0 (`licenses/by/4.0/`) | would be allowed, not done |
| 2608.30273 Tandon | CC BY 4.0 (`licenses/by/4.0/`) | would be allowed, not done |

The git history was rewritten on 2026-09-26 (`git filter-repo --invert-paths`) so that no
commit of this repository contains the papers, not only the current one.

What *is* committed: `sources/<id>/SHA256` — the checksums of the three files each dump consists
of, so that a re-fetch can be compared byte for byte with what the quotations in `SOURCES.md`
were checked against. `SOURCES.md` itself carries only short verbatim quotations with precise
references, which is quotation, not redistribution.

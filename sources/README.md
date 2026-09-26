# sources/ — the dumps Rule 0 checks against

`SOURCES.md` quotes only from dumped e-prints, and `scripts/check_sources.py` re-checks every
quotation against them. The dumps live here, one directory per arXiv identifier, and
`scripts/fetch_arxiv.sh <id>` reproduces any of them from scratch:

```
scripts/fetch_arxiv.sh 1808.07438     # and 1504.01472, 2607.21517, 2607.27869, 2607.29681, 2608.30273
```

**The third-party papers themselves are not redistributed.** They are present in a working
checkout because the checks need them, but they are not committed and not published with this
repository — not in the git history, not in the Zenodo archive. Two of the six are under arXiv's
perpetual non-exclusive licence, which grants us no right to redistribute them at all;
`sources/LICENCES.md` lists the licence of each. Run the fetch script and
the checks pass identically — the file checksums in each `sources/<id>/SHA256` say whether you
got the same bytes we did.

`sources/venue/` is the same idea for the publisher pages whose rules the note is shaped by
(`scripts/fetch_venue.sh`): only the URL, the HTTP status and the SHA-256 of each page are kept
here, never the page.

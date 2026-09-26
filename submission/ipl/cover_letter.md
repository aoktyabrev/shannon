To the Editors, *Information Processing Letters*

Dear Editors,

Please consider the enclosed note, **"The Polak–Schrijver code has exactly eight private
pairs"**, for publication in *Information Processing Letters*.

**It is a short note with a single theorem.** The note states one result, proves it, and
reports the finite computations around it; in the journal's print layout it runs to five pages,
within the journal's stated limit. Two statements that are weaker than the theorem are labelled
as search evidence rather than proof, at the points where they are made.

**The theorem closes a specific route to improving a record, and that route is the one all of
the recent work stands on.** The lower bound on the Shannon capacity of the seven-cycle improved
four times between July and August 2026 — Itty, Rosin, Carstensen and Reichman; Gao; Buys, Polak
and Zuiddam; Tandon — and every one of those improvements is built on the same five-dimensional
base gadget: the 367-word independent set of Polak and Schrijver together with eight *private
pairs*, vertices outside the code with a single neighbour in it. The private-pair count is the
parameter those recursions are most sensitive to: one more pair would move the record by about
1.7·10⁻⁴, several times the spread between the published schemes, so "is there a ninth pair?"
has been the obvious next question.

The answer is no, exactly. In the whole of the ambient space precisely eight vertices have a
single neighbour in that code — the eight already in use — and their confusability graph is a
matching, so all eight are simultaneously admissible and eight is the maximum. The proof is a
short lemma plus two finite checks that a reader can repeat from the printed code. The note also
records which neighbouring routes are closed: all eight codes the Polak–Schrijver construction
can produce, with private-pair counts 5, 6, 6, 6, 7, 7, 7, 8; the arithmetic that rules out
smaller codes; and an exhaustive sweep over the automorphism group which explains why the
published construction has to replace one auxiliary vector.

The journal is the natural home for the note in a second sense: the code the theorem is about
was published here, in Polak and Schrijver, *Inform. Process. Lett.* **143** (2019) 37–40.

**Prior dissemination and priority.** The note is deposited as a preprint on Zenodo,
doi:10.5281/zenodo.22979509, dated 26 September 2026, together with the archive of the code and
data. There is no arXiv version. The note has not been published elsewhere, has not been
submitted to another journal, and is not under consideration anywhere else; the Zenodo record
exists to timestamp the result in a fast-moving problem — four improvements to this bound appeared
between July and August 2026 — and, as your guide puts it, sharing a preprint does not count as
prior publication.

**Data and code.** Everything the note reports is in that archive: an exact verifier in C with
no dependencies, its calibration on cases where it can fail, the sets with their SHA-256, and a
script that reconciles every number printed in the note against the stored computation that
produced it.

**Declarations.** The manuscript carries the declaration of generative AI use in the wording
your policy prescribes, and the use of AI in the research process itself is described separately
in the reproducibility section, as the policy asks. There are no competing interests and no
funding to declare. I am the sole author.

Thank you for considering the note.

Sincerely,

Artem Oktiabrev
ORCID 0009-0003-3626-2002
aoktyabrev@gmail.com

---

*Suggested referees — the submission checklist asks for names with contact details. These are the
people who have worked directly on this construction; each address below is the one printed in
their own paper that this note cites, so check it is still current before entering it:*

| referee | why | contact, as printed in |
|---|---|---|
| Sven C. Polak, Korteweg–de Vries Institute, University of Amsterdam | co-author of the code the theorem is about | `s.c.polak@uva.nl` — arXiv:1808.07438 |
| Alexander Schrijver, Korteweg–de Vries Institute, University of Amsterdam | the same | `a.schrijver@uva.nl` — arXiv:1808.07438 |
| Ravi Tandon, University of Arizona | holds the current record on the same gadget | `tandonr@arizona.edu` — arXiv:2608.30273 |
| Patric R. J. Östergård, Aalto University | the previous generation of bounds for these powers | `patric.ostergard@aalto.fi` — arXiv:1504.01472 |
| Yu Gao | defined the gadget whose parameter the theorem bounds | no address in arXiv:2607.27869 |
| Jeroen Zuiddam, University of Amsterdam | the Lean-verified refinement of the same base gadget | no address in arXiv:2607.29681 |

*Delete this section before sending the letter itself; it belongs in the submission form, not in
the letter.*

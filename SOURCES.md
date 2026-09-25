# SOURCES — verbatim quotations

Rule 0: every external number, definition or formula used anywhere in this repository
is backed below by a verbatim quotation from a dumped source. The dumps live in
`sources/<arXiv-id>/`:

* `abs.html` — the abstract page (title, authors, date, as arXiv serves them);
* `paper.pdf` — the PDF; `paper.txt` — its text layer where available;
* `src/` — the LaTeX source from `https://arxiv.org/e-print/<id>`, i.e. the authors' own text;
* `SHA256` — checksums of the three downloaded files.

Quotations are taken from the LaTeX source. `sources/<id>/src/*.tex` line numbers are given
so that each quotation can be found again. The dumps were taken on 2026-09-25;
`scripts/fetch_arxiv.sh <id>` reproduces them.

Three works are cited here only **through** other papers, because they are not on arXiv and
were not obtained: Baumert–McEliece–Rodemich–Rumsey–Stanley–Taylor (1971), Vesel–Žerovnik
(*Inform. Process. Lett.* 81 (2002) 277–282) and Lovász (*IEEE Trans. Inform. Theory* 25
(1979) 1–7). Where a number of theirs is used, the quotation is from the citing paper and
says so. Nothing in this repository depends on a number that has no quotation at all.

---

## [PS19] Polak, Schrijver — arXiv:1808.07438

`abs.html`: `citation_title` = "New lower bound on the Shannon capacity of C7 from circular
graphs"; authors Polak, Sven C.; Schrijver, Alexander. Published as *Information Processing
Letters* 143 (2019) 37–40. The dumped e-print is the arXiv version of 26.11.2018.

**PS19-1 (the result and the circular graph), abstract, `paper.tex` line 131:**
> We give an independent set of size~$367$ in the fifth strong product power of~$C_7$, where~$C_7$ is the cycle on~$7$ vertices. This leads to an improved lower bound on the Shannon capacity of~$C_7$: $\Theta(C_7)\geq 367^{1/5} > 3.2578$. The independent set is found by computer, using the fact that the set~$\{t \cdot (1,7,7^2,7^3,7^4) \,\, | \,\, t \in \Z_{382}\} \subseteq \Z_{382}^5$ is independent in the fifth strong product power of the circular graph~$C_{108,382}$. Here the circular graph~$C_{k,n}$ is the graph with vertex set~$\Z_{n}$, the cyclic group of order~$n$, in which two distinct vertices are adjacent if and only if their distance (mod~$n$) is strictly less than~$k$.

**PS19-2 (the Lovász upper bound for odd cycles), Eq. (2), `paper.tex` lines 149–151:**
> More generally, for odd~$n$,
> \Theta(C_n) \leq \vartheta(C_n) = \frac{n\cos(\pi/n)}{1+\cos(\pi/n)}.

**PS19-3 (the upper bound 3.3177, and the lower bounds 350, 343, 108), `paper.tex` line 155:**
> while the best known upper bound is~$\Theta(C_7)\leq \vartheta(C_7) < 3.3177$. Here we give an independent set of size~$367$ in~$C_7^5$, which yields~$\Theta(C_7)\geq 367^{1/5} > 3.2578$. The best previously known lower bound on~$\Theta(C_7)$ is~$\Theta(C_7) \geq 350^{1/5} > 3.2271$, found by Mathew and \"Osterg{\aa}rd~$\cite{matos}$. They proved that~$\alpha(C_7^5) \geq 350$ using stochastic search methods that utilize the symmetry of the problem. In~$\cite{baumert}$, a construction is given of an independent set of size~$7^3=343$ in~$C_7^5$. The best known lower bound on~$\alpha(C_7^4)$ is~$108$, by Vesel and \v{Z}erovnik~\cite{veszer}.

This single sentence is the citation carrier for three numbers whose primary sources were not
obtained: **343** (Baumert et al. 1971), **108** (Vesel–Žerovnik 2002) and the **3.3177**
upper bound (Lovász 1979). **350** has a primary source, [MO17] below.

**PS19-4 (small values of α(C₇^d)), Table 1, `paper.tex` lines 160–161 with its key at 165–169:**
> $d$ & 1 & 2 & 3 & 4 & 5 \\ \hline
> $\alpha(C_7^d)$ & 3 & $10^a$ & $33^d$ & $108^e$--$115^b$ & $367^f$--$401^c$
>
> $^a$ $\alpha(C_n^2)= \floor{(n^2-n)/4}$ \cite[Theorem 2]{baumert}
> $^d$ Baumert et al.~\cite{baumert}
> $^e$ Vesel and \v{Z}erovnik~\cite{veszer}

So α(C₇) = 3, α(C₇^⊠2) = 10 and α(C₇^⊠3) = 33 are exact values, 33 due to Baumert et al.;
108 and 367 are lower bounds. The closed form ⌊(n²−n)/4⌋ is quoted with it.

**PS19-5 (the circular independent set S), Proposition 1, `paper.tex` lines 190–191:**
> The set~$S:=\{t \cdot (1,7,7^2,7^3,7^4) \,\, | \,\, t \in \Z_{382}\} \subseteq \Z_{382}^5$ is independent in $C_{108,382}^5$.

**PS19-6 (the five steps that produce the 367-set), Section 3, `paper.tex` lines 277–282:**
> \item Start with the independent set~$S$ in~$C_{108,382}^5$ from Proposition~\ref{is}.
> \item Add the word~$(40,123,40,123,40)$ mod~$382$ to each word in~$S$.
> \item Replace each letter~$i$, which we now consider to be an integer between~$0$ and~$381$ and not anymore an element in~$\Z_{382}$, in each word from~$S$ by~$\floor{i/54.5}$. Now we have a set of words~$S'$ with only symbols in~$[0,6]$ in it, which we consider as elements of~$\Z_7$.
> \item Remove each word~$u\in S'$ for which there is a~$v \in S'$ such that~$uv \in E(C_7^5)$ from~$S'$, i.e., we remove~$u$ if there is a~$v \in S'$ with~$v \neq u$ such that~$u_i-v_i\in \{0,1,6\}$ for all~$i \in [1,5]$. We denote the set of words which are not removed from~$S'$ by this procedure by~$M$. The computer finds~$|M| = 327$. Note that~$M$ is independent in~$C_7^5$.
> \item \label{v} Find the best possible extension of~$M$ to a larger independent set in~$C_7^5$. To do this, consider the subgraph~$G$ of~$C_7^5$ induced by the words~$x$ in~$\Z_7^5$ with the property that~$M\cup \{x\}$ is independent in~$C_7^5$. This graph is not large, in this case it has~$71$ vertices and~$85$ edges, so a computer finds a maximum size independent set~$I$ in~$G$ quickly. The computer finds $|I|=\alpha(G)=40$, so we can add~$40$ words to~$M$. Write~$R:=M \cup I$. Then~$|R|=327+40=367$ and~$R$ is independent in~$C_7^5$.

**PS19-7 (the 367 words themselves), Appendix, `paper.tex` lines 289–293.** The appendix prints
the 367 five-letter words as a single `\texttt{...}` block, beginning
`02020, 02112, 02204, 02306, 02461, ...` and ending `..., 64154, 64340, 65105, 66025`.
Transcribed into `sets/C7_d5_367_polak_schrijver.txt` by the extraction recorded in
`results/json/sources.json`.

**PS19-8 (the set is not easily extendable), `paper.tex` line 284:**
> Also, the independent set~$R$ of size~$367$ did not seem to be easily extendable. A local search was performed, showing that there exists no triple of words from~$R$ such that if one removes these three words from~$R$, four words can be added to obtain an independent set of size~$368$ in~$C_7^5$.

---

## [MO17] Mathew, Östergård — arXiv:1504.01472

`abs.html`: `citation_title` = "New Lower Bounds for the Shannon Capacity of Odd Cycles";
authors Mathew, K. Ashik; Östergård, Patric R. J. Published as *Designs, Codes and
Cryptography* 84 (2017) 13–22. Notation: `G(d,p)` is α(C_p^⊠d) and `c(G)` is Θ(G).

**MO17-1 (the 350), abstract, `arxiv.tex` lines 69–72:**
> $\alpha(C_7^5)\geq 350$, $\alpha(C_{11}^4)\geq 748$, $\alpha(C_{13}^4)\geq 1534$ and
> of $C_7$ and $C_{15}$:
> $c(C_7)\geq 350^{\frac{1}{5}}> 3.2271$ and $c(C_{15})\geq 381^{\frac{1}{3}}> 7.2495$.

**MO17-2 (the ϑ upper bounds), `arxiv.tex` lines 379–387:**
> \vartheta(p)=\frac{p\cos\frac{\pi}{p}}{1+\cos\frac{\pi}{p}}
> gives
> upper bounds for the Shannon capacity of the odd cycle $C_p$~\cite{Lova1979}.
> Using this function,
> $c(C_7)< 3.3177$, $c(C_9)< 4.3601$,
> $c(C_{11})< 5.3864$, $c(C_{13})< 6.4042$
> and $c(C_{15})< 7.4172$.

**MO17-3 (the table of known bounds, second column = α(C_p^⊠2)), Table 1, `arxiv.tex` lines 400–408:**
> $p\backslash d$&1&2&3&4&5\\
> $5$ & $^a2^a$ & $^a5^a$ & $^c10^f$ & $^c25^d$ & $^c50$--$55^j$\\
> $7$ & $^a3^a$ &$^a10^a$ & $^f33^f$ & $^h108$--$115^d$ & $^k350$--$401^j$\\
> $9$ & $^a4^a$ &$^a18^a$ & $^e81^d$ & $^c324$--$361^j$ & $^c1458$--$1575^j$\\
> $11$ & $^a5^a$ &$^a27^a$ & $^e148^d$ & $^k748$--$814^d$ & $^c3996$--$4477^d$\\
> $13$ & $^a6^a$ &$^a39^a$ & $^g247^i$ & $^k1534$--$1605^d$ & $^c9633$--$10432^d$\\
> $15$ & $^a7^a$ &$^a52^a$ & $^k381$--$390^d$ & $^b2720$--$2925^d$ & $^c19812$--$21937^d$\\\hline

The d = 2 column (5, 10, 18, 27, 39, 52) is what `scripts/mis` is calibrated against.

---

## [IRCR26] Itty, Rosin, Carstensen, Reichman — arXiv:2607.21517

`abs.html`: `citation_title` = "Improved lower bounds for the Shannon capacity of odd cycles";
authors Itty, Nathaniel; Rosin, Christopher D.; Carstensen, Chase; Reichman, Daniel;
`citation_date` = 2026/07/23. Dumped e-print of 30.07.2026.

**IRCR26-1 (the four new independent sets), abstract, `main.tex` lines 103–104:**
> We construct independent sets of size $134753$ in $C_7^{10}$, $21909$ in $C_{11}^{6}$, $62530$ in $C_{13}^{6}$, and $8076974$ in $C_{15}^{8}$, improving the best known lower bounds for the Shannon capacity of these graphs to $\Theta(C_7)\geq 134753^{1/10}>3.258020$, $\Theta(C_{11})\geq 21909^{1/6}>5.289773$, $\Theta(C_{13})\geq 62530^{1/6}>6.300109$, and $\Theta(C_{15})\geq 8076974^{1/8}>7.301399$. We also improve the best known lower bounds on the independence numbers of several individual strong products of odd cycles that do not improve the Shannon capacity lower bound. The constructions were discovered through iterative interactions with a Large Language Model (LLM), illustrating the potential of LLMs for finding explicit combinatorial constructions.

**IRCR26-2 (the recipe for C₇^⊠10), Section 3.1, `main.tex` lines 155–189.** Quoted in the
pieces the reconstruction uses:
> Let $R$ be the explicit size-367 set of 5-vectors as given in the Appendix of the original publication \cite{polak2019new}.  Note that $R \times R$ would give a set of $367 \times 367 = 134689$ 10-vectors that constitute an independent set in the strong $10$-product.  We are instead going to delete several vectors from $R$ to yield $B$, and then take $B \times B$ augmented with additional vectors derived from $R$, to reach a larger independent set.
>
> Let $B$ be a subset of 359 vectors from $R$, defined as $B = R \setminus \{r_j: 0 \leq j < 8\}$.
>
> Taking arithmetic modulo 7, define:
> \[X_0 = \{(2-w_1, w_3, w_0, (2-w_2), w_4): w \in R\}\]
> Let $X$ be $X_0$ with the vector (2,4,6,3,5) replaced by (1,5,6,3,5).
>
> Define $J_0 = \{0,5,6\}$ and $J_1 = \{1,2,3,4,7\}$.  Let:
> \[P_H = \{r_j: j \in J_0\} \cup \{q_j: j \in J_1\}\]
> \[P_V = \{q_j: j \in J_0\} \cup \{r_j: j \in J_1\}\]
>
> \[A = \{x \in X|\exists y \in P_V : x \sim y\}\]
> \[D = \{x \in X|\exists y \in P_H : x \sim y\}\]
>
> The set $A$ has 20 vectors and $D$ has 26.
>
> If $j \in J_0$ and $x \in A$, or $j \in J_1$ and $x \in D$, then let $h_j(x) = q_j$.  Otherwise let $h_j(x) = r_j$.
>
> If $j \in J_0$ and $x \in D$, or $j \in J_1$ and $x \in A$, then let $v_j(x) = q_j$.  Otherwise let $v_j(x) = r_j$.
>
> \[I = (B \times B) \cup \{(h_j(x),x): x \in X, 0 \leq j < 8\} \cup \{(x,v_j(x)): x \in X, 0 \leq j < 8\}\]
>
> $I$ has $359 \times 359 + 8 \times 367 + 8 \times 367 = 134753$ vectors.

The table of the eight pairs (`main.tex` lines 163–174) is transcribed into
`scripts/construct_c7_d10.py` as the list `RQ`:
> 0 & (1,3,4,4,6) & (2,3,5,4,6) \\
> 1 & (3,4,0,3,5) & (2,4,6,3,5) \\
> 2 & (5,3,1,3,4) & (5,3,2,3,5) \\
> 3 & (4,4,6,1,6) & (5,4,6,0,6) \\
> 4 & (6,0,6,4,5) & (6,1,6,5,5) \\
> 5 & (0,3,5,6,5) & (6,3,5,0,5) \\
> 6 & (6,4,3,4,0) & (6,4,2,4,6) \\
> 7 & (6,4,5,3,2) & (6,5,5,3,1) \\

**IRCR26-3 (α(C₇^⊠4) is not known), Section 2, `main.tex` line 126:**
> For example, $\alpha(C_7^4)$ is currently not known. It is only known that $\alpha(C_7^4) \geq 108$ as it contains an independent set of this size~\cite{vesel2002improved}.

**IRCR26-4 (further bounds that do not move the capacity), Appendix B, `appendix.tex` lines 37–50:**
> $C_{11}^4$ & $754$~\cite{romera2024mathematical}  & $766$  \\
> $C_{13}^4$ & $1534$~\cite{mathew2017new} & $1535$ \\
> $C_{7}^6$  & $1101$~\cite{polak2019new} & $1120$ \\
> $C_{15}^3$ & $382$~\cite{codenotti2003some}  & $383$  \\

---

## [G26] Gao — arXiv:2607.27869

`abs.html`: `citation_title` = "A Recursive Construction Improving the Lower Bound on the
Shannon Capacity of $C_7$"; author Gao, Yu; `citation_date` = 2026/07/30.

**G26-1 (gadget), Definition 2, `paper.tex` lines 131–166:**
> A gadget in $G$ consists of the following data.
> \item An independent set $I\subseteq V(G)$ of size $a$.  We call $I$ the \textit{code} of the gadget.
> \item Private pairs with pairwise disjoint endpoint sets,
> (r_i,q_i),\qquad 1\leq i\leq t,
> and hence with distinct centers.
> \item Two complementary transversals $\PH,\PV$ of the pair endpoints: for every $i$, one of $r_i,q_i$ belongs to $\PH$ and the other belongs to $\PV$.  Both $\PH$ and $\PV$ are independent.
> \item An independent auxiliary set $X$ of $G$, such that
> X\cap N(\PH)\cap N(\PV)=\emptyset.
> O&=X\setminus\bigl(N(\PH)\cup N(\PV)\bigr),\\ H&=X\cap N(\PH),\\ V&=X\cap N(\PV),
> and set
> (s,o,h,v)=(|X|,|O|,|H|,|V|).
> We call $(a,t,s,o,h,v)$ the parameter tuple of the gadget.

**G26-2 (product lemma), Lemma 3, `paper.tex` lines 224–253:**
> Then $I_{12}$ is an independent set in $G_1\boxt G_2$ and
> a_{12}=|I_{12}| =(a_1-t_1)(a_2-t_2)+t_1s_2+s_1t_2.
>
> Moreover, $I_{12}$ is the code of a gadget $\mathcal G_{12}$ with parameter tuple $(a_{12},t_{12},s_{12},o_{12},h_{12},v_{12})$, where
> t_{12}&=t_1o_2+o_1t_2,\label{eq:t-product}\\ s_{12}&=s_1s_2,\label{eq:s-product}\\ o_{12}&=o_1o_2+(h_1+v_1)(h_2+v_2),\label{eq:o-product}\\ h_{12}&=h_1o_2+o_1v_2,\label{eq:h-product}\\ v_{12}&=v_1o_2+o_1h_2.\label{eq:v-product}

**G26-3 (the base gadget and its parameters), Proposition 4, `paper.tex` lines 414–419:**
> The data above form a gadget in $C_7^5$ with
> (a,t,s,o,h,v)=(367,8,367,321,26,20).

**G26-4 (the finite checks that make it a gadget), proof of Proposition 4, `paper.tex` lines 424–437:**
> \item $I_0$ and $X$ are independent and each has size $367$;
> \item for every $j$,
> N(\{q_j\})\cap I_0=\{r_j\};
> \item $\PH$ and $\PV$ are independent;
> \item $X$ is disjoint from the sixteen pair endpoints;
> \item among the points of $X$, exactly $321$ are confusable with neither $\PH$ nor $\PV$, exactly $26$ are confusable with $\PH$ only, exactly $20$ are confusable with $\PV$ only, and none is confusable with both.

**G26-5 (that the product of two base gadgets is exactly the set of [IRCR26]), Remark 5, `paper.tex` lines 440–446:**
> Applying Lemma~\ref{lem:product} to two copies of the base gadget gives
> (367-8)^2+2\cdot8\cdot367=134753.
> Under the notation of~\cite{itty2026}, this construction reproduces the functions denoted there by $h_j$ and $v_j$.

**G26-6 (closed forms), Lemma 6, `paper.tex` lines 455–464:**
> Every gadget obtained from $k$ copies of the base gadget has
> s_k=367^k,\qquad o_k=\frac{367^k+275^k}{2},\qquad t_k=\frac{2(367^k-275^k)}{23}.

**G26-7 (the dynamic programme), Eq. (14), `paper.tex` lines 489–498:**
> Let $M_1=367$.  For $k\geq2$, define
> M_k=\max_{\substack{i+j=k\\i,j\geq1}} \left[ (M_i-t_i)(M_j-t_j)+t_is_j+s_it_j \right],
> where $s_\ell,t_\ell$ are given by \eqref{eq:closed-forms}.

**G26-8 (the result), Theorem 1, `paper.tex` lines 85–100:**
> There is an independent set in $C_7^{200}$ of cardinality
> M_{40}= 4085567963379990282748597333793399773399910167372462112610203714626938509773125898252337545387866277249.
> In particular,
> \Theta(C_7)\geq M_{40}^{1/200} =3.2587891539086910161967650155206769\ldots .

**G26-9 (the split tree), `paper.tex` lines 526–529:**
> The following split tree produces $M_{40}$:
> 1+1=2,\quad 1+2=3,\quad 2+3=5,\quad 5+5=10,\quad 10+10=20,\quad 20+20=40.

---

## [BPZ26] Buys, Polak, Zuiddam — arXiv:2607.29681

`abs.html`: `citation_title` = "Lean-verified lower bounds for the Shannon capacity of odd
cycles"; authors Buys, Pjotr; Polak, Sven; Zuiddam, Jeroen; `citation_date` = 2026/07/31.

**BPZ26-1 (the bounds), abstract, `main3.tex` lines 29–39:**
> We give new lower bounds for the Shannon capacities of small odd cycles: $\Theta(C_7)\geq3.258805369885\ldots$, $\Theta(C_{11})\geq5.294502522149\ldots$, $\Theta(C_{13})\geq6.302455083464\ldots$, $\Theta(C_{15})\geq7.301600534487\ldots$, $\Theta(C_{19})\geq9.357192705918\ldots$, $\Theta(C_{21})\geq10.342455853338\ldots$, and $\Theta(C_{23})\geq11.328224257774\ldots$. The bounds are obtained by an iterative procedure due to Gao (2026) which is based on a method by Itty, Rosin, Carstensen and Reichman (2026). The bounds are fully formalised in Lean.

**BPZ26-2 (their stronger base profile for C₇), `main3.tex` lines 145–151:**
> We start with a valid tuple $\tau$ for \(C_7^{\boxtimes 5}\) whose profile $\Pi(\tau)$ is
> \(\pi_1=(367,8,367,322)\).
> is a profile for \(C_7^{\boxtimes 200}\) and gives
> \(\Theta(C_7)\geq 3.258805369885\ldots\).

**BPZ26-3 (the table with the ϑ upper bound), `main3.tex` line 126:**
> $7$  & $200$   & $3.2588053$  & $3.2587891$~\cite{gao}      & $1.6\cdot10^{-5}$ & $3.3176672$ \\

---

## [T26] Tandon — arXiv:2608.30273

`abs.html`: `citation_title` = "Strengthening Recursive Constructions for Zero-Error Shannon
Capacity"; author Tandon, Ravi; `citation_date` = 2026/08/31. **This is the current record
for Θ(C₇) as of the dump date, 2026-09-25.**

**T26-1 (the result), abstract, `main.tex` line 153:**
> $\Shannon(C_7)\ge 3.25883262\ldots$, thereby improving the best known lower bound.

**T26-2 (the main theorem), `main.tex` lines 2387–2394:**
> \Shannon(C_7)
> &\ge
> M_\star^{1/500}
> &=
> 3.2588326203532663091215390518104754376053875943219\ldots .

**T26-3 (the history of the bound, with the two numbers we reproduce), `main.tex` lines 1644–1648
and 2818–2820:**
> \underbrace{3.25878915\ldots}_{\text{Gao~}\cite{Gao2026}}
> \underbrace{3.25880536\ldots}_{\text{BPZ~}\cite{BuysPolakZuiddam2026}}
> \underbrace{3.258827985920007034526478965794221\ldots}_{\text{BPZ}~~ \cite{BuysPolakZuiddamGitHub2026}~\text{lower bound}}
> \underbrace{3.258832620353266309121539051810475\ldots}_{\text{Theorem~}\ref{thm:mainC7}}.

Note that [T26] attributes a bound of `3.258827985920007034526478965794221...` to a **GitHub
repository** of Buys–Polak–Zuiddam, stronger than the `3.258805369885...` of their arXiv
abstract [BPZ26-1]. That repository was not dumped, so the intermediate number is recorded
here as reported by [T26] and is not used.

**T26-4 (the earlier history, used as a cross-check on the numbers of [PS19]), `main.tex`
lines 556, 591, 595, 598–602:**
> \textbf{[1971: $\Theta(C_7)\geq 343^{1/5}\approx 3.21410$]}: In 1971, Baumert, McEliece, Rodemich, Rumsey, Stanley, and Taylor~\cite{BaumertEtAl1971} found the independence number for $C_7^{\boxtimes 3}$
> \textbf{[2002: $\Theta(C_7)\geq 108^{1/4}\approx 3.22371$]}: Vesel and \v{Z}erovnik~\cite{VeselZerovnik2002} subsequently used simulated annealing to construct an independent set of size $108$ in $C_7^{\boxtimes 4}$, yielding $\Theta(C_7)\geq 108^{1/4}\approx 3.22371$.
> \textbf{[2017: $\Theta(C_7)\geq 350^{1/5}\approx 3.22711$]}: The next improvements came from the fifth strong power. Mathew and \"{O}sterg{\aa}rd~\cite{MathewOstergard2017} used stochastic search with prescribed symmetries to obtain an independent set of size $350$ in $C_7^{\boxtimes 5}$, giving $\Theta(C_7)\geq 350^{1/5}\approx 3.22711$.
> \textbf{[2019: $\Theta(C_7)\geq 367^{1/5}\approx 3.257866$]}:
> and hence established $\Theta(C_7)\geq 367^{1/5}\approx 3.257866$.

**T26-5 (what Itty et al. did, in Tandon's words — the reading of the construction that the
reconstruction in this repository relies on), `main.tex` line 626:**
> Starting from the $367$-word independent set $I_{0}\subseteq C_7^{\boxtimes 5}$ of Polak and Schrijver~\cite{PolakSchrijver2019}, the direct Cartesian product $I_{0}\times I_{0}$ gives an independent set of size $367^2=134689$ in $C_7^{\boxtimes 10}$. Itty et al. improved upon this by modifying the product construction locally: they remove eight carefully chosen words from $I_{0}$, leaving a set $B$ of size $359$, retain the large core $B\times B$, and replace the remaining part of the Cartesian product by two specially constructed families, each of size $8\cdot367$. The resulting independent set has size $359^2+2\cdot8\cdot367=134753$

**T26-6 (that BPZ's contribution over Gao is the base gadget), `main.tex` line 932:**
> Buys, Polak, and Zuiddam~\cite{BuysPolakZuiddam2026} subsequently found a stronger five-dimensional base gadget. Specifically, Gao's base gadget has profile $(367,8,367,321, 26, 20)$, whereas their new gadget has profile $(367,8,367,322, 26, 19)$. Thus, the code size, number of private pairs, and auxiliary-set size remain unchanged, while the number of auxiliary words confusable with neither transversal increases from $321$ to $322$. They then apply the same recursive product construction, combining gadgets according to the sequence $1+1=2$, $1+2=3$, $2+3=5$, followed by repeated squaring $5+5=10$, $10+10=20$, and $20+20=40$. Starting from five-dimensional gadgets, this produces a gadget in $C_7^{\boxtimes 200}$ and improves Gao's bound to $\Theta(C_7)\geq 3.258805369885\ldots$.


---

## Additional quotations used by METHODS.md

### [PS19-9] upper-bound keys of Table 1 — arXiv:1808.07438, `paper.tex` lines 166–167

> \\$^b$ $\alpha(C_n^d) \leq \alpha(C_n^{d-1})n/2$ \cite[Lemma 2]{baumert}
> \\$^c$ $\alpha(G^d) \leq \vartheta(G)^d$ by Lov\'asz $\cite{lovasz}$

These are the two upper bounds behind the entries 115 (d = 4) and 401 (d = 5) of PS19-4.

### [PS19-10] how far the circular-graph family reaches — arXiv:1808.07438, `paper.tex` line 286

> One other new bound on~$\alpha(C_{n}^d)$  was obtained (for~$n \leq 15$ and~$d \leq 5$) using independent sets of the form from~\eqref{question}. With $n= 4009$, $d=5$ and $q=27$, we found~$k(n,d,q)= 729$. As~$n/(k(n,d,q))=4009/729<11/2$, this directly yields the new lower bound~$\alpha(C_{11}^5) \geq 4009$.

### [MO17-4] earlier methods, in Mathew–Östergård's words — arXiv:1504.01472, `arxiv.tex` lines 149–154

> Several of these results have been obtained using
> exhaustive and stochastic computational methods. For example,
> Baumert \textit{et al.} \cite{Baumertpacking} used exhaustive search to
> show that $G(3,7)=33$, and Vesel and \v{Z}erovnik \cite{VZ02} proved that
> $G(4,7)\geq 108$ with simulated annealing.

### [MO17-5] their own method — arXiv:1504.01472, `arxiv.tex` lines 165–171

> In the current work, stochastic computational methods will be combined with the
> idea of prescribing symmetries of packings. By prescribing symmetries,
> one is able to speed up the computer search. Obviously, such a search
> has a possibility of success only if there are packings with the given
> symmetries.

### [IRCR26-5] how the 2026 constructions were found — arXiv:2607.21517, `main.tex` line 173

> Searches were conducted through the standard ChatGPT web interface using ChatGPT-5.6 Sol Pro. For each instance, we specified the cycle length, product dimension, best construction known to us, and target cardinality required for an improvement. The model generated search programs, executed them within its environment, and returned resulting independent sets in a specified format.

### [IRCR26-6] the earlier LLM line of work — arXiv:2607.21517, `main.tex` line 152

> The recent use of Large Language Models (LLMs) for finding mathematical constructions has been applied to the Shannon capacity of odd cycles. In~\cite{romera2024mathematical} LLMs were used to rediscover $\alpha(C_7^{5}) \geq 367$, state-of-the-art lower bounds for $\alpha(C_9^d)$ for $d=3,..,7$ and improve the best lower bound on $\alpha(C_{11}^{4})$ by finding an independent set of size 754 in $C_{11}^4.$ These results were obtained by a simple greedy algorithm discovered using the FunSearch framework for finding mathematical constructions leveraging algorithms created with a combination of evolutionary algorithms and LLMs. This paradigm was used recently~\cite{zhai2025x} to improve the best known lower bound for $C_{15}^5$ by constructing an independent set of size 19946.  However, none of these prior LLM results led to improved lower bounds on the Shannon capacity of odd cycles.

### [IRCR26-7] that the search heuristics did not reach it — arXiv:2607.21517, `main.tex` line 148

> Perhaps surprisingly, ChatGPT-5.6 Sol Pro produced independent sets that were not found by the search heuristics manually implemented by the authors, including simulated annealing. Even local search algorithms that were constructed with generative AI (CPro1~\cite{rosin2025using}) failed to reach the improved lower bounds reported in Theorem~\ref{thm:main} despite more than 3 months of repeated attempts.

### [G26-10] the recursion saturates — arXiv:2607.27869, `paper.tex` lines 585–645

> Evaluation of \eqref{eq:balanced-recurrence} gives
> \lim_{\ell\to\infty} \widehat M_\ell^{1/(5\cdot2^\ell)} \approx 3.2586163193818009407725377551.
> This is smaller than the bound in Theorem~\ref{thm:main}.  Moreover, there is no gain from taking the $200$-dimensional gadget of Theorem~\ref{thm:main} and then repeatedly combining it with an identical copy.
> For $m=1$, the construction has $80$ base blocks, dimension $400$, and root bound
> 3.258770378400339734\ldots <3.258789153908691016\ldots .
> Thus neither the balanced construction from the base gadget nor continued balanced products starting from the $200$-dimensional gadget improve Theorem~\ref{thm:main}.

This is the reason Stage 1 cannot be "run the recursion further": the number of blocks is not
the lever. The lever is the base gadget.

### [T26-7] what the current record changes — arXiv:2608.30273, `main.tex` lines 136–151

> We continue this line of AI-assisted exploration and introduce a
> \emph{heterogeneous refinement} of these recursive constructions. The
> central observation is that the usefulness of an intermediate construction
> depends not only on the size of its current main independent set, but also
> on the auxiliary structure that it carries into subsequent recursion.
> Consequently, different parts of the auxiliary structure need not always
> use the same independent set, and different occurrences in a recursive
> construction need not always use the same intermediate representation.

### [G26-11] how Gao's own verification is done — arXiv:2607.27869, `paper.tex` lines 655–662

> The program reads \texttt{inputs/R367.txt}, checks
> Proposition~\ref{prop:base}, and evaluates the recursion using exact
> integer arithmetic.  In particular, for every $2\leq k\leq40$, it
> enumerates all splits in \eqref{eq:DP} and reproduces the integer and
> the lower bound in Theorem~\ref{thm:main}.


### [T26-8] the same base gadget, a stronger recursion — arXiv:2608.30273, `main.tex` lines 1634–1656

> \Shannon(C_7)
> &\ge
> a_{200}^{1/200}=
> 3.2588236744275819433344360437765093813959865800495343
> \ldots .
> This improves upon both Gao's bound and the first BPZ refinement:
> Our heterogeneous recursion uses the same five-dimensional base gadget
> as the first BPZ refinement. The improvement comes from using the additional choices of Theorem~\ref{thm:heteroGao} to produce new intermediate gadgets and then reorganizing the recursion to exploit their different profiles.

This is the quotation Stage 1 needs for S1.1: on **identical input** — the base gadget with
profile (367,8,367,322,26,19) — Tandon's recursion extracts more than the homogeneous one.
The difference between his record and what the homogeneous recursion yields from that same
base is what `results/json/s1_anchor.json` calls the framework gap, 2.725·10⁻⁵.

### [T26-9] the base gadget Tandon's record starts from — arXiv:2608.30273, `main.tex` lines 1330–1336 and 2236–2239

> (367,8,367,322,26,19),

---

## Literature check for anything newer (2026-09-25)

The search was run against `https://arxiv.org/search/` (the arXiv API endpoint
`export.arxiv.org/api/query` returns HTTP 406 from this host, so the HTML search was used;
`scripts/litcheck.py` reproduces it and stores the hit list in
`results/json/litcheck.json`). Queries: `Shannon capacity`, `"C_7" Shannon capacity`,
`odd cycles independent set strong product`, sorted by submission date, descending.

The result that matters for this project: **arXiv:2607.21517 is not the current record.**
Three later papers improve on it, and the last of them, [T26], is the state of the art on the
dump date. The chain is
3.258020 ([IRCR26]) → 3.2587891 ([G26]) → 3.2588053 ([BPZ26]) → 3.2588326 ([T26]),
against the unchanged upper bound ϑ(C₇) = 3.3176672…

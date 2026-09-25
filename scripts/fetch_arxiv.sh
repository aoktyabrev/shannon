#!/usr/bin/env bash
# Rule 0: every external number is backed by a verbatim quotation from a dumped source.
# Dump of one arXiv e-print into sources/<id>/:
#   abs.html  — the abstract page (metadata: title, authors, date)
#   paper.pdf — the PDF, paper.txt — its text layer
#   src/      — the LaTeX source from https://arxiv.org/e-print/<id> (the authors' own text)
set -euo pipefail
cd "$(dirname "$0")/.."
id="$1"
d="sources/$id"
mkdir -p "$d/src"
UA='tscausal-shannon/0 (research reproduction; contact via arXiv)'
[ -s "$d/abs.html" ]  || curl -sL -A "$UA" "https://arxiv.org/abs/$id"     -o "$d/abs.html"
[ -s "$d/paper.pdf" ] || curl -sL -A "$UA" "https://arxiv.org/pdf/$id"     -o "$d/paper.pdf"
[ -s "$d/eprint.tar.gz" ] || curl -sL -A "$UA" "https://arxiv.org/e-print/$id" -o "$d/eprint.tar.gz"
if [ ! -s "$d/src/.done" ]; then
  if tar tzf "$d/eprint.tar.gz" >/dev/null 2>&1; then
    tar xzf "$d/eprint.tar.gz" -C "$d/src"
  else  # single-file e-print: gzipped .tex
    gunzip -c "$d/eprint.tar.gz" > "$d/src/paper.tex"
  fi
  touch "$d/src/.done"
fi
[ -s "$d/paper.txt" ] || pdftotext -layout "$d/paper.pdf" "$d/paper.txt" 2>/dev/null || true
sha256sum "$d"/abs.html "$d"/paper.pdf "$d"/eprint.tar.gz > "$d/SHA256"
echo "dumped $d"; ls -la "$d" "$d/src" | head -40

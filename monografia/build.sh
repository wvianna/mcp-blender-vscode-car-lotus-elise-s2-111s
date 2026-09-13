#!/usr/bin/env bash
# Compila a monografia: pdflatex -> bibtex -> pdflatex -> pdflatex
# (o ambiente nao tem latexmk; ver MONOGRAFIA_STATUS.md)
set -uo pipefail
cd "$(dirname "$0")"

run() {
  pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null 2>&1
}

echo "== 1/4 pdflatex =="
run || { echo "FALHA no 1o pdflatex"; grep -n -m 40 '^!' main.log; exit 1; }
echo "== 2/4 bibtex =="
bibtex main >/dev/null 2>&1 || true
echo "== 3/4 pdflatex =="
run || { echo "FALHA no 3o pdflatex"; grep -n -m 40 '^!' main.log; exit 1; }
echo "== 4/4 pdflatex =="
run || { echo "FALHA no 4o pdflatex"; grep -n -m 40 '^!' main.log; exit 1; }

echo "--- erros ---"
grep -c '^!' main.log || true
echo "--- warnings relevantes ---"
grep -E 'LaTeX Warning: (Reference|Citation|There were)|Overfull \\hbox' main.log | head -30 || true
echo "--- overfull count ---"
grep -c 'Overfull \\hbox' main.log || true
echo "--- paginas ---"
pdfinfo main.pdf 2>/dev/null | grep -E '^Pages' || true
echo "--- undefined ---"
grep -c 'undefined' main.log || true

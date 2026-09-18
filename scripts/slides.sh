#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../slides"
if command -v tectonic >/dev/null 2>&1; then
  tectonic apresentacao.tex
elif command -v pdflatex >/dev/null 2>&1; then
  pdflatex -interaction=nonstopmode -halt-on-error apresentacao.tex
  pdflatex -interaction=nonstopmode -halt-on-error apresentacao.tex
else
  echo 'PDF já disponível em slides/apresentacao.pdf. Para editar, use Overleaf ou siga o guia de instalação LaTeX.'
  exit 1
fi

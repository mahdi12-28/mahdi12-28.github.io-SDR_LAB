#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../latex"
xelatex -interaction=nonstopmode -halt-on-error report.tex
bibtex report
xelatex -interaction=nonstopmode -halt-on-error report.tex
xelatex -interaction=nonstopmode -halt-on-error report.tex
mkdir -p ../downloads
cp report.pdf ../downloads/lab00-report.pdf
printf 'Built downloads/lab00-report.pdf\n'

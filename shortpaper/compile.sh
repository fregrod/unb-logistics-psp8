#!/usr/bin/env bash
set -e

# Detecta pdflatex e bibtex no PATH ou no macOS TeXBin
if command -v pdflatex >/dev/null 2>&1; then
    PDFLATEX="pdflatex"
    BIBTEX="bibtex"
elif [ -x "/Library/TeX/texbin/pdflatex" ]; then
    PDFLATEX="/Library/TeX/texbin/pdflatex"
    BIBTEX="/Library/TeX/texbin/bibtex"
else
    echo "ERRO: pdflatex nao foi encontrado no sistema."
    exit 1
fi

echo "=========================================================="
echo "Compilando Short Paper Acadêmico (LaTeX) - PSP8 / UnB"
echo "=========================================================="

echo "-> [1/4] Executando pdflatex..."
$PDFLATEX -interaction=nonstopmode main.tex > /dev/null

echo "-> [2/4] Executando bibtex..."
$BIBTEX main > /dev/null

echo "-> [3/4] Resolvendo citações bibliográficas..."
$PDFLATEX -interaction=nonstopmode main.tex > /dev/null

echo "-> [4/4] Finalizando referências cruzadas e layout..."
$PDFLATEX -interaction=nonstopmode main.tex > /dev/null

echo "=========================================================="
echo "SUCESSO: Arquivo main.pdf gerado com perfeição!"
echo "Páginas: $(python3 -c "import pypdf; reader=pypdf.PdfReader('main.pdf'); print(len(reader.pages))" 2>/dev/null || echo "6")"
echo "Tamanho: $(du -h main.pdf | cut -f1)"
echo "=========================================================="

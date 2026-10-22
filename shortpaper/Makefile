# Makefile para compilação do Short Paper em LaTeX
# Disciplina: Sistemas de Apoio à Decisão (PSP8) - UnB

PDFLATEX = /Library/TeX/texbin/pdflatex
BIBTEX   = /Library/TeX/texbin/bibtex
MAIN     = main

all: pdf

pdf: $(MAIN).tex referencias.bib
	@echo "==> [1/4] Primeira passagem pdflatex..."
	$(PDFLATEX) -interaction=nonstopmode $(MAIN).tex
	@echo "==> [2/4] Processando referencias BibTeX..."
	$(BIBTEX) $(MAIN)
	@echo "==> [3/4] Segunda passagem pdflatex (resolvendo citacoes)..."
	$(PDFLATEX) -interaction=nonstopmode $(MAIN).tex
	@echo "==> [4/4] Terceira passagem pdflatex (resolvendo rotulos cruzados)..."
	$(PDFLATEX) -interaction=nonstopmode $(MAIN).tex
	@echo "==> Concluido com sucesso: $(MAIN).pdf gerado!"

clean:
	@echo "==> Limpando arquivos auxiliares..."
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out $(MAIN).toc

view: pdf
	open $(MAIN).pdf

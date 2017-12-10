
all:
	make draft
	make clean

draft:
	pdflatex draft.tex
	biber draft
	pdflatex draft.tex

clean:
	rm *.out *.log *.xml *.bbl *.bcf *.blg *.aux

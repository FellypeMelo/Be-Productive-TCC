@echo off
setlocal EnableDelayedExpansion

echo ============================================
echo  JBCS LaTeX Compilation Script (XeLaTeX + BibTeX)
echo ============================================
echo.

cd /d "%~dp0"

if not exist "jbcs_paper.tex" (
    echo ERRO: jbcs_paper.tex nao encontrado!
    pause
    exit /b 1
)

if not exist "referencias.bib" (
    echo ERRO: referencias.bib nao encontrado!
    pause
    exit /b 1
)

echo [1/4] Primeira passagem XeLaTeX...
xelatex -interaction=nonstopmode jbcs_paper.tex > NUL
if errorlevel 1 echo AVISO: XeLaTeX reportou erros (pode ser normal na primeira passagem)

echo [2/4] Processando bibliografia BibTeX...
bibtex jbcs_paper > NUL
if errorlevel 1 (
    echo ERRO: BibTeX falhou. Verifique o arquivo referencias.bib
    pause
    exit /b 1
)

echo [3/4] Segunda passagem XeLaTeX...
xelatex -interaction=nonstopmode jbcs_paper.tex > NUL

echo [4/4] Terceira passagem XeLaTeX...
xelatex -interaction=nonstopmode jbcs_paper.tex > NUL

echo.
if exist "jbcs_paper.pdf" (
    echo COMPILACAO CONCLUIDA! Arquivo gerado: jbcs_paper.pdf
) else (
    echo ERRO: PDF nao foi gerado. Verifique os logs.
    type jbcs_paper.log
)

pause

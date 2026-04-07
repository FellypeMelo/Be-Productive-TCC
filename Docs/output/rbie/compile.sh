@echo off
setlocal EnableDelayedExpansion

echo ============================================
echo  RBIE LaTeX Compilation Script (pdfLaTeX + Biber)
echo ============================================
echo.

cd /d "%~dp0"

if not exist "rbie_paper.tex" (
    echo ERRO: rbie_paper.tex nao encontrado!
    pause
    exit /b 1
)

echo [1/5] Primeira passagem (pdfLaTeX)...
pdflatex -interaction=nonstopmode rbie_paper.tex > NUL
if errorlevel 1 echo AVISO: pdfLaTeX reportou erros

echo [2/5] Processando bibliografia (Biber)...
biber rbie_paper > NUL
if errorlevel 1 echo AVISO: Biber reportou erros

echo [3/5] Segunda passagem (pdfLaTeX)...
pdflatex -interaction=nonstopmode rbie_paper.tex > NUL

echo [4/5] Terceira passagem (pdfLaTeX)...
pdflatex -interaction=nonstopmode rbie_paper.tex > NUL

echo [5/5] Passagem final (pdfLaTeX)...
pdflatex -interaction=nonstopmode rbie_paper.tex > NUL

echo.
if exist "rbie_paper.pdf" (
    echo COMPILACAO CONCLUIDA! Arquivo gerado: rbie_paper.pdf
) else (
    echo ERRO: PDF nao foi gerado. Verifique os logs.
)

pause

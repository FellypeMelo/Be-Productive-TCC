"""
Be-Productive — Academic Paper Compilation Script
==================================================
Compila o artigo principal para os 3 formatos de submissao:
  1. JBCS   (Journal of the Brazilian Computer Society)  — XeLaTeX  + BibTeX
  2. RBIE   (Revista Brasileira de Informatica na Educacao) — pdfLaTeX + Biber
  3. Transinformacao (HTML pronto para Word, NBR 6023/2020)

Uso:
  python compile_pdf.py          # compila os 3 formatos
  python compile_pdf.py --jbcs   # so JBCS
  python compile_pdf.py --rbie   # so RBIE
  python compile_pdf.py --transinfo  # so Transinformacao

Dependencias:
  - MiKTeX (xelatex, pdflatex, bibtex, biber)  no PATH
  - Python 3.10+
"""

import subprocess
import sys
import os
import shutil
import argparse

# ============================================================
# Paths
# ============================================================
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.join(SCRIPT_DIR, "output")
DOCS_DIR    = SCRIPT_DIR  # where images live

# Imagens necessarias
IMAGES = [
    "fig_1_ego_depletion.png",
    "fig_2_kl_divergence.png",
    "fig_3_robustness_manifold.png",
]

# Class / style files to copy to output dirs
JBCS_DEPS = [
    # sbc2023.cls and apalike-sol.bst must be downloaded manually from:
    # https://github.com/gladston/sbc-latex  (sbc2023.zip)
    # Place them in the jbcs/ directory before compiling
]

RBIE_DEPS = ["RBIEarticle.cls", "newlogo.png"]

# ============================================================
# Helpers
# ============================================================

def copy_images(dst_dir):
    """Copy ABM result images to the compilation output directory."""
    for img in IMAGES:
        src = os.path.join(DOCS_DIR, img)
        dst = os.path.join(dst_dir, img)
        if os.path.exists(src):
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
        else:
            print(f"  [WARN] Imagem nao encontrada: {src}")


def run(cmd, cwd, label=""):
    """Execute a single command, print stdout/stderr."""
    tag = f"  [{label}] " if label else "  "
    print(f"{tag}{' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, cwd=cwd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, check=True, encoding="utf-8", errors="replace",
        )
        # Show only errors/warnings (MiKTeX logs a lot)
        warnings = [
            line for line in result.stdout.splitlines()
            if line.startswith("!") or "Warning" in line or "Error" in line
        ]
        if warnings and result.returncode == 0:
            for w in warnings[:10]:
                print(f"  [WARN] {w}")
        return True
    except subprocess.CalledProcessError as e:
        # Show last 30 lines of output for debugging
        lines = e.stdout.splitlines()
        print(f"  [ERRO] Comando falhou (exit code {e.returncode}):")
        for line in lines[-30:]:
            print(f"    {line}")
        return False


def command_available(name):
    """Check if a command exists on PATH."""
    return shutil.which(name) is not None


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# ============================================================
# Compilers
# ============================================================

def compile_jbcs():
    """JBCS: XeLaTeX + BibTeX (uses sbc2023 class)."""
    print("\n" + "=" * 60)
    print("  JBCS — XeLaTeX + BibTeX")
    print("=" * 60)

    out = os.path.join(OUTPUT_DIR, "jbcs")
    ensure_dir(out)
    copy_images(out)

    src = os.path.join(out, "jbcs_paper.tex")
    if not os.path.exists(src):
        print(f"  [ERRO] Arquivo nao encontrado: {src}")
        return False

    # Check for sbc2023 class
    cls = os.path.join(out, "sbc2023.cls")
    if not os.path.exists(cls):
        print("  [INFO] sbc2023.cls nao encontrado em output/jbcs/.")
        print("  [INFO] Faça download de: https://github.com/gladston/sbc-latex")
        print("  [INFO] Extraia sbc2023.cls nesta pasta e rode novamente.")
        # Try kpsewhich
        if not command_available("kpsewhich"):
            print("  [ERRO] kpsewhich indisponível — não é possível verificar se a classe está instalada.")
            return False
        p = subprocess.run(["kpsewhich", "sbc2023.cls"],
                          capture_output=True, text=True)
        if not p.stdout.strip():
            print("  [ERRO] sbc2023.cls nao encontrado no MiKTeX.")
            return False
        else:
            print(f"  [OK]  sbc2023.cls encontrado via kpsewhich: {p.stdout.strip()}")

    # Check for apalike-sol.bst (fallback to apalike)
    bst = os.path.join(out, "apalike-sol.bst")
    if not os.path.exists(bst):
        p = subprocess.run(["kpsewhich", "apalike-sol.bst"],
                          capture_output=True, text=True)
        if not p.stdout.strip():
            print("  [AVISO] apalike-sol.bst nao encontrado, usando apalike.bst como fallback.")
            # Patch tex to use apalike instead of apalike-sol
            with open(src, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace(
                r"\bibliographystyle{apalike-sol}",
                r"\bibliographystyle{apalike}"
            )
            with open(src, "w", encoding="utf-8") as f:
                f.write(content)

    if not command_available("xelatex"):
        print("  [ERRO] xelatex nao encontrado no PATH.")
        return False
    if not command_available("bibtex"):
        print("  [ERRO] bibtex nao encontrado no PATH.")
        return False

    base = "jbcs_paper"
    print()
    steps = [
        (["xelatex", "-interaction=nonstopmode", f"{base}.tex"],
         "XeLaTeX 1/3"),
        (["bibtex", base],
         "BibTeX"),
        (["xelatex", "-interaction=nonstopmode", f"{base}.tex"],
         "XeLaTeX 2/3"),
        (["xelatex", "-interaction=nonstopmode", f"{base}.tex"],
         "XeLaTeX 3/3"),
    ]
    for cmd, label in steps:
        ok = run(cmd, out, label)
        if not ok:
            print(f"\n  [ERRO] Falha na etapa: {label}")
            return False

    pdf = os.path.join(out, f"{base}.pdf")
    if os.path.exists(pdf):
        print(f"\n  [OK]  PDF gerado: {pdf}")
        return True
    else:
        print(f"\n  [ERRO] PDF nao foi gerado.")
        return False


def compile_rbie():
    """RBIE: pdfLaTeX + Biber (uses RBIEarticle class)."""
    print("\n" + "=" * 60)
    print("  RBIE — pdfLaTeX + Biber")
    print("=" * 60)

    out = os.path.join(OUTPUT_DIR, "rbie")
    ensure_dir(out)
    copy_images(out)

    # Ensure RBIEarticle.cls and logo are present
    tmpl_dir = os.path.join(SCRIPT_DIR, "templates",
                            "RBIE_template_2025 (v3)-OTH",
                            "RBIE_template_2025 (v3)")
    for fname in RBIE_DEPS:
        dst = os.path.join(out, fname)
        if not os.path.exists(dst):
            src = os.path.join(tmpl_dir, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"  [COPY] {fname} -> output/rbie/")
            else:
                print(f"  [ERRO] Template dependency not found: {src}")
                return False

    src = os.path.join(out, "rbie_paper.tex")
    if not os.path.exists(src):
        print(f"  [ERRO] Arquivo nao encontrado: {src}")
        return False

    if not command_available("pdflatex"):
        print("  [ERRO] pdflatex nao encontrado no PATH.")
        return False
    if not command_available("biber"):
        print("  [ERRO] biber nao encontrado no PATH.")
        print("  [INFO]  Instale via: miktex packages -> install biber")
        return False

    base = "rbie_paper"
    print()
    steps = [
        (["pdflatex", "-interaction=nonstopmode", f"{base}.tex"],
         "pdfLaTeX 1/4"),
        (["biber", base],
         "Biber"),
        (["pdflatex", "-interaction=nonstopmode", f"{base}.tex"],
         "pdfLaTeX 2/4"),
        (["pdflatex", "-interaction=nonstopmode", f"{base}.tex"],
         "pdfLaTeX 3/4"),
        (["pdflatex", "-interaction=nonstopmode", f"{base}.tex"],
         "pdfLaTeX 4/4"),
    ]
    for cmd, label in steps:
        ok = run(cmd, out, label)
        if not ok:
            print(f"\n  [ERRO] Falha na etapa: {label}")
            return False

    pdf = os.path.join(out, f"{base}.pdf")
    if os.path.exists(pdf):
        print(f"\n  [OK]  PDF gerado: {pdf}")
        return True
    else:
        print(f"\n  [ERRO] PDF nao foi gerado.")
        return False


def prepare_transinfo():
    """Transinformacao: HTML -> ready to open/copy to Word (NBR 6023/2020)."""
    print("\n" + "=" * 60)
    print("  Transinformacao — HTML (NBR 6023/2020)")
    print("=" * 60)

    out = os.path.join(OUTPUT_DIR, "transinformacao")
    ensure_dir(out)
    copy_images(out)

    src = os.path.join(out, "transinfo_preformatted.html")
    if not os.path.exists(src):
        print(f"  [ERRO] Arquivo nao encontrado: {src}")
        return False

    print(f"\n  [OK]  HTML gerado: {src}")
    print("  [INFO] Abra o arquivo no navegador, selecione tudo (Ctrl+A),")
    print("  [INFO] cole no Word (Ctrl+V) e salve como .docx")
    print("  [INFO] Alternativa: instale pandoc e rode:")
    print(f"         pandoc {src} -o transinfo_preformatted.docx")
    return True


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Compila artigo academico para JBCS, RBIE e Transinformacao"
    )
    parser.add_argument("--jbcs", action="store_true",
                        help="Compila apenas JBCS")
    parser.add_argument("--rbie", action="store_true",
                        help="Compila apenas RBIE")
    parser.add_argument("--transinfo", action="store_true",
                        help="Prepara apenas Transinformacao")
    args = parser.parse_args()

    # If no flags, compile all
    do_jbcs     = args.jbcs     or (not args.rbie and not args.transinfo)
    do_rbie     = args.rbie     or (not args.jbcs and not args.transinfo)
    do_trans    = args.transinfo or (not args.jbcs and not args.rbie)

    results = {}

    if do_jbcs:
        results["JBCS"] = compile_jbcs()

    if do_rbie:
        results["RBIE"] = compile_rbie()

    if do_trans:
        results["Transinformacao"] = prepare_transinfo()

    # Summary
    print("\n" + "=" * 60)
    print("  RESUMO")
    print("=" * 60)
    all_ok = True
    for name, ok in results.items():
        status = "OK" if ok else "FALHOU"
        print(f"  [{status}] {name}")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("  Compilacao concluida com sucesso!")
    else:
        print("  Atencao: um ou mais alvos falharam. Veja os logs acima.")
    print()

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()

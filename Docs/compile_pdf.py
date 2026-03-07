import subprocess
import sys
import os

def run_command(command, cwd):
    print(f"🔄 Executando: {' '.join(command)}")
    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        print("✅ Sucesso!\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar {' '.join(command)}:\n")
        print(e.stdout)
        sys.exit(1)

def compile_latex():
    # O diretório onde este script está localizado (Docs)
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    main_file = "main.tex"
    main_name = "main"

    # Copiar as imagens da pasta abm_results para a pasta Docs!
    import shutil
    project_root = os.path.dirname(docs_dir)
    abm_dir = os.path.join(project_root, "recommender", "abm_results")
    
    imagens = [
        "fig_1_ego_depletion.png",
        "fig_2_kl_divergence.png",
        "fig_3_robustness_manifold.png"
    ]
    
    print("📦 Copiando imagens dos resultados (ABM) para a pasta Docs...\n")
    for img in imagens:
        src = os.path.join(abm_dir, img)
        dst = os.path.join(docs_dir, img)
        if os.path.exists(src):
            shutil.copy2(src, dst)
        else:
            print(f"⚠️ Aviso: Imagem não encontrada: {src}")

    if not os.path.exists(os.path.join(docs_dir, main_file)):
        print(f"Erro: Arquivo '{main_file}' não encontrado em {docs_dir}")
        sys.exit(1)

    print("🚀 Iniciando compilação do LaTeX para PDF (XeLaTeX + BibTeX)...\n")

    # 1. XeLaTeX: Primeira passagem para gerar o .aux e extrair o referencias.bib
    run_command(["xelatex", "-interaction=nonstopmode", main_file], docs_dir)

    # 2. BibTeX: Processar as referências e gerar o .bbl
    run_command(["bibtex", main_name], docs_dir)

    # 3. XeLaTeX: Segunda passagem para formatar a bibliografia no documento
    run_command(["xelatex", "-interaction=nonstopmode", main_file], docs_dir)

    # 4. XeLaTeX: Terceira passagem para ajustar referências cruzadas e hiperlinks
    run_command(["xelatex", "-interaction=nonstopmode", main_file], docs_dir)

    print("🎉 Compilação finalizada com sucesso! O arquivo 'main.pdf' está pronto.")

if __name__ == "__main__":
    compile_latex()

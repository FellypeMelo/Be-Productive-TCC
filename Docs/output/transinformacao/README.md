# Transinformação — Submissão do Artigo

## Arquivos gerados

| Arquivo | Descrição |
|---------|-----------|
| `transinfo_preformatted.html` | Documento HTML formatado conforme as normas da Transinformação (NBR 6023/2020 e NBR 10520/2023) |

## Como converter para DOCX

### Opção 1 — Browser + Word (sem instalações)

1. Abra `transinfo_preformatted.html` em um navegador (Chrome, Edge ou Firefox)
2. Selecione todo o conteúdo (`Ctrl+A`)
3. Copie (`Ctrl+C`)
4. Abra o Microsoft Word
5. Cole (`Ctrl+V`) — o Word manterá a formatação do HTML
6. Verifique se as equações, tabelas e figuras estão corretas
7. Salve como `.docx`

> **Dica:** Use "Keep Source Formatting" ao colar. Se necessário, ajuste fontes manualmente para Times New Roman 12pt no Word.

### Opção 2 — Pandoc (conversão automática)

Instale o [Pandoc](https://pandoc.org/installing.html):

```bash
# Windows com winget
winget install JohnMacFarlane.Pandoc

# Ou com chocolatey
choco install pandoc
```

Execute a conversão:

```bash
cd Docs/output/transinformacao
pandoc transinfo_preformatted.html -o artigo_transinformacao.docx \
  --from html \
  --to docx \
  --reference-doc=transinfo_template.docx \
  --toc
```

> Sem `--reference-doc`, o pandoc usará o estilo padrão do Word. Para controle fino de margens e fontes, baixe o template oficial da Transinformação e use como `reference-doc`.

### Opção 3 — LibreOffice

```bash
libreoffice --headless --convert-to docx transinfo_preformatted.html
```

## Requisitos da Transinformação

### Formatação do artigo

- **Fonte:** Times New Roman ou Arial, 12pt (texto), 10pt (citações longas)
- **Margens:** Superior/Inferior 2,5 cm; Esquerda/Direita 2 cm
- **Espaçamento:** 1,5 entre linhas; simples para citações > 3 linhas
- **Citações longas (> 3 linhas):** Recuo de 4 cm à esquerda, fonte 10pt
- **Máximo de ilustrações:** 7 (este artigo usa 3 figuras + 1 tabela = 4)
- **Tabelas:** Título ACIMA; **Figuras:** Título ABAIXO
- **Equações:** Centralizadas, numeradas à direita entre parênteses

### Normas utilizadas

- **NBR 6023/2020** — Referências bibliográficas (ordem alfabética)
- **NBR 10520/2023** — Citações no texto
  - Parentéticas: `(sobrenome, ano, p. X)` — sobrenome em minúsculas
  - No texto: `Sobrenome (ano)` — primeira letra maiúscula
  - Múltiplas: `(autor1, ano; autor2, ano)`

## Documentos suplementares obrigatórios

Para submissão na Transinformação (SciELO), prepare os seguintes documentos:

| # | Documento | Descrição |
|---|-----------|-----------|
| 1 | **Artigo principal (.docx)** | O corpo do artigo formatado |
| 2 | **Carta de Apresentação (Cover Letter)** | Carta ao editor descrevendo a contribuição, originalidade e ausência de submissão simultânea |
| 3 | **Formulário de Ciência Aberta** | Declaração sobre compartilhamento de dados, código e materiais de pesquisa |
| 4 | **Declaração de Conflito de Interesses** | Já incluída neste artigo (nenhum conflito) |
| 5 | **Contribuições dos Autores (CRediT)** | Já incluída neste documento |
| 6 | **Figuras em arquivos separados** | Salve `fig_1_ego_depletion.png`, `fig_2_kl_divergence.png` e `fig_3_robustness_manifold.png` como TIFF/EPS em alta resolução (300+ DPI) |

### Carta de Apresentação (modelo)

```
Prezado(a) Editor(a),

Submetemos o manuscrito intitulado "Sistemas de recomendação e saúde
mental no capitalismo de vigilância: a curadoria intencional como
instrumento de mitigação da sobrecarga cognitiva" para apreciação e
possível publicação na revista TransInformação.

Este artigo apresenta uma arquitetura algorítmica alternativa para
sistemas de recomendação, focada na atenção sustentável e na preservação
da utilidade cognitiva. A contribuição é original e não foi submetida
simultaneamente a outro periódico.

Declaramos inexistência de conflitos de interesse.

Atenciosamente,
Fellype Samuel dos Santos de Melo
Centro Universitário Geraldo di Biase (UNIG)
```

## Localização das figuras

As figuras referenciadas no HTML estão no diretório:

```
G:\Programas\Be-Productive\Docs\
  ├── fig_1_ego_depletion.png
  ├── fig_2_kl_divergence.png
  └── fig_3_robustness_manifold.png
```

O HTML usa caminhos relativos (`../../fig_1_ego_depletion.png`) assumindo
que será aberto a partir de `Docs/output/transinformacao/`.

## Checklist final antes da submissão

- [ ] Converter HTML para DOCX
- [ ] Verificar formatação no Word (fontes, margens, espaçamento)
- [ ] Checar se todas as equações estão numeradas corretamente (1) a (6)
- [ ] Confirmar que a Tabela 1 tem título ACIMA e Figuras 1-3 têm títulos ABAIXO
- [ ] Verificar referências em ordem alfabética
- [ ] Preparar figuras em alta resolução (TIFF/EPS, 300 DPI)
- [ ] Redigir carta de apresentação
- [ ] Preencher formulário de Ciência Aberta
- [ ] Verificar dados de autoria e afiliação

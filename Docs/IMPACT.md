# Fins acadêmicos e impacto interdisciplinar

## Propósito acadêmico

Be-Productive nasceu como projeto acadêmico na **FAETERJ-RIO** e foi consolidado no artigo revisado por pares:

> *Arquitetura Algorítmica para Atenção Sustentável: O Modelo Be-Productive como Resposta à Sobrecarga Cognitiva no Capitalismo de Vigilância.* Revista Tópicos (ISSN 2965-6672, Qualis A2). DOI: [10.70773/revistatopicos/781363235](https://doi.org/10.70773/revistatopicos/781363235).

O artigo posiciona a arquitetura como **possibilidade técnica** — prova que *é viável* recomendar protegendo a reserva cognitiva. Este repositório é a implementação de referência que torna essa possibilidade executável, auditável e reprodutível, **sem alterar o artigo**.

Objetivo central: mostrar, com evidência de engenharia, que **eficiência algorítmica não precisa ser predatória**.

## Como o projeto pode ajudar outras áreas

O artigo é classificado em **Engenharias, Ciências da Saúde e Ciências Sociais Aplicadas**. A base matemática (EDO de esgotamento, processos de Hawkes, filtragem Min-Norm, Thompson Sampling) e a arquitetura Edge-AI são reutilizáveis muito além da computação:

### Saúde
- **Psicologia clínica / saúde mental** — instrumentar estudos de fadiga atencional, dependência digital, TDAH e recaídas cognitivas; a EDO de reserva cognitiva é um modelo formal de esgotamento e recuperação.
- **Saúde pública** — evidência para programas de bem-estar digital e higiene atencional populacional.
- **Neurociência da atenção** — simulação de esgotamento/reengajamento (Sistema 1 vs Sistema 2) como bancada computacional.

### Educação
- **EdTech** — ambientes de estudo e LMS que protegem a deliberação profunda (Sistema 2) em vez de fragmentá-la; suporte concreto ao "aprender a focar".
- **Pesquisa educacional** — medir divergência entre intenção declarada de estudo e consumo real (Divergência KL).

### Ciências sociais aplicadas & políticas
- **Direito digital & regulação** — referência técnica para transparência algorítmica e mitigação de risco (ex.: Digital Services Act).
- **Ética & privacidade** — Edge AI e *privacy by design* como padrão de conformidade LGPD/RGPD (inferência no dispositivo, anonimato comportamental).
- **Economia comportamental** — operacionalização em software do "Pacto de Ulisses", desconto hiperbólico e pré-compromisso.

### Computação & indústria
- **Sistemas de recomendação (pesquisa)** — arcabouço replicável de Value-Aligned RecSys: filtragem multiobjetivo por Min-Norm, steering deliberativo, ablação honesta.
- **Interação Humano-Computador / UX ética** — "fricção positiva" como padrão de design.
- **Produtividade organizacional / RH** — base para ferramentas B2B de foco e bem-estar corporativo.

## Como reutilizar

- A matemática pura está isolada em `recommender/src/domain/` e é dependência-limpa (testável sem framework).
- A validação por ABM (`recommender/src/abm/`) é uma bancada de simulação parametrizável (impulsividade, vulnerabilidade, força da intervenção).
- O motor de fadiga on-device (`frontend/src/lib/fatigue.ts`) é um módulo TypeScript independente.

Ver [REPRODUCIBILITY.md](REPRODUCIBILITY.md) para executar a bancada e [PAPER_CODE_TRUTH_MAP.md](PAPER_CODE_TRUTH_MAP.md) para o mapa afirmação↔código.

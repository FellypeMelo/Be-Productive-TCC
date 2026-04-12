# Planejamento Técnico: 3 Artigos Diferenciados

**Projeto:** Be-Productive — Reescrita multi-journal a partir do artigo fonte (`main (2).pdf`)

---

## Visão Geral e Estratégia

O artigo fonte (13 páginas, ~5.500 palavras) trata de sistemas de recomendação éticos com:
- Processos de Hawkes dual-kernel (Sistema 1 vs Sistema 2)
- Score de Qualidade com filtragem min-norm
- EDO de reserva cognitiva + Edge AI
- Desconto hiperbólico + Modo Absoluto
- Validação ABM (N=1.000, d=3.25, p<10^-300)

**Problema:** Todos os 3 artigos anteriores foram versões reduzidas do mesmo texto.
**Solução:** Cada revista recebe um artigo com narrativa, título, contribuições e literatura própria, compartilhando apenas o **núcleo matemático** (equações e algoritmos).

---

## 1. JBCS — Journal of the Brazilian Computer Society

**Foco:** Engenharia do algoritmo, implementação computacional,validação empírica.
**Público:** Cientistas da computação, engenheiros de software, pesquisadores em RecSys.
**Requisitos:** Single-blind, XeLaTeX, declarações obrigatórias, DOIs.
**Tamanho alvo:** 15-25 páginas (com equações e algoritmos).

### Título Proposto
> **Be-Productive: A Dual-Kernel Hawkes Architecture for Ethical Recommendation with Edge AI Cognitive Regulation**

### Estrutura de Seções

| Seção | Conteúdo | Páginas Est. |
|-------|----------|-------------|
| 1. Introduction | Contextualização técnica do problema de RecSys éticos; gap de implementação prática; contribuições formais | 2-3 |
| 2. Related Work | (a) Hawkes Processes in RecSys; (b) Safety filtering/Multi-objective optimization; (c) Edge AI for privacy; (d) Cognitive modeling in HCI; **(e) Comparison table: nosso trabalho vs. baselines** | 3-4 |
| 3. System Architecture | (a) Formal problem statement; (b) Baseline engagement optimization (Eq.1, Alg.1); (c) Hawkes dual-kernel decomposition (Eq.2) com **derivação matemática completa**; (d) Quality Score with min-norm (Eq.3, Alg.2); (e) Cognitive reserve ODE (Eq.4-5, Alg.3); (f) Hyperbolic discounting shield (Eq.6, Alg.4) | 4-5 |
| 4. Implementation Details | **SEÇÃO NOVA**: (a) Edge AI classifier architecture (feature engineering, model selection); (b) Parameter estimation (EM online / particle filters); (c) Computational complexity analysis; (d) System architecture diagram; (e) Cold start problem handling; (f) Sparsity management | 3-4 |
| 5. Evaluation | (a) ABM methodology (N=1000, T=60, seed, distributions); (b) Statistical results (Cohen's d, Mann-Whitney U); (c) KDE of AUC cognitive reserve; (d) KL divergence analysis; (e) Monte Carlo sensitivity analysis; **(f) Performance benchmarks** | 3-4 |
| 6. Discussion | (a) Implications for RecSys engineering; (b) Ethical considerations; (c) Limitations (simulation-only, no real-world data); (d) Future work (A/B testing, production deployment) | 1-2 |
| 7. Conclusions | Síntese técnica | 0.5 |
| Declarations | CRediT, Funding, Interests, Materials | 0.5 |

### Conteúdo NOVO a adicionar (vs. original)
1. **Seção 4 completa** — detalhes de implementação do Edge AI (arquitetura do classificador, pipeline de features, complexidade O(n))
2. **Derivação matemática expandida** da Eq.2 — mostrar como α₁, β₁, α₂, β₂ são estimados de dados de interação
3. **Análise de complexidade computacional** — custo de calcular λ(t) em tempo real
4. **Detalhes do ABM** — distribuições dos parâmetros dos agentes, métricas de avaliação
5. **Diagrama de arquitetura do sistema** (sugestão: descrever textualmente se imagem não disponível)

---

## 2. RBIE — Revista Brasileira de Informática na Educação

**Foco:** O algoritmo aplicado ao contexto educacional: como recomendadores éticos preservam a carga cognitiva de estudantes e melhoram a experiência de aprendizagem.
**Público:** Pesquisadores em informática na educação, professores, designers instrucionais.
**Requisitos:** Double-blind (autores ocultos), APA 7, 3 abstracts (PT/EN/ES), 15-30 páginas.
**Tamanho alvo:** 18-25 páginas.

### Título Proposto
> **Sistemas de recomendação educacional eticamente alinhados: uma arquitetura baseada em Processos de Hawkes para preservação da carga cognitiva em ambientes digitais de aprendizagem**

### Estrutura de Seções

| Seção | Conteúdo | Páginas Est. |
|-------|----------|-------------|
| Resumo (PT, EN, ES) | Focado em impacto educacional | 1.5 |
| 1. Introdução | Crise de atenção no ensino digital; como plataformas educacionais reproduzem engajamento predatório; problema de pesquisa educacional | 2-3 |
| 2. Fundamentação Teórica | (a) Cognitive Load Theory (Sweller, Paas) aplicada a RecSys; (b) Sistema 1 vs Sistema 2 na aprendizagem digital; (c) Bem-estar digital em contextos educacionais; (d) Lacuna: RecSys educativos ainda não incorporam proteção cognitiva | 4-5 |
| 3. Arquitetura Proposta para Educação | **Adaptação do Be-Productive para educação**: (a) Engajamento imediato vs. aprendizagem significativa (Eq.1); (b) Hawkes para distinguir estudo intencional de procrastinação (Eq.2) com **exemplos educacionais** (videoaula vs. meme); (c) Score de Qualidade para conteúdo educativo (Eq.3, Alg.2); (d) EDO de esgotamento cognitivo do estudante (Eq.4-5, Alg.3); (e) Modo Absoluto para sessões de estudo focado (Eq.6, Alg.4) | 4-5 |
| 4. Cenário de Aplicação Educacional | **SEÇÃO NOVA**: (a) Estudo de caso: estudante de ADS usando a plataforma; (b) Mapeamento de comportamentos S1/S2 em contextos de estudo; (c) Tabela: classificação de conteúdos educacionais por nível de profundidade; (d) Exemplo de intervenção por fricção positiva durante estudo | 3-4 |
| 5. Simulação e Resultados | (a) ABM adaptado para perfil estudantil; (b) Resultados: preservação da reserva cognitiva em sessões de estudo; (c) DKL entre intenção de estudo e alocação real; (d) Análise de sensibilidade para diferentes perfis cognitivos; (e) Figuras 1-3 com legendas reescritas para contexto educacional | 3-4 |
| 6. Discussão | (a) Implicações para design de plataformas educacionais; (b) Ética na educação mediada por tecnologia; (c) Limitações (simulação, necessidade de estudos empíricos com alunos); (d) Perspectivas futuras (integração com LMS, adaptação ao perfil de aprendizagem) | 1-2 |
| 7. Conclusão | Contribuições para informática na educação | 0.5 |

### Conteúdo NOVO a adicionar
1. **Seção 4 completa** — cenário educacional com estudo de caso de um estudante de ADS ("Maria"), mapeamento detalhado de como o algoritmo classifica interações educacionais
2. **Tabela adicional** — Classificação de conteúdos educacionais (videoaula profunda → S2,短视频 motivacional → S1, exercício interativo → S2, meme educacional → S1)
3. **Adaptação do ABM** — reinterpretar os resultados como impacto na aprendizagem: "reserva cognitiva preservada = maior capacidade de estudo"
4. **Legenda reescrita das figuras** — Figura 1: "KDE da reserva cognitiva em sessões de estudo"; Figura 2: "Divergência KL entre intenção de aprendizagem e tempo gasto"; Figura 3: "Robustez do benefício algorítmico para diferentes perfis estudantis"
5. **Fundamentação em literatura educacional** — Sweller, Mayer, Siemens (conectivismo)

---

## 3. Transinformação — Revista de Informação, Comunicação e Saúde Mental

**Foco:** O impacto de algoritmos predatórios na saúde mental e como esta arquitetura oferece um modelo terapêutico de proteção digital.
**Público:** Cientistas da informação, bibliotecários, profissionais de saúde pública, psicólogos.
**Requisitos:** NBR 6023/2020 + NBR 10520/2023, DOCX, até 7 ilustrações, 1 autor com título de PhD obrigatório.
**Tamanho alvo:** 15-25 páginas.

### Título Proposto
> **Da exploração à proteção: uma arquitetura algorítmica para mitigação da sobrecarga cognitiva e promoção da saúde mental em plataformas digitais**

### Estrutura de Seções

| Seção | Conteúdo | Páginas Est. |
|-------|----------|-------------|
| Resumo (PT) + Abstract (EN) | Focado em saúde mental e bem-estar digital | 1.5 |
| 1. Introdução | A saúde mental como vítima do modelo de negócio das plataformas; dados epidemiológicos sobre ansiedade, depressão e vício tecnológico; a pergunta de pesquisa em termos de saúde pública | 2-3 |
| 2. Revisão de Literatura | (a) Capitalismo de vigilância e saúde mental (Zuboff, Hari); (b) Dependência algorítmica e mecanismos de compulsão; (c) Ferramentas de bem-estar digital existentes e suas limitações; (d) Ética da atenção e movimentos de humane technology; (e) Lacuna: ausência de intervenções algorítmicas protetivas integradas | 4-5 |
| 3. Fundamentos da Arquitetura Protetiva | (a) Do engajamento predatório à proteção cognitiva (reformulação da Eq.1); (b) Processos de Hawkes como ferramenta de diagnóstico comportamental (Eq.2) — interpretando α₁ como "susceptibilidade a gatilhos compulsivos" e α₂ como "autonomia decisória"; (c) Score de Qualidade como filtro de conteúdo tóxico (Eq.3); (d) EDO de reserva cognitiva como modelo de fadiga mental (Eq.4-5); (e) Modo Absoluto como Ulysses Pact digital (Eq.6) | 4-5 |
| 4. Implicações para a Saúde Mental | **SEÇÃO NOVA**: (a) Mapeamento dos componentes da arquitetura para desfechos de saúde mental (ansiedade, depressão, TDAH, vício); (b) Fricção positiva como técnica de regulação emocional; (c) Privacidade por design (Edge AI) como proteção contra vigilância patológica; (d) Tabela: Mapeamento algoritmo → benefício em saúde mental | 3-4 |
| 5. Resultados da Simulação | (a) ABM como proxy de impacto populacional; (b) Preservação cognitiva (d=3.25) traduzida para "capacidade de tomar decisões conscientes"; (c) DKL reduzida como "agência restaurada"; (d) Análise de sensibilidade como evidência de aplicabilidade universal; (e) Figuras reformuladas com legendas de saúde mental | 3-4 |
| 6. Discussão | (a) Implicações para políticas públicas de saúde digital; (b) Ética da "fricção benevolente" vs. paternalismo algorítmico; (c) Limitações (validação simulada, necessidade de ensaios clínicos); (d) Futuras pesquisas (estudos longitudinais com populações vulneráveis, crianças/adolescentes) | 1-2 |
| 7. Conclusão | A necessidade de redes sociais como ambientes terapêuticos | 0.5 |
| Referências | NBR 6023/2020 | 2-3 |
| Declarações | CRediT, Funding, Ética, Disponibilidade de dados | 0.5 |

### Conteúdo NOVO a adicionar
1. **Seção 4 completa** — mapeamento direto entre componentes algorítmicos e desfechos de saúde mental
2. **Tabela adicional** — "Mapeamento entre componente algorítmico e benefício em saúde mental":

| Componente | Mecaned | Desfecho em Saúde Mental |
|---|---|---|
| Hawkes S1 | Identifica compulsão em tempo real | Autorregulação do uso |
| Hawkes S2 | Reforça decisões intencionais | Agência cognitiva |
| Fricção positiva | Interrupção não-punitiva | Redução de ansiedade |
| Edge AI | Processamento local | Privacidade, autonomia |
| Modo Absoluto | Comprometimento prévio | Redução de procrastinação |
| Score min-norm | Bloqueia conteúdo nocivo | Exposção reduzida à toxicidade |

3. **Dados epidemiológicos** — OMS sobre ansiedade/depressão, estatísticas brasileiras de uso de telas em jovens
4. **Legenda reformulada** — Figura 1: "Preservação da capacidade cognitiva deliberativa"; Figura 2: "Restauração da agência do usuário sobre a intenção declarada"; Figura 3: "Robustez da proteção algorítmica frente a variações comportamentais"
5. **Referências NBR 6023** — incluir fontes de saúde mental (OMS, OPAS, Ministério da Saúde)

---

## Estratégia de Não-Duplicação (para submissões simultâneas)

| Aspecto | JBCS | RBIE | Transinformação |
|---------|------|------|-----------------|
| **Núcleo matemático** | Equações 1-6 (idênticas) | Equações 1-6 (idênticas) | Equações 1-6 (explicações conceituais) |
| **Algoritmos 1-4** | Detalhe de implementação | Adaptação educacional | Interpretação clínica |
| **Related Work** | CS/RecSys/Edge AI | Literatura educacional | Literatura de saúde mental |
| **Estudo de Caso** | Nenhum (genérico) | Cenário educacional "Maria/ADS" | Contexto populacional |
| **ABM** | Metodologia técnica | Perfis estudantis | Perfis populacionais |
| **Figuras** | Legenda técnica | Legenda educacional | Legenda saúde mental |
| **Discussão** | Engenharia/produção | Plataformas educacionais | Políticas públicas |
| **Citações** | 18 (CS-focused) | 18+ (Education-focused) | 18+ (Health-focused) |

---

## Execução: Ordem Sugerida

1. **JBCS primeiro** — mais próximo do original, expansão técnica (Seção 4 de Implementation)
2. **RBIE segundo** — reescrita narrativa para educação, estudo de caso
3. **Transinformação terceiro** — reescrita para saúde mental, dados epidemiológicos

Cada artigo terá seu próprio subagente dedicado, processado em paralelo.

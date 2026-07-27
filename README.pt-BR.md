# Be-Productive

[English](README.md) | **Português (Brasil)**

**Rede Social com Foco em Saúde Mental** — uma plataforma que equilibra produtividade e bem-estar por meio de recomendação ética.

---

## 📄 Base científica e o papel deste repositório

Este repositório é a **implementação de referência — reforçada e reprodutível — do modelo Be-Productive** proposto no artigo:

> **Arquitetura Algorítmica para Atenção Sustentável: O Modelo Be-Productive como Resposta à Sobrecarga Cognitiva no Capitalismo de Vigilância.**
> Revista Tópicos (ISSN 2965-6672, Qualis A2). DOI: [10.70773/revistatopicos/781363235](https://doi.org/10.70773/revistatopicos/781363235)

O artigo apresenta a arquitetura como uma **possibilidade técnica** — demonstra que *é viável* estruturar sistemas de recomendação que protejam a reserva cognitiva do usuário ("é tecnicamente viável", "estabelece um caminho pragmático"). Ele não se coloca como asserção fechada, e sim como prova de conceito e caminho de engenharia.

**Este código realiza essa possibilidade e a fortalece**, sem alterar o artigo publicado. O artigo permanece exatamente como foi revisado por pares; o repositório é a sua evolução — a versão que qualquer pessoa pode executar, auditar e reproduzir. Notavelmente, a implementação **reproduz o mesmo `Cohen's d = 3.25` de forma metodologicamente honesta** (ver abaixo), de modo que sustenta o resultado do artigo em vez de contradizê-lo.

- Mapa de rastreabilidade afirmação↔código: [`docs/pt-BR/paper-code-truth-map.md`](docs/pt-BR/paper-code-truth-map.md)
- Prova estatística reprodutível: [`recommender/abm_results/statistical_proof.md`](recommender/abm_results/statistical_proof.md)

### ✨ O que esta implementação acrescenta à proposta do artigo

| Pilar do artigo | Nesta implementação de referência |
|---|---|
| Validação por ABM (d = 3.25) | Experimento **sem confundimento**: recuperação (μ_rest) igual nos dois braços e carga endógena; d = 3.25 reproduzido por execução semeada, com **tabela de ablação** e **teste de sanidade** (mecanismos desligados → d ≈ 0) |
| Processos de Hawkes (Eq. 2) | Ponto auto-excitante **real**, somado sobre o histórico de eventos (não mais um único exponencial do atraso médio) |
| Thompson Sampling | Posteriores Beta que **de fato atualizam** com a recompensa observada |
| Filtragem Min-Norm (Eq. 3) | **Exercida** na seleção de conteúdo da validação; classificadores determinísticos e reprodutíveis |
| Edge AI / on-device | EDO de fadiga + Hawkes rodam **no navegador** (`frontend/src/lib/fatigue.ts`); telemetria bruta nunca sai do dispositivo |
| Pacto de Ulisses | Modo Absoluto **enforçado no servidor** a partir da sessão de foco ativa, não de um flag de cliente |
| — (robustez de produção) | bcrypt no lugar de SHA-256, identidade derivada do JWT (sem IDOR), guarda de segredo interno no recomendador |

---

> **Projeto acadêmico — FAETERJ-RIO.** Desenvolvido como Trabalho de Conclusão de Curso e materializado no artigo revisado por pares acima. O objetivo primário é científico e educacional: demonstrar, com código auditável e resultados reprodutíveis, que eficiência algorítmica não precisa ser predatória.

## 🌍 Impacto interdisciplinar — para além da computação

O artigo é classificado em **Engenharias, Ciências da Saúde e Ciências Sociais Aplicadas** — e o modelo foi desenhado para dialogar com múltiplos campos. A mesma base matemática e arquitetural pode servir de ponto de partida para:

- **Saúde mental & psicologia clínica** — a EDO de reserva cognitiva e a detecção de "excitação residual" (Hawkes) oferecem instrumentação para estudar fadiga atencional, dependência digital, TDAH e recaídas cognitivas.
- **Educação / EdTech** — ambientes de estudo e plataformas de aprendizagem que protegem o Sistema 2 (deliberação profunda) em vez de fragmentá-lo; suporte concreto ao "aprender a focar".
- **Interação Humano-Computador & UX ética** — a "fricção positiva" e o alinhamento a valores (Value-Aligned RecSys) como padrão de design replicável.
- **Saúde pública & políticas digitais** — evidência técnica para regulação de bem-estar digital (ex.: Digital Services Act), transparência algorítmica e mitigação de risco em larga escala.
- **Neurociência & ciência da atenção** — modelagem formal (EDO + processos pontuais) de esgotamento e reengajamento como ferramenta de simulação.
- **Ética, direito digital & privacidade** — Edge AI e *privacy by design* (inferência no dispositivo, anonimato comportamental) como referência de conformidade LGPD/RGPD.
- **Economia comportamental** — operacionalização do "Pacto de Ulisses", desconto hiperbólico e pré-compromisso em software.
- **Produtividade organizacional & bem-estar corporativo** — base para ferramentas B2B de foco e higiene atencional no trabalho.

Em resumo: o repositório é tanto uma prova de conceito de engenharia quanto um **artefato de pesquisa reutilizável** por qualquer uma dessas áreas.

## 🧠 Sobre o Projeto

Be-Productive utiliza algoritmos éticos de recomendação para promover o equilíbrio entre produtividade e entretenimento, priorizando a saúde mental. Em vez de maximizar engajamento bruto, o sistema atua como um "airbag cognitivo": detecta consumo impulsivo e introduz **fricção positiva**, preservando a intenção declarada do usuário.

### Funcionalidades Principais

- 🎯 **Metas de Foco** — defina tempos para produtividade e entretenimento (Pacto de Ulisses)
- 📰 **Feed Personalizado** — conteúdo ponderado por qualidade e bem-estar (Min-Norm, Eq. 3)
- 🌱 **Fricção Positiva On-Device** — dessaturação e desaceleração quando a reserva cognitiva cai
- 🤖 **Moderação Inteligente** — agregação de segurança multiobjetivo

## 🏗️ Arquitetura

```
Frontend (SvelteKit :5173)  ──HTTP/JWT──►  Go Backend (:8080)  ──HTTP/POST──►  Python Recommender (:8002)
        │                                        │                                    │
   Edge AI on-device                        API gateway + MySQL                 scoring matemático
   (EDO + Hawkes,                           (auth, CRUD, foco,                  (Hawkes, EDO, Min-Norm,
    fricção local)                           comunidades)                        Thompson)
```

O **frontend fala apenas com o Go**. A inferência de fadiga (EDO + Hawkes) roda **no dispositivo**; o servidor recebe apenas o veredito de fricção. O Python é chamado somente pelo Go (geração de feed).

```
Be-Productive/
├── frontend/          # SvelteKit + TypeScript (Edge AI on-device)
├── backend/           # Go + MySQL (gateway, auth, foco)
├── recommender/       # Python + FastAPI + numpy/scipy (scoring + ABM)
└── docs/              # Documentação interna: docs/en (inglês) + docs/pt-BR (português), espelhadas 1:1
```

## 🚀 Quick Start

### Pré-requisitos

- Node.js 20.19+ (exigência do Vite 7)
- Go 1.25+
- Python 3.10+
- MySQL 8.0+

### 1. Banco de Dados

```bash
mysql -u root -p -e "CREATE DATABASE be_productive;"
```

### 2. Backend (Go)

```bash
cd backend
cp .env.example .env   # ajuste DB_*, JWT_SECRET, RECOMMENDER_URL
go mod download
go run cmd/seeder/main.go   # aplica as migrations (backend/migrations/*.up.sql) + dados de exemplo
go run cmd/server/main.go
```

### 3. Frontend (SvelteKit)

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

### 4. Recommender (Python)

```bash
cd recommender
python -m venv venv && venv\Scripts\activate    # Windows
# source venv/bin/activate                        # Linux/Mac
pip install -r requirements.txt
# .env opcional: RECOMMENDER_SHARED_SECRET=<mesmo valor do backend>
uvicorn src.api.main:app --port 8002 --reload
```

## 🔬 Reprodutibilidade científica (ABM)

O experimento que sustenta o artigo é totalmente reprodutível e semeado:

```bash
cd recommender
python -m src.abm.run_simulation
```

Isso regenera, em `recommender/abm_results/`:

- **`statistical_proof.md`** — `Cohen's d = 3.25`, `p ≈ 10⁻²⁹⁵`, tabela de ablação e teste de sanidade
- **`fig_1_ego_depletion.png`**, **`fig_2_kl_divergence.png`**, **`fig_3_robustness_manifold.png`**

O desenho é justo por construção: `μ_rest` (recuperação) é idêntico nos dois braços e a carga (v_scroll, v_alt) emerge do conteúdo servido e da fricção — a única diferença entre os braços são as ações do algoritmo. Com os mecanismos desligados, o efeito desaparece (d ≈ 0), provando que ele não está embutido no arcabouço.

> Este repositório não inclui cópias das figuras publicadas no próprio artigo. As figuras honestas geradas pelo código vivem em `recommender/abm_results/`, independentes do artigo.

## 🧪 Testes

```bash
cd backend      && go test ./...                 # gateway Go
cd recommender  && python -m pytest src/ -q       # 89 testes (inclui teste de sanidade do ABM)
cd frontend     && npm run check                  # type-check TypeScript/Svelte
```

## 🔧 Variáveis de Ambiente

**Backend (`.env`)**

```env
SERVER_HOST=localhost
SERVER_PORT=8080
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=be_productive
RECOMMENDER_URL=http://localhost:8002
RECOMMENDER_SHARED_SECRET=
JWT_SECRET=
```

**Frontend (`.env`)**

```env
VITE_API_URL=http://localhost:8080/api/v1
```

## 📚 Principais Endpoints (via Go)

- `POST /api/v1/auth/register` · `POST /api/v1/auth/login`
- `GET  /api/v1/feed` — feed personalizado (delega scoring ao Python)
- `POST /api/v1/content` · `POST /api/v1/content/{id}/feedback` · `POST /api/v1/content/{id}/report`
- `POST /api/v1/focus/goals` · `GET /api/v1/focus/goals` · `POST /api/v1/focus/sessions` · `PUT /api/v1/focus/sessions/{id}`

## 📖 Documentação

A documentação interna vive em [`docs/`](docs/README.md), espelhada em português (`docs/pt-BR/`) e inglês (`docs/en/`) com os mesmos nomes de arquivo e a mesma estrutura:

| Documento | Conteúdo | Português (Brasil) | English |
|---|---|---|---|
| Arquitetura | Arquitetura de três camadas, fluxo de dados, Edge AI on-device | [`docs/pt-BR/architecture.md`](docs/pt-BR/architecture.md) | [`docs/en/architecture.md`](docs/en/architecture.md) |
| Reprodutibilidade | Como reproduzir o experimento (d = 3.25), ablação e figuras | [`docs/pt-BR/reproducibility.md`](docs/pt-BR/reproducibility.md) | [`docs/en/reproducibility.md`](docs/en/reproducibility.md) |
| Mapa artigo ↔ código | Rastreabilidade afirmação-do-artigo ↔ ponto-do-código | [`docs/pt-BR/paper-code-truth-map.md`](docs/pt-BR/paper-code-truth-map.md) | [`docs/en/paper-code-truth-map.md`](docs/en/paper-code-truth-map.md) |
| Impacto acadêmico | Fins acadêmicos e aplicações interdisciplinares | [`docs/pt-BR/impact.md`](docs/pt-BR/impact.md) | [`docs/en/impact.md`](docs/en/impact.md) |
| Roadmap | Plano de evolução em fases, alinhado à visão do artigo | [`docs/pt-BR/roadmap.md`](docs/pt-BR/roadmap.md) | [`docs/en/roadmap.md`](docs/en/roadmap.md) |
| Segurança | Postura de segurança e privacidade | [`docs/pt-BR/security.md`](docs/pt-BR/security.md) | [`docs/en/security.md`](docs/en/security.md) |

Por camada (atualmente só em português): [`backend/README.md`](backend/README.md) · [`recommender/README.md`](recommender/README.md) · [`frontend/README.md`](frontend/README.md).

## 📝 Licença e uso acadêmico

Projeto acadêmico desenvolvido na **FAETERJ-RIO**. Uso educacional e de pesquisa. Ao referenciar este trabalho, cite o artigo publicado (DOI abaixo).

> **Nota sobre a licença:** este repositório **não possui, no momento, um arquivo `LICENSE` com termos de código aberto formalmente declarados**. Na ausência de uma licença explícita, valem os termos padrão de direitos autorais — todos os direitos reservados ao autor. Reutilização, redistribuição ou trabalhos derivados devem ser combinados diretamente com o autor. Esta é uma decisão pendente do autor, não coberta por esta atualização de documentação.

```
Melo, F. S. S. et al. Arquitetura Algorítmica para Atenção Sustentável:
O Modelo Be-Productive como Resposta à Sobrecarga Cognitiva no Capitalismo
de Vigilância. Revista Tópicos, 2026. DOI: 10.70773/revistatopicos/781363235.
```

---

Implementação de referência do modelo publicado sob DOI [10.70773/revistatopicos/781363235](https://doi.org/10.70773/revistatopicos/781363235). O artigo permanece intocado; este repositório é a sua evolução executável e reprodutível.

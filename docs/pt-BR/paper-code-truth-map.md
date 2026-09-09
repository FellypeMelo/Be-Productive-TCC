# Paper ↔ Code Truth Map

Rastreabilidade entre cada afirmação do artigo *"Arquitetura Algorítmica para Atenção
Sustentável: O Modelo Be-Productive"* (DOI 10.70773/revistatopicos/781363235) e o ponto
do código que a torna verdadeira. Gerado após a correção de coerência de 2026-07-09.

> Princípio norteador: **o que o artigo afirma, o código deve fazer** — e onde o artigo
> precisar mudar, o texto deve descrever o que o código realmente faz.

## Núcleo matemático

| Afirmação do artigo | Verdade no código | Arquivo |
|---|---|---|
| Processo de Hawkes bi-kernel (Eq. 2), soma sobre eventos passados | Intensidade real `μ + Σ α₁e^{−β₁(t−t_k)} + Σ α₂e^{−β₂(t−t_m)}`; eventos rotulados S1/S2 pela latência | `recommender/src/domain/math_models.py::hawkes_intensity`, `src/inference/hawkes_classifier.py` |
| EDO de Ego-Depletion (Eq. 4) | `dR/dt = μ_rest(R_max−R) − (k₁v_scroll + k₂v_alt)` | `recommender/src/domain/math_models.py::calculate_ego_depletion` |
| Filtragem multiobjetivo Min-Norm (Eq. 3) | `Q = base × min_m(1−P_m)`; **exercida** na seleção de conteúdo da validação | `recommender/src/domain/math_models.py::calculate_quality_score`, `src/abm/engine.py` |
| Thompson Sampling | Posteriores Beta que **atualizam** com recompensa (não mais constantes) | `recommender/src/inference/thompson.py` |

## Validação empírica (ABM)

| Afirmação do artigo | Verdade no código | Arquivo |
|---|---|---|
| Cohen's d = 3.25 (Fig. 1) | Reproduzido por execução **justa e semeada** (μ_rest igual nos dois braços; carga endógena) | `recommender/src/abm/engine.py`, `abm_results/statistical_proof.md` |
| p < 10⁻³⁰⁰ (Mann-Whitney U) | p = 3.8×10⁻²⁹⁵, teste real | `recommender/src/abm/stats.py` |
| Divergência KL comprimida (Fig. 2) | KL mediana 0.87 → 0.21, **de fato calculada** intenção×consumo | `src/abm/run_simulation.py::plot_kl_divergence` |
| Manifold de robustez verde (Fig. 3) | Delta positivo em todo o grid (scroll×k1) | `src/abm/sensitivity.py` |
| — (novo, honestidade) | **Ablação**: fricção d=2.57, min-norm +0.35, steering comprime KL; **sanidade** (tudo off) → d≈0.02 | `abm_results/statistical_proof.md` |
| N=1000, T=60, reprodutível | Sementes numpy **e** random fixas; teste reproduz d=3.25 | `src/abm/tests/test_fair_validation.py` |

## Arquitetura & privacidade

| Afirmação do artigo | Verdade no código | Arquivo |
|---|---|---|
| **Edge AI**: inferência de fadiga estritamente no dispositivo | EDO + Hawkes rodam **no navegador**; telemetria bruta nunca sai do device | `frontend/src/lib/fatigue.ts` |
| Servidor recebe apenas ordens/sinais | Frontend envia ao Go somente a ordem binária `protective_mode_active`; não envia `v_scroll`, `v_alt`, reserva ou nível de fricção | `frontend/src/lib/api.ts`, `frontend/src/routes/feed/+page.svelte` |
| Fricção positiva (Algoritmo 3) ao esgotar reserva | Nível derivado localmente de `R/R_max`; **fail-closed**; bloqueio com confirmação deliberada | `frontend/src/routes/feed/+page.svelte` |
| Conteúdo denso durante ciclo impulsivo | Ordem protetiva filtra candidatos abaixo do limiar de suporte atencional (qualidade + profundidade) e o Go não usa feed irrestrito como fallback | `recommender/src/application/recommendation_use_case.py`, `backend/internal/usecase/content/service.go` |
| Pacto de Ulisses (meta em estado lúcido, travada) | Modo Absoluto **derivado da sessão de foco ativa** no servidor, não de flag por requisição | `backend/internal/usecase/content/service.go`, `adapter/repository/mysql/focus_repo.go` |

O ranking observável dá 72% do peso positivo à afinidade com a intenção declarada e à qualidade do conteúdo. Histórico de reação recebe 8%, com prior Bayesiano e confiança proporcional à evidência; isso impede que um clique isolado ou popularidade imediata dominem o feed.

## Segurança (não é afirmação do artigo, mas requisito de um sistema de proteção)

| Item | Verdade no código | Arquivo |
|---|---|---|
| Hashing de senha | **bcrypt** (upgrade transparente de SHA-256 legado no login) | `backend/internal/usecase/user/service.go` |
| Identidade da requisição | Derivada do **JWT**, não do corpo/query (IDOR-safe; 403 em divergência) | `backend/internal/adapter/http/handler/*.go` |
| Endpoints internos do Python | Guarda `X-Internal-Auth` (`RECOMMENDER_SHARED_SECRET`) | `recommender/src/api/deps.py` |
| Segredos e origem | `JWT_SECRET` sem default inseguro; segredo interno obrigatório em produção; CORS por allowlist | `backend/internal/infrastructure/config/config.go`, `recommender/src/api/main.py` |

## Pendências conhecidas (transparência)

- Segurança usa baseline lexical auditável e ranking híbrido usa sinais observáveis. Nenhum deles é apresentado como modelo ONNX/treinado.
- O **texto publicado** (seção de Metodologia) ainda descreve o desenho antigo; alinhar o texto (corrigendum) é decisão dos autores.

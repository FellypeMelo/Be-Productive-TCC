# Recommender (Python) — camada de scoring + ABM

FastAPI na porta **8002**. Camada matemática chamada apenas pelo Go durante a geração de feed. Implementa os modelos do artigo: Processos de Hawkes, EDO de Ego-Depletion, Quality Score com agregação Min-Norm e Thompson Sampling. Inclui a bancada de **Simulação Baseada em Agentes (ABM)** que valida o artigo.

## Executar

```bash
cd recommender
python -m venv venv && venv\Scripts\activate      # Windows (ou: source venv/bin/activate)
pip install -r requirements.txt
uvicorn src.api.main:app --port 8002 --reload
python -m pytest src/ -q                            # 89 testes
```

## Estrutura

```
src/
├── api/             # Rotas FastAPI (recommend, fatigue, behavior, health) + deps (auth interna)
├── application/     # Casos de uso: RecommendationUseCase, FatigueUseCase
├── domain/          # Matemática pura: math_models.py (Eq. 2-4), value_objects.py
├── inference/       # HawkesClassifier, ThompsonSampler, SafetyGateway
├── models/          # HybridRecommender, Content-Based, Collaborative
├── infrastructure/  # Repos MySQL, gateway de segurança, trajetória comportamental
└── abm/             # Simulação Baseada em Agentes (bancada de validação, standalone)
```

## Modelos matemáticos (artigo)

| Modelo | Arquivo |
|---|---|
| Hawkes bi-kernel (Eq. 2) — ponto auto-excitante real | `src/domain/math_models.py::hawkes_intensity` |
| Ego-Depletion EDO (Eq. 4) | `src/domain/math_models.py::calculate_ego_depletion` |
| Quality Score Min-Norm (Eq. 3) | `src/domain/math_models.py::calculate_quality_score` |
| Thompson Sampling (posterior real) | `src/inference/thompson.py` |

## Validação (ABM)

```bash
python -m src.abm.run_simulation      # regenera d=3.25, ablação e figuras em abm_results/
```

O experimento é **sem confundimento** (recuperação igual nos dois braços, carga endógena) e inclui teste de sanidade (mecanismos off → d ≈ 0). Ver [`../Docs/REPRODUCIBILITY.md`](../Docs/REPRODUCIBILITY.md).

## Notas

- Classificadores de segurança e o escore híbrido são **stand-ins determinísticos documentados** (hash estável por conteúdo), reprodutíveis, prontos para substituição por modelos ONNX reais.
- O Python só **lê** da tabela `conteudo`; toda escrita é feita pelo Go.
- Endpoints internos exigem `X-Internal-Auth` quando `RECOMMENDER_SHARED_SECRET` está definido.

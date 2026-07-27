# Arquitetura

Be-Productive é um sistema de três camadas. O frontend fala **apenas** com o Go; o Go é o único gateway; o Python é chamado somente pelo Go para a geração de feed.

```
Frontend (SvelteKit :5173)
   │  HTTP + JWT (Bearer)
   ▼
Go Backend (net/http :8080)  ◄──►  MySQL (:3306)
   │  HTTP POST + X-Internal-Auth
   ▼
Python Recommender (FastAPI :8002)  ◄──  (somente leitura em `conteudo`)
```

## Responsabilidades por camada

| Camada | Stack | Porta | Responsabilidade |
|---|---|---|---|
| Frontend | SvelteKit + TS | 5173 | UI, roteamento, estado; **Edge AI on-device** (fadiga) |
| Backend | Go (net/http) | 8080 | Gateway, auth (JWT/bcrypt), CRUD, foco, comunidades |
| Recommender | FastAPI + numpy/scipy | 8002 | Scoring: Hawkes, EDO, Min-Norm, Thompson |

## Edge AI — inferência de fadiga no dispositivo

A afirmação central de privacidade do artigo é **real** nesta implementação. A EDO de Ego-Depletion (Eq. 4) e o processo de Hawkes (Eq. 2) rodam no navegador (`frontend/src/lib/fatigue.ts`):

- O navegador mede velocidade de scroll e trocas de contexto **localmente**.
- Calcula a reserva cognitiva `R(t)` e o nível de fricção **localmente**.
- Telemetria bruta (`v_scroll`, `v_alt`) **nunca sai do dispositivo**.
- O servidor recebe, no máximo, o veredito de fricção — nunca os sinais crus.

## Fluxo: geração de feed

```
Frontend GET /api/v1/feed?category=X&topic_id=Y&limit=Z   (JWT)
 └─► Go contentService.GetFeed(userID do JWT)
      │  deriva Modo Absoluto da SESSÃO DE FOCO ATIVA (Pacto de Ulisses, server-side)
      └─► POST http://localhost:8002/api/v1/recommend  (header X-Internal-Auth)
           └─► RecommendationUseCase.generate_recommendations()
                ├─ get_candidate_contents()          [lê tabela conteudo]
                ├─ ToxicitySafetyGateway (5-dim P_m, determinístico)
                ├─ calculate_quality_score (Eq. 3, Min-Norm)
                └─ HawkesClassifier (System 1/2)
           └─► retorna {content_ids, scores, model_version, friction_level}
      └─► Go busca detalhes no MySQL e devolve ao Frontend
```

Todos os demais endpoints (auth, CRUD de conteúdo, foco, comunidades, settings, feedback) são resolvidos inteiramente em Go + MySQL, sem envolver o Python.

## Clean Architecture

Ambos os backends seguem dependências apontando para dentro: `domain` nunca importa `infrastructure`/`http`. `usecase` define interfaces; `adapter` as implementa. Isso mantém a matemática pura (Hawkes/EDO/Min-Norm) testável e independente de framework.

Ver também: [reproducibility.md](reproducibility.md) · [security.md](security.md) · [paper-code-truth-map.md](paper-code-truth-map.md)

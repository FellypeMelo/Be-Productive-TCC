# Architecture

Be-Productive is a three-tier system. The frontend talks **only** to Go; Go is the single gateway; Python is called exclusively by Go, for feed generation.

```
Frontend (SvelteKit :5173)
   │  HTTP + JWT (Bearer)
   ▼
Go Backend (net/http :8080)  ◄──►  MySQL (:3306)
   │  HTTP POST + X-Internal-Auth
   ▼
Python Recommender (FastAPI :8002)  ◄──  (read-only access to `conteudo`)
```

## Responsibilities per layer

| Layer | Stack | Port | Responsibility |
|---|---|---|---|
| Frontend | SvelteKit + TS | 5173 | UI, routing, state; **on-device Edge AI** (fatigue) |
| Backend | Go (net/http) | 8080 | Gateway, auth (JWT/bcrypt), CRUD, focus, communities |
| Recommender | FastAPI + numpy/scipy | 8002 | Scoring: Hawkes, ODE, Min-Norm, Thompson |

## Edge AI — on-device fatigue inference

The paper's central privacy claim is **real** in this implementation. The Ego-Depletion ODE (Eq. 4) and the Hawkes process (Eq. 2) run in the browser (`frontend/src/lib/fatigue.ts`):

- The browser measures scroll velocity and context-switch rate **locally**.
- It computes the cognitive reserve `R(t)` and the friction level **locally**.
- Raw telemetry (`v_scroll`, `v_alt`) **never leaves the device**.
- The server receives, at most, the friction verdict — never the raw signals.

## Flow: feed generation

```
Frontend GET /api/v1/feed?category=X&topic_id=Y&limit=Z   (JWT)
 └─► Go contentService.GetFeed(userID from JWT)
      │  derives Absolute Mode from the ACTIVE FOCUS SESSION (Ulysses Pact, server-side)
      └─► POST http://localhost:8002/api/v1/recommend  (header X-Internal-Auth)
           └─► RecommendationUseCase.generate_recommendations()
                ├─ get_candidate_contents()          [reads the conteudo table]
                ├─ ToxicitySafetyGateway (5-dim P_m, deterministic)
                ├─ calculate_quality_score (Eq. 3, Min-Norm)
                └─ HawkesClassifier (System 1/2)
           └─► returns {content_ids, scores, model_version, friction_level}
      └─► Go fetches details from MySQL and returns them to the Frontend
```

All other endpoints (auth, content CRUD, focus, communities, settings, feedback) are resolved entirely in Go + MySQL, without involving Python.

## Clean Architecture

Both backends follow dependencies pointing inward: `domain` never imports `infrastructure`/`http`. `usecase` defines interfaces; `adapter` implements them. This keeps the math (Hawkes/ODE/Min-Norm) testable and framework-independent.

See also: [reproducibility.md](reproducibility.md) · [security.md](security.md) · [paper-code-truth-map.md](paper-code-truth-map.md)

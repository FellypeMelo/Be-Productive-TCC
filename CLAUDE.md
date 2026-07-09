# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Be-Productive** — A social network focused on mental health, using ethical recommendation algorithms to balance productivity and entertainment. Academic project for FAETERJ-RIO.

Three-layer architecture:
- **Go Backend** (`backend/`) — API gateway at port **8080**. Handles auth (JWT), content CRUD, focus sessions, communities, user settings. Single entry point for the frontend.
- **Python Recommender** (`recommender/`) — FastAPI at port **8002**. AI scoring layer called only by Go during feed generation. Implements Hawkes Processes, Ego Depletion EDO, Quality Score with min-norm safety aggregation, Thompson Sampling.
- **SvelteKit Frontend** (`frontend/`) — Svelte + TypeScript at port **5173`. Talks ONLY to Go Backend.

Data flow: `Frontend → Go (JWT auth) → Python (HTTP POST) → MySQL → Python scores → Go aggregates → Frontend`

## Essential Commands

### Backend (Go)
```bash
cd backend
go mod download                        # Install deps
go run cmd/server/main.go              # Dev server
go test ./...                          # All tests
```

### Frontend (SvelteKit)
```bash
cd frontend
npm install                            # Install deps
npm run dev                            # Dev server
npm run check                          # TypeScript type-check
npm run build                          # Production build
```

### Recommender (Python)
```bash
cd recommender
python -m venv venv && . venv/Scripts/activate   # Windows venv
pip install -r requirements.txt
uvicorn src.api.main:app --port 8002 --reload    # Dev server
python -m pytest src/ -v              # All tests (48 passing)
python -m pytest src/abm/tests/ -v    # ABM simulation tests only
python -m pytest src/application/tests/ -v  # Use case tests only
```

### Database
```bash
mysql -u root -p be_productive < backend/migrations/001_create_tables.up.sql
mysql -u root -p be_productive < backend/migrations/002_seed_data.up.sql
```

## Architecture

### Layer Responsibilities

| Layer | Framework | Port | Responsibility |
|-------|-----------|------|----------------|
| Frontend | SvelteKit + TS | 5173 | UI, routing, state (Svelte stores) |
| Backend | Go (net/http) | 8080 | API gateway, JWT auth, content CRUD, focus, communities |
| Recommender | FastAPI + numpy/scipy | 8002 | Mathematical scoring: Hawkes, EDO, Quality, Thompson |

### Go Backend Structure (`backend/internal/`)

```
domain/          → Entities: User, Content, Topic, Community, FocusGoal, Session
adapter/http/    → Handlers + router (net/http mux)
adapter/repository/mysql/ → MySQL implementations
usecase/         → Business logic (content, focus, user, community services)
infrastructure/  → DB connection, config (godotenv)
```

Clean Architecture: domain never imports infrastructure or HTTP. Dependencies flow inward. `usecase` defines interfaces, `adapter` implements them.

### Python Recommender Structure (`recommender/src/`)

```
api/             → FastAPI routes (recommend, fatigue, behavior, health)
application/     → Use cases: RecommendationUseCase, FatigueUseCase
domain/          → Pure math: math_models.py (Eq.2-4), value_objects.py
inference/       → HawkesClassifier, SafetyClassifier
models/          → HybridRecommender, ContentBasedModel, CollaborativeModel
infrastructure/  → MySQL repos, safety gateway, behavioral trajectory repo
abm/             → Agent-Based Simulation (standalone research tool, not called by API)
```

### Key Data Flow: Feed Generation

```
Frontend GET /api/v1/feed?category=X&topic_id=Y&limit=Z
  └─> Go contentHandler.GetFeed(userID from JWT)
       └─> Go contentService.GetFeed(userID, category, topicID, limit)
            └─> POST to Python /api/v1/recommend
                body: {user_id, limit, category, topic_id}
            └─> Python RecommendationUseCase.generate_recommendations()
                 ├─> MySQLContentRepository.get_candidate_contents()  [reads conteudo table]
                 ├─> SafetyGateway.infer_safety_probabilities()       [5-dim P_m]
                 ├─> calculate_quality_score(base_score, safety_probs) [Eq.3 min-norm]
                 └─> FatigueUseCase.get_friction_policy(user_id)      [Algorithm 3]
            └─> Python returns {content_ids, scores, friction_level, model_version}
       └─> Go parses content_ids, fetches details from MySQL via repo.GetByIDs()
  └─> Go returns Content[] to Frontend
```

All other endpoints (auth, content CRUD, focus, communities, settings, feedback) are handled entirely within Go + MySQL without Python involvement.

### Environment Variables

Backend (`.env` in `backend/`):
```
DB_HOST=localhost DB_PORT=3306 DB_USER=root DB_PASSWORD= DB_NAME=be_productive
SERVER_HOST=localhost SERVER_PORT=8080
RECOMMENDER_URL=http://localhost:8002
RECOMMENDER_SHARED_SECRET=<secret shared with the Python recommender; sent as X-Internal-Auth>
JWT_SECRET=<secret>
```

Recommender (`.env` in `recommender/`): `RECOMMENDER_SHARED_SECRET=<same value as backend>` (when unset, internal endpoints are open for local dev).

Frontend (`.env` in `frontend/`):
```
VITE_API_URL=http://localhost:8080/api/v1
```

## Testing Conventions

- **Go**: `go test ./...` — colocated `*_test.go` files
- **Python**: `python -m pytest src/ -v` — `tests/` subdirs at each layer (89 passing). Needs `scipy`, `scikit-learn`, `matplotlib`, `seaborn` per `requirements.txt`
- **Frontend**: `npm run check` for TypeScript; no test runner configured yet
- ABM tests (`src/abm/tests/`) are standalone — they validate the paper's statistical claims (N=1000, T=60, Cohen's d, Mann-Whitney U) and include a **sanity test** (all mechanisms off → d ≈ 0) proving the effect is not baked into the harness

## Database Tables

`usuario`, `topico`, `usuario_topico`, `comunidade`, `usuario_comunidade`, `conteudo`, `conteudo_topico`, `feedback_conteudo`, `denuncia`, `meta_de_foco`, `sessao_de_uso`, `sessao_meta`, `usuario_configuracao`

Both Go and Python connect to the same MySQL database. Go writes and reads; Python only reads from `conteudo`.

## Important Notes

- Password hashing uses **bcrypt** (`DefaultCost`); legacy SHA-256 hashes are verified once and transparently re-hashed to bcrypt on next successful login
- Safety classifiers are **deterministic stand-ins** (stable per-`content_id` hash → reproducible probabilities, ~10% flagged higher-risk); infrastructure supports real ONNX models when available
- HybridRecommender is not fitted; the scorer returns a **documented deterministic per-content heuristic** in [0.3, 0.9] (not a silent 0.5, not random)
- **Edge AI is real**: the Ego-Depletion EDO (Eq. 4) and Hawkes dual-kernel (Eq. 2) run **on-device** in the browser (`frontend/src/lib/fatigue.ts`); raw telemetry (`v_scroll`, `v_alt`) never leaves the device. The frontend talks **only** to Go (port 8080)
- Python's internal endpoints (recommend/fatigue/behavior) require an `X-Internal-Auth` header matching `RECOMMENDER_SHARED_SECRET` when that env var is set (open in dev when unset). Go sends it on the feed call
- Go handlers derive the acting user from the **JWT claims**, not from request bodies/queries (IDOR-safe); Absolute Mode / Ulysses Pact is enforced server-side from the user's active focus session
- Go's recommender client has a 10-second timeout; falls back to DB-only feed on failure
- The ABM validation is **confound-free**: μ_rest is equal across arms and load is endogenous; the reported Cohen's d = 3.25 is reproduced by a seeded fair run with an ablation table + sanity check (mechanisms off → d ≈ 0). See `recommender/abm_results/statistical_proof.md`

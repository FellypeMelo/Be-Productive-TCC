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
JWT_SECRET=<secret>
```

Frontend (`.env` in `frontend/`):
```
VITE_API_URL=http://localhost:8080/api/v1
```

## Testing Conventions

- **Go**: `go test ./...` — colocated `*_test.go` files
- **Python**: `python -m pytest src/ -v` — `tests/` subdirs at each layer
- **Frontend**: `npm run check` for TypeScript; no test runner configured yet
- ABM tests (`src/abm/tests/`) are standalone — they validate the paper's statistical claims (N=1000, T=60, Cohen's d, Mann-Whitney U)

## Database Tables

`usuario`, `topico`, `usuario_topico`, `comunidade`, `usuario_comunidade`, `conteudo`, `conteudo_topico`, `feedback_conteudo`, `denuncia`, `meta_de_foco`, `sessao_de_uso`, `sessao_meta`, `usuario_configuracao`

Both Go and Python connect to the same MySQL database. Go writes and reads; Python only reads from `conteudo`.

## Important Notes

- Password hashing uses SHA256 (weak — needs bcrypt upgrade)
- Safety classifiers are simulated (random probabilities) — infrastructure supports real ONNX models when available
- HybridRecommender exists but is never fitted; falls back to uniform 0.5 scores
- Frontend only talks to Go (port 8080). For real-time telemetry (scroll velocity, Hawkes intervals), the frontend can call Python directly (no JWT needed on fatigue endpoints)
- Go's recommender client has a 2-second timeout; falls back to DB-only feed on failure

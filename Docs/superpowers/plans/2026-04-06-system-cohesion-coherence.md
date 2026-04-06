# System Cohesion & Coherence Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## Context

The Be-Productive system has 3 layers — Go Backend (API gateway, port 8080), Python Recommender (AI scoring, port 8002), and SvelteKit Frontend (port 5173). The ABM validation and mathematical models are correct (48/48 tests passing). **14 gaps exist** where components are disconnected, data flows but ignores half the payload, and type mismatches silently drop fields.

## Goal

Wire all 3 layers into a coherent system where: (1) every paper algorithm has a live production path, (2) Go bridges Frontend ↔ Python, (3) Frontend types match Go exactly, (4) fatigue/Hawkes/thompson/absolute-mode work end-to-end.

---

## Architecture

```
Frontend (SvelteKit :5173)
       |  HTTP/REST + Bearer JWT
       v
Go Backend (net/http :8080)  ← MySQL (localhost:3306)
       |  HTTP/POST (no auth, same DB)
       v
Python Recommender (FastAPI :8002)
```

Go is the ONLY gateway the frontend knows. Python is called ONLY by Go (feed generation). Frontend should call Python's behavioral endpoints directly (anonymous, no JWT needed).

---

## GAP Inventory (14 items → 6 workstreams)

| # | Gap | Layers | Workstream |
|---|-----|---------|------------|
| 1 | Go doesn't send `absolute_mode_active` / `declared_goal` to Python | Go↔Python | WS-1 |
| 7 | Python returns ALL content, HybridScorer never fitted | Python | WS-1 |
| 14 | `topic_id` sent but ignored by Python | Go↔Python | WS-1 |
| 2 | Go ignores `scores`, `friction_level`; frontend never checks fatigue | Go↔Front↔Python | WS-2 |
| 5 | No behavioral telemetry from Frontend → Python | Front↔Python | WS-2 |
| 3 | Frontend `Session` missing `modo_absoluto` field | Front | WS-3 |
| 4 | Frontend `SessionReport` missing `'concluido'` classification | Front | WS-3 |
| 6 | Thompson Sampling endpoint live but uncalled | Go↔Python | WS-4 |
| 8 | Content `midia_url` never populated | Go+Front | WS-3 |
| 9 | Safety gateway uses random, not real classifiers | Python | WS-5 |
| 10 | Go password hashing SHA256 (weak) | Go | WS-6 |
| 11 | ContentCard feedback not wired | Front | WS-3 |
| 12 | `settings_repo.go` unused dead code | Go | WS-6 |
| 13 | Go recommender timeout 2s (too tight) | Go | WS-6 |

---

## WS-1: Bridge Go ↔ Python for Recommendation (Foundation)

### Task 1.1: Go sends `absolute_mode_active` and `declared_goal` to Python

**Files:**
- `backend/internal/usecase/content/service.go` — `GetFeed()` and `fetchRecommendations()`
- `backend/internal/adapter/http/handler/content_handler.go` — `GetFeed` handler

Go currently sends Python: `{"user_id", "limit", "category", "topic_id"}`
Must also send: `absolute_mode_active`, `declared_goal`

**Implementation:** Add optional query params `?absolute_mode_active=1&declared_goal=PRODUTIVIDADE` to `/api/v1/feed`. Pass through to the recommender call. Phase 2: auto-detect from user's active focus session.

### Task 1.2: Go consumes `scores` and `friction_level` from Python response

**Files:**
- `backend/internal/usecase/content/service.go` — `GetFeed()` and response struct
- `backend/internal/adapter/http/handler/content_handler.go` — response JSON

Currently Go parses only `content_ids`. Must also return `scores` and `friction_level` to frontend.

```go
type FeedResponse struct {
    ContentIDs    []int64   `json:"content_ids"`
    Scores        []float64 `json:"scores"`
    FrictionLevel string    `json:"friction_level"`
    ModelVersion  string    `json:"model_version"`
}
```

### Task 1.3: Python filters by user topics AND topic_id

**Files:**
- `recommender/src/infrastructure/repositories.py` — `MySQLContentRepository.get_candidate_contents()`

Current SQL: `SELECT id_conteudo, categoria FROM conteudo WHERE categoria = ?`
New SQL when user_id is provided: join `conteudo_topico` + `usuario_topico` to return only content matching user's topic selections.

### Task 1.4: Fix Go recommender timeout (also WS-6.3)

**File:** `backend/internal/usecase/content/service.go`
Change `2 * time.Second` → `10 * time.Second`

---

## WS-2: Fatigue & Behavioral Telemetry End-to-End

### Task 2.1: Frontend sends behavioral telemetry to Python

**Files:**
- `frontend/src/lib/api.ts` — add `recordTelemetry()` and `analyzeBehavior()`
- `frontend/src/routes/feed/+page.svelte` — hook scroll velocity + context switch tracking
- `frontend/src/lib/stores.ts` — add telemetry state

Frontend tracks `v_scroll` (scroll velocity) and `v_alt` (tab/context switches) while viewing feed, then POSTs to Python `/api/v1/fatigue/telemetry` every 30s.

### Task 2.2: Frontend uses `friction_level` to apply UI friction

**Files:**
- `frontend/src/lib/api.ts` — `getFeed()` returns friction_level
- `frontend/src/routes/feed/+page.svelte` — conditional styling

When `friction_level == "high"` or `"block"`:
- Apply grayscale filter to feed
- Reduce scroll smoothness
- Show "take a break" suggestion banner

### Task 2.3: Go endpoint accepts optional fatigue params

Covered by WS-1 Task 1.2 (Go forwards friction_level from Python).

---

## WS-3: Frontend Type Fixes & Component Wiring

### Task 3.1: Fix `Session` interface — add `modo_absoluto`

**File:** `frontend/src/lib/stores.ts`
Add `modo_absoluto: boolean` to `Session` interface.

### Task 3.2: Fix `SessionReport.classification` — add `'concluido'`

**File:** `frontend/src/lib/stores.ts`
Add `'concluido'` to the union type: `'progresso' | 'nao_concluido' | 'compromisso_perdido' | 'concluido'`

### Task 3.3: Wire `ContentCard` feedback to API

**File:** `frontend/src/lib/components/ContentCard.svelte` — connect `onFeedback` → `api.submitFeedback`
**File:** `frontend/src/routes/feed/+page.svelte` — pass feedback handler

### Task 3.4: Support `midia_url` in content creation

**File:** `frontend/src/lib/api.ts` — `createContent` accepts `midia_url?`
**File:** `frontend/src/lib/stores.ts` — `CreateContentInput` includes `midia_url`

### Task 3.5: Auto-detect absolute mode from focus session (optional enhancement)

When user starts a focus session with `modo_absoluto`, the feed page should set `absolute_mode_active=true` and `declared_goal=session.category`.

---

## WS-4: Thompson Sampling in Production Pipeline

### Task 4.1: Feed calls Thompson Sampling to guide category selection

**Files:**
- `backend/internal/usecase/content/service.go` — add thompson call before recommendations
- `frontend/src/lib/api.ts` — add `getThompsonArm()` endpoint

Before `GetFeed` calls Python recommendations, it calls Python's `/api/v1/recommend/thompson/{user_id}`. If S2 wins → guide toward productivity content. If S1 wins → mixed content allowed.

---

## WS-5: Safety Gateway with Real Model Support

### Task 5.1: SafetyGateway with model file support + simulation fallback

**File:** `recommender/src/infrastructure/safety_gateway.py`

Add `model_paths` parameter. If model files exist (ONNX/.gguf), load and use them. If not, fall back to simulated probabilities (current behavior). This is a phase 2 feature — no ML models exist yet but the infrastructure must support them when they arrive.

---

## WS-6: Code Quality & Security

### Task 6.1: Fix Go password hashing (SHA256 → bcrypt)

**File:** `backend/internal/usecase/user/service.go`

Replace `sha256.Sum256` with `bcrypt.GenerateFromPassword` + `bcrypt.CompareHashAndPassword`.

### Task 6.2: Remove dead code `settings_repo.go`

**File:** `backend/internal/adapter/repository/mysql/settings_repo.go` — DELETE
Remove from `main.go` if imported.

---

## Execution Order

```
Phase 1 (quick fixes, no dependencies):
  └─ Task 1.4 (timeout)
  └─ Task 3.1, 3.2, 3.4 (frontend types)
  └─ Task 6.2 (dead code removal)

Phase 2 (Go↔Python bridge):
  └─ Task 1.1 (Go sends absolute_mode + declared_goal)
  └─ Task 1.2 (Go reads scores+friction)
  └─ Task 1.3 (Python topic filtering)

Phase 3 (Fatigue pipeline):
  └─ Task 2.1 (Frontend telemetry)
  └─ Task 2.2 (Frontend friction UI)

Phase 4 (Advanced features):
  └─ Task 4.1 (Thompson sampling)
  └─ Task 5.1 (Real safety models support)

Phase 5 (Security):
  └─ Task 6.1 (bcrypt)
  └─ Task 3.3 (ContentCard feedback)
```

## Verification

1. `cd recommender && python -m pytest src/ -v` → all tests pass
2. `cd backend && go test ./...` → all tests pass
3. `cd frontend && npm run check` → TypeScript clean
4. Manual: Start all 3 services → feed returns scores + friction_level → absolute mode filters content
5. Manual: Scroll feed for 60s → Python `/fatigue/telemetry` receives data

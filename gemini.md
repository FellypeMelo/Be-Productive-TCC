# 🧠 Be-Productive (Fluxo) — Gemini CLI Agent Context

> This file defines the operational contract for the Gemini CLI code agent working on Fluxo.

---

# 0️⃣ Agent Operating Rules

## 🔎 Source of Truth

1. `@docs/` contains system documentation.
2. If conflict exists:

   * `@docs` overrides this file.
3. If documentation is unclear:

   * Infer from architecture invariants.
4. Never invent architecture patterns not defined here or in `@docs`.

---

## 🧱 Non-Negotiable Invariants

The system MUST:

* Always return JSON responses
* Work even if AI service is offline
* Never panic on context extraction
* Preserve Clean Architecture boundaries
* Maintain API versioning discipline
* Avoid introducing new frameworks without justification

---

# 1️⃣ System Architecture

## Microservices-Lite

```
Frontend (SvelteKit)
        ↓
Backend API (Go)
        ↓
MySQL

Backend → Recommender (Python, read-only DB)
```

## Responsibilities

### Frontend

* Rendering
* Session persistence
* API communication
* No business logic

### Backend (Go)

* Business logic
* Auth
* Feed orchestration
* Fallback handling
* Owns API contract

### Recommender (Python)

* Ranking only
* Read-only DB access
* No writes
* No auth logic

### Database

* Persistence only
* No derived logic

---

# 2️⃣ Backend Rules (Go)

Directory: `backend/internal`

## Architecture Pattern (Strict)

```
handler → service → repository
```

### Enforcement Rules

* Handlers must not access DB directly.
* Services must not contain HTTP logic.
* Repositories must not contain business logic.
* No cross-layer imports.

---

## Feed Resilience Contract

When generating feed:

1. Call recommender.
2. If:

   * Error
   * Timeout
   * Empty result
3. Fallback to `repo.GetFeed`.

Example logic pattern:

```go
feed, err := recommender.Get(userID)
if err != nil || len(feed) == 0 {
    log.Println("Fallback to DB feed")
    return repo.GetFeed(userID)
}
```

Agent Rule:

> Never remove fallback logic.

---

## Context Extraction (Mandatory Pattern)

Always use comma-ok idiom.

```go
userID, ok := r.Context().Value("user_id").(int64)
if !ok {
    respondError(w, http.StatusUnauthorized, "invalid user")
    return
}
```

Never use direct assertion.

---

## Error Response Contract

All API errors must return:

```json
{
  "success": false,
  "error": "message"
}
```

No plain text responses.

---

# 3️⃣ Frontend Rules (SvelteKit)

Directory: `frontend/src`

## State Management

* Use Svelte `writable` stores only.
* Do NOT introduce Redux/Zustand.
* Persist auth in `localStorage`.

---

## API Layer

File: `lib/api.ts`

Responsibilities:

* Inject `Authorization: Bearer`
* Handle 401 globally
* Avoid redirect loops

Rule:
If already on auth route → do not redirect on 401.

---

# 4️⃣ Recommender Rules (Python)

Directory: `recommender/src`

## Ranking Pipeline

1. Candidate fetch (bounded query only)
2. Score computation:

   * Collaborative signal
   * Content-based signal
3. Well-being modifier

Example:

```
if emotional_state == "ESTRESSADO":
    relaxing_score *= 1.2
```

Constraint:
Well-being may rebalance but must not completely override relevance ranking.

---

# 5️⃣ Code Quality Constraints

## Function Design

* Target < 30 lines
* Max 3 nesting levels
* Prefer early return

## Naming

* Go: CamelCase / mixedCase
* JS/TS: camelCase
* Python: snake_case

---

# 6️⃣ Performance Directives

## Required Indexes

Ensure existence of:

* `content(category)`
* `content(author_id)`
* `community_members(user_id)`

---

## Caching Strategy (When Implemented)

* Redis for feed caching
* TTL default: 5 minutes
* Never cache per-user sensitive auth data

---

# 7️⃣ API Versioning

Current version: `/api/v1/`

Rules:

* No breaking changes inside same version.
* Breaking change → create `/api/v2/`
* Prefer additive evolution.

---

# 8️⃣ Containerization Roadmap

Each service must have:

* Dockerfile
* Environment-based config
* No hardcoded credentials

`docker-compose.yml` orchestrates:

* Backend
* Frontend
* Recommender
* MySQL

---

# 9️⃣ Agent Behavior Guidelines

When modifying code:

1. Read related files fully.
2. Respect architectural boundaries.
3. Preserve invariants.
4. Avoid speculative refactors.
5. Do not introduce new dependencies unless necessary.
6. Check if `@docs` defines the feature before implementing.

When uncertain:

* Choose simplest deterministic solution.
* Preserve backward compatibility.

---

# 🔟 Definition of Done (Agent Checklist)

Before finishing a task:

* Backend builds (`go build`)
* No architectural boundary violations
* Fallback logic intact
* JSON error format respected
* No added unnecessary complexity
* No business logic moved to frontend

---

# 🧠 Product Alignment Reminder

Fluxo optimizes for:

* Quality of attention
* Emotional stability
* Sustainable usage patterns

The agent must not introduce:

* Infinite scroll without limit
* Addictive notification loops
* Engagement-maximizing dark patterns

---

*Maintained by Antigravity Agent*
*Optimized for Gemini CLI Code Agent*
*Last Updated: 2026-02-14*

---

### What Changed for Gemini Optimization

* Removed narrative language
* Added deterministic directives
* Added explicit agent behavior section
* Strengthened invariants
* Made fallback and boundaries machine-clear
* Added doc-precedence rule
* Reduced ambiguity in responsibilities

---
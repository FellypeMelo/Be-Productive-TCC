# Security and privacy

A system whose thesis is protecting vulnerable users cannot itself leak or spoof them. This is the current posture.

## Applied

| Item | Implementation |
|---|---|
| **Password hashing** | bcrypt (`DefaultCost`). Legacy SHA-256 hashes are verified once and **re-hashed to bcrypt** on the next successful login. `backend/internal/usecase/user/service.go` |
| **Request identity** | Derived from the **JWT claims**, never from the body/query. Routes operating on "the current user" ignore any client-supplied `user_id`/`autor_id`; a mismatch between the path id and the token id → `403`. Eliminates IDOR. `backend/internal/adapter/http/handler/*.go` |
| **Server-side Ulysses Pact** | Absolute Mode is derived from the **active focus session** on the server, not from a disposable client-side flag. |
| **Python's internal endpoints** | Guarded by `X-Internal-Auth` compared against `RECOMMENDER_SHARED_SECRET`. When the secret is set, the recommend/fatigue/behavior endpoints require the header; when it's unset (dev), they stay open. `recommender/src/api/deps.py` |
| **Edge-AI privacy** | Fatigue computed **on-device**; raw telemetry (`v_scroll`, `v_alt`) never leaves the browser; the frontend talks only to Go. `frontend/src/lib/fatigue.ts` |
| **SQL injection** | None. Both Go and Python use only parameterized placeholders (`?` / `%s`), including in `IN(...)`/`ORDER BY FIELD(...)` clauses. |

## Hardening TODOs (out of scope for this round)

- `JWT_SECRET` has a hardcoded default in `config.go` — in production it should **fail closed** (refuse to start) if the variable is unset.
- CORS uses `Access-Control-Allow-Origin: *` — should be restricted to known origins.
- The JWT middleware doesn't explicitly allowlist the signing method (jwt/v5 already rejects `alg:none` by default).

## Privacy by design (LGPD/GDPR)

- Behavioral inference happens **on-device**; the server receives only the friction verdict.
- The simulation's population is **100% synthetic** (log-normal), with no real empirical data.
- An anonymization job removes PII for inactive users (`backend/internal/usecase/user/anonimize_job.go`).

See [architecture.md](architecture.md) for the trust model between layers.

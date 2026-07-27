# Paper ↔ Code Truth Map

Traceability between each claim of the paper *"Arquitetura Algorítmica para Atenção
Sustentável: O Modelo Be-Productive"* (DOI 10.70773/revistatopicos/781363235) and the
point in the code that makes it true. Generated after the 2026-07-09 coherence pass.

> Guiding principle: **what the paper claims, the code must do** — and where the paper
> needs to change, the text should describe what the code actually does.

## Mathematical core

| Paper claim | Truth in the code | File |
|---|---|---|
| Bi-kernel Hawkes process (Eq. 2), summed over past events | Real intensity `μ + Σ α₁e^{−β₁(t−t_k)} + Σ α₂e^{−β₂(t−t_m)}`; events labeled S1/S2 by latency | `recommender/src/domain/math_models.py::hawkes_intensity`, `src/inference/hawkes_classifier.py` |
| Ego-Depletion ODE (Eq. 4) | `dR/dt = μ_rest(R_max−R) − (k₁v_scroll + k₂v_alt)` | `recommender/src/domain/math_models.py::calculate_ego_depletion` |
| Min-Norm multi-objective filtering (Eq. 3) | `Q = base × min_m(1−P_m)`; **exercised** in the validation's content selection | `recommender/src/domain/math_models.py::calculate_quality_score`, `src/abm/engine.py` |
| Thompson Sampling | Beta posteriors that **update** with observed reward (no longer constants) | `recommender/src/inference/thompson.py` |

## Empirical validation (ABM)

| Paper claim | Truth in the code | File |
|---|---|---|
| Cohen's d = 3.25 (Fig. 1) | Reproduced by a **fair, seeded** run (equal μ_rest across both arms; endogenous load) | `recommender/src/abm/engine.py`, `abm_results/statistical_proof.md` |
| p < 10⁻³⁰⁰ (Mann-Whitney U) | p = 3.8×10⁻²⁹⁵, real test | `recommender/src/abm/stats.py` |
| Compressed KL divergence (Fig. 2) | Median KL 0.87 → 0.21, **actually computed** intent × consumption | `src/abm/run_simulation.py::plot_kl_divergence` |
| Green robustness manifold (Fig. 3) | Positive delta across the entire grid (scroll×k1) | `src/abm/sensitivity.py` |
| — (new, honesty) | **Ablation**: friction d=2.57, min-norm +0.35, steering compresses KL; **sanity check** (everything off) → d≈0.02 | `abm_results/statistical_proof.md` |
| N=1000, T=60, reproducible | Both numpy **and** the random module's seeds fixed; the test reproduces d=3.25 | `src/abm/tests/test_fair_validation.py` |

## Architecture & privacy

| Paper claim | Truth in the code | File |
|---|---|---|
| **Edge AI**: fatigue inference strictly on-device | ODE + Hawkes run **in the browser**; raw telemetry never leaves the device | `frontend/src/lib/fatigue.ts` |
| Server receives only orders/signals | Frontend talks **only to Go**; `RECOMMENDER_URL` removed; no upload of `v_scroll`/`v_alt` | `frontend/src/lib/api.ts` |
| Positive friction (Algorithm 3) when reserve is depleted | Level derived locally from `R/R_max`; **fail-closed**; blocking requires deliberate confirmation | `frontend/src/routes/feed/+page.svelte` |
| Ulysses Pact (goal set in a lucid state, then locked) | Absolute Mode **derived from the active focus session** on the server, not from a per-request flag | `backend/internal/usecase/content/service.go`, `adapter/repository/mysql/focus_repo.go` |

## Security (not a paper claim, but a requirement for a protection system)

| Item | Truth in the code | File |
|---|---|---|
| Password hashing | **bcrypt** (transparent upgrade from legacy SHA-256 on login) | `backend/internal/usecase/user/service.go` |
| Request identity | Derived from the **JWT**, not the body/query (IDOR-safe; 403 on mismatch) | `backend/internal/adapter/http/handler/*.go` |
| Python's internal endpoints | Guarded by `X-Internal-Auth` (`RECOMMENDER_SHARED_SECRET`) | `recommender/src/api/deps.py` |

## Known gaps (transparency)

- Safety classifiers and the hybrid score are **documented deterministic stand-ins**, not real trained/ONNX models — reproducible and honestly labeled, ready for replacement.
- The **published text** (Methodology section) still describes the earlier design; aligning the text (a corrigendum) is a decision for the authors.
- A hardcoded default `JWT_SECRET` and wildcard CORS remain as hardening items (Tier 1) outside the scope of this round, except for the bcrypt/IDOR fixes already applied.

# Evolution roadmap — from prototype to the paper's vision

A plan of improvements organized around the paper's thesis: **turning recommender systems from predators of attention into guardians of cognitive reserve.** Each phase moves the implementation closer to the idealized model and addresses the limitations the paper itself acknowledges (in-vivo validation, real classifiers, business models).

Status legend: ✅ done · 🟡 partial · ⬜ planned.

## Where we stand today

| Paper pillar | Status |
|---|---|
| Confound-free ABM reproducing d = 3.25 | ✅ |
| Real Hawkes process, Thompson with updating posterior, Min-Norm exercised | ✅ |
| On-device Edge AI (ODE + Hawkes in the browser) | ✅ |
| Ulysses Pact enforced server-side | ✅ |
| Baseline security (bcrypt, no IDOR, internal auth) | ✅ |
| Safety classifiers / hybrid recommender | 🟡 observable lexical/ranking baselines; trained models pending |
| Validation with real users | ⬜ |

---

## Phase 1 — From stand-ins to real models
*Goal: Min-Norm and `base_score` operating on learned signal, not heuristics.*

- 🟡 **Real safety classifiers (IA_Safety, Eq. 3).** The ID hash is gone; an auditable five-dimensional lexical baseline analyzes actual text. Train and validate ONNX models before replacing it.
- 🟡 **Trained hybrid recommender.** Runtime ranking now uses observable interaction and content features. Fit TF-IDF/ALS on real data before enabling learned components.
- ⬜ **Hawkes estimation via MLE.** Fit α/β for both kernels from real event trajectories, instead of fixed constants.
- ⬜ **Per-user fatigue calibration.** Learn individual `μ_rest`, `k1`, `k2` from observed behavior (with consent), synced through the existing Edge endpoints.

## Phase 2 — Edge AI maturity
*Goal: fully deliver on "strictly on-device inference."*

- ⬜ **On-device inference via WASM/ONNX Runtime Web / TF.js** for the safety classifiers, not just the ODE/Hawkes.
- ⬜ **Local persistence** of reserve `R(t)` and its parameters (IndexedDB) for continuity across sessions, without a server round-trip.
- ⬜ **Offline-first / PWA** with a service worker; the server receives only friction verdicts.
- ⬜ **Full sensory friction**: progressive desaturation, real scroll deceleration, and exclusive ranking of dense content when `R` drops (today: desaturation + a blocking gate).

## Phase 3 — In-vivo empirical validation *(the paper's main declared limitation)*
*Goal: move from the simulated environment to real users.*

- ⬜ **Longitudinal study** with opt-in volunteers, ethics/IRB approval, control group vs. Be-Productive.
- ⬜ **Metrics beyond screen time**: wellbeing (validated scales), cognitive relapse, acceptance of the friction, retention of declared intent (real KL).
- ⬜ **Anonymous, aggregated telemetry instrumentation** (under consent) that preserves the on-device principle.
- ⬜ **Pre-registration** of the experimental design and publication of the data/`abm` as reproducible material.

## Phase 4 — Sustainability and compliance *(discussed in the paper)*
*Goal: make viable a system that, by design, reduces usage time.*

- ⬜ **Non-extractive business models**: premium subscription, B2B productivity licensing, licensing to educational/health institutions.
- ⬜ **Regulatory compliance**: algorithmic transparency and risk mitigation aligned with the Digital Services Act (DSA) and LGPD; an "algorithmic nutrition" report.
- ⬜ **Transparency dashboard** for the user: why an item was demoted (which `P_m` triggered Min-Norm), reserve state, friction history.

## Phase 5 — Production hardening
*Goal: a protection system that doesn't compromise itself.*

- ⬜ **Fail-closed `JWT_SECRET`** (refuse to start without a secret); signing-method allowlist.
- ⬜ CORS restricted to known origins; rate limiting; security headers.
- 🟡 Structured logs, metrics, request correlation, readiness, and three-layer CI are implemented. Distributed tracing remains planned.
- ⬜ Migrate anonymization to use real `last_active` (today it uses `updated_at`) and cascade across behavioral rows.

## Phase 6 — Research extensions
*Goal: deepen the Value-Aligned RecSys.*

- ⬜ **Contextual bandits** replacing the 2-arm Thompson Sampling with context-sensitive selection (time of day, history, fatigue state).
- ⬜ **Explicit Pareto multi-objective optimization** between engagement, intent alignment, and cognitive reserve.
- ⬜ **Off-policy causal evaluation** (IPS/doubly-robust) to estimate effect without a disruptive A/B test.
- ⬜ **Additional ablations** and expanded sensitivity analysis in the ABM (more vulnerability axes).

## Cross-cutting (ongoing)

- ⬜ **Accessibility** (WCAG AA), i18n (PT/EN), a real light/dark theme.
- ⬜ **Frontend test runner** (Vitest already present) with component coverage; expanded Playwright E2E.
- ⬜ **Living documentation**: keep [architecture](architecture.md), [reproducibility](reproducibility.md), [security](security.md), and [paper-code-truth-map](paper-code-truth-map.md) in sync with every structural change.

---

### Prioritization principle

Whenever there is a conflict, the priority order follows the paper's thesis: **preserve the user's agency and cognitive reserve > alignment with declared intent > technical efficiency > engagement**. No improvement should invert this hierarchy.

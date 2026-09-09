# SPEC-AB-001 — Robust A/B test for sustainable attention

**Status:** implementation-ready proposal  
**Version:** 1.0  
**Scope:** consented real-user experiment, separate from the ABM  
**Principle:** agency and cognitive reserve > declared intent > efficiency > engagement

## 1. Objective

Measure, with causal validity and privacy protection, whether Be-Productive improves declared-intent retention and preserves cognitive reserve compared with a control ranking.

The experiment must answer three separate questions:

1. Does treatment preserve more reserve over time?
2. Does consumed content remain better aligned with declared intent?
3. Is the protection accepted without increasing abandonment, frustration, or unsafe-content exposure?

The ABM (`N=1000`, `T=60`) is a mechanism and instrumentation validation, not a real-user effect estimate.

## 2. Current-state diagnosis

The repository already has stable `control`/`treatment` assignment, experiment metadata, exposure-like product events, offline ranking metrics, a confound-free ABM, and on-device fatigue inference.

It is not yet a complete real-world A/B test. `ranking-v2` currently applies the online variant mainly to ranking diversification; the online test is not automatically the same comparison as the ABM's baseline-versus-sustainable arms. Product personalization consent must also be separated from research consent.

## 3. Arms

### Control

The standard production ranking, with mandatory safety, quality, availability, authentication, accessibility, and legal protections. It must not deliberately expose unsafe content.

### Treatment

The same control ranking plus one immutable, versioned sustainable-attention package: declared-intent alignment, quality/depth priority, bounded diversity, safety Min-Norm, protective mode from the local binary order, dense content during impulsive states, positive friction, and user-selected Ulysses Pact.

### Invalid comparisons

Do not mix a package-level claim with an isolated diversity effect. Do not change visual, safety, or ranking behavior during a run without creating a new experiment version.

## 4. Eligibility and consent

Eligibility requires an authenticated active account, approved region/age cohort, explicit research consent, any separate consent required for aggregated wellbeing metrics, no incompatible concurrent experiment, and a device capable of the local inference path.

Declining must not degrade the product. The experiment must not infer a diagnosis or clinical vulnerability.

## 5. Randomization and isolation

Randomize by `user_id`, not by session or impression. Use a versioned stable hash equivalent to `SHA-256(experiment_name + salt + user_id)`, and preserve the same assignment for the whole run. Record the salt, allocation rule, dates, experiment ID, assignment version, request ID, and variant.

Ramp by user: 5%, 25%, then 50/50 after safety gates. Mark fallbacks, emergency windows, tests, duplicate accounts, and users with no valid exposure so they cannot contaminate the primary analysis.

## 6. Exposure contract

Every eligible feed response must create an idempotent exposure record for both arms, independently from commercial personalization consent. It should include event ID, experiment ID, variant, assignment version, algorithm version, request ID, internal user ID, eligibility, served/fallback flags, position count, and UTC timestamp.

It must never include raw scroll, context switches, reserve, friction, typed text, or browsing history.

## 7. Metrics

The primary metric is normalized seven-day reserve AUC per user, calculated on-device. Only an explicitly consented, bounded aggregate may leave the device; raw reserve time series remain local. If that summary is not ethically approved, use declared-intent retention as the primary metric and keep reserve as a local protection metric.

Secondary metrics include intent/consumption KL divergence, voluntary focus-session completion, friction acceptance, explicit quality feedback, catalog coverage/diversity, and time to first deliberate action. Screen time and clicks are diagnostic only, never the primary objective.

Guardrails cover safety reports, critical blocks, errors, latency, immediate abandonment, negative feedback, accessibility, support volume, repetitive/unsafe/off-intent exposure, and pre-specified subgroup harm.

## 8. Power and analysis

Pre-register bilateral `alpha=0.05`, at least 80% power (preferably 90%), a plausible minimum detectable effect, expected loss/non-exposure, repeated-user correlation, and multiplicity handling. Do not power the real-user test from the ABM's `Cohen's d = 3.25`; start with a small plausible effect such as `d=0.20` and run a blinded pilot.

Use intention-to-treat as primary, user as the inference unit, a 95% confidence interval, repeated-user-robust estimation, pre-specified strata only, and report null results. Sequential looks require an alpha-spending rule. Secondary/subgroup analyses must be pre-registered or labeled exploratory.

## 9. Privacy and rollout

The required data flow is:

```text
scroll/context → local EdgeFatigueEngine → binary order → protected feed
```

No raw fatigue telemetry may reach the server. Network failure must preserve protection rather than silently falling back to an unrestricted feed.

Before launch, require a versioned manifesto, SRM/balance tests, privacy review, rollback test, and reproducible fixtures. Then run shadow, 5%, 25%, and 50/50 stages. Rollback immediately for critical safety, privacy, availability, or guardrail failures; retain data and mark the reason instead of deleting the window.

## 10. Acceptance criteria

1. Each eligible user receives exactly one stable variant.
2. Assignment passes the pre-specified sample-ratio-mismatch test.
3. No non-consenting user enters the analysis.
4. Exposure events contain no raw fatigue telemetry.
5. Control and treatment exposures are recorded when research consent exists, regardless of commercial personalization.
6. Fallback, emergency, and test traffic are identifiable.
7. Treatment can be disabled by configuration.
8. Every guardrail has a threshold, owner, and rollback action.
9. The final report is reproducible from the immutable manifesto and extract.
10. No ABM number is presented as a real-user effect.

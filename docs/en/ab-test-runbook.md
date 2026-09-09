# Operational runbook — sustainable-attention-v1

This runbook operates the implementation without turning ABM results into efficacy claims.

## Before exposure

1. Review and freeze `recommender/experiment_manifest.sustainable-attention-v1.json` and the algorithm version.
2. Confirm protocol, consent language, eligibility, owner, and power plan outside the code.
3. Set `EXPERIMENT_ROLLOUT` in the recommender container to `0.05`, `0.25`, or `0.50`.
4. Rebuild the service and record the image digest. Assignment is per user and does not move during ramp-up.

## Monitoring and rollback

Use `experimento_exposicao` as the valid exposure source; `event_id` makes writes idempotent. Run the aggregate-only ITT report with `python -m src.evaluation.ab_report`. Stop a window for SRM (`p < 0.001`), critical errors, safety, accessibility, or retention guardrails. Set `EXPERIMENT_ROLLOUT=0` for rollback and retain existing exposures for audit.

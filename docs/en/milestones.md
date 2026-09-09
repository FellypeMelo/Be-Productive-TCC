# Ten-milestone implementation

The executable engineering scope now covers all ten milestones:

1. Offline ranking metrics and reproducible evaluation fixture.
2. Production secrets, restricted CORS, rate limits, body limits and timeouts.
3. Versioned feed/event contracts, request correlation and model metadata.
4. Idempotent, consent-aware interaction events.
5. Observable ranking using affinity, quality, recency, feedback, repetition and bounded exploration.
6. Consent-aware on-device fatigue monitoring with local continuity.
7. Auditable text safety baseline with Min-Norm penalty and blocking.
8. Stable user-level experiment assignment recorded with events.
9. Structured logs, metrics, readiness and fallback reporting.
10. Three-layer CI, containers, Compose and migration ledger.

```bash
cd recommender
python -m src.evaluation.run --input evaluation_fixture.example.json --k 3
docker compose up --build
```

External evidence remains separate. Trained safety needs labeled data and evaluation. Causal claims need consented users, ethics review and a pre-registered study.

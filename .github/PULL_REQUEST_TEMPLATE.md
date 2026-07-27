## Summary

<!-- What does this PR do, and why? One or two sentences. -->

## Layer(s) touched

- [ ] Backend (Go, `backend/`)
- [ ] Recommender (Python, `recommender/`)
- [ ] Frontend (SvelteKit, `frontend/`)
- [ ] Database migrations (`backend/migrations/`)
- [ ] Documentation only

## Testing

There is no CI in this repository — paste the actual output of the suite(s) relevant to your change.

- [ ] `cd backend && go test ./...`
- [ ] `cd recommender && python -m pytest src/ -q`
- [ ] `cd frontend && npm run test`
- [ ] `cd frontend && npm run check`
- [ ] `cd frontend && npx playwright test` (only if you changed frontend behavior touching auth/feed/focus flows, and you ran the full stack locally)

```
<!-- paste command output here -->
```

## If this touches the math or the ABM (`recommender/src/domain`, `recommender/src/abm`)

- [ ] I updated `docs/en/paper-code-truth-map.md` (and its `docs/pt-BR/` mirror) to reflect the change.
- [ ] I re-ran `python -m src.abm.run_simulation` and checked whether `recommender/abm_results/statistical_proof.md` changed materially (paste the before/after Cohen's d if it did).

## Checklist

- [ ] I read `CONTRIBUTING.md`.
- [ ] This PR is scoped to one concern (not an unrelated bundle of changes).
- [ ] I did not add a LICENSE file or change licensing terms (see `README.md#license` — that's the author's decision, not a PR's).

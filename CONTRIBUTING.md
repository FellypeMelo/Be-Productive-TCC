# Contributing to Be-Productive

Thanks for considering a contribution. This is an academic capstone project (TCC) reproducing a published, peer-reviewed paper, so accuracy and traceability matter as much as code quality — please read [`docs/en/paper-code-truth-map.md`](docs/en/paper-code-truth-map.md) before touching anything under `recommender/src/domain` or `recommender/src/abm`.

## Before you start

- Skim [`README.md`](README.md) for the architecture and the three-tier trust boundary (frontend → Go → Python, never frontend → Python directly).
- Skim [`CLAUDE.md`](CLAUDE.md) for the layer-by-layer structure, data flow, and the project's own list of known shortcuts (deterministic safety classifiers, unfitted hybrid recommender, etc.) — don't "fix" those silently; see [`docs/en/roadmap.md`](docs/en/roadmap.md) first, they are usually intentional and documented.
- CI runs all three layer gates. Run the relevant suite locally before opening a pull request for faster feedback.

## Project layout

```
backend/       Go API gateway (Clean Architecture: domain / usecase / adapter / infrastructure)
frontend/      SvelteKit + TypeScript UI, including on-device fatigue inference
recommender/   Python FastAPI scoring service + standalone ABM research module
docs/          Internal architecture/security/reproducibility/roadmap docs (docs/en + docs/pt-BR)
```

## Development setup

See the [Quickstart](README.md#quickstart) section of the root README for verified, working setup commands per layer.

## Running the tests

| Layer | Command |
|---|---|
| Go backend | `cd backend && go test ./...` |
| Python recommender | `cd recommender && python -m pytest src/ -q` |
| Frontend (unit) | `cd frontend && npm run test` |
| Frontend (types) | `cd frontend && npm run check` |
| Frontend (E2E) | `cd frontend && npx playwright test` (requires MySQL + all three services running) |

A pull request that changes behavior in a given layer should include or update tests in that layer, and you should have run that layer's suite locally and confirmed it passes before opening the PR.

## Code conventions

- **Go**: standard `gofmt` formatting; Clean Architecture layering is enforced by convention, not tooling — `domain` must never import `infrastructure` or HTTP packages; `usecase` defines interfaces that `adapter` implements.
- **Python**: no linter/formatter config is currently checked into the repo; match the existing style in the file you're editing (type hints, docstrings on public functions).
- **TypeScript/Svelte**: run `npm run check` (svelte-check) before submitting; no ESLint/Prettier config is currently checked in either, so again, match surrounding style.
- Keep the math (`recommender/src/domain/math_models.py`) and its docstrings aligned with the paper's equation numbers (Eq. 2, Eq. 3, Eq. 4, Eq. 5, Algorithm 3) — if you change the math, update [`docs/en/paper-code-truth-map.md`](docs/en/paper-code-truth-map.md) (and its `docs/pt-BR/` mirror) in the same PR.

## Commit messages

The existing history mostly follows a `type(scope): summary` convention (`feat`, `fix`, `test`, `docs`, `chore`, `security`, `merge`), e.g. `feat(backend): bcrypt, JWT-derived identity (IDOR fix)`. Please follow the same pattern.

## Documentation & the ABM statistical result

If a change touches `recommender/src/abm/`, regenerate and re-check the statistical proof before submitting:

```bash
cd recommender
python -m src.abm.run_simulation
```

This overwrites `recommender/abm_results/statistical_proof.md` and the three `fig_*.png` files. Include the resulting diff in your PR description so reviewers can see whether the headline effect size changed.

## Pull requests

- Open the PR against `main` and fill in the PR template.
- Describe what you tested and how (paste the relevant command output).
- Keep PRs scoped to one layer or one concern where possible — this makes the traceability work in `docs/en/paper-code-truth-map.md` (and its `docs/pt-BR/` mirror) easier to maintain.

## Licensing note for contributors

This repository currently has **no LICENSE file** — see the [License](README.md#license) section of the root README. Until the author formally declares a license, submitting a contribution does not itself grant you or anyone else redistribution rights beyond what the author explicitly agrees to for that contribution. If this matters to you, ask before investing significant effort.

## Reporting bugs or requesting features

Please use the issue templates (Bug report / Feature request) rather than an unstructured issue — they ask for the information (layer affected, reproduction steps, expected vs. actual) that's usually needed to act on a report.

## Reporting a security vulnerability

Do **not** open a public issue for security vulnerabilities. See [`SECURITY.md`](SECURITY.md).

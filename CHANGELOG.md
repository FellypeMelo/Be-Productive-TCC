# Changelog

All notable changes to this project are documented in this file.

The format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project has **no tagged releases** as of this writing, so there is no `[X.Y.Z]` version history yet — everything below is grouped under `[Unreleased]` and reconstructed from the real commit history (`git log`, 37 commits between 2026-02-14 and 2026-07-09 on `main`, plus this documentation pass). Entries are grouped by theme, not by individual commit, and are not tied to invented version numbers or release dates.

## [Unreleased]

### Added

- Initial three-tier scaffold: Go API gateway, SvelteKit frontend, Python FastAPI recommender, with database seeding and mock data generation.
- Value-aligned recommender system: Agent-Based Simulation (ABM), Ego-Depletion model, safety-aware scoring.
- Hawkes dual-kernel scoring (paper Eq. 2).
- Continuous Ego-Depletion ODE loop with four friction levels (Algorithm 3 / Eq. 4).
- Hyperbolic discounting (Eq. 5) plus its API endpoint.
- Friction UI and client-side telemetry on the frontend.
- Full test suites across all three layers: Go unit tests for domain entities, content/focus/user/community services, and HTTP handlers; Python tests for API routes, use cases, and edge cases; Vitest unit tests for the API client and friction logic; a Playwright E2E suite covering auth, feed, and focus flows.
- A rich pt-BR mock dataset across all database tables.
- A phased evolution roadmap document (originally `Docs/ROADMAP.md`, now `docs/pt-BR/roadmap.md`).
- This documentation pass: English `README.md` (with a pt-BR mirror), `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, this `CHANGELOG.md`, and GitHub issue/PR templates.
- A bilingual internal-docs restructure: the former `Docs/` folder became `docs/en/` (authored English translations) and `docs/pt-BR/` (the original Portuguese content, relocated via `git mv`), with a `docs/README.md` language index.

### Changed

- Responsive frontend redesign on a new design system.
- Repository restructured and internal documentation overhauled (originally the `Docs/` folder).
- Fatigue inference moved on-device (Edge AI): the Ego-Depletion ODE and Hawkes process now run in the browser, and raw scroll/interaction telemetry is no longer uploaded to the server.
- Recommender scoring made deterministic and honestly documented (explicit stand-in safety classifiers instead of silent defaults), plus an internal shared-secret guard and a real health probe.
- The Agent-Based Simulation was rebuilt as a confound-free, fair experiment (equal recovery rate across arms, endogenous load).

### Fixed

- The feed endpoint now returns the recommender's real scores instead of a hardcoded `nil`.
- `CLAUDE.md`'s claim that the frontend has "no test runner configured" was corrected — Vitest and two real test files exist and pass.

### Security

- Passwords are now hashed with bcrypt instead of SHA-256; legacy SHA-256 hashes are verified once and transparently re-hashed on next login.
- The acting user is now derived from JWT claims rather than request bodies/query parameters (fixes an IDOR-shaped class of bug).
- The Ulysses Pact / Absolute Mode is enforced server-side from the active focus session, not from a client-controlled flag.
- Updated vulnerable frontend dependencies (Vite / SvelteKit / Rollup).

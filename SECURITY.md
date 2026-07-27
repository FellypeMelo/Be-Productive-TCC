# Security Policy

## Reporting a vulnerability

Please report security vulnerabilities through **GitHub's private vulnerability reporting**, not through a public issue:

1. Go to the repository's Security tab: <https://github.com/FellypeMelo/Be-Productive-TCC/security>
2. Click "Report a vulnerability" (or use the direct link: <https://github.com/FellypeMelo/Be-Productive-TCC/security/advisories/new>) to open a private draft security advisory.
3. Describe the issue, the affected layer (Go backend / Python recommender / SvelteKit frontend), and, if possible, steps to reproduce.

This opens a private conversation with the repository owner and avoids exposing the issue publicly before a fix is available.

Do not email an address you found elsewhere for this repository — none is published in this project, and GitHub Security Advisories is the only channel this policy asks you to use.

## Scope

Be-Productive is an **academic capstone (TCC) prototype**, the reference implementation of a peer-reviewed paper (see [`README.md`](README.md)). It is a three-service local application (SvelteKit frontend, Go API gateway, Python FastAPI recommender, MySQL) intended for research, coursework, and demonstration. It has not been hardened or audited for production use with real user data.

In scope for a report:

- Authentication/authorization bypasses (JWT handling, IDOR-style access to other users' data)
- Injection issues (SQL, or otherwise) in the Go or Python layers
- Server-side enforcement gaps (e.g., a way to defeat the Ulysses Pact / Absolute Mode from the client)
- Secrets or credentials committed to the repository

Out of scope / already known and tracked (not new findings):

- The deterministic, hash-based safety classifiers are documented stand-ins, not trained models — see `CLAUDE.md` and [`docs/en/roadmap.md`](docs/en/roadmap.md).
- `RECOMMENDER_SHARED_SECRET` being unset leaves the recommender's internal endpoints open — this is a documented local-dev default, not a hidden behavior; see [`docs/en/security.md`](docs/en/security.md) for the full current security posture and its known hardening TODOs (e.g., default `JWT_SECRET`, permissive CORS).

## Supported versions

This repository has no tagged releases. All fixes land on `main`; there is no maintained branch or backport policy for older commits.

## Disclosure

There is no fixed SLA for a project maintained by a single academic author. If you don't hear back within a reasonable time through the GitHub Security Advisory flow, it's fine to follow up on the same advisory thread.

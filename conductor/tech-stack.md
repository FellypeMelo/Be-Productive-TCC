# Technology Stack: Be-Productive (Fluxo)

## Core Languages
- **Go (1.21+):** Primary language for the Backend API, chosen for its performance and concurrency support.
- **TypeScript:** Used for the Frontend to ensure type safety and improved developer experience.
- **Python (3.11+):** Powering the Recommender service, leveraging its strong AI/ML ecosystem.

## Frameworks & Libraries
- **Frontend:** [SvelteKit](https://kit.svelte.dev/) for a fast, reactive user interface and optimized server-side rendering.
- **Backend API:** Custom Go implementation following Clean Architecture principles (Handler -> Usecase -> Repository).
- **Recommender:** [FastAPI](https://fastapi.tiangolo.com/) for building high-performance, asynchronous recommendation endpoints.
- **ML/Inference:** scikit-learn and related Python libraries for ethical ranking algorithms.

## Data Persistence
- **MySQL (8.0+):** Relational database for storing user data, content, and focus session records.

## Infrastructure & Tooling
- **Environment:** Local development using Node.js 18+, Go 1.21+, and Python 3.11+.
- **Git:** Version control for the monorepo.
- **CI/CD:** Targeted for high quality with mandatory TDD and coverage checks.

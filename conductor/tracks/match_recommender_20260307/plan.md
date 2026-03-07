# Implementation Plan: Match The New Recommender Algorithm with BackEnd and FrontEnd

## Phase 1: Recommender Refinement (Python)
- [ ] Task: RED - Define mental health metrics tests in Recommender
    - [ ] Create `recommender/tests/test_wellbeing_metrics.py` with failing test cases for new scoring.
- [ ] Task: GREEN - Implement wellbeing scoring in `recommender/src/domain/metrics.py`
- [ ] Task: REFACTOR - Optimize Python ranking pipeline
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Recommender Refinement (Python)' (Protocol in workflow.md)

## Phase 2: Backend API Integration (Go)
- [ ] Task: RED - Create test for well-being feed fallback in Backend
    - [ ] Implement `backend/internal/usecase/content/feed_test.go` verifying fallback logic.
- [ ] Task: GREEN - Update Feed Usecase to handle new Recommender signals
- [ ] Task: REFACTOR - Clean up Go service layer dependencies
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Backend API Integration (Go)' (Protocol in workflow.md)

## Phase 3: Frontend UI Update (SvelteKit)
- [ ] Task: RED - Write unit tests for enhanced Feed cards
- [ ] Task: GREEN - Update Feed components to display well-being attributes
- [ ] Task: REFACTOR - Simplify Svelte store usage for feed data
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Frontend UI Update (SvelteKit)' (Protocol in workflow.md)

# Be-Productive (Fluxo): AI-XP Workflow

This workflow implements **AI-XP (Artificially Intelligent eXtreme Programming)**, combining Conductor's task management with strict engineering rigor.

## 📜 Guiding Principles (Non-Negotiable)

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`.
2. **Mandatory TDD (Red-Green-Refactor):** No production code changes without a preceding failing test.
3. **Clean Architecture:** Domain logic must NEVER depend on infrastructure (DB, HTTP, Frameworks).
4. **SOLID Enforcement:** Every class/module must have exactly one reason to change.
5. **Zero Vibe Coding:** Technical decisions are based on patterns and metrics, not "feelings."
6. **Economy of Context:** Limit tool usage and reads to the exact scope of the task.
7. **YAGNI + KISS:** No "just-in-case" code. Functions < 30 lines, Nesting < 3 levels.

---

## 🔄 The AI-XP Task Lifecycle

### 1. Selection & Initialization
- **Choose Task:** Select the next atomic unit from `plan.md`.
- **Mark In Progress:** Update status to `[~]`.

### 2. Phase 🔴 RED (Write Failing Tests)
- **Action:** Create a new test file in an ephemeral or dedicated test directory.
- **Strictness:** Tests must capture behavioral requirements (Gherkin/BDD style where possible).
- **Validation:** Run the test suite. **MUST** result in a clear `AssertionError`. Do not proceed until the test fails.

### 3. Phase 🟢 GREEN (Minimal Implementation)
- **Action:** Implement the **minimum** code necessary to pass the test.
- **Rule:** Do not implement features not covered by the current red test (YAGNI).
- **Validation:** Run tests. If they fail, fix the implementation or revert and start over.

### 4. Phase 🔵 REFACTOR (Design Improvement)
- **Action:** Improve code quality while tests are green.
- **Checklist:**
  - Remove duplication (DRY).
  - Simplify logic (KISS).
  - Ensure SOLID compliance.
  - Verify complexity metrics (Ciclomatic complexity ≤ 15).
- **Validation:** Rerun tests to ensure zero behavioral regression.

---

## 🏛️ Architectural Invariants

### Backend (Go)
- **Pattern:** `handler → service → repository`.
- **Constraint:** Handlers handle HTTP, Services handle logic, Repositories handle DB. No cross-layer imports.
- **Feed Resilience:** Recommender calls must always have a fallback to `repo.GetFeed`.
- **Context:** Use the `comma-ok` idiom for context extraction.

### Frontend (SvelteKit)
- **State:** Use Svelte `writable` stores ONLY. No Redux/Zustand.
- **API:** Use `lib/api.ts` for all calls. 401 handling must be global.

### Recommender (Python)
- **Constraint:** Read-only DB access. No writes. No auth logic.
- **Ranking:** Candidates → Scoring → Well-being Modifier.

---

## 🛡️ Quality Gates & Definition of Done

A task is complete ONLY when:
- [ ] **Tests:** Red-Green-Refactor cycle completed and all tests pass.
- [ ] **Coverage:** Minimum 80% code coverage for new modules.
- [ ] **Complexity:** Functions < 30 lines, Nesting ≤ 2 levels, Cyclomatic Complexity ≤ 15.
- [ ] **Types:** Strict type safety (TS/Go) and type hints (Python) enforced.
- [ ] **Boundaries:** No Clean Architecture or SOLID violations.
- [ ] **Documentation:** Public APIs documented (JSDoc/GoDoc).
- [ ] **Response Format:** All API errors return JSON: `{"success": false, "error": "msg"}`.
- [ ] **Commit:** Changes committed with Conventional Commits message.
- [ ] **Summary:** Detailed task summary attached via `git notes`.

---

## 🏁 Phase Completion & Checkpointing

When a phase concludes in `plan.md`:
1. **Automated Audit:** Run full test suite and linting (`go build`, `npm run lint`, etc.).
2. **Manual Verification:** Propose a step-by-step verification plan to the user.
3. **User Approval:** **PAUSE** for explicit user confirmation.
4. **Checkpoint Commit:** Create a commit `conductor(checkpoint): End of Phase X`.
5. **Git Note:** Attach an auditable verification report to the checkpoint commit.

---

## 🚨 Emergency Protocols
- **Failure Loop:** If a fix fails twice, revert all changes (`git checkout .`) and re-evaluate the strategy.
- **Security:** Zero tolerance for hardcoded secrets or unvalidated inputs.
- **Stability:** System must work even if AI/Recommender services are offline (Fallback logic).

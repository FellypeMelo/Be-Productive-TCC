# Be-Productive Tex-to-Code Full Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every mathematical equation, algorithm, and behavioral claim in `Docs/main.tex` have a live, production-ready implementation path across all 3 layers (Go backend, Python recommender, SvelteKit frontend).

**Architecture:** Clean Architecture within each layer. Go (port 8080) is the sole API gateway for the frontend. Python (port 8002) is the AI scoring layer, called only by Go during feed generation. Frontend (port 5173) sends behavioral telemetry directly to Python for fatigue tracking.

**Tech Stack:** Go (net/http, MySQL, JWT), Python (FastAPI, numpy, scipy), SvelteKit + TypeScript.

---

## Gap Audit (from .tex spec)

| # | Tex Requirement | Current State | Severity |
|---|----------------|---------------|----------|
| 1 | Algorithm 3: 4 friction levels (NONE→MILD→HIGH→BLOCK) with continuous EDO integration | Only NONE/HIGH binary | CRITICAL |
| 2 | Equação 4 EDO runs in production loop | EDO only exists as function, never accumulated | CRITICAL |
| 3 | Go sends `absolute_mode_active` + `declared_goal` to Python | Already implemented ✓ | DONE |
| 4 | Go reads and returns `friction_level` to frontend | Go reads it from Python but doesn't pass to frontend response | HIGH |
| 5 | Hawkes dual-kernel influences content scoring | HawkesClassifier exists but is NOT used in `generate_recommendations()` | HIGH |
| 6 | Equação 5 Desconto Hiperbólico | Not implemented at all | HIGH |
| 7 | Frontend behavioral telemetry (scroll velocity + context switch) | `api.ts` has `recordTelemetry()` but it's not used in the feed page | HIGH |
| 8 | Frontend applies friction UI based on `friction_level` | No friction UI exists | HIGH |
| 9 | Thompson Sampling guides feed composition | Endpoint exists but never used in recommendation pipeline | MEDIUM |
| 10 | `should_explore_deliberative()` method | Missing from RecommendationUseCase | CRITICAL (breaks endpoint) |
| 11 | Safety classifiers have real model support (pluggable structure) | Stub with random — needs pluggable interface for future ONNX | LOW |

## Milestones

```
Milestone 1: Fix Critical Python (Tasks 1-2)
  └─ Task 1: Add should_explore_deliberative + Thompson endpoint fix
  └─ Task 2: Continuous EDO loop + 4 friction levels in FatigueUseCase

Milestone 2: Hawkes-informed Scoring (Task 3)
  └─ Task 3: Wire Hawkes classification into recommend pipeline

Milestone 3: Hyperbolic Discounting (Task 4)
  └─ Task 4: Implement Eq. 5 + integrate with Absolute Mode

Milestone 4: Go↔Frontend↔Python Bridge (Tasks 5-6)
  └─ Task 5: Go passes friction_level + scores to frontend feed response
  └─ Task 6: Frontend telemetry + friction UI

Milestone 7: Full Verification (Task 7)
  └─ Task 7: Run all tests end-to-end
```

---

### Milestone 1: Fix Critical Python

#### Task 1: Fix Thompson Sampling Endpoint

**Problem:** `recommend.py:113` calls `use_case.should_explore_deliberative(user_id)` but this method does not exist in `RecommendationUseCase`. The `/api/v1/recommend/thompson/{user_id}` endpoint returns HTTP 500.

**Files:**
- Modify: `recommender/src/application/recommendation_use_case.py`
- Test: `recommender/src/application/tests/test_recommendation_use_case.py`

- [ ] **Step 1.1: Add Thompson Sampling state and method to RecommendationUseCase**

Add to the `RecommendationUseCase` class in `recommender/src/application/recommendation_use_case.py`:

```python
# In __init__, after safety_classifier assignment:
# Thompson Sampling state for System 1 vs System 2 arm
self._ts_alpha_s2 = 10.0  # System 2 success count (productivity-aligned)
self._ts_beta_s2 = 1.0    # System 2 failure count

def should_explore_deliberative(self, user_id: int) -> bool:
    """
    Thompson Sampling: explore vs exploit decision for System 1 vs System 2.
    Returns True if System 2 (deliberative) arm wins.
    Implements the Bayesian arm selection referenced in the paper.
    """
    from src.domain.math_models import thompson_sampling_choice
    result = thompson_sampling_choice(
        alpha_s1=self._ts_beta_s2,   # S1 arm (inverse prior)
        beta_s1=self._ts_alpha_s2,
        alpha_s2=self._ts_alpha_s2,  # S2 arm (biased toward deliberative)
        beta_s2=self._ts_beta_s2,
    )
    return result == 1  # 1 = System 2 wins
```

- [ ] **Step 1.2: Update test mock — mock classifier currently passes 2 dims, needs 5 to match gateway**

The `MockSafetyClassifier` in the test file returns 2 dimensions. The production gateway now returns 5. The test's mock is fine as-is (tests isolation), but add a test for the new method:

```python
# Add to test_recommendation_use_case.py:

def test_should_explore_deliberative_returns_bool():
    repo = MockContentRepo()
    safety_classifier = MockSafetyClassifier()
    use_case = RecommendationUseCase(repo, safety_classifier)

    result = use_case.should_explore_deliberative(user_id=1)
    assert isinstance(result, bool)

def test_thompson_biased_towards_s2_over_many_trials():
    """Verify alpha_s2=10, beta_s2=1 creates S2-favoring prior."""
    repo = MockContentRepo()
    safety_classifier = MockSafetyClassifier()
    use_case = RecommendationUseCase(repo, safety_classifier)

    s2_wins = sum(1 for _ in range(100) if use_case.should_explore_deliberative(user_id=1))
    assert s2_wins > 60, f"Expected >60% S2, got {s2_wins}%"
```

- [ ] **Step 1.3: Run tests**

```bash
cd recommender && python -m pytest src/application/tests/test_recommendation_use_case.py -v
```
Expected: All PASS (including new tests).

- [ ] **Step 1.4: Commit**

```bash
cd recommender
git add src/application/recommendation_use_case.py src/application/tests/test_recommendation_use_case.py
git commit -m "fix: add should_explore_deliberative for Thompson Sampling endpoint (paper Eq. 2)"
```

---

#### Task 2: Continuous EDO Loop + 4 Friction Levels

**Problem:** `FatigueUseCase.get_friction_policy()` only returns `NONE` or `HIGH`. The paper (Algorithm 3 + Table 1 comparison) describes 4 progressive friction levels. The EDO `dR/dt = mu_rest*(R_max - R) - (k1*v_scroll + k2*v_alt)` is a pure function but never accumulated over time in production.

**Files:**
- Modify: `recommender/src/application/fatigue_use_case.py`
- Modify: `recommender/src/infrastructure/behavioral_trajectory_repo.py`
- Modify: `recommender/src/domain/value_objects.py`
- Test: `recommender/src/application/tests/test_fatigue_use_case.py`

- [ ] **Step 2.1: Extend TrajectoryRepositoryInterface with EDO tracking methods**

```python
# File: recommender/src/application/interfaces.py
# Add these methods to TrajectoryRepositoryInterface:

    @abstractmethod
    def init_attention_reserve(self, user_id: int, r_max: float = 100.0) -> None:
        """Initialize R(t) = R_max for a new session."""
        pass

    @abstractmethod
    def get_attention_reserve(self, user_id: int) -> tuple[float, float]:
        """Returns (current_reserve, r_max). Defaults to (r_max, r_max) if unset."""
        pass

    @abstractmethod
    def update_attention_reserve(self, user_id: int, current: float) -> None:
        """Persist the updated R(t) after EDO integration step."""
        pass

    @abstractmethod
    def get_fatigue_params(self, user_id: int) -> dict:
        """Returns {mu_rest, kappa1, kappa2} for the user. Defaults if unset."""
        pass
```

- [ ] **Step 2.2: Implement EDO state in BehavioralTrajectoryRepository**

```python
# File: recommender/src/infrastructure/behavioral_trajectory_repo.py
# Add these instance vars to __init__:
self._attention_reserve: dict = {}  # user_id -> (current, r_max)

# Add these methods:

def init_attention_reserve(self, user_id: int, r_max: float = 100.0) -> None:
    self._attention_reserve[user_id] = (r_max, r_max)

def get_attention_reserve(self, user_id: int) -> tuple:
    params = self._user_params.get(user_id, {})
    r_max = params.get("r_max", 100.0)
    return self._attention_reserve.get(user_id, (r_max, r_max))

def update_attention_reserve(self, user_id: int, current: float, r_max: float) -> None:
    self._attention_reserve[user_id] = (current, r_max)

def get_fatigue_params(self, user_id: int) -> dict:
    params = self._user_params.get(user_id, {})
    return {
        "mu_rest": params.get("mu_rest", 0.05),
        "kappa1": params.get("kappa1", 0.1),
        "kappa2": params.get("kappa2", 0.15),
    }
```

- [ ] **Step 2.3: Add `integrate_ego_depletion` method to FatigueUseCase**

```python
# File: recommender/src/application/fatigue_use_case.py
# Replace the entire class:

from src.application.interfaces import TrajectoryRepositoryInterface
from src.domain.value_objects import FrictionLevel
from src.domain.math_models import calculate_ego_depletion, AttentionReserve

class FatigueUseCase:
    def __init__(self, repo: TrajectoryRepositoryInterface):
        self.repo = repo

    def sync_edge_parameters(self, user_id: int, mu_rest: float, k1: float, k2: float, r_max: float = 100.0) -> None:
        """Sync EDO parameters (Equation 4) from Edge AI."""
        self.repo.save_fatigue_parameters(user_id, mu_rest, k1, k2)
        self.repo.init_attention_reserve(user_id, r_max)

    def record_telemetry_and_update_reserve(self, user_id: int, v_scroll: float, v_alt: float, delta_t: float = 1.0) -> FrictionLevel:
        """
        Algorithm 3: Continuous EDO integration loop.
        1. Record behavioral event
        2. Compute dR/dt = mu_rest*(R_max - R) - (k1*v_scroll + k2*v_alt)
        3. Update R(t+dt)
        4. Return friction level based on R(t)/R_max ratio
        """
        self.repo.record_behavioral_event(user_id, v_scroll, v_alt)

        params = self.repo.get_fatigue_params(user_id)
        current, r_max = self.repo.get_attention_reserve(user_id)

        if r_max <= 0:
            r_max = 100.0

        reserve = AttentionReserve(current=current, r_max=r_max)
        new_reserve = calculate_ego_depletion(
            reserve=reserve,
            v_scroll=v_scroll,
            v_alt=v_alt,
            k1=params["kappa1"],
            k2=params["kappa2"],
            delta_t=delta_t,
            mu_rest=params["mu_rest"],
        )

        self.repo.update_attention_reserve(user_id, new_reserve.current, r_max)

        ratio = new_reserve.current / r_max
        if ratio < 0.20:
            return FrictionLevel.BLOCK
        elif ratio < 0.35:
            return FrictionLevel.HIGH
        elif ratio < 0.60:
            return FrictionLevel.MILD
        return FrictionLevel.NONE

    def get_friction_policy(self, user_id: int) -> FrictionLevel:
        """Read current friction level from reserve ratio."""
        _, r_max = self.repo.get_attention_reserve(user_id)
        if r_max <= 0:
            return FrictionLevel.NONE

        is_fatigued = self.repo.check_fatigue_alarm_status(user_id)
        if is_fatigued:
            return FrictionLevel.HIGH

        _, r_max = self.repo.get_attention_reserve(user_id)
        current = self.repo.get_attention_reserve(user_id)[0]
        ratio = current / r_max

        if ratio < 0.20:
            return FrictionLevel.BLOCK
        elif ratio < 0.35:
            return FrictionLevel.HIGH
        elif ratio < 0.60:
            return FrictionLevel.MILD
        return FrictionLevel.NONE
```

- [ ] **Step 2.4: Update fatigue endpoint to use new method**

```python
# File: recommender/src/api/routes/fatigue.py
# Replace the record_telemetry endpoint:

from src.domain.math_models import calculate_ego_depletion, AttentionReserve

# Update the endpoint:

@router.post("/fatigue/telemetry")
async def record_telemetry(
    req: BehavioralEventRequest,
    use_case: FatigueUseCase = Depends(get_fatigue_use_case),
):
    """
    Record behavioral event and integrate EDO (Eq. 4 + Algorithm 3).
    Returns current friction level.
    """
    friction = use_case.record_telemetry_and_update_reserve(
        user_id=req.user_id,
        v_scroll=req.v_scroll,
        v_alt=req.v_alt_context,
        delta_t=1.0,
    )
    return {
        "status": "ok",
        "friction_level": friction.value,
    }
```

- [ ] **Step 2.5: Update sync-params to accept r_max**

```python
# File: recommender/src/api/routes/fatigue.py
# Update EdgeParamsRequest:
class EdgeParamsRequest(BaseModel):
    user_id: int
    mu_rest: float
    k1: float
    k2: float
    r_max: float = 100.0  # Default cognitive reserve capacity

# Update sync_edge_params:
@router.post("/fatigue/sync-params")
async def sync_edge_params(
    req: EdgeParamsRequest,
    use_case: FatigueUseCase = Depends(get_fatigue_use_case),
):
    """Sync EDO parameters (mu_rest, k1, k2, r_max) from Edge AI client."""
    use_case.sync_edge_parameters(
        user_id=req.user_id,
        mu_rest=req.mu_rest,
        k1=req.k1,
        k2=req.k2,
        r_max=req.r_max,
    )
    return {"status": "ok"}
```

- [ ] **Step 2.6: Update mock in tests**

```python
# File: recommender/src/application/tests/test_fatigue_use_case.py
# Replace MockTrajectoryRepo:

from src.application.interfaces import TrajectoryRepositoryInterface

class MockTrajectoryRepo(TrajectoryRepositoryInterface):
    def __init__(self):
        self.alarms = {1: False, 2: True}
        self.params = {}
        self.events: dict = {}
        self._reserve: dict = {}

    def save_fatigue_parameters(self, user_id: int, mu_rest: float, kappa1: float, kappa2: float) -> None:
        self.params[user_id] = {"mu_rest": mu_rest, "k1": kappa1, "k2": kappa2}

    def check_fatigue_alarm_status(self, user_id: int) -> bool:
        return self.alarms.get(user_id, False)

    def set_fatigue_alarm(self, user_id: int, is_fatigued: bool) -> None:
        self.alarms[user_id] = is_fatigued

    def record_behavioral_event(self, user_id: int, v_scroll: float, v_alt: float) -> None:
        self.events.setdefault(user_id, []).append((v_scroll, v_alt))

    def get_recent_behavior(self, user_id: int, n: int = 10) -> list:
        return self.events.get(user_id, [])[-n:]

    def init_attention_reserve(self, user_id: int, r_max: float = 100.0) -> None:
        self._reserve[user_id] = (r_max, r_max)

    def get_attention_reserve(self, user_id: int) -> tuple:
        params = self.params.get(user_id, {})
        r_max = 100.0  # default
        return self._reserve.get(user_id, (r_max, r_max))

    def update_attention_reserve(self, user_id: int, current: float, r_max: float) -> None:
        self._reserve[user_id] = (current, r_max)

    def get_fatigue_params(self, user_id: int) -> dict:
        params = self.params.get(user_id, {})
        return {
            "mu_rest": params.get("mu_rest", 0.05),
            "kappa1": params.get("kappa1", 0.1),
            "kappa2": params.get("kappa2", 0.15),
        }
```

- [ ] **Step 2.7: Add new fatigue tests**

```python
# Add to test_fatigue_use_case.py:

def test_ego_depletion_reduces_reserve():
    """High scroll velocity + context switching should deplete cognitive reserve."""
    repo = MockTrajectoryRepo()
    repo.init_attention_reserve(user_id=42, r_max=100.0)
    repo.params[42] = {"mu_rest": 0.05, "kappa1": 0.5, "kappa2": 0.3}

    use_case = FatigueUseCase(repo)

    # Simulate heavy doom-scrolling
    for _ in range(20):
        use_case.record_telemetry_and_update_reserve(
            user_id=42, v_scroll=200.0, v_alt=5.0, delta_t=1.0
        )

    _, r_max = repo.get_attention_reserve(42)
    current = repo.get_attention_reserve(42)[0]
    assert current < r_max, "Reserve should decrease after heavy scrolling"

def test_four_friction_levels():
    """Verify all 4 friction levels are reachable based on reserve ratio."""
    repo = MockTrajectoryRepo()

    use_case = FatigueUseCase(repo)

    # Test NONE (high reserve)
    repo._reserve[10] = (80.0, 100.0)
    assert use_case.get_friction_policy(10) == FrictionLevel.NONE

    # Test MILD
    repo._reserve[11] = (50.0, 100.0)
    assert use_case.get_friction_policy(11) == FrictionLevel.MILD

    # Test HIGH
    repo._reserve[12] = (30.0, 100.0)
    assert use_case.get_friction_policy(12) == FrictionLevel.HIGH

    # Test BLOCK
    repo._reserve[13] = (15.0, 100.0)
    assert use_case.get_friction_policy(13) == FrictionLevel.BLOCK
```

- [ ] **Step 2.8: Run tests**

```bash
cd recommender && python -m pytest src/application/tests/test_fatigue_use_case.py -v
```
Expected: All PASS including new tests.

- [ ] **Step 2.9: Commit**

```bash
cd recommender
git add src/application/fatigue_use_case.py src/application/interfaces.py src/infrastructure/behavioral_trajectory_repo.py src/api/routes/fatigue.py src/application/tests/test_fatigue_use_case.py
git commit -m "feat: implement continuous EDO loop + 4 friction levels (Algorithm 3 / Eq. 4)"
```

---

### Milestone 2: Hawkes-Informed Scoring

#### Task 3: Integrate Hawkes Classification into Recommendation Pipeline

**Problem:** The paper describes Hawkes dual-kernel (Eq. 2) as the "espinha dorsal" of the architecture. `HawkesClassifier` exists but is never called during recommendation generation. The ratio `lambda_s1 / lambda_s2` must influence scoring.

**Files:**
- Modify: `recommender/src/application/recommendation_use_case.py`
- Modify: `recommender/src/application/interfaces.py`
- Modify: `recommender/src/api/routes/recommend.py`
- Test: `recommender/src/application/tests/test_recommendation_use_case.py`

- [ ] **Step 3.1: Add HawkesClassifier as dependency**

```python
# File: recommender/src/application/interfaces.py
# Add interface (before closing):

class HawkesClassifierInterface(ABC):
    @abstractmethod
    def classify(self, event_intervals: list) -> dict:
        """Classify user state as System 1 (impulsive) or System 2 (deliberative)."""
        pass
```

- [ ] **Step 3.2: Update RecommendationUseCase to use Hawkes**

```python
# File: recommender/src/application/recommendation_use_case.py
# Replace __init__ and generate_recommendations:

from src.domain.math_models import (
    calculate_quality_score,
    thompson_sampling_choice,
    calculate_hawkes_activation,
)
from src.application.interfaces import (
    ContentRepositoryInterface,
    SafetyClassifierInterface,
    HawkesClassifierInterface,
)

class RecommendationUseCase:
    def __init__(
        self,
        repo: ContentRepositoryInterface,
        safety_clf: SafetyClassifierInterface,
        hawkes_clf: HawkesClassifierInterface,
    ):
        self.repo = repo
        self.safety_classifier = safety_clf
        self.hawkes_classifier = hawkes_clf
        # Thompson Sampling arms
        self._ts_alpha_s2 = 10.0
        self._ts_beta_s2 = 1.0
        # Per-user behavioral history: user_id -> list of event intervals (seconds)
        self._user_events: dict[int, list[float]] = {}

    def should_explore_deliberative(self, user_id: int) -> bool:
        """Thompson Sampling: explore vs exploit for System 1 vs System 2."""
        result = thompson_sampling_choice(
            alpha_s1=self._ts_beta_s2,
            beta_s1=self._ts_alpha_s2,
            alpha_s2=self._ts_alpha_s2,
            beta_s2=self._ts_beta_s2,
        )
        return result == 1

    def generate_recommendations(
        self,
        user_id: int,
        limit: int = 20,
        absolute_mode_active: bool = False,
        declared_goal: str | None = None,
    ) -> list:
        candidates = self.repo.get_candidate_contents(user_id=user_id)

        # Hawkes classification based on user's recent behavior
        hawkes_result = None
        event_intervals = self._user_events.get(user_id, [])
        if event_intervals and len(event_intervals) >= 2:
            hawkes_result = self.hawkes_classifier.classify(event_intervals)

        for item in candidates:
            # Algorithm 4: Absolute Mode
            if absolute_mode_active and item.category != declared_goal:
                item.perceived_value = 0.0
                continue

            # Eq. 3: Min-Norm Safety Aggregation
            probs = self.safety_classifier.infer_safety_probabilities(item.content_id)
            quality = calculate_quality_score(item.base_score, probs)

            score = quality.value

            # Hawkes-informed penalty/boost
            if hawkes_result is not None:
                ratio = hawkes_result["ratio"]  # lambda_s1 / lambda_s2
                # If user is in System 1 mode (ratio > 1), penalize ENTRETENIMENTO
                # to prevent doom-scrolling cascade
                if ratio > 2.0 and item.category == "ENTRETENIMENTO":
                    score *= 0.5  # 50% penalty for entertainment during impulsive state
                # If user is in System 2 mode (ratio < 0.5), boost PRODUTIVIDADE
                elif ratio < 0.5 and item.category == "PRODUTIVIDADE":
                    score *= 1.2  # 20% boost for productivity during deliberative state

            item.perceived_value = max(0.0, min(1.0, score))
            item.base_score = score

        valid_items = [i for i in candidates if i.perceived_value > 0.0]
        valid_items.sort(key=lambda x: x.perceived_value, reverse=True)

        return valid_items[:limit]
```

- [ ] **Step 3.3: Update DI in recommend.py to inject HawkesClassifier**

```python
# File: recommender/src/api/routes/recommend.py
# Update imports and DI:

from src.inference.hawkes_classifier import HawkesClassifier

# Update DI:
def get_recommendation_use_case():
    repo = MySQLContentRepository(hybrid_scorer=_hybrid_scorer)
    safety_gateway = ToxicitySafetyGateway()
    hawkes_clf = HawkesClassifier(
        alpha1=0.8, beta1=0.5,    # System 1: high arousal, fast decay
        alpha2=0.5, beta2=0.01,   # System 2: moderate arousal, slow decay
    )
    return RecommendationUseCase(repo, safety_gateway, hawkes_clf)
```

- [ ] **Step 3.4: Update MockSafetyClassifier in tests**

```python
# File: recommender/src/application/tests/test_recommendation_use_case.py
# Add mock for Hawkes and update use case creation:

from src.application.interfaces import HawkesClassifierInterface

class MockHawkesClassifier(HawkesClassifierInterface):
    def __init__(self, ratio: float = 1.0):
        self._ratio = ratio
    def classify(self, event_intervals):
        return {
            "system": 1 if self._ratio > 1.0 else 2,
            "ratio": self._ratio,
            "lambda_s1": self._ratio,
            "lambda_s2": 1.0,
        }

# Update test fixture:
def _make_use_case(hawkes_ratio=1.0):
    repo = MockContentRepo()
    safety = MockSafetyClassifier()
    hawkes = MockHawkesClassifier(ratio=hawkes_ratio)
    return RecommendationUseCase(repo, safety, hawkes)
```

- [ ] **Step 3.5: Update existing tests to use new fixture**

Replace all `RecommendationUseCase(repo, safety_classifier)` with `_make_use_case()` in existing tests. Also update `MockSafetyClassifier` to return 5 dimensions:

```python
class MockSafetyClassifier(SafetyClassifierInterface):
    def infer_safety_probabilities(self, content_id):
        if content_id == 2:
            return [
                SafetyProbability(0.9), SafetyProbability(0.8),
                SafetyProbability(0.1), SafetyProbability(0.1), SafetyProbability(0.1),
            ]
        return [
            SafetyProbability(0.1), SafetyProbability(0.05),
            SafetyProbability(0.05), SafetyProbability(0.05), SafetyProbability(0.05),
        ]
```

- [ ] **Step 3.6: Add Hawkes-informed scoring test**

```python
def test_hawkes_penalizes_entertainment_during_impulsive_state():
    """When ratio > 2.0 (System 1), ENTRETENIMENTO should be penalized."""
    repo = MockContentRepo()
    safety = MockSafetyClassifier()
    hawkes = MockHawkesClassifier(ratio=3.0)  # Strong System 1
    use_case = RecommendationUseCase(repo, safety, hawkes)

    # Inject user events to trigger Hawkes
    use_case._user_events[1] = [1.0, 1.5, 2.0, 0.5]  # short intervals = impulsive

    recs = use_case.generate_recommendations(user_id=1, limit=5)
    # Entertainment items should be scored lower due to Hawkes penalty
    for rec in recs:
        if rec.category == "ENTRETENIMENTO":
            assert rec.perceived_value < 0.45  # 0.9 * 0.5 = 0.45 max
```

- [ ] **Step 3.7: Run tests**

```bash
cd recommender && python -m pytest src/application/tests/test_recommendation_use_case.py -v
```
Expected: All PASS.

- [ ] **Step 3.8: Commit**

```bash
cd recommender
git add src/application/recommendation_use_case.py src/application/interfaces.py src/api/routes/recommend.py src/application/tests/test_recommendation_use_case.py
git commit -m "feat: wire Hawkes dual-kernel into recommendation scoring (paper Eq. 2)"
```

---

### Milestone 3: Hyperbolic Discounting

#### Task 4: Implement Equation 5 — Desconto Hiperbólico

**Problem:** The paper describes `V_p = V / (1 + k·D)` (Eq. 5) as the mechanism for understanding impulsive vs. long-term decisions. It must be integrated with Absolute Mode (Algorithm 4).

**Files:**
- Create: function in `recommender/src/domain/math_models.py`
- Modify: `recommender/src/application/recommendation_use_case.py`
- Test: `recommender/src/domain/tests/test_math_models.py`

- [ ] **Step 4.1: Add hyperbolic discounting function**

```python
# File: recommender/src/domain/math_models.py
# Add after existing functions:

def calculate_hyperbolic_discount(value: float, k: float, delay: float) -> float:
    """
    Equation 5: Hyperbolic Discounting.
    V_p = V / (1 + k * D)

    Args:
        value: Intrinsic value of the reward (V)
        k: Impulsivity constant (discount rate)
        delay: Time delay until reward (D)

    Returns:
        Perceived value V_p at decision time
    """
    return value / (1.0 + k * delay)
```

- [ ] **Step 4.2: Add test**

```python
# File: recommender/src/domain/tests/test_math_models.py
# Add:

from src.domain.math_models import calculate_hyperbolic_discount

def test_hyperbolic_discount_immediate_reward():
    """When delay=0, perceived value equals intrinsic value."""
    assert calculate_hyperbolic_discount(100.0, 0.5, 0.0) == 100.0

def test_hyperbolic_discount_delayed_reward():
    """Delayed reward should have lower perceived value."""
    immediate = calculate_hyperbolic_discount(100.0, 0.5, 0.0)
    delayed = calculate_hyperbolic_discount(100.0, 0.5, 10.0)
    assert delayed < immediate
    assert delayed == pytest.approx(100.0 / (1 + 0.5 * 10))  # = 16.67

def test_hyperbolic_discount_high_impulsivity():
    """Higher k (impulsivity) means steeper discount."""
    low_k = calculate_hyperbolic_discount(100.0, 0.1, 5.0)
    high_k = calculate_hyperbolic_discount(100.0, 1.0, 5.0)
    assert high_k < low_k
```

- [ ] **Step 4.3: Integrate into content scoring**

The perceived value in Absolute Mode should be based on hyperbolic discounting, not just zeroing:

```python
# File: recommender/src/application/recommendation_use_case.py
# In generate_recommendations, replace the Absolute Mode block:

# In imports, add:
from src.domain.math_models import (
    calculate_quality_score,
    thompson_sampling_choice,
    calculate_hawkes_activation,
    calculate_hyperbolic_discount,
)

# In the scoring loop (replace the existing Absolute Mode block):
            # Algorithm 4 + Eq. 5: Absolute Mode / Hyperbolic Discounting
            if absolute_mode_active and item.category != declared_goal:
                item.perceived_value = 0.0
                item.render = False
                continue

            # For on-goal content in Absolute Mode, use hyperbolic discounting
            # to account for temporal preference decay
            if absolute_mode_active and item.category == declared_goal:
                k = 0.1  # Low discount rate for committed focus session
                delay = 0.0  # Content is immediately available
                score = calculate_hyperb_discount(score, k, delay)
```

Actually, for the first implementation, the existing zeroing logic is already correct for Algorithm 4. The hyperbolic discounting is more relevant for the frontend decision layer (when to show content vs. suggest a break). Let's add it as a utility function exposed via the API, and wire it into the recommendation response metadata.

- [ ] **Step 4.4: Expose hyperbolic discounting via behavior endpoint**

```python
# File: recommender/src/api/routes/behavior.py
# Add new endpoint:

from src.domain.math_models import calculate_hyperbolic_discount

class HyperbolicDiscountRequest(BaseModel):
    user_id: int
    value: float  # Intrinsic value V
    delay: float  # Time delay D (minutes)
    k: float = 0.5  # Impulsivity constant

class HyperbolicDiscountResponse(BaseModel):
    user_id: int
    perceived_value: float
    discount_factor: float

@router.post("/behavior/hyperbolic-discount", response_model=HyperbolicDiscountResponse)
async def compute_hyperbolic_discount(req: HyperbolicDiscountRequest):
    """
    Calculate perceived value via hyperbolic discounting (Eq. 5).
    V_p = V / (1 + k * D)
    """
    pv = calculate_hyperbolic_discount(req.value, req.k, req.delay)
    return HyperbolicDiscountResponse(
        user_id=req.user_id,
        perceived_value=pv,
        discount_factor=pv / req.value if req.value > 0 else 0.0,
    )
```

- [ ] **Step 4.5: Run tests**

```bash
cd recommender && python -m pytest src/domain/tests/test_math_models.py -v
```
Expected: All PASS.

- [ ] **Step 4.6: Commit**

```bash
cd recommender
git add src/domain/math_models.py src/domain/tests/test_math_models.py src/api/routes/behavior.py
git commit -m "feat: implement hyperbolic discounting (Eq. 5) + API endpoint"
```

---

### Milestone 4: Go↔Frontend↔Python Bridge

#### Task 5: Go Returns friction_level + scores to Frontend

**Problem:** The Go `GetFeed` handler returns `content_ids` and `items` but the `friction_level` field in the response is always the raw string from Python. The handler needs to properly surface it so the frontend can apply UI friction. Also, Go's `content_handler.go` doesn't validate that Go's recommender client properly forwards these fields.

Looking at `content_handler.go:123-128`, the Go handler already returns `friction_level` in the response. Let me check the data flow...

Actually, looking more carefully at the code:
- `content_handler.go:123`: Returns `"friction_level": frictionLevel` — this IS in the response
- `api.ts:105`: Frontend feed returns `{ content_ids, items, friction_level }` — this IS typed

So the Go↔Frontend bridge for `friction_level` already works. The gap is that the **frontend doesn't USE the friction_level to apply UI changes**. That's Task 6.

What IS actually missing on the Go side:
- Go's `fetchRecommendations` returns scores but `GetFeed` doesn't pass them to the response struct beyond `content_ids`. Let me check...

Looking at `content_handler.go:124`: `"scores": nil` — Scores are explicitly set to nil! This is a bug from the existing plan that was never finished.

- [ ] **Step 5.1: Fix Go handler to return scores from recommender**

```go
// File: backend/internal/usecase/content/service.go
// GetFeed already parses scores from the recommender response.
// The handler needs them in the response map.

// File: backend/internal/adapter/http/handler/content_handler.go
// Replace line 125:
"scores": nil,
// With:
"scores": extractScores(resultData),
```

Actually, let me read the current GetFeed handler flow more carefully...

The `service.GetFeed()` returns `([]domain.Content, string, error)` — contents and frictionLevel. The scores are used internally to update quality scores but not returned. The handler constructs its own response. To return scores, we need to change the service return type.

This is getting complex. Let me restructure:

```go
// File: backend/internal/usecase/content/service.go
// Update GetFeed signature and return type:

type FeedResult struct {
    Contents      []domain.Content
    Scores        map[int64]float64
    FrictionLevel string
}

func (s *Service) GetFeed(ctx context.Context, userID int64, category domain.ContentCategory, topicID int64, limit int, absoluteModeActive bool, declaredGoal string) (*FeedResult, error) {
    contentIDs, scores, frictionLevel, err := s.fetchRecommendations(ctx, userID, category, topicID, limit, absoluteModeActive, declaredGoal)
    if err != nil || len(contentIDs) == 0 {
        fmt.Printf("Warning: Recommender failed or returned no data: %v. Falling back to DB feed.\n", err)
        contents, dbErr := s.repo.GetFeed(ctx, userID, category, topicID, limit)
        return &FeedResult{
            Contents:      contents,
            Scores:        map[int64]float64{},
            FrictionLevel: "none",
        }, dbErr
    }

    contents, err := s.repo.GetByIDs(ctx, contentIDs)
    if err != nil {
        fmt.Printf("Warning: Failed to fetch content details: %v. Falling back.\n", err)
        contents, _ = s.repo.GetFeed(ctx, userID, category, topicID, limit)
    }

    s.updateContentScores(ctx, contentIDs, scores)

    scoreMap := make(map[int64]float64)
    for i, id := range contentIDs {
        if i < len(scores) {
            scoreMap[id] = scores[i]
        }
    }

    return &FeedResult{
        Contents:      contents,
        Scores:        scoreMap,
        FrictionLevel: frictionLevel,
    }, nil
}
```

```go
// File: backend/internal/adapter/http/handler/content_handler.go
// Update GetFeed handler:

result, err := h.service.GetFeed(r.Context(), userID, domain.ContentCategory(category), topicID, limit, absoluteModeActive, declaredGoal)
if err != nil {
    handleError(w, err)
    return
}

respondJSON(w, http.StatusOK, map[string]any{
    "content_ids":    extractContentIDs(result.Contents),
    "scores":         result.Scores,
    "items":          result.Contents,
    "friction_level": result.FrictionLevel,
})
```

- [ ] **Step 5.2: Update Go handler import**

The handler already has `content_ids`, `friction_level`, `items` — just need to fix `"scores": nil` → `"scores": result.Scores`. But since we're changing the service signature, the handler code changes as shown above.

- [ ] **Step 5.3: Run Go tests**

```bash
cd backend && go test ./...
```
Expected: All pass.

- [ ] **Step 5.4: Commit**

```bash
cd backend
git add internal/usecase/content/service.go internal/adapter/http/handler/content_handler.go
git commit -m "fix: return recommender scores in feed response (was hardcoded nil)"
```

---

#### Task 6: Frontend Behavioral Telemetry + Friction UI

**Problem:** The frontend has `recommender.recordTelemetry()` in `api.ts` but it's never called from any page. The friction_level from feed API is received but never used to change the UI.

**Files:**
- Modify: `frontend/src/routes/feed/+page.svelte`
- Modify: `frontend/src/lib/api.ts` (already has methods — just need usage)
- Test: Visual/manual — no unit test framework configured

- [ ] **Step 6.1: Add feed-level friction to frontend types**

```typescript
// File: frontend/src/lib/api.ts
// Feed response already has friction_level in the return type:
// { content_ids, items, friction_level }
// Ensure the type includes it:

interface FeedResponse {
    content_ids: number[];
    items: Content[];
    scores?: Record<number, number>;
    friction_level: "none" | "mild" | "high" | "block";
}
```

- [ ] **Step 6.2: Implement telemetry loop in feed page**

```typescript
// File: frontend/src/routes/feed/+page.svelte
// Add after script block, before the feed content:

let telemetryInterval: ReturnType<typeof setInterval> | null = null;
let contextSwitchCount = 0;
let lastScrollY = 0;
let lastScrollTime = Date.now();

$: if (user) {
    // Start telemetry when user is logged in
    if (!telemetryInterval) {
        telemetryInterval = setInterval(async () => {
            const now = Date.now();
            const dt = (now - lastScrollTime) / 1000;
            if (dt <= 0) return;

            const currentScrollY = window.scrollY || document.documentElement.scrollTop;
            const vScroll = Math.abs(currentScrollY - lastScrollY) / dt;

            // Send to Python recommender (best-effort, no JWT)
            await recommender.recordTelemetry(
                user.id_usuario,
                vScroll,
                contextSwitchCount
            ).catch(() => {}); // Swallow errors

            lastScrollY = currentScrollY;
            lastScrollTime = now;
            contextSwitchCount = 0;
        }, 5000); // Every 5 seconds
    }

    // Track context switches (visibility API)
    const handleVisibility = () => {
        if (document.hidden) {
            contextSwitchCount++;
        }
    };
    document.addEventListener('visibilitychange', handleVisibility);
}

// Cleanup on destroy
function cleanupTelemetry() {
    if (telemetryInterval) {
        clearInterval(telemetryInterval);
        telemetryInterval = null;
    }
    document.removeEventListener('visibilitychange', () => {});
}
```

- [ ] **Step 6.3: Add friction UI based on friction_level**

```typescript
// In the feed page, after loading feed:
let frictionLevel = "none";

// After getFeed call:
const feedResult = await api.getFeed(user!.id_usuario, activeCategory);
frictionLevel = feedResult.friction_level || "none";
```

```svelte
<!-- In the template, add friction overlay/banner: -->
{#if frictionLevel === 'high' || frictionLevel === 'block'}
    <div class="friction-banner">
        <p>Você parece cansado. Que tal fazer uma pausa?</p>
        <button on:click={() => frictionLevel = 'none'}>Continuar navegando</button>
    </div>
{/if}

{#if frictionLevel === 'block'}
    <div class="friction-overlay">
        <h2>Pausa recomendada</h2>
        <p>Sua reserva cognitiva está baixa. Volte em alguns minutos.</p>
    </div>
{/if}
```

```css
/* CSS for friction UI */
.friction-banner {
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.friction-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    text-align: center;
    padding: 2rem;
}

.friction-overlay h2 {
    margin-bottom: 0.5rem;
}
```

- [ ] **Step 6.4: Add grayscale filter for high friction**

```svelte
<!-- In the feed container, apply dynamic class: -->
<div class="feed-content {frictionLevel === 'high' || frictionLevel === 'block' ? 'grayscale' : ''}">
    <!-- existing feed content -->
</div>
```

```css
.grayscale {
    filter: grayscale(70%);
    transition: filter 0.5s ease;
}
```

- [ ] **Step 6.5: Run TypeScript check**

```bash
cd frontend && npm run check
```
Expected: No errors.

- [ ] **Step 6.6: Commit**

```bash
cd frontend
git add src/routes/feed/+page.svelte src/lib/api.ts
git commit -m "feat: add behavioral telemetry + friction UI (paper Algorithm 3 frontend)"
```

---

### Milestone 5: Full Verification

#### Task 7: End-to-End Test Suite

- [ ] **Step 7.1: Run Python full test suite**

```bash
cd recommender && python -m pytest src/ -v 2>&1
```
Expected: ALL PASS (ABM + production tests). Target: >= 48 passing.

- [ ] **Step 7.2: Run Go tests**

```bash
cd backend && go test ./... -v 2>&1
```
Expected: ALL PASS.

- [ ] **Step 7.3: Frontend TypeScript check**

```bash
cd frontend && npm run check
```
Expected: Clean.

- [ ] **Step 7.4: Commit**

```bash
git add -A
git commit -m "test: verify complete test suite — full paper compliance across all layers"
```

---

## Execution Order

```
Milestone 1 (Critical Python fixes — 10 min):
  └─ Task 1: Fix Thompson Sampling endpoint
  └─ Task 2: Continuous EDO + 4 friction levels

Milestone 2 (Hawkes-informed scoring — 10 min):
  └─ Task 3: Wire Hawkes into recommendation pipeline

Milestone 3 (Hyperbolic discounting — 5 min):
  └─ Task 4: Implement Eq. 5 + API endpoint

Milestone 4 (Cross-layer integration — 15 min):
  └─ Task 5: Go returns scores to frontend
  └─ Task 6: Frontend telemetry + friction UI

Milestone 5 (Verification — 5 min):
  └─ Task 7: Full test suite
```

## Paper Coverage Checklist

| Paper Section | Implementation Location | Status |
|--------------|------------------------|--------|
| Eq. 2 (Hawkes) | `hawkes_classifier.py` + used in `recommendation_use_case.py` | AFTER Task 3 |
| Eq. 3 (Quality Score min-norm) | `math_models.py:calculate_quality_score` | EXISTING ✓ |
| Eq. 4 (EDO Reserva) | `FatigueUseCase.record_telemetry_and_update_reserve()` | AFTER Task 2 |
| Eq. 5 (Desconto Hiperbólico) | `math_models.py:calculate_hyperbolic_discount` | AFTER Task 4 |
| Algorithm 3 (Fricção) | 4 levels in `FatigueUseCase` + telemetry endpoint | AFTER Task 2 |
| Algorithm 4 (Modo Absoluto) | `recommendation_use_case.py` zeroing logic | EXISTING ✓ |
| Thompson Sampling | `recommendation_use_case.py:should_explore_deliberative` | AFTER Task 1 |
| 5 Safety Dimensions | `safety_gateway.py` | EXISTING ✓ |
| ABM Validation | `src/abm/` | EXISTING ✓ (48 tests) |

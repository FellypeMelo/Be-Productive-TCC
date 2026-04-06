import pytest
from src.application.interfaces import TrajectoryRepositoryInterface
from src.application.fatigue_use_case import FatigueUseCase
from src.domain.value_objects import FrictionLevel


class MockTrajectoryRepo(TrajectoryRepositoryInterface):
    def __init__(self):
        self.alarms = {1: False, 2: True}
        self.params = {}
        self.events: dict = {}
        self._attention_reserve: dict = {}

    def save_fatigue_parameters(self, user_id: int, mu_rest: float, kappa1: float, kappa2: float) -> None:
        self.params[user_id] = {"mu_rest": mu_rest, "kappa1": kappa1, "kappa2": kappa2}

    def check_fatigue_alarm_status(self, user_id: int) -> bool:
        return self.alarms.get(user_id, False)

    def set_fatigue_alarm(self, user_id: int, is_fatigued: bool) -> None:
        self.alarms[user_id] = is_fatigued

    def record_behavioral_event(self, user_id: int, v_scroll: float, v_alt: float) -> None:
        self.events.setdefault(user_id, []).append((v_scroll, v_alt))

    def get_recent_behavior(self, user_id: int, n: int = 10) -> list:
        return self.events.get(user_id, [])[-n:]

    def init_attention_reserve(self, user_id: int, r_max: float = 100.0) -> None:
        self._attention_reserve[user_id] = {"current": r_max, "r_max": r_max}

    def get_attention_reserve(self, user_id: int) -> tuple:
        reserve = self._attention_reserve.get(user_id)
        if reserve is None:
            r_max = 100.0
            return (r_max, r_max)
        return (reserve["current"], reserve["r_max"])

    def update_attention_reserve(self, user_id: int, current: float, r_max: float) -> None:
        self._attention_reserve[user_id] = {"current": current, "r_max": r_max}

    def get_fatigue_params(self, user_id: int) -> dict:
        params = self.params.get(user_id, {})
        return {
            "mu_rest": params.get("mu_rest", 0.05),
            "kappa1": params.get("kappa1", 0.01),
            "kappa2": params.get("kappa2", 0.5),
        }


def test_sync_edo_parameters():
    """Garante que a EDO do paper seja sincronizada com o front-end Edge AI."""
    repo = MockTrajectoryRepo()
    use_case = FatigueUseCase(repo)

    use_case.sync_edge_parameters(user_id=1, mu_rest=0.5, k1=0.1, k2=1.0)
    assert repo.params[1] == {"mu_rest": 0.5, "kappa1": 0.1, "kappa2": 1.0}


def test_respond_to_fatigue_alarm():
    """
    Testes das regras de resposta ao alarme de fadiga do cliente.
    Se alarmado (True), retorna fricção alta.
    """
    repo = MockTrajectoryRepo()
    use_case = FatigueUseCase(repo)

    # User 1 is not fatigued, reserve initialized
    repo.init_attention_reserve(1, 100.0)
    friction_user1 = use_case.get_friction_policy(user_id=1)
    assert friction_user1 == FrictionLevel.NONE

    # User 2 is fatigued (alarm=True set in __init__)
    repo.init_attention_reserve(2, 100.0)
    friction_user2 = use_case.get_friction_policy(user_id=2)
    assert friction_user2 == FrictionLevel.HIGH


def test_set_fatigue_alarm():
    """Test that alarm can be set and affects friction policy."""
    repo = MockTrajectoryRepo()
    use_case = FatigueUseCase(repo)

    repo.init_attention_reserve(1, 100.0)
    assert use_case.get_friction_policy(1) == FrictionLevel.NONE

    repo.set_fatigue_alarm(1, True)
    assert use_case.get_friction_policy(1) == FrictionLevel.HIGH


def test_record_behavioral_event():
    """Test recording behavioral events."""
    repo = MockTrajectoryRepo()
    repo.record_behavioral_event(1, 120.5, 3.2)
    repo.record_behavioral_event(1, 150.0, 4.1)

    events = repo.get_recent_behavior(1)
    assert len(events) == 2
    assert events[0] == (120.5, 3.2)
    assert events[1] == (150.0, 4.1)


def test_ego_depletion_reduces_reserve():
    """Simulates heavy doom-scrolling, asserts reserve decreases and friction increases."""
    repo = MockTrajectoryRepo()
    use_case = FatigueUseCase(repo)

    r_max = 100.0
    # k1=0.1, k2=1.0 with heavy v_scroll=500, v_alt=10:
    # load = 0.1*500 + 1.0*10 = 60. Recovery = 0.05*(100-100) = 0.
    # new_reserve = 100 + (0 - 60)*1.0 = 40 → ratio 0.40 → HIGH
    use_case.sync_edge_parameters(user_id=1, mu_rest=0.05, k1=0.1, k2=1.0, r_max=r_max)

    initial, _ = repo.get_attention_reserve(1)
    assert initial == r_max

    # Simulate heavy doom-scrolling: high scroll velocity + context switching
    friction = use_case.record_telemetry_and_update_reserve(
        user_id=1, v_scroll=500.0, v_alt=10.0, delta_t=1.0
    )
    assert friction in (FrictionLevel.MILD, FrictionLevel.HIGH, FrictionLevel.BLOCK)

    new, max_after = repo.get_attention_reserve(1)
    assert max_after == r_max
    assert new < initial


def test_four_friction_levels():
    """Tests NONE/MILD/HIGH/BLOCK are reachable at correct ratios."""
    repo = MockTrajectoryRepo()
    use_case = FatigueUseCase(repo)

    r_max = 100.0

    # NONE: ratio >= 0.60
    repo.init_attention_reserve(1, r_max)
    repo.update_attention_reserve(1, 80.0, r_max)
    assert use_case.get_friction_policy(1) == FrictionLevel.NONE

    # MILD: 0.35 <= ratio < 0.60
    repo.init_attention_reserve(1, r_max)
    repo.update_attention_reserve(1, 50.0, r_max)
    assert use_case.get_friction_policy(1) == FrictionLevel.MILD

    # HIGH: 0.20 <= ratio < 0.35
    repo.init_attention_reserve(1, r_max)
    repo.update_attention_reserve(1, 25.0, r_max)
    assert use_case.get_friction_policy(1) == FrictionLevel.HIGH

    # BLOCK: ratio < 0.20
    repo.init_attention_reserve(1, r_max)
    repo.update_attention_reserve(1, 10.0, r_max)
    assert use_case.get_friction_policy(1) == FrictionLevel.BLOCK


def test_record_telemetry_triggers_friction():
    """Verify that telemetry calls actually update reserve and return friction."""
    repo = MockTrajectoryRepo()
    use_case = FatigueUseCase(repo)

    # k1=0.1, k2=1.0: load per step = 0.1*300 + 1.0*8 = 38
    # After 2 steps: R = 100 - 38*2 = 24 → ratio 0.24 → HIGH
    use_case.sync_edge_parameters(user_id=5, mu_rest=0.02, k1=0.1, k2=1.0, r_max=100.0)

    # Heavy usage should eventually push below NONE
    for _ in range(3):
        friction = use_case.record_telemetry_and_update_reserve(
            user_id=5, v_scroll=300.0, v_alt=8.0, delta_t=1.0
        )

    current, r_max = repo.get_attention_reserve(5)
    initial = 100.0
    assert current < initial
    assert friction != FrictionLevel.NONE

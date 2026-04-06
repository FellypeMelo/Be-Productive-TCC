import pytest
from src.application.interfaces import TrajectoryRepositoryInterface
from src.application.fatigue_use_case import FatigueUseCase
from src.domain.value_objects import FrictionLevel

class MockTrajectoryRepo(TrajectoryRepositoryInterface):
    def __init__(self):
        self.alarms = {1: False, 2: True} # User 2 is fatigued
        self.params = {}
        self.events: dict = {}

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


def test_sync_edo_parameters():
    """Garante que a EDO do paper seja sincronizada com o front-end Edge AI."""
    repo = MockTrajectoryRepo()
    use_case = FatigueUseCase(repo)

    use_case.sync_edge_parameters(user_id=1, mu_rest=0.5, k1=0.1, k2=1.0)
    assert repo.params[1] == {"mu_rest": 0.5, "k1": 0.1, "k2": 1.0}

def test_respond_to_fatigue_alarm():
    """
    Testes das regras de resposta ao alarme de fadiga do cliente.
    Se alarmado (True), retorna fricção alta.
    """
    repo = MockTrajectoryRepo()
    use_case = FatigueUseCase(repo)

    # User 1 is not fatigued
    friction_user1 = use_case.get_friction_policy(user_id=1)
    assert friction_user1 == FrictionLevel.NONE

    # User 2 is fatigued
    friction_user2 = use_case.get_friction_policy(user_id=2)
    assert friction_user2 == FrictionLevel.HIGH

def test_set_fatigue_alarm():
    """Test that alarm can be set and affects friction policy."""
    repo = MockTrajectoryRepo()
    use_case = FatigueUseCase(repo)

    # User 1 not fatigued
    assert use_case.get_friction_policy(1) == FrictionLevel.NONE

    # Set alarm for user 1
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

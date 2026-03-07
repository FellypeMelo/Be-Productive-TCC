import pytest
from src.application.interfaces import TrajectoryRepositoryInterface
# Must fail before GREEN phase
from src.application.fatigue_use_case import FatigueUseCase

class MockTrajectoryRepo(TrajectoryRepositoryInterface):
    def __init__(self):
        self.alarms = {1: False, 2: True} # User 2 is fatigued
        self.params = {}

    def save_fatigue_parameters(self, user_id: int, mu_rest: float, kappa1: float, kappa2: float) -> None:
        self.params[user_id] = {"mu_rest": mu_rest, "k1": kappa1, "k2": kappa2}
        
    def check_fatigue_alarm_status(self, user_id: int) -> bool:
        return self.alarms.get(user_id, False)


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
    assert friction_user1 == "NONE"
    
    # User 2 is fatigued
    friction_user2 = use_case.get_friction_policy(user_id=2)
    assert friction_user2 == "HIGH_FRICTION"

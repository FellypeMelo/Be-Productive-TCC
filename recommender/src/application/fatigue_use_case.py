from src.application.interfaces import TrajectoryRepositoryInterface

class FatigueUseCase:
    def __init__(self, repo: TrajectoryRepositoryInterface):
        self.repo = repo
        
    def sync_edge_parameters(self, user_id: int, mu_rest: float, k1: float, k2: float) -> None:
        """
        Sincroniza os parâmetros de degradação e repouso (Equação 4) para Edge AI. 
        Backend delega o stress computing local.
        """
        self.repo.save_fatigue_parameters(user_id, mu_rest, k1, k2)
        
    def get_friction_policy(self, user_id: int) -> str:
        """
        Recebe e processa o alarme de fadiga do Edge AI (Algoritmo 3).
        Retorna a política de contenção.
        """
        is_fatigued = self.repo.check_fatigue_alarm_status(user_id)
        if is_fatigued:
            return "HIGH_FRICTION"
        return "NONE"

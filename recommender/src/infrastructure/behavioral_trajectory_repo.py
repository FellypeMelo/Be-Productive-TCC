from src.application.interfaces import TrajectoryRepositoryInterface

class BehavioralTrajectoryRepository(TrajectoryRepositoryInterface):
    """
    Persists fatigue state and behavioral trajectory data.
    In production, this would be Redis or MongoDB for low-latency reads.
    Currently in-memory.
    """

    def __init__(self):
        self._user_params: dict = {}
        self._alarm_status: dict = {}
        self._behavioral_buffer: dict = {}  # user_id -> list of (v_scroll, v_alt)

    def save_fatigue_parameters(
        self, user_id: int, mu_rest: float, kappa1: float, kappa2: float
    ) -> None:
        self._user_params[user_id] = {
            "mu_rest": mu_rest,
            "kappa1": kappa1,
            "kappa2": kappa2,
        }

    def check_fatigue_alarm_status(self, user_id: int) -> bool:
        return self._alarm_status.get(user_id, False)

    def set_fatigue_alarm(self, user_id: int, is_fatigued: bool) -> None:
        """Called by Edge AI client to report fatigue status."""
        self._alarm_status[user_id] = is_fatigued

    def record_behavioral_event(
        self, user_id: int, v_scroll: float, v_alt: float
    ) -> None:
        """Buffer behavioral signals for fatigue calculation."""
        if user_id not in self._behavioral_buffer:
            self._behavioral_buffer[user_id] = []
        self._behavioral_buffer[user_id].append((v_scroll, v_alt))

    def get_recent_behavior(self, user_id: int, n: int = 10) -> list:
        """Get last n behavioral events for this user."""
        return self._behavioral_buffer.get(user_id, [])[-n:]

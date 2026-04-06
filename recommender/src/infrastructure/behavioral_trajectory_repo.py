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
        self._attention_reserve: dict = {}  # user_id -> {"current": float, "r_max": float}

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

    def init_attention_reserve(self, user_id: int, r_max: float = 100.0) -> None:
        """Initialize R(t) = R_max for a new session."""
        self._attention_reserve[user_id] = {"current": r_max, "r_max": r_max}

    def get_attention_reserve(self, user_id: int) -> tuple:
        """Returns (current_reserve, r_max). Defaults to (r_max, r_max) if unset."""
        reserve = self._attention_reserve.get(user_id)
        if reserve is None:
            r_max = 100.0
            return (r_max, r_max)
        return (reserve["current"], reserve["r_max"])

    def update_attention_reserve(self, user_id: int, current: float, r_max: float) -> None:
        """Persist the updated R(t) after EDO integration step."""
        self._attention_reserve[user_id] = {"current": current, "r_max": r_max}

    def get_fatigue_params(self, user_id: int) -> dict:
        """Returns {mu_rest, kappa1, kappa2} for the user. Defaults if unset."""
        params = self._user_params.get(user_id, {})
        return {
            "mu_rest": params.get("mu_rest", 0.05),
            "kappa1": params.get("kappa1", 0.01),
            "kappa2": params.get("kappa2", 0.5),
        }

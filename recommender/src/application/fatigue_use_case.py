from src.application.interfaces import TrajectoryRepositoryInterface
from src.domain.value_objects import FrictionLevel


class FatigueUseCase:
    def __init__(self, repo: TrajectoryRepositoryInterface):
        self.repo = repo

    def sync_edge_parameters(
        self, user_id: int, mu_rest: float, k1: float, k2: float, r_max: float = 100.0
    ) -> None:
        """Sync EDO parameters (Equation 4) from Edge AI."""
        self.repo.save_fatigue_parameters(user_id, mu_rest, k1, k2)
        self.repo.init_attention_reserve(user_id, r_max)

    def record_telemetry_and_update_reserve(
        self, user_id: int, v_scroll: float, v_alt: float, delta_t: float = 1.0
    ) -> FrictionLevel:
        """
        Algorithm 3: Continuous EDO integration loop.
        1. Record behavioral event
        2. Compute dR/dt = mu_rest*(R_max - R) - (k1*v_scroll + k2*v_alt)
        3. Update R(t+dt)
        4. Return friction level based on R(t)/R_max ratio
        """
        from src.domain.math_models import calculate_ego_depletion
        from src.domain.value_objects import AttentionReserve

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
        current, r_max = self.repo.get_attention_reserve(user_id)
        if r_max <= 0:
            return FrictionLevel.NONE

        is_fatigued = self.repo.check_fatigue_alarm_status(user_id)
        if is_fatigued:
            return FrictionLevel.HIGH

        ratio = current / r_max
        if ratio < 0.20:
            return FrictionLevel.BLOCK
        elif ratio < 0.35:
            return FrictionLevel.HIGH
        elif ratio < 0.60:
            return FrictionLevel.MILD
        return FrictionLevel.NONE

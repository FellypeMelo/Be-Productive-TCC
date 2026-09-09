import hashlib
import os


EXPERIMENT_ID = "sustainable-attention-v1"
ASSIGNMENT_VERSION = "sha256-v1"
ALGORITHM_VERSION = "2.3.0-sustainable-attention"
EXPERIMENT_NAME = EXPERIMENT_ID
VARIANTS = ("control", "treatment")
ROLLOUT_FRACTION = min(1.0, max(0.0, float(os.getenv("EXPERIMENT_ROLLOUT", "1.0"))))


def stable_variant(user_id: int, eligible: bool = True, rollout_fraction: float = ROLLOUT_FRACTION) -> str:
    """Return a deterministic arm, or ``not_eligible`` without consent."""
    if user_id < 1 or not eligible or not 0.0 <= rollout_fraction <= 1.0:
        return "not_eligible"
    rollout_digest = hashlib.sha256(
        f"{EXPERIMENT_ID}:{ASSIGNMENT_VERSION}:rollout:{user_id}".encode("utf-8")
    ).digest()
    if int.from_bytes(rollout_digest[:8], "big") / 2**64 >= rollout_fraction:
        return "not_eligible"
    digest = hashlib.sha256(
        f"{EXPERIMENT_ID}:{ASSIGNMENT_VERSION}:{user_id}".encode("utf-8")
    ).digest()
    return "treatment" if digest[0] < 128 else "control"


def experiment_assignment(user_id: int, eligible: bool = True, rollout_fraction: float = ROLLOUT_FRACTION) -> dict[str, object]:
    """Expose only non-sensitive assignment metadata to the API contract."""
    variant = stable_variant(user_id, eligible, rollout_fraction)
    return {
        "experiment_id": EXPERIMENT_ID,
        "variant": variant,
        "assignment_version": ASSIGNMENT_VERSION,
        "algorithm_version": ALGORITHM_VERSION,
        "eligible": eligible and variant in VARIANTS,
        "rollout_fraction": rollout_fraction,
    }

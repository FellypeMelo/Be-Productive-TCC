import hashlib


EXPERIMENT_ID = "sustainable-attention-v1"
ASSIGNMENT_VERSION = "sha256-v1"
ALGORITHM_VERSION = "2.3.0-sustainable-attention"
EXPERIMENT_NAME = EXPERIMENT_ID
VARIANTS = ("control", "treatment")


def stable_variant(user_id: int, eligible: bool = True) -> str:
    """Return a deterministic arm, or ``not_eligible`` without consent."""
    if user_id < 1 or not eligible:
        return "not_eligible"
    digest = hashlib.sha256(
        f"{EXPERIMENT_ID}:{ASSIGNMENT_VERSION}:{user_id}".encode("utf-8")
    ).digest()
    return "treatment" if digest[0] < 128 else "control"


def experiment_assignment(user_id: int, eligible: bool = True) -> dict[str, str | bool]:
    """Expose only non-sensitive assignment metadata to the API contract."""
    variant = stable_variant(user_id, eligible)
    return {
        "experiment_id": EXPERIMENT_ID,
        "variant": variant,
        "assignment_version": ASSIGNMENT_VERSION,
        "algorithm_version": ALGORITHM_VERSION,
        "eligible": eligible and variant in VARIANTS,
    }

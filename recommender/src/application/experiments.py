import hashlib


EXPERIMENT_NAME = "ranking-v2"


def stable_variant(user_id: int) -> str:
    """Stable 50/50 assignment. No user can enter both variants."""
    digest = hashlib.sha256(f"{EXPERIMENT_NAME}:{user_id}".encode("utf-8")).digest()
    return "treatment" if digest[0] < 128 else "control"

from src.application.experiments import stable_variant


def test_assignment_is_stable_and_binary():
    assignments = [stable_variant(user_id) for user_id in range(1, 100)]
    assert assignments == [stable_variant(user_id) for user_id in range(1, 100)]
    assert set(assignments) == {"control", "treatment"}

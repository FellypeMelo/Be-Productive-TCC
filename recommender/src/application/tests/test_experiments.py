from src.application.experiments import experiment_assignment, stable_variant


def test_assignment_is_stable_and_binary():
    assignments = [stable_variant(user_id) for user_id in range(1, 100)]
    assert assignments == [stable_variant(user_id) for user_id in range(1, 100)]
    assert set(assignments) == {"control", "treatment"}


def test_assignment_requires_research_consent():
    assert stable_variant(12345, eligible=False) == "not_eligible"
    assert experiment_assignment(12345, eligible=False)["eligible"] is False

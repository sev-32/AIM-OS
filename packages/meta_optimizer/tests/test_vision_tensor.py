from __future__ import annotations

from packages.meta_optimizer.vision_tensor import compute_tensor, g_vision_fit


def test_compute_tensor_returns_deterministic_result() -> None:
    seed = {"vision": "Build Memory-to-Idea Growth Engine", "axes": ["memory", "idea", "governance"]}
    result_one = compute_tensor(seed, model="test-model")
    result_two = compute_tensor(seed, model="test-model", correlation_id=result_one.correlation_id)

    assert result_one.tensor == result_two.tensor
    assert result_one.correlation_id == result_two.correlation_id
    assert 0.0 <= result_one.score <= 1.0
    assert result_one.policy_pack_ids == result_two.policy_pack_ids == []


def test_compute_tensor_promotes_policy_pack_ids() -> None:
    seed = {
        "vision": "Policy aware seed",
        "policy_pack_ids": ["policy.seed", "policy.shared"],
    }
    result = compute_tensor(seed, model="test-model", policy_pack_ids=["policy.override", "policy.seed"])
    assert result.policy_pack_ids == ["policy.override", "policy.seed", "policy.shared"]
    second = compute_tensor(seed, model="test-model")
    assert second.policy_pack_ids == ["policy.seed", "policy.shared"]


def test_compute_tensor_supports_policy_packs_alias() -> None:
    result = compute_tensor("Alias test", policy_packs=["policy.alias", "policy.extra"])
    assert result.policy_pack_ids == ["policy.alias", "policy.extra"]


def test_g_vision_fit_gate_passes_when_threshold_met() -> None:
    seed = "Simple seed"
    result = compute_tensor(seed, model="test-model")
    gate = g_vision_fit(result, threshold=0.0)
    assert gate.passed is True
    assert gate.score == result.score

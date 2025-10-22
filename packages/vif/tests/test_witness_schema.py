"""Tests for VIF witness schema"""

import pytest
from datetime import datetime, timezone
import hashlib

from vif.witness import VIF, ConfidenceBand, TaskCriticality


def test_vif_minimal_creation():
    """Test creating VIF with minimal required fields"""
    vif = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_123",
        prompt_hash=VIF.hash_text("test prompt"),
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash=VIF.hash_text("test output"),
        output_tokens=5,
        total_tokens=15,
    )
    
    assert vif.id.startswith("vif_")
    assert vif.model_id == "gpt-4-turbo"
    assert vif.confidence_score == 0.95
    assert vif.confidence_band == ConfidenceBand.A
    assert vif.kappa_gate_passed is True


def test_vif_full_creation():
    """Test creating VIF with all fields"""
    vif = VIF(
        model_id="gpt-4-turbo-2025-01-15",
        model_provider="openai",
        weights_hash="abc123",
        context_snapshot_id="snap_456",
        context_atom_ids=["atom1", "atom2"],
        prompt_template="Answer: {question}",
        prompt_hash=VIF.hash_text("Answer: What is AI?"),
        prompt_tokens=100,
        retrieved_atom_ids=["atom3", "atom4"],
        tool_ids=["hhni.retrieve", "cmc.store"],
        tool_parameters={"k": 10, "budget": 4000},
        tool_results_hash=VIF.hash_text("tool results"),
        confidence_score=0.85,
        confidence_band=ConfidenceBand.B,
        ece_score=0.03,
        entropy=2.5,
        top_k_probs=[("the", 0.3), ("a", 0.2)],
        replay_seed=42,
        temperature=0.7,
        top_p=0.9,
        top_k=50,
        max_tokens=500,
        other_params={"frequency_penalty": 0.1},
        output_hash=VIF.hash_text("AI is artificial intelligence"),
        output_tokens=50,
        total_tokens=150,
        writer="agent_planner",
        task_criticality=TaskCriticality.IMPORTANT,
        kappa_threshold=0.80,
        kappa_gate_passed=True,
        execution_time_ms=123.45,
        parent_vif_id="vif_parent123",
    )
    
    assert vif.model_id == "gpt-4-turbo-2025-01-15"
    assert vif.tool_ids == ["hhni.retrieve", "cmc.store"]
    assert vif.ece_score == 0.03
    assert vif.task_criticality == TaskCriticality.IMPORTANT
    assert vif.kappa_threshold == 0.80
    assert vif.parent_vif_id == "vif_parent123"


def test_confidence_band_determination():
    """Test automatic confidence band determination"""
    # High confidence (A)
    vif_high = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
    )
    assert vif_high.determine_confidence_band() == ConfidenceBand.A
    
    # Medium confidence (B)
    vif_medium = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.75,
        confidence_band=ConfidenceBand.B,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
    )
    assert vif_medium.determine_confidence_band() == ConfidenceBand.B
    
    # Low confidence (C)
    vif_low = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.50,
        confidence_band=ConfidenceBand.C,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
    )
    assert vif_low.determine_confidence_band() == ConfidenceBand.C


def test_kappa_gate_check():
    """Test κ-gate confidence threshold checking"""
    # Passes gate
    vif_pass = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash",
        prompt_tokens=10,
        confidence_score=0.85,
        confidence_band=ConfidenceBand.B,
        output_hash="hash",
        output_tokens=5,
        total_tokens=15,
        kappa_threshold=0.80,
    )
    assert vif_pass.check_kappa_gate() is True
    
    # Fails gate
    vif_fail = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash",
        prompt_tokens=10,
        confidence_score=0.65,
        confidence_band=ConfidenceBand.C,
        output_hash="hash",
        output_tokens=5,
        total_tokens=15,
        kappa_threshold=0.70,
    )
    assert vif_fail.check_kappa_gate() is False


def test_child_lineage():
    """Test adding children to witness lineage"""
    parent = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash",
        prompt_tokens=10,
        confidence_score=0.90,
        confidence_band=ConfidenceBand.A,
        output_hash="hash",
        output_tokens=5,
        total_tokens=15,
    )
    
    assert len(parent.child_vif_ids) == 0
    
    parent.add_child("vif_child1")
    assert len(parent.child_vif_ids) == 1
    assert "vif_child1" in parent.child_vif_ids
    
    parent.add_child("vif_child2")
    assert len(parent.child_vif_ids) == 2
    
    # Adding same child twice doesn't duplicate
    parent.add_child("vif_child1")
    assert len(parent.child_vif_ids) == 2


def test_hash_utilities():
    """Test VIF hash generation utilities"""
    text = "Hello, World!"
    expected_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    assert VIF.hash_text(text) == expected_hash
    assert VIF.hash_bytes(text.encode("utf-8")) == expected_hash


def test_serialization():
    """Test VIF to/from dict serialization"""
    original = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_789",
        prompt_hash=VIF.hash_text("prompt"),
        prompt_tokens=20,
        confidence_score=0.88,
        confidence_band=ConfidenceBand.B,
        output_hash=VIF.hash_text("output"),
        output_tokens=10,
        total_tokens=30,
        tool_ids=["tool1", "tool2"],
        task_criticality=TaskCriticality.CRITICAL,
    )
    
    # Serialize to dict
    data = original.to_dict()
    assert isinstance(data, dict)
    assert data["model_id"] == "gpt-4"
    assert data["confidence_score"] == 0.88
    
    # Deserialize from dict
    restored = VIF.from_dict(data)
    assert restored.model_id == original.model_id
    assert restored.confidence_score == original.confidence_score
    assert restored.tool_ids == original.tool_ids
    assert restored.task_criticality == original.task_criticality


def test_validation_constraints():
    """Test Pydantic validation constraints"""
    # Confidence score must be 0.0-1.0
    with pytest.raises(ValueError):
        VIF(
            model_id="test",
            model_provider="test",
            context_snapshot_id="snap",
            prompt_hash="hash",
            prompt_tokens=10,
            confidence_score=1.5,  # Invalid!
            confidence_band=ConfidenceBand.A,
            output_hash="hash",
            output_tokens=5,
            total_tokens=15,
        )
    
    # Token counts must be non-negative
    with pytest.raises(ValueError):
        VIF(
            model_id="test",
            model_provider="test",
            context_snapshot_id="snap",
            prompt_hash="hash",
            prompt_tokens=-10,  # Invalid!
            confidence_score=0.9,
            confidence_band=ConfidenceBand.A,
            output_hash="hash",
            output_tokens=5,
            total_tokens=15,
        )


def test_datetime_handling():
    """Test datetime creation and serialization"""
    vif = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash",
        prompt_tokens=10,
        confidence_score=0.9,
        confidence_band=ConfidenceBand.A,
        output_hash="hash",
        output_tokens=5,
        total_tokens=15,
    )
    
    # created_at should be auto-set
    assert isinstance(vif.created_at, datetime)
    assert vif.created_at.tzinfo is not None  # Should have timezone
    
    # Should serialize to ISO format
    data = vif.to_dict()
    assert isinstance(data["created_at"], str)
    assert "T" in data["created_at"]  # ISO format


def test_enums():
    """Test enum handling"""
    vif = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash",
        prompt_tokens=10,
        confidence_score=0.9,
        confidence_band=ConfidenceBand.A,
        output_hash="hash",
        output_tokens=5,
        total_tokens=15,
        task_criticality=TaskCriticality.CRITICAL,
    )
    
    # Enums should be actual enum objects
    assert isinstance(vif.confidence_band, ConfidenceBand)
    assert isinstance(vif.task_criticality, TaskCriticality)
    
    # Should work with equality
    assert vif.confidence_band == ConfidenceBand.A
    assert vif.task_criticality == TaskCriticality.CRITICAL


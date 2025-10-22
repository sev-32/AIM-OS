"""Tests for VIF-CMC integration"""

import pytest
import json
from unittest.mock import Mock, MagicMock

from vif.witness import VIF, ConfidenceBand, TaskCriticality
from vif.cmc_integration import (
    vif_to_atom_payload,
    atom_to_vif,
    VIFStore,
    create_witness_and_store,
)


def test_vif_to_atom_payload():
    """Test converting VIF to CMC atom payload"""
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
        task_criticality=TaskCriticality.CRITICAL,
    )
    
    payload = vif_to_atom_payload(vif)
    
    # Check modality
    assert payload["modality"] == "witness"
    
    # Check content
    assert payload["content"]["media_type"] == "application/json"
    assert "inline" in payload["content"]
    
    # Check VIF is serialized in content
    vif_data = json.loads(payload["content"]["inline"])
    assert vif_data["model_id"] == "gpt-4-turbo"
    assert vif_data["confidence_score"] == 0.95
    
    # Check tags
    assert payload["tags"]["vif_id"] == vif.id
    assert payload["tags"]["confidence_score"] == 0.95
    assert payload["tags"]["confidence_band"] == "A"
    assert payload["tags"]["kappa_gate_passed"] == 1.0
    
    # Check metadata
    assert payload["metadata"]["context_snapshot_id"] == "snap_123"
    assert payload["metadata"]["total_tokens"] == 15


def test_atom_to_vif():
    """Test converting CMC atom back to VIF"""
    # Create original VIF
    original = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_456",
        prompt_hash="hash1",
        prompt_tokens=20,
        confidence_score=0.85,
        confidence_band=ConfidenceBand.B,
        output_hash="hash2",
        output_tokens=10,
        total_tokens=30,
    )
    
    # Convert to atom payload
    payload = vif_to_atom_payload(original)
    
    # Create mock atom
    mock_atom = Mock()
    mock_atom.modality = "witness"
    mock_atom.content = payload["content"]
    
    # Convert back to VIF
    restored = atom_to_vif(mock_atom)
    
    # Verify roundtrip
    assert restored.model_id == original.model_id
    assert restored.confidence_score == original.confidence_score
    assert restored.context_snapshot_id == original.context_snapshot_id
    assert restored.total_tokens == original.total_tokens


def test_atom_to_vif_wrong_modality():
    """Test error when atom is not witness modality"""
    mock_atom = Mock()
    mock_atom.modality = "text"  # Not "witness"
    
    with pytest.raises(ValueError, match="modality must be 'witness'"):
        atom_to_vif(mock_atom)


def test_vif_store_initialization():
    """Test VIFStore initialization"""
    mock_cmc = Mock()
    store = VIFStore(mock_cmc)
    
    assert store.cmc is mock_cmc


def test_vif_store_store_witness():
    """Test storing VIF witness in CMC"""
    # Create mock CMC store
    mock_cmc = MagicMock()
    mock_atom = Mock()
    mock_atom.id = "atom_789"
    mock_cmc.create_atom.return_value = mock_atom
    
    store = VIFStore(mock_cmc)
    
    # Create VIF
    vif = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.9,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
    )
    
    # Store
    atom_id = store.store_witness(vif)
    
    # Verify CMC was called
    assert mock_cmc.create_atom.called
    assert atom_id == "atom_789"


def test_vif_store_get_witness():
    """Test retrieving VIF witness from CMC"""
    # Create original VIF
    original = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.9,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
    )
    
    # Create mock atom
    payload = vif_to_atom_payload(original)
    mock_atom = Mock()
    mock_atom.modality = "witness"
    mock_atom.content = payload["content"]
    
    # Create mock CMC
    mock_cmc = Mock()
    mock_cmc.get_atom.return_value = mock_atom
    
    # Get witness
    store = VIFStore(mock_cmc)
    retrieved = store.get_witness("atom_123")
    
    # Verify
    assert retrieved.model_id == original.model_id
    assert retrieved.confidence_score == original.confidence_score


def test_create_witness_and_store():
    """Test convenience function for creating and storing"""
    # Create mock CMC
    mock_cmc = MagicMock()
    mock_atom = Mock()
    mock_atom.id = "atom_999"
    mock_cmc.create_atom.return_value = mock_atom
    
    # Create and store
    vif, atom_id = create_witness_and_store(
        mock_cmc,
        operation_name="test_operation",
        prompt="What is 2+2?",
        output="4",
        confidence=0.99,
        context_snapshot_id="snap_123",
        model_id="gpt-4",
        model_provider="openai",
    )
    
    # Verify VIF created
    assert vif.confidence_score == 0.99
    assert vif.context_snapshot_id == "snap_123"
    assert vif.model_id == "gpt-4"
    
    # Verify stored in CMC
    assert atom_id == "atom_999"
    assert mock_cmc.create_atom.called


def test_roundtrip_serialization():
    """Test full roundtrip: VIF → atom payload → CMC → atom → VIF"""
    # Create original
    original = VIF(
        model_id="gpt-4-turbo-2025",
        model_provider="openai",
        context_snapshot_id="snap_critical_123",
        prompt_hash=VIF.hash_text("Diagnose patient symptoms"),
        prompt_tokens=100,
        confidence_score=0.92,
        confidence_band=ConfidenceBand.A,
        ece_score=0.03,
        entropy=1.5,
        replay_seed=42,
        temperature=0.0,
        output_hash=VIF.hash_text("Diagnosis: Common cold"),
        output_tokens=50,
        total_tokens=150,
        writer="medical_agent",
        task_criticality=TaskCriticality.CRITICAL,
        kappa_threshold=0.95,
        kappa_gate_passed=False,  # Failed gate!
        tool_ids=["hhni.retrieve", "medical_kb.query"],
    )
    
    # Convert to payload
    payload = vif_to_atom_payload(original)
    
    # Simulate CMC storage
    mock_atom = Mock()
    mock_atom.modality = "witness"
    mock_atom.content = payload["content"]
    
    # Convert back
    restored = atom_to_vif(mock_atom)
    
    # Verify all fields preserved
    assert restored.model_id == original.model_id
    assert restored.confidence_score == original.confidence_score
    assert restored.ece_score == original.ece_score
    assert restored.entropy == original.entropy
    assert restored.replay_seed == original.replay_seed
    assert restored.task_criticality == original.task_criticality
    assert restored.kappa_gate_passed == original.kappa_gate_passed
    assert restored.tool_ids == original.tool_ids


def test_witness_tags_for_querying():
    """Test that payload includes useful tags for CMC queries"""
    vif = VIF(
        model_id="claude-3",
        model_provider="anthropic",
        context_snapshot_id="snap",
        prompt_hash="hash",
        prompt_tokens=10,
        confidence_score=0.88,
        confidence_band=ConfidenceBand.B,
        output_hash="hash",
        output_tokens=5,
        total_tokens=15,
        task_criticality=TaskCriticality.IMPORTANT,
        ece_score=0.04,
    )
    
    payload = vif_to_atom_payload(vif)
    tags = payload["tags"]
    
    # Should have queryable tags
    assert "model_id" in tags
    assert "confidence_score" in tags
    assert "confidence_band" in tags
    assert "task_criticality" in tags
    assert "kappa_gate_passed" in tags
    assert "ece_score" in tags
    
    # Tags should be numeric for CMC
    assert isinstance(tags["confidence_score"], (int, float))
    assert isinstance(tags["kappa_gate_passed"], (int, float))


def test_metadata_for_context():
    """Test that payload includes useful metadata"""
    vif = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap_999",
        prompt_hash="hash",
        prompt_tokens=10,
        confidence_score=0.9,
        confidence_band=ConfidenceBand.A,
        output_hash="hash",
        output_tokens=5,
        total_tokens=15,
        execution_time_ms=123.45,
        parent_vif_id="vif_parent_456",
    )
    
    payload = vif_to_atom_payload(vif)
    metadata = payload["metadata"]
    
    assert metadata["context_snapshot_id"] == "snap_999"
    assert metadata["total_tokens"] == 15
    assert metadata["execution_time_ms"] == 123.45
    assert metadata["parent_vif_id"] == "vif_parent_456"


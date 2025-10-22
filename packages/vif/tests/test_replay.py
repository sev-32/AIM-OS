"""Tests for deterministic replay system"""

import pytest
import hashlib

from vif.replay import (
    ReplayEngine,
    ReplayResult,
    ReplayCache,
    create_replay_witness,
)
from vif.witness import VIF, ConfidenceBand


def test_replay_result_creation():
    """Test ReplayResult creation"""
    result = ReplayResult(
        success=True,
        output="test output",
        output_hash="abc123",
        matches_original=True,
        original_hash="abc123",
        execution_time_ms=100.0,
    )
    
    assert result.success is True
    assert result.matches_original is True


def test_replay_engine_initialization():
    """Test ReplayEngine initialization"""
    engine = ReplayEngine()
    
    assert engine.context_loader is None


def test_replay_engine_with_context_loader():
    """Test ReplayEngine with custom context loader"""
    def custom_loader(snapshot_id):
        return {"data": f"context for {snapshot_id}"}
    
    engine = ReplayEngine(context_loader=custom_loader)
    
    assert engine.context_loader is not None


def test_simple_replay():
    """Test replaying a simple operation"""
    engine = ReplayEngine()
    
    # Create original VIF
    vif = VIF(
        model_id="test-model",
        model_provider="test",
        context_snapshot_id="snap_123",
        prompt_hash=VIF.hash_text("test prompt"),
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash=VIF.hash_text("test output"),
        output_tokens=5,
        total_tokens=15,
        replay_seed=42,
        temperature=0.0,
    )
    
    # Operation that returns deterministic output
    def operation(params):
        return "test output"
    
    # Replay
    result = engine.replay(vif, operation, verify_hash=True)
    
    assert result.success is True
    assert result.matches_original is True


def test_replay_with_different_output():
    """Test replay that produces different output"""
    engine = ReplayEngine()
    
    vif = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash=VIF.hash_text("prompt"),
        prompt_tokens=10,
        confidence_score=0.9,
        confidence_band=ConfidenceBand.A,
        output_hash=VIF.hash_text("original output"),
        output_tokens=5,
        total_tokens=15,
    )
    
    def operation(params):
        return "different output"
    
    result = engine.replay(vif, operation, verify_hash=True)
    
    assert result.success is True
    assert result.matches_original is False


def test_replay_failure():
    """Test replay that raises exception"""
    engine = ReplayEngine()
    
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
    
    def failing_operation(params):
        raise ValueError("Test error")
    
    result = engine.replay(vif, failing_operation)
    
    assert result.success is False
    assert result.error is not None
    assert "Test error" in result.error


def test_verify_witness():
    """Test witness verification"""
    engine = ReplayEngine()
    
    output = "test output"
    vif = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap",
        prompt_hash="hash",
        prompt_tokens=10,
        confidence_score=0.9,
        confidence_band=ConfidenceBand.A,
        output_hash=VIF.hash_text(output),
        output_tokens=5,
        total_tokens=15,
    )
    
    # Verify correct output
    assert engine.verify_witness(vif, output) is True
    
    # Verify incorrect output
    assert engine.verify_witness(vif, "wrong output") is False


def test_batch_replay():
    """Test batch replay of multiple operations"""
    engine = ReplayEngine()
    
    vifs = []
    for i in range(5):
        vif = VIF(
            model_id="test",
            model_provider="test",
            context_snapshot_id=f"snap_{i}",
            prompt_hash=VIF.hash_text(f"prompt {i}"),
            prompt_tokens=10,
            confidence_score=0.9,
            confidence_band=ConfidenceBand.A,
            output_hash=VIF.hash_text(f"output {i}"),
            output_tokens=5,
            total_tokens=15,
        )
        vifs.append(vif)
    
    def operation(params):
        snap_id = params["context"]["snapshot_id"]
        return f"output {snap_id.split('_')[1]}"
    
    results = engine.batch_replay(vifs, operation)
    
    assert len(results) == 5
    assert all(r.success for r in results)
    assert all(r.matches_original for r in results)


def test_reproducibility_rate():
    """Test reproducibility rate calculation"""
    engine = ReplayEngine()
    
    results = [
        ReplayResult(success=True, matches_original=True),
        ReplayResult(success=True, matches_original=True),
        ReplayResult(success=True, matches_original=False),
        ReplayResult(success=False, matches_original=False),
    ]
    
    rate = engine.calculate_reproducibility_rate(results)
    assert rate == 0.5  # 2 out of 4 matched


def test_reproducibility_rate_empty():
    """Test reproducibility rate with empty results"""
    engine = ReplayEngine()
    
    rate = engine.calculate_reproducibility_rate([])
    assert rate == 0.0


def test_create_replay_witness():
    """Test creating replay witness"""
    original_vif = VIF(
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
    
    replay_result = ReplayResult(
        success=True,
        matches_original=True,
        output_hash="hash2",
        execution_time_ms=123.45,
    )
    
    witness = create_replay_witness("test_operation", original_vif, replay_result)
    
    assert witness["operation"] == "test_operation"
    assert witness["original_vif_id"] == original_vif.id
    assert witness["success"] is True
    assert witness["matches_original"] is True


def test_replay_cache_basic():
    """Test basic replay cache functionality"""
    cache = ReplayCache(max_size=10)
    
    result = ReplayResult(success=True, matches_original=True)
    
    cache.put("vif_123", result)
    
    assert cache.has("vif_123")
    assert cache.get("vif_123") == result
    assert cache.size() == 1


def test_replay_cache_eviction():
    """Test cache evicts oldest when full"""
    cache = ReplayCache(max_size=3)
    
    for i in range(5):
        result = ReplayResult(success=True, matches_original=True)
        cache.put(f"vif_{i}", result)
    
    # Cache should only have 3 items (evicted 2 oldest)
    assert cache.size() == 3


def test_replay_cache_clear():
    """Test clearing cache"""
    cache = ReplayCache()
    
    cache.put("vif_1", ReplayResult(success=True, matches_original=True))
    cache.put("vif_2", ReplayResult(success=True, matches_original=True))
    
    assert cache.size() == 2
    
    cache.clear()
    
    assert cache.size() == 0


def test_replay_with_custom_context_loader():
    """Test replay with custom context loader"""
    def load_context(snapshot_id):
        return {
            "snapshot_id": snapshot_id,
            "atoms": ["atom1", "atom2"],
            "data": "test data"
        }
    
    engine = ReplayEngine(context_loader=load_context)
    
    vif = VIF(
        model_id="test",
        model_provider="test",
        context_snapshot_id="snap_999",
        prompt_hash="hash",
        prompt_tokens=10,
        confidence_score=0.9,
        confidence_band=ConfidenceBand.A,
        output_hash=VIF.hash_text("output"),
        output_tokens=5,
        total_tokens=15,
    )
    
    def operation(params):
        context = params["context"]
        assert context["snapshot_id"] == "snap_999"
        assert context["data"] == "test data"
        return "output"
    
    result = engine.replay(vif, operation)
    
    assert result.success is True
    assert result.matches_original is True


def test_replay_result_to_dict():
    """Test ReplayResult serialization"""
    result = ReplayResult(
        success=True,
        output="test",
        output_hash="abc123",
        matches_original=True,
        original_hash="abc123",
        execution_time_ms=100.0,
    )
    
    data = result.to_dict()
    
    assert data["success"] is True
    assert data["matches_original"] is True
    assert data["output_hash"] == "abc123"


def test_realistic_replay_scenario():
    """Test realistic replay scenario with all features"""
    # Setup
    engine = ReplayEngine(
        context_loader=lambda sid: {"snapshot_id": sid, "context": "loaded"}
    )
    cache = ReplayCache()
    
    # Original operation
    original_output = "The answer is 42"
    vif = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_real_123",
        prompt_hash=VIF.hash_text("What is the answer?"),
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash=VIF.hash_text(original_output),
        output_tokens=5,
        total_tokens=15,
        replay_seed=42,
        temperature=0.0,
    )
    
    # Replay operation
    def operation(params):
        # Deterministic operation
        return "The answer is 42"
    
    # Check cache (should miss)
    assert not cache.has(vif.id)
    
    # Execute replay
    result = engine.replay(vif, operation, verify_hash=True)
    
    # Verify success
    assert result.success is True
    assert result.matches_original is True
    
    # Cache result
    cache.put(vif.id, result)
    
    # Second replay should hit cache
    assert cache.has(vif.id)
    cached_result = cache.get(vif.id)
    assert cached_result.matches_original is True


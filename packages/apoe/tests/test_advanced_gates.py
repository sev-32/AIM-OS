"""Tests for Advanced Gate System"""

from __future__ import annotations
import pytest

from apoe.advanced_gates import (
    CompoundGate,
    GateAction,
    GateChain,
    create_quality_gate,
    create_performance_gate,
    create_completeness_gate
)


def test_simple_gate_passes():
    """Test simple gate with passing condition."""
    gate = CompoundGate(
        id="g1",
        name="test_gate",
        conditions=["output.confidence >= 0.80"]
    )
    
    outputs = {"confidence": 0.85}
    passed, message = gate.evaluate(outputs)
    
    assert passed
    assert "satisfied" in message.lower()


def test_simple_gate_fails():
    """Test simple gate with failing condition."""
    gate = CompoundGate(
        id="g1",
        name="test_gate",
        conditions=["output.confidence >= 0.80"]
    )
    
    outputs = {"confidence": 0.65}
    passed, message = gate.evaluate(outputs)
    
    assert not passed
    assert "failed" in message.lower()


def test_compound_gate_and_logic():
    """Test compound gate with AND logic."""
    gate = CompoundGate(
        id="g1",
        name="compound_gate",
        conditions=[
            "output.confidence >= 0.80",
            "output.verified == True"
        ],
        operator="AND"
    )
    
    # Both conditions met
    outputs = {"confidence": 0.85, "verified": True}
    passed, _ = gate.evaluate(outputs)
    assert passed
    
    # One condition fails
    outputs = {"confidence": 0.85, "verified": False}
    passed, _ = gate.evaluate(outputs)
    assert not passed


def test_compound_gate_or_logic():
    """Test compound gate with OR logic."""
    gate = CompoundGate(
        id="g1",
        name="or_gate",
        conditions=[
            "output.confidence >= 0.90",
            "output.verified == True"
        ],
        operator="OR"
    )
    
    # First condition met
    outputs = {"confidence": 0.92, "verified": False}
    passed, _ = gate.evaluate(outputs)
    assert passed
    
    # Second condition met
    outputs = {"confidence": 0.70, "verified": True}
    passed, _ = gate.evaluate(outputs)
    assert passed
    
    # Neither condition met
    outputs = {"confidence": 0.70, "verified": False}
    passed, _ = gate.evaluate(outputs)
    assert not passed


def test_gate_with_nested_output():
    """Test gate accessing nested output fields."""
    gate = CompoundGate(
        id="g1",
        name="nested_gate",
        conditions=["output.results.score >= 0.75"]
    )
    
    outputs = {"results": {"score": 0.80}}
    passed, _ = gate.evaluate(outputs)
    
    assert passed


def test_gate_retry_action():
    """Test gate with retry action."""
    gate = CompoundGate(
        id="g1",
        name="retry_gate",
        conditions=["output.success == True"],
        on_fail=GateAction.RETRY,
        max_retries=3
    )
    
    outputs = {"success": False}
    passed, _ = gate.evaluate(outputs)
    
    assert not passed
    
    # Handle failure
    action, should_continue = gate.handle_failure()
    
    assert action == GateAction.RETRY
    assert should_continue
    assert gate.retry_count == 1


def test_gate_retry_exhausted():
    """Test gate when retries exhausted."""
    gate = CompoundGate(
        id="g1",
        name="retry_gate",
        conditions=["output.success == True"],
        on_fail=GateAction.RETRY,
        max_retries=2
    )
    
    # Exhaust retries
    gate.retry_count = 2
    
    action, should_continue = gate.handle_failure()
    
    # Should not retry anymore
    assert action == GateAction.RETRY
    assert not should_continue


def test_gate_abort_action():
    """Test gate with abort action."""
    gate = CompoundGate(
        id="g1",
        name="abort_gate",
        conditions=["output.critical == True"],
        on_fail=GateAction.ABORT
    )
    
    outputs = {"critical": False}
    passed, _ = gate.evaluate(outputs)
    
    assert not passed
    
    action, _ = gate.handle_failure()
    assert action == GateAction.ABORT


def test_gate_chain_all_pass():
    """Test gate chain where all gates pass."""
    gate1 = CompoundGate(id="g1", name="gate1", conditions=["output.a >= 10"])
    gate2 = CompoundGate(id="g2", name="gate2", conditions=["output.b == True"])
    
    chain = GateChain([gate1, gate2])
    
    outputs = {"a": 15, "b": True}
    all_passed, results = chain.evaluate_all(outputs)
    
    assert all_passed
    assert len(results["passed"]) == 2
    assert len(results["failed"]) == 0


def test_gate_chain_one_fails():
    """Test gate chain where one gate fails."""
    gate1 = CompoundGate(id="g1", name="gate1", conditions=["output.a >= 10"])
    gate2 = CompoundGate(id="g2", name="gate2", conditions=["output.b == True"], on_fail=GateAction.ABORT)
    
    chain = GateChain([gate1, gate2])
    
    outputs = {"a": 15, "b": False}
    all_passed, results = chain.evaluate_all(outputs)
    
    assert not all_passed
    assert len(results["passed"]) == 1
    assert len(results["failed"]) == 1
    assert chain.failed_gate == "g2"


def test_gate_chain_stops_on_abort():
    """Test that gate chain stops when abort gate fails."""
    gate1 = CompoundGate(id="g1", name="gate1", conditions=["output.a >= 10"], on_fail=GateAction.ABORT)
    gate2 = CompoundGate(id="g2", name="gate2", conditions=["output.b == True"])
    gate3 = CompoundGate(id="g3", name="gate3", conditions=["output.c >= 5"])
    
    chain = GateChain([gate1, gate2, gate3])
    
    outputs = {"a": 5, "b": True, "c": 10}  # gate1 fails
    all_passed, results = chain.evaluate_all(outputs)
    
    assert not all_passed
    # Should stop after gate1 fails (abort)
    assert len(results["passed"]) == 0
    assert len(results["failed"]) == 1


def test_create_quality_gate():
    """Test quality gate creation helper."""
    gate = create_quality_gate(min_confidence=0.85)
    
    # Should pass
    outputs = {"confidence": 0.90}
    passed, _ = gate.evaluate(outputs)
    assert passed
    
    # Should fail
    outputs = {"confidence": 0.70}
    passed, _ = gate.evaluate(outputs)
    assert not passed


def test_create_quality_gate_with_verification():
    """Test quality gate with verification requirement."""
    gate = create_quality_gate(
        min_confidence=0.80,
        require_verification=True
    )
    
    # Both conditions met
    outputs = {"confidence": 0.85, "verified": True}
    passed, _ = gate.evaluate(outputs)
    assert passed
    
    # Confidence met but not verified
    outputs = {"confidence": 0.85, "verified": False}
    passed, _ = gate.evaluate(outputs)
    assert not passed


def test_create_performance_gate():
    """Test performance gate creation helper."""
    gate = create_performance_gate(
        max_time=10.0,
        max_tokens=1000
    )
    
    # Within limits
    outputs = {"execution_time": 5.0, "tokens_used": 500}
    passed, _ = gate.evaluate(outputs)
    assert passed
    
    # Exceeds time limit
    outputs = {"execution_time": 15.0, "tokens_used": 500}
    passed, _ = gate.evaluate(outputs)
    assert not passed


def test_create_completeness_gate():
    """Test completeness gate creation helper."""
    gate = create_completeness_gate(
        required_fields=["name", "value"]
    )
    
    # Note: Current implementation checks != None
    # In production, would check field presence
    
    assert "name" in gate.metadata["required_fields"]
    assert "value" in gate.metadata["required_fields"]


def test_gate_comparison_operators():
    """Test all comparison operators."""
    # Test >=
    gate_gte = CompoundGate(id="gte", name="gte", conditions=["output.x >= 10"])
    assert gate_gte.evaluate({"x": 10})[0]
    assert gate_gte.evaluate({"x": 11})[0]
    assert not gate_gte.evaluate({"x": 9})[0]
    
    # Test <=
    gate_lte = CompoundGate(id="lte", name="lte", conditions=["output.x <= 10"])
    assert gate_lte.evaluate({"x": 10})[0]
    assert gate_lte.evaluate({"x": 9})[0]
    assert not gate_lte.evaluate({"x": 11})[0]
    
    # Test >
    gate_gt = CompoundGate(id="gt", name="gt", conditions=["output.x > 10"])
    assert gate_gt.evaluate({"x": 11})[0]
    assert not gate_gt.evaluate({"x": 10})[0]
    
    # Test <
    gate_lt = CompoundGate(id="lt", name="lt", conditions=["output.x < 10"])
    assert gate_lt.evaluate({"x": 9})[0]
    assert not gate_lt.evaluate({"x": 10})[0]
    
    # Test ==
    gate_eq = CompoundGate(id="eq", name="eq", conditions=["output.x == 10"])
    assert gate_eq.evaluate({"x": 10})[0]
    assert not gate_eq.evaluate({"x": 9})[0]
    
    # Test !=
    gate_ne = CompoundGate(id="ne", name="ne", conditions=["output.x != 10"])
    assert gate_ne.evaluate({"x": 9})[0]
    assert not gate_ne.evaluate({"x": 10})[0]


def test_gate_with_missing_field():
    """Test gate behavior when field is missing."""
    gate = CompoundGate(
        id="g1",
        name="missing_field_gate",
        conditions=["output.nonexistent >= 10"]
    )
    
    outputs = {"other_field": 5}
    passed, message = gate.evaluate(outputs)
    
    # Should fail gracefully
    assert not passed


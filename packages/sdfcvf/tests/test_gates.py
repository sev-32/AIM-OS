"""Tests for parity gates"""

import pytest

from sdfcvf.quartet import Quartet
from sdfcvf.parity import ParityResult
from sdfcvf.gates import (
    ParityGate,
    GateConfig,
    GateType,
    GateResult,
    create_pre_commit_gate,
    create_deployment_gate,
    create_pr_gate,
)


def test_gate_config_creation():
    """Test creating gate configuration"""
    config = GateConfig(
        gate_type=GateType.PRE_COMMIT,
        parity_threshold=0.85,
        require_complete_quartet=True,
        allow_override=True,
    )
    
    assert config.gate_type == GateType.PRE_COMMIT
    assert config.parity_threshold == 0.85
    assert config.allow_override is True


def test_gate_result_creation():
    """Test creating gate result"""
    result = GateResult(
        passed=True,
        parity_score=0.95,
        threshold=0.90,
        reasons=["Parity gate passed"],
    )
    
    assert result.passed is True
    assert result.parity_score == 0.95


def test_gate_result_to_dict():
    """Test gate result serialization"""
    result = GateResult(
        passed=False,
        parity_score=0.75,
        threshold=0.90,
        reasons=["Parity too low"],
        warnings=["Low code-docs alignment"],
    )
    
    data = result.to_dict()
    
    assert data["passed"] is False
    assert data["parity_score"] == 0.75
    assert len(data["reasons"]) == 1


def test_parity_gate_initialization():
    """Test ParityGate initialization"""
    config = GateConfig(gate_type=GateType.PRE_COMMIT)
    gate = ParityGate(config)
    
    assert gate.config.gate_type == GateType.PRE_COMMIT


def test_gate_passes_high_parity():
    """Test gate passes with high parity"""
    config = GateConfig(
        gate_type=GateType.PRE_COMMIT,
        parity_threshold=0.90,
    )
    gate = ParityGate(config)
    
    # High parity result
    parity_result = ParityResult(
        parity_score=0.95,
        code_docs_similarity=0.95,
        code_tests_similarity=0.95,
        code_traces_similarity=0.95,
        complete=True,
    )
    
    quartet = Quartet(
        code_files=["code.py"],
        doc_files=["doc.md"],
        test_files=["test.py"],
        trace_files=["trace.md"],
    )
    
    result = gate.check(quartet, parity_result)
    
    assert result.passed is True
    assert result.parity_score == 0.95


def test_gate_fails_low_parity():
    """Test gate fails with low parity"""
    config = GateConfig(
        gate_type=GateType.DEPLOYMENT,
        parity_threshold=0.95,
    )
    gate = ParityGate(config)
    
    # Low parity result
    parity_result = ParityResult(
        parity_score=0.75,
        code_docs_similarity=0.75,
        code_tests_similarity=0.75,
        code_traces_similarity=0.75,
        complete=True,
    )
    
    quartet = Quartet(
        code_files=["code.py"],
        doc_files=["doc.md"],
        test_files=["test.py"],
        trace_files=["trace.md"],
    )
    
    result = gate.check(quartet, parity_result)
    
    assert result.passed is False
    assert "below threshold" in result.reasons[0].lower()


def test_gate_fails_incomplete_quartet():
    """Test gate fails with incomplete quartet"""
    config = GateConfig(
        gate_type=GateType.DEPLOYMENT,
        parity_threshold=0.90,
        require_complete_quartet=True,
    )
    gate = ParityGate(config)
    
    # High parity but incomplete
    parity_result = ParityResult(
        parity_score=0.50,
        code_docs_similarity=0.0,
        code_tests_similarity=0.0,
        code_traces_similarity=0.0,
        complete=False,
        warnings=["Incomplete quartet: missing docs, tests, traces"],
    )
    
    quartet = Quartet(
        code_files=["code.py"],
    )
    
    result = gate.check(quartet, parity_result)
    
    assert result.passed is False
    assert "incomplete quartet" in result.reasons[0].lower()


def test_gate_allows_incomplete_if_configured():
    """Test gate allows incomplete quartet if configured"""
    config = GateConfig(
        gate_type=GateType.PRE_COMMIT,
        parity_threshold=0.80,
        require_complete_quartet=False,  # Allow incomplete
    )
    gate = ParityGate(config)
    
    # Incomplete but parity decent
    parity_result = ParityResult(
        parity_score=0.85,  # Above threshold
        code_docs_similarity=0.85,
        code_tests_similarity=0.85,
        code_traces_similarity=0.85,
        complete=False,
    )
    
    quartet = Quartet(code_files=["code.py"])
    
    result = gate.check(quartet, parity_result)
    
    # Should pass (incomplete allowed, parity good)
    assert result.passed is True


def test_gate_strict_mode_fails_on_warnings():
    """Test strict mode fails even with good parity if warnings exist"""
    config = GateConfig(
        gate_type=GateType.DEPLOYMENT,
        parity_threshold=0.90,
        strict_mode=True,
    )
    gate = ParityGate(config)
    
    # Good parity but has warnings
    parity_result = ParityResult(
        parity_score=0.92,
        code_docs_similarity=0.92,
        code_tests_similarity=0.92,
        code_traces_similarity=0.92,
        complete=True,
        warnings=["Minor alignment issue detected"],
    )
    
    quartet = Quartet(
        code_files=["code.py"],
        doc_files=["doc.md"],
        test_files=["test.py"],
        trace_files=["trace.md"],
    )
    
    result = gate.check(quartet, parity_result)
    
    assert result.passed is False
    assert "strict mode" in result.reasons[0].lower()


def test_gate_override_availability():
    """Test override availability in gate result"""
    config_override = GateConfig(
        gate_type=GateType.PRE_COMMIT,
        allow_override=True,
    )
    gate_override = ParityGate(config_override)
    
    # Failing parity with override allowed
    parity_result = ParityResult(
        parity_score=0.70,
        code_docs_similarity=0.70,
        code_tests_similarity=0.70,
        code_traces_similarity=0.70,
        complete=True,
    )
    
    quartet = Quartet(
        code_files=["code.py"],
        doc_files=["doc.md"],
        test_files=["test.py"],
        trace_files=["trace.md"],
    )
    
    result = gate_override.check(quartet, parity_result)
    
    assert result.passed is False
    assert result.can_override is True


def test_gate_no_override():
    """Test gate without override"""
    config_no_override = GateConfig(
        gate_type=GateType.DEPLOYMENT,
        allow_override=False,
    )
    gate_no_override = ParityGate(config_no_override)
    
    parity_result = ParityResult(
        parity_score=0.70,
        code_docs_similarity=0.70,
        code_tests_similarity=0.70,
        code_traces_similarity=0.70,
        complete=True,
    )
    
    quartet = Quartet(
        code_files=["code.py"],
        doc_files=["doc.md"],
        test_files=["test.py"],
        trace_files=["trace.md"],
    )
    
    result = gate_no_override.check(quartet, parity_result)
    
    assert result.passed is False
    assert result.can_override is False


def test_gate_failure_message():
    """Test failure message generation"""
    config = GateConfig(gate_type=GateType.PRE_COMMIT)
    gate = ParityGate(config)
    
    result = GateResult(
        passed=False,
        parity_score=0.75,
        threshold=0.90,
        reasons=["Parity too low", "Missing tests"],
        warnings=["Code-docs misalignment"],
        can_override=True,
    )
    
    message = gate.get_failure_message(result)
    
    assert "BLOCKED" in message
    assert "0.75" in message
    assert "0.90" in message
    assert "override" in message.lower()


def test_gate_success_message():
    """Test success message generation"""
    config = GateConfig(gate_type=GateType.PRE_COMMIT)
    gate = ParityGate(config)
    
    result = GateResult(
        passed=True,
        parity_score=0.95,
        threshold=0.90,
        reasons=["Parity gate passed"],
    )
    
    message = gate.get_failure_message(result)
    assert "PASSED" in message


def test_create_pre_commit_gate():
    """Test pre-commit gate factory"""
    gate = create_pre_commit_gate()
    
    assert gate.config.gate_type == GateType.PRE_COMMIT
    assert gate.config.parity_threshold == 0.85  # Relaxed
    assert gate.config.allow_override is True


def test_create_deployment_gate():
    """Test deployment gate factory"""
    gate = create_deployment_gate()
    
    assert gate.config.gate_type == GateType.DEPLOYMENT
    assert gate.config.parity_threshold == 0.95  # Strict!
    assert gate.config.allow_override is False
    assert gate.config.strict_mode is True


def test_create_pr_gate():
    """Test PR gate factory"""
    gate = create_pr_gate()
    
    assert gate.config.gate_type == GateType.PR_REVIEW
    assert gate.config.parity_threshold == 0.90
    assert gate.config.allow_override is True


def test_realistic_pre_commit_scenario():
    """Test realistic pre-commit gate scenario"""
    gate = create_pre_commit_gate()
    
    # Developer commits code + tests, but no docs/traces yet
    quartet = Quartet(
        code_files=["feature.py"],
        test_files=["test_feature.py"],
        # Missing docs and traces
    )
    
    # Calculate parity (will be incomplete)
    from sdfcvf.parity import ParityCalculator
    calc = ParityCalculator()
    parity_result = calc.calculate(quartet)
    
    # Check gate
    result = gate.check(quartet, parity_result)
    
    # Pre-commit allows incomplete (require_complete_quartet=False)
    # But parity will be low (0.50), below threshold (0.85)
    assert result.passed is False  # Parity too low
    assert result.can_override is True  # But can force


def test_realistic_deployment_scenario():
    """Test realistic deployment gate scenario"""
    gate = create_deployment_gate()
    
    # Production deployment - everything must be perfect
    parity_result = ParityResult(
        parity_score=0.96,
        code_docs_similarity=0.96,
        code_tests_similarity=0.97,
        code_traces_similarity=0.95,
        complete=True,
        warnings=[],
    )
    
    quartet = Quartet(
        code_files=["feature.py"],
        doc_files=["feature.md"],
        test_files=["test_feature.py"],
        trace_files=["audit/feature_deployment.md"],
    )
    
    result = gate.check(quartet, parity_result)
    
    # Should pass (high parity, complete, no warnings)
    assert result.passed is True


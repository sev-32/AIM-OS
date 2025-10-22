"""Tests for κ-gating (behavioral abstention)"""

import pytest

from vif.kappa_gate import (
    KappaGate,
    KappaGateResult,
    HITLEscalator,
    TaskCriticality,
    create_confidence_based_gate,
    adaptive_kappa_threshold,
    DEFAULT_KAPPA_THRESHOLDS,
)


def test_default_thresholds():
    """Test default κ thresholds are set correctly"""
    assert DEFAULT_KAPPA_THRESHOLDS[TaskCriticality.CRITICAL] == 0.95
    assert DEFAULT_KAPPA_THRESHOLDS[TaskCriticality.IMPORTANT] == 0.85
    assert DEFAULT_KAPPA_THRESHOLDS[TaskCriticality.ROUTINE] == 0.70
    assert DEFAULT_KAPPA_THRESHOLDS[TaskCriticality.LOW_STAKES] == 0.60


def test_kappa_gate_initialization():
    """Test KappaGate initialization"""
    gate = KappaGate()
    
    assert gate.thresholds == DEFAULT_KAPPA_THRESHOLDS
    assert gate.escalation_margin == 0.10


def test_critical_task_high_confidence_passes():
    """Test critical task with high confidence passes gate"""
    gate = KappaGate()
    result = gate.check(
        confidence=0.97,
        task_criticality=TaskCriticality.CRITICAL
    )
    
    assert result.passed is True
    assert result.confidence == 0.97
    assert result.threshold == 0.95
    assert result.task_criticality == TaskCriticality.CRITICAL


def test_critical_task_low_confidence_fails():
    """Test critical task with low confidence fails gate"""
    gate = KappaGate()
    result = gate.check(
        confidence=0.85,
        task_criticality=TaskCriticality.CRITICAL
    )
    
    assert result.passed is False
    assert result.should_escalate is True
    assert "below" in result.escalation_reason.lower()


def test_routine_task_medium_confidence_passes():
    """Test routine task with medium confidence passes"""
    gate = KappaGate()
    result = gate.check(
        confidence=0.75,
        task_criticality=TaskCriticality.ROUTINE
    )
    
    assert result.passed is True


def test_margin_calculation():
    """Test safety margin calculation"""
    gate = KappaGate()
    result = gate.check(confidence=0.80, task_criticality=TaskCriticality.ROUTINE)
    
    # Margin should be confidence - threshold = 0.80 - 0.70 = 0.10
    assert abs(result.margin - 0.10) < 0.01


def test_negative_margin_when_failed():
    """Test negative margin when gate fails"""
    gate = KappaGate()
    result = gate.check(confidence=0.60, task_criticality=TaskCriticality.ROUTINE)
    
    # Margin should be negative (0.60 - 0.70 = -0.10)
    assert result.margin < 0
    assert not result.passed


def test_custom_threshold():
    """Test using custom threshold"""
    gate = KappaGate()
    result = gate.check(
        confidence=0.80,
        task_criticality=TaskCriticality.ROUTINE,
        custom_threshold=0.90
    )
    
    assert result.passed is False  # 0.80 < 0.90
    assert result.threshold == 0.90


def test_escalation_margin_important_task():
    """Test escalation for important task close to threshold"""
    gate = KappaGate(escalation_margin=0.10)
    
    # Confidence 0.87 is above threshold (0.85) but within margin
    result = gate.check(
        confidence=0.87,
        task_criticality=TaskCriticality.IMPORTANT
    )
    
    assert result.passed is True
    assert result.should_escalate is True  # Close to threshold
    assert "marginally" in result.escalation_reason.lower()


def test_no_escalation_routine_task_close_to_threshold():
    """Test routine task close to threshold doesn't escalate"""
    gate = KappaGate(escalation_margin=0.10)
    
    # Routine task with confidence just above threshold
    result = gate.check(
        confidence=0.72,
        task_criticality=TaskCriticality.ROUTINE
    )
    
    assert result.passed is True
    assert result.should_escalate is False  # Routine task, no escalation


def test_set_custom_threshold():
    """Test setting custom threshold"""
    gate = KappaGate()
    
    gate.set_threshold(TaskCriticality.ROUTINE, 0.80)
    assert gate.get_threshold(TaskCriticality.ROUTINE) == 0.80


def test_set_invalid_threshold_error():
    """Test setting invalid threshold raises error"""
    gate = KappaGate()
    
    with pytest.raises(ValueError):
        gate.set_threshold(TaskCriticality.ROUTINE, 1.5)
    
    with pytest.raises(ValueError):
        gate.set_threshold(TaskCriticality.ROUTINE, -0.1)


def test_gate_result_to_dict():
    """Test KappaGateResult serialization"""
    result = KappaGateResult(
        passed=True,
        confidence=0.95,
        threshold=0.90,
        task_criticality=TaskCriticality.IMPORTANT,
        gap=0.05,
    )
    
    data = result.to_dict()
    
    assert data["passed"] is True
    assert data["confidence"] == 0.95
    assert data["threshold"] == 0.90
    assert data["task_criticality"] == "important"


def test_gate_operation_passes():
    """Test gating an operation that passes"""
    gate = KappaGate()
    
    def operation():
        return "success"
    
    output, result = gate.gate_operation(
        operation,
        confidence=0.95,
        task_criticality=TaskCriticality.CRITICAL
    )
    
    assert output == "success"
    assert result.passed is True


def test_gate_operation_fails():
    """Test gating an operation that fails"""
    gate = KappaGate()
    
    def operation():
        return "should not execute"
    
    def fallback(gate_result):
        return f"refused: confidence too low"
    
    output, result = gate.gate_operation(
        operation,
        confidence=0.50,
        task_criticality=TaskCriticality.CRITICAL,
        on_fail=fallback
    )
    
    assert output == "refused: confidence too low"
    assert result.passed is False


def test_gate_operation_fail_no_fallback():
    """Test gate failure without fallback"""
    gate = KappaGate()
    
    def operation():
        return "should not execute"
    
    output, result = gate.gate_operation(
        operation,
        confidence=0.50,
        task_criticality=TaskCriticality.CRITICAL
    )
    
    assert output is None
    assert result.passed is False


def test_hitl_escalator_initialization():
    """Test HITLEscalator initialization"""
    escalator = HITLEscalator()
    
    assert escalator.escalation_queue == []
    assert escalator.escalation_callback is None


def test_hitl_escalate():
    """Test escalating to human review"""
    escalator = HITLEscalator()
    gate = KappaGate()
    
    result = gate.check(confidence=0.60, task_criticality=TaskCriticality.CRITICAL)
    escalation_id = escalator.escalate(result, context={"task": "medical diagnosis"})
    
    assert escalation_id.startswith("escalation_")
    assert len(escalator.escalation_queue) == 1
    assert escalator.escalation_queue[0]["status"] == "pending"


def test_hitl_resolve():
    """Test resolving escalation"""
    escalator = HITLEscalator()
    gate = KappaGate()
    
    result = gate.check(confidence=0.60, task_criticality=TaskCriticality.CRITICAL)
    escalation_id = escalator.escalate(result)
    
    resolved = escalator.resolve(escalation_id, decision="reject", feedback="Too risky")
    
    assert resolved is True
    assert escalator.escalation_queue[0]["status"] == "resolved"
    assert escalator.escalation_queue[0]["human_decision"]["decision"] == "reject"


def test_hitl_resolve_invalid_id():
    """Test resolving non-existent escalation"""
    escalator = HITLEscalator()
    
    resolved = escalator.resolve("invalid_id", decision="approve")
    assert resolved is False


def test_hitl_get_pending():
    """Test getting pending escalations"""
    escalator = HITLEscalator()
    gate = KappaGate()
    
    # Add pending escalations
    result1 = gate.check(confidence=0.60, task_criticality=TaskCriticality.CRITICAL)
    id1 = escalator.escalate(result1)
    
    result2 = gate.check(confidence=0.65, task_criticality=TaskCriticality.IMPORTANT)
    id2 = escalator.escalate(result2)
    
    # Resolve one
    escalator.resolve(id1, decision="approve")
    
    pending = escalator.get_pending()
    assert len(pending) == 1
    assert pending[0]["id"] == id2


def test_hitl_get_resolved():
    """Test getting resolved escalations"""
    escalator = HITLEscalator()
    gate = KappaGate()
    
    result = gate.check(confidence=0.60, task_criticality=TaskCriticality.CRITICAL)
    escalation_id = escalator.escalate(result)
    escalator.resolve(escalation_id, decision="approve")
    
    resolved = escalator.get_resolved()
    assert len(resolved) == 1
    assert resolved[0]["id"] == escalation_id


def test_hitl_escalation_callback():
    """Test HITL escalation callback"""
    callback_called = []
    
    def callback(gate_result, context):
        callback_called.append((gate_result, context))
    
    escalator = HITLEscalator(escalation_callback=callback)
    gate = KappaGate()
    
    result = gate.check(confidence=0.60, task_criticality=TaskCriticality.CRITICAL)
    escalator.escalate(result, context={"test": "data"})
    
    assert len(callback_called) == 1


def test_create_standard_gate():
    """Test creating standard confidence gate"""
    gate = create_confidence_based_gate(strict=False)
    
    assert gate.get_threshold(TaskCriticality.CRITICAL) == 0.95
    assert gate.get_threshold(TaskCriticality.ROUTINE) == 0.70


def test_create_strict_gate():
    """Test creating strict confidence gate"""
    gate = create_confidence_based_gate(strict=True)
    
    assert gate.get_threshold(TaskCriticality.CRITICAL) == 0.98
    assert gate.get_threshold(TaskCriticality.ROUTINE) == 0.80


def test_adaptive_threshold_poor_calibration():
    """Test adaptive threshold with poor calibration"""
    base = 0.70
    adjusted = adaptive_kappa_threshold(base, ece_score=0.20)
    
    # Poor calibration should raise threshold
    assert adjusted > base


def test_adaptive_threshold_excellent_calibration():
    """Test adaptive threshold with excellent calibration"""
    base = 0.70
    adjusted = adaptive_kappa_threshold(base, ece_score=0.03)
    
    # Excellent calibration can lower threshold slightly
    assert adjusted <= base


def test_adaptive_threshold_poor_accuracy():
    """Test adaptive threshold with poor past accuracy"""
    base = 0.70
    adjusted = adaptive_kappa_threshold(base, past_accuracy=0.60)
    
    # Poor accuracy should raise threshold
    assert adjusted > base


def test_adaptive_threshold_excellent_accuracy():
    """Test adaptive threshold with excellent past accuracy"""
    base = 0.70
    adjusted = adaptive_kappa_threshold(base, past_accuracy=0.95)
    
    # Excellent accuracy can lower threshold
    assert adjusted <= base


def test_adaptive_threshold_clamping():
    """Test adaptive threshold stays in valid range"""
    # Test lower bound
    low = adaptive_kappa_threshold(0.50, ece_score=0.01, past_accuracy=0.99)
    assert low >= 0.50
    
    # Test upper bound
    high = adaptive_kappa_threshold(0.90, ece_score=0.30, past_accuracy=0.50)
    assert high <= 0.99


def test_multiple_task_criticalities():
    """Test different task criticalities with same confidence"""
    gate = KappaGate()
    confidence = 0.75
    
    # Should fail critical
    result_critical = gate.check(confidence, TaskCriticality.CRITICAL)
    assert not result_critical.passed
    
    # Should fail important
    result_important = gate.check(confidence, TaskCriticality.IMPORTANT)
    assert not result_important.passed
    
    # Should pass routine
    result_routine = gate.check(confidence, TaskCriticality.ROUTINE)
    assert result_routine.passed
    
    # Should pass low-stakes
    result_low = gate.check(confidence, TaskCriticality.LOW_STAKES)
    assert result_low.passed


def test_realistic_medical_scenario():
    """Test realistic medical (critical) scenario"""
    gate = KappaGate()
    escalator = HITLEscalator()
    
    # Medical diagnosis - critical task
    confidence = 0.88  # Below 0.95 threshold
    
    result = gate.check(confidence, TaskCriticality.CRITICAL)
    
    assert not result.passed
    assert result.should_escalate
    
    # Escalate to doctor for review
    escalation_id = escalator.escalate(
        result,
        context={
            "task": "diagnosis",
            "patient_id": "12345",
            "symptoms": ["fever", "cough"]
        }
    )
    
    # Doctor reviews and approves
    escalator.resolve(escalation_id, decision="approve", feedback="Diagnosis correct")
    
    resolved = escalator.get_resolved()
    assert len(resolved) == 1


def test_realistic_routine_scenario():
    """Test realistic routine task scenario"""
    gate = KappaGate()
    
    # Content moderation - routine task
    confidence = 0.72
    
    result = gate.check(confidence, TaskCriticality.ROUTINE)
    
    assert result.passed
    assert not result.should_escalate  # Routine task, sufficient confidence


def test_edge_case_exactly_at_threshold():
    """Test confidence exactly at threshold"""
    gate = KappaGate()
    
    result = gate.check(
        confidence=0.70,
        task_criticality=TaskCriticality.ROUTINE
    )
    
    # Exactly at threshold should pass
    assert result.passed
    assert result.margin == 0.0


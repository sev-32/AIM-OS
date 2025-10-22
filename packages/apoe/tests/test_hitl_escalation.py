"""Tests for HITL Escalation System"""

from __future__ import annotations
import pytest

from apoe.hitl_escalation import (
    EscalationReason,
    EscalationPriority,
    EscalationRequest,
    HITLManager,
    create_hitl_manager,
)


def test_create_escalation():
    """Test creating HITL escalation."""
    manager = HITLManager()
    
    escalation_id = manager.create_escalation(
        step_id="step1",
        plan_name="test_plan",
        reason=EscalationReason.LOW_CONFIDENCE,
        question="Should we proceed with low confidence?",
        options=["yes", "no", "retry"],
        priority=EscalationPriority.HIGH
    )
    
    assert escalation_id.startswith("hitl_")
    assert escalation_id in manager.pending_escalations


def test_resolve_escalation():
    """Test resolving escalation with human decision."""
    manager = HITLManager()
    
    escalation_id = manager.create_escalation(
        step_id="step1",
        plan_name="test_plan",
        reason=EscalationReason.LOW_CONFIDENCE,
        question="Proceed?",
        options=["yes", "no"]
    )
    
    manager.resolve_escalation(
        escalation_id=escalation_id,
        human_decision="no",
        human_reasoning="Confidence too low, need more research"
    )
    
    assert escalation_id not in manager.pending_escalations
    assert len(manager.resolved_escalations) == 1
    assert manager.resolved_escalations[0].human_decision == "no"


def test_resolve_nonexistent_escalation_raises_error():
    """Test resolving nonexistent escalation raises error."""
    manager = HITLManager()
    
    with pytest.raises(ValueError, match="not found"):
        manager.resolve_escalation("nonexistent", "yes")


def test_get_pending_escalations_sorted_by_priority():
    """Test pending escalations sorted correctly."""
    manager = HITLManager()
    
    # Create escalations with different priorities
    manager.create_escalation("s1", "p1", EscalationReason.LOW_CONFIDENCE, "Q1?", ["yes", "no"], EscalationPriority.LOW)
    manager.create_escalation("s2", "p2", EscalationReason.HIGH_STAKES, "Q2?", ["yes", "no"], EscalationPriority.CRITICAL)
    manager.create_escalation("s3", "p3", EscalationReason.POLICY_VIOLATION, "Q3?", ["yes", "no"], EscalationPriority.HIGH)
    
    pending = manager.get_pending_escalations()
    
    # Should be sorted: CRITICAL, HIGH, LOW
    assert pending[0].priority == EscalationPriority.CRITICAL
    assert pending[1].priority == EscalationPriority.HIGH
    assert pending[2].priority == EscalationPriority.LOW


def test_get_pending_escalations_filtered_by_priority():
    """Test filtering pending escalations by priority."""
    manager = HITLManager()
    
    manager.create_escalation("s1", "p1", EscalationReason.LOW_CONFIDENCE, "Q?", ["yes"], EscalationPriority.LOW)
    manager.create_escalation("s2", "p2", EscalationReason.HIGH_STAKES, "Q?", ["yes"], EscalationPriority.CRITICAL)
    
    critical_only = manager.get_pending_escalations(priority=EscalationPriority.CRITICAL)
    
    assert len(critical_only) == 1
    assert critical_only[0].priority == EscalationPriority.CRITICAL


def test_get_escalation_statistics_no_escalations():
    """Test statistics with no escalations."""
    manager = HITLManager()
    
    stats = manager.get_escalation_statistics()
    
    assert stats["total"] == 0
    assert stats["pending"] == 0
    assert stats["resolved"] == 0


def test_get_escalation_statistics_with_escalations():
    """Test statistics calculation."""
    manager = HITLManager()
    
    # Create and resolve some escalations
    for i in range(3):
        esc_id = manager.create_escalation(
            f"s{i}",
            "plan",
            EscalationReason.LOW_CONFIDENCE,
            "Q?",
            ["yes", "no"]
        )
        if i < 2:  # Resolve 2, leave 1 pending
            manager.resolve_escalation(esc_id, "yes")
    
    stats = manager.get_escalation_statistics()
    
    assert stats["total"] == 3
    assert stats["pending"] == 1
    assert stats["resolved"] == 2


def test_should_escalate_for_low_confidence_medium_stakes():
    """Test escalation decision for low confidence, medium stakes."""
    manager = HITLManager()
    
    should_escalate, priority = manager.should_escalate_for_confidence(
        confidence=0.60,  # Below threshold
        threshold=0.70,
        stakes="medium"
    )
    
    assert should_escalate
    assert priority is not None


def test_should_not_escalate_for_high_confidence():
    """Test no escalation for high confidence."""
    manager = HITLManager()
    
    should_escalate, priority = manager.should_escalate_for_confidence(
        confidence=0.95,
        threshold=0.70,
        stakes="medium"
    )
    
    assert not should_escalate
    assert priority is None


def test_high_stakes_raises_confidence_requirement():
    """Test that high stakes require higher confidence."""
    manager = HITLManager()
    
    # Medium stakes: 0.75 confidence is OK
    should_escalate_medium, _ = manager.should_escalate_for_confidence(
        confidence=0.75,
        stakes="medium"
    )
    assert not should_escalate_medium
    
    # High stakes: 0.75 confidence triggers escalation
    should_escalate_high, _ = manager.should_escalate_for_confidence(
        confidence=0.75,
        stakes="high"
    )
    assert should_escalate_high


def test_critical_stakes_requires_very_high_confidence():
    """Test critical stakes require very high confidence."""
    manager = HITLManager()
    
    # Even 0.90 confidence should escalate for critical stakes
    should_escalate, priority = manager.should_escalate_for_confidence(
        confidence=0.90,
        stakes="critical"
    )
    
    assert should_escalate
    assert priority == EscalationPriority.CRITICAL


def test_escalation_priority_based_on_confidence_gap():
    """Test escalation priority reflects confidence gap."""
    manager = HITLManager()
    
    # Large gap (0.65 vs 0.70) → higher priority
    _, priority_large_gap = manager.should_escalate_for_confidence(
        confidence=0.40,  # 0.30 below threshold
        threshold=0.70,
        stakes="medium"
    )
    
    # Small gap (0.68 vs 0.70) → lower priority
    _, priority_small_gap = manager.should_escalate_for_confidence(
        confidence=0.68,  # 0.02 below threshold
        threshold=0.70,
        stakes="medium"
    )
    
    # Large gap should be higher priority
    priority_order = {
        EscalationPriority.CRITICAL: 0,
        EscalationPriority.HIGH: 1,
        EscalationPriority.MEDIUM: 2,
        EscalationPriority.LOW: 3
    }
    
    assert priority_order[priority_large_gap] < priority_order[priority_small_gap]


def test_escalation_statistics_by_reason():
    """Test statistics grouped by escalation reason."""
    manager = HITLManager()
    
    # Create escalations with different reasons
    manager.create_escalation("s1", "p", EscalationReason.LOW_CONFIDENCE, "Q?", ["y"])
    manager.create_escalation("s2", "p", EscalationReason.LOW_CONFIDENCE, "Q?", ["y"])
    manager.create_escalation("s3", "p", EscalationReason.HIGH_STAKES, "Q?", ["y"])
    
    stats = manager.get_escalation_statistics()
    
    assert stats["by_reason"]["low_confidence"] == 2
    assert stats["by_reason"]["high_stakes"] == 1


def test_escalation_statistics_by_priority():
    """Test statistics grouped by priority."""
    manager = HITLManager()
    
    manager.create_escalation("s1", "p", EscalationReason.LOW_CONFIDENCE, "Q?", ["y"], EscalationPriority.CRITICAL)
    manager.create_escalation("s2", "p", EscalationReason.LOW_CONFIDENCE, "Q?", ["y"], EscalationPriority.HIGH)
    manager.create_escalation("s3", "p", EscalationReason.LOW_CONFIDENCE, "Q?", ["y"], EscalationPriority.HIGH)
    
    stats = manager.get_escalation_statistics()
    
    assert stats["by_priority"]["critical"] == 1
    assert stats["by_priority"]["high"] == 2


def test_create_hitl_manager():
    """Test HITL manager creation helper."""
    manager = create_hitl_manager()
    
    assert isinstance(manager, HITLManager)
    assert len(manager.pending_escalations) == 0


def test_escalation_context_preserved():
    """Test that escalation preserves full context."""
    manager = HITLManager()
    
    context = {
        "current_step": "analyze_data",
        "previous_steps": ["gather", "clean"],
        "data_quality": 0.65,
        "stakes": "high"
    }
    
    esc_id = manager.create_escalation(
        step_id="step_analyze",
        plan_name="data_pipeline",
        reason=EscalationReason.LOW_CONFIDENCE,
        question="Data quality low. Proceed anyway?",
        options=["proceed", "abort", "retry_cleaning"],
        context=context
    )
    
    request = manager.pending_escalations[esc_id]
    
    assert request.context == context
    assert request.context["data_quality"] == 0.65


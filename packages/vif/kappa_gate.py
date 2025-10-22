"""κ-Gating: Behavioral Abstention System

Implements confidence-based behavioral abstention where the system
refuses to answer when confidence is below task-appropriate thresholds.

This is κ-gating: the system "knows when it doesn't know" and abstains
rather than generating potentially incorrect output.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Callable, Any
from enum import Enum


class TaskCriticality(str, Enum):
    """Task criticality levels with associated κ thresholds"""
    CRITICAL = "critical"      # Medical, legal, safety → κ=0.95
    IMPORTANT = "important"    # Financial, strategic → κ=0.85
    ROUTINE = "routine"        # Standard operations → κ=0.70
    LOW_STAKES = "low_stakes"  # Experimental, low-impact → κ=0.60


# Default κ thresholds by task criticality
DEFAULT_KAPPA_THRESHOLDS = {
    TaskCriticality.CRITICAL: 0.95,
    TaskCriticality.IMPORTANT: 0.85,
    TaskCriticality.ROUTINE: 0.70,
    TaskCriticality.LOW_STAKES: 0.60,
}


@dataclass
class KappaGateResult:
    """Result of κ-gate evaluation"""
    passed: bool
    confidence: float
    threshold: float
    task_criticality: TaskCriticality
    gap: float  # How far above/below threshold
    should_escalate: bool = False  # Should this go to human?
    escalation_reason: Optional[str] = None
    
    @property
    def margin(self) -> float:
        """Safety margin above threshold (positive if passed)"""
        return self.confidence - self.threshold
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "passed": self.passed,
            "confidence": self.confidence,
            "threshold": self.threshold,
            "task_criticality": self.task_criticality.value,
            "gap": self.gap,
            "margin": self.margin,
            "should_escalate": self.should_escalate,
            "escalation_reason": self.escalation_reason,
        }


class KappaGate:
    """κ-Gate implementation for behavioral abstention
    
    The κ-gate checks if confidence meets task-appropriate thresholds.
    If not, the operation should be refused or escalated to human review.
    
    Examples:
        >>> gate = KappaGate()
        >>> result = gate.check(
        ...     confidence=0.95,
        ...     task_criticality=TaskCriticality.CRITICAL
        ... )
        >>> assert result.passed
        
        >>> result = gate.check(
        ...     confidence=0.65,
        ...     task_criticality=TaskCriticality.CRITICAL
        ... )
        >>> assert not result.passed
        >>> assert result.should_escalate
    """
    
    def __init__(
        self,
        thresholds: Optional[dict[TaskCriticality, float]] = None,
        escalation_margin: float = 0.10,
    ):
        """Initialize κ-gate
        
        Args:
            thresholds: Custom κ thresholds by criticality
            escalation_margin: How close to threshold triggers escalation
        """
        self.thresholds = thresholds or DEFAULT_KAPPA_THRESHOLDS.copy()
        self.escalation_margin = escalation_margin
    
    def check(
        self,
        confidence: float,
        task_criticality: TaskCriticality = TaskCriticality.ROUTINE,
        *,
        custom_threshold: Optional[float] = None,
    ) -> KappaGateResult:
        """Check if confidence meets κ threshold
        
        Args:
            confidence: Model's confidence score (0.0-1.0)
            task_criticality: Criticality level of task
            custom_threshold: Override default threshold
            
        Returns:
            KappaGateResult with pass/fail and escalation info
        """
        # Get threshold
        threshold = custom_threshold if custom_threshold is not None else self.get_threshold(task_criticality)
        
        # Check if passed
        passed = confidence >= threshold
        gap = abs(confidence - threshold)
        
        # Check if should escalate (close to threshold or failed)
        should_escalate = False
        escalation_reason = None
        
        if not passed:
            # Failed gate - always escalate
            should_escalate = True
            escalation_reason = f"Confidence {confidence:.3f} below κ={threshold:.3f} for {task_criticality.value} task"
        
        elif confidence < (threshold + self.escalation_margin):
            # Passed but close to threshold - escalate for critical tasks
            if task_criticality in [TaskCriticality.CRITICAL, TaskCriticality.IMPORTANT]:
                should_escalate = True
                escalation_reason = f"Confidence {confidence:.3f} marginally above κ={threshold:.3f} for {task_criticality.value} task"
        
        return KappaGateResult(
            passed=passed,
            confidence=confidence,
            threshold=threshold,
            task_criticality=task_criticality,
            gap=gap,
            should_escalate=should_escalate,
            escalation_reason=escalation_reason,
        )
    
    def get_threshold(self, task_criticality: TaskCriticality) -> float:
        """Get κ threshold for task criticality"""
        return self.thresholds.get(task_criticality, 0.70)
    
    def set_threshold(self, task_criticality: TaskCriticality, threshold: float) -> None:
        """Set custom κ threshold for task criticality"""
        if not (0.0 <= threshold <= 1.0):
            raise ValueError(f"Threshold must be in [0.0, 1.0], got {threshold}")
        self.thresholds[task_criticality] = threshold
    
    def gate_operation(
        self,
        operation: Callable[[], Any],
        confidence: float,
        task_criticality: TaskCriticality = TaskCriticality.ROUTINE,
        *,
        on_fail: Optional[Callable[[KappaGateResult], Any]] = None,
    ) -> tuple[Any, KappaGateResult]:
        """Gate an operation through κ-check
        
        Args:
            operation: Function to execute if gate passes
            confidence: Model's confidence in operation
            task_criticality: Criticality level
            on_fail: Function to call if gate fails
            
        Returns:
            (operation_result, gate_result) if passed
            (on_fail_result, gate_result) if failed
            
        Examples:
            >>> gate = KappaGate()
            >>> def risky_operation():
            ...     return "executed"
            >>> def safe_fallback(result):
            ...     return "refused - low confidence"
            >>> output, result = gate.gate_operation(
            ...     risky_operation,
            ...     confidence=0.60,
            ...     task_criticality=TaskCriticality.CRITICAL,
            ...     on_fail=safe_fallback
            ... )
            >>> assert output == "refused - low confidence"
            >>> assert not result.passed
        """
        result = self.check(confidence, task_criticality)
        
        if result.passed:
            # Execute operation
            output = operation()
            return output, result
        else:
            # Gate failed - call fallback if provided
            if on_fail:
                output = on_fail(result)
            else:
                output = None
            return output, result


class HITLEscalator:
    """Human-In-The-Loop escalation handler
    
    Manages escalation of low-confidence operations to human review.
    """
    
    def __init__(
        self,
        escalation_callback: Optional[Callable[[KappaGateResult, Any], Any]] = None
    ):
        """Initialize HITL escalator
        
        Args:
            escalation_callback: Function to call when escalating to human
        """
        self.escalation_callback = escalation_callback
        self.escalation_queue: list[dict] = []
    
    def escalate(
        self,
        gate_result: KappaGateResult,
        context: Optional[dict] = None
    ) -> str:
        """Escalate operation to human review
        
        Args:
            gate_result: Result from κ-gate
            context: Additional context about operation
            
        Returns:
            Escalation ID for tracking
        """
        import uuid
        from datetime import datetime, timezone
        
        escalation_id = f"escalation_{uuid.uuid4().hex[:8]}"
        
        escalation = {
            "id": escalation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gate_result": gate_result.to_dict(),
            "context": context or {},
            "status": "pending",
            "human_decision": None,
        }
        
        self.escalation_queue.append(escalation)
        
        # Call escalation callback if provided
        if self.escalation_callback:
            self.escalation_callback(gate_result, context)
        
        return escalation_id
    
    def resolve(
        self,
        escalation_id: str,
        decision: str,
        feedback: Optional[str] = None
    ) -> bool:
        """Mark escalation as resolved by human
        
        Args:
            escalation_id: ID of escalation to resolve
            decision: Human decision ("approve", "reject", "modify")
            feedback: Optional human feedback
            
        Returns:
            True if escalation found and resolved
        """
        for escalation in self.escalation_queue:
            if escalation["id"] == escalation_id:
                escalation["status"] = "resolved"
                escalation["human_decision"] = {
                    "decision": decision,
                    "feedback": feedback,
                    "resolved_at": datetime.now(timezone.utc).isoformat(),
                }
                return True
        return False
    
    def get_pending(self) -> list[dict]:
        """Get all pending escalations"""
        return [e for e in self.escalation_queue if e["status"] == "pending"]
    
    def get_resolved(self) -> list[dict]:
        """Get all resolved escalations"""
        return [e for e in self.escalation_queue if e["status"] == "resolved"]


def create_confidence_based_gate(
    strict: bool = False
) -> KappaGate:
    """Create κ-gate with preset thresholds
    
    Args:
        strict: If True, use stricter thresholds
        
    Returns:
        Configured KappaGate
    """
    if strict:
        # Stricter thresholds for high-stakes applications
        thresholds = {
            TaskCriticality.CRITICAL: 0.98,
            TaskCriticality.IMPORTANT: 0.90,
            TaskCriticality.ROUTINE: 0.80,
            TaskCriticality.LOW_STAKES: 0.70,
        }
    else:
        # Standard thresholds
        thresholds = DEFAULT_KAPPA_THRESHOLDS.copy()
    
    return KappaGate(thresholds=thresholds)


from datetime import datetime, timezone


def adaptive_kappa_threshold(
    base_threshold: float,
    ece_score: Optional[float] = None,
    past_accuracy: Optional[float] = None,
) -> float:
    """Adaptively adjust κ threshold based on calibration
    
    If the model is well-calibrated (low ECE), we can trust its confidence.
    If poorly calibrated (high ECE), raise the threshold.
    
    Args:
        base_threshold: Starting κ threshold
        ece_score: Expected Calibration Error (if available)
        past_accuracy: Historical accuracy (if available)
        
    Returns:
        Adjusted κ threshold
    """
    adjusted = base_threshold
    
    # Adjust based on ECE
    if ece_score is not None:
        if ece_score > 0.15:  # Poor calibration
            adjusted += 0.10  # Raise threshold
        elif ece_score < 0.05:  # Excellent calibration
            adjusted -= 0.05  # Can lower threshold slightly
    
    # Adjust based on past accuracy
    if past_accuracy is not None:
        if past_accuracy < 0.70:  # Poor past performance
            adjusted += 0.10
        elif past_accuracy > 0.90:  # Excellent past performance
            adjusted -= 0.05
    
    # Clamp to valid range
    adjusted = max(0.50, min(0.99, adjusted))
    
    return adjusted


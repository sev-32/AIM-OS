"""Human-in-the-Loop (HITL) Escalation for APOE

Enables AI to escalate decisions to humans when confidence too low or stakes too high.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EscalationReason(Enum):
    """Reasons for HITL escalation."""
    LOW_CONFIDENCE = "low_confidence"
    HIGH_STAKES = "high_stakes"
    CONTRADICTORY_INFO = "contradictory_info"
    ETHICAL_CONCERN = "ethical_concern"
    RESOURCE_LIMIT = "resource_limit"
    POLICY_VIOLATION = "policy_violation"
    MANUAL_TRIGGER = "manual_trigger"


class EscalationPriority(Enum):
    """Priority levels for escalations."""
    CRITICAL = "critical"  # Immediate attention required
    HIGH = "high"  # Needs response within hour
    MEDIUM = "medium"  # Needs response within day
    LOW = "low"  # Can wait, informational


@dataclass
class EscalationRequest:
    """Request for human intervention."""
    escalation_id: str
    step_id: str
    plan_name: str
    reason: EscalationReason
    priority: EscalationPriority
    context: Dict[str, Any]
    question: str
    options: list[str]
    created_at: datetime
    resolved_at: Optional[datetime] = None
    human_decision: Optional[str] = None
    human_reasoning: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class HITLManager:
    """Manages human-in-the-loop escalations."""
    
    def __init__(self):
        self.pending_escalations: Dict[str, EscalationRequest] = {}
        self.resolved_escalations: list[EscalationRequest] = []
        self._escalation_counter = 0
    
    def create_escalation(
        self,
        step_id: str,
        plan_name: str,
        reason: EscalationReason,
        question: str,
        options: list[str],
        priority: EscalationPriority = EscalationPriority.HIGH,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create HITL escalation request."""
        self._escalation_counter += 1
        escalation_id = f"hitl_{self._escalation_counter:04d}"
        
        request = EscalationRequest(
            escalation_id=escalation_id,
            step_id=step_id,
            plan_name=plan_name,
            reason=reason,
            priority=priority,
            context=context or {},
            question=question,
            options=options,
            created_at=datetime.utcnow()
        )
        
        self.pending_escalations[escalation_id] = request
        
        return escalation_id
    
    def resolve_escalation(
        self,
        escalation_id: str,
        human_decision: str,
        human_reasoning: Optional[str] = None
    ):
        """Resolve escalation with human decision."""
        if escalation_id not in self.pending_escalations:
            raise ValueError(f"Escalation {escalation_id} not found")
        
        request = self.pending_escalations[escalation_id]
        request.resolved_at = datetime.utcnow()
        request.human_decision = human_decision
        request.human_reasoning = human_reasoning
        
        # Move to resolved
        del self.pending_escalations[escalation_id]
        self.resolved_escalations.append(request)
    
    def get_pending_escalations(
        self,
        priority: Optional[EscalationPriority] = None
    ) -> list[EscalationRequest]:
        """Get pending escalations, optionally filtered by priority."""
        requests = list(self.pending_escalations.values())
        
        if priority:
            requests = [r for r in requests if r.priority == priority]
        
        # Sort by priority (critical first) then by age
        priority_order = {
            EscalationPriority.CRITICAL: 0,
            EscalationPriority.HIGH: 1,
            EscalationPriority.MEDIUM: 2,
            EscalationPriority.LOW: 3
        }
        
        requests.sort(key=lambda r: (priority_order[r.priority], r.created_at))
        
        return requests
    
    def get_escalation_statistics(self) -> Dict[str, Any]:
        """Get statistics on escalations."""
        all_escalations = self.resolved_escalations + list(self.pending_escalations.values())
        
        if not all_escalations:
            return {
                "total": 0,
                "pending": 0,
                "resolved": 0,
                "avg_resolution_time_seconds": 0.0,
                "by_reason": {},
                "by_priority": {}
            }
        
        # Resolution time calculation
        resolved_with_time = [
            e for e in self.resolved_escalations
            if e.resolved_at and e.created_at
        ]
        
        avg_resolution_time = 0.0
        if resolved_with_time:
            total_time = sum(
                (e.resolved_at - e.created_at).total_seconds()
                for e in resolved_with_time
            )
            avg_resolution_time = total_time / len(resolved_with_time)
        
        # Count by reason
        by_reason: Dict[str, int] = {}
        for e in all_escalations:
            by_reason[e.reason.value] = by_reason.get(e.reason.value, 0) + 1
        
        # Count by priority
        by_priority: Dict[str, int] = {}
        for e in all_escalations:
            by_priority[e.priority.value] = by_priority.get(e.priority.value, 0) + 1
        
        return {
            "total": len(all_escalations),
            "pending": len(self.pending_escalations),
            "resolved": len(self.resolved_escalations),
            "avg_resolution_time_seconds": avg_resolution_time,
            "by_reason": by_reason,
            "by_priority": by_priority
        }
    
    def should_escalate_for_confidence(
        self,
        confidence: float,
        threshold: float = 0.70,
        stakes: str = "medium"
    ) -> tuple[bool, Optional[EscalationPriority]]:
        """
        Determine if operation should be escalated based on confidence and stakes.
        
        Args:
            confidence: AI's confidence score
            threshold: Minimum confidence to proceed
            stakes: "low", "medium", "high", "critical"
        
        Returns:
            (should_escalate, priority)
        """
        # High stakes lower the threshold
        stake_adjustments = {
            "low": 0.60,
            "medium": 0.70,
            "high": 0.85,
            "critical": 0.95
        }
        
        adjusted_threshold = stake_adjustments.get(stakes, threshold)
        
        if confidence >= adjusted_threshold:
            return False, None
        
        # Determine escalation priority based on how far below threshold
        gap = adjusted_threshold - confidence
        
        if gap > 0.30 or stakes == "critical":
            return True, EscalationPriority.CRITICAL
        elif gap > 0.15 or stakes == "high":
            return True, EscalationPriority.HIGH
        elif gap > 0.05:
            return True, EscalationPriority.MEDIUM
        else:
            return True, EscalationPriority.LOW


def create_hitl_manager() -> HITLManager:
    """Create HITL manager instance."""
    return HITLManager()


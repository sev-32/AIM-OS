"""
Policy Enforcement Gates - Programmatic behavioral enforcement of policies.

This module provides runtime policy enforcement that goes beyond prompt instructions.
When policies are violated, it actually truncates, escalates, or denies execution.

This is the "behavioral enforcement" layer that makes governance real.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Dict, Optional


class PolicyDecision(str, Enum):
    """Policy enforcement decisions."""
    ALLOW = "allow"
    TRUNCATE = "truncate"
    ESCALATE = "escalate"
    DENY = "deny"


@dataclass
class EvidenceScores:
    """Evidence quality metrics."""
    coverage: float  # 0-1: How much of topic is covered
    credibility: float  # 0-1: Source credibility
    consistency: float  # 0-1: Internal consistency
    
    @property
    def overall(self) -> float:
        """Weighted average of evidence scores."""
        return (self.coverage * 0.4 + 
                self.credibility * 0.4 + 
                self.consistency * 0.2)


@dataclass
class RuntimeState:
    """Current execution state for policy evaluation."""
    orchestration_started: float  # timestamp
    orchestration_budget_s: float  # seconds
    agents_executed: int = 0
    total_cost_usd: float = 0.0


@dataclass
class PolicyEnforcementDecision:
    """Result of policy gate evaluation."""
    decision: PolicyDecision
    reason: str
    evidence_score: float
    latency_exceeded: bool
    depth_exceeded: bool
    uncertainty_too_high: bool
    cost_exceeded: bool
    
    # SEG/VIF integration (for provenance)
    vif_id: Optional[str] = None
    seg_uri: Optional[str] = None
    
    @property
    def allowed(self) -> bool:
        """Is execution allowed?"""
        return self.decision == PolicyDecision.ALLOW


class PolicyEnforcer:
    """
    Enforces policies at runtime with actual behavioral consequences.
    
    This is the difference between:
    - "AI knows the rules" (prompt awareness)
    - "AI follows the rules" (behavioral enforcement)
    """
    
    def __init__(
        self,
        evidence_threshold: float = 0.7,
        latency_budget_s: float = 30.0,
        max_research_depth: int = 3,
        kappa_threshold: float = 0.2,  # κ-gating (uncertainty abstention)
        max_cost_usd: Optional[float] = None
    ):
        self.evidence_threshold = evidence_threshold
        self.latency_budget_s = latency_budget_s
        self.max_research_depth = max_research_depth
        self.kappa_threshold = kappa_threshold
        self.max_cost_usd = max_cost_usd
    
    def guard_agent(
        self,
        agent_fn: Callable,
        *,
        runtime_state: RuntimeState,
        depth: int,
        evidence: Optional[EvidenceScores] = None,
        uncertainty: float = 0.0,
        estimated_cost: float = 0.0,
        agent_id: str = "unknown",
        stage: str = "unknown"
    ) -> PolicyEnforcementDecision:
        """
        Evaluate policies before agent execution.
        
        Returns decision: allow, truncate, escalate, or deny
        
        This is PROGRAMMATIC enforcement - actually stops execution if violated.
        """
        
        # Check 1: Research depth limit
        if depth > self.max_research_depth:
            return PolicyEnforcementDecision(
                decision=PolicyDecision.DENY,
                reason=f"Research depth {depth} exceeds limit {self.max_research_depth}",
                evidence_score=evidence.overall if evidence else 0.0,
                latency_exceeded=False,
                depth_exceeded=True,
                uncertainty_too_high=False,
                cost_exceeded=False
            )
        
        # Check 2: Latency budget
        elapsed = time.time() - runtime_state.orchestration_started
        remaining = runtime_state.orchestration_budget_s - elapsed
        
        if remaining < self.latency_budget_s:
            # Not enough budget remaining for this agent
            return PolicyEnforcementDecision(
                decision=PolicyDecision.TRUNCATE,
                reason=f"Orchestration budget nearly exhausted: {remaining:.1f}s remaining, agent needs {self.latency_budget_s}s",
                evidence_score=evidence.overall if evidence else 0.0,
                latency_exceeded=True,
                depth_exceeded=False,
                uncertainty_too_high=False,
                cost_exceeded=False
            )
        
        # Check 3: Evidence threshold (if evidence provided)
        if evidence and evidence.overall < self.evidence_threshold:
            return PolicyEnforcementDecision(
                decision=PolicyDecision.ESCALATE,
                reason=f"Evidence score {evidence.overall:.2f} below threshold {self.evidence_threshold:.2f}",
                evidence_score=evidence.overall,
                latency_exceeded=False,
                depth_exceeded=False,
                uncertainty_too_high=False,
                cost_exceeded=False
            )
        
        # Check 4: κ-gating (uncertainty abstention)
        if uncertainty > self.kappa_threshold:
            return PolicyEnforcementDecision(
                decision=PolicyDecision.ESCALATE,
                reason=f"Uncertainty {uncertainty:.2f} exceeds κ threshold {self.kappa_threshold:.2f} (agent should abstain)",
                evidence_score=evidence.overall if evidence else 0.0,
                latency_exceeded=False,
                depth_exceeded=False,
                uncertainty_too_high=True,
                cost_exceeded=False
            )
        
        # Check 5: Cost limit (if specified)
        if self.max_cost_usd and (runtime_state.total_cost_usd + estimated_cost) > self.max_cost_usd:
            return PolicyEnforcementDecision(
                decision=PolicyDecision.DENY,
                reason=f"Cost limit would be exceeded: {runtime_state.total_cost_usd + estimated_cost:.4f} > {self.max_cost_usd:.4f}",
                evidence_score=evidence.overall if evidence else 0.0,
                latency_exceeded=False,
                depth_exceeded=False,
                uncertainty_too_high=False,
                cost_exceeded=True
            )
        
        # All checks passed
        return PolicyEnforcementDecision(
            decision=PolicyDecision.ALLOW,
            reason="All policy constraints satisfied",
            evidence_score=evidence.overall if evidence else 1.0,
            latency_exceeded=False,
            depth_exceeded=False,
            uncertainty_too_high=False,
            cost_exceeded=False
        )
    
    def log_enforcement_decision(
        self,
        decision: PolicyEnforcementDecision,
        agent_id: str,
        stage: str
    ) -> Dict:
        """
        Log enforcement decision for SEG/VIF audit trail.
        
        Returns dict suitable for JSONL witness format.
        """
        return {
            "event": "policy_enforcement",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": agent_id,
            "stage": stage,
            "decision": decision.decision.value,
            "reason": decision.reason,
            "evidence_score": decision.evidence_score,
            "violations": {
                "latency_exceeded": decision.latency_exceeded,
                "depth_exceeded": decision.depth_exceeded,
                "uncertainty_too_high": decision.uncertainty_too_high,
                "cost_exceeded": decision.cost_exceeded
            },
            "vif_id": decision.vif_id,
            "seg_uri": decision.seg_uri
        }


# Example usage
def example_usage():
    """
    Demonstrate policy gate usage in orchestration.
    """
    
    # Create policy enforcer
    enforcer = PolicyEnforcer(
        evidence_threshold=0.95,  # Strict
        latency_budget_s=5.0,  # Tight
        max_research_depth=1,  # Shallow
        kappa_threshold=0.2  # High confidence required
    )
    
    # Runtime state
    state = RuntimeState(
        orchestration_started=time.time(),
        orchestration_budget_s=900.0  # 15 minutes
    )
    
    # Before executing agent
    def some_agent():
        return {"result": "agent output"}
    
    # Evaluate policy
    decision = enforcer.guard_agent(
        some_agent,
        runtime_state=state,
        depth=2,  # This will trigger DENY (exceeds max_depth=1)
        evidence=EvidenceScores(coverage=0.8, credibility=0.9, consistency=0.85),
        uncertainty=0.15,
        agent_id="test.agent",
        stage="test"
    )
    
    # Handle decision
    if decision.decision == PolicyDecision.DENY:
        print(f"❌ Agent denied: {decision.reason}")
        # Don't execute agent
    
    elif decision.decision == PolicyDecision.ESCALATE:
        print(f"⚠️ Agent escalated: {decision.reason}")
        # Route to supervisor/coordinator for decision
    
    elif decision.decision == PolicyDecision.TRUNCATE:
        print(f"⏱️ Agent truncated: {decision.reason}")
        # Execute with reduced scope/timeout
    
    else:  # ALLOW
        print(f"✅ Agent allowed: {decision.reason}")
        result = some_agent()
    
    # Log for audit trail
    log_entry = enforcer.log_enforcement_decision(
        decision, "test.agent", "test"
    )
    print(f"Audit log: {log_entry}")


if __name__ == "__main__":
    example_usage()


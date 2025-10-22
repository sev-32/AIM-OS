"""Advanced Role Dispatch System for APOE

Intelligently selects and configures roles for steps.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

from apoe.roles import RoleType


@dataclass
class RoleCapability:
    """Describes what a role can do."""
    role_type: RoleType
    strengths: list[str]  # What it's good at
    weaknesses: list[str]  # What it's not good for
    cost_estimate: float  # Relative cost (tokens, time, etc.)
    confidence_range: tuple[float, float]  # Typical confidence range


# Role capability database
ROLE_CAPABILITIES: Dict[RoleType, RoleCapability] = {
    RoleType.PLANNER: RoleCapability(
        role_type=RoleType.PLANNER,
        strengths=["strategy", "decomposition", "long-term thinking"],
        weaknesses=["execution", "details", "implementation"],
        cost_estimate=0.7,
        confidence_range=(0.70, 0.90)
    ),
    RoleType.RETRIEVER: RoleCapability(
        role_type=RoleType.RETRIEVER,
        strengths=["memory", "context", "information gathering"],
        weaknesses=["reasoning", "synthesis", "creativity"],
        cost_estimate=0.3,
        confidence_range=(0.80, 0.95)
    ),
    RoleType.REASONER: RoleCapability(
        role_type=RoleType.REASONER,
        strengths=["analysis", "logic", "problem solving"],
        weaknesses=["speed", "memory", "execution"],
        cost_estimate=0.8,
        confidence_range=(0.75, 0.92)
    ),
    RoleType.VERIFIER: RoleCapability(
        role_type=RoleType.VERIFIER,
        strengths=["accuracy", "validation", "fact-checking"],
        weaknesses=["creativity", "speed"],
        cost_estimate=0.6,
        confidence_range=(0.85, 0.98)
    ),
    RoleType.BUILDER: RoleCapability(
        role_type=RoleType.BUILDER,
        strengths=["implementation", "code", "artifacts"],
        weaknesses=["planning", "verification"],
        cost_estimate=0.9,
        confidence_range=(0.70, 0.88)
    ),
    RoleType.CRITIC: RoleCapability(
        role_type=RoleType.CRITIC,
        strengths=["quality", "gaps", "weaknesses"],
        weaknesses=["construction", "optimism"],
        cost_estimate=0.5,
        confidence_range=(0.75, 0.90)
    ),
    RoleType.OPERATOR: RoleCapability(
        role_type=RoleType.OPERATOR,
        strengths=["execution", "reliability", "consistency"],
        weaknesses=["creativity", "complex reasoning"],
        cost_estimate=0.4,
        confidence_range=(0.80, 0.95)
    ),
    RoleType.WITNESS: RoleCapability(
        role_type=RoleType.WITNESS,
        strengths=["provenance", "audit", "documentation"],
        weaknesses=["speed"],
        cost_estimate=0.2,
        confidence_range=(0.90, 0.99)
    ),
}


class RoleDispatcher:
    """Intelligent role selection and configuration."""
    
    def __init__(self):
        self.capabilities = ROLE_CAPABILITIES
        self._custom_handlers: Dict[str, Callable] = {}
    
    def register_custom_handler(self, role_name: str, handler: Callable):
        """Register custom handler for a specific role name."""
        self._custom_handlers[role_name] = handler
    
    def recommend_role_for_task(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RoleType:
        """Recommend best role type for a given task."""
        desc_lower = task_description.lower()
        context = context or {}
        
        # Keyword-based recommendation
        if any(word in desc_lower for word in ["plan", "strategy", "design"]):
            return RoleType.PLANNER
        
        if any(word in desc_lower for word in ["retrieve", "search", "find", "context"]):
            return RoleType.RETRIEVER
        
        if any(word in desc_lower for word in ["analyze", "reason", "think", "solve"]):
            return RoleType.REASONER
        
        if any(word in desc_lower for word in ["verify", "check", "validate", "confirm"]):
            return RoleType.VERIFIER
        
        if any(word in desc_lower for word in ["build", "implement", "code", "create"]):
            return RoleType.BUILDER
        
        if any(word in desc_lower for word in ["critique", "review", "evaluate", "assess"]):
            return RoleType.CRITIC
        
        if any(word in desc_lower for word in ["execute", "run", "perform", "do"]):
            return RoleType.OPERATOR
        
        if any(word in desc_lower for word in ["document", "record", "witness", "log"]):
            return RoleType.WITNESS
        
        # Default to OPERATOR for general tasks
        return RoleType.OPERATOR
    
    def estimate_step_cost(self, role_type: RoleType, description: str) -> float:
        """Estimate relative cost of executing a step."""
        capability = self.capabilities.get(role_type)
        if not capability:
            return 1.0
        
        base_cost = capability.cost_estimate
        
        # Adjust based on description complexity
        word_count = len(description.split())
        complexity_multiplier = min(1.0 + (word_count / 100), 2.0)
        
        return base_cost * complexity_multiplier
    
    def select_optimal_role_chain(
        self,
        task: str,
        available_roles: list[RoleType],
        constraints: Optional[Dict[str, Any]] = None
    ) -> list[RoleType]:
        """Select optimal sequence of roles for complex task."""
        constraints = constraints or {}
        max_cost = constraints.get("max_cost", float("inf"))
        require_verification = constraints.get("require_verification", False)
        
        # Start with recommended role
        primary_role = self.recommend_role_for_task(task)
        
        # Build role chain
        chain = [primary_role]
        total_cost = self.estimate_step_cost(primary_role, task)
        
        # Add verification if required and cost allows
        if require_verification and total_cost < max_cost:
            verification_cost = self.estimate_step_cost(RoleType.VERIFIER, "verify")
            if total_cost + verification_cost <= max_cost:
                chain.append(RoleType.VERIFIER)
                total_cost += verification_cost
        
        # Add witness if cost allows (always beneficial)
        witness_cost = self.estimate_step_cost(RoleType.WITNESS, "document")
        if total_cost + witness_cost <= max_cost:
            chain.append(RoleType.WITNESS)
        
        return chain
    
    def get_fallback_role(self, failed_role: RoleType, reason: str) -> Optional[RoleType]:
        """Get fallback role if primary role fails."""
        # If retriever fails, try operator
        if failed_role == RoleType.RETRIEVER:
            return RoleType.OPERATOR
        
        # If reasoner fails, try planner
        if failed_role == RoleType.REASONER:
            return RoleType.PLANNER
        
        # If builder fails, try operator
        if failed_role == RoleType.BUILDER:
            return RoleType.OPERATOR
        
        # Default fallback: operator (most reliable)
        return RoleType.OPERATOR
    
    def assess_role_performance(
        self,
        role_type: RoleType,
        actual_confidence: float,
        execution_time: float
    ) -> Dict[str, Any]:
        """Assess how well a role performed."""
        capability = self.capabilities.get(role_type)
        if not capability:
            return {"assessment": "unknown", "within_range": False}
        
        # Check if confidence in expected range
        min_conf, max_conf = capability.confidence_range
        within_range = min_conf <= actual_confidence <= max_conf
        
        # Assess performance
        if within_range:
            if actual_confidence > (min_conf + max_conf) / 2:
                assessment = "excellent"
            else:
                assessment = "good"
        else:
            if actual_confidence < min_conf:
                assessment = "below_expected"
            else:
                assessment = "above_expected"  # Surprisingly good!
        
        return {
            "assessment": assessment,
            "within_range": within_range,
            "expected_range": (min_conf, max_conf),
            "actual_confidence": actual_confidence,
            "deviation": actual_confidence - ((min_conf + max_conf) / 2)
        }


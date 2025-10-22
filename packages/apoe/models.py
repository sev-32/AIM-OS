"""APOE Core Data Models

Base types for APOE orchestration system.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class RoleType(str, Enum):
    """The 8 specialized AI agent roles."""
    PLANNER = "planner"
    RETRIEVER = "retriever"
    REASONER = "reasoner"
    VERIFIER = "verifier"
    BUILDER = "builder"
    CRITIC = "critic"
    OPERATOR = "operator"
    WITNESS = "witness"


class StepStatus(str, Enum):
    """Execution status for steps."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ABSTAINED = "abstained"  # κ-gate triggered


class Budget(BaseModel):
    """Resource budget for operations."""
    tokens_limit: int = 10000
    tokens_consumed: int = 0
    time_limit_seconds: float = 300.0
    time_elapsed_seconds: float = 0.0
    tools_limit: int = 10
    tools_consumed: int = 0
    
    def check_tokens(self, cost: int) -> bool:
        """Check if tokens available."""
        return self.tokens_consumed + cost <= self.tokens_limit
    
    def consume_tokens(self, cost: int) -> bool:
        """Consume tokens from budget."""
        if self.check_tokens(cost):
            self.tokens_consumed += cost
            return True
        return False
    
    def check_time(self, duration: float) -> bool:
        """Check if time available."""
        return self.time_elapsed_seconds + duration <= self.time_limit_seconds
    
    def consume_time(self, duration: float) -> bool:
        """Consume time from budget."""
        if self.check_time(duration):
            self.time_elapsed_seconds += duration
            return True
        return False
    
    def remaining_tokens(self) -> int:
        """Get remaining token budget."""
        return self.tokens_limit - self.tokens_consumed
    
    def remaining_time(self) -> float:
        """Get remaining time budget."""
        return self.time_limit_seconds - self.time_elapsed_seconds


class Gate(BaseModel):
    """Quality gate that must pass before proceeding."""
    id: str
    name: str
    gate_type: str  # "quality" | "budget" | "confidence" | "custom"
    condition: str  # e.g., "output.confidence >= 0.95"
    on_fail: Optional[str] = "abort"  # "abort" | "retry" | "skip" | "escalate"
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate gate condition against context.
        
        Args:
            context: Variables available for condition evaluation
            
        Returns:
            True if gate passes, False if fails
        """
        try:
            # Simple eval-based gate (production would use safer evaluation)
            return eval(self.condition, {"__builtins__": {}}, context)
        except Exception:
            # On error, fail safe (gate fails)
            return False


class Step(BaseModel):
    """Single step in execution plan."""
    id: str
    name: str
    role: RoleType
    role_name: Optional[str] = None  # Name of role from ASSIGN (e.g., "validator")
    description: Optional[str] = None
    budget: Optional[Budget] = None
    gates: List[Gate] = Field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    
    # Execution results
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def duration(self) -> Optional[float]:
        """Calculate execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


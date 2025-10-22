"""Error Recovery System for APOE

Provides intelligent error handling, retry logic, and circuit breakers.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class RecoveryStrategy(Enum):
    """Error recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"
    ESCALATE = "escalate"


@dataclass
class RecoveryConfig:
    """Configuration for error recovery."""
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0
    enable_fallback: bool = True
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5  # Failures before opening circuit
    circuit_breaker_timeout: int = 60  # Seconds before trying again


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    step_id: str
    error_type: str
    error_message: str
    timestamp: datetime
    retry_count: int
    recovery_attempted: bool
    recovery_successful: Optional[bool] = None


@dataclass
class CircuitBreaker:
    """Circuit breaker to prevent repeated failures."""
    step_id: str
    failure_count: int = 0
    last_failure: Optional[datetime] = None
    state: str = "closed"  # closed, open, half_open
    opened_at: Optional[datetime] = None
    
    def should_allow_execution(self, timeout_seconds: int = 60) -> bool:
        """Check if execution should be allowed."""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Check if timeout has passed
            if self.opened_at and self.last_failure:
                elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
                if elapsed > timeout_seconds:
                    self.state = "half_open"
                    return True
            return False
        
        if self.state == "half_open":
            # Allow one attempt
            return True
        
        return False
    
    def record_success(self):
        """Record successful execution."""
        self.failure_count = 0
        self.state = "closed"
        self.opened_at = None
    
    def record_failure(self, threshold: int = 5):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure = datetime.utcnow()
        
        if self.failure_count >= threshold:
            self.state = "open"
            self.opened_at = datetime.utcnow()


class ErrorRecoveryManager:
    """Manages error recovery for APOE workflows."""
    
    def __init__(self, config: Optional[RecoveryConfig] = None):
        self.config = config or RecoveryConfig()
        self.error_history: list[ErrorRecord] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_counts: Dict[str, int] = {}
    
    def should_retry(
        self,
        step_id: str,
        error: Exception
    ) -> tuple[bool, Optional[float]]:
        """
        Determine if step should be retried.
        
        Returns:
            (should_retry, delay_seconds)
        """
        # Check circuit breaker
        if self.config.enable_circuit_breaker:
            if not self._check_circuit_breaker(step_id):
                return False, None
        
        # Check retry count
        current_retries = self.retry_counts.get(step_id, 0)
        if current_retries >= self.config.max_retries:
            return False, None
        
        # Calculate delay
        delay = self._calculate_retry_delay(current_retries)
        
        return True, delay
    
    def record_retry_attempt(self, step_id: str):
        """Record that a retry was attempted."""
        self.retry_counts[step_id] = self.retry_counts.get(step_id, 0) + 1
    
    def record_error(
        self,
        step_id: str,
        error: Exception,
        recovery_attempted: bool = False
    ) -> ErrorRecord:
        """Record error occurrence."""
        record = ErrorRecord(
            step_id=step_id,
            error_type=type(error).__name__,
            error_message=str(error),
            timestamp=datetime.utcnow(),
            retry_count=self.retry_counts.get(step_id, 0),
            recovery_attempted=recovery_attempted
        )
        
        self.error_history.append(record)
        
        # Update circuit breaker
        if self.config.enable_circuit_breaker:
            self._record_failure_to_circuit_breaker(step_id)
        
        return record
    
    def record_success(self, step_id: str):
        """Record successful execution."""
        # Reset retry count
        self.retry_counts[step_id] = 0
        
        # Reset circuit breaker
        if step_id in self.circuit_breakers:
            self.circuit_breakers[step_id].record_success()
    
    def get_recovery_strategy(
        self,
        step_id: str,
        error: Exception,
        has_fallback: bool = False
    ) -> RecoveryStrategy:
        """Determine best recovery strategy for error."""
        current_retries = self.retry_counts.get(step_id, 0)
        
        # Check circuit breaker first
        if self.config.enable_circuit_breaker:
            if not self._check_circuit_breaker(step_id):
                return RecoveryStrategy.ABORT
        
        # If out of retries, try fallback or abort
        if current_retries >= self.config.max_retries:
            if has_fallback and self.config.enable_fallback:
                return RecoveryStrategy.FALLBACK
            return RecoveryStrategy.ABORT
        
        # Otherwise retry
        return RecoveryStrategy.RETRY
    
    def get_error_statistics(self, step_id: Optional[str] = None) -> Dict[str, Any]:
        """Get error statistics."""
        if step_id:
            errors = [e for e in self.error_history if e.step_id == step_id]
        else:
            errors = self.error_history
        
        if not errors:
            return {
                "total_errors": 0,
                "error_types": {},
                "avg_retries": 0.0,
                "recovery_success_rate": 0.0
            }
        
        # Count error types
        error_types: Dict[str, int] = {}
        for error in errors:
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
        
        # Calculate recovery stats
        recovery_attempted = [e for e in errors if e.recovery_attempted]
        recovery_successful = [e for e in recovery_attempted if e.recovery_successful]
        
        return {
            "total_errors": len(errors),
            "error_types": error_types,
            "avg_retries": sum(e.retry_count for e in errors) / len(errors),
            "recovery_success_rate": len(recovery_successful) / len(recovery_attempted) if recovery_attempted else 0.0,
            "most_common_error": max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        }
    
    def _check_circuit_breaker(self, step_id: str) -> bool:
        """Check if circuit breaker allows execution."""
        if step_id not in self.circuit_breakers:
            self.circuit_breakers[step_id] = CircuitBreaker(step_id=step_id)
        
        breaker = self.circuit_breakers[step_id]
        return breaker.should_allow_execution(self.config.circuit_breaker_timeout)
    
    def _record_failure_to_circuit_breaker(self, step_id: str):
        """Record failure to circuit breaker."""
        if step_id not in self.circuit_breakers:
            self.circuit_breakers[step_id] = CircuitBreaker(step_id=step_id)
        
        breaker = self.circuit_breakers[step_id]
        breaker.record_failure(self.config.circuit_breaker_threshold)
    
    def _calculate_retry_delay(self, retry_count: int) -> float:
        """Calculate delay before retry."""
        base_delay = self.config.retry_delay_seconds
        
        if self.config.exponential_backoff:
            # Exponential backoff: delay * multiplier^retry_count
            return base_delay * (self.config.backoff_multiplier ** retry_count)
        
        return base_delay


def create_recovery_manager(
    max_retries: int = 3,
    enable_circuit_breaker: bool = True
) -> ErrorRecoveryManager:
    """Create error recovery manager with common configuration."""
    config = RecoveryConfig(
        max_retries=max_retries,
        enable_circuit_breaker=enable_circuit_breaker
    )
    return ErrorRecoveryManager(config)


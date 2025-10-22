"""Tests for Error Recovery System"""

from __future__ import annotations
import pytest
from datetime import datetime, timedelta

from apoe.error_recovery import (
    RecoveryStrategy,
    RecoveryConfig,
    ErrorRecord,
    CircuitBreaker,
    ErrorRecoveryManager,
    create_recovery_manager
)


def test_should_retry_within_limit():
    """Test retry allowed within max retries."""
    manager = ErrorRecoveryManager()
    
    error = Exception("Test error")
    should_retry, delay = manager.should_retry("step1", error)
    
    assert should_retry
    assert delay is not None


def test_should_not_retry_after_max_retries():
    """Test retry blocked after max retries."""
    manager = ErrorRecoveryManager(RecoveryConfig(max_retries=2))
    
    # Exhaust retries
    manager.retry_counts["step1"] = 2
    
    error = Exception("Test error")
    should_retry, delay = manager.should_retry("step1", error)
    
    assert not should_retry


def test_exponential_backoff():
    """Test exponential backoff delay calculation."""
    manager = ErrorRecoveryManager(RecoveryConfig(
        retry_delay_seconds=1.0,
        exponential_backoff=True,
        backoff_multiplier=2.0
    ))
    
    # First retry: 1 second
    delay0 = manager._calculate_retry_delay(0)
    assert delay0 == 1.0
    
    # Second retry: 2 seconds
    delay1 = manager._calculate_retry_delay(1)
    assert delay1 == 2.0
    
    # Third retry: 4 seconds
    delay2 = manager._calculate_retry_delay(2)
    assert delay2 == 4.0


def test_record_retry_attempt():
    """Test recording retry attempts."""
    manager = ErrorRecoveryManager()
    
    manager.record_retry_attempt("step1")
    assert manager.retry_counts["step1"] == 1
    
    manager.record_retry_attempt("step1")
    assert manager.retry_counts["step1"] == 2


def test_record_error():
    """Test recording error occurrence."""
    manager = ErrorRecoveryManager()
    
    error = ValueError("Test error")
    record = manager.record_error("step1", error)
    
    assert record.step_id == "step1"
    assert record.error_type == "ValueError"
    assert record.error_message == "Test error"
    assert len(manager.error_history) == 1


def test_record_success_resets_retry_count():
    """Test successful execution resets retry count."""
    manager = ErrorRecoveryManager()
    
    manager.retry_counts["step1"] = 3
    manager.record_success("step1")
    
    assert manager.retry_counts["step1"] == 0


def test_get_recovery_strategy_retry():
    """Test recovery strategy returns retry when appropriate."""
    manager = ErrorRecoveryManager(RecoveryConfig(max_retries=3))
    
    error = Exception("Test")
    strategy = manager.get_recovery_strategy("step1", error, has_fallback=False)
    
    assert strategy == RecoveryStrategy.RETRY


def test_get_recovery_strategy_fallback():
    """Test recovery strategy returns fallback when retries exhausted."""
    manager = ErrorRecoveryManager(RecoveryConfig(max_retries=2, enable_fallback=True))
    
    manager.retry_counts["step1"] = 2
    
    error = Exception("Test")
    strategy = manager.get_recovery_strategy("step1", error, has_fallback=True)
    
    assert strategy == RecoveryStrategy.FALLBACK


def test_get_recovery_strategy_abort():
    """Test recovery strategy returns abort when no options."""
    manager = ErrorRecoveryManager(RecoveryConfig(max_retries=2, enable_fallback=False))
    
    manager.retry_counts["step1"] = 2
    
    error = Exception("Test")
    strategy = manager.get_recovery_strategy("step1", error, has_fallback=False)
    
    assert strategy == RecoveryStrategy.ABORT


def test_circuit_breaker_closed_allows_execution():
    """Test circuit breaker allows execution when closed."""
    breaker = CircuitBreaker(step_id="step1")
    
    assert breaker.should_allow_execution()


def test_circuit_breaker_opens_after_threshold():
    """Test circuit breaker opens after failure threshold."""
    breaker = CircuitBreaker(step_id="step1")
    
    # Record failures
    for _ in range(5):
        breaker.record_failure(threshold=5)
    
    assert breaker.state == "open"
    assert not breaker.should_allow_execution(timeout_seconds=60)


def test_circuit_breaker_half_open_after_timeout():
    """Test circuit breaker transitions to half-open after timeout."""
    breaker = CircuitBreaker(step_id="step1")
    
    # Open the breaker
    for _ in range(5):
        breaker.record_failure(threshold=5)
    
    assert breaker.state == "open"
    
    # Simulate timeout passed (manually set timestamp)
    breaker.opened_at = datetime.utcnow() - timedelta(seconds=61)
    
    # Should transition to half-open
    allowed = breaker.should_allow_execution(timeout_seconds=60)
    
    assert allowed
    assert breaker.state == "half_open"


def test_circuit_breaker_closes_on_success():
    """Test circuit breaker closes on successful execution."""
    breaker = CircuitBreaker(step_id="step1")
    
    # Open breaker
    for _ in range(5):
        breaker.record_failure(threshold=5)
    
    assert breaker.state == "open"
    
    # Record success
    breaker.record_success()
    
    assert breaker.state == "closed"
    assert breaker.failure_count == 0


def test_get_error_statistics_no_errors():
    """Test error statistics with no errors."""
    manager = ErrorRecoveryManager()
    
    stats = manager.get_error_statistics()
    
    assert stats["total_errors"] == 0
    assert stats["avg_retries"] == 0.0


def test_get_error_statistics_with_errors():
    """Test error statistics calculation."""
    manager = ErrorRecoveryManager()
    
    # Record multiple errors
    manager.record_error("step1", ValueError("Error 1"))
    manager.record_error("step1", ValueError("Error 2"))
    manager.retry_counts["step1"] = 2
    manager.record_error("step1", TypeError("Error 3"))
    
    stats = manager.get_error_statistics("step1")
    
    assert stats["total_errors"] == 3
    assert "ValueError" in stats["error_types"]
    assert "TypeError" in stats["error_types"]
    assert stats["error_types"]["ValueError"] == 2


def test_get_error_statistics_most_common():
    """Test identifying most common error type."""
    manager = ErrorRecoveryManager()
    
    # Record errors
    for _ in range(5):
        manager.record_error("step1", ValueError("Test"))
    for _ in range(2):
        manager.record_error("step1", TypeError("Test"))
    
    stats = manager.get_error_statistics("step1")
    
    assert stats["most_common_error"] == "ValueError"


def test_create_recovery_manager():
    """Test recovery manager creation helper."""
    manager = create_recovery_manager(max_retries=5, enable_circuit_breaker=True)
    
    assert manager.config.max_retries == 5
    assert manager.config.enable_circuit_breaker


def test_error_recovery_with_circuit_breaker_integration():
    """Test error recovery integrates with circuit breaker."""
    config = RecoveryConfig(
        max_retries=3,
        enable_circuit_breaker=True,
        circuit_breaker_threshold=3
    )
    manager = ErrorRecoveryManager(config)
    
    # Cause 3 failures (should open circuit)
    for i in range(3):
        manager.record_error("step1", Exception(f"Error {i}"))
    
    # Circuit should be open
    should_retry, _ = manager.should_retry("step1", Exception("Another error"))
    
    assert not should_retry  # Circuit breaker prevents retry


def test_recovery_config_defaults():
    """Test recovery config default values."""
    config = RecoveryConfig()
    
    assert config.max_retries == 3
    assert config.exponential_backoff
    assert config.enable_fallback
    assert config.enable_circuit_breaker


"""Tests for APOE CMC Integration"""

from __future__ import annotations
import pytest
from datetime import datetime

from apoe.cmc_integration import (
    PlanMemory,
    CMCPlanStore,
    MemoryAwareExecutor
)


def test_store_plan_start():
    """Test storing plan execution start."""
    store = CMCPlanStore()
    
    exec_id = store.store_plan_start(
        plan_name="test_plan",
        execution_id="exec_001",
        total_steps=5,
        metadata={"user": "test"}
    )
    
    assert exec_id == "exec_001"
    assert "exec_001" in store._memory_cache
    
    memory = store._memory_cache["exec_001"]
    assert memory.plan_name == "test_plan"
    assert memory.status == "running"
    assert memory.steps_completed == 0
    assert memory.total_steps == 5


def test_update_plan_progress():
    """Test updating plan execution progress."""
    store = CMCPlanStore()
    
    store.store_plan_start("test_plan", "exec_001", total_steps=5)
    
    store.update_plan_progress(
        execution_id="exec_001",
        steps_completed=2,
        current_outputs={"step1": "done", "step2": "done"}
    )
    
    memory = store._memory_cache["exec_001"]
    assert memory.steps_completed == 2
    assert "step1" in memory.outputs
    assert memory.status == "running"


def test_store_plan_complete_success():
    """Test storing successful plan completion."""
    store = CMCPlanStore()
    
    store.store_plan_start("test_plan", "exec_001", total_steps=3)
    
    store.store_plan_complete(
        execution_id="exec_001",
        final_outputs={"result": "success"},
        success=True
    )
    
    memory = store._memory_cache["exec_001"]
    assert memory.status == "completed"
    assert memory.completed_at is not None
    assert memory.outputs["result"] == "success"


def test_store_plan_complete_failure():
    """Test storing failed plan completion."""
    store = CMCPlanStore()
    
    store.store_plan_start("test_plan", "exec_001", total_steps=3)
    
    store.store_plan_complete(
        execution_id="exec_001",
        final_outputs={"error": "Something failed"},
        success=False
    )
    
    memory = store._memory_cache["exec_001"]
    assert memory.status == "failed"


def test_retrieve_plan_history():
    """Test retrieving plan execution history."""
    store = CMCPlanStore()
    
    # Store multiple executions
    for i in range(3):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=5)
        store.store_plan_complete(exec_id, {}, success=True)
    
    history = store.retrieve_plan_history("test_plan")
    
    assert len(history) == 3
    # Should be sorted by most recent first
    assert history[0].execution_id == "exec_002"


def test_retrieve_plan_history_with_limit():
    """Test retrieving plan history with limit."""
    store = CMCPlanStore()
    
    # Store 15 executions
    for i in range(15):
        exec_id = f"exec_{i:03d}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
    
    history = store.retrieve_plan_history("test_plan", limit=10)
    
    assert len(history) == 10


def test_retrieve_similar_plans():
    """Test retrieving similar plan executions."""
    store = CMCPlanStore()
    
    # Store plans with similar names
    store.store_plan_start("user_auth", "exec_001", total_steps=3)
    store.store_plan_start("user_registration", "exec_002", total_steps=5)
    store.store_plan_start("admin_auth", "exec_003", total_steps=4)
    
    similar = store.retrieve_similar_plans("user")
    
    # Should find plans with "user" in name
    assert len(similar) >= 2


def test_get_plan_statistics_no_history():
    """Test statistics for plan with no history."""
    store = CMCPlanStore()
    
    stats = store.get_plan_statistics("nonexistent_plan")
    
    assert stats["total_executions"] == 0
    assert stats["success_rate"] == 0.0


def test_get_plan_statistics_with_history():
    """Test statistics calculation from history."""
    store = CMCPlanStore()
    
    # 3 successes, 1 failure
    for i in range(4):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
        store.store_plan_complete(exec_id, {}, success=(i < 3))
    
    stats = store.get_plan_statistics("test_plan")
    
    assert stats["total_executions"] == 4
    assert stats["success_rate"] == 0.75  # 3/4
    assert stats["avg_steps"] == 3.0


def test_memory_aware_executor_stores_execution():
    """Test that memory-aware executor stores execution."""
    store = CMCPlanStore()
    executor = MemoryAwareExecutor(store)
    
    # Mock plan
    class MockPlan:
        steps = [1, 2, 3]
    
    result = executor.execute_with_memory(
        plan_name="test_plan",
        plan=MockPlan(),
        execution_id="exec_001"
    )
    
    assert result["execution_id"] == "exec_001"
    assert result["success"]
    
    # Should be stored in CMC
    assert "exec_001" in store._memory_cache


def test_should_retry_based_on_high_success_rate():
    """Test retry recommendation with high success rate."""
    store = CMCPlanStore()
    executor = MemoryAwareExecutor(store)
    
    # Create history with high success rate
    for i in range(10):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
        store.store_plan_complete(exec_id, {}, success=(i < 8))  # 80% success
    
    should_retry = executor.should_retry_based_on_history(
        "test_plan",
        "Some error"
    )
    
    assert should_retry


def test_should_not_retry_based_on_low_success_rate():
    """Test no retry recommendation with low success rate."""
    store = CMCPlanStore()
    executor = MemoryAwareExecutor(store)
    
    # Create history with low success rate
    for i in range(10):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
        store.store_plan_complete(exec_id, {}, success=(i < 3))  # 30% success
    
    should_retry = executor.should_retry_based_on_history(
        "test_plan",
        "Some error"
    )
    
    assert not should_retry


def test_should_not_retry_with_no_history():
    """Test no retry recommendation with no history."""
    store = CMCPlanStore()
    executor = MemoryAwareExecutor(store)
    
    should_retry = executor.should_retry_based_on_history(
        "nonexistent_plan",
        "Some error"
    )
    
    assert not should_retry


def test_get_plan_recommendations():
    """Test getting plan recommendations from history."""
    store = CMCPlanStore()
    executor = MemoryAwareExecutor(store)
    
    # Create good history
    for i in range(10):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
        store.store_plan_complete(exec_id, {}, success=True)
    
    recommendations = executor.get_plan_recommendations("test_plan")
    
    assert recommendations["confidence"] == 1.0  # 100% success
    assert recommendations["recommended_retries"] == 2  # High success rate
    assert len(recommendations["warnings"]) == 0


def test_recommendations_with_warnings():
    """Test recommendations include warnings for problematic plans."""
    store = CMCPlanStore()
    executor = MemoryAwareExecutor(store)
    
    # Create history with low success
    for i in range(10):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
        store.store_plan_complete(exec_id, {}, success=(i < 3))  # 30% success
    
    recommendations = executor.get_plan_recommendations("test_plan")
    
    assert recommendations["confidence"] == 0.3
    assert recommendations["recommended_retries"] == 0
    assert len(recommendations["warnings"]) > 0
    assert "Low historical success rate" in recommendations["warnings"][0]


def test_plan_memory_dataclass():
    """Test PlanMemory dataclass creation."""
    memory = PlanMemory(
        plan_name="test",
        execution_id="exec_001",
        started_at=datetime.utcnow(),
        completed_at=None,
        status="running",
        steps_completed=2,
        total_steps=5,
        outputs={"step1": "done"},
        metadata={"user": "test"}
    )
    
    assert memory.plan_name == "test"
    assert memory.status == "running"
    assert memory.steps_completed == 2


def test_update_nonexistent_plan_raises_error():
    """Test updating nonexistent plan raises error."""
    store = CMCPlanStore()
    
    with pytest.raises(ValueError, match="not found"):
        store.update_plan_progress("nonexistent", 1, {})


def test_complete_nonexistent_plan_raises_error():
    """Test completing nonexistent plan raises error."""
    store = CMCPlanStore()
    
    with pytest.raises(ValueError, match="not found"):
        store.store_plan_complete("nonexistent", {}, True)


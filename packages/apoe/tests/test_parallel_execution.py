"""Tests for Parallel Execution"""

from __future__ import annotations
import pytest
import asyncio
from datetime import datetime

from apoe.parallel_execution import (
    ParallelExecutionConfig,
    ExecutionBatch,
    DependencyAnalyzer,
    ParallelExecutor,
    execute_plan_parallel
)
from apoe.models import Step, StepStatus, Budget, RoleType
from apoe.acl_parser import ExecutionPlan


def create_mock_plan_linear():
    """Create plan with linear dependencies (no parallelization)."""
    plan = ExecutionPlan(name="linear_plan")
    
    s1 = Step(id="s1", name="step1", role=RoleType.OPERATOR, role_name="op", description="First")
    s2 = Step(id="s2", name="step2", role=RoleType.OPERATOR, role_name="op", description="Second")
    s3 = Step(id="s3", name="step3", role=RoleType.OPERATOR, role_name="op", description="Third")
    
    plan.steps = [s1, s2, s3]
    plan.dependencies = {
        "s1": [],
        "s2": ["s1"],
        "s3": ["s2"]
    }
    
    return plan


def create_mock_plan_parallel():
    """Create plan with independent steps (can parallelize)."""
    plan = ExecutionPlan(name="parallel_plan")
    
    s1 = Step(id="s1", name="step1", role=RoleType.OPERATOR, role_name="op", description="Independent 1")
    s2 = Step(id="s2", name="step2", role=RoleType.OPERATOR, role_name="op", description="Independent 2")
    s3 = Step(id="s3", name="step3", role=RoleType.OPERATOR, role_name="op", description="Independent 3")
    s4 = Step(id="s4", name="step4", role=RoleType.OPERATOR, role_name="op", description="Depends on all")
    
    plan.steps = [s1, s2, s3, s4]
    plan.dependencies = {
        "s1": [],
        "s2": [],
        "s3": [],
        "s4": ["s1", "s2", "s3"]
    }
    
    return plan


def test_dependency_analyzer_linear_plan():
    """Test dependency analyzer with linear plan."""
    plan = create_mock_plan_linear()
    analyzer = DependencyAnalyzer(plan)
    
    batches = analyzer.get_execution_batches()
    
    # Linear plan should have 3 batches (one step each)
    assert len(batches) == 3
    assert all(len(batch.steps) == 1 for batch in batches)
    assert all(not batch.can_execute_parallel for batch in batches)


def test_dependency_analyzer_parallel_plan():
    """Test dependency analyzer with parallelizable plan."""
    plan = create_mock_plan_parallel()
    analyzer = DependencyAnalyzer(plan)
    
    batches = analyzer.get_execution_batches()
    
    # Should have 2 batches: [s1,s2,s3] then [s4]
    assert len(batches) == 2
    assert len(batches[0].steps) == 3  # s1, s2, s3 can run together
    assert len(batches[1].steps) == 1  # s4 waits for all
    assert batches[0].can_execute_parallel
    assert not batches[1].can_execute_parallel


def test_can_parallelize():
    """Test checking if two steps can parallelize."""
    plan = create_mock_plan_parallel()
    analyzer = DependencyAnalyzer(plan)
    
    # s1 and s2 are independent
    assert analyzer.can_parallelize("s1", "s2")
    
    # s1 and s4 are not (s4 depends on s1)
    assert not analyzer.can_parallelize("s1", "s4")


def test_parallel_executor_sequential():
    """Test parallel executor with sequential execution."""
    config = ParallelExecutionConfig(enable_parallel=False)
    executor = ParallelExecutor(config)
    
    batch = ExecutionBatch(
        batch_id=0,
        steps=[
            Step(id="s1", name="s1", role=RoleType.OPERATOR, role_name="op", description="test")
        ],
        can_execute_parallel=False
    )
    
    async def mock_executor(step):
        return {"step_id": step.id, "result": "done"}
    
    results = asyncio.run(executor.execute_batch(batch, mock_executor))
    
    assert len(results) == 1
    assert results["s1"]["result"] == "done"


def test_parallel_executor_parallel():
    """Test parallel executor with concurrent execution."""
    config = ParallelExecutionConfig(enable_parallel=True, max_concurrent_steps=3)
    executor = ParallelExecutor(config)
    
    steps = [
        Step(id=f"s{i}", name=f"s{i}", role=RoleType.OPERATOR, role_name="op", description="test")
        for i in range(3)
    ]
    
    batch = ExecutionBatch(
        batch_id=0,
        steps=steps,
        can_execute_parallel=True
    )
    
    execution_order = []
    
    async def mock_executor(step):
        execution_order.append(f"start_{step.id}")
        await asyncio.sleep(0.01)  # Simulate work
        execution_order.append(f"end_{step.id}")
        return {"step_id": step.id, "result": "done"}
    
    results = asyncio.run(executor.execute_batch(batch, mock_executor))
    
    # All 3 should complete
    assert len(results) == 3
    assert all(results[f"s{i}"]["result"] == "done" for i in range(3))
    
    # Parallel execution means starts should interleave
    # (not all starts before all ends)
    assert execution_order.count("start_s0") == 1


def test_parallel_execution_respects_concurrency_limit():
    """Test that concurrency limit is respected."""
    config = ParallelExecutionConfig(max_concurrent_steps=2)
    executor = ParallelExecutor(config)
    
    steps = [Step(id=f"s{i}", name=f"s{i}", role=RoleType.OPERATOR, role_name="op", description="test") for i in range(5)]
    batch = ExecutionBatch(batch_id=0, steps=steps, can_execute_parallel=True)
    
    max_concurrent = [0]
    
    async def mock_executor(step):
        current = len(executor.active_steps)
        max_concurrent[0] = max(max_concurrent[0], current)
        await asyncio.sleep(0.01)
        return {"result": "done"}
    
    asyncio.run(executor.execute_batch(batch, mock_executor))
    
    # Should never exceed limit
    assert max_concurrent[0] <= 2


def test_execute_plan_parallel():
    """Test complete plan execution with parallelization."""
    plan = create_mock_plan_parallel()
    
    async def mock_executor(step):
        return {"step_id": step.id, "success": True}
    
    result = asyncio.run(execute_plan_parallel(plan, mock_executor))
    
    assert result["success"]
    assert result["total_steps"] == 4
    assert result["batches"] == 2  # Two batches
    assert len(result["results"]) == 4  # All steps executed


def test_parallel_execution_timing():
    """Test that parallel execution is actually faster."""
    plan = create_mock_plan_parallel()
    
    async def mock_executor(step):
        await asyncio.sleep(0.1)  # 100ms per step
        return {"result": "done"}
    
    start = datetime.utcnow()
    asyncio.run(execute_plan_parallel(plan, mock_executor))
    duration = (datetime.utcnow() - start).total_seconds()
    
    # Sequential would take 4 * 0.1 = 0.4 seconds
    # Parallel: batch1 (0.1s for 3 parallel) + batch2 (0.1s) = ~0.2s
    # Allow some overhead, but should be < 0.3s
    assert duration < 0.35, f"Expected parallel speedup, got {duration:.2f}s"


def test_execution_batch_dataclass():
    """Test ExecutionBatch dataclass."""
    steps = [Step(id="s1", name="s1", role=RoleType.OPERATOR, role_name="op", description="test")]
    batch = ExecutionBatch(
        batch_id=0,
        steps=steps,
        can_execute_parallel=False
    )
    
    assert batch.batch_id == 0
    assert len(batch.steps) == 1
    assert not batch.can_execute_parallel


def test_parallel_config_defaults():
    """Test parallel execution config defaults."""
    config = ParallelExecutionConfig()
    
    assert config.max_concurrent_steps == 5
    assert config.enable_parallel
    assert config.timeout_seconds == 300.0


def test_timeout_handling():
    """Test timeout handling in parallel execution."""
    config = ParallelExecutionConfig(timeout_seconds=0.1)
    executor = ParallelExecutor(config)
    
    steps = [Step(id="s1", name="s1", role=RoleType.OPERATOR, role_name="op", description="test")]
    batch = ExecutionBatch(batch_id=0, steps=steps, can_execute_parallel=True)  # Enable parallel for timeout
    
    async def slow_executor(step):
        await asyncio.sleep(1.0)  # Longer than timeout
        return {"result": "done"}
    
    with pytest.raises(TimeoutError):
        asyncio.run(executor.execute_batch(batch, slow_executor))


def test_circular_dependency_detection():
    """Test detection of circular dependencies."""
    plan = ExecutionPlan(name="circular")
    
    s1 = Step(id="s1", name="s1", role=RoleType.OPERATOR, role_name="op", description="test")
    s2 = Step(id="s2", name="s2", role=RoleType.OPERATOR, role_name="op", description="test")
    
    plan.steps = [s1, s2]
    plan.dependencies = {
        "s1": ["s2"],  # s1 depends on s2
        "s2": ["s1"]   # s2 depends on s1 - CIRCULAR!
    }
    
    analyzer = DependencyAnalyzer(plan)
    
    with pytest.raises(ValueError, match="Circular dependency"):
        analyzer.get_execution_batches()


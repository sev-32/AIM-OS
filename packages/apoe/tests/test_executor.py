"""Tests for APOE Executor"""

from __future__ import annotations
import pytest
from datetime import datetime

from apoe import ACLParser, PlanExecutor, StepStatus, Budget, ExecutionResult


def test_execute_simple_plan():
    """Test executing a simple plan."""
    acl = """
    PLAN test:
      ROLE validator: llm(model="gpt-4")
      
      STEP validate:
        ASSIGN validator: "Validate input"
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    executor = PlanExecutor()
    
    # Register mock handler
    def mock_handler(description, params):
        return {"status": "success", "confidence": 0.95}
    
    executor.register_role_handler("validator", mock_handler)
    
    # Execute
    result = executor.execute(plan)
    
    assert result.success
    assert result.completed_steps == 1
    assert result.failed_steps == 0
    assert result.completion_rate() == 1.0


def test_execute_with_dependencies():
    """Test executing plan with dependencies."""
    acl = """
    PLAN test:
      ROLE worker: llm(model="gpt-4")
      
      STEP step1:
        ASSIGN worker: "First"
      
      STEP step2:
        ASSIGN worker: "Second"
        REQUIRES step1
      
      STEP step3:
        ASSIGN worker: "Third"
        REQUIRES step2
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    executor = PlanExecutor()
    executor.register_role_handler("worker", lambda desc, params: {"result": desc})
    
    result = executor.execute(plan)
    
    assert result.success
    assert result.completed_steps == 3
    
    # Verify execution order
    steps = plan.steps
    assert steps[0].status == StepStatus.COMPLETED
    assert steps[1].status == StepStatus.COMPLETED
    assert steps[2].status == StepStatus.COMPLETED
    
    # step2 should complete after step1
    assert steps[1].started_at >= steps[0].completed_at
    
    # step3 should complete after step2
    assert steps[2].started_at >= steps[1].completed_at


def test_gate_failure_stops_execution():
    """Test that gate failures stop execution."""
    acl = """
    PLAN test:
      ROLE validator: llm(model="gpt-4")
      
      STEP validate:
        ASSIGN validator: "Validate"
        GATE confidence_check: output.confidence >= 0.95
      
      STEP next_step:
        ASSIGN validator: "Should not run"
        REQUIRES validate
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    executor = PlanExecutor()
    
    # Handler returns low confidence (fails gate)
    executor.register_role_handler(
        "validator",
        lambda desc, params: {"confidence": 0.80}  # Below 0.95
    )
    
    result = executor.execute(plan)
    
    assert not result.success
    assert result.failed_steps == 1
    assert result.completed_steps == 0
    assert plan.steps[0].status == StepStatus.FAILED
    assert "Gate" in plan.steps[0].error


def test_execute_with_budget_tracking():
    """Test budget tracking during execution."""
    acl = """
    PLAN test:
      ROLE worker: llm(model="gpt-4")
      
      STEP step1:
        ASSIGN worker: "Task 1"
        BUDGET tokens=1000, time=10s
      
      STEP step2:
        ASSIGN worker: "Task 2"
        BUDGET tokens=2000, time=20s
        REQUIRES step1
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    executor = PlanExecutor()
    executor.register_role_handler("worker", lambda desc, params: {"result": "done"})
    
    # Create global budget
    global_budget = Budget(tokens_limit=5000, time_limit_seconds=60.0)
    
    # Execute with budget
    result = executor.execute(plan)
    
    assert result.success
    assert result.completed_steps == 2


def test_parallel_steps_both_execute():
    """Test that independent steps can execute."""
    acl = """
    PLAN test:
      ROLE worker: llm(model="gpt-4")
      
      STEP step1:
        ASSIGN worker: "First"
      
      STEP step2:
        ASSIGN worker: "Independent second"
      
      STEP step3:
        ASSIGN worker: "Independent third"
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    executor = PlanExecutor()
    executor.register_role_handler("worker", lambda desc, params: {"result": desc})
    
    result = executor.execute(plan)
    
    assert result.success
    assert result.completed_steps == 3


def test_execution_stops_on_first_failure():
    """Test fail-fast behavior."""
    acl = """
    PLAN test:
      ROLE worker: llm(model="gpt-4")
      
      STEP step1:
        ASSIGN worker: "Will fail"
      
      STEP step2:
        ASSIGN worker: "Should not run"
        REQUIRES step1
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    executor = PlanExecutor()
    
    # Handler that raises exception (simulates failure)
    def failing_handler(desc, params):
        if "fail" in desc.lower():
            raise ValueError("Simulated failure")
        return {"result": "success"}
    
    executor.register_role_handler("worker", failing_handler)
    
    result = executor.execute(plan)
    
    assert not result.success
    assert result.failed_steps == 1
    assert result.completed_steps == 0
    assert plan.steps[0].status == StepStatus.FAILED
    assert plan.steps[1].status == StepStatus.PENDING  # Never started


def test_execution_result_metrics():
    """Test ExecutionResult metrics calculation."""
    result = ExecutionResult(
        plan_name="test",
        total_steps=10,
        completed_steps=8,
        failed_steps=1,
        skipped_steps=1,
        total_duration_seconds=45.5,
        success=False,
        error="One step failed"
    )
    
    assert result.completion_rate() == 0.8
    assert not result.success
    assert result.error is not None


def test_step_duration_tracking():
    """Test that step duration is tracked."""
    from apoe.models import Step, RoleType
    import time
    
    step = Step(
        id="s1",
        name="test_step",
        role=RoleType.OPERATOR
    )
    
    step.started_at = datetime.utcnow()
    time.sleep(0.1)  # Small delay
    step.completed_at = datetime.utcnow()
    
    duration = step.duration()
    assert duration is not None
    assert duration >= 0.1
    assert duration < 1.0  # Should be quick


def test_realistic_execution_workflow():
    """Test complete realistic workflow."""
    acl = """
    PLAN data_processing:
      ROLE retriever: hhni(k=100)
      ROLE processor: llm(model="gpt-4")
      ROLE validator: llm(model="gpt-4", temperature=0.0)
      
      STEP retrieve_data:
        ASSIGN retriever: "Retrieve relevant data"
        BUDGET tokens=2000, time=10s
      
      STEP process_data:
        ASSIGN processor: "Process and analyze data"
        REQUIRES retrieve_data
        BUDGET tokens=5000, time=30s
        GATE quality_check: output.quality >= 0.90
      
      STEP validate_results:
        ASSIGN validator: "Validate processing results"
        REQUIRES process_data
        BUDGET tokens=1000, time=5s
        GATE confidence_check: output.confidence >= 0.95
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    executor = PlanExecutor()
    
    # Register handlers
    executor.register_role_handler("retriever", lambda d, p: {"data": ["item1", "item2"]})
    executor.register_role_handler("processor", lambda d, p: {"result": "processed", "quality": 0.92})
    executor.register_role_handler("validator", lambda d, p: {"valid": True, "confidence": 0.96})
    
    # Execute
    result = executor.execute(plan)
    
    assert result.success
    assert result.completed_steps == 3
    assert result.failed_steps == 0
    
    # Verify all steps completed in order
    for step in plan.steps:
        assert step.status == StepStatus.COMPLETED
        assert step.started_at is not None
        assert step.completed_at is not None
        assert step.duration() > 0


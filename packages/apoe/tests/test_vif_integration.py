"""Tests for APOE VIF Integration"""

from __future__ import annotations
import pytest

from apoe import (
    ACLParser,
    PlanExecutor,
    create_plan_witness,
    create_step_witness,
    create_witnesses_for_plan,
    StepStatus
)


def test_create_plan_witness():
    """Test creating VIF witness for plan execution."""
    acl = """
    PLAN test:
      ROLE worker: llm(model="gpt-4")
      STEP do_work:
        ASSIGN worker: "Do something"
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    executor = PlanExecutor()
    executor.register_role_handler("worker", lambda d, p: {"result": "done"})
    
    result = executor.execute(plan)
    
    # Create witness
    witness = create_plan_witness(plan, result, confidence=0.95)
    
    assert witness["operation"] == "execute_plan:test"
    assert witness["confidence"] == 0.95
    assert witness["inputs"]["plan_name"] == "test"
    assert witness["outputs"]["success"] == True
    assert witness["outputs"]["completed_steps"] == 1
    assert "timestamp" in witness
    assert "metadata" in witness


def test_create_step_witness():
    """Test creating VIF witness for step execution."""
    from apoe.models import Step, RoleType
    from datetime import datetime
    
    step = Step(
        id="s1",
        name="test_step",
        role=RoleType.REASONER,
        description="Test reasoning",
        status=StepStatus.COMPLETED
    )
    
    step.started_at = datetime.utcnow()
    step.completed_at = datetime.utcnow()
    step.outputs = {"result": "success", "confidence": 0.92}
    
    witness = create_step_witness(step, "test_plan")
    
    assert witness["operation"] == "execute_step:test_plan.test_step"
    assert witness["confidence"] == 0.92  # Extracted from outputs
    assert witness["inputs"]["step_name"] == "test_step"
    assert witness["inputs"]["role"] == "reasoner"
    assert witness["outputs"]["result"] == "success"
    assert witness["metadata"]["status"] == "completed"


def test_create_witnesses_for_complete_plan():
    """Test creating complete witness set for plan."""
    acl = """
    PLAN workflow:
      ROLE planner: llm(model="gpt-4")
      ROLE executor: llm(model="gpt-4")
      
      STEP plan:
        ASSIGN planner: "Create plan"
      
      STEP execute:
        ASSIGN executor: "Execute plan"
        REQUIRES plan
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    executor = PlanExecutor()
    executor.register_role_handler("planner", lambda d, p: {"plan": "ready", "confidence": 0.90})
    executor.register_role_handler("executor", lambda d, p: {"result": "done", "confidence": 0.95})
    
    result = executor.execute(plan)
    
    # Create all witnesses
    witnesses = create_witnesses_for_plan(plan, result)
    
    assert "plan_witness" in witnesses
    assert "step_witnesses" in witnesses
    assert witnesses["witness_count"] == 3  # 1 plan + 2 steps
    assert len(witnesses["step_witnesses"]) == 2


def test_witness_includes_error_info():
    """Test that witnesses include error information."""
    from apoe.models import Step, RoleType
    from datetime import datetime
    
    step = Step(
        id="s1",
        name="failed_step",
        role=RoleType.VERIFIER,
        status=StepStatus.FAILED
    )
    
    step.started_at = datetime.utcnow()
    step.completed_at = datetime.utcnow()
    step.error = "Gate 'confidence_check' failed"
    
    witness = create_step_witness(step, "test_plan", confidence=0.60)
    
    assert witness["confidence"] == 0.60  # Low confidence for failure
    assert witness["metadata"]["status"] == "failed"
    assert witness["metadata"]["error"] == "Gate 'confidence_check' failed"


def test_witness_with_budget_tracking():
    """Test witness includes budget information."""
    from apoe.models import Step, RoleType, Budget
    from datetime import datetime
    
    step = Step(
        id="s1",
        name="budgeted_step",
        role=RoleType.BUILDER,
        budget=Budget(tokens_limit=5000, time_limit_seconds=30.0),
        status=StepStatus.COMPLETED
    )
    
    step.started_at = datetime.utcnow()
    step.completed_at = datetime.utcnow()
    step.outputs = {"built": "artifact"}
    
    witness = create_step_witness(step, "test_plan")
    
    assert witness["inputs"]["budget"]["tokens_limit"] == 5000
    assert witness["inputs"]["budget"]["time_limit"] == 30.0
    assert witness["metadata"]["duration_seconds"] is not None


def test_realistic_witness_workflow():
    """Test witness creation for realistic multi-step plan."""
    acl = """
    PLAN user_auth:
      ROLE validator: llm(model="gpt-4")
      ROLE retriever: hhni(k=100)
      ROLE reasoner: llm(model="gpt-4")
      
      STEP validate:
        ASSIGN validator: "Validate credentials"
        GATE format_check: output.valid == True
      
      STEP retrieve:
        ASSIGN retriever: "Get user data"
        REQUIRES validate
      
      STEP verify:
        ASSIGN reasoner: "Verify password"
        REQUIRES retrieve
        GATE confidence_check: output.confidence >= 0.95
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    executor = PlanExecutor()
    executor.register_role_handler("validator", lambda d, p: {"valid": True, "confidence": 0.99})
    executor.register_role_handler("retriever", lambda d, p: {"user": "found", "confidence": 0.98})
    executor.register_role_handler("reasoner", lambda d, p: {"verified": True, "confidence": 0.96})
    
    result = executor.execute(plan)
    
    # Create witnesses
    witnesses = create_witnesses_for_plan(plan, result)
    
    # Validate plan witness
    plan_witness = witnesses["plan_witness"]
    assert plan_witness["inputs"]["plan_name"] == "user_auth"
    assert plan_witness["outputs"]["success"] == True
    assert plan_witness["outputs"]["completed_steps"] == 3
    
    # Validate step witnesses
    step_witnesses = witnesses["step_witnesses"]
    assert len(step_witnesses) == 3
    
    # Each step should have witness with confidence
    for witness in step_witnesses:
        assert "confidence" in witness
        assert witness["confidence"] >= 0.95  # All should be high confidence
        assert "timestamp" in witness
        assert "model_id" in witness


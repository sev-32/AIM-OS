"""Tests for DEPP (Dynamic Execution Plan Processor)"""

from __future__ import annotations
import pytest

from apoe.depp import (
    PlanModification,
    SelfModifyingPlan,
    DEPPController,
    low_confidence_adds_verification,
    timeout_increases_budget
)
from apoe.models import Step, StepStatus, Budget, Gate, RoleType
from apoe.acl_parser import ExecutionPlan


def create_mock_plan():
    """Create mock execution plan for testing."""
    plan = ExecutionPlan(name="test_plan")
    
    step1 = Step(
        id="s1",
        name="step1",
        role=RoleType.OPERATOR,
        role_name="worker",
        description="Do something",
        budget=Budget(tokens_limit=1000, time_limit_seconds=30)
    )
    
    step2 = Step(
        id="s2",
        name="step2",
        role=RoleType.OPERATOR,
        role_name="worker",
        description="Do something else"
    )
    
    plan.steps = [step1, step2]
    
    return plan


def test_create_self_modifying_plan():
    """Test creating self-modifying plan."""
    base_plan = create_mock_plan()
    sm_plan = SelfModifyingPlan(base_plan)
    
    assert sm_plan.base_plan == base_plan
    assert len(sm_plan.current_plan.steps) == 2
    assert not sm_plan.has_been_modified()


def test_add_step_dynamically():
    """Test adding step to plan dynamically."""
    base_plan = create_mock_plan()
    sm_plan = SelfModifyingPlan(base_plan)
    
    new_step = Step(
        id="s3",
        name="dynamic_step",
        role=RoleType.VERIFIER,
        role_name="verifier",
        description="Added dynamically"
    )
    
    mod_id = sm_plan.add_step_dynamically(
        step=new_step,
        after_step_id="s1",
        reason="Need verification"
    )
    
    assert mod_id.startswith("mod_")
    assert len(sm_plan.current_plan.steps) == 3
    assert sm_plan.has_been_modified()
    assert len(sm_plan.modifications) == 1


def test_add_step_to_end():
    """Test adding step to end of plan."""
    base_plan = create_mock_plan()
    sm_plan = SelfModifyingPlan(base_plan)
    
    new_step = Step(
        id="s3",
        name="final_step",
        role=RoleType.WITNESS,
        role_name="witness",
        description="Final step"
    )
    
    sm_plan.add_step_dynamically(step=new_step)
    
    assert len(sm_plan.current_plan.steps) == 3
    assert sm_plan.current_plan.steps[-1].id == "s3"


def test_modify_step_budget():
    """Test modifying step budget dynamically."""
    base_plan = create_mock_plan()
    sm_plan = SelfModifyingPlan(base_plan)
    
    new_budget = Budget(tokens_limit=5000, time_limit_seconds=60)
    
    mod_id = sm_plan.modify_step_budget(
        step_id="s1",
        new_budget=new_budget,
        reason="Need more resources"
    )
    
    assert sm_plan.current_plan.steps[0].budget.tokens_limit == 5000
    assert sm_plan.has_been_modified()


def test_add_gate_to_step():
    """Test adding gate to step dynamically."""
    base_plan = create_mock_plan()
    sm_plan = SelfModifyingPlan(base_plan)
    
    new_gate = Gate(
        id="g1",
        name="quality_gate",
        gate_type="quality",
        condition="output.confidence >= 0.90"
    )
    
    sm_plan.add_gate_to_step(
        step_id="s1",
        gate=new_gate,
        reason="Additional quality check needed"
    )
    
    assert len(sm_plan.current_plan.steps[0].gates) == 1
    assert sm_plan.has_been_modified()


def test_remove_step():
    """Test removing step from plan dynamically."""
    base_plan = create_mock_plan()
    sm_plan = SelfModifyingPlan(base_plan)
    
    assert len(sm_plan.current_plan.steps) == 2
    
    sm_plan.remove_step(
        step_id="s2",
        reason="Step no longer needed"
    )
    
    assert len(sm_plan.current_plan.steps) == 1
    assert sm_plan.has_been_modified()


def test_get_modification_history():
    """Test retrieving modification history."""
    base_plan = create_mock_plan()
    sm_plan = SelfModifyingPlan(base_plan)
    
    # Make several modifications
    new_step = Step(id="s3", name="new", role=RoleType.OPERATOR, role_name="op", description="test")
    sm_plan.add_step_dynamically(new_step)
    sm_plan.remove_step("s2")
    
    history = sm_plan.get_modification_history()
    
    assert len(history) == 2
    assert history[0].modification_type == "add_step"
    assert history[1].modification_type == "remove_step"


def test_depp_controller_register_rule():
    """Test registering modification rule."""
    controller = DEPPController()
    
    def my_rule(plan, results):
        return []
    
    controller.register_modification_rule(my_rule)
    
    assert len(controller.modification_rules) == 1


def test_depp_controller_evaluate_modifications():
    """Test evaluating modification rules."""
    controller = DEPPController()
    
    # Register rule that adds step if confidence low
    def add_step_if_low_conf(plan, results):
        if results.get("confidence", 1.0) < 0.70:
            return [PlanModification(
                modification_id="m1",
                modification_type="add_step",
                target_step_id=None,
                new_data={},
                reason="Low confidence",
                confidence=0.80
            )]
        return []
    
    controller.register_modification_rule(add_step_if_low_conf)
    
    plan = SelfModifyingPlan(create_mock_plan())
    results = {"confidence": 0.60}
    
    modifications = controller.evaluate_modifications(plan, results)
    
    assert len(modifications) == 1
    assert modifications[0].reason == "Low confidence"


def test_low_confidence_rule():
    """Test low_confidence_adds_verification rule."""
    plan = SelfModifyingPlan(create_mock_plan())
    results = {"confidence": 0.65}  # Low!
    
    modifications = low_confidence_adds_verification(plan, results)
    
    assert len(modifications) > 0
    assert modifications[0].modification_type == "add_step"


def test_low_confidence_rule_no_trigger():
    """Test low_confidence rule doesn't trigger for high confidence."""
    plan = SelfModifyingPlan(create_mock_plan())
    results = {"confidence": 0.95}  # High!
    
    modifications = low_confidence_adds_verification(plan, results)
    
    assert len(modifications) == 0


def test_timeout_rule():
    """Test timeout_increases_budget rule."""
    plan = SelfModifyingPlan(create_mock_plan())
    results = {"timeout": True, "step_id": "s1"}
    
    modifications = timeout_increases_budget(plan, results)
    
    assert len(modifications) > 0
    assert modifications[0].modification_type == "modify_step"


def test_timeout_rule_no_trigger():
    """Test timeout rule doesn't trigger without timeout."""
    plan = SelfModifyingPlan(create_mock_plan())
    results = {"timeout": False}
    
    modifications = timeout_increases_budget(plan, results)
    
    assert len(modifications) == 0


def test_depp_apply_modifications():
    """Test applying modifications to plan."""
    controller = DEPPController()
    plan = SelfModifyingPlan(create_mock_plan())
    
    # Create modification
    new_step = Step(id="s3", name="added", role=RoleType.OPERATOR, role_name="op", description="test")
    modification = PlanModification(
        modification_id="m1",
        modification_type="add_step",
        target_step_id=None,
        new_data={"step": new_step},
        reason="Testing",
        confidence=0.90
    )
    
    controller.apply_modifications(plan, [modification])
    
    # Plan should be modified
    assert len(plan.current_plan.steps) == 3


def test_plan_modification_preserves_base_plan():
    """Test that base plan is preserved during modifications."""
    base_plan = create_mock_plan()
    sm_plan = SelfModifyingPlan(base_plan)
    
    original_steps = len(base_plan.steps)
    
    # Modify current plan
    new_step = Step(id="s3", name="new", role=RoleType.OPERATOR, role_name="op", description="test")
    sm_plan.add_step_dynamically(new_step)
    
    # Base plan should be unchanged
    assert len(sm_plan.base_plan.steps) == original_steps
    # Current plan should be modified
    assert len(sm_plan.current_plan.steps) == original_steps + 1


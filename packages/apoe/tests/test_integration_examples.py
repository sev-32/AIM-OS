"""Tests for APOE Integration Examples

Validates that integration examples work correctly.
"""

from __future__ import annotations
import pytest

from apoe.integration_examples import (
    execute_hhni_workflow,
    execute_complete_workflow,
    demonstrate_error_recovery,
    HHNI_RETRIEVAL_WORKFLOW,
    COMPLETE_WORKFLOW,
    ERROR_HANDLING_WORKFLOW
)
from apoe import ACLParser


def test_hhni_workflow_executes():
    """Test HHNI retrieval workflow executes successfully."""
    result_dict = execute_hhni_workflow()
    
    assert result_dict["success"]
    assert result_dict["result"].completed_steps == 2
    assert result_dict["witnesses"]["witness_count"] == 3  # 1 plan + 2 steps


def test_complete_workflow_all_steps():
    """Test complete multi-system workflow executes all steps."""
    result_dict = execute_complete_workflow()
    
    assert result_dict["result"].success
    assert result_dict["steps_completed"] == 7  # All 7 steps should complete
    assert result_dict["result"].failed_steps == 0
    assert result_dict["witnesses"]["witness_count"] == 8  # 1 plan + 7 steps


def test_error_recovery_demonstrates_fail_fast():
    """Test error handling workflow demonstrates fail-fast behavior."""
    result = demonstrate_error_recovery()
    
    assert not result.success  # Should fail
    assert result.failed_steps == 1  # First step fails
    assert result.completed_steps == 0  # Nothing completed


def test_hhni_workflow_acl_parseable():
    """Test HHNI workflow ACL is valid."""
    parser = ACLParser()
    plan = parser.parse(HHNI_RETRIEVAL_WORKFLOW)
    
    assert plan.name == "knowledge_retrieval"
    assert len(plan.steps) == 2
    assert "retriever" in plan.roles
    assert "synthesizer" in plan.roles


def test_complete_workflow_acl_parseable():
    """Test complete workflow ACL is valid."""
    parser = ACLParser()
    plan = parser.parse(COMPLETE_WORKFLOW)
    
    assert plan.name == "ai_research_pipeline"
    assert len(plan.steps) == 7
    assert len(plan.roles) == 7  # All roles defined


def test_error_workflow_acl_parseable():
    """Test error handling workflow ACL is valid."""
    parser = ACLParser()
    plan = parser.parse(ERROR_HANDLING_WORKFLOW)
    
    assert plan.name == "resilient_workflow"
    assert len(plan.steps) == 2


def test_complete_workflow_has_proper_dependencies():
    """Test complete workflow has correct dependency chain."""
    parser = ACLParser()
    plan = parser.parse(COMPLETE_WORKFLOW)
    
    # Step 1 (retrieve_background) should have no dependencies
    assert plan.get_dependencies("s1") == []
    
    # Step 2 (create_research_plan) should depend on step 1
    assert plan.get_dependencies("s2") == ["s1"]
    
    # Step 3 (conduct_analysis) should depend on step 2
    assert plan.get_dependencies("s3") == ["s2"]
    
    # Later steps should have dependencies
    assert len(plan.get_dependencies("s7")) > 0  # store_results depends on create_witness


def test_workflows_have_budgets():
    """Test that workflows include budget specifications."""
    parser = ACLParser()
    plan = parser.parse(COMPLETE_WORKFLOW)
    
    # Most steps should have budgets (budgets are optional but recommended)
    steps_with_budgets = [s for s in plan.steps if s.budget is not None]
    
    assert len(steps_with_budgets) >= 4, "Workflow should have budgets on most steps"
    
    # Budgeted steps should have valid limits
    for step in steps_with_budgets:
        assert step.budget.tokens_limit > 0
        assert step.budget.time_limit_seconds > 0


def test_workflows_have_gates():
    """Test that workflows include quality gates."""
    parser = ACLParser()
    plan = parser.parse(COMPLETE_WORKFLOW)
    
    # Count steps with gates
    steps_with_gates = [s for s in plan.steps if len(s.gates) > 0]
    
    # Should have multiple gated steps
    assert len(steps_with_gates) >= 3, "Complete workflow should have multiple gates"


def test_integration_examples_demonstrate_all_systems():
    """Test that examples cover all major AIM-OS systems."""
    parser = ACLParser()
    
    # HHNI example
    plan1 = parser.parse(HHNI_RETRIEVAL_WORKFLOW)
    assert any("hhni" in role.model_type for role in plan1.roles.values())
    
    # Complete example should reference multiple systems
    plan2 = parser.parse(COMPLETE_WORKFLOW)
    
    # Should have HHNI role
    assert any("hhni" in role.model_type for role in plan2.roles.values())
    
    # Should have VIF role
    assert any("vif" in role.model_type for role in plan2.roles.values())
    
    # Should have CMC role
    assert any("cmc" in role.model_type for role in plan2.roles.values())


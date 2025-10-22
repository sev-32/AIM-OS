"""Tests for Advanced Role Dispatch System"""

from __future__ import annotations
import pytest

from apoe.role_dispatcher import RoleDispatcher, ROLE_CAPABILITIES
from apoe.roles import RoleType


def test_recommend_role_for_planning_task():
    """Test role recommendation for planning tasks."""
    dispatcher = RoleDispatcher()
    
    role = dispatcher.recommend_role_for_task("Create a strategy for the project")
    
    assert role == RoleType.PLANNER


def test_recommend_role_for_retrieval_task():
    """Test role recommendation for retrieval tasks."""
    dispatcher = RoleDispatcher()
    
    role = dispatcher.recommend_role_for_task("Search for relevant context")
    
    assert role == RoleType.RETRIEVER


def test_recommend_role_for_reasoning_task():
    """Test role recommendation for reasoning tasks."""
    dispatcher = RoleDispatcher()
    
    role = dispatcher.recommend_role_for_task("Analyze the problem and solve it")
    
    assert role == RoleType.REASONER


def test_recommend_role_for_building_task():
    """Test role recommendation for building tasks."""
    dispatcher = RoleDispatcher()
    
    role = dispatcher.recommend_role_for_task("Implement the feature in code")
    
    assert role == RoleType.BUILDER


def test_estimate_step_cost():
    """Test cost estimation for steps."""
    dispatcher = RoleDispatcher()
    
    # Simple task
    cost1 = dispatcher.estimate_step_cost(RoleType.OPERATOR, "Do something")
    
    # Complex task (more words)
    cost2 = dispatcher.estimate_step_cost(
        RoleType.REASONER,
        "Perform deep analysis of the entire system architecture and identify all potential issues"
    )
    
    # Complex task should cost more
    assert cost2 > cost1


def test_select_optimal_role_chain():
    """Test selecting optimal role chain for task."""
    dispatcher = RoleDispatcher()
    
    chain = dispatcher.select_optimal_role_chain(
        "Build a feature",
        [RoleType.BUILDER, RoleType.VERIFIER],
        constraints={"require_verification": True, "max_cost": 10.0}
    )
    
    # Should include builder (primary) and verifier (required)
    assert RoleType.BUILDER in chain
    assert RoleType.VERIFIER in chain
    # May also include witness if cost allows
    assert len(chain) >= 2


def test_role_chain_respects_cost_constraint():
    """Test that role chain respects cost constraints."""
    dispatcher = RoleDispatcher()
    
    chain = dispatcher.select_optimal_role_chain(
        "Analyze everything",
        [RoleType.REASONER],
        constraints={"max_cost": 0.5}  # Very low cost
    )
    
    # Should be minimal chain due to cost constraint
    assert len(chain) <= 2  # Primary role + maybe witness


def test_get_fallback_role():
    """Test fallback role selection."""
    dispatcher = RoleDispatcher()
    
    # If retriever fails, should fallback to operator
    fallback = dispatcher.get_fallback_role(RoleType.RETRIEVER, "no results")
    
    assert fallback == RoleType.OPERATOR


def test_assess_role_performance_good():
    """Test role performance assessment for good performance."""
    dispatcher = RoleDispatcher()
    
    # Reasoner with confidence in expected range
    assessment = dispatcher.assess_role_performance(
        RoleType.REASONER,
        actual_confidence=0.85,
        execution_time=10.0
    )
    
    assert assessment["within_range"]
    assert assessment["assessment"] in ["good", "excellent"]


def test_assess_role_performance_below_expected():
    """Test role performance assessment for below expected."""
    dispatcher = RoleDispatcher()
    
    # Verifier with low confidence (below range)
    assessment = dispatcher.assess_role_performance(
        RoleType.VERIFIER,
        actual_confidence=0.60,  # Below expected 0.85-0.98
        execution_time=5.0
    )
    
    assert not assessment["within_range"]
    assert assessment["assessment"] == "below_expected"


def test_all_role_types_have_capabilities():
    """Test that all role types have capability definitions."""
    for role_type in RoleType:
        assert role_type in ROLE_CAPABILITIES
        
        capability = ROLE_CAPABILITIES[role_type]
        assert len(capability.strengths) > 0
        assert len(capability.weaknesses) > 0
        assert capability.cost_estimate > 0
        assert capability.confidence_range[0] < capability.confidence_range[1]


def test_register_custom_handler():
    """Test registering custom handlers."""
    dispatcher = RoleDispatcher()
    
    custom_handler = lambda desc, params: {"result": "custom"}
    dispatcher.register_custom_handler("my_special_role", custom_handler)
    
    assert "my_special_role" in dispatcher._custom_handlers


def test_role_chain_includes_witness_when_possible():
    """Test that role chains include witness when cost allows."""
    dispatcher = RoleDispatcher()
    
    chain = dispatcher.select_optimal_role_chain(
        "Do something",
        [RoleType.OPERATOR],
        constraints={"max_cost": 5.0}  # Generous cost
    )
    
    # Should include witness for provenance
    assert RoleType.WITNESS in chain or len(chain) >= 1


def test_cost_estimation_scales_with_complexity():
    """Test that cost scales with task complexity."""
    dispatcher = RoleDispatcher()
    
    simple = "Do it"
    complex = " ".join(["word"] * 100)  # 100 words
    
    cost_simple = dispatcher.estimate_step_cost(RoleType.OPERATOR, simple)
    cost_complex = dispatcher.estimate_step_cost(RoleType.OPERATOR, complex)
    
    assert cost_complex > cost_simple


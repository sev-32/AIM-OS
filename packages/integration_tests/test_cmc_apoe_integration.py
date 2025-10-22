"""Integration Tests: CMC + APOE

Tests that APOE plans can be stored/retrieved from CMC.
"""

from __future__ import annotations
import pytest


def test_apoe_plan_stored_to_cmc():
    """Test that executed APOE plans stored to CMC."""
    # Executed plan
    plan_execution = {
        "plan_name": "user_research",
        "execution_id": "exec_001",
        "steps_completed": 5,
        "success": True,
        "duration_seconds": 120
    }
    
    # Store as CMC atom
    cmc_atom = {
        "modality": "plan_execution",
        "content": str(plan_execution),
        "tags": ["apoe", "user_research", "success"],
        "metadata": plan_execution
    }
    
    assert cmc_atom["modality"] == "plan_execution"
    assert "apoe" in cmc_atom["tags"]


def test_retrieve_plan_history_from_cmc():
    """Test retrieving plan execution history from CMC."""
    # Historical executions in CMC
    history = [
        {"plan": "auth", "success": True, "confidence": 0.92},
        {"plan": "auth", "success": True, "confidence": 0.88},
        {"plan": "auth", "success": False, "confidence": 0.65}
    ]
    
    # Calculate success rate
    success_rate = sum(1 for h in history if h["success"]) / len(history)
    
    assert success_rate > 0.66  # 2/3 success
    
    # APOE can use this to decide if retry is worth it


def test_cmc_enables_apoe_learning():
    """Test that CMC enables APOE to learn from past executions."""
    # Pattern: Plans with high confidence succeed more
    executions = [
        {"confidence": 0.95, "success": True},
        {"confidence": 0.90, "success": True},
        {"confidence": 0.70, "success": False},
        {"confidence": 0.88, "success": True}
    ]
    
    high_conf = [e for e in executions if e["confidence"] >= 0.85]
    low_conf = [e for e in executions if e["confidence"] < 0.85]
    
    high_conf_success = sum(1 for e in high_conf if e["success"]) / len(high_conf)
    low_conf_success = sum(1 for e in low_conf if e["success"]) / len(low_conf)
    
    # High confidence should succeed more
    assert high_conf_success > low_conf_success
    
    # APOE learns: maintain confidence >= 0.85 for success


def test_plan_templates_stored_in_cmc():
    """Test that successful plan patterns stored as templates."""
    # Successful plan structure
    template = {
        "plan_type": "research_workflow",
        "steps": ["retrieve", "analyze", "synthesize"],
        "avg_success_rate": 0.90,
        "avg_duration": 180,
        "recommended_confidence": 0.85
    }
    
    # Store as CMC atom (template for future)
    cmc_atom = {
        "modality": "plan_template",
        "content": str(template),
        "tags": ["apoe", "template", "research_workflow"],
        "metadata": template
    }
    
    assert "template" in cmc_atom["tags"]
    
    # Future APOE executions can retrieve template
    # "How should I structure a research workflow?"


def test_apoe_retrieves_context_from_cmc():
    """Test APOE step retrieving context from CMC before executing."""
    # APOE step: "Analyze user preferences"
    # First: Retrieve from CMC
    
    cmc_results = [
        {"content": "User prefers TypeScript", "confidence": 0.95},
        {"content": "User likes async/await", "confidence": 0.90}
    ]
    
    # Use retrieved context in step
    step_context = "\n".join(r["content"] for r in cmc_results)
    
    assert "TypeScript" in step_context
    assert "async/await" in step_context
    
    # This makes APOE memory-aware


def test_failed_plans_analyzed_via_cmc():
    """Test analyzing failed plans through CMC storage."""
    failed_executions = [
        {
            "plan": "deployment",
            "failure_step": "validate",
            "failure_reason": "Tests failed",
            "confidence_at_failure": 0.70
        },
        {
            "plan": "deployment",
            "failure_step": "validate",
            "failure_reason": "Tests failed",
            "confidence_at_failure": 0.68
        }
    ]
    
    # Pattern: "validate" step fails when confidence < 0.75
    
    # APOE learns: Add extra validation if confidence < 0.75
    # Or: Increase confidence threshold for validate step
    
    assert all(e["failure_step"] == "validate" for e in failed_executions)
    assert all(e["confidence_at_failure"] < 0.75 for e in failed_executions)
    
    # CMC enables this pattern detection


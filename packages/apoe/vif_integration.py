"""VIF Integration for APOE

Creates VIF witnesses for APOE operations (plan execution, step execution).
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, Optional

from .models import Step
from .executor import ExecutionResult
from .acl_parser import ExecutionPlan


def create_plan_witness(
    plan: ExecutionPlan,
    result: ExecutionResult,
    confidence: float = 0.95
) -> Dict[str, Any]:
    """
    Create VIF witness for complete plan execution.
    
    Args:
        plan: Executed plan
        result: Execution result
        confidence: Confidence in execution (0.0-1.0)
        
    Returns:
        VIF witness dictionary
    """
    return {
        "operation": f"execute_plan:{plan.name}",
        "timestamp": datetime.utcnow().isoformat(),
        "inputs": {
            "plan_name": plan.name,
            "total_steps": result.total_steps,
            "roles": list(plan.roles.keys())
        },
        "outputs": {
            "completed_steps": result.completed_steps,
            "failed_steps": result.failed_steps,
            "success": result.success,
            "duration_seconds": result.total_duration_seconds
        },
        "confidence": confidence,
        "model_id": "apoe-executor-v1",
        "model_provider": "aether",
        "metadata": {
            "completion_rate": result.completion_rate(),
            "plan_structure": {
                "steps": len(plan.steps),
                "roles": len(plan.roles),
                "gates": len(plan.gates),
                "dependencies": len(plan.dependencies)
            }
        }
    }


def create_step_witness(
    step: Step,
    plan_name: str,
    confidence: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create VIF witness for individual step execution.
    
    Args:
        step: Executed step
        plan_name: Name of parent plan
        confidence: Confidence in step execution
        
    Returns:
        VIF witness dictionary
    """
    # Extract confidence from outputs if not provided
    if confidence is None and step.outputs:
        confidence = step.outputs.get("confidence", 0.95)
    elif confidence is None:
        confidence = 0.95  # Default
    
    return {
        "operation": f"execute_step:{plan_name}.{step.name}",
        "timestamp": (step.started_at or datetime.utcnow()).isoformat(),
        "inputs": {
            "step_name": step.name,
            "role": step.role.value,
            "description": step.description,
            "budget": {
                "tokens_limit": step.budget.tokens_limit if step.budget else None,
                "time_limit": step.budget.time_limit_seconds if step.budget else None
            } if step.budget else None
        },
        "outputs": step.outputs or {},
        "confidence": confidence,
        "model_id": step.role.value,
        "model_provider": "apoe",
        "metadata": {
            "status": step.status.value,
            "duration_seconds": step.duration(),
            "gates_count": len(step.gates),
            "error": step.error
        }
    }


def create_witnesses_for_plan(
    plan: ExecutionPlan,
    result: ExecutionResult
) -> Dict[str, Any]:
    """
    Create complete witness set for plan execution.
    
    Includes one witness for the plan and one for each executed step.
    
    Args:
        plan: Executed plan
        result: Execution result
        
    Returns:
        Dictionary with plan_witness and step_witnesses
    """
    # Plan-level witness
    plan_witness = create_plan_witness(plan, result)
    
    # Step-level witnesses
    step_witnesses = []
    for step in plan.steps:
        if step.status != "pending":  # Only for executed steps
            witness = create_step_witness(step, plan.name)
            step_witnesses.append(witness)
    
    return {
        "plan_witness": plan_witness,
        "step_witnesses": step_witnesses,
        "witness_count": 1 + len(step_witnesses)
    }


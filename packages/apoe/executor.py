"""APOE Execution Engine

Executes ExecutionPlans by running steps in dependency order.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

from .models import Step, StepStatus, Budget, Gate
from .acl_parser import ExecutionPlan


@dataclass
class ExecutionResult:
    """Result of executing a plan."""
    plan_name: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    skipped_steps: int
    total_duration_seconds: float
    success: bool
    error: Optional[str] = None
    
    def completion_rate(self) -> float:
        """Calculate completion rate (0.0-1.0)."""
        if self.total_steps == 0:
            return 0.0
        return self.completed_steps / self.total_steps


class PlanExecutor:
    """
    Execute ExecutionPlans with dependency resolution and gate validation.
    
    Runs steps in topological order, respecting dependencies,
    tracking budgets, and validating gates.
    """
    
    def __init__(self):
        self.role_handlers: Dict[str, Callable] = {}
    
    def register_role_handler(
        self,
        role_name: str,
        handler: Callable[[str, Dict], Dict[str, Any]]
    ):
        """
        Register a handler function for a role.
        
        Args:
            role_name: Name of role (from plan.roles)
            handler: Function(description, params) -> outputs
        """
        self.role_handlers[role_name] = handler
    
    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        """
        Execute a plan to completion (or failure).
        
        Args:
            plan: ExecutionPlan to execute
            
        Returns:
            ExecutionResult with metrics
        """
        start_time = datetime.utcnow()
        completed = 0
        failed = 0
        skipped = 0
        
        # Execute until no more ready steps
        while True:
            ready_steps = plan.get_ready_steps()
            
            if not ready_steps:
                # No more ready steps - either done or blocked
                break
            
            # Execute each ready step
            for step in ready_steps:
                result = self._execute_step(step, plan)
                
                if result == "completed":
                    completed += 1
                elif result == "failed":
                    failed += 1
                    # Fail fast - stop on error
                    break
                elif result == "skipped":
                    skipped += 1
            
            # If any step failed, abort execution
            if failed > 0:
                break
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Check if all steps completed successfully
        success = (completed == len(plan.steps) and failed == 0)
        error = None if success else "Execution failed or incomplete"
        
        return ExecutionResult(
            plan_name=plan.name,
            total_steps=len(plan.steps),
            completed_steps=completed,
            failed_steps=failed,
            skipped_steps=skipped,
            total_duration_seconds=duration,
            success=success,
            error=error
        )
    
    def _execute_step(self, step: Step, plan: ExecutionPlan) -> str:
        """
        Execute a single step.
        
        Returns:
            "completed" | "failed" | "skipped"
        """
        # Mark as running
        step.status = StepStatus.RUNNING
        step.started_at = datetime.utcnow()
        
        try:
            # Get role handler using step's assigned role_name
            if not step.role_name:
                raise ValueError(f"Step {step.name} has no role assigned")
            
            role_config = plan.roles.get(step.role_name)
            if not role_config:
                raise ValueError(f"Role '{step.role_name}' not defined in plan")
            
            # Execute step via role handler
            if step.role_name in self.role_handlers:
                handler = self.role_handlers[step.role_name]
                outputs = handler(step.description or "", role_config.params)
            else:
                # Mock execution for testing
                outputs = {"status": "success", "confidence": 0.95}
            
            step.outputs = outputs
            
            # Validate gates
            for gate in step.gates:
                context = {"output": type('obj', (object,), outputs)()}
                
                if not gate.evaluate(context):
                    step.status = StepStatus.FAILED
                    step.error = f"Gate '{gate.name}' failed: {gate.condition}"
                    step.completed_at = datetime.utcnow()
                    return "failed"
            
            # Success
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            return "completed"
        
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.utcnow()
            return "failed"
    
    def execute_step_with_budget(
        self,
        step: Step,
        plan: ExecutionPlan,
        global_budget: Optional[Budget] = None
    ) -> str:
        """
        Execute step with budget tracking.
        
        Args:
            step: Step to execute
            plan: Full execution plan
            global_budget: Optional global budget (in addition to step budget)
            
        Returns:
            "completed" | "failed" | "skipped"
        """
        # Check budget before execution
        if global_budget and step.budget:
            if not global_budget.check_tokens(step.budget.tokens_limit):
                step.status = StepStatus.SKIPPED
                step.error = "Insufficient global budget tokens"
                return "skipped"
            
            if not global_budget.check_time(step.budget.time_limit_seconds):
                step.status = StepStatus.SKIPPED
                step.error = "Insufficient global budget time"
                return "skipped"
        
        # Execute step
        result = self._execute_step(step, plan)
        
        # Consume budget if successful
        if result == "completed" and step.budget:
            # Estimate consumption (in production, measure actual)
            tokens_used = int(step.budget.tokens_limit * 0.8)  # Assume 80% of limit
            time_used = step.duration() or step.budget.time_limit_seconds
            
            if global_budget:
                global_budget.consume_tokens(tokens_used)
                global_budget.consume_time(time_used)
        
        return result


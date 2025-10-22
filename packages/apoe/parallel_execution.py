"""Parallel Execution for APOE

Enables concurrent execution of independent steps in execution plans.
"""

from __future__ import annotations
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass
import asyncio
from datetime import datetime

from apoe.models import Step, StepStatus


@dataclass
class ParallelExecutionConfig:
    """Configuration for parallel execution."""
    max_concurrent_steps: int = 5
    enable_parallel: bool = True
    timeout_seconds: float = 300.0  # 5 minutes default


@dataclass
class ExecutionBatch:
    """Batch of steps that can execute in parallel."""
    batch_id: int
    steps: List[Step]
    can_execute_parallel: bool


class DependencyAnalyzer:
    """Analyzes dependencies to determine parallelizable steps."""
    
    def __init__(self, plan):
        """
        Initialize with execution plan.
        
        Args:
            plan: ExecutionPlan with steps and dependencies
        """
        self.plan = plan
    
    def get_execution_batches(self) -> List[ExecutionBatch]:
        """
        Organize steps into batches that can execute in parallel.
        
        Steps in same batch have no dependencies on each other.
        """
        batches = []
        remaining_steps = set(s.id for s in self.plan.steps)
        completed_steps: Set[str] = set()
        batch_id = 0
        
        while remaining_steps:
            # Find steps whose dependencies are all satisfied
            ready_steps = []
            
            for step in self.plan.steps:
                if step.id not in remaining_steps:
                    continue
                
                # Check dependencies
                deps = self.plan.get_dependencies(step.id)
                
                if all(dep in completed_steps for dep in deps):
                    ready_steps.append(step)
            
            if not ready_steps:
                # No steps ready - check for circular dependencies
                if remaining_steps:
                    raise ValueError(f"Circular dependency detected: {remaining_steps}")
                break
            
            # Create batch
            batch = ExecutionBatch(
                batch_id=batch_id,
                steps=ready_steps,
                can_execute_parallel=len(ready_steps) > 1
            )
            
            batches.append(batch)
            
            # Mark as "will be completed"
            for step in ready_steps:
                remaining_steps.remove(step.id)
                completed_steps.add(step.id)
            
            batch_id += 1
        
        return batches
    
    def can_parallelize(self, step1_id: str, step2_id: str) -> bool:
        """Check if two steps can execute in parallel."""
        # Get dependencies for both
        deps1 = set(self.plan.get_dependencies(step1_id))
        deps2 = set(self.plan.get_dependencies(step2_id))
        
        # They can parallelize if neither depends on the other
        if step1_id in deps2 or step2_id in deps1:
            return False
        
        return True


class ParallelExecutor:
    """Executes steps in parallel when possible."""
    
    def __init__(self, config: Optional[ParallelExecutionConfig] = None):
        self.config = config or ParallelExecutionConfig()
        self.active_steps: Set[str] = set()
    
    async def execute_batch(
        self,
        batch: ExecutionBatch,
        step_executor: Any  # Function that executes single step
    ) -> Dict[str, Any]:
        """Execute a batch of steps (in parallel if possible)."""
        
        if not self.config.enable_parallel or not batch.can_execute_parallel:
            # Sequential execution
            results = {}
            for step in batch.steps:
                result = await self._execute_single_step(step, step_executor)
                results[step.id] = result
            return results
        
        # Parallel execution
        # Limit concurrency
        semaphore = asyncio.Semaphore(self.config.max_concurrent_steps)
        
        async def execute_with_limit(step):
            async with semaphore:
                return await self._execute_single_step(step, step_executor)
        
        # Execute all steps concurrently
        tasks = [asyncio.create_task(execute_with_limit(step)) for step in batch.steps]
        
        try:
            results_list = await asyncio.wait_for(
                asyncio.gather(*tasks),
                timeout=self.config.timeout_seconds
            )
            
            # Map results back to step IDs
            results = {
                step.id: result
                for step, result in zip(batch.steps, results_list)
            }
            
            return results
            
        except asyncio.TimeoutError:
            # Timeout - cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            
            raise TimeoutError(f"Batch {batch.batch_id} execution timed out")
    
    async def _execute_single_step(self, step: Step, executor) -> Dict[str, Any]:
        """Execute single step (async wrapper)."""
        self.active_steps.add(step.id)
        
        try:
            # If executor is async
            if asyncio.iscoroutinefunction(executor):
                result = await executor(step)
            else:
                # If executor is sync, run in executor
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, executor, step)
            
            return result
            
        finally:
            self.active_steps.discard(step.id)
    
    def get_active_steps(self) -> Set[str]:
        """Get currently executing step IDs."""
        return self.active_steps.copy()


async def execute_plan_parallel(
    plan,
    step_executor,
    config: Optional[ParallelExecutionConfig] = None
) -> Dict[str, Any]:
    """
    Execute plan with parallel execution of independent steps.
    
    Args:
        plan: ExecutionPlan
        step_executor: Function to execute single step
        config: Parallel execution configuration
    
    Returns:
        Execution results
    """
    analyzer = DependencyAnalyzer(plan)
    batches = analyzer.get_execution_batches()
    
    executor = ParallelExecutor(config)
    
    all_results = {}
    batch_timings = []
    
    for batch in batches:
        batch_start = datetime.utcnow()
        
        batch_results = await executor.execute_batch(batch, step_executor)
        all_results.update(batch_results)
        
        batch_end = datetime.utcnow()
        batch_duration = (batch_end - batch_start).total_seconds()
        
        batch_timings.append({
            "batch_id": batch.batch_id,
            "step_count": len(batch.steps),
            "parallel": batch.can_execute_parallel,
            "duration": batch_duration
        })
    
    return {
        "success": True,
        "results": all_results,
        "batches": len(batches),
        "batch_timings": batch_timings,
        "total_steps": len(plan.steps)
    }


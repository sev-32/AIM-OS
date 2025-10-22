"""Budget Pooling for APOE

Enables shared budget pools across steps for efficient resource management.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from apoe.models import Budget


class PoolStrategy(str, Enum):
    """Strategy for allocating from shared pool."""
    FAIR = "fair"  # Equal distribution
    PRIORITY = "priority"  # Higher priority gets more
    GREEDY = "greedy"  # First-come, first-served
    ADAPTIVE = "adaptive"  # Adjusts based on actual usage


@dataclass
class BudgetPool:
    """Shared budget pool for multiple steps."""
    pool_id: str
    total_tokens: int
    total_time: float  # seconds
    remaining_tokens: int = field(default=None)
    remaining_time: float = field(default=None)
    participants: Set[str] = field(default_factory=set)
    strategy: PoolStrategy = PoolStrategy.FAIR
    allocations: Dict[str, Budget] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.remaining_tokens is None:
            self.remaining_tokens = self.total_tokens
        if self.remaining_time is None:
            self.remaining_time = self.total_time
    
    def add_participant(self, step_id: str):
        """Add step to pool."""
        self.participants.add(step_id)
    
    def allocate(self, step_id: str, requested: Budget) -> Budget:
        """
        Allocate budget from pool to step.
        
        Args:
            step_id: Step requesting allocation
            requested: Requested budget
        
        Returns:
            Allocated budget (may be less than requested)
        """
        if step_id not in self.participants:
            raise ValueError(f"Step {step_id} not in pool {self.pool_id}")
        
        # Apply strategy
        if self.strategy == PoolStrategy.FAIR:
            allocated = self._allocate_fair(step_id, requested)
        elif self.strategy == PoolStrategy.GREEDY:
            allocated = self._allocate_greedy(step_id, requested)
        elif self.strategy == PoolStrategy.ADAPTIVE:
            allocated = self._allocate_adaptive(step_id, requested)
        else:
            allocated = self._allocate_fair(step_id, requested)  # Default to fair
        
        # Track allocation
        self.allocations[step_id] = allocated
        
        # Deduct from pool
        self.remaining_tokens -= allocated.tokens_limit
        self.remaining_time -= allocated.time_limit_seconds
        
        return allocated
    
    def _allocate_fair(self, step_id: str, requested: Budget) -> Budget:
        """Fair allocation - equal share."""
        # How many steps still need allocation?
        unallocated = len(self.participants) - len(self.allocations)
        
        if unallocated <= 0:
            # No budget left
            return Budget(tokens_limit=0, time_limit_seconds=0.0)
        
        # Fair share
        fair_tokens = self.remaining_tokens // unallocated
        fair_time = self.remaining_time / unallocated
        
        # Give fair share or requested, whichever is smaller
        allocated_tokens = min(fair_tokens, requested.tokens_limit)
        allocated_time = min(fair_time, requested.time_limit_seconds)
        
        return Budget(tokens_limit=allocated_tokens, time_limit_seconds=allocated_time)
    
    def _allocate_greedy(self, step_id: str, requested: Budget) -> Budget:
        """Greedy allocation - first come, first served."""
        allocated_tokens = min(self.remaining_tokens, requested.tokens_limit)
        allocated_time = min(self.remaining_time, requested.time_limit_seconds)
        
        return Budget(tokens_limit=allocated_tokens, time_limit_seconds=allocated_time)
    
    def _allocate_adaptive(self, step_id: str, requested: Budget) -> Budget:
        """Adaptive allocation - based on historical usage."""
        # For now, same as fair (would need historical data)
        # Future: Adjust based on actual usage patterns
        return self._allocate_fair(step_id, requested)
    
    def return_unused(self, step_id: str, used: Budget):
        """Return unused budget to pool."""
        if step_id not in self.allocations:
            return
        
        allocated = self.allocations[step_id]
        
        # Calculate unused
        unused_tokens = allocated.tokens_limit - used.tokens_consumed
        unused_time = allocated.time_limit_seconds - used.time_elapsed_seconds
        
        # Return to pool
        self.remaining_tokens += max(0, unused_tokens)
        self.remaining_time += max(0.0, unused_time)
    
    def get_utilization(self) -> Dict[str, float]:
        """Get pool utilization stats."""
        token_used = self.total_tokens - self.remaining_tokens
        time_used = self.total_time - self.remaining_time
        
        return {
            "token_utilization": token_used / self.total_tokens if self.total_tokens > 0 else 0.0,
            "time_utilization": time_used / self.total_time if self.total_time > 0 else 0.0,
            "remaining_tokens": self.remaining_tokens,
            "remaining_time": self.remaining_time
        }


class BudgetPoolManager:
    """Manages multiple budget pools."""
    
    def __init__(self):
        self.pools: Dict[str, BudgetPool] = {}
    
    def create_pool(
        self,
        pool_id: str,
        total_tokens: int,
        total_time: float,
        strategy: PoolStrategy = PoolStrategy.FAIR
    ) -> BudgetPool:
        """Create new budget pool."""
        pool = BudgetPool(
            pool_id=pool_id,
            total_tokens=total_tokens,
            total_time=total_time,
            strategy=strategy
        )
        
        self.pools[pool_id] = pool
        return pool
    
    def get_pool(self, pool_id: str) -> Optional[BudgetPool]:
        """Get pool by ID."""
        return self.pools.get(pool_id)
    
    def add_to_pool(self, pool_id: str, step_id: str):
        """Add step to pool."""
        pool = self.pools.get(pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} not found")
        
        pool.add_participant(step_id)
    
    def allocate_from_pool(
        self,
        pool_id: str,
        step_id: str,
        requested: Budget
    ) -> Budget:
        """Allocate budget from pool to step."""
        pool = self.pools.get(pool_id)
        if not pool:
            raise ValueError(f"Pool {pool_id} not found")
        
        return pool.allocate(step_id, requested)
    
    def return_to_pool(self, pool_id: str, step_id: str, used: Budget):
        """Return unused budget to pool."""
        pool = self.pools.get(pool_id)
        if pool:
            pool.return_unused(step_id, used)
    
    def get_all_utilization(self) -> Dict[str, Dict[str, float]]:
        """Get utilization for all pools."""
        return {
            pool_id: pool.get_utilization()
            for pool_id, pool in self.pools.items()
        }


def create_pool_from_steps(
    pool_id: str,
    step_ids: List[str],
    total_budget: Budget,
    strategy: PoolStrategy = PoolStrategy.FAIR
) -> BudgetPool:
    """
    Create budget pool from list of steps.
    
    Args:
        pool_id: Pool identifier
        step_ids: Steps to include in pool
        total_budget: Total budget for pool
        strategy: Allocation strategy
    
    Returns:
        Configured budget pool
    """
    pool = BudgetPool(
        pool_id=pool_id,
        total_tokens=total_budget.tokens_limit,
        total_time=total_budget.time_limit_seconds,
        strategy=strategy
    )
    
    for step_id in step_ids:
        pool.add_participant(step_id)
    
    return pool


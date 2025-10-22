"""Tests for Budget Pooling"""

from __future__ import annotations
import pytest

from apoe.budget_pooling import (
    BudgetPool,
    BudgetPoolManager,
    PoolStrategy,
    create_pool_from_steps
)
from apoe.models import Budget


def test_budget_pool_creation():
    """Test creating budget pool."""
    pool = BudgetPool(
        pool_id="test_pool",
        total_tokens=1000,
        total_time=60.0,
        strategy=PoolStrategy.FAIR
    )
    
    assert pool.pool_id == "test_pool"
    assert pool.total_tokens == 1000
    assert pool.remaining_tokens == 1000
    assert pool.total_time == 60.0
    assert pool.remaining_time == 60.0
    assert len(pool.participants) == 0


def test_add_participants():
    """Test adding participants to pool."""
    pool = BudgetPool(pool_id="test", total_tokens=1000, total_time=60.0)
    
    pool.add_participant("step1")
    pool.add_participant("step2")
    
    assert len(pool.participants) == 2
    assert "step1" in pool.participants
    assert "step2" in pool.participants


def test_fair_allocation():
    """Test fair allocation strategy."""
    pool = BudgetPool(
        pool_id="test",
        total_tokens=900,
        total_time=60.0,
        strategy=PoolStrategy.FAIR
    )
    
    pool.add_participant("s1")
    pool.add_participant("s2")
    pool.add_participant("s3")
    
    # Each step requests 500 tokens
    requested = Budget(tokens_limit=500, time_limit_seconds=30.0)
    
    # First allocation: 900/3 = 300 tokens (fair share)
    alloc1 = pool.allocate("s1", requested)
    assert alloc1.tokens_limit == 300
    assert alloc1.time_limit_seconds == 20.0
    
    # Second allocation: 600/2 = 300 tokens
    alloc2 = pool.allocate("s2", requested)
    assert alloc2.tokens_limit == 300
    
    # Third allocation: 300/1 = 300 tokens
    alloc3 = pool.allocate("s3", requested)
    assert alloc3.tokens_limit == 300
    
    # Pool should be exhausted
    assert pool.remaining_tokens == 0


def test_greedy_allocation():
    """Test greedy allocation strategy."""
    pool = BudgetPool(
        pool_id="test",
        total_tokens=1000,
        total_time=60.0,
        strategy=PoolStrategy.GREEDY
    )
    
    pool.add_participant("s1")
    pool.add_participant("s2")
    
    # s1 requests and gets 700 tokens
    alloc1 = pool.allocate("s1", Budget(tokens_limit=700, time_limit_seconds=40.0))
    assert alloc1.tokens_limit == 700
    assert pool.remaining_tokens == 300
    
    # s2 requests 500 but only 300 remain
    alloc2 = pool.allocate("s2", Budget(tokens_limit=500, time_limit_seconds=30.0))
    assert alloc2.tokens_limit == 300
    assert pool.remaining_tokens == 0


def test_return_unused_budget():
    """Test returning unused budget to pool."""
    pool = BudgetPool(pool_id="test", total_tokens=1000, total_time=60.0)
    pool.add_participant("s1")
    
    # Allocate 500 tokens
    allocated = pool.allocate("s1", Budget(tokens_limit=500, time_limit_seconds=30.0))
    assert pool.remaining_tokens == 500
    
    # Step only used 300 tokens
    used = Budget(tokens_consumed=300, time_elapsed_seconds=20.0)
    pool.return_unused("s1", used)
    
    # 200 tokens returned
    assert pool.remaining_tokens == 700


def test_pool_utilization():
    """Test pool utilization calculation."""
    pool = BudgetPool(pool_id="test", total_tokens=1000, total_time=60.0)
    pool.add_participant("s1")
    
    # Use 400 tokens
    pool.allocate("s1", Budget(tokens_limit=400, time_limit_seconds=24.0))
    
    util = pool.get_utilization()
    
    assert util["token_utilization"] == 0.4  # 400/1000
    assert util["time_utilization"] == 0.4   # 24/60
    assert util["remaining_tokens"] == 600
    assert util["remaining_time"] == 36.0


def test_budget_pool_manager():
    """Test budget pool manager."""
    manager = BudgetPoolManager()
    
    # Create pool
    pool = manager.create_pool(
        pool_id="pool1",
        total_tokens=1000,
        total_time=60.0,
        strategy=PoolStrategy.FAIR
    )
    
    assert pool.pool_id == "pool1"
    assert manager.get_pool("pool1") == pool


def test_manager_add_to_pool():
    """Test adding steps to pool via manager."""
    manager = BudgetPoolManager()
    manager.create_pool("pool1", 1000, 60.0)
    
    manager.add_to_pool("pool1", "step1")
    manager.add_to_pool("pool1", "step2")
    
    pool = manager.get_pool("pool1")
    assert len(pool.participants) == 2


def test_manager_allocate():
    """Test allocation via manager."""
    manager = BudgetPoolManager()
    manager.create_pool("pool1", 1000, 60.0, PoolStrategy.GREEDY)
    manager.add_to_pool("pool1", "step1")
    
    allocated = manager.allocate_from_pool(
        "pool1",
        "step1",
        Budget(tokens_limit=500, time_limit_seconds=30.0)
    )
    
    assert allocated.tokens_limit == 500


def test_manager_return_unused():
    """Test returning unused budget via manager."""
    manager = BudgetPoolManager()
    manager.create_pool("pool1", 1000, 60.0)
    manager.add_to_pool("pool1", "step1")
    
    manager.allocate_from_pool("pool1", "step1", Budget(tokens_limit=500, time_limit_seconds=30.0))
    
    # Return 200 unused tokens
    manager.return_to_pool("pool1", "step1", Budget(tokens_consumed=300, time_elapsed_seconds=20.0))
    
    pool = manager.get_pool("pool1")
    assert pool.remaining_tokens == 700


def test_manager_all_utilization():
    """Test getting utilization for all pools."""
    manager = BudgetPoolManager()
    
    manager.create_pool("pool1", 1000, 60.0)
    manager.create_pool("pool2", 2000, 120.0)
    
    manager.add_to_pool("pool1", "s1")
    manager.add_to_pool("pool2", "s2")
    
    manager.allocate_from_pool("pool1", "s1", Budget(tokens_limit=400, time_limit_seconds=24.0))
    manager.allocate_from_pool("pool2", "s2", Budget(tokens_limit=1000, time_limit_seconds=60.0))
    
    all_util = manager.get_all_utilization()
    
    assert "pool1" in all_util
    assert "pool2" in all_util
    assert all_util["pool1"]["token_utilization"] == 0.4
    assert all_util["pool2"]["token_utilization"] == 0.5


def test_create_pool_from_steps():
    """Test helper to create pool from step list."""
    step_ids = ["s1", "s2", "s3"]
    total_budget = Budget(tokens_limit=1500, time_limit_seconds=90.0)
    
    pool = create_pool_from_steps(
        pool_id="test",
        step_ids=step_ids,
        total_budget=total_budget,
        strategy=PoolStrategy.FAIR
    )
    
    assert pool.pool_id == "test"
    assert pool.total_tokens == 1500
    assert len(pool.participants) == 3
    assert all(sid in pool.participants for sid in step_ids)


def test_allocation_requires_participant():
    """Test that allocation requires step to be in pool."""
    pool = BudgetPool(pool_id="test", total_tokens=1000, total_time=60.0)
    
    # Try to allocate to step not in pool
    with pytest.raises(ValueError, match="not in pool"):
        pool.allocate("unknown_step", Budget(tokens_limit=100, time_limit_seconds=10.0))


def test_manager_nonexistent_pool():
    """Test manager with nonexistent pool."""
    manager = BudgetPoolManager()
    
    with pytest.raises(ValueError, match="Pool .* not found"):
        manager.add_to_pool("nonexistent", "step1")
    
    with pytest.raises(ValueError, match="Pool .* not found"):
        manager.allocate_from_pool("nonexistent", "step1", Budget(tokens_limit=100, time_limit_seconds=10.0))


def test_pool_strategy_enum():
    """Test pool strategy enum."""
    assert PoolStrategy.FAIR == "fair"
    assert PoolStrategy.GREEDY == "greedy"
    assert PoolStrategy.ADAPTIVE == "adaptive"


"""Tests for performance optimization utilities."""

from __future__ import annotations

import sqlite3
from pathlib import Path
import time

import pytest

from cmc_service.performance import (
    ConnectionPool,
    PerformanceMonitor,
    IndexOptimizer,
    BatchWriter,
)


def test_connection_pool_basic(tmp_path: Path):
    """Test basic connection pool operations."""
    db_path = tmp_path / "test.db"
    pool = ConnectionPool(str(db_path), pool_size=3)
    
    # Get connection
    with pool.get_connection() as conn:
        assert conn is not None
        conn.execute("CREATE TABLE test (id INTEGER)")
    
    # Get another connection (should be from pool)
    with pool.get_connection() as conn:
        conn.execute("INSERT INTO test VALUES (1)")
    
    pool.close_all()


def test_connection_pool_concurrent(tmp_path: Path):
    """Test connection pool handles concurrent access."""
    db_path = tmp_path / "test.db"
    pool = ConnectionPool(str(db_path), pool_size=2)
    
    # Use both connections simultaneously
    with pool.get_connection() as conn1:
        conn1.execute("CREATE TABLE test (id INTEGER)")
        
        with pool.get_connection() as conn2:
            # Both connections should work
            assert conn1 is not None
            assert conn2 is not None
    
    pool.close_all()


def test_performance_monitor_records():
    """Test performance monitor records operations."""
    monitor = PerformanceMonitor()
    
    # Record some operations
    monitor.record_operation('atom_create', 45.2, success=True)
    monitor.record_operation('atom_create', 52.1, success=True)
    monitor.record_operation('atom_create', 48.7, success=True)
    
    stats = monitor.get_stats('atom_create')
    assert stats is not None
    assert stats['count'] == 3
    assert stats['success_count'] == 3
    assert 40 < stats['avg'] < 60


def test_performance_monitor_percentiles():
    """Test performance monitor calculates percentiles correctly."""
    monitor = PerformanceMonitor()
    
    # Record operations with known distribution
    for i in range(100):
        monitor.record_operation('test_op', float(i), success=True)
    
    stats = monitor.get_stats('test_op')
    assert stats['p50'] == 50  # Median
    assert stats['p95'] == 95
    assert stats['p99'] == 99
    assert stats['min'] == 0
    assert stats['max'] == 99


def test_performance_monitor_multiple_operations():
    """Test monitor tracks multiple operation types."""
    monitor = PerformanceMonitor()
    
    monitor.record_operation('read', 10.0)
    monitor.record_operation('write', 50.0)
    monitor.record_operation('read', 12.0)
    
    all_stats = monitor.get_all_stats()
    assert 'read' in all_stats
    assert 'write' in all_stats
    assert all_stats['read']['count'] == 2
    assert all_stats['write']['count'] == 1


def test_index_optimizer_creates_indexes(tmp_path: Path):
    """Test index optimizer creates optimal indexes."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    
    # Create base schema
    conn.execute("""
        CREATE TABLE mpd_nodes (
            mpd_id TEXT PRIMARY KEY,
            tt_start TEXT,
            tt_end TEXT,
            vt_start TEXT,
            vt_end TEXT
        )
    """)
    
    # Create optimal indexes
    indexes = IndexOptimizer.create_optimal_indexes(conn)
    
    assert len(indexes) >= 3  # Should create multiple indexes
    assert 'idx_mpd_nodes_tt_range' in indexes
    assert 'idx_mpd_nodes_vt_range' in indexes
    assert 'idx_mpd_nodes_id_tt' in indexes
    
    conn.close()


def test_index_optimizer_analyzes_queries(tmp_path: Path):
    """Test query plan analysis."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    
    # Create table and index
    conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
    conn.execute("CREATE INDEX idx_test_value ON test(value)")
    
    # Analyze indexed query
    analysis = IndexOptimizer.analyze_query_plan(
        conn,
        "SELECT * FROM test WHERE value = 'test'"
    )
    
    assert 'uses_index' in analysis
    assert 'full_scan' in analysis
    assert 'plan_rows' in analysis
    
    conn.close()


def test_batch_writer_batches_operations():
    """Test batch writer accumulates operations."""
    writer = BatchWriter(batch_size=5)
    
    # Add operations
    for i in range(3):
        result = writer.add_operation(("INSERT INTO test VALUES (?)", (i,)))
        assert result is None  # Not full yet
    
    assert writer.pending_count() == 3
    
    # Add more until batch is full
    writer.add_operation(("INSERT INTO test VALUES (?)", (3,)))
    result = writer.add_operation(("INSERT INTO test VALUES (?)", (4,)))  # 5th operation triggers flush
    
    # Should have flushed
    assert result is not None
    assert len(result) == 5
    assert writer.pending_count() == 0  # Flushed


def test_batch_writer_manual_flush():
    """Test manual flush of batch writer."""
    writer = BatchWriter(batch_size=100)
    
    # Add some operations
    for i in range(10):
        writer.add_operation(("INSERT INTO test VALUES (?)", (i,)))
    
    assert writer.pending_count() == 10
    
    # Manual flush
    results = writer.flush()
    assert len(results) == 10
    assert writer.pending_count() == 0


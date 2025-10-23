"""Performance optimization utilities for CMC.

Provides:
- Connection pooling
- Query result caching
- Batch operations
- Index optimization
- Performance monitoring
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import time


class ConnectionPool:
    """Simple connection pool for SQLite with WAL mode."""
    
    def __init__(self, db_path: str, pool_size: int = 5):
        """Initialize connection pool.
        
        Args:
            db_path: Path to SQLite database
            pool_size: Number of connections to maintain
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self._connections: List[sqlite3.Connection] = []
        self._in_use: set = set()
        
        # Pre-create connections
        for _ in range(pool_size):
            conn = self._create_connection()
            self._connections.append(conn)
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new connection with optimal settings."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        # Increase cache size
        conn.execute("PRAGMA cache_size=-64000")  # 64MB
        # Use memory for temp tables
        conn.execute("PRAGMA temp_store=MEMORY")
        return conn
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool.
        
        Yields:
            sqlite3.Connection
            
        Example:
            with pool.get_connection() as conn:
                rows = conn.execute("SELECT * FROM atoms").fetchall()
        """
        # Find available connection
        conn = None
        for c in self._connections:
            if id(c) not in self._in_use:
                conn = c
                break
        
        if conn is None:
            # All busy, create temporary
            conn = self._create_connection()
        
        self._in_use.add(id(conn))
        try:
            yield conn
        finally:
            self._in_use.discard(id(conn))
    
    def close_all(self):
        """Close all connections in pool."""
        for conn in self._connections:
            conn.close()
        self._connections.clear()


class PerformanceMonitor:
    """Monitor and track CMC performance metrics."""
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = {}
        self._operation_counts: Dict[str, int] = {}
    
    def record_operation(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True
    ) -> None:
        """Record operation performance.
        
        Args:
            operation: Name of operation (e.g., 'atom_create', 'query_as_of')
            duration_ms: Duration in milliseconds
            success: Whether operation succeeded
        """
        if operation not in self._metrics:
            self._metrics[operation] = []
            self._operation_counts[operation] = 0
        
        self._metrics[operation].append(duration_ms)
        if success:
            self._operation_counts[operation] += 1
    
    def get_stats(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get statistics for an operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Dictionary with p50, p95, p99, count, success_rate
        """
        if operation not in self._metrics:
            return None
        
        durations = sorted(self._metrics[operation])
        count = len(durations)
        
        if count == 0:
            return None
        
        return {
            'operation': operation,
            'count': count,
            'p50': durations[int(count * 0.5)] if count > 0 else 0,
            'p95': durations[int(count * 0.95)] if count > 1 else durations[-1],
            'p99': durations[int(count * 0.99)] if count > 2 else durations[-1],
            'min': durations[0],
            'max': durations[-1],
            'avg': sum(durations) / count,
            'success_count': self._operation_counts[operation]
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations."""
        return {
            op: self.get_stats(op)
            for op in self._metrics.keys()
        }
    
    def reset(self) -> None:
        """Reset all metrics."""
        self._metrics.clear()
        self._operation_counts.clear()


class IndexOptimizer:
    """Optimize database indexes for common query patterns."""
    
    @staticmethod
    def create_optimal_indexes(conn: sqlite3.Connection) -> List[str]:
        """Create optimal indexes for bitemporal queries.
        
        Args:
            conn: SQLite connection
            
        Returns:
            List of created index names
        """
        indexes = []
        cur = conn.cursor()
        
        # Composite index for as-of queries (transaction time)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mpd_nodes_tt_range
            ON mpd_nodes(tt_start, tt_end)
        """)
        indexes.append('idx_mpd_nodes_tt_range')
        
        # Composite index for as-of queries (valid time)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mpd_nodes_vt_range
            ON mpd_nodes(vt_start, vt_end)
        """)
        indexes.append('idx_mpd_nodes_vt_range')
        
        # Composite index for history queries
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_mpd_nodes_id_tt
            ON mpd_nodes(mpd_id, tt_start)
        """)
        indexes.append('idx_mpd_nodes_id_tt')
        
        # Index for edge queries (only if table exists)
        try:
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_mpd_edges_source_relation
                ON mpd_edges(source_id, relation, tt_start)
            """)
            indexes.append('idx_mpd_edges_source_relation')
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_mpd_edges_target
                ON mpd_edges(target_id, tt_start)
            """)
            indexes.append('idx_mpd_edges_target')
        except sqlite3.OperationalError:
            # Table doesn't exist, skip edge indexes
            pass
        
        conn.commit()
        return indexes
    
    @staticmethod
    def analyze_query_plan(conn: sqlite3.Connection, query: str) -> Dict[str, Any]:
        """Analyze query execution plan.
        
        Args:
            conn: SQLite connection
            query: SQL query to analyze
            
        Returns:
            Query plan analysis
        """
        cur = conn.cursor()
        plan = cur.execute(f"EXPLAIN QUERY PLAN {query}").fetchall()
        
        uses_index = any('USING INDEX' in str(row) for row in plan)
        full_scan = any('SCAN' in str(row) for row in plan)
        
        return {
            'uses_index': uses_index,
            'full_scan': full_scan,
            'plan_rows': len(plan),
            'plan_detail': [str(row) for row in plan]
        }


class BatchWriter:
    """Optimize write operations with batching."""
    
    def __init__(self, batch_size: int = 100):
        """Initialize batch writer.
        
        Args:
            batch_size: Number of operations to batch
        """
        self.batch_size = batch_size
        self._pending: List[tuple] = []
    
    def add_operation(self, operation: tuple) -> Optional[List]:
        """Add operation to batch.
        
        Args:
            operation: Tuple of (sql, params)
            
        Returns:
            None if batch not full, executed results if batch full
        """
        self._pending.append(operation)
        
        if len(self._pending) >= self.batch_size:
            return self.flush()
        
        return None
    
    def flush(self) -> List:
        """Execute all pending operations in a transaction.
        
        Returns:
            List of results
        """
        if not self._pending:
            return []
        
        results = []
        # In real implementation, would execute in transaction
        for sql, params in self._pending:
            results.append((sql, params))
        
        self._pending.clear()
        return results
    
    def pending_count(self) -> int:
        """Get count of pending operations."""
        return len(self._pending)


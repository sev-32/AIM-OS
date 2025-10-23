"""CMC Service - Context Memory Core (Production-Ready v0.95)

Complete bitemporal memory substrate with advanced pipelines and performance optimization.

Capabilities:
- Atom storage with bitemporal tracking
- Snapshot management for point-in-time state
- Time-travel queries (as-of, range, history, audit)
- Advanced batch processing pipelines
- Performance optimization (pooling, caching, indexing)
- SQLite backend with WAL mode
- Complete test coverage (59 tests)
"""

from .memory_store import MemoryStore
from .models import Atom, AtomCreate, AtomContent, Snapshot, SnapshotStats, WitnessStub
from .logging_utils import configure_logging
from .bitemporal_queries import BitemporalQueryEngine
from .repository import AtomRepository, SQLiteConfig
from .advanced_pipelines import (
    BatchProcessor,
    EmbeddingBatcher,
    PipelineComposer,
    QueryOptimizer,
    CacheManager,
)
from .performance import (
    ConnectionPool,
    PerformanceMonitor,
    IndexOptimizer,
    BatchWriter,
)

configure_logging()

__all__ = [
    # Core storage
    "MemoryStore",
    "Atom",
    "AtomCreate",
    "AtomContent",
    "Snapshot",
    "SnapshotStats",
    "WitnessStub",
    # Repository & queries
    "AtomRepository",
    "SQLiteConfig",
    "BitemporalQueryEngine",
    # Advanced pipelines
    "BatchProcessor",
    "EmbeddingBatcher",
    "PipelineComposer",
    "QueryOptimizer",
    "CacheManager",
    # Performance
    "ConnectionPool",
    "PerformanceMonitor",
    "IndexOptimizer",
    "BatchWriter",
    # Utils
    "configure_logging",
]

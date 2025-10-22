"""HHNI package exposing indexing, search, budget, physics, and retrieval primitives."""

from .hierarchical_index import HierarchicalIndex, IndexLevel, IndexNode  # noqa: F401
from .semantic_search import EmbeddingProvider, SearchResult, SemanticSearchEngine  # noqa: F401
from .budget_manager import (  # noqa: F401
    BudgetAllocation,
    BudgetItem,
    BudgetStrategy,
    TokenBudgetManager,
)
from .dvns_physics import (  # noqa: F401
    ContextParticle,
    DVNSConfig,
    DVNSPhysics,
    SimulationMetrics,
    SimulationResult,
)
from .retrieval import RetrievalConfig, RetrievalResult, TwoStageRetriever  # noqa: F401
from .models import HHNINode, TagPriorityVector  # noqa: F401
from .deduplication import DeduplicationMetrics, deduplicate_candidates  # noqa: F401
from .conflict_resolver import ConflictMetrics, ConflictRecord, detect_conflicts  # noqa: F401
from .compressor import (  # noqa: F401
    CompressionConfig,
    CompressionLevel,
    CompressionMetrics,
    compress_candidates,
)

__all__ = [
    # Indexing & search
    "HierarchicalIndex",
    "IndexLevel",
    "IndexNode",
    "EmbeddingProvider",
    "SearchResult",
    "SemanticSearchEngine",
    # Budgeting
    "BudgetAllocation",
    "BudgetItem",
    "BudgetStrategy",
    "TokenBudgetManager",
    # DVNS physics
    "ContextParticle",
    "DVNSConfig",
    "DVNSPhysics",
    "SimulationMetrics",
    "SimulationResult",
    # Retrieval
    "RetrievalConfig",
    "RetrievalResult",
    "TwoStageRetriever",
    # Deduplication
    "DeduplicationMetrics",
    "deduplicate_candidates",
    # Conflict resolution
    "ConflictMetrics",
    "ConflictRecord",
    "detect_conflicts",
    # Compression
    "CompressionConfig",
    "CompressionLevel",
    "CompressionMetrics",
    "compress_candidates",
    # Legacy data models
    "HHNINode",
    "TagPriorityVector",
]

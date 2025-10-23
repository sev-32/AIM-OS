"""SEG: Shared Evidence Graph (Production-Ready)

Bitemporal knowledge graph with contradiction detection and provenance tracking.

Components:
- Entity, Relation, Evidence nodes (bitemporal)
- SEGraph (NetworkX-based graph with time-travel)
- Contradiction detection
- Provenance tracing
- CMC integration
"""

from .models import (
    Entity,
    Relation,
    Evidence,
    Contradiction,
    TimeSlice,
    NodeType,
    RelationType,
)
from .seg_graph import SEGraph
from .witness import write_witness  # Legacy function for compatibility

__all__ = [
    # Core models
    "Entity",
    "Relation",
    "Evidence",
    "Contradiction",
    "TimeSlice",
    # Enums
    "NodeType",
    "RelationType",
    # Graph
    "SEGraph",
    # Legacy
    "write_witness",
]

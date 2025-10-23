"""SEG (Shared Evidence Graph) core models.

Defines Entity, Relation, and Evidence nodes for knowledge graph.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid


class NodeType(str, Enum):
    """Types of nodes in the evidence graph."""
    ENTITY = "entity"
    EVIDENCE = "evidence"
    CLAIM = "claim"


class RelationType(str, Enum):
    """Types of relationships between nodes."""
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    REFERENCES = "references"
    DERIVES_FROM = "derives_from"
    RELATES_TO = "relates_to"


class Entity(BaseModel):
    """Entity node in the knowledge graph.
    
    Represents a thing, concept, or fact with bitemporal tracking.
    """
    id: str = Field(default_factory=lambda: f"entity_{uuid.uuid4().hex[:12]}")
    type: str  # Entity type (person, concept, event, etc.)
    name: str  # Human-readable name
    attributes: Dict[str, Any] = Field(default_factory=dict)  # Additional properties
    
    # Bitemporal tracking
    tt_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Transaction time start
    tt_end: Optional[datetime] = None  # Transaction time end (None = current)
    vt_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Valid time start
    vt_end: Optional[datetime] = None  # Valid time end (None = still valid)
    
    # Metadata
    source: Optional[str] = None  # Where this entity came from
    confidence: float = 1.0  # Confidence in this entity (0-1)
    tags: List[str] = Field(default_factory=list)
    
    # VIF integration
    witness_id: Optional[str] = None  # VIF witness for provenance
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "entity_abc123",
                "type": "concept",
                "name": "Neural Architecture Search",
                "attributes": {"field": "machine_learning", "year": 2023},
                "confidence": 0.95,
                "tags": ["ai", "architecture"]
            }
        }
    )


class Relation(BaseModel):
    """Relation edge between entities.
    
    Represents a typed relationship with evidence support.
    """
    id: str = Field(default_factory=lambda: f"relation_{uuid.uuid4().hex[:12]}")
    source_id: str  # Source entity ID
    target_id: str  # Target entity ID
    relation_type: RelationType  # Type of relationship
    
    # Supporting evidence
    evidence_ids: List[str] = Field(default_factory=list)  # Evidence supporting this relation
    confidence: float = 1.0  # Confidence in this relation (0-1)
    
    # Bitemporal tracking
    tt_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tt_end: Optional[datetime] = None
    vt_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    vt_end: Optional[datetime] = None
    
    # Metadata
    source: Optional[str] = None  # Where this relation came from
    tags: List[str] = Field(default_factory=list)
    
    # VIF integration
    witness_id: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "relation_xyz789",
                "source_id": "entity_abc123",
                "target_id": "entity_def456",
                "relation_type": "supports",
                "evidence_ids": ["evidence_001", "evidence_002"],
                "confidence": 0.85
            }
        }
    )


class Evidence(BaseModel):
    """Evidence node supporting claims and relations.
    
    Represents a piece of evidence (document, observation, etc).
    """
    id: str = Field(default_factory=lambda: f"evidence_{uuid.uuid4().hex[:12]}")
    content: str  # The actual evidence content
    source: str  # Source of this evidence (URL, citation, etc.)
    evidence_type: str = "text"  # Type of evidence (text, image, data, etc.)
    
    # Quality metrics
    confidence: float = 1.0  # Confidence in this evidence (0-1)
    reliability: float = 1.0  # Reliability of the source (0-1)
    
    # Bitemporal tracking
    tt_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tt_end: Optional[datetime] = None
    vt_start: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    vt_end: Optional[datetime] = None
    
    # CMC integration
    atom_id: Optional[str] = None  # CMC atom ID if this evidence came from memory
    
    # VIF integration
    witness_id: Optional[str] = None
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "evidence_001",
                "content": "Research paper shows 95% accuracy on ImageNet",
                "source": "https://arxiv.org/abs/2023.12345",
                "evidence_type": "academic_paper",
                "confidence": 0.90,
                "reliability": 0.95
            }
        }
    )


class Contradiction(BaseModel):
    """Detected contradiction between two entities or relations.
    
    Represents a conflict that needs resolution.
    """
    id: str = Field(default_factory=lambda: f"contradiction_{uuid.uuid4().hex[:12]}")
    entity1_id: str  # First conflicting entity/relation
    entity2_id: str  # Second conflicting entity/relation
    contradiction_type: str  # Type of contradiction
    
    # Analysis
    similarity: float  # How similar the entities are (0-1)
    confidence: float  # Confidence that this is actually a contradiction (0-1)
    explanation: str  # Human-readable explanation
    
    # Resolution
    resolved: bool = False
    resolution: Optional[str] = None  # How this was resolved
    resolved_at: Optional[datetime] = None
    
    # Metadata
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "contradiction_001",
                "entity1_id": "entity_abc",
                "entity2_id": "entity_xyz",
                "contradiction_type": "conflicting_claim",
                "similarity": 0.85,
                "confidence": 0.75,
                "explanation": "Both entities claim different values for the same property",
                "resolved": False
            }
        }
    )


class TimeSlice(BaseModel):
    """A snapshot of the graph at a specific point in time."""
    timestamp: datetime
    entity_count: int
    relation_count: int
    evidence_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


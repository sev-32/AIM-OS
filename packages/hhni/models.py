"""Dataclasses representing HHNI nodes and related structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Dict, List, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def sha256_hex(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


@dataclass
class TagPriorityVector:
    priority: float = 0.5
    relevance: float = 1.0
    decay_tau: int = 365


@dataclass
class HHNINode:
    """In-memory representation of a HHNI node prior to persistence."""

    id: str
    level: int
    path: str

    content_hash: str
    text: Optional[str] = None

    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)

    depends_on: List[str] = field(default_factory=list)
    depended_by: List[str] = field(default_factory=list)

    vector_id: Optional[str] = None  # reference to vector store entry
    tags: Dict[str, float] = field(default_factory=dict)
    tpv: TagPriorityVector = field(default_factory=TagPriorityVector)

    atom_refs: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)
    snapshot_id: str = ""

    impact_score: Optional[float] = None
    staleness_days: Optional[int] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "level": self.level,
            "path": self.path,
            "content_hash": self.content_hash,
            "text": self.text,
            "parent_id": self.parent_id,
            "children_ids": list(self.children_ids),
            "depends_on": list(self.depends_on),
            "depended_by": list(self.depended_by),
            "vector_id": self.vector_id,
            "tags": dict(self.tags),
            "tpv": {
                "priority": self.tpv.priority,
                "relevance": self.tpv.relevance,
                "decay_tau": self.tpv.decay_tau,
            },
            "atom_refs": list(self.atom_refs),
            "created_at": self.created_at.isoformat(),
            "snapshot_id": self.snapshot_id,
            "impact_score": self.impact_score,
            "staleness_days": self.staleness_days,
        }

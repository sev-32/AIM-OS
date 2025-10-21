from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from datetime import timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional


ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def _isoformat(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime(ISO_FORMAT)


def _parse_datetime(value: str) -> datetime:
    return datetime.strptime(value, ISO_FORMAT).replace(tzinfo=timezone.utc)


@dataclass
class WitnessStub:
    model_id: Optional[str] = None
    tool_ids: List[str] = field(default_factory=list)
    snapshot_id: Optional[str] = None
    correlation_id: Optional[str] = None
    uncertainty_band: str = "green"
    uncertainty_ece: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "tool_ids": list(self.tool_ids),
            "snapshot_id": self.snapshot_id,
            "correlation_id": self.correlation_id,
            "uncertainty": {
                "band": self.uncertainty_band,
                "ece": self.uncertainty_ece,
            },
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WitnessStub":
        uncertainty = data.get("uncertainty", {}) or {}
        return cls(
            model_id=data.get("model_id"),
            tool_ids=list(data.get("tool_ids", []) or []),
            snapshot_id=data.get("snapshot_id"),
            correlation_id=data.get("correlation_id"),
            uncertainty_band=uncertainty.get("band", "green"),
            uncertainty_ece=uncertainty.get("ece"),
        )


@dataclass
class AtomContent:
    inline: Optional[str] = None
    uri: Optional[str] = None
    media_type: str = "text/plain"

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"media_type": self.media_type}
        if self.inline is not None:
            payload["inline"] = self.inline
        if self.uri is not None:
            payload["uri"] = self.uri
        return payload

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "AtomContent":
        return cls(
            inline=data.get("inline"),
            uri=data.get("uri"),
            media_type=data.get("media_type", "text/plain"),
        )


@dataclass
class AtomCreate:
    modality: str
    content: AtomContent
    tags: Mapping[str, float] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    policy_tags: Iterable[str] = field(default_factory=list)

    def to_record(self) -> Dict[str, Any]:
        record: Dict[str, Any] = {
            "modality": self.modality,
            "content": self.content.to_dict(),
            "tags": {k: float(v) for k, v in self.tags.items()},
            "metadata": dict(self.metadata),
        }
        if self.embedding is not None:
            record["embedding"] = list(self.embedding)
        policy = list(self.policy_tags or [])
        if policy:
            record["policy_tags"] = policy
        return record


@dataclass
class Atom(AtomCreate):
    id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    hash: str = ""
    witness: WitnessStub = field(default_factory=WitnessStub)
    snapshot_ids: List[str] = field(default_factory=list)

    def to_record(self) -> Dict[str, Any]:  # type: ignore[override]
        record = super().to_record()
        record.update(
            {
                "id": self.id,
                "created_at": _isoformat(self.created_at),
                "hash": self.hash,
                "witness": self.witness.to_dict(),
                "snapshot_ids": list(self.snapshot_ids),
            }
        )
        return record

    @classmethod
    def from_record(cls, data: Mapping[str, Any]) -> "Atom":
        atom = cls(
            modality=data["modality"],
            content=AtomContent.from_dict(data["content"]),
            tags=data.get("tags", {}),
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
            policy_tags=data.get("policy_tags", []),
            id=data["id"],
            created_at=_parse_datetime(data["created_at"]),
            hash=data.get("hash", ""),
            witness=WitnessStub.from_dict(data.get("witness", {})),
            snapshot_ids=list(data.get("snapshot_ids", [])),
        )
        return atom


@dataclass
class SnapshotStats:
    atom_count: int
    tag_counts: Mapping[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "atom_count": int(self.atom_count),
            "tag_counts": {k: int(v) for k, v in self.tag_counts.items()},
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SnapshotStats":
        return cls(
            atom_count=int(data.get("atom_count", 0)),
            tag_counts={k: int(v) for k, v in (data.get("tag_counts", {}) or {}).items()},
        )


@dataclass
class Snapshot:
    id: str
    created_at: datetime
    atom_ids: List[str]
    previous_id: Optional[str] = None
    note: Optional[str] = None
    stats: SnapshotStats = field(default_factory=lambda: SnapshotStats(atom_count=0))
    witness: WitnessStub = field(default_factory=WitnessStub)

    def to_record(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": _isoformat(self.created_at),
            "atom_ids": list(self.atom_ids),
            "previous_id": self.previous_id,
            "note": self.note,
            "stats": self.stats.to_dict(),
            "witness": self.witness.to_dict(),
        }

    @classmethod
    def from_record(cls, data: Mapping[str, Any]) -> "Snapshot":
        return cls(
            id=data["id"],
            created_at=_parse_datetime(data["created_at"]),
            atom_ids=list(data.get("atom_ids", [])),
            previous_id=data.get("previous_id"),
            note=data.get("note"),
            stats=SnapshotStats.from_dict(data.get("stats", {})),
            witness=WitnessStub.from_dict(data.get("witness", {})),
        )


__all__ = [
    "Atom",
    "AtomContent",
    "AtomCreate",
    "Snapshot",
    "SnapshotStats",
    "WitnessStub",
]

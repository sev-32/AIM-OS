"""Pydantic schema for BTSM edges with bitemporal metadata."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, model_validator


class BitemporalEdge(BaseModel):
    """Represents a relationship between two MPD nodes."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    target_id: str
    relation: str
    policy_pack_ids: List[str] = []
    tt_start: datetime
    tt_end: Optional[datetime] = None
    vt_start: datetime
    vt_end: Optional[datetime] = None

    @model_validator(mode="after")
    def ensure_policy_inheritance(self) -> "BitemporalEdge":
        if self.relation == "depends_on" and not self.policy_pack_ids:
            raise ValueError("depends_on edges must include policy_pack_ids")
        return self

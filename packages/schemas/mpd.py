"""Pydantic models for Minimal-Perfect-Details (MPD) nodes."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator


class KPIReference(BaseModel):
    """Lightweight KPI reference so nodes can surface metric hooks."""

    name: str
    target: Optional[float] = None


class MPDNode(BaseModel):
    """Minimal-Perfect-Details manager node."""

    model_config = ConfigDict(extra="forbid")

    mpd_id: str
    type: str
    purpose: str
    capabilities: List[str] = []
    interfaces: List[str] = []
    manager_of: List[str] = []
    depends_on: List[str] = []
    policy_pack_ids: List[str] = []
    budgets: List[str] = []
    owners: List[str] = []
    kpis: List[KPIReference] = []
    lifecycle: Optional[str] = None
    witness: Optional[str] = None
    links: List[str] = []
    max_dependency_degree: int = 0
    tt_start: datetime
    tt_end: Optional[datetime] = None
    vt_start: datetime
    vt_end: Optional[datetime] = None

    @field_validator("max_dependency_degree")
    @classmethod
    def validate_degree(cls, value: int) -> int:
        if value < 0:
            raise ValueError("max_dependency_degree cannot be negative")
        return value

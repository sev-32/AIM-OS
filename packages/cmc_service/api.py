from __future__ import annotations

import os
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Literal, Optional, Set, Tuple

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel
import json

from schemas import BitemporalEdge, MPDNode

from .btsm import draft_trunk_nodes
from .repository import AtomRepository, SQLiteConfig

APP_TITLE = "AIM-OS BTSM API"


def _default_db_path() -> Path:
    return Path(os.environ.get("CMC_DB_PATH", "packages/cmc_service/data/cmc.db"))


def _repository_dependency() -> Iterator[AtomRepository]:
    config = SQLiteConfig(path=_default_db_path())
    repo = AtomRepository(config)
    try:
        yield repo
    finally:
        repo.close()


app = FastAPI(title=APP_TITLE, version="0.1.0")


def _derive_edges(nodes: Iterable[MPDNode]) -> List[BitemporalEdge]:
    seen: Set[Tuple[str, str, str]] = set()
    edges: List[BitemporalEdge] = []
    for node in nodes:
        base_tt_start = node.tt_start if isinstance(node.tt_start, datetime) else datetime.now(timezone.utc)
        base_vt_start = node.vt_start if isinstance(node.vt_start, datetime) else base_tt_start
        base_tt_end = node.tt_end if isinstance(node.tt_end, datetime) else None
        base_vt_end = node.vt_end if isinstance(node.vt_end, datetime) else None
        for target_id in node.manager_of:
            key = (node.mpd_id, target_id, "manager_of")
            if key in seen:
                continue
            seen.add(key)
            edges.append(
                BitemporalEdge(
                    source_id=node.mpd_id,
                    target_id=target_id,
                    relation="manager_of",
                    policy_pack_ids=list(node.policy_pack_ids),
                    tt_start=base_tt_start,
                    tt_end=base_tt_end,
                    vt_start=base_vt_start,
                    vt_end=base_vt_end,
                )
            )
        for target_id in node.depends_on:
            key = (node.mpd_id, target_id, "depends_on")
            if key in seen:
                continue
            seen.add(key)
            edges.append(
                BitemporalEdge(
                    source_id=node.mpd_id,
                    target_id=target_id,
                    relation="depends_on",
                    policy_pack_ids=list(node.policy_pack_ids),
                    tt_start=base_tt_start,
                    tt_end=base_tt_end,
                    vt_start=base_vt_start,
                    vt_end=base_vt_end,
                )
            )
    return edges


@app.get("/mpd/nodes", response_model=List[MPDNode])
def list_mpd_nodes(
    policy_pack_ids: Optional[List[str]] = Query(
        None,
        description="Filter nodes by policy pack IDs (combined with policy_match).",
    ),
    policy_match: Literal["all", "any"] = Query(
        "all",
        description="Policy filter match mode: 'all' requires every value, 'any' matches partial overlap.",
    ),
    lifecycle: Optional[List[str]] = Query(
        None,
        description="Filter nodes by lifecycle state (exact match).",
    ),
    repo: AtomRepository = Depends(_repository_dependency),
) -> List[MPDNode]:
    return repo.fetch_mpd_nodes(
        policy_pack_ids=policy_pack_ids,
        policy_match=policy_match,
        lifecycle=lifecycle,
    )


@app.post("/mpd/nodes")
def upsert_mpd_nodes(nodes: List[MPDNode], repo: AtomRepository = Depends(_repository_dependency)) -> dict:
    if not nodes:
        raise HTTPException(status_code=400, detail="Request body must contain at least one MPD node.")
    repo.upsert_mpd_nodes(nodes)
    return {"status": "ok", "count": len(nodes)}


@app.post("/mpd/seed/trunk")
def seed_trunk(
    *,
    vision_summary: str,
    correlation_id: str | None = None,
    owners: List[str] | None = None,
    repo: AtomRepository = Depends(_repository_dependency),
) -> dict:
    vision_tensor = {
        "summary": vision_summary,
        "correlation_id": correlation_id,
    }
    nodes = draft_trunk_nodes(vision_tensor, owners=owners)
    repo.upsert_mpd_nodes(nodes)
    edges = _derive_edges(nodes)
    if edges:
        repo.upsert_mpd_edges(edges)
    return {
        "status": "ok",
        "count": len(nodes),
        "mpd_ids": [node.mpd_id for node in nodes],
        "edge_count": len(edges),
    }


@app.get("/mpd/edges", response_model=List[BitemporalEdge])
def list_mpd_edges(
    relation: Optional[str] = Query(None, description="Filter edges by relation type."),
    source_id: Optional[str] = Query(None, description="Filter edges by source node ID."),
    target_id: Optional[str] = Query(None, description="Filter edges by target node ID."),
    policy_pack_ids: Optional[List[str]] = Query(
        None,
        description="Filter edges by policy pack IDs (combined with policy_match).",
    ),
    policy_match: Literal["all", "any"] = Query(
        "all",
        description="Policy filter match mode: 'all' requires every value, 'any' matches partial overlap.",
    ),
    repo: AtomRepository = Depends(_repository_dependency),
) -> List[BitemporalEdge]:
    return repo.fetch_mpd_edges(
        relation=relation,
        source_id=source_id,
        target_id=target_id,
        policy_pack_ids=policy_pack_ids,
        policy_match=policy_match,
    )


@app.post("/mpd/edges")
def upsert_mpd_edges(edges: List[BitemporalEdge], repo: AtomRepository = Depends(_repository_dependency)) -> dict:
    if not edges:
        raise HTTPException(status_code=400, detail="Request body must contain at least one edge.")
    try:
        repo.upsert_mpd_edges(edges)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ok", "count": len(edges)}


class DependsOnRequest(BaseModel):
    source_id: str
    targets: List[str]
    policy_pack_ids: List[str] = []
    tt_start: Optional[datetime] = None
    vt_start: Optional[datetime] = None


class BlastRadiusRequest(BaseModel):
    root_ids: List[str]
    required_policy_pack_ids: List[str] = []
    relation_types: List[str] = ["depends_on"]


def _parse_iso8601(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid ISO timestamp: {value}") from exc


class EdgeSummary(BaseModel):
    source_id: str
    target_id: str
    relation: str
    policy_pack_ids: List[str]


class BlastRadiusViolation(BaseModel):
    kind: str
    subject_id: str
    message: str
    policy_pack_ids: List[str] = []


class BlastRadiusResponse(BaseModel):
    root_ids: List[str]
    required_policy_pack_ids: List[str]
    impacted_nodes: List[str]
    traversed_edges: List[EdgeSummary]
    violations: List[BlastRadiusViolation]
    compliant: bool


class KPIHistoryPoint(BaseModel):
    timestamp: datetime
    value: Any


class KPIHistoryRecord(BaseModel):
    metric: str
    history: List[KPIHistoryPoint]


@app.post("/mpd/edges/depends-on")
def add_depends_on_edges(payload: DependsOnRequest, repo: AtomRepository = Depends(_repository_dependency)) -> dict:
    now = datetime.now(timezone.utc)
    tt_start = payload.tt_start or now
    vt_start = payload.vt_start or tt_start
    edges: List[BitemporalEdge] = []
    for target_id in payload.targets:
        edges.append(
            BitemporalEdge(
                source_id=payload.source_id,
                target_id=target_id,
                relation="depends_on",
                policy_pack_ids=list(payload.policy_pack_ids),
                tt_start=tt_start,
                vt_start=vt_start,
                tt_end=None,
                vt_end=None,
            )
        )
    try:
        repo.upsert_mpd_edges(edges)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ok", "count": len(edges)}


@app.post("/mpd/blast-radius", response_model=BlastRadiusResponse)
def compute_blast_radius(
    payload: BlastRadiusRequest,
    repo: AtomRepository = Depends(_repository_dependency),
) -> BlastRadiusResponse:
    if not payload.root_ids:
        raise HTTPException(status_code=400, detail="At least one root_id is required to compute blast radius.")

    result = repo.calculate_blast_radius(
        payload.root_ids,
        relation_types=payload.relation_types,
        required_policy_pack_ids=payload.required_policy_pack_ids,
    )

    traversed = [EdgeSummary(**edge) for edge in result["traversed_edges"]]
    traversed.sort(key=lambda item: (item.source_id, item.target_id, item.relation))
    violations = [BlastRadiusViolation(**violation) for violation in result["violations"]]

    return BlastRadiusResponse(
        root_ids=result["root_ids"],
        required_policy_pack_ids=result["required_policy_pack_ids"],
        impacted_nodes=result["impacted_nodes"],
        traversed_edges=traversed,
        violations=violations,
        compliant=bool(result["compliant"]),
    )


@app.get("/health")
def healthcheck() -> dict:
    db_path = _default_db_path()
    return {"status": "ok", "db_path": str(db_path.resolve())}


@app.get("/kpis")
def list_kpis() -> dict:
    kpi_path = Path("goals/KPI_METRICS.json")
    if not kpi_path.exists():
        raise HTTPException(status_code=404, detail="KPI metrics file not found.")
    with kpi_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data


@app.get("/kpi/history", response_model=List[KPIHistoryRecord])
def list_kpi_history(
    metrics: Optional[List[str]] = Query(
        None,
        description="Filter to specific metric keys (can be provided multiple times).",
    ),
    start_time: Optional[str] = Query(
        None,
        description="ISO8601 timestamp inclusive lower bound.",
    ),
    end_time: Optional[str] = Query(
        None,
        description="ISO8601 timestamp inclusive upper bound.",
    ),
) -> List[KPIHistoryRecord]:
    kpi_path = Path("goals/KPI_METRICS.json")
    if not kpi_path.exists():
        raise HTTPException(status_code=404, detail="KPI metrics file not found.")

    with kpi_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    history = payload.get("history") or {}
    if not isinstance(history, dict):
        return []

    metrics_filter = {item for item in (metrics or []) if item}
    start_dt = _parse_iso8601(start_time) if start_time else None
    end_dt = _parse_iso8601(end_time) if end_time else None
    if start_dt and end_dt and start_dt > end_dt:
        raise HTTPException(status_code=400, detail="start_time must be before end_time")

    response: List[KPIHistoryRecord] = []
    for metric_key, entries in history.items():
        if metrics_filter and metric_key not in metrics_filter:
            continue
        if not isinstance(entries, list):
            continue
        points: List[KPIHistoryPoint] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            timestamp_str = entry.get("timestamp")
            if not isinstance(timestamp_str, str):
                continue
            try:
                timestamp = _parse_iso8601(timestamp_str)
            except HTTPException:
                continue
            if start_dt and timestamp < start_dt:
                continue
            if end_dt and timestamp > end_dt:
                continue
            points.append(KPIHistoryPoint(timestamp=timestamp, value=entry.get("value")))
        if points:
            points.sort(key=lambda item: item.timestamp)
            response.append(KPIHistoryRecord(metric=metric_key, history=points))

    response.sort(key=lambda item: item.metric)
    return response


def create_app() -> FastAPI:
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("packages.cmc_service.api:app", host="0.0.0.0", port=8000, reload=False)

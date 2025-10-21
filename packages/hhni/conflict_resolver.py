"""Conflict detection and resolution utilities for HHNI context selection."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .budget_manager import BudgetItem


@dataclass
class ConflictRecord:
    """Details of a resolved conflict cluster."""

    topic: str
    stances: Dict[str, List[str]]
    winning_stance: str
    representative_id: str
    suppressed_ids: List[str]
    rationale: str


@dataclass
class ConflictMetrics:
    """Summary metrics for conflict detection."""

    total_candidates: int
    conflicts_detected: int
    suppressed_items: int
    notes: List[str] = field(default_factory=list)


STANCE_POSITIVE = {"positive", "supports", "pro", "affirmative", "for"}
STANCE_NEGATIVE = {"negative", "contra", "against", "refutes", "con"}


def detect_conflicts(
    items: Sequence[BudgetItem],
    *,
    recency_bias: float = 0.2,
    authority_bias: float = 0.3,
    audit: Optional[List[ConflictRecord]] = None,
) -> Tuple[List[BudgetItem], ConflictMetrics]:
    """
    Detect contradictory items (same topic, opposing stance) and retain the most trustworthy representative.
    """

    if not items:
        metrics = ConflictMetrics(0, 0, 0)
        return [], metrics

    clusters: Dict[str, Dict[str, List[BudgetItem]]] = {}

    for item in items:
        topic = _extract_topic(item)
        if not topic:
            continue
        stance = _normalise_stance(item)
        if not stance:
            continue
        clusters.setdefault(topic, {}).setdefault(stance, []).append(item)

    resolved_items: List[BudgetItem] = []
    conflict_records: List[ConflictRecord] = []
    suppressed_ids: set[str] = set()
    kept_by_topic: Dict[str, BudgetItem] = {}

    for topic, stance_map in clusters.items():
        if len(stance_map) <= 1:
            continue
        best_item, winning_stance, suppressed_list, rationale = _resolve_cluster(
            topic,
            stance_map,
            recency_bias=recency_bias,
            authority_bias=authority_bias,
        )
        kept_by_topic[topic] = best_item
        cluster_suppressed = set(suppressed_list)
        for stance, members in stance_map.items():
            for member in members:
                if member.source_id != best_item.source_id:
                    cluster_suppressed.add(member.source_id)
        suppressed_ids.update(cluster_suppressed)
        conflict_records.append(
            ConflictRecord(
                topic=topic,
                stances={stance: [member.source_id for member in members] for stance, members in stance_map.items()},
                winning_stance=winning_stance,
                representative_id=best_item.source_id,
                suppressed_ids=sorted(cluster_suppressed),
                rationale=rationale,
            )
        )

    kept_ids: set[str] = set()
    for item in items:
        topic = _extract_topic(item)
        stance = _normalise_stance(item)
        if topic and stance and topic in kept_by_topic:
            if item.source_id == kept_by_topic[topic].source_id and item.source_id not in kept_ids:
                resolved_items.append(item)
                kept_ids.add(item.source_id)
        else:
            if item.source_id not in suppressed_ids and item.source_id not in kept_ids:
                resolved_items.append(item)
                kept_ids.add(item.source_id)

    metrics = ConflictMetrics(
        total_candidates=len(items),
        conflicts_detected=len(conflict_records),
        suppressed_items=len(suppressed_ids),
    )

    if audit is not None:
        audit.extend(conflict_records)

    return resolved_items, metrics


# --------------------------------------------------------------------------- #
# Helpers


def _extract_topic(item: BudgetItem) -> Optional[str]:
    metadata = item.metadata
    for key in ("topic", "claim_id", "entity", "subject"):
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return None


def _normalise_stance(item: BudgetItem) -> Optional[str]:
    metadata = item.metadata
    for key in ("stance", "polarity", "label"):
        value = metadata.get(key)
        if isinstance(value, str):
            normalised = value.strip().lower()
            if normalised in STANCE_POSITIVE:
                return "positive"
            if normalised in STANCE_NEGATIVE:
                return "negative"
    return None


def _authority_score(item: BudgetItem) -> float:
    metadata = item.metadata
    for key in ("confidence", "authority", "evidence"):
        value = metadata.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return 0.0


def _extract_timestamp(item: BudgetItem) -> Optional[datetime]:
    metadata = item.metadata
    ts = metadata.get("timestamp") or metadata.get("created_at") or metadata.get("updated_at")
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(float(ts))
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            pass
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(ts, fmt)
            except ValueError:
                continue
    return None


def _select_best_item(
    candidates: Iterable[BudgetItem],
    *,
    recency_bias: float,
    authority_bias: float,
) -> Tuple[BudgetItem, float]:
    items = list(candidates)
    if len(items) == 1:
        return items[0], 1.0

    timestamps = [_extract_timestamp(item) for item in items]
    valid_ts = [ts.timestamp() for ts in timestamps if ts is not None]
    recency_scores: Dict[str, float] = {}
    if valid_ts:
        minimum = min(valid_ts)
        maximum = max(valid_ts)
        for item, ts in zip(items, timestamps):
            if ts is None:
                recency_scores[item.source_id] = 0.0
            elif maximum == minimum:
                recency_scores[item.source_id] = 0.5
            else:
                recency_scores[item.source_id] = (ts.timestamp() - minimum) / (maximum - minimum)
    else:
        for item in items:
            recency_scores[item.source_id] = 0.0

    authority_scores = {_authority_score(item) for item in items}
    authority_map: Dict[str, float] = {}
    if any(authority_scores):
        values = [float(_authority_score(item)) for item in items]
        min_val = min(values)
        max_val = max(values)
        for item, value in zip(items, values):
            if max_val == min_val:
                authority_map[item.source_id] = 0.5
            else:
                authority_map[item.source_id] = (value - min_val) / (max_val - min_val)
    else:
        for item in items:
            authority_map[item.source_id] = 0.0

    base_weight = max(0.0, 1.0 - recency_bias - authority_bias)
    composite_scores: Dict[str, float] = {}
    for item in items:
        composite_scores[item.source_id] = (
            base_weight * item.relevance_score
            + recency_bias * recency_scores[item.source_id]
            + authority_bias * authority_map[item.source_id]
        )

    best_id = max(composite_scores, key=composite_scores.get)
    best_item = next(item for item in items if item.source_id == best_id)
    return best_item, composite_scores[best_id]


def _resolve_cluster(
    topic: str,
    stance_map: Dict[str, List[BudgetItem]],
    *,
    recency_bias: float,
    authority_bias: float,
) -> Tuple[BudgetItem, str, List[str], str]:
    suppressed_ids: List[str] = []
    best_item: Optional[BudgetItem] = None
    best_score = -1.0
    winning_stance = ""

    for stance, members in stance_map.items():
        candidate, score = _select_best_item(members, recency_bias=recency_bias, authority_bias=authority_bias)
        if score > best_score:
            if best_item is not None:
                suppressed_ids.append(best_item.source_id)
            best_item = candidate
            winning_stance = stance
            best_score = score
        else:
            suppressed_ids.extend(member.source_id for member in members)

    rationale = (
        f"topic '{topic}' resolved in favour of {winning_stance} stance; kept {best_item.source_id} "
        f"with composite score {best_score:.4f}"
    )
    return best_item, winning_stance, suppressed_ids, rationale


__all__ = [
    "ConflictRecord",
    "ConflictMetrics",
    "detect_conflicts",
]

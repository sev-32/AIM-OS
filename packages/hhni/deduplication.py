"""Deduplication utilities for the HHNI retrieval pipeline."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .budget_manager import BudgetItem


@dataclass
class DeduplicationMetrics:
    """Summary of a deduplication run."""

    total_candidates: int
    duplicates_removed: int
    clusters_formed: int
    threshold_used: float
    notes: List[str] = field(default_factory=list)


def deduplicate_candidates(
    items: Sequence[BudgetItem],
    *,
    similarity_threshold: float = 0.88,
    recency_bias: float = 0.2,
    authority_bias: float = 0.2,
    max_cluster_size: int = 6,
    audit: Optional[List[Dict[str, object]]] = None,
) -> Tuple[List[BudgetItem], DeduplicationMetrics]:
    """
    Group near-duplicate candidates and retain the best representative.

    Args:
        items: Candidate budget items in relevance order.
        similarity_threshold: Minimum cosine/Jaccard similarity to consider duplicates.
        recency_bias: Weight [0,1] given to recency when ranking cluster representative.
        authority_bias: Weight [0,1] given to authority/confidence when ranking representative.
        max_cluster_size: Hard limit for duplicate cluster size (guards against pathologies).
        audit: Optional list populated with cluster details.
    """

    candidates: List[BudgetItem] = list(items)
    if not candidates:
        metrics = DeduplicationMetrics(0, 0, 0, similarity_threshold)
        return [], metrics

    clusters: List[Dict[str, object]] = []
    vector_cache: Dict[str, List[float]] = {}
    token_cache: Dict[str, set] = {}

    def get_vector(item: BudgetItem) -> Optional[List[float]]:
        vec = item.metadata.get("embedding")
        if isinstance(vec, list) and vec and all(isinstance(v, (int, float)) for v in vec):
            vector_cache[item.source_id] = [float(v) for v in vec]
            return vector_cache[item.source_id]
        return None

    def get_tokens(item: BudgetItem) -> set:
        cached = token_cache.get(item.source_id)
        if cached is not None:
            return cached
        text = item.content or item.metadata.get("summary") or ""
        tokens = {token for token in _basic_tokenise(text)}
        token_cache[item.source_id] = tokens
        return tokens

    def similarity(a: BudgetItem, b: BudgetItem) -> float:
        vec_a = vector_cache.get(a.source_id) or get_vector(a)
        vec_b = vector_cache.get(b.source_id) or get_vector(b)
        if vec_a and vec_b and len(vec_a) == len(vec_b):
            return _cosine_similarity(vec_a, vec_b)

        tokens_a = get_tokens(a)
        tokens_b = get_tokens(b)
        if not tokens_a or not tokens_b:
            return 0.0
        intersection = len(tokens_a & tokens_b)
        union = len(tokens_a | tokens_b)
        return intersection / union if union else 0.0

    for idx, item in enumerate(candidates):
        assigned = False
        best_cluster: Optional[Dict[str, object]] = None
        best_similarity = 0.0

        for cluster in clusters:
            if len(cluster["members"]) >= max_cluster_size:
                continue
            reference_item: BudgetItem = cluster["representative"]  # type: ignore
            sim = similarity(item, reference_item)
            if sim >= similarity_threshold and sim > best_similarity:
                best_cluster = cluster
                best_similarity = sim

        if best_cluster:
            best_cluster["members"].append(item)
            best_cluster["similarities"].append(best_similarity)
            assigned = True
        if not assigned:
            clusters.append(
                {
                    "id": len(clusters) + 1,
                    "representative": item,
                    "members": [item],
                    "similarities": [1.0],
                    "indices": [idx],
                }
            )

    representatives: List[Tuple[int, BudgetItem]] = []
    total_duplicates = 0

    for cluster in clusters:
        members: List[BudgetItem] = cluster["members"]  # type: ignore
        chosen = _select_representative(
            members,
            recency_bias=recency_bias,
            authority_bias=authority_bias,
        )
        cluster["representative"] = chosen
        representatives.append((min(cluster["indices"]), chosen))  # type: ignore
        duplicates_here = max(0, len(members) - 1)
        total_duplicates += duplicates_here

        if audit is not None and duplicates_here:
            audit.append(
                {
                    "cluster_id": cluster["id"],
                    "representative_id": chosen.source_id,
                    "merged_ids": [member.source_id for member in members if member.source_id != chosen.source_id],
                    "reason": (
                        f"kept {chosen.source_id} with composite score "
                        f"{_composite_score(chosen, members, recency_bias, authority_bias):.4f}"
                    ),
                }
            )

    representatives.sort(key=lambda pair: pair[0])
    deduped_items = [item for _, item in representatives]

    metrics = DeduplicationMetrics(
        total_candidates=len(candidates),
        duplicates_removed=total_duplicates,
        clusters_formed=len(clusters),
        threshold_used=similarity_threshold,
    )

    return deduped_items, metrics


# --------------------------------------------------------------------------- #
# Helpers


TOKEN_RE = re.compile(r"[a-z0-9]+")


def _basic_tokenise(text: str) -> Iterable[str]:
    return TOKEN_RE.findall(text.lower())


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _normalise(values: List[float]) -> List[float]:
    if not values:
        return []
    minimum = min(values)
    maximum = max(values)
    if maximum - minimum == 0:
        return [0.0 for _ in values]
    return [(value - minimum) / (maximum - minimum) for value in values]


def _extract_timestamp(item: BudgetItem) -> Optional[datetime]:
    ts = item.metadata.get("timestamp") or item.metadata.get("created_at") or item.metadata.get("updated_at")
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


def _authority_score(item: BudgetItem) -> float:
    metadata = item.metadata
    if isinstance(metadata.get("confidence"), (int, float)):
        return float(metadata["confidence"])
    if isinstance(metadata.get("authority"), (int, float)):
        return float(metadata["authority"])
    if isinstance(metadata.get("policy_score"), (int, float)):
        return float(metadata["policy_score"])
    return 0.0


def _composite_score(
    item: BudgetItem,
    cluster_members: List[BudgetItem],
    recency_bias: float,
    authority_bias: float,
) -> float:
    base_weight = max(0.0, 1.0 - recency_bias - authority_bias)

    relevance_component = item.relevance_score

    timestamps = [_extract_timestamp(member) for member in cluster_members]
    valid_ts = [ts.timestamp() for ts in timestamps if ts is not None]
    recency_component = 0.0
    if valid_ts:
        timestamp_values = []
        for ts in timestamps:
            timestamp_values.append(ts.timestamp() if ts else min(valid_ts))
        recency_scores = _normalise(timestamp_values)
        recency_component = recency_scores[cluster_members.index(item)]

    authority_values = [_authority_score(member) for member in cluster_members]
    authority_scores = _normalise(authority_values) if any(authority_values) else [0.0] * len(cluster_members)
    authority_component = authority_scores[cluster_members.index(item)]

    return (
        base_weight * relevance_component
        + recency_bias * recency_component
        + authority_bias * authority_component
    )


def _select_representative(
    members: List[BudgetItem],
    *,
    recency_bias: float,
    authority_bias: float,
) -> BudgetItem:
    if len(members) == 1:
        return members[0]

    scored = [
        (
            _composite_score(member, members, recency_bias, authority_bias),
            member,
        )
        for member in members
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[0][1]


__all__ = ["DeduplicationMetrics", "deduplicate_candidates"]

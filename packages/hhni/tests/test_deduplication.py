"""Tests for HHNI deduplication helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hhni.budget_manager import BudgetItem
from hhni.deduplication import DeduplicationMetrics, deduplicate_candidates


def make_item(
    id_suffix: str,
    content: str,
    *,
    relevance: float,
    timestamp: datetime | None = None,
    confidence: float | None = None,
    embedding: list[float] | None = None,
) -> BudgetItem:
    metadata = {}
    if timestamp:
        metadata["timestamp"] = timestamp.isoformat()
    if confidence is not None:
        metadata["confidence"] = confidence
    if embedding:
        metadata["embedding"] = embedding
    return BudgetItem(
        content=content,
        relevance_score=relevance,
        token_count=len(content.split()),
        source_id=f"item-{id_suffix}",
        level="PARAGRAPH",
        metadata=metadata,
    )


def test_deduplicate_removes_near_duplicates():
    base_time = datetime.now(timezone.utc)
    items = [
        make_item("a", "AI builds trillion dollar system", relevance=0.9, timestamp=base_time),
        make_item("b", "AI builds trillion-dollar system!", relevance=0.85, timestamp=base_time - timedelta(minutes=5)),
        make_item("c", "Completely different content about governance", relevance=0.7, timestamp=base_time),
    ]

    audit: list[dict] = []
    deduped, metrics = deduplicate_candidates(items, audit=audit)

    assert len(deduped) == 2
    assert deduped[0].source_id == "item-a"
    assert metrics.duplicates_removed == 1
    assert audit and audit[0]["representative_id"] == "item-a"


def test_recency_bias_breaks_ties():
    base_time = datetime.now(timezone.utc)
    older = make_item("old", "Important insight about HHNI", relevance=0.8, timestamp=base_time - timedelta(days=2))
    newer = make_item("new", "Important insight about HHNI", relevance=0.8, timestamp=base_time)

    deduped, _ = deduplicate_candidates(
        [older, newer],
        similarity_threshold=0.7,
        recency_bias=0.4,
        authority_bias=0.0,
    )

    assert len(deduped) == 1
    assert deduped[0].source_id == "item-new"


def test_authority_bias_prefers_high_confidence():
    base_time = datetime.now(timezone.utc)
    low_conf = make_item(
        "low",
        "DVNS physics implementation details",
        relevance=0.8,
        timestamp=base_time,
        confidence=0.3,
        embedding=[0.1, 0.2, 0.3],
    )
    high_conf = make_item(
        "high",
        "DVNS physics implementation details",
        relevance=0.8,
        timestamp=base_time - timedelta(hours=1),
        confidence=0.95,
        embedding=[0.1, 0.2, 0.31],
    )

    deduped, _ = deduplicate_candidates(
        [low_conf, high_conf],
        similarity_threshold=0.95,
        recency_bias=0.1,
        authority_bias=0.5,
    )

    assert len(deduped) == 1
    assert deduped[0].source_id == "item-high"


def test_audit_logs_clusters():
    base_time = datetime.now(timezone.utc)
    alpha = make_item("alpha", "Budget manager audit trails", relevance=0.6, timestamp=base_time)
    beta = make_item("beta", "Budget manager audit trails", relevance=0.55, timestamp=base_time)

    audit: list[dict] = []
    deduplicate_candidates([alpha, beta], audit=audit)

    assert audit
    entry = audit[0]
    assert entry["representative_id"] == "item-alpha"
    assert "item-beta" in entry["merged_ids"]


def test_metrics_report_counts():
    base_time = datetime.now(timezone.utc)
    items = [
        make_item("a", "Node export pipeline", relevance=0.9, timestamp=base_time),
        make_item("b", "Graph export pipeline", relevance=0.7, timestamp=base_time - timedelta(hours=1)),
    ]

    _, metrics = deduplicate_candidates(items, similarity_threshold=0.5)

    assert isinstance(metrics, DeduplicationMetrics)
    assert metrics.total_candidates == 2
    assert metrics.threshold_used == 0.5


def test_no_duplicates_returns_identical_list():
    base_time = datetime.now(timezone.utc)
    items = [
        make_item("a", "Unique entry one", relevance=0.6, timestamp=base_time),
        make_item("b", "Different unique entry", relevance=0.5, timestamp=base_time - timedelta(minutes=10)),
    ]

    deduped, metrics = deduplicate_candidates(items, similarity_threshold=0.9)

    assert len(deduped) == len(items)
    assert metrics.duplicates_removed == 0

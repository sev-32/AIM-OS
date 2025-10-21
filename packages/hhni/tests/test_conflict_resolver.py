"""Tests for HHNI conflict detection and resolution."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hhni.budget_manager import BudgetItem
from hhni.conflict_resolver import ConflictMetrics, ConflictRecord, detect_conflicts


def make_item(
    suffix: str,
    content: str,
    *,
    relevance: float,
    topic: str,
    stance: str,
    confidence: float,
    timestamp: datetime,
) -> BudgetItem:
    return BudgetItem(
        content=content,
        relevance_score=relevance,
        token_count=len(content.split()),
        source_id=f"item-{suffix}",
        level="PARAGRAPH",
        metadata={
            "topic": topic,
            "stance": stance,
            "confidence": confidence,
            "timestamp": timestamp.isoformat(),
        },
    )


def test_conflict_detects_opposing_stances():
    base_time = datetime.now(timezone.utc)
    positive = make_item(
        "pro",
        "HHNI improves recall performance",
        relevance=0.9,
        topic="hhni performance",
        stance="supports",
        confidence=0.8,
        timestamp=base_time,
    )
    negative = make_item(
        "contra",
        "HHNI harms recall performance",
        relevance=0.8,
        topic="hhni performance",
        stance="refutes",
        confidence=0.4,
        timestamp=base_time - timedelta(hours=1),
    )
    neutral = make_item(
        "neutral",
        "CMC policy enforcement update",
        relevance=0.7,
        topic="policy update",
        stance="supports",
        confidence=0.6,
        timestamp=base_time,
    )

    audit: list[ConflictRecord] = []
    resolved, metrics = detect_conflicts([positive, negative, neutral], audit=audit)

    assert len(resolved) == 2
    kept_ids = {item.source_id for item in resolved}
    assert "item-pro" in kept_ids
    assert "item-neutral" in kept_ids
    assert "item-contra" not in kept_ids
    assert metrics.conflicts_detected == 1
    assert audit and audit[0].representative_id == "item-pro"


def test_recency_breaks_ties():
    base_time = datetime.now(timezone.utc)
    older = make_item(
        "old",
        "Beta feature is unstable",
        relevance=0.75,
        topic="feature stability",
        stance="refutes",
        confidence=0.6,
        timestamp=base_time - timedelta(days=2),
    )
    newer = make_item(
        "new",
        "Beta feature is stable",
        relevance=0.75,
        topic="feature stability",
        stance="supports",
        confidence=0.6,
        timestamp=base_time,
    )

    resolved, _ = detect_conflicts(
        [older, newer],
        recency_bias=0.4,
        authority_bias=0.1,
    )

    assert len(resolved) == 1
    assert resolved[0].source_id == "item-new"


def test_no_conflicts_returns_all_items():
    base_time = datetime.now(timezone.utc)
    items = [
        make_item(
            "alpha",
            "Observation about DVNS convergence",
            relevance=0.8,
            topic="dvns convergence",
            stance="supports",
            confidence=0.7,
            timestamp=base_time,
        ),
        make_item(
            "beta",
            "Observation about budget manager",
            relevance=0.75,
            topic="budget manager",
            stance="supports",
            confidence=0.6,
            timestamp=base_time,
        ),
    ]

    resolved, metrics = detect_conflicts(items)

    assert len(resolved) == len(items)
    assert metrics.conflicts_detected == 0
    assert metrics.suppressed_items == 0


def test_conflict_metrics_reflect_suppression():
    base_time = datetime.now(timezone.utc)
    positive = make_item(
        "pos",
        "System passes compliance checks",
        relevance=0.8,
        topic="compliance",
        stance="supports",
        confidence=0.6,
        timestamp=base_time,
    )
    negative = make_item(
        "neg",
        "System fails compliance checks",
        relevance=0.9,
        topic="compliance",
        stance="refutes",
        confidence=0.7,
        timestamp=base_time - timedelta(hours=3),
    )

    _, metrics = detect_conflicts([positive, negative])

    assert isinstance(metrics, ConflictMetrics)
    assert metrics.conflicts_detected == 1
    assert metrics.suppressed_items == 1

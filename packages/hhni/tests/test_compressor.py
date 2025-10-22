"""Tests for HHNI strategic compression."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hhni.budget_manager import BudgetItem
from hhni.compressor import (
    CompressionConfig,
    CompressionLevel,
    CompressionMetrics,
    compress_candidates,
)


def make_item(
    suffix: str,
    content: str,
    *,
    relevance: float,
    token_count: int,
    timestamp: datetime,
    priority: float = 0.5,
) -> BudgetItem:
    """Helper to create test budget items."""
    return BudgetItem(
        content=content,
        relevance_score=relevance,
        token_count=token_count,
        source_id=f"item-{suffix}",
        level="PARAGRAPH",
        metadata={
            "timestamp": timestamp.isoformat(),
            "priority": priority,
        },
    )


def test_recent_items_not_compressed():
    """Items less than 7 days old should keep full detail."""
    now = datetime.now(timezone.utc)
    recent = make_item(
        "recent",
        "This is recent content that should not be compressed at all.",
        relevance=0.8,
        token_count=20,
        timestamp=now - timedelta(days=3),
    )

    compressed, metrics = compress_candidates([recent])

    assert len(compressed) == 1
    assert compressed[0].content == recent.content
    assert compressed[0].token_count == recent.token_count
    assert metrics.compressed_count == 0
    assert metrics.tokens_saved == 0


def test_week_old_gets_detailed_compression():
    """Items 7-30 days old should get detailed summary (70% retention)."""
    now = datetime.now(timezone.utc)
    week_old = make_item(
        "week",
        "This is week old content. " * 20,  # Make it long enough to compress
        relevance=0.7,
        token_count=100,
        timestamp=now - timedelta(days=14),
    )

    config = CompressionConfig(preserve_key_sentences=False)
    compressed, metrics = compress_candidates([week_old], config=config)

    assert len(compressed) == 1
    assert compressed[0].token_count < week_old.token_count
    assert compressed[0].token_count >= int(100 * config.detailed_ratio * 0.8)  # Allow variance
    assert metrics.compressed_count == 1
    assert metrics.tokens_saved > 0


def test_month_old_gets_brief_compression():
    """Items 30-90 days old should get brief summary (40% retention)."""
    now = datetime.now(timezone.utc)
    month_old = make_item(
        "month",
        "This is month old content. " * 30,  # Make it long
        relevance=0.6,
        token_count=150,
        timestamp=now - timedelta(days=45),
    )

    config = CompressionConfig(preserve_key_sentences=False)
    compressed, metrics = compress_candidates([month_old], config=config)

    assert len(compressed) == 1
    assert compressed[0].token_count < month_old.token_count
    assert compressed[0].token_count <= int(150 * config.brief_ratio * 1.2)  # Allow variance
    assert metrics.compressed_count == 1


def test_old_items_get_reference_only():
    """Items > 90 days old should get reference only (15% retention)."""
    now = datetime.now(timezone.utc)
    old = make_item(
        "old",
        "This is very old content that was discussed many months ago. " * 20,
        relevance=0.5,
        token_count=200,
        timestamp=now - timedelta(days=120),
    )

    config = CompressionConfig(preserve_key_sentences=False)
    compressed, metrics = compress_candidates([old], config=config)

    assert len(compressed) == 1
    assert compressed[0].token_count < old.token_count
    assert compressed[0].token_count <= int(200 * config.reference_ratio * 1.5)  # Allow variance
    assert metrics.compressed_count == 1


def test_high_priority_gets_preferential_treatment():
    """High priority items should get less aggressive compression."""
    now = datetime.now(timezone.utc)

    # Use 60 days (clearly in BRIEF range for normal, but DETAILED for high priority)
    normal_priority = make_item(
        "normal",
        "Normal priority content. " * 30,
        relevance=0.7,
        token_count=150,
        timestamp=now - timedelta(days=60),
        priority=0.5,
    )

    high_priority = make_item(
        "high",
        "High priority content. " * 30,
        relevance=0.7,
        token_count=150,
        timestamp=now - timedelta(days=60),
        priority=0.9,  # >= 0.85, gets preferential treatment
    )

    compressed, _ = compress_candidates([normal_priority, high_priority])

    # High priority should have more tokens retained
    normal_tokens = next(item for item in compressed if item.source_id == "item-normal").token_count
    high_tokens = next(item for item in compressed if item.source_id == "item-high").token_count

    # High priority should be compressed less aggressively
    assert high_tokens > normal_tokens, f"Expected high ({high_tokens}) > normal ({normal_tokens})"


def test_preserve_key_sentences_mode():
    """When preserve_key_sentences is True, should keep first and last sentences."""
    now = datetime.now(timezone.utc)
    item = make_item(
        "test",
        "First sentence is important. Middle sentence has detail. Last sentence summarizes.",
        relevance=0.7,
        token_count=50,
        timestamp=now - timedelta(days=45),  # BRIEF compression
    )

    config = CompressionConfig(preserve_key_sentences=True)
    compressed, _ = compress_candidates([item], config=config)

    assert len(compressed) == 1
    content = compressed[0].content
    # Should contain first and last sentences
    assert "First sentence" in content
    assert "summarizes" in content


def test_compression_metrics_accurate():
    """Compression metrics should accurately reflect operations."""
    now = datetime.now(timezone.utc)
    items = [
        make_item("recent", "Recent" * 10, relevance=0.8, token_count=20, timestamp=now - timedelta(days=2)),
        make_item("week", "Week" * 50, relevance=0.7, token_count=100, timestamp=now - timedelta(days=14)),
        make_item("month", "Month" * 75, relevance=0.6, token_count=150, timestamp=now - timedelta(days=45)),
    ]

    compressed, metrics = compress_candidates(items)

    assert metrics.total_candidates == 3
    assert metrics.compressed_count >= 1  # At least week and month should compress
    assert metrics.tokens_saved > 0
    assert 0 < metrics.compression_ratio < 1  # Some compression happened
    assert "FULL" in metrics.levels_applied
    assert metrics.levels_applied["FULL"] >= 1  # Recent item


def test_mixed_age_compression():
    """Test compression on mixed-age items."""
    now = datetime.now(timezone.utc)
    items = [
        make_item("recent1", "Recent A" * 10, relevance=0.9, token_count=30, timestamp=now - timedelta(days=1)),
        make_item("recent2", "Recent B" * 10, relevance=0.85, token_count=30, timestamp=now - timedelta(days=5)),
        make_item("week1", "Week A" * 40, relevance=0.75, token_count=100, timestamp=now - timedelta(days=10)),
        make_item("week2", "Week B" * 40, relevance=0.7, token_count=100, timestamp=now - timedelta(days=20)),
        make_item("month1", "Month A" * 60, relevance=0.65, token_count=150, timestamp=now - timedelta(days=60)),
        make_item("old1", "Old A" * 80, relevance=0.6, token_count=200, timestamp=now - timedelta(days=120)),
    ]

    compressed, metrics = compress_candidates(items)

    assert len(compressed) == len(items)
    assert metrics.total_candidates == 6

    # Check that compression was applied appropriately
    recent_items = [item for item in compressed if item.source_id in ["item-recent1", "item-recent2"]]
    week_items = [item for item in compressed if item.source_id in ["item-week1", "item-week2"]]
    old_items = [item for item in compressed if item.source_id in ["item-month1", "item-old1"]]

    # Recent should have original token count
    for item in recent_items:
        assert item.token_count == 30

    # Week and old should be compressed
    for item in week_items + old_items:
        assert item.token_count < item.metadata.get("original_tokens", float("inf"))


def test_audit_trail_populated():
    """Audit trail should contain compression details."""
    now = datetime.now(timezone.utc)
    items = [
        make_item("test1", "Test" * 50, relevance=0.8, token_count=100, timestamp=now - timedelta(days=30)),
        make_item("test2", "Test" * 50, relevance=0.7, token_count=100, timestamp=now - timedelta(days=60)),
    ]

    audit: List[Dict] = []
    compressed, _ = compress_candidates(items, audit=audit)

    assert len(audit) == 2
    for record in audit:
        assert "source_id" in record
        assert "age_days" in record
        assert "priority" in record
        assert "compression_level" in record
        assert "original_tokens" in record
        assert "compressed_tokens" in record
        assert "tokens_saved" in record


def test_empty_list_returns_empty():
    """Empty input should return empty output with zero metrics."""
    compressed, metrics = compress_candidates([])

    assert len(compressed) == 0
    assert metrics.total_candidates == 0
    assert metrics.compressed_count == 0
    assert metrics.tokens_saved == 0
    assert metrics.compression_ratio == 1.0


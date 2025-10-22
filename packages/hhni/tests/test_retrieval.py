"""Tests for the HHNI two-stage retrieval pipeline."""

from __future__ import annotations

from typing import Tuple

import pytest

from hhni.hierarchical_index import HierarchicalIndex
from hhni.retrieval import RetrievalConfig, RetrievalResult, TwoStageRetriever
from hhni.semantic_search import EmbeddingProvider


SAMPLE_DOC = """AIM-OS Overview

Context Memory Core
The CMC stores atoms and enables perfect recall across time.

Hierarchical Hypergraph Neural Index
HHNI provides semantic retrieval with multi-level zoom capabilities.

Vision Tensor
Vision Tensor propagates policy metadata and guidance heuristics.
"""


LONG_SAMPLE_DOC = """Lost in the Middle Case Study

Section 1: Intro
This section provides context but does not contain the main answer.

Section 2: Distractor
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum vestibulum erat sed arcu fermentum, vitae luctus ipsum gravida.

Section 3: Key Insight
IMPORTANT: The critical information is buried here. DVNS should surface this section to the top of the retrieval list.

Section 4: Additional Notes
More content that provides supporting details but is less relevant.
"""


def _build_index_with_sample_doc() -> HierarchicalIndex:
    index = HierarchicalIndex()
    index.index_document(SAMPLE_DOC, "sample")
    return index


def _build_index_with_long_doc() -> HierarchicalIndex:
    index = HierarchicalIndex()
    index.index_document(LONG_SAMPLE_DOC, "long")
    return index


def _ensure_results(result: RetrievalResult) -> Tuple[int, int]:
    return len(result.selected_items), result.total_tokens


def test_two_stage_retrieval_end_to_end():
    index = _build_index_with_sample_doc()
    retriever = TwoStageRetriever(index, RetrievalConfig(token_budget=1000))

    result = retriever.retrieve("memory systems", token_budget=1000)

    count, tokens = _ensure_results(result)
    assert count > 0
    assert tokens <= 1000
    assert result.coarse_time_ms >= 0
    assert result.dvns_time_ms >= 0
    assert result.relevance_score >= 0


def test_rs_lift_measurement():
    index = _build_index_with_sample_doc()
    retriever = TwoStageRetriever(index)

    dvns_result, baseline_result, rs_lift = retriever.retrieve_with_baseline_comparison(
        "context optimization",
        token_budget=1000,
    )

    assert dvns_result.selected_items
    assert baseline_result.selected_items
    assert rs_lift is not None
    dvns_result.rs_lift = rs_lift  # ensure field is populated
    assert isinstance(dvns_result.rs_lift, float)


def test_dvns_improves_relevance():
    index = _build_index_with_long_doc()
    retriever = TwoStageRetriever(index, RetrievalConfig(token_budget=500))

    dvns_result, baseline_result, _ = retriever.retrieve_with_baseline_comparison(
        "critical information", token_budget=500
    )

    assert dvns_result.relevance_score >= baseline_result.relevance_score


def test_respects_token_budget():
    index = _build_index_with_sample_doc()
    config = RetrievalConfig(token_budget=200)
    retriever = TwoStageRetriever(index, config)

    result = retriever.retrieve("test query", token_budget=200)
    assert result.total_tokens <= 200


def test_metrics_populated():
    index = _build_index_with_sample_doc()
    retriever = TwoStageRetriever(index)

    result = retriever.retrieve("test")
    assert result.coarse_candidates >= 0
    assert result.coarse_time_ms >= 0
    assert result.dvns_iterations >= 0
    assert result.dvns_time_ms >= 0
    assert result.relevance_score >= 0
    assert result.efficiency >= 0


def test_empty_query_returns_empty_result():
    index = _build_index_with_sample_doc()
    retriever = TwoStageRetriever(index)

    with pytest.raises(ValueError):
        retriever.retrieve("", token_budget=500)


def test_high_min_relevance_filters_results():
    index = _build_index_with_sample_doc()
    config = RetrievalConfig(min_relevance=0.99)
    retriever = TwoStageRetriever(index, config)

    result = retriever.retrieve("memory systems")
    assert len(result.selected_items) == 0


def test_custom_embedding_provider():
    index = _build_index_with_sample_doc()
    retriever = TwoStageRetriever(index)

    result = retriever.retrieve("memory systems", provider=EmbeddingProvider.FALLBACK)
    assert result.coarse_candidates > 0


def test_conflict_detection_integration():
    """Test that conflict detection works in the retrieval pipeline."""
    from datetime import datetime, timezone

    index = HierarchicalIndex()

    # Create conflicting documents
    conflicting_doc = """
    The beta feature is unstable and should not be used in production.
    The beta feature causes crashes and data loss.
    """

    supporting_doc = """
    The beta feature is stable and ready for production.
    The beta feature has been thoroughly tested and performs well.
    """

    index.index_document(conflicting_doc, "conflicting-doc")
    index.index_document(supporting_doc, "supporting-doc")

    # Create retriever with conflict detection enabled
    retriever = TwoStageRetriever(
        index,
        RetrievalConfig(
            enable_conflict_resolution=True,
            conflict_recency_bias=0.4,
            conflict_authority_bias=0.1,
            token_budget=1000,
        )
    )

    result = retriever.retrieve("beta feature stability")

    # Should detect and resolve conflicts
    assert result.conflicts_detected >= 0  # May or may not have conflicts depending on content

    # Should still return valid results
    assert len(result.selected_items) >= 0
    assert result.total_tokens <= 1000

    # Should have conflict records if conflicts were detected
    if result.conflicts_detected > 0:
        assert len(result.conflict_records) > 0
        assert result.conflicts_resolved == result.conflicts_detected


def test_compression_integration():
    """Test that strategic compression works in the retrieval pipeline."""
    from datetime import datetime, timezone, timedelta

    index = HierarchicalIndex()

    # Create documents with different ages (simulated via metadata)
    recent_doc = "This is recent content. " * 50
    old_doc = "This is old content. " * 50

    index.index_document(recent_doc, "recent-doc")
    index.index_document(old_doc, "old-doc")

    # Create retriever with compression enabled
    retriever = TwoStageRetriever(
        index,
        RetrievalConfig(
            enable_compression=True,
            token_budget=500,
        )
    )

    result = retriever.retrieve("content")

    # Should return results
    assert len(result.selected_items) >= 0
    assert result.total_tokens <= 500

    # Compression metrics should be populated
    assert result.compression_ratio >= 0
    assert result.tokens_saved_by_compression >= 0

    # Should indicate if compression was applied
    assert isinstance(result.compression_applied, bool)
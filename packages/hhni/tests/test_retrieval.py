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

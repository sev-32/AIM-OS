"""Tests for the HHNI semantic search engine."""

from __future__ import annotations

import pytest

from hhni.hierarchical_index import HierarchicalIndex, IndexLevel
from hhni.semantic_search import (
    EmbeddingProvider,
    SearchResult,
    SemanticSearchEngine,
)


SAMPLE_DOC = """AIM-OS Overview

Context Memory Core
The CMC stores atoms and enables perfect recall across time.

Hierarchical Hypergraph Neural Index
HHNI provides semantic retrieval with multi-level zoom capabilities.

Vision Tensor
Vision Tensor propagates policy metadata.
"""


def _build_index() -> HierarchicalIndex:
    index = HierarchicalIndex()
    index.index_document(SAMPLE_DOC, doc_id="aimos")
    return index


def test_search_returns_ranked_results():
    index = _build_index()
    engine = SemanticSearchEngine(index=index)

    results = engine.search("semantic retrieval", target_level=IndexLevel.PARAGRAPH, top_k=3)

    assert results
    assert all(isinstance(res, SearchResult) for res in results)
    assert all(res.node.level == IndexLevel.PARAGRAPH for res in results)
    # ensure scores are in descending order
    scores = [res.score for res in results]
    assert scores == sorted(scores, reverse=True)


def test_confidence_values_are_normalized():
    index = _build_index()
    engine = SemanticSearchEngine(index=index)

    results = engine.search("context memory", target_level=IndexLevel.PARAGRAPH, top_k=2)

    assert results
    assert all(0.0 <= res.confidence <= 1.0 for res in results)
    assert results[0].confidence >= results[-1].confidence


def test_filter_fn_limits_candidates():
    index = _build_index()
    engine = SemanticSearchEngine(index=index)

    # restrict search to sections mentioning HHNI
    results = engine.search(
        "semantic retrieval",
        target_level=IndexLevel.PARAGRAPH,
        filter_fn=lambda node: "HHNI" in node.content or "HHNI" in node.summary,
    )

    assert results
    assert all("HHNI" in res.node.content or "HHNI" in res.node.summary for res in results)


def test_empty_query_raises():
    engine = SemanticSearchEngine(index=_build_index())
    with pytest.raises(ValueError):
        engine.search("", target_level=IndexLevel.PARAGRAPH)


def test_fallback_provider_produces_results():
    index = _build_index()
    engine = SemanticSearchEngine(index=index, provider=EmbeddingProvider.FALLBACK)

    results = engine.search("policy metadata", target_level=IndexLevel.PARAGRAPH, top_k=1)

    assert results
    assert results[0].score > 0

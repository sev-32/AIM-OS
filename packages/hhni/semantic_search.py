"""Semantic search utilities for HHNI.

This module provides a lightweight search engine that operates on top of the
hierarchical index. It computes relevance scores using cosine similarity and
returns the most relevant nodes together with confidence estimates.

The implementation is provider-agnostic: it can use the local embedding model
(`packages.hhni.embeddings`) when available and falls back to a deterministic
feature embedding when external providers are unavailable. Additional providers
can be registered later by extending `_embed_text`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, List, Optional

try:  # pragma: no cover - optional heavy dependency
    from .embeddings import encode_text
except Exception:  # pragma: no cover - handled by fallback
    encode_text = None  # type: ignore

from .hierarchical_index import HierarchicalIndex, IndexLevel, IndexNode


class EmbeddingProvider(Enum):
    """Supported embedding providers."""

    LOCAL = "local"  # sentence-transformers (default)
    FALLBACK = "fallback"  # deterministic character statistics


@dataclass
class SearchResult:
    """Result returned by the semantic search engine."""

    node: IndexNode
    score: float
    confidence: float  # 0..1 relative confidence


class SemanticSearchEngine:
    """Performs semantic search over a hierarchical index."""

    def __init__(
        self,
        *,
        index: HierarchicalIndex,
        provider: EmbeddingProvider = EmbeddingProvider.LOCAL,
    ) -> None:
        self.index = index
        self.provider = provider

    def search(
        self,
        query: str,
        *,
        target_level: IndexLevel = IndexLevel.PARAGRAPH,
        top_k: int = 5,
        filter_fn: Optional[Callable[[IndexNode], bool]] = None,
    ) -> List[SearchResult]:
        """Return the top-k nodes matching the query at the requested level."""
        query = (query or "").strip()
        if not query:
            raise ValueError("query must be non-empty")
        if top_k <= 0:
            raise ValueError("top_k must be positive")

        query_vector = _embed_text(query, provider=self.provider)

        candidates: Iterable[IndexNode] = (
            node for node in self.index.nodes.values() if node.level == target_level
        )
        if filter_fn:
            candidates = (node for node in candidates if filter_fn(node))

        scored: List[SearchResult] = []
        for node in candidates:
            node_vector = node.embeddings or _fallback_embedding(node.summary or node.content)
            score = _cosine_similarity(query_vector, node_vector)
            if score <= 0:
                continue
            scored.append(SearchResult(node=node, score=score, confidence=0.0))

        if not scored:
            return []

        scored.sort(key=lambda result: result.score, reverse=True)
        top = scored[:top_k]
        max_score = top[0].score
        min_score = top[-1].score if len(top) > 1 else top[0].score
        score_range = max(max_score - min_score, 1e-6)
        for result in top:
            result.confidence = (result.score - min_score) / score_range
        return top


# ----------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------


def _embed_text(text: str, *, provider: EmbeddingProvider) -> List[float]:
    if provider == EmbeddingProvider.LOCAL and encode_text is not None:
        try:
            return [float(x) for x in encode_text(text)]
        except Exception:
            pass
    return _fallback_embedding(text)


def _fallback_embedding(text: str) -> List[float]:
    text = (text or "").strip()
    if not text:
        return [0.0, 0.0, 0.0]
    codes = [ord(ch) for ch in text[:128]]
    length = len(codes)
    total = float(sum(codes))
    average = total / length
    variance = sum((code - average) ** 2 for code in codes) / length
    return [total, average, variance]


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    if len(vec_a) != len(vec_b):
        # align lengths by truncation/padding with zeros
        min_len = min(len(vec_a), len(vec_b))
        vec_a = vec_a[:min_len]
        vec_b = vec_b[:min_len]
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


__all__ = [
    "SemanticSearchEngine",
    "EmbeddingProvider",
    "SearchResult",
]


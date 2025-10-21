"""Tests for the HHNI token budget manager."""

from __future__ import annotations

from typing import List

import pytest

from hhni.budget_manager import BudgetItem, BudgetStrategy, TokenBudgetManager
from hhni.hierarchical_index import HierarchicalIndex, IndexLevel
from hhni.semantic_search import SemanticSearchEngine


def create_mock_items(count: int, *, tokens_per_item: int = 10) -> List[BudgetItem]:
    """Create deterministic mock items with descending relevance scores."""
    items: List[BudgetItem] = []
    for idx in range(count):
        score = max(0.0, 1.0 - idx * 0.02)  # ensures strictly descending until zero
        items.append(
            BudgetItem(
                content=f"Item {idx}",
                relevance_score=score,
                token_count=tokens_per_item,
                source_id=f"item-{idx}",
                level="PARAGRAPH",
                metadata={"rank": idx},
            )
        )
    return items


def _build_index() -> HierarchicalIndex:
    sample_doc = """AIM-OS Overview

Context Memory Core
The CMC stores atoms and enables perfect recall across time.

Hierarchical Hypergraph Neural Index
HHNI provides semantic retrieval with multi-level zoom capabilities.

Vision Tensor
Vision Tensor propagates policy metadata.
"""
    index = HierarchicalIndex()
    index.index_document(sample_doc, doc_id="aimos")
    return index


def test_budget_manager_respects_limit():
    mgr = TokenBudgetManager()
    items = create_mock_items(20)  # 20 items * 10 tokens = 200 tokens

    allocation = mgr.optimize_for_budget(
        items,
        token_budget=100,  # Only room for 10 items
        strategy=BudgetStrategy.GREEDY,
    )

    assert allocation.total_tokens_used <= 100
    assert len(allocation.included) == 10
    assert len(allocation.excluded) == 10


def test_greedy_prioritizes_relevance():
    mgr = TokenBudgetManager()

    items = [
        BudgetItem("Low", 0.3, 10, "low", "PARAGRAPH", {}),
        BudgetItem("High", 0.9, 10, "high", "PARAGRAPH", {}),
        BudgetItem("Medium", 0.6, 10, "med", "PARAGRAPH", {}),
    ]

    allocation = mgr.optimize_for_budget(
        items,
        token_budget=20,  # Room for 2 items
        strategy=BudgetStrategy.GREEDY,
    )

    assert len(allocation.included) == 2
    included_ids = [item.source_id for item in allocation.included]
    assert "high" in included_ids
    assert "med" in included_ids
    assert "low" not in included_ids


def test_min_relevance_threshold():
    mgr = TokenBudgetManager()

    items = [
        BudgetItem("High", 0.9, 10, "high", "PARAGRAPH", {}),
        BudgetItem("Low", 0.2, 10, "low", "PARAGRAPH", {}),
    ]

    allocation = mgr.optimize_for_budget(
        items,
        token_budget=100,
        min_relevance=0.5,  # Filter out low relevance
    )

    assert len(allocation.included) == 1
    assert allocation.included[0].source_id == "high"
    assert allocation.audit_trail["candidates_filtered_below_threshold"] == 1


def test_audit_trail_completeness():
    mgr = TokenBudgetManager()
    items = create_mock_items(10)

    allocation = mgr.optimize_for_budget(items, token_budget=50)

    audit = allocation.audit_trail
    assert audit["strategy"] == BudgetStrategy.GREEDY.value
    assert "candidates_considered" in audit
    assert "included_count" in audit
    assert "excluded_count" in audit
    assert "tokens_used" in audit
    assert "budget_utilization" in audit
    assert audit["candidates_considered"] == 10


def test_token_counting():
    mgr = TokenBudgetManager()

    text = "This is a test sentence with several words."
    token_count = mgr.count_tokens(text)

    assert 5 < token_count < 15


def test_efficiency_calculation():
    mgr = TokenBudgetManager()

    items = [
        BudgetItem("A", 0.9, 10, "a", "PARAGRAPH", {}),
        BudgetItem("B", 0.8, 10, "b", "PARAGRAPH", {}),
    ]

    allocation = mgr.optimize_for_budget(items, token_budget=20)

    assert pytest.approx(allocation.efficiency, rel=1e-2) == (0.9 + 0.8) / 20.0


def test_integration_with_search_results():
    index = _build_index()
    engine = SemanticSearchEngine(index=index)
    results = engine.search(
        "semantic retrieval",
        target_level=IndexLevel.PARAGRAPH,
        top_k=3,
    )
    mgr = TokenBudgetManager()

    items = mgr.create_budget_items_from_search(results)

    assert items
    assert len(items) == len(results)
    assert all(item.token_count > 0 for item in items)
    assert all(item.level == IndexLevel.PARAGRAPH.name for item in items)
    assert all("confidence" in item.metadata for item in items)


def test_excluded_high_relevance_flagged():
    mgr = TokenBudgetManager()

    items = [
        BudgetItem("Include", 0.95, 10, "inc", "PARAGRAPH", {}),
        BudgetItem("Exclude but relevant", 0.85, 100, "exc", "PARAGRAPH", {}),
    ]

    allocation = mgr.optimize_for_budget(items, token_budget=15)

    audit = allocation.audit_trail
    assert "excluded_high_relevance" in audit
    assert len(audit["excluded_high_relevance"]) > 0

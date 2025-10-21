"""Token Budget Manager for Context Optimization.

This module ensures retrieved context fits within LLM token limits while
maximizing relevance. It integrates with HierarchicalIndex and SemanticSearch
to provide budget-aware context retrieval and emit audit trails that can be
consumed by downstream verification systems (VIF).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence, TYPE_CHECKING

try:  # pragma: no cover - optional dependency
    import tiktoken  # type: ignore
except ImportError:  # pragma: no cover - fallback path is exercised in tests
    tiktoken = None  # type: ignore

if TYPE_CHECKING:  # pragma: no cover - typing helpers only
    from .semantic_search import SearchResult


class BudgetStrategy(Enum):
    """Strategies supported by the budget manager."""

    GREEDY = "greedy"  # Take top-ranked until the budget is full
    BALANCED = "balanced"  # Ensure coverage across hierarchy levels/sources
    OPTIMAL = "optimal"  # Maximize relevance per token (future dynamic programming)


@dataclass
class BudgetItem:
    """Represents a single candidate for inclusion in the context window."""

    content: str
    relevance_score: float
    token_count: int
    source_id: str
    level: str  # Human-readable level (e.g., IndexLevel.PARAGRAPH.name)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BudgetAllocation:
    """Outcome of running the allocation algorithm."""

    included: List[BudgetItem]
    excluded: List[BudgetItem]
    total_tokens_used: int
    budget_limit: int
    efficiency: float  # Aggregate relevance per token
    audit_trail: Dict[str, Any] = field(default_factory=dict)


class TokenBudgetManager:
    """
    Manage context fitting within token budgets.

    Integrates with:
    - HierarchicalIndex (for multi-level content)
    - SemanticSearch (for relevance scores)
    - VIF (for audit witnesses)
    """

    def __init__(self, tokenizer: str = "cl100k_base", default_budget: int = 8000) -> None:
        self._tokenizer_name = tokenizer
        self.tokenizer = self._init_tokenizer(tokenizer)
        self.default_budget = default_budget

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def optimize_for_budget(
        self,
        candidates: List[BudgetItem],
        token_budget: int,
        strategy: BudgetStrategy = BudgetStrategy.GREEDY,
        min_relevance: float = 0.0,
    ) -> BudgetAllocation:
        """Fit candidates within the token budget using the selected strategy."""
        if token_budget <= 0:
            raise ValueError("token_budget must be a positive integer")

        initial_count = len(candidates)
        filtered_candidates = [
            candidate for candidate in candidates if candidate.relevance_score >= min_relevance
        ]

        if not filtered_candidates:
            audit = {
                "strategy_requested": strategy.value,
                "strategy": strategy.value,
                "candidates_considered": 0,
                "candidates_filtered_below_threshold": initial_count,
                "included_count": 0,
                "excluded_count": 0,
                "tokens_used": 0,
                "budget_limit": token_budget,
                "budget_utilization": 0.0,
                "min_relevance": min_relevance,
                "notes": ["No candidates met the minimum relevance threshold."],
            }
            return BudgetAllocation([], [], 0, token_budget, 0.0, audit)

        ordered = sorted(
            filtered_candidates,
            key=lambda candidate: (candidate.relevance_score, -candidate.token_count),
            reverse=True,
        )

        if strategy == BudgetStrategy.GREEDY:
            allocation = self._greedy_allocation(ordered, token_budget)
        elif strategy == BudgetStrategy.BALANCED:
            allocation = self._balanced_allocation(ordered, token_budget)
        elif strategy == BudgetStrategy.OPTIMAL:
            allocation = self._optimal_allocation(ordered, token_budget)
        else:  # pragma: no cover - defensive guard
            raise ValueError(f"Unknown strategy: {strategy}")

        allocation.audit_trail.update(
            {
                "strategy_requested": strategy.value,
                "min_relevance": min_relevance,
                "candidates_filtered_below_threshold": initial_count - len(filtered_candidates),
                "budget_limit": token_budget,
            }
        )
        return allocation

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken if available, otherwise a fallback heuristic."""
        if not text:
            return 0

        if self.tokenizer is not None:
            try:
                return len(self.tokenizer.encode(text, disallowed_special=()))
            except Exception:  # pragma: no cover - tokenizer failures fall back to heuristic
                pass

        return self._approximate_token_count(text)

    def create_budget_items_from_search(
        self,
        results: Iterable["SearchResult"],
        *,
        include_summary: bool = False,
        min_confidence: float = 0.0,
    ) -> List[BudgetItem]:
        """
        Convert search results into budget items with counted tokens.

        Args:
            results: Iterable of `SearchResult` objects.
            include_summary: Whether to prepend node summaries to content.
            min_confidence: Drop results whose confidence is below this threshold.
        """
        items: List[BudgetItem] = []
        for result in results:
            if result.confidence < min_confidence:
                continue

            node = result.node
            content_parts: List[str] = []
            if include_summary and node.summary:
                content_parts.append(node.summary.strip())
            if node.content:
                content_parts.append(node.content.strip())
            content = "\n\n".join(part for part in content_parts if part) or node.summary or ""

            token_count = max(self.count_tokens(content), 1)
            metadata = dict(node.metadata or {})
            metadata.update(
                {
                    "confidence": result.confidence,
                    "relevance_score": result.score,
                    "summary": node.summary,
                }
            )
            items.append(
                BudgetItem(
                    content=content,
                    relevance_score=result.score,
                    token_count=token_count,
                    source_id=node.id,
                    level=getattr(node.level, "name", str(node.level)),
                    metadata=metadata,
                )
            )
        return items

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _init_tokenizer(self, tokenizer_name: Optional[str]):
        if tiktoken is None or not tokenizer_name:
            return None
        try:
            return tiktoken.get_encoding(tokenizer_name)
        except Exception:
            try:
                return tiktoken.encoding_for_model(tokenizer_name)
            except Exception:
                return None

    def _greedy_allocation(
        self,
        candidates: Sequence[BudgetItem],
        budget: int,
    ) -> BudgetAllocation:
        included: List[BudgetItem] = []
        excluded: List[BudgetItem] = []
        tokens_used = 0

        excluded_due_to_budget: List[str] = []
        excluded_invalid: List[str] = []

        for item in candidates:
            tokens = max(int(item.token_count), 0)
            if tokens == 0:
                excluded.append(item)
                excluded_invalid.append(item.source_id)
                continue

            if tokens_used + tokens > budget:
                excluded.append(item)
                excluded_due_to_budget.append(item.source_id)
                continue

            included.append(item)
            tokens_used += tokens

        efficiency = self._calculate_efficiency(included, tokens_used)

        audit_trail = {
            "strategy": BudgetStrategy.GREEDY.value,
            "candidates_considered": len(candidates),
            "included_count": len(included),
            "excluded_count": len(excluded),
            "tokens_used": tokens_used,
            "budget_utilization": tokens_used / budget if budget > 0 else 0.0,
            "budget_remaining": max(budget - tokens_used, 0),
            "excluded_high_relevance": [
                {
                    "id": item.source_id,
                    "relevance": item.relevance_score,
                    "tokens": item.token_count,
                }
                for item in excluded
                if item.relevance_score >= 0.75
            ],
            "excluded_due_to_budget": excluded_due_to_budget,
            "excluded_invalid_token_counts": excluded_invalid,
        }

        return BudgetAllocation(
            included=included,
            excluded=excluded,
            total_tokens_used=tokens_used,
            budget_limit=budget,
            efficiency=efficiency,
            audit_trail=audit_trail,
        )

    def _balanced_allocation(
        self,
        candidates: Sequence[BudgetItem],
        budget: int,
    ) -> BudgetAllocation:
        allocation = self._greedy_allocation(candidates, budget)
        audit = dict(allocation.audit_trail)
        notes = list(audit.get("notes", []))
        notes.append("Balanced strategy not yet implemented; falling back to greedy selection.")
        audit.update(
            {
                "strategy": BudgetStrategy.BALANCED.value,
                "fallback_strategy": BudgetStrategy.GREEDY.value,
                "notes": notes,
            }
        )
        return BudgetAllocation(
            included=list(allocation.included),
            excluded=list(allocation.excluded),
            total_tokens_used=allocation.total_tokens_used,
            budget_limit=allocation.budget_limit,
            efficiency=allocation.efficiency,
            audit_trail=audit,
        )

    def _optimal_allocation(
        self,
        candidates: Sequence[BudgetItem],
        budget: int,
    ) -> BudgetAllocation:
        allocation = self._greedy_allocation(candidates, budget)
        audit = dict(allocation.audit_trail)
        notes = list(audit.get("notes", []))
        notes.append("Optimal DP strategy slated for Phase 3; using greedy fallback.")
        audit.update(
            {
                "strategy": BudgetStrategy.OPTIMAL.value,
                "fallback_strategy": BudgetStrategy.GREEDY.value,
                "notes": notes,
            }
        )
        return BudgetAllocation(
            included=list(allocation.included),
            excluded=list(allocation.excluded),
            total_tokens_used=allocation.total_tokens_used,
            budget_limit=allocation.budget_limit,
            efficiency=allocation.efficiency,
            audit_trail=audit,
        )

    @staticmethod
    def _calculate_efficiency(items: Sequence[BudgetItem], tokens_used: int) -> float:
        if tokens_used <= 0:
            return 0.0
        total_relevance = sum(item.relevance_score for item in items)
        return total_relevance / tokens_used if tokens_used else 0.0

    @staticmethod
    def _approximate_token_count(text: str) -> int:
        tokens = re.findall(r"\w+|\S", text)
        return len(tokens)


__all__ = [
    "BudgetStrategy",
    "BudgetItem",
    "BudgetAllocation",
    "TokenBudgetManager",
]

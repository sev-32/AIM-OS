"""Two-stage retrieval pipeline combining semantic search, DVNS physics, and token budgeting."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from .budget_manager import BudgetItem, BudgetStrategy, TokenBudgetManager
from .compressor import CompressionConfig, CompressionLevel, CompressionMetrics, compress_candidates
from .conflict_resolver import ConflictMetrics, ConflictRecord, detect_conflicts
from .dvns_physics import DVNSConfig, DVNSPhysics, SimulationResult, create_particles_from_search
from .hierarchical_index import HierarchicalIndex, IndexLevel, IndexNode
from .semantic_search import EmbeddingProvider, SearchResult, SemanticSearchEngine, _fallback_embedding as _semantic_fallback  # type: ignore


@dataclass
class RetrievalConfig:
    """Configuration for two-stage retrieval."""

    coarse_k: int = 100
    min_relevance: float = 0.3

    dvns_config: Optional[DVNSConfig] = None
    dvns_iterations: int = 50

    token_budget: int = 4000
    budget_strategy: BudgetStrategy = BudgetStrategy.GREEDY

    include_metrics: bool = True
    top_k_after_dvns: Optional[int] = None

    # Conflict resolution settings
    enable_conflict_resolution: bool = True
    conflict_recency_bias: float = 0.2
    conflict_authority_bias: float = 0.3

    # Strategic compression settings
    enable_compression: bool = True
    compression_config: Optional[CompressionConfig] = None


@dataclass
class RetrievalResult:
    """Result returned by the two-stage retriever."""

    selected_items: List[SearchResult]
    total_tokens: int

    coarse_candidates: int
    coarse_time_ms: float

    dvns_iterations: int
    dvns_converged: bool
    dvns_time_ms: float

    relevance_score: float
    efficiency: float
    rs_lift: Optional[float] = None

    excluded_count: int = 0
    excluded_high_relevance: List[Dict[str, float]] = field(default_factory=list)

    # Conflict resolution results
    conflicts_detected: int = 0
    conflicts_resolved: int = 0
    conflict_records: List[ConflictRecord] = field(default_factory=list)

    # Compression results
    compression_applied: bool = False
    tokens_saved_by_compression: int = 0
    compression_ratio: float = 1.0

    audit_trail: Dict[str, str] = field(default_factory=dict)


class TwoStageRetriever:
    """Complete HHNI retrieval pipeline: semantic search → DVNS → budget manager."""

    def __init__(
        self,
        hierarchical_index: HierarchicalIndex,
        config: Optional[RetrievalConfig] = None,
        *,
        semantic_search_engine: Optional[SemanticSearchEngine] = None,
        budget_manager: Optional[TokenBudgetManager] = None,
        dvns_physics: Optional[DVNSPhysics] = None,
    ) -> None:
        self.index = hierarchical_index
        self.config = config or RetrievalConfig()

        self.semantic_search = semantic_search_engine or SemanticSearchEngine(index=hierarchical_index)
        self.budget_manager = budget_manager or TokenBudgetManager(default_budget=self.config.token_budget)
        self.dvns = dvns_physics or DVNSPhysics(self.config.dvns_config or DVNSConfig())

    def retrieve(
        self,
        query: str,
        *,
        token_budget: Optional[int] = None,
        target_level: IndexLevel = IndexLevel.PARAGRAPH,
        provider: EmbeddingProvider = EmbeddingProvider.LOCAL,
    ) -> RetrievalResult:
        """Perform two-stage retrieval and return optimized context selection."""
        budget = token_budget or self.config.token_budget

        coarse_time_start = time.perf_counter()
        coarse_results = self.semantic_search.search(
            query,
            target_level=target_level,
            top_k=self.config.coarse_k,
            filter_fn=None,
        )
        coarse_time_ms = (time.perf_counter() - coarse_time_start) * 1000.0

        filtered_results = [
            result for result in coarse_results if result.score >= self.config.min_relevance
        ]

        if not filtered_results:
            return self._empty_result(coarse_time_ms)

        dvns_time_start = time.perf_counter()
        dvns_result = self._run_dvns_refinement(query, filtered_results, provider=provider)
        dvns_time_ms = (time.perf_counter() - dvns_time_start) * 1000.0

        budget_items = self._create_budget_items(dvns_result.particles, filtered_results)

        allocation = self.budget_manager.optimize_for_budget(
            budget_items,
            budget,
            strategy=self.config.budget_strategy,
            min_relevance=self.config.min_relevance,
        )

        selected_node_ids = {item.source_id for item in allocation.included}
        selected = [result for result in filtered_results if result.node.id in selected_node_ids]

        top_k = self.config.top_k_after_dvns
        if top_k is not None and len(selected) > top_k:
            selected = selected[:top_k]

        average_relevance = (
            sum(result.score for result in selected) / len(selected) if selected else 0.0
        )

        audit = allocation.audit_trail
        metrics = dvns_result.metrics

        return RetrievalResult(
            selected_items=selected,
            total_tokens=allocation.total_tokens_used,
            coarse_candidates=len(coarse_results),
            coarse_time_ms=coarse_time_ms,
            dvns_iterations=metrics.iterations,
            dvns_converged=metrics.max_velocity < self.dvns.config.convergence_velocity_threshold,
            dvns_time_ms=dvns_time_ms,
            relevance_score=average_relevance,
            efficiency=allocation.efficiency,
            excluded_count=len(allocation.excluded),
            excluded_high_relevance=audit.get("excluded_high_relevance", []),
            audit_trail={
                "budget": str(budget),
                "strategy": self.config.budget_strategy.value,
                "dvns_average_velocity": f"{metrics.avg_velocity:.6f}",
                "dvns_avg_displacement": f"{metrics.avg_displacement:.6f}",
            },
        )

    def retrieve_with_baseline_comparison(
        self,
        query: str,
        *,
        token_budget: Optional[int] = None,
        target_level: IndexLevel = IndexLevel.PARAGRAPH,
    ) -> Tuple[RetrievalResult, RetrievalResult, float]:
        """Retrieve with DVNS and baseline, returning RS-lift measurement."""
        dvns_result = self.retrieve(
            query,
            token_budget=token_budget,
            target_level=target_level,
            provider=EmbeddingProvider.LOCAL,
        )
        baseline_result = self._retrieve_baseline(query, token_budget=token_budget, target_level=target_level)
        rs_lift = self._compute_rs_lift(dvns_result, baseline_result)
        dvns_result.rs_lift = rs_lift
        return dvns_result, baseline_result, rs_lift

    # ------------------------------------------------------------------ #
    # Internal methods

    def _run_dvns_refinement(
        self,
        query: str,
        coarse_results: List[SearchResult],
        *,
        provider: EmbeddingProvider,
    ) -> SimulationResult:
        particles = create_particles_from_search(coarse_results, self.index)
        query_embedding = self._get_query_embedding(query, provider=provider)
        return self.dvns.optimize_layout(
            particles,
            query_embedding,
            iterations=self.config.dvns_iterations,
        )

    def _create_budget_items(
        self,
        particles: List["ContextParticle"],
        coarse_results: List[SearchResult],
    ) -> List[BudgetItem]:
        node_lookup: Dict[str, SearchResult] = {result.node.id: result for result in coarse_results}
        items: List[BudgetItem] = []
        for particle in particles:
            result = node_lookup.get(particle.id)
            if result is None:
                continue
            token_count = self.budget_manager.count_tokens(result.node.content or result.node.summary or "")
            token_count = max(token_count, 1)
            items.append(
                BudgetItem(
                    content=result.node.content,
                    relevance_score=result.score,
                    token_count=token_count,
                    source_id=result.node.id,
                    level=result.node.level.name if hasattr(result.node.level, "name") else str(result.node.level),
                    metadata={
                        "relevance_score": result.score,
                        "dvns_mass": particle.mass,
                        "dvns_position": (particle.position.x, particle.position.y, particle.position.z),
                    },
                )
            )
        return items

    def _retrieve_baseline(
        self,
        query: str,
        *,
        token_budget: Optional[int],
        target_level: IndexLevel,
    ) -> RetrievalResult:
        budget = token_budget or self.config.token_budget
        coarse_start = time.perf_counter()
        coarse_results = self.semantic_search.search(
            query,
            target_level=target_level,
            top_k=self.config.coarse_k,
        )
        coarse_time_ms = (time.perf_counter() - coarse_start) * 1000.0

        filtered_results = [
            result for result in coarse_results if result.score >= self.config.min_relevance
        ]

        if not filtered_results:
            return self._empty_result(coarse_time_ms)

        budget_items = [
            BudgetItem(
                content=result.node.content,
                relevance_score=result.score,
                token_count=self.budget_manager.count_tokens(result.node.content or ""),
                source_id=result.node.id,
                level=result.node.level.name if hasattr(result.node.level, "name") else str(result.node.level),
                metadata={"relevance_score": result.score},
            )
            for result in filtered_results
        ]

        # Step 3: Conflict Detection & Resolution (if enabled)
        conflict_records: List[ConflictRecord] = []
        if self.config.enable_conflict_resolution and len(budget_items) > 1:
            resolved_items, conflict_metrics = detect_conflicts(
                budget_items,
                recency_bias=self.config.conflict_recency_bias,
                authority_bias=self.config.conflict_authority_bias,
                audit=conflict_records,
            )
            budget_items = resolved_items
        else:
            conflict_metrics = ConflictMetrics(
                total_candidates=len(budget_items),
                conflicts_detected=0,
                suppressed_items=0,
            )

        # Step 4: Strategic Compression (if enabled)
        compression_audit: List[Dict] = []
        if self.config.enable_compression and len(budget_items) > 0:
            compressed_items, compression_metrics = compress_candidates(
                budget_items,
                config=self.config.compression_config,
                audit=compression_audit,
            )
            budget_items = compressed_items
        else:
            compression_metrics = CompressionMetrics(
                total_candidates=len(budget_items),
                compressed_count=0,
                tokens_saved=0,
                compression_ratio=1.0,
            )

        allocation = self.budget_manager.optimize_for_budget(
            budget_items,
            budget,
            strategy=self.config.budget_strategy,
            min_relevance=self.config.min_relevance,
        )

        selected_node_ids = {item.source_id for item in allocation.included}
        selected = [result for result in filtered_results if result.node.id in selected_node_ids]

        average_relevance = (
            sum(result.score for result in selected) / len(selected) if selected else 0.0
        )

        return RetrievalResult(
            selected_items=selected,
            total_tokens=allocation.total_tokens_used,
            coarse_candidates=len(coarse_results),
            coarse_time_ms=coarse_time_ms,
            dvns_iterations=0,
            dvns_converged=True,
            dvns_time_ms=0.0,
            relevance_score=average_relevance,
            efficiency=allocation.efficiency,
            excluded_count=len(allocation.excluded),
            excluded_high_relevance=allocation.audit_trail.get("excluded_high_relevance", []),
            conflicts_detected=conflict_metrics.conflicts_detected,
            conflicts_resolved=conflict_metrics.conflicts_detected,  # All detected conflicts are resolved
            conflict_records=conflict_records,
            compression_applied=compression_metrics.compressed_count > 0,
            tokens_saved_by_compression=compression_metrics.tokens_saved,
            compression_ratio=compression_metrics.compression_ratio,
        )

    def _compute_rs_lift(self, dvns_result: RetrievalResult, baseline_result: RetrievalResult) -> float:
        if baseline_result.relevance_score <= 0:
            return 0.0
        return (dvns_result.relevance_score - baseline_result.relevance_score) / baseline_result.relevance_score

    def _get_query_embedding(self, query: str, *, provider: EmbeddingProvider) -> List[float]:
        query = (query or "").strip()
        if not query:
            return [0.0, 0.0, 0.0]

        embed_fn = getattr(self.semantic_search, "_embed_text", None)
        if embed_fn:
            try:
                values = embed_fn(query, provider=provider)
                return [float(x) for x in values]
            except Exception:
                pass

        fallback_fn = getattr(self.semantic_search, "_fallback_embedding", None)
        if fallback_fn:
            try:
                values = fallback_fn(query)
                return [float(x) for x in values]
            except Exception:
                pass

        return list(_semantic_fallback(query))

    def _empty_result(self, coarse_time_ms: float) -> RetrievalResult:
        return RetrievalResult(
            selected_items=[],
            total_tokens=0,
            coarse_candidates=0,
            coarse_time_ms=coarse_time_ms,
            dvns_iterations=0,
            dvns_converged=True,
            dvns_time_ms=0.0,
            relevance_score=0.0,
            efficiency=0.0,
            excluded_count=0,
            excluded_high_relevance=[],
            conflicts_detected=0,
            conflicts_resolved=0,
            conflict_records=[],
            compression_applied=False,
            tokens_saved_by_compression=0,
            compression_ratio=1.0,
        )


__all__ = [
    "RetrievalConfig",
    "RetrievalResult",
    "TwoStageRetriever",
    "ConflictRecord",
    "ConflictMetrics",
    "CompressionConfig",
    "CompressionLevel",
    "CompressionMetrics",
]

"""Tests for advanced pipeline capabilities."""

from __future__ import annotations

from datetime import datetime, timezone
import time

import pytest

from cmc_service.models import AtomCreate, AtomContent, Atom
from cmc_service.advanced_pipelines import (
    BatchProcessor,
    EmbeddingBatcher,
    PipelineComposer,
    QueryOptimizer,
    CacheManager,
)


def test_batch_processor():
    """Test batch processing of atoms."""
    # Mock processor that adds ID
    def mock_processor(item: AtomCreate) -> Atom:
        return Atom(
            id=f"atom_{item.modality}",
            modality=item.modality,
            content=item.content,
            tags=item.tags
        )
    
    # Create batch
    items = [
        AtomCreate(modality="text", content=AtomContent(inline=f"Content {i}"), tags={})
        for i in range(10)
    ]
    
    processor = BatchProcessor(max_workers=4)
    results = processor.process_batch(items, mock_processor)
    
    assert len(results) == 10
    assert all(isinstance(r, Atom) for r in results)


def test_batch_processor_with_progress():
    """Test batch processor with progress callback."""
    progress_calls = []
    
    def track_progress(current: int, total: int):
        progress_calls.append((current, total))
    
    def mock_processor(item: AtomCreate) -> Atom:
        time.sleep(0.01)  # Simulate work
        return Atom(
            id=f"atom_{len(progress_calls)}",
            modality=item.modality,
            content=item.content,
            tags={}
        )
    
    items = [
        AtomCreate(modality="text", content=AtomContent(inline=f"Item {i}"), tags={})
        for i in range(5)
    ]
    
    processor = BatchProcessor(max_workers=2)
    results = processor.process_batch(items, mock_processor, progress_callback=track_progress)
    
    assert len(results) == 5
    assert len(progress_calls) == 5
    assert progress_calls[-1] == (5, 5)  # Final call should be (5, 5)


def test_pipeline_composer():
    """Test pipeline composition."""
    # Create test atoms
    atoms = [
        Atom(
            id=f"atom_{i}",
            modality="text",
            content=AtomContent(inline=f"Content {i}"),
            tags={"priority": float(i)}
        )
        for i in range(5)
    ]
    
    # Define pipeline stages
    def add_tag(atoms: List[Atom]) -> List[Atom]:
        for atom in atoms:
            atom.tags["processed"] = 1.0
        return atoms
    
    def filter_high_priority(atoms: List[Atom]) -> List[Atom]:
        return [a for a in atoms if a.tags.get("priority", 0) >= 3]
    
    # Compose pipeline
    pipeline = (PipelineComposer()
        .add_stage(add_tag)
        .add_stage(filter_high_priority))
    
    # Execute
    result = pipeline.execute(atoms)
    
    # Should only have high priority items
    assert len(result) == 2  # atoms 3 and 4
    assert all(a.tags.get("processed") == 1.0 for a in result)
    assert all(a.tags.get("priority", 0) >= 3 for a in result)


def test_query_optimizer_index_hints():
    """Test query optimizer provides correct index hints."""
    # As-of query hints
    hints = QueryOptimizer.build_index_hints('as_of')
    assert 'use_index' in hints
    assert isinstance(hints['use_index'], list)
    
    # Range query hints
    hints = QueryOptimizer.build_index_hints('range')
    assert 'use_index' in hints
    
    # History query hints
    hints = QueryOptimizer.build_index_hints('history')
    assert 'order_by' in hints


def test_query_optimizer_cost_estimation():
    """Test query cost estimation."""
    # As-of query cost
    cost = QueryOptimizer.estimate_query_cost('as_of', node_count=1000)
    assert cost['query_type'] == 'as_of'
    assert cost['estimated_rows'] == 1000
    assert cost['estimated_time_ms'] == 10  # 1000 * 0.01
    
    # Range query cost
    cost = QueryOptimizer.estimate_query_cost('range', time_range_days=30, node_count=1000)
    assert cost['query_type'] == 'range'
    assert cost['estimated_rows'] < 1000  # Should be fraction
    
    # History query cost
    cost = QueryOptimizer.estimate_query_cost('history', node_count=1000)
    assert cost['query_type'] == 'history'
    assert cost['estimated_rows'] == 5  # Average versions


def test_cache_manager_basic():
    """Test basic cache operations."""
    cache = CacheManager(max_cache_size=3)
    
    # Store results
    cache.put("query_1", ["result_1"])
    cache.put("query_2", ["result_2"])
    
    # Retrieve
    assert cache.get("query_1") == ["result_1"]
    assert cache.get("query_2") == ["result_2"]
    assert cache.get("query_3") is None


def test_cache_manager_eviction():
    """Test cache evicts oldest entries when full."""
    cache = CacheManager(max_cache_size=3)
    
    # Fill cache
    cache.put("query_1", "result_1")
    time.sleep(0.01)
    cache.put("query_2", "result_2")
    time.sleep(0.01)
    cache.put("query_3", "result_3")
    
    # Add one more (should evict oldest)
    time.sleep(0.01)
    cache.put("query_4", "result_4")
    
    # query_1 should be evicted
    assert cache.get("query_1") is None
    assert cache.get("query_2") == "result_2"
    assert cache.get("query_3") == "result_3"
    assert cache.get("query_4") == "result_4"


def test_cache_manager_invalidation():
    """Test cache invalidation."""
    cache = CacheManager(max_cache_size=10)
    
    # Store various queries
    cache.put("user_queries:123", "result_1")
    cache.put("user_queries:456", "result_2")
    cache.put("system_queries:abc", "result_3")
    
    # Invalidate user queries
    cache.invalidate(pattern="user_queries")
    
    assert cache.get("user_queries:123") is None
    assert cache.get("user_queries:456") is None
    assert cache.get("system_queries:abc") == "result_3"  # Still there
    
    # Clear all
    cache.invalidate()
    assert cache.get("system_queries:abc") is None


def test_cache_manager_stats():
    """Test cache statistics."""
    cache = CacheManager(max_cache_size=100)
    
    # Add some entries
    for i in range(10):
        cache.put(f"query_{i}", f"result_{i}")
    
    stats = cache.stats()
    assert stats['size'] == 10
    assert stats['capacity'] == 100
    assert stats['utilization'] == 0.1
    assert stats['oldest_entry'] is not None


def test_embedding_batcher_creates_batches():
    """Test embedding batcher handles batch sizes correctly."""
    # Mock model
    class MockEmbeddingModel:
        def encode(self, texts, show_progress_bar=False):
            # Return random embeddings
            import numpy as np
            return np.random.rand(len(texts), 384)
    
    batcher = EmbeddingBatcher(batch_size=3)
    model = MockEmbeddingModel()
    
    # 7 texts should create 3 batches (3, 3, 1)
    texts = [f"Text {i}" for i in range(7)]
    embeddings = batcher.generate_embeddings_batch(texts, model)
    
    assert len(embeddings) == 7
    assert all(len(emb) == 384 for emb in embeddings)


"""Advanced pipeline capabilities for CMC.

Provides:
- Batch atom processing
- Parallel embedding generation
- Pipeline composition
- Performance optimization
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Callable, Dict, Any
from datetime import datetime, timezone

from .models import Atom, AtomCreate, AtomContent


class BatchProcessor:
    """Process multiple atoms efficiently with batching and parallelism."""
    
    def __init__(self, max_workers: int = 4):
        """Initialize batch processor.
        
        Args:
            max_workers: Maximum parallel workers for processing
        """
        self.max_workers = max_workers
    
    def process_batch(
        self,
        items: List[AtomCreate],
        processor: Callable[[AtomCreate], Atom],
        *,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Atom]:
        """Process a batch of atom creation requests in parallel.
        
        Args:
            items: List of AtomCreate requests
            processor: Function to process each item
            progress_callback: Optional callback(current, total)
            
        Returns:
            List of created atoms
            
        Example:
            processor = BatchProcessor(max_workers=4)
            atoms = processor.process_batch(
                atom_requests,
                store.create_atom,
                progress_callback=lambda cur, tot: print(f"{cur}/{tot}")
            )
        """
        results: List[Atom] = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(processor, item): (i, item)
                for i, item in enumerate(items)
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_item):
                i, item = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                    completed += 1
                    
                    if progress_callback:
                        progress_callback(completed, len(items))
                        
                except Exception as e:
                    # Log error but continue processing
                    print(f"Error processing item {i}: {e}")
        
        return results


class EmbeddingBatcher:
    """Batch embedding generation for efficiency."""
    
    def __init__(self, batch_size: int = 32):
        """Initialize embedding batcher.
        
        Args:
            batch_size: Number of texts to embed in one batch
        """
        self.batch_size = batch_size
    
    def generate_embeddings_batch(
        self,
        texts: List[str],
        embedding_model: Any  # SentenceTransformer or similar
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of text strings to embed
            embedding_model: Model with encode() method
            
        Returns:
            List of embedding vectors
            
        Example:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            batcher = EmbeddingBatcher(batch_size=32)
            embeddings = batcher.generate_embeddings_batch(texts, model)
        """
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = embedding_model.encode(batch, show_progress_bar=False)
            all_embeddings.extend(batch_embeddings.tolist())
        
        return all_embeddings


class PipelineComposer:
    """Compose atom processing pipelines with multiple stages."""
    
    def __init__(self):
        self.stages: List[Callable] = []
    
    def add_stage(self, stage: Callable[[List[Atom]], List[Atom]]) -> 'PipelineComposer':
        """Add a processing stage to the pipeline.
        
        Args:
            stage: Function that takes atoms and returns processed atoms
            
        Returns:
            Self for chaining
        """
        self.stages.append(stage)
        return self
    
    def execute(self, atoms: List[Atom]) -> List[Atom]:
        """Execute the complete pipeline.
        
        Args:
            atoms: Input atoms
            
        Returns:
            Atoms after all pipeline stages
            
        Example:
            pipeline = (PipelineComposer()
                .add_stage(enrich_with_embeddings)
                .add_stage(extract_entities)
                .add_stage(apply_quality_gates))
            
            processed_atoms = pipeline.execute(raw_atoms)
        """
        current = atoms
        for stage in self.stages:
            current = stage(current)
        return current


class QueryOptimizer:
    """Optimize complex queries for performance."""
    
    @staticmethod
    def build_index_hints(query_type: str) -> Dict[str, Any]:
        """Provide index hints for different query types.
        
        Args:
            query_type: Type of query (as_of, range, history, audit)
            
        Returns:
            Dictionary of optimization hints
        """
        hints = {
            'as_of': {
                'use_index': ['idx_mpd_nodes_tt_start', 'idx_mpd_nodes_vt_start'],
                'order_by': 'mpd_id',  # Use primary key order
                'limit_first': True  # Apply limits before joins
            },
            'range': {
                'use_index': ['idx_mpd_nodes_tt_start', 'idx_mpd_nodes_tt_end'],
                'consider_covering': True,  # Covering index scan
                'parallel_scan': False  # Sequential for range
            },
            'history': {
                'use_index': ['idx_mpd_nodes_id_tt'],  # Composite index ideal
                'order_by': 'tt_start',
                'limit_first': False
            },
            'audit': {
                'use_index': 'multiple',
                'join_order': ['nodes', 'edges'],  # Nodes first
                'materialize': True  # Materialize subqueries
            }
        }
        
        return hints.get(query_type, {})
    
    @staticmethod
    def estimate_query_cost(
        query_type: str,
        time_range_days: Optional[int] = None,
        node_count: int = 1000
    ) -> Dict[str, Any]:
        """Estimate query cost for planning.
        
        Args:
            query_type: Type of query
            time_range_days: For range queries
            node_count: Estimated node count
            
        Returns:
            Cost estimates (rows scanned, time estimate)
        """
        if query_type == 'as_of':
            rows_scanned = node_count  # Full table scan
            time_ms = node_count * 0.01  # ~0.01ms per node
        elif query_type == 'range':
            fraction = (time_range_days or 30) / 365
            rows_scanned = int(node_count * fraction)
            time_ms = rows_scanned * 0.02
        elif query_type == 'history':
            rows_scanned = 5  # Average versions per entity
            time_ms = 5
        else:
            rows_scanned = node_count
            time_ms = node_count * 0.05
        
        return {
            'query_type': query_type,
            'estimated_rows': rows_scanned,
            'estimated_time_ms': time_ms,
            'recommended_indexes': QueryOptimizer.build_index_hints(query_type)
        }


class CacheManager:
    """Manage query result caching for performance."""
    
    def __init__(self, max_cache_size: int = 1000):
        """Initialize cache manager.
        
        Args:
            max_cache_size: Maximum number of cached queries
        """
        self.max_cache_size = max_cache_size
        self._cache: Dict[str, Any] = {}
        self._access_times: Dict[str, datetime] = {}
    
    def get(self, cache_key: str) -> Optional[Any]:
        """Get cached result if available.
        
        Args:
            cache_key: Unique key for the query
            
        Returns:
            Cached result or None
        """
        if cache_key in self._cache:
            self._access_times[cache_key] = datetime.now(timezone.utc)
            return self._cache[cache_key]
        return None
    
    def put(self, cache_key: str, result: Any) -> None:
        """Store query result in cache.
        
        Args:
            cache_key: Unique key for the query
            result: Query result to cache
        """
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_cache_size:
            oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
            del self._cache[oldest_key]
            del self._access_times[oldest_key]
        
        self._cache[cache_key] = result
        self._access_times[cache_key] = datetime.now(timezone.utc)
    
    def invalidate(self, pattern: Optional[str] = None) -> None:
        """Invalidate cache entries.
        
        Args:
            pattern: Optional pattern to match keys (None = clear all)
        """
        if pattern is None:
            self._cache.clear()
            self._access_times.clear()
        else:
            keys_to_remove = [k for k in self._cache if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
                del self._access_times[key]
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with size, hit rate estimate, etc.
        """
        return {
            'size': len(self._cache),
            'capacity': self.max_cache_size,
            'utilization': len(self._cache) / self.max_cache_size,
            'oldest_entry': min(self._access_times.values()) if self._access_times else None
        }


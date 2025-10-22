#!/usr/bin/env python
"""HHNI Retrieval Performance Benchmark

Measures retrieval latency and relevance against KR-1-2 targets:
- Goal: Retrieval <200ms (p95), 90% relevance score

This benchmark specifically measures the READ path (retrieval.retrieve()),
complementing hhni_performance.py which measures the WRITE path.

Usage:
    python benchmarks/hhni_retrieval_benchmark.py --queries 100 --corpus 1000
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

from hhni.retrieval import RetrievalConfig, TwoStageRetriever
from hhni.semantic_search import SearchResult, FallbackEmbeddingProvider
from hhni.budget_manager import BudgetItem


def create_test_corpus(size: int) -> List[SearchResult]:
    """Create a synthetic corpus for benchmarking."""
    corpus = []
    topics = [
        "machine learning", "neural networks", "AI safety", "consciousness",
        "memory systems", "context optimization", "retrieval algorithms",
        "semantic search", "embeddings", "knowledge graphs"
    ]
    
    for i in range(size):
        topic = topics[i % len(topics)]
        text = f"Document {i} about {topic}. " * 10  # ~100 tokens
        
        # Simulate relevance scores
        base_score = 0.5 + (i % 50) / 100  # 0.5 to 1.0
        
        result = SearchResult(
            source_id=f"doc-{i}",
            text=text,
            relevance_score=base_score,
            level="paragraph",
            metadata={"topic": topic, "index": i}
        )
        corpus.append(result)
    
    return corpus


def create_test_queries(count: int) -> List[tuple[str, List[str]]]:
    """Create test queries with expected relevant doc IDs."""
    queries = [
        ("What is machine learning?", ["doc-0", "doc-10", "doc-20"]),
        ("How do neural networks work?", ["doc-1", "doc-11", "doc-21"]),
        ("Explain AI safety concerns", ["doc-2", "doc-12", "doc-22"]),
        ("What is consciousness?", ["doc-3", "doc-13", "doc-23"]),
        ("How do memory systems work?", ["doc-4", "doc-14", "doc-24"]),
        ("Optimize context retrieval", ["doc-5", "doc-15", "doc-25"]),
        ("Retrieval algorithm comparison", ["doc-6", "doc-16", "doc-26"]),
        ("Semantic search techniques", ["doc-7", "doc-17", "doc-27"]),
        ("Embedding generation methods", ["doc-8", "doc-18", "doc-28"]),
        ("Knowledge graph construction", ["doc-9", "doc-19", "doc-29"]),
    ]
    
    # Repeat to reach desired count
    repeated = []
    while len(repeated) < count:
        repeated.extend(queries)
    
    return repeated[:count]


def calculate_relevance(retrieved_ids: List[str], expected_ids: List[str]) -> float:
    """Calculate relevance as precision@k."""
    if not retrieved_ids:
        return 0.0
    
    relevant_retrieved = sum(1 for doc_id in retrieved_ids if doc_id in expected_ids)
    return relevant_retrieved / len(retrieved_ids)


def benchmark_retrieval(
    retriever: TwoStageRetriever,
    queries: List[tuple[str, List[str]]],
    corpus: List[SearchResult],
    config: RetrievalConfig,
) -> Dict[str, Any]:
    """Run retrieval benchmark on a set of queries."""
    print(f"\n{'='*60}")
    print(f"Benchmark: HHNI Retrieval Pipeline")
    print(f"Queries: {len(queries)}")
    print(f"Corpus: {len(corpus)}")
    print(f"{'='*60}\n")
    
    latencies = []
    relevances = []
    tokens_used = []
    
    for i, (query, expected_ids) in enumerate(queries):
        start = time.perf_counter()
        
        # This is what we're benchmarking
        result = retriever.retrieve(query, corpus, config)
        
        duration = (time.perf_counter() - start) * 1000  # ms
        latencies.append(duration)
        
        # Calculate relevance
        retrieved_ids = [item.source_id for item in result.selected_items]
        relevance = calculate_relevance(retrieved_ids, expected_ids)
        relevances.append(relevance)
        
        tokens_used.append(result.total_tokens)
        
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{len(queries)} queries")
    
    # Calculate statistics
    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p90 = latencies[int(len(latencies) * 0.90)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    
    return {
        "queries": len(queries),
        "corpus_size": len(corpus),
        "mean_latency_ms": statistics.mean(latencies),
        "median_latency_ms": p50,
        "p90_latency_ms": p90,
        "p95_latency_ms": p95,
        "p99_latency_ms": p99,
        "min_latency_ms": min(latencies),
        "max_latency_ms": max(latencies),
        "mean_relevance": statistics.mean(relevances),
        "median_relevance": statistics.median(relevances),
        "min_relevance": min(relevances),
        "max_relevance": max(relevances),
        "mean_tokens": statistics.mean(tokens_used),
        "config": {
            "coarse_k": config.coarse_k,
            "token_budget": config.token_budget,
            "dvns_iterations": config.dvns_iterations,
            "enable_conflict_resolution": config.enable_conflict_resolution,
            "enable_compression": config.enable_compression,
        }
    }


def benchmark_ablation_study(
    corpus: List[SearchResult],
    queries: List[tuple[str, List[str]]],
) -> Dict[str, Any]:
    """Benchmark different configurations to measure feature impact."""
    print(f"\n{'='*60}")
    print(f"Ablation Study: Feature Impact on Performance")
    print(f"{'='*60}\n")
    
    configs = {
        "baseline": RetrievalConfig(
            enable_conflict_resolution=False,
            enable_compression=False,
            dvns_iterations=0  # Disable DVNS
        ),
        "with_dvns": RetrievalConfig(
            enable_conflict_resolution=False,
            enable_compression=False,
            dvns_iterations=50
        ),
        "with_conflicts": RetrievalConfig(
            enable_conflict_resolution=True,
            enable_compression=False,
            dvns_iterations=50
        ),
        "full_pipeline": RetrievalConfig(
            enable_conflict_resolution=True,
            enable_compression=True,
            dvns_iterations=50
        ),
    }
    
    results = {}
    embedding_provider = FallbackEmbeddingProvider()
    
    for name, config in configs.items():
        print(f"\nTesting configuration: {name}")
        retriever = TwoStageRetriever(embedding_provider)
        results[name] = benchmark_retrieval(retriever, queries[:20], corpus, config)
    
    return results


def print_results(results: Dict[str, Any], target_latency: float, target_relevance: float) -> None:
    """Print formatted benchmark results."""
    print(f"\n{'='*60}")
    print("RETRIEVAL BENCHMARK RESULTS")
    print(f"{'='*60}\n")
    
    print(f"Corpus: {results['corpus_size']} documents")
    print(f"Queries: {results['queries']}")
    print(f"\nLatency Statistics:")
    print(f"  Mean: {results['mean_latency_ms']:.2f}ms")
    print(f"  Median: {results['median_latency_ms']:.2f}ms")
    print(f"  p90: {results['p90_latency_ms']:.2f}ms")
    print(f"  p95: {results['p95_latency_ms']:.2f}ms")
    print(f"  p99: {results['p99_latency_ms']:.2f}ms")
    print(f"  Range: [{results['min_latency_ms']:.2f}, {results['max_latency_ms']:.2f}]ms")
    
    print(f"\nRelevance Statistics:")
    print(f"  Mean: {results['mean_relevance']:.3f} ({results['mean_relevance']*100:.1f}%)")
    print(f"  Median: {results['median_relevance']:.3f}")
    print(f"  Range: [{results['min_relevance']:.3f}, {results['max_relevance']:.3f}]")
    
    print(f"\nToken Usage:")
    print(f"  Mean: {results['mean_tokens']:.0f} tokens")
    
    print(f"\n{'='*60}")
    print("KR-1-2 TARGET VALIDATION")
    print(f"{'='*60}\n")
    
    latency_pass = results['p95_latency_ms'] < target_latency
    relevance_pass = results['mean_relevance'] >= target_relevance
    
    latency_status = "[PASS]" if latency_pass else "[FAIL]"
    relevance_status = "[PASS]" if relevance_pass else "[FAIL]"
    
    print(f"{latency_status} Retrieval p95 < {target_latency}ms: {results['p95_latency_ms']:.2f}ms")
    print(f"{relevance_status} Mean relevance >= {target_relevance*100}%: {results['mean_relevance']*100:.1f}%")
    
    if latency_pass and relevance_pass:
        print(f"\n✅ KR-1-2 ACHIEVED!")
    else:
        print(f"\n⚠️ KR-1-2 NOT MET - Optimization needed")


def print_ablation_results(results: Dict[str, Any]) -> None:
    """Print ablation study results."""
    print(f"\n{'='*60}")
    print("ABLATION STUDY RESULTS")
    print(f"{'='*60}\n")
    
    print(f"{'Configuration':<20} {'Latency (p95)':<15} {'Relevance':<12} {'Delta Latency':<15} {'Delta Relevance'}")
    print(f"{'-'*80}")
    
    baseline_latency = results['baseline']['p95_latency_ms']
    baseline_relevance = results['baseline']['mean_relevance']
    
    for name, data in results.items():
        latency = data['p95_latency_ms']
        relevance = data['mean_relevance']
        
        delta_latency = latency - baseline_latency
        delta_relevance = relevance - baseline_relevance
        
        delta_lat_str = f"{delta_latency:+.2f}ms" if name != "baseline" else "baseline"
        delta_rel_str = f"{delta_relevance:+.3f}" if name != "baseline" else "baseline"
        
        print(f"{name:<20} {latency:.2f}ms{'':<7} {relevance:.3f}{'':<6} {delta_lat_str:<15} {delta_rel_str}")


def main():
    parser = argparse.ArgumentParser(description="HHNI Retrieval Benchmark")
    parser.add_argument("--queries", type=int, default=100, help="Number of queries to run")
    parser.add_argument("--corpus", type=int, default=1000, help="Corpus size (number of documents)")
    parser.add_argument("--ablation", action="store_true", help="Run ablation study")
    parser.add_argument("--output", type=str, help="Save results to JSON file")
    args = parser.parse_args()
    
    print(f"\nHHNI Retrieval Performance Benchmark")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print(f"Queries: {args.queries}")
    print(f"Corpus: {args.corpus}")
    
    # Setup
    corpus = create_test_corpus(args.corpus)
    queries = create_test_queries(args.queries)
    
    embedding_provider = FallbackEmbeddingProvider()
    retriever = TwoStageRetriever(embedding_provider)
    config = RetrievalConfig(
        coarse_k=100,
        token_budget=4000,
        dvns_iterations=50,
        enable_conflict_resolution=True,
        enable_compression=True,
    )
    
    # KR-1-2 targets
    target_latency = 200  # ms (p95)
    target_relevance = 0.90  # 90%
    
    # Run main benchmark
    results = benchmark_retrieval(retriever, queries, corpus, config)
    print_results(results, target_latency, target_relevance)
    
    # Optional ablation study
    ablation_results = None
    if args.ablation:
        ablation_results = benchmark_ablation_study(corpus, queries)
        print_ablation_results(ablation_results)
    
    # Save results
    if args.output:
        output_path = Path(args.output)
        output_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config": {
                "queries": args.queries,
                "corpus": args.corpus,
            },
            "results": results,
            "ablation": ablation_results,
            "targets": {
                "latency_p95_ms": target_latency,
                "relevance_mean": target_relevance,
            }
        }
        output_path.write_text(json.dumps(output_data, indent=2))
        print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()


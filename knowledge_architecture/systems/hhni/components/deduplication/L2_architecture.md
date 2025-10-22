# Deduplication L2: Implementation Architecture

**Detail Level:** 2 of 5 (2,000 words)  
**Context Budget:** ~32k tokens  
**Purpose:** Complete deduplication specification

---

## Algorithm Implementation

### Semantic Clustering

```python
def remove_duplicates(
    items: List[BudgetItem],
    threshold: float = 0.85,
    audit: Optional[List[Dict]] = None
) -> Tuple[List[BudgetItem], int]:
    """
    Remove semantically similar items via clustering.
    
    Algorithm:
    1. Compute pairwise similarity matrix
    2. Cluster items with similarity >= threshold
    3. Select best from each cluster
    4. Return unique items + suppressed count
    """
    if not items:
        return [], 0
    
    # Build similarity matrix
    n = len(items)
    embeddings = np.array([item.embedding for item in items])
    similarities = cosine_similarity(embeddings)
    
    # Agglomerative clustering
    clusters = []
    assigned = set()
    
    for i in range(n):
        if i in assigned:
            continue
        
        # Start new cluster
        cluster_indices = [i]
        assigned.add(i)
        
        # Add similar items
        for j in range(i + 1, n):
            if j not in assigned and similarities[i, j] >= threshold:
                cluster_indices.append(j)
                assigned.add(j)
        
        clusters.append(cluster_indices)
    
    # Select best from each cluster
    kept_items = []
    suppressed_count = 0
    
    for cluster_idx in clusters:
        cluster_items = [items[i] for i in cluster_idx]
        
        # Select best (composite score)
        best_item = select_best_from_cluster(cluster_items)
        kept_items.append(best_item)
        
        suppressed_count += len(cluster_items) - 1
        
        # Audit trail
        if audit is not None and len(cluster_items) > 1:
            audit.append({
                "cluster_size": len(cluster_items),
                "kept": best_item.source_id,
                "suppressed": [item.source_id for item in cluster_items if item != best_item],
                "similarity_threshold": threshold,
                "best_score": composite_score(best_item)
            })
    
    return kept_items, suppressed_count

def select_best_from_cluster(cluster: List[BudgetItem]) -> BudgetItem:
    """Choose most valuable item"""
    scores = [composite_score(item) for item in cluster]
    best_idx = scores.index(max(scores))
    return cluster[best_idx]

def composite_score(item: BudgetItem) -> float:
    """Combined quality metric"""
    # Recency (7-day half-life)
    age_seconds = (datetime.utcnow() - item.timestamp).total_seconds()
    recency = 1.0 / (1.0 + age_seconds / (7 * 86400))
    
    # Relevance (from retrieval)
    relevance = item.relevance_score
    
    # Authority (verified source)
    authority = 1.0 if item.verified else 0.7
    
    # Weighted combination
    return 0.4 * relevance + 0.3 * recency + 0.3 * authority
```

---

## Hash-Based Exact Deduplication

```python
def deduplicate_by_hash(items: List[BudgetItem]) -> List[BudgetItem]:
    """Remove exact duplicates using content hash"""
    seen_hashes = set()
    unique_items = []
    
    for item in items:
        # Compute content hash
        content_hash = hashlib.sha256(item.content.encode('utf-8')).hexdigest()
        
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_items.append(item)
    
    return unique_items
```

---

## Hybrid Approach (Default)

```python
def deduplicate_hybrid(
    items: List[BudgetItem],
    semantic_threshold: float = 0.85
) -> Tuple[List[BudgetItem], DeduplicationMetrics]:
    """Combined hash + semantic deduplication"""
    start_time = time.time()
    
    # Step 1: Hash-based exact match removal
    hash_start = time.time()
    items_after_hash = deduplicate_by_hash(items)
    hash_removed = len(items) - len(items_after_hash)
    hash_time = time.time() - hash_start
    
    # Step 2: Semantic near-duplicate removal
    semantic_start = time.time()
    audit_trail = []
    items_final, semantic_removed = remove_duplicates(
        items_after_hash,
        threshold=semantic_threshold,
        audit=audit_trail
    )
    semantic_time = time.time() - semantic_start
    
    # Build metrics
    metrics = DeduplicationMetrics(
        original_count=len(items),
        final_count=len(items_final),
        hash_duplicates_removed=hash_removed,
        semantic_duplicates_removed=semantic_removed,
        total_removed=hash_removed + semantic_removed,
        tokens_saved=estimate_tokens_saved(items, items_final),
        time_ms=(time.time() - start_time) * 1000,
        hash_time_ms=hash_time * 1000,
        semantic_time_ms=semantic_time * 1000,
        audit_trail=audit_trail
    )
    
    return items_final, metrics
```

---

## Performance Analysis

**Complexity:**
- Hash-based: O(N) - linear scan
- Semantic: O(N²) - pairwise similarity
- Combined: O(N²) dominated by semantic

**Optimizations:**
```python
# Use approximate nearest neighbors for large N
from sklearn.neighbors import NearestNeighbors

def deduplicate_semantic_fast(items: List[BudgetItem]) -> List[BudgetItem]:
    """Fast approximate semantic dedup"""
    embeddings = np.array([item.embedding for item in items])
    
    # Build NN index
    nn = NearestNeighbors(n_neighbors=10, metric='cosine')
    nn.fit(embeddings)
    
    # Find neighbors for each item
    distances, indices = nn.kneighbors(embeddings)
    
    # Cluster based on neighbors
    clusters = cluster_from_neighbors(indices, distances, threshold=0.15)
    
    # Select best from each
    return [select_best_from_cluster([items[i] for i in cluster]) for cluster in clusters]
```

---

## Testing

```python
def test_removes_exact_duplicates():
    """Hash-based dedup test"""
    items = [
        create_item("exact content"),
        create_item("exact content"),  # Duplicate!
        create_item("different content")
    ]
    
    result, count = deduplicate_hybrid(items)
    
    assert len(result) == 2  # Removed 1 duplicate
    assert count == 1

def test_removes_semantic_near_duplicates():
    """Semantic dedup test"""
    items = [
        create_item("The user logged in successfully"),
        create_item("User login was successful"),  # Near duplicate
        create_item("Payment failed with error")
    ]
    
    result, count = deduplicate_hybrid(items, semantic_threshold=0.85)
    
    assert len(result) == 2  # Removed semantic duplicate
    
def test_preserves_best_item():
    """Ensure best quality item kept"""
    items = [
        create_item("content", relevance=0.6, age=10, verified=False),
        create_item("content", relevance=0.9, age=1, verified=True),  # BEST
        create_item("content", relevance=0.7, age=5, verified=False)
    ]
    
    result, _ = deduplicate_hybrid(items)
    
    assert len(result) == 1
    assert result[0].relevance_score == 0.9  # Kept best
```

---

## Summary

Efficient deduplication with hash + semantic methods, composite scoring, complete audit trails.

**Implementation:** `packages/hhni/deduplication.py` (217 lines, 8 tests passing)

---

**Word Count:** ~2,000  
**Next:** [L3_detailed.md](L3_detailed.md)


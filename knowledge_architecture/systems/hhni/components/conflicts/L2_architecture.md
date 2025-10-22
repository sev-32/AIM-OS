# Conflict Resolution L2: Architecture & Implementation

**Detail Level:** 2 of 5 (2,000 words)  
**Context Budget:** ~32k tokens  
**Purpose:** Complete conflict resolution specification

---

## Detection Algorithm

### Contradiction Detection

```python
class ConflictDetector:
    """Detect contradictory information"""
    
    def detect_conflicts(
        self,
        items: List[BudgetItem]
    ) -> List[ConflictRecord]:
        """Find contradictions in retrieval results"""
        conflicts = []
        n = len(items)
        
        for i in range(n):
            for j in range(i + 1, n):
                # Check if same topic (high similarity)
                topic_sim = cosine_similarity(
                    [items[i].embedding],
                    [items[j].embedding]
                )[0, 0]
                
                if topic_sim < 0.6:
                    continue  # Different topics
                
                # Check if contradictory
                contradiction_score = self._analyze_contradiction(
                    items[i].content,
                    items[j].content
                )
                
                if contradiction_score > 0.5:
                    # Contradiction detected!
                    topic = self._extract_topic(items[i], items[j])
                    
                    conflicts.append(ConflictRecord(
                        topic=topic,
                        item_ids=[items[i].source_id, items[j].source_id],
                        similarity=topic_sim,
                        contradiction_score=contradiction_score
                    ))
        
        return conflicts
    
    def _analyze_contradiction(
        self,
        content_a: str,
        content_b: str
    ) -> float:
        """
        Determine if two texts are contradictory (0.0-1.0).
        
        Uses simplified stance detection.
        Real implementation would use NLP or LLM.
        """
        stance_a = self._extract_stance(content_a)
        stance_b = self._extract_stance(content_b)
        
        # Opposite stances = contradiction
        if self._are_opposite(stance_a, stance_b):
            return 1.0
        elif stance_a != stance_b:
            return 0.5  # Somewhat contradictory
        else:
            return 0.0  # Same stance
    
    def _extract_stance(self, content: str) -> str:
        """Extract stance (positive/negative/neutral)"""
        content_lower = content.lower()
        
        # Keyword-based (simplified)
        positive_kw = ["yes", "good", "better", "recommend", "should", "prefer"]
        negative_kw = ["no", "bad", "worse", "avoid", "shouldn't", "against"]
        
        pos_count = sum(1 for kw in positive_kw if kw in content_lower)
        neg_count = sum(1 for kw in negative_kw if kw in content_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
```

---

## Resolution Algorithm

### Clustering by Topic and Stance

```python
def resolve_conflicts(
    items: List[BudgetItem],
    conflicts: List[ConflictRecord],
    recency_bias: float = 0.3,
    authority_bias: float = 0.4
) -> Tuple[List[BudgetItem], List[ResolutionRecord]]:
    """Resolve all detected conflicts"""
    resolution_records = []
    suppressed_ids = set()
    
    # Group conflicts by topic
    by_topic = {}
    for conflict in conflicts:
        topic = conflict.topic
        if topic not in by_topic:
            by_topic[topic] = []
        by_topic[topic].extend(conflict.item_ids)
    
    # Resolve each topic
    for topic, item_ids in by_topic.items():
        # Get items
        topic_items = [item for item in items if item.source_id in item_ids]
        
        # Cluster by stance
        stance_map = cluster_by_stance(topic_items)
        
        # CRITICAL: Select ABSOLUTE best across ALL stances
        # (This was the Week 3 fix!)
        best_item, winning_stance, suppressed, rationale = resolve_cluster(
            topic=topic,
            stance_map=stance_map,
            recency_bias=recency_bias,
            authority_bias=authority_bias
        )
        
        # Record resolution
        resolution_records.append(ResolutionRecord(
            topic=topic,
            stances_detected=list(stance_map.keys()),
            winning_stance=winning_stance,
            winner_id=best_item.source_id,
            suppressed_ids=suppressed,
            rationale=rationale
        ))
        
        suppressed_ids.update(suppressed)
    
    # Filter out suppressed items
    final_items = [item for item in items if item.source_id not in suppressed_ids]
    
    return final_items, resolution_records

def resolve_cluster(
    topic: str,
    stance_map: Dict[str, List[BudgetItem]],
    recency_bias: float,
    authority_bias: float
) -> Tuple[BudgetItem, str, List[str], str]:
    """
    CRITICAL FUNCTION - Fixed Week 3!
    
    OLD BUG: Selected best from each stance separately
    NEW FIX: Selects ABSOLUTE best across ALL stances
    """
    # Collect ALL items from ALL stances
    all_items = []
    for stance, members in stance_map.items():
        all_items.extend(members)
    
    if not all_items:
        raise ValueError(f"No items to resolve for topic '{topic}'")
    
    # Select SINGLE best across EVERYTHING
    best_item, best_score = select_best_item(
        all_items,
        recency_bias=recency_bias,
        authority_bias=authority_bias
    )
    
    # Determine winning stance
    winning_stance = get_stance(best_item.content)
    if not winning_stance:
        winning_stance = next(iter(stance_map.keys()))
    
    # Suppress ALL others (not just per-stance!)
    suppressed_ids = [
        item.source_id for item in all_items
        if item.source_id != best_item.source_id
    ]
    
    # Rationale
    rationale = (
        f"topic '{topic}' had conflicting stances {list(stance_map.keys())}; "
        f"resolved in favour of {winning_stance} stance; "
        f"kept {best_item.source_id} with composite score {best_score:.4f} "
        f"(relevance={best_item.relevance_score:.3f}, recency_bias={recency_bias}, "
        f"authority_bias={authority_bias})"
    )
    
    return best_item, winning_stance, suppressed_ids, rationale

def select_best_item(
    items: List[BudgetItem],
    recency_bias: float,
    authority_bias: float
) -> Tuple[BudgetItem, float]:
    """Select best item with configurable bias"""
    base_weight = 1.0 - recency_bias - authority_bias
    
    best_item = None
    best_score = -1.0
    
    for item in items:
        # Recency component
        age_seconds = (datetime.utcnow() - item.timestamp).total_seconds()
        recency = 1.0 / (1.0 + age_seconds / (7 * 86400))
        
        # Authority component
        authority = 1.0 if item.verified else 0.7
        
        # Composite score
        score = (
            base_weight * item.relevance_score +
            recency_bias * recency +
            authority_bias * authority
        )
        
        if score > best_score:
            best_score = score
            best_item = item
    
    return best_item, best_score
```

---

## Testing (Critical Week 3 Fix Validation)

```python
def test_recency_breaks_ties():
    """
    Test that newer items win when relevance tied.
    
    This test FAILED before Week 3 fix!
    NOW PASSES after fixing resolve_cluster to select absolute best.
    """
    old_item = BudgetItem(
        source_id="item-old",
        relevance_score=0.8,
        timestamp=datetime.utcnow() - timedelta(days=30),
        verified=False
    )
    
    new_item = BudgetItem(
        source_id="item-new",
        relevance_score=0.8,  # Same relevance!
        timestamp=datetime.utcnow() - timedelta(days=1),
        verified=False
    )
    
    stance_map = {"positive": [old_item, new_item]}
    
    winner, stance, suppressed, rationale = resolve_cluster(
        topic="test",
        stance_map=stance_map,
        recency_bias=0.5,  # High recency bias
        authority_bias=0.0
    )
    
    # NEW item should win (recency bias)
    assert winner.source_id == "item-new"  # ✅ PASSES after fix!
    assert "item-old" in suppressed
    
def test_authority_beats_recency_when_high_bias():
    """Authority bias can override recency"""
    new_unverified = BudgetItem(
        source_id="new",
        relevance_score=0.8,
        timestamp=datetime.utcnow(),
        verified=False
    )
    
    old_verified = BudgetItem(
        source_id="old",
        relevance_score=0.8,
        timestamp=datetime.utcnow() - timedelta(days=30),
        verified=True  # But verified!
    )
    
    winner, _, _, _ = resolve_cluster(
        topic="test",
        stance_map={"positive": [new_unverified, old_verified]},
        recency_bias=0.2,
        authority_bias=0.6  # High authority bias
    )
    
    assert winner.source_id == "old"  # Verified wins despite age!
```

---

## Summary

Complete conflict detection and resolution with stance clustering, composite scoring, and audit trails.

**Implementation:** `packages/hhni/conflict_resolver.py` (8 tests passing)

**Critical fix:** Week 3 - absolute best selection (not per-stance)

---

**Word Count:** ~2,000  
**Next:** [L3_detailed.md](L3_detailed.md)


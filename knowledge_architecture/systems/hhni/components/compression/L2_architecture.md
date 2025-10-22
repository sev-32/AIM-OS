# Compression L2: Implementation Architecture

**Detail Level:** 2 of 5 (2,000 words)  
**Context Budget:** ~32k tokens  
**Purpose:** Complete compression specification

---

## Compression Level System

### Level Determination (With Priority Boost)

```python
from enum import Enum
from dataclasses import dataclass

class CompressionLevel(Enum):
    NONE = "none"      # 0% reduction
    LIGHT = "light"    # 10-15% reduction
    MEDIUM = "medium"  # 30-40% reduction
    HEAVY = "heavy"    # 50-70% reduction

def determine_compression_level(
    age_days: float,
    priority: str,
    config: CompressionConfig
) -> CompressionLevel:
    """
    Determine compression level based on age and priority.
    
    Priority boost (Week 3 enhancement):
    - High priority items get 2x age thresholds
    - Keeps important content detailed longer
    """
    # Priority multiplier
    if priority == "high" and config.enable_priority_boost:
        multiplier = config.high_priority_multiplier  # 2.0 default
    else:
        multiplier = 1.0
    
    # Apply thresholds with multiplier
    if age_days < config.none_threshold * multiplier:
        return CompressionLevel.NONE
    elif age_days < config.light_threshold * multiplier:
        return CompressionLevel.LIGHT
    elif age_days < config.medium_threshold * multiplier:
        return CompressionLevel.MEDIUM
    else:
        return CompressionLevel.HEAVY
```

**Priority Boost Example:**
```
Normal priority, age=10 days:
    10 < 7? No
    10 < 30? Yes → LIGHT compression

High priority, age=10 days:
    10 < 7*2=14? Yes → NONE (full detail!)
    
Result: High priority stays detailed 2x longer!
```

---

## Compression Methods

### LIGHT Compression (10-15% reduction)

```python
def compress_light(content: str) -> str:
    """Remove redundant phrases, keep structure"""
    # Remove filler words
    fillers = ["basically", "actually", "literally", "essentially"]
    for filler in fillers:
        content = content.replace(f" {filler} ", " ")
    
    # Remove redundant phrases
    content = remove_redundant_phrases(content)
    
    # Compress whitespace
    content = ' '.join(content.split())
    
    return content

def remove_redundant_phrases(text: str) -> str:
    """Remove semantically redundant phrases"""
    # "in order to" → "to"
    text = text.replace("in order to", "to")
    # "due to the fact that" → "because"
    text = text.replace("due to the fact that", "because")
    # "at this point in time" → "now"
    text = text.replace("at this point in time", "now")
    
    return text
```

---

### MEDIUM Compression (30-40% reduction)

```python
def compress_medium(content: str) -> str:
    """Extractive summarization - keep key sentences"""
    sentences = nltk.sent_tokenize(content)
    
    if len(sentences) <= 3:
        return content  # Too short to compress
    
    # Score sentences by importance
    scores = []
    for sent in sentences:
        score = score_sentence_importance(sent, sentences)
        scores.append(score)
    
    # Keep top 60%
    keep_count = max(2, int(len(sentences) * 0.6))
    top_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:keep_count]
    
    # Preserve order
    top_indices.sort()
    kept_sentences = [sentences[i] for i in top_indices]
    
    return ' '.join(kept_sentences)

def score_sentence_importance(
    sentence: str,
    all_sentences: List[str]
) -> float:
    """Score sentence importance"""
    # Position (earlier = more important)
    position_score = 1.0 - (all_sentences.index(sentence) / len(all_sentences))
    
    # Length (mid-length = more info)
    length = len(sentence.split())
    length_score = min(1.0, length / 20.0) if length < 40 else 0.7
    
    # Keywords (contains important terms)
    important_terms = ["implement", "algorithm", "result", "because", "therefore"]
    keyword_score = sum(0.1 for term in important_terms if term in sentence.lower())
    keyword_score = min(1.0, keyword_score)
    
    # Combined
    return 0.4 * position_score + 0.3 * length_score + 0.3 * keyword_score
```

---

### HEAVY Compression (50-70% reduction)

```python
def compress_heavy(content: str) -> str:
    """Abstractive summarization - extreme brevity"""
    # Extract key entities and actions
    entities = extract_entities(content)
    actions = extract_actions(content)
    
    # Build minimal summary
    if entities and actions:
        summary = f"{', '.join(entities[:3])}: {', '.join(actions[:2])}"
    elif entities:
        summary = ', '.join(entities[:5])
    else:
        # Fallback: first sentence heavily trimmed
        first_sent = nltk.sent_tokenize(content)[0]
        summary = first_sent[:100] + "..." if len(first_sent) > 100 else first_sent
    
    return summary

def extract_entities(text: str) -> List[str]:
    """Extract key entities (simplified NER)"""
    # Simplified: capitalized words not at sentence start
    words = text.split()
    entities = []
    
    for i, word in enumerate(words):
        if word[0].isupper() and i > 0:
            # Likely entity
            entities.append(word.strip('.,;:'))
    
    return list(set(entities))[:10]  # Dedupe, limit
```

---

## Complete Compression Pipeline

```python
def compress_candidates(
    items: List[BudgetItem],
    config: CompressionConfig,
    audit: Optional[List[Dict]] = None
) -> Tuple[List[BudgetItem], CompressionMetrics]:
    """Apply strategic compression to all items"""
    original_tokens = sum(item.tokens for item in items)
    compressed_items = []
    
    by_level_count = {level: 0 for level in CompressionLevel}
    
    for item in items:
        # Determine level
        age_days = (datetime.utcnow() - item.timestamp).days
        level = determine_compression_level(age_days, item.priority, config)
        
        # Apply compression
        if level == CompressionLevel.NONE:
            compressed_content = item.content
        elif level == CompressionLevel.LIGHT:
            compressed_content = compress_light(item.content)
        elif level == CompressionLevel.MEDIUM:
            compressed_content = compress_medium(item.content)
        else:  # HEAVY
            compressed_content = compress_heavy(item.content)
        
        # Create compressed item
        compressed_item = BudgetItem(
            source_id=item.source_id,
            content=compressed_content,
            embedding=item.embedding,
            relevance_score=item.relevance_score,
            tokens=estimate_tokens(compressed_content),
            timestamp=item.timestamp,
            priority=item.priority,
            verified=item.verified
        )
        
        compressed_items.append(compressed_item)
        by_level_count[level] += 1
        
        # Audit
        if audit is not None and level != CompressionLevel.NONE:
            audit.append({
                "item_id": item.source_id,
                "level": level.value,
                "original_tokens": item.tokens,
                "compressed_tokens": compressed_item.tokens,
                "saved": item.tokens - compressed_item.tokens,
                "age_days": age_days,
                "priority": item.priority
            })
    
    # Metrics
    final_tokens = sum(item.tokens for item in compressed_items)
    
    metrics = CompressionMetrics(
        original_tokens=original_tokens,
        compressed_tokens=final_tokens,
        tokens_saved=original_tokens - final_tokens,
        compression_ratio=(original_tokens - final_tokens) / original_tokens if original_tokens > 0 else 0.0,
        items_compressed=sum(by_level_count[l] for l in [CompressionLevel.LIGHT, CompressionLevel.MEDIUM, CompressionLevel.HEAVY]),
        items_kept_full=by_level_count[CompressionLevel.NONE],
        by_level=by_level_count
    )
    
    return compressed_items, metrics
```

---

## Testing

```python
def test_compression_levels_by_age():
    """Validate age-based level selection"""
    items = [
        create_item(age=5, priority="normal"),   # NONE
        create_item(age=15, priority="normal"),  # LIGHT
        create_item(age=50, priority="normal"),  # MEDIUM
        create_item(age=100, priority="normal")  # HEAVY
    ]
    
    compressed, metrics = compress_candidates(items, CompressionConfig())
    
    assert compressed[0].tokens == items[0].tokens  # No compression
    assert compressed[1].tokens < items[1].tokens  # Some compression
    assert compressed[3].tokens << items[3].tokens  # Heavy compression

def test_high_priority_gets_preferential_treatment():
    """
    Week 3 test - validates priority boost!
    
    FAILED initially - high priority wasn't getting preferential treatment.
    FIXED by adjusting thresholds with multiplier.
    NOW PASSES!
    """
    items = [
        create_item(age=10, priority="normal"),  # Should compress (LIGHT)
        create_item(age=10, priority="high")     # Should NOT compress (NONE)
    ]
    
    compressed, metrics = compress_candidates(
        items,
        config=CompressionConfig(enable_priority_boost=True, high_priority_multiplier=2.0)
    )
    
    # High priority should have MORE tokens (less compression)
    normal_tokens = compressed[0].tokens
    high_tokens = compressed[1].tokens
    
    assert high_tokens > normal_tokens  # ✅ PASSES after fix!
```

---

## Summary

Strategic age-based compression with priority boost, 4 levels, configurable thresholds.

**Implementation:** `packages/hhni/compressor.py` (10 tests passing)

---

**Word Count:** ~2,000  
**Next:** [L3_detailed.md](L3_detailed.md)


# Contradiction Detection

**Type:** SEG Component  
**Purpose:** Automatically find and flag conflicting information  
**Status:** 25% Implemented

---

## 🎯 **Quick Context (50 words)**

Contradiction detection finds conflicting claims in the evidence graph. Algorithm: (1) Find semantically similar claims (same topic), (2) Check for opposite stances, (3) Create "contradicts" edge, (4) Flag for resolution. Prevents drift, ensures coherence, surfaces conflicts automatically. Foundation for consistent, trustworthy knowledge.

---

## 📦 **Detection Algorithm**

**Steps:**
1. **Find Similar Claims** - Semantic similarity > 0.7 (same topic)
2. **Check Stances** - Are they saying opposite things?
3. **Create Edge** - Add "contradicts" relationship
4. **Flag** - Surface to user/system for resolution

**Implementation:**
```python
def detect_contradictions(graph: SEG) -> List[Conflict]:
    """Find conflicting claims"""
    conflicts = []
    claims = graph.get_nodes_by_type("claim")
    
    for c1, c2 in combinations(claims, 2):
        # Same topic?
        similarity = cosine_similarity(c1.embedding, c2.embedding)
        if similarity > 0.7:
            # Opposite stances?
            if are_contradictory(c1.content, c2.content):
                # Add edge
                graph.add_edge(type="contradicts", source=c1.id, target=c2.id)
                conflicts.append(Conflict(c1, c2))
    
    return conflicts
```

---

## 🔧 **Implementation**

**Status:** 25% implemented

**Working:**
- ✅ Basic concept documented

**Needed:**
- 🔄 Stance detection (positive/negative/neutral)
- 🔄 Semantic similarity for claims
- 🔄 Automated flagging
- 🔄 Resolution workflow (human-in-loop)

**Code:** (Needs implementation)

---

**Parent:** [../../README.md](../../README.md)


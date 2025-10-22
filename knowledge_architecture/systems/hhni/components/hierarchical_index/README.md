# Hierarchical Index - 6-Level Fractal Structure

**Component of:** HHNI  
**Type:** Core Component  
**Purpose:** Multi-resolution indexing (System→Subword)  
**Status:** ✅ Fully Implemented

---

## 🎯 **Quick Context (100 words)**

Hierarchical Index implements HHNI's fractal 6-level structure: System (corpus overview), Section (major divisions), Paragraph (content blocks), Sentence (atomic facts), Word (tokens), Subword (characters). Every atom indexed at all levels simultaneously. Enables multi-resolution queries: "Show me system overview" vs "Find this exact sentence." Parent-child relationships tracked. Dependency hashing for change impact. IDS (Index Depth Score) measures coverage. Critical for zoom-in/zoom-out navigation. Like Google Maps for knowledge—view at any scale.

---

## 📊 **Context Budget Guide**

**4k:** This README  
**8k:** [L1_overview.md](L1_overview.md) - All 6 levels explained  
**32k:** [L2_architecture.md](L2_architecture.md) - Implementation details  
**200k+:** L3-L5 + level-specific docs

---

## 📦 **The 6 Levels**

### **Level 1: System**
**Granularity:** Entire corpus  
**Example:** "Authentication system", "Payment processing"  
**Use Case:** "Give me everything about auth"  
**Index Size:** 1-10 entries per corpus

**Location:** [levels/system/](levels/system/)

---

### **Level 2: Section**
**Granularity:** Major divisions  
**Example:** "OAuth2 implementation", "Token validation"  
**Use Case:** "Show me OAuth2 components"  
**Index Size:** 10-100 entries per system

**Location:** [levels/section/](levels/section/)

---

### **Level 3: Paragraph**
**Granularity:** Content blocks  
**Example:** "Token expiration logic", "User role checking"  
**Use Case:** "Find token expiration details"  
**Index Size:** 100-1000 entries per section

**Location:** [levels/paragraph/](levels/paragraph/)

---

### **Level 4: Sentence**
**Granularity:** Atomic facts  
**Example:** "Tokens expire after 1 hour", "Admin role required"  
**Use Case:** "What's the exact expiration time?"  
**Index Size:** 1000-10000 entries per paragraph

**Location:** [levels/sentence/](levels/sentence/)

---

### **Level 5: Word**
**Granularity:** Token-level  
**Example:** "expire", "hour", "admin"  
**Use Case:** Fuzzy search, partial matching  
**Index Size:** 10000+ entries

**Location:** [levels/word/](levels/word/)

---

### **Level 6: Subword**
**Granularity:** Character/byte  
**Example:** "exp", "hou", "adm"  
**Use Case:** Typo tolerance, prefix matching  
**Index Size:** 100000+ entries

**Location:** [levels/subword/](levels/subword/)

---

## 🔧 **How It Works**

**Indexing (Bottom-Up):**
```
Content arrives
    ↓
Parse into sentences → Level 4 index
    ↓
Group into paragraphs → Level 3 index
    ↓
Group into sections → Level 2 index
    ↓
Entire system → Level 1 index
    ↓
Tokenize → Level 5 index
    ↓
Character n-grams → Level 6 index
```

**Retrieval (Top-Down):**
```
Query arrives
    ↓
Match at System level → Narrow scope
    ↓
Match at Section level → Narrow more
    ↓
Match at Paragraph level → Get content blocks
    ↓
Match at Sentence level → Precise facts
    ↓
(Word/Subword for fuzzy matching)
```

---

## 📊 **Index Structure**

**Each Level Has:**
```python
class IndexLevel:
    level: int                    # 1-6
    entries: List[IndexEntry]     # Indexed items
    embeddings: NDArray          # Vector representations
    parent_level: Optional[int]  # Level above (e.g., 3→2)
    child_level: Optional[int]   # Level below (e.g., 3→4)

class IndexEntry:
    id: str                      # Entry identifier
    content_summary: str         # Brief description
    embedding: List[float]       # Vector for this level
    parent_id: Optional[str]     # Parent in hierarchy
    child_ids: List[str]         # Children in hierarchy
    atom_refs: List[str]         # Atoms at this level
    depth_score: float          # IDS component
```

---

## 🔗 **Relationships**

**Hierarchical Index uses:**
- CMC atoms (content to index)
- Embeddings (semantic vectors)
- Dependency hashing (change tracking)

**Hierarchical Index enables:**
- Multi-resolution queries
- DVNS physics (elastic forces use structure)
- IDS calculation (depth score in RS formula)
- Blast radius (via dependency graph)

---

## 📈 **Metrics**

**IDS (Index Depth Score):**
```
IDS = Σ(coverage_at_level_i × weight_i) / Σ(weight_i)
```

**Measures:** How well content is indexed across all levels  
**Range:** 0.0-1.0 (higher = better coverage)

**Dependency Hash:**
- SHA-256 of all child IDs + content hashes
- Changes propagate up (child change → parent rehash)
- Enables impact preview

---

## 🔧 **Implementation**

**File:** `packages/hhni/hierarchical_index.py` (327 lines)  
**Tests:** 5 passing  
**Status:** ✅ Complete

**Key Functions:**
- `build_hierarchical_index()` - Construct all 6 levels
- `query_at_level()` - Retrieve at specific granularity
- `zoom_in()` / `zoom_out()` - Navigate hierarchy
- `compute_dependency_hash()` - Change impact
- `calculate_ids()` - Depth score

---

## 📚 **Detail Levels**

**L0:** This README  
**L1-L5:** Architecture docs (to create)

**Sub-components:**
- [levels/system/](levels/system/) - Level 1 indexing
- [levels/section/](levels/section/) - Level 2 indexing
- [levels/paragraph/](levels/paragraph/) - Level 3 indexing
- [levels/sentence/](levels/sentence/) - Level 4 indexing
- [levels/word/](levels/word/) - Level 5 indexing
- [levels/subword/](levels/subword/) - Level 6 indexing

---

## 🎯 **Key Concepts**

**Multi-Resolution:** Index at ALL levels simultaneously  
**Parent-Child:** Track hierarchical relationships  
**Dependency Hashing:** Detect change impact  
**IDS:** Measure index completeness  
**Zoom Navigation:** Move between abstraction levels

---

**Parent:** [../../README.md](../../README.md)  
**Siblings:** [../dvns/](../dvns/), [../retrieval/](../retrieval/)  
**Implementation:** `packages/hhni/hierarchical_index.py`  
**Status:** ✅ Production-ready, tested


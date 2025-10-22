# Query Engine

**Type:** SEG Component  
**Purpose:** Powerful graph queries (lineage, temporal, provenance, contradictions)  
**Status:** 35% Implemented

---

## 🎯 **Quick Context (50 words)**

Query engine provides four critical query types: Lineage (trace origins), Temporal (what was known when?), Provenance (who created this?), Contradiction (what conflicts?). Uses graph traversal, bitemporal indexing, and semantic search. Foundation for auditable, traceable, historically-aware AI reasoning.

---

## 📦 **Query Types**

### **1. Lineage Queries**
**Question:** "Where did this claim come from?"  
**Method:** Backward graph traversal  
**Example:**
```python
ancestors = seg.trace_lineage(
    claim_id="c123",
    direction="backward",
    max_depth=10
)
# Returns: [Source nodes, Derivation nodes, Parent claims]
```

### **2. Temporal Queries**
**Question:** "What was true at time T?"  
**Method:** Bitemporal indexing (VT + TT)  
**Example:**
```python
snapshot = seg.snapshot_at_time(
    timestamp="2025-10-15T12:00:00Z"
)
# Returns: All claims with VT covering 2025-10-15
```

### **3. Provenance Queries**
**Question:** "Who created this?"  
**Method:** Follow "witnesses" edges  
**Example:**
```python
chain = seg.get_provenance_chain(claim_id="c123")
# Returns: [VIF witness, APOE execution, Model ID, User]
```

### **4. Contradiction Queries**
**Question:** "What conflicts with this claim?"  
**Method:** Follow "contradicts" edges  
**Example:**
```python
conflicts = seg.find_contradictions(claim_id="c123")
# Returns: [All conflicting claims]
```

---

## 🔧 **Implementation**

**Status:** 35% implemented

**Working:**
- ✅ Basic graph traversal
- ✅ Simple queries

**Needed:**
- 🔄 Bitemporal query optimization
- 🔄 Graph query language (Cypher-like)
- 🔄 Performance indexing
- 🔄 Query caching

**Code:** `packages/seg/` (partial)

---

**Parent:** [../../README.md](../../README.md)


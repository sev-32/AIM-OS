# Pipelines - Data Flow Orchestration

**Component of:** CMC  
**Type:** Processing Component  
**Purpose:** Orchestrate write (ingest) and read (query) data flows  
**Status:** ✅ 75% Implemented (write operational, read integrated with HHNI)

---

## 🎯 **Quick Context (100 words)**

Pipelines orchestrate CMC data flows. Write Pipeline: ingest → atomize → enrich → index → gate → persist → snapshot (7 stages). Read Pipeline: query → HHNI lookup → DVNS optimize → deduplicate → resolve conflicts → compress → budget fit (7 stages). Each stage can fail independently with error handling. Instrumented with metrics (latency, throughput). Gates enforce quality/policy. HHNI integration for intelligent retrieval. DVNS physics for "lost in middle" prevention. Critical for CMC performance and correctness.

**[More detail below ↓]**

---

## 📊 **Context Budget Guide**

**4k:** This README  
**8k:** [L1_overview.md](L1_overview.md)  
**32k:** [L2_architecture.md](L2_architecture.md)  
**200k+:** L3-L5 + stage-specific docs

---

## 📦 **The Two Pipelines**

### **Write Pipeline** (Input → Storage)

**Flow:**
```
Input Context
    ↓
1. Validate      (check format, modality)
    ↓
2. Atomize       (split into atomic units)
    ↓
3. Enrich        (embeddings, QS, TPV)
    ↓
4. Index         (assign HHNI paths)
    ↓
5. Gate          (quality/policy checks)
    ↓
6. Persist       (save to all stores)
    ↓
7. Snapshot      (create immutable bundle)
    ↓
Snapshot ID returned
```

**Performance:** p95 < 200ms (target met)  
**Location:** [write_pipeline/](write_pipeline/)

---

### **Read Pipeline** (Query → Context)

**Flow:**
```
Query
    ↓
1. Query         (parse + prepare)
    ↓
2. HHNI Lookup   (hierarchical retrieval)
    ↓
3. DVNS Optimize (physics-guided layout)
    ↓
4. Deduplicate   (remove redundant)
    ↓
5. Resolve       (handle contradictions)
    ↓
6. Compress      (age-based strategic)
    ↓
7. Budget Fit    (respect token limits)
    ↓
Optimal Context
```

**Performance:** p95 < 100ms (target met)  
**Location:** [read_pipeline/](read_pipeline/)

---

## 🔧 **Write Pipeline Details**

### **Stage 1: Validate**
- Check modality valid
- Content non-empty
- Tags properly formatted

### **Stage 2: Atomize**
- Text: split paragraphs/sentences
- Code: parse functions/classes
- Events: single atom

### **Stage 3: Enrich**
- Generate embeddings (batch)
- Calculate QS (quality score)
- Assign TPV (priority vector)

### **Stage 4: Index**
- Call HHNI service
- Assign hierarchical path
- Compute dependency hash

### **Stage 5: Gate**
- Confidence threshold (Band C reject)
- Content validation
- Embedding present
- Policy checks

### **Stage 6: Persist**
- Metadata store (SQLite)
- Vector store (Faiss)
- Object store (if >1KB)
- Graph store (SEG edges)

### **Stage 7: Snapshot**
- Compute content hash
- Create snapshot record
- Update atom snapshot_id
- Return snapshot ID

**Location:** [write_pipeline/stages/](write_pipeline/stages/)

---

## 🔧 **Read Pipeline Details**

### **Stage 1: Query Parsing**
- Extract intent
- Prepare filters
- Set budget

### **Stage 2: HHNI Lookup**
- Semantic search (KNN)
- Hierarchical filtering
- Get top-K candidates (100)

### **Stage 3: DVNS Optimize**
- Apply 4 physics forces
- Optimize spatial layout
- Improve retrieval quality (+15%)

### **Stage 4: Deduplicate**
- Semantic similarity detection
- Content hash comparison
- Cluster and merge

### **Stage 5: Resolve Conflicts**
- Detect contradictions
- Cluster by stance
- Select best item
- Suppress others

### **Stage 6: Compress**
- Age-based compression levels
- Priority boost for important
- Token savings

### **Stage 7: Budget Fit**
- Estimate tokens
- Select top items within budget
- Preserve diversity

**Location:** [read_pipeline/stages/](read_pipeline/stages/)

---

## 📊 **Performance Metrics**

**Write Pipeline:**
- p50: 40ms
- p95: 150ms ✅ (target: <200ms)
- p99: 300ms

**Bottleneck:** Embedding generation (30-50ms)

**Read Pipeline:**
- p50: 20ms
- p95: 80ms ✅ (target: <100ms)
- p99: 150ms

**Bottleneck:** DVNS physics (large candidate sets)

**Optimization:** Batch processing, caching, async

---

## 🔗 **Relationships**

**Pipelines use:**
- Storage layers (all four)
- HHNI service (indexing, retrieval)
- DVNS physics (optimization)
- Embedding service (vectors)
- Quality gates (validation)

**Pipelines enable:**
- CMC write operations
- CMC read operations
- Snapshot creation
- HHNI integration

---

## 📚 **Detail Levels**

**L0:** This README  
**L1-L5:** Architecture docs

**Sub-components:**
- [write_pipeline/](write_pipeline/)
  - [stages/validate/](write_pipeline/stages/validate/)
  - [stages/atomize/](write_pipeline/stages/atomize/)
  - [stages/enrich/](write_pipeline/stages/enrich/)
  - [stages/index/](write_pipeline/stages/index/)
  - [stages/gate/](write_pipeline/stages/gate/)
  - [stages/persist/](write_pipeline/stages/persist/)
  - [stages/snapshot/](write_pipeline/stages/snapshot/)
- [read_pipeline/](read_pipeline/)
  - [stages/query/](read_pipeline/stages/query/)
  - [stages/hhni_lookup/](read_pipeline/stages/hhni_lookup/)
  - [stages/dvns_optimize/](read_pipeline/stages/dvns_optimize/)
  - [stages/deduplicate/](read_pipeline/stages/deduplicate/)
  - [stages/resolve/](read_pipeline/stages/resolve/)
  - [stages/compress/](read_pipeline/stages/compress/)
  - [stages/budget_fit/](read_pipeline/stages/budget_fit/)

---

**Parent:** [../../README.md](../../README.md)  
**Implementation:** `packages/cmc_service/memory_store.py`, `packages/hhni/retrieval.py`  
**Tests:** 10+ passing, integration validated  
**Status:** Core functionality complete, optimizations ongoing


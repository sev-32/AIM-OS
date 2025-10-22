# Pipelines L1: Data Flow Overview

**Detail Level:** 1 of 5 (500 words)  
**Context Budget:** ~8k tokens  
**Purpose:** Understand write and read pipelines

---

## The Two Pipelines

CMC has two data flow pipelines: Write (ingest context → storage) and Read (query → optimized context). Write has 7 stages, takes ~150ms p95. Read has 7 stages, takes ~80ms p95. Both instrumented with metrics, gates, error handling. Write creates atoms and snapshots. Read integrates HHNI/DVNS for intelligent retrieval. Critical for CMC performance and correctness.

## Write Pipeline (Input → Storage)

**Flow:** Ingest → Atomize → Enrich → Index → Gate → Persist → Snapshot

### Stage 1: Validate
**Purpose:** Check input validity  
**Checks:** Modality valid, content non-empty, tags formatted  
**Latency:** <1ms  
**Fail:** Reject with error message

### Stage 2: Atomize
**Purpose:** Split content into atomic units  
**Logic:**
- Text: Paragraphs or sentences
- Code: Functions or classes  
- Events: Single atom
**Latency:** <5ms  
**Output:** List of atom candidates

### Stage 3: Enrich
**Purpose:** Add embeddings, calculate QS, assign TPV  
**Operations:**
- Generate embeddings (batch)
- Calculate quality scores
- Assign priority vectors
**Latency:** ~30-50ms (bottleneck: embeddings)  
**Output:** Enriched atoms

### Stage 4: Index
**Purpose:** Assign HHNI hierarchical paths  
**Integration:** Calls HHNI service  
**Latency:** <10ms  
**Output:** Indexed atoms

### Stage 5: Gate
**Purpose:** Quality/policy enforcement  
**Checks:**
- Confidence threshold (Band C rejected)
- Content validation
- Embedding present
- Policy compliance
**Latency:** <5ms  
**Output:** Passed atoms, failed atoms

### Stage 6: Persist
**Purpose:** Write to all storage tiers  
**Operations:**
- Metadata store (SQLite)
- Vector store (Faiss)
- Object store (if >1KB)
- Graph store (SEG edges)
**Latency:** <20ms  
**Output:** Persisted atoms

### Stage 7: Snapshot
**Purpose:** Create immutable bundle  
**Operations:**
- Compute content hash
- Create snapshot record
- Update atom snapshot_ids
**Latency:** <5ms  
**Output:** Snapshot ID

**Total:** p95 ~150ms ✅ (target: <200ms)

---

## Read Pipeline (Query → Context)

**Flow:** Query → HHNI → DVNS → Dedup → Resolve → Compress → Budget

### Stage 1: Query Parsing
**Purpose:** Prepare query  
**Operations:** Extract intent, prepare filters, set budget  
**Latency:** <1ms

### Stage 2: HHNI Lookup
**Purpose:** Hierarchical semantic retrieval  
**Method:** KNN in vector space (top-100)  
**Latency:** ~10ms  
**Output:** Candidate atoms

### Stage 3: DVNS Optimize
**Purpose:** Physics-guided layout optimization  
**Method:** 4 forces, Velocity-Verlet integration  
**Latency:** ~40-50ms  
**Output:** Optimized candidates (+15% quality)

### Stage 4: Deduplicate
**Purpose:** Remove redundant items  
**Method:** Semantic clustering (threshold 0.85)  
**Latency:** <5ms  
**Output:** 20-30% fewer items

### Stage 5: Resolve Conflicts
**Purpose:** Handle contradictions  
**Method:** Stance clustering, best selection  
**Latency:** <10ms  
**Output:** Coherent, contradiction-free

### Stage 6: Compress
**Purpose:** Age-based token savings  
**Method:** 4 compression levels (NONE/LIGHT/MEDIUM/HEAVY)  
**Latency:** <5ms  
**Output:** 15-25% token savings

### Stage 7: Budget Fit
**Purpose:** Respect token limits  
**Method:** Select top items within budget  
**Latency:** <5ms  
**Output:** Final context (never exceeds budget)

**Total:** p95 ~80ms ✅ (target: <100ms)

---

## Pipeline Configuration

```python
@dataclass
class WriteConfig:
    enable_validation: bool = True
    atomization_strategy: str = "auto"  # or "sentences", "paragraphs"
    enable_gates: bool = True
    gate_thresholds: Dict[str, float] = ...
    embedding_batch_size: int = 32

@dataclass
class ReadConfig:
    enable_dvns: bool = True
    enable_dedup: bool = True
    enable_conflicts: bool = True
    enable_compression: bool = True
    token_budget: int = 8000
    preserve_diversity: bool = True
```

**Highly configurable:** Enable/disable stages, tune thresholds

---

## Error Handling

**Each stage can fail independently:**

```python
try:
    atoms = atomize(content)
except AtomizationError as e:
    log_error("Atomization failed", error=e)
    return ErrorResult(stage="atomize", error=str(e))

try:
    enriched = enrich(atoms)
except EnrichmentError as e:
    log_error("Enrichment failed", error=e)
    # Partial success: keep unenriched atoms
    enriched = atoms  # Fallback
```

**Graceful degradation:** Later stages can proceed even if earlier ones partially fail

---

## Metrics & Observability

**Write Pipeline Metrics:**
```python
@dataclass
class WriteMetrics:
    total_latency_ms: float
    stage_latencies: Dict[str, float]  # Per-stage timing
    atoms_created: int
    atoms_failed_gates: int
    snapshot_id: str
```

**Read Pipeline Metrics:**
```python
@dataclass
class ReadMetrics:
    total_latency_ms: float
    stage_latencies: Dict[str, float]
    candidates_retrieved: int
    duplicates_removed: int
    conflicts_resolved: int
    tokens_saved_compression: int
    final_items_count: int
    final_tokens: int
```

**Enables:**
- Performance monitoring
- Bottleneck identification
- Quality tracking
- Debugging

---

## Integration

**Write Pipeline uses:**
- Embedding Service (enrichment)
- HHNI Service (indexing)
- All storage tiers (persistence)
- Quality gates (validation)

**Read Pipeline uses:**
- Vector Store (KNN search)
- HHNI components (DVNS, dedup, conflicts, compression)
- Budget Manager (token limiting)

**Pipelines enable:**
- CMC write operations
- CMC read operations
- Snapshot creation
- Optimal context retrieval

---

## Performance

**Write:**
- p50: 40ms
- p95: 150ms ✅
- p99: 300ms

**Read:**
- p50: 20ms
- p95: 80ms ✅
- p99: 150ms

**Bottlenecks:**
- Write: Embedding generation (30-50ms)
- Read: DVNS physics (40-50ms)

**Both meet targets!** ✅

---

## Summary

Pipelines provide:
- ✅ Complete data flows (write & read)
- ✅ 7-stage architecture (each validated)
- ✅ Error handling (graceful degradation)
- ✅ Metrics & observability
- ✅ Performance targets met
- ✅ HHNI integration (intelligent retrieval)
- ✅ Quality gates (enforce standards)

**Core CMC functionality!** ✅

---

**Word Count:** ~500  
**Next:** [L2_architecture.md](L2_architecture.md)  
**Parent:** [README.md](README.md)  
**Implementation:** `packages/cmc_service/memory_store.py`, `packages/hhni/retrieval.py`


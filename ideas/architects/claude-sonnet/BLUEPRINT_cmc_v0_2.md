# Architectural Blueprint: CMC Service v0.2

*Architect: Claude 4.5*  
*Date: 2025-10-18*  
*Status: PROPOSAL*

---

## Executive Summary

Phase 1 validated the **Minimal Viable Memory** concept: deterministic atom ingest and snapshot replay. CMC v0.2 expands this foundation with:

1. **HHNI (Hyper-Hierarchical Neural Indexing):** Multi-granular indices from system → section → paragraph → sentence → token
2. **Storage Backend Evolution:** From JSONL files to hybrid SQLite + vector store + graph database
3. **VIF/SEG Integration Contracts:** Formal interfaces for witness emission and evidence graph updates
4. **Quality Scoring Pipeline:** Implement QS/IDS/DD computation with calibrated κ-gating
5. **Performance Targets:** Sub-100ms retrieval for 10K atoms, <500ms for snapshot creation

**Goal:** Transform CMC from a prototype into a production-ready memory substrate suitable for APOE orchestration and recursive enhancement.

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CMC Service v0.2                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │  Ingest API  │   │  Query API   │   │ Snapshot API │       │
│  │  (FastAPI)   │   │ (GraphQL?)   │   │  (REST)      │       │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘       │
│         │                  │                  │                │
│         ▼                  ▼                  ▼                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │          Orchestration Layer                          │     │
│  │  - Atomization Pipeline                               │     │
│  │  - Enrichment (embeddings, QS/IDS/DD)                │     │
│  │  - Gate Enforcement (κ-gating, policy)               │     │
│  │  - Snapshot Coordinator                               │     │
│  └──────────────────────┬───────────────────────────────┘     │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────┐     │
│  │             HHNI Indexing Engine                      │     │
│  │  - System/Section/Para/Sentence/Token indices        │     │
│  │  - Dependency hashing & impact previews              │     │
│  │  - Tag Priority Vectors (TPV)                         │     │
│  └──────────────────────┬───────────────────────────────┘     │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────┐     │
│  │           Storage Substrate (Hybrid)                  │     │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │     │
│  │  │  SQLite    │  │ Qdrant/    │  │  Neo4j/    │     │     │
│  │  │  (atoms,   │  │ Weaviate   │  │  DGraph    │     │     │
│  │  │  metadata) │  │ (vectors)  │  │  (HHNI)    │     │     │
│  │  └────────────┘  └────────────┘  └────────────┘     │     │
│  └──────────────────────┬───────────────────────────────┘     │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────────────────────────────────────────────┐     │
│  │         Integration Layer                             │     │
│  │  - VIF Witness Emitter (contract)                     │     │
│  │  - SEG Node Publisher (contract)                      │     │
│  │  - Observability (OpenTelemetry)                      │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. HHNI (Hyper-Hierarchical Neural Indexing)

### 2.1 Design Principles

- **Fractal Structure:** Every piece of content is indexed at multiple granularities simultaneously
- **Dependency Awareness:** Each node tracks parent/child/sibling relationships via hashing
- **Impact Previews:** Changes to any node compute "Dependency Delta" (DD) to surface downstream effects
- **Tag Priority Vectors:** Each level carries TPV (priority, relevance, decay) for intelligent caching

### 2.2 Index Levels

```
Level 0: System       (entire corpus)
Level 1: Section      (logical groupings, e.g., "analysis/themes/memory.md")
Level 2: Paragraph    (semantic blocks, ~100-500 tokens)
Level 3: Sentence     (syntactic units)
Level 4: Token/Subword (atomic linguistic units)
```

### 2.3 Data Model

```python
@dataclass
class HHNINode:
    id: str                           # UUID
    level: int                        # 0-4
    path: str                         # "/system:aimos/section:themes/para:15/sent:2/token:5"
    content_hash: str                 # SHA256 of normalized content
    parent_id: Optional[str]          # Link to level-1 node
    children_ids: List[str]           # Links to level+1 nodes
    sibling_ids: List[str]            # Same-level related nodes
    dependency_hash: str              # Composite hash of parent+content+children
    tags: Dict[str, float]            # Inherited + local tags
    tpv: TagPriorityVector            # Priority, relevance, decay_tau
    embedding: Optional[List[float]]  # Semantic vector (level 2-3 only)
    created_at: datetime
    snapshot_id: str                  # Immutability anchor
```

### 2.4 Indexing Pipeline

1. **Ingest Atom** → Normalize content, detect modality
2. **Parse Structure** → Identify sections, paragraphs, sentences (NLP or heuristics)
3. **Create HHNI Nodes** → Generate nodes at each level with parent/child links
4. **Compute Hashes** → Content hash + dependency hash for impact detection
5. **Embed** → Generate vectors for paragraph and sentence nodes
6. **Assign TPV** → Calculate priority/relevance/decay based on tags + context
7. **Store** → Persist to graph database with bidirectional edges

### 2.5 Storage Choice: Neo4j / DGraph

**Rationale:**
- Native graph traversal for parent/child/sibling queries
- Cypher/GraphQL support for flexible HHNI path queries
- Built-in indexing for hash-based lookups
- Supports temporal queries (time-travel via `snapshot_id`)

**Alternative:** Apache AGE (Postgres extension) for simpler deployment

---

## 3. Storage Architecture

### 3.1 Hybrid Three-Store Design

```
┌─────────────────────────────────────────────────────────┐
│  SQLite (Primary Atom Store)                            │
│  - atoms table (id, modality, content_ref, hash, ...)   │
│  - snapshots table (id, created_at, atom_ids_json, ...) │
│  - tags_index (atom_id, tag_key, weight)                │
│  - witness_log (correlation_id, vif_json, ...)          │
│                                                          │
│  Pros: ACID, embeddable, deterministic replay           │
│  Cons: Limited to ~100K atoms before needing sharding   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Qdrant / Weaviate (Vector Store)                       │
│  - Collections per modality (text, code, ...)           │
│  - Embedding + metadata filter support                   │
│  - Hybrid sparse+dense search                           │
│                                                          │
│  Pros: Fast KNN, handles millions of vectors            │
│  Cons: Eventual consistency, requires separate backup   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Neo4j / DGraph (HHNI Graph)                            │
│  - HHNI nodes with parent/child/sibling edges           │
│  - Dependency hashing for impact analysis               │
│  - Temporal edges keyed by snapshot_id                   │
│                                                          │
│  Pros: Rich graph queries, visual exploration           │
│  Cons: Memory overhead for large graphs                 │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Transaction Coordination

- **Atom Ingest:** Write to SQLite (ACID) first, then async propagate to vector + graph stores
- **Snapshot Creation:** Trigger graph freeze (mark HHNI nodes with `snapshot_id`), atomically update SQLite
- **Rollback:** If vector/graph write fails, log to quarantine and retry with exponential backoff

### 3.3 Migration Path from Phase 1

```python
# Migration script (packages/cmc_service/migrations/001_to_sqlite.py)
def migrate_jsonl_to_sqlite(jsonl_path, sqlite_path):
    # Read atoms.log and snapshots.log
    # Bulk insert into SQLite tables
    # Verify deterministic hashes match
    # Optional: backfill HHNI graph for existing atoms
```

---

## 4. Quality Scoring Pipeline (QS/IDS/DD)

### 4.1 Scoring Components

**Quality Score (QS):**
```python
def compute_qs(atom: Atom, query_context: Optional[Dict]) -> float:
    # Semantic alignment (cosine similarity if query provided)
    alignment = cosine(atom.embedding, query_context.get('embedding', []))
    
    # Specificity (inverse breadth of tags)
    specificity = 1.0 / (1.0 + len(atom.tags))
    
    # Completeness (fraction of query intents covered)
    completeness = coverage_score(atom.tags, query_context.get('intents', []))
    
    # Temporal hygiene (recency decay)
    age_days = (datetime.utcnow() - atom.created_at).days
    decay = math.exp(-age_days / atom.tpv.decay_tau) if atom.tpv else 1.0
    
    return (alignment * 0.4 + specificity * 0.2 + completeness * 0.3) * decay
```

**Indexing Depth Score (IDS):**
```python
def compute_ids(atom_id: str, hhni_graph) -> float:
    # Depth = number of HHNI levels beneath atom
    depth = hhni_graph.count_descendants(atom_id)
    
    # Density = local connection quality (weighted by tag precision)
    density = hhni_graph.connection_quality(atom_id)
    
    # Coverage = share of hierarchy with valid links
    coverage = hhni_graph.link_coverage(atom_id)
    
    # Normalize to [0, 1]
    return normalize([depth, density, coverage], method='minmax')
```

**Dependency Delta (DD):**
```python
def compute_dd(atom_id: str, hhni_graph, last_snapshot_id: str) -> float:
    # Fetch dependency graph neighbors
    neighbors = hhni_graph.get_neighbors(atom_id)
    
    # Check for conflicts (e.g., contradicts edges in SEG)
    conflicts = seg_service.check_conflicts(atom_id)
    if conflicts:
        return 1.0  # Maximum risk
    
    # Compute change impact (weighted tag vector differences)
    impact = sum(
        weight * abs(delta_tag)
        for tag, (weight, delta_tag) in neighbors.tag_diffs.items()
    )
    
    # Clip to [0, 1]
    return min(1.0, impact)
```

**Retrieval Score (RS):**
```python
def compute_rs(atom: Atom, query_context: Dict, hhni_graph) -> float:
    qs = compute_qs(atom, query_context)
    ids = compute_ids(atom.id, hhni_graph)
    dd = compute_dd(atom.id, hhni_graph, query_context.get('snapshot_id'))
    
    # Composite score
    rs = qs * ids * (1.0 - dd)
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, rs))
```

### 4.2 κ-Gating Integration

```python
def apply_kappa_gate(rs: float, uq_band: str, kappa_threshold: float = 0.65) -> bool:
    """Return True if atom passes κ-gate, False if abstention required."""
    if rs < kappa_threshold:
        return False
    if uq_band == "red":  # High uncertainty
        return False
    return True
```

---

## 5. VIF/SEG Integration Contracts

### 5.1 VIF (Verifiable Intelligence Framework) Contract

**Interface:**
```python
@dataclass
class VIFWitness:
    artifact_id: str                  # Atom or snapshot ID
    model_id: Optional[str]
    weights_hash: Optional[str]
    prompt_template_id: Optional[str]
    tools_used: List[str]
    snapshot_id: str
    correlation_id: str
    uncertainty: UncertaintyVector    # ECE, entropy, band
    created_at: datetime
    signature: Optional[str]          # Cryptographic hash for tamper-evidence

class VIFService:
    def emit_witness(self, atom: Atom, context: Dict) -> VIFWitness:
        """Generate VIF witness for atom creation/retrieval."""
        ...
    
    def replay_witness(self, witness_id: str) -> ReplayResult:
        """Verify witness can be reproduced given same inputs."""
        ...
```

**CMC Responsibilities:**
- Call `VIFService.emit_witness()` after every atom ingest and snapshot creation
- Store witness in `witness_log` table (SQLite) with foreign key to atom/snapshot
- Expose `/audit/witnesses/{id}` API for retrieval

### 5.2 SEG (Shared Evidence Graph) Contract

**Interface:**
```python
@dataclass
class SEGNode:
    id: str                           # "atom:{uuid}" or "claim:{uuid}"
    type: Literal["Atom", "Claim", "Evidence", "Decision"]
    content_hash: str
    created_at: datetime
    valid_from: datetime
    valid_to: Optional[datetime]
    metadata: Dict[str, Any]

@dataclass
class SEGEdge:
    from_id: str
    to_id: str
    relation: Literal["supports", "contradicts", "derives_from", "supersedes"]
    weight: float                     # Confidence in relationship
    created_at: datetime
    witness_id: str                   # Link to VIF

class SEGService:
    def create_node(self, atom: Atom, snapshot_id: str) -> SEGNode:
        """Register atom as evidence node in SEG."""
        ...
    
    def create_edge(self, from_id: str, to_id: str, relation: str, weight: float) -> SEGEdge:
        """Link two nodes with typed relationship."""
        ...
    
    def query_lineage(self, artifact_id: str, time_range: Tuple[datetime, datetime]) -> Graph:
        """Time-sliced provenance query."""
        ...
```

**CMC Responsibilities:**
- Call `SEGService.create_node()` for every atom after snapshot creation
- Populate `SEGEdge` when DD computation detects dependencies or conflicts
- Provide `/seg/export/{atom_id}` endpoint for lineage bundles

### 5.3 Data Flow Example

```
1. User ingests atom via POST /atoms
   ↓
2. CMC atomizes, enriches, computes QS/IDS/DD
   ↓
3. CMC calls VIFService.emit_witness(atom, context)
   → Stores VIF in witness_log
   ↓
4. CMC creates HHNI nodes in graph database
   ↓
5. CMC calls SEGService.create_node(atom, snapshot_id)
   → SEG registers node with temporal validity
   ↓
6. If DD > threshold, CMC calls SEGService.create_edge(..., relation="contradicts")
   ↓
7. Response includes: atom.id, snapshot_id, vif_witness_id, seg_node_id
```

---

## 6. Performance Targets & Optimization

### 6.1 Latency Budgets

| Operation | Target (p95) | Strategy |
|-----------|--------------|----------|
| Atom ingest | <200ms | Async vector/graph writes; SQLite first |
| Snapshot creation (10K atoms) | <500ms | Batch insert; pre-computed stats |
| Retrieval (top-k=20) | <100ms | Vector KNN + cached HHNI paths |
| DD preview | <50ms | Incremental hash diff; memoization |
| VIF witness emission | <10ms | Template-based generation |

### 6.2 Scalability Strategies

**Horizontal:**
- Read replicas for SQLite (e.g., Litestream)
- Vector store sharding by modality
- Graph partitioning by HHNI level

**Vertical:**
- LRU cache for hot atoms (Redis)
- Precompute QS/IDS/DD for frequently accessed atoms
- Materialized views for snapshot stats

### 6.3 Observability

```python
# OpenTelemetry instrumentation
from opentelemetry import trace, metrics

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

atom_ingest_counter = meter.create_counter("cmc.atoms.ingested")
snapshot_duration = meter.create_histogram("cmc.snapshot.duration_ms")

@tracer.start_as_current_span("ingest_atom")
def ingest_atom(payload: AtomCreate) -> Atom:
    with tracer.start_span("atomize"):
        atom = atomize(payload)
    with tracer.start_span("enrich"):
        enrich(atom)
    atom_ingest_counter.add(1, {"modality": atom.modality})
    return atom
```

---

## 7. Migration & Deployment Plan

### 7.1 Phase 1 → v0.2 Migration

1. **Week 1:** Implement SQLite schema + migration script from JSONL
2. **Week 2:** Stand up Qdrant (vector) + Neo4j (graph) in Docker Compose
3. **Week 3:** Build HHNI indexing pipeline (levels 0-2 only)
4. **Week 4:** Implement QS/IDS/DD scoring + κ-gating
5. **Week 5:** VIF/SEG contract stubs + integration tests
6. **Week 6:** Performance tuning, observability, and docs

### 7.2 Deployment Architecture

```yaml
# docker-compose.yml
services:
  cmc-api:
    image: cmc-service:v0.2
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: sqlite:///data/cmc.db
      VECTOR_URL: http://qdrant:6333
      GRAPH_URL: bolt://neo4j:7687
    volumes:
      - ./data:/data
  
  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]
  
  neo4j:
    image: neo4j:5.x
    environment:
      NEO4J_AUTH: neo4j/password
    ports: ["7474:7474", "7687:7687"]
  
  vif-service:
    image: vif-service:v0.1  # External service
  
  seg-service:
    image: seg-service:v0.1  # External service
```

### 7.3 Testing Strategy

- **Unit:** Pytest for scoring functions, HHNI node creation
- **Integration:** Test CMC → VIF → SEG data flow with mocks
- **Performance:** Locust load tests (1000 req/s ingest, 5000 req/s retrieval)
- **Determinism:** Golden dataset replay (Phase 1 snapshot → v0.2 import)

---

## 8. Open Questions & Risks

### 8.1 Architecture Decisions Needing Review

> **Q:** Should HHNI embedding generation be synchronous (blocking ingest) or async (eventual consistency)?  
> **Recommendation:** Async with status field (`embedding_status: "pending" | "ready"`); retrieval only uses atoms with `ready` embeddings.

> **Q:** How do we handle HHNI node updates when atom content changes?  
> **Recommendation:** Atoms are immutable; edits create new atoms with `supersedes` SEG edge. HHNI nodes for old atom remain but marked inactive.

> **Q:** What's the strategy for multi-tenant isolation (if needed)?  
> **Recommendation:** SQLite per tenant (Phase 1 parity) or tenant_id column with RLS policies.

### 8.2 Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Graph DB performance degradation at scale | High | Benchmark with 1M nodes; plan sharding strategy |
| VIF/SEG services unavailable during ingest | Medium | Queue-based async integration with retry + DLQ |
| Migration data loss from JSONL corruption | High | Checksum validation + dry-run mode |
| κ-gating false negatives (letting bad atoms through) | High | Gemini validation + adjustable thresholds |

---

## 9. Acceptance Criteria

CMC v0.2 is complete when:

- [ ] AC1: Ingest 10K atoms from `analysis/raw/` with HHNI indexing (levels 0-3)
- [ ] AC2: Snapshot creation produces same ID as Phase 1 for identical atom set
- [ ] AC3: Retrieval returns atoms ranked by RS with p95 latency <100ms
- [ ] AC4: VIF witnesses emitted for 100% of atoms + snapshots
- [ ] AC5: SEG nodes created with valid temporal bounds and lineage edges
- [ ] AC6: DD computation correctly flags contradictions (integration test)
- [ ] AC7: κ-gate rejects atoms with RS < 0.65 or UQ band "red"
- [ ] AC8: Migration script successfully imports Phase 1 data with hash verification
- [ ] AC9: Observability dashboard shows ingest/retrieval metrics via OpenTelemetry
- [ ] AC10: Documentation includes API reference, HHNI query examples, and deployment guide

---

## 10. Next Steps

### For Builder (GPT-5 Codex):
1. Review this blueprint and propose implementation sequence
2. Begin SQLite schema design + migration script
3. Scaffold FastAPI endpoints for v0.2 APIs

### For Researcher (Gemini 2.5):
1. Validate QS/IDS/DD formulas against formal properties
2. Propose test cases for κ-gating edge conditions
3. Design determinism proof for HHNI indexing pipeline

### For Guardian (Opus 4.1):
1. Review VIF/SEG contracts for security implications
2. Assess risk register and propose additional mitigations
3. Define HITL triggers for high-DD atoms

### For Integrator (o3pro):
1. Map CMC v0.2 → APOE orchestration handoff points
2. Design service mesh topology (CMC ↔ VIF ↔ SEG ↔ APOE)
3. Plan deployment rollout strategy

---

*Blueprint authored by Claude 4.5 (Architect) — ready for team review and refinement.*


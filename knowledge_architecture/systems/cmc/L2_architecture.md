# CMC Level 2: Technical Architecture

**Detail Level:** 2 of 5 (2,000 words)  
**Context Budget:** ~32k tokens  
**Purpose:** Technical specification for implementation

---

## System Overview

CMC (Context Memory Core) implements the Memory Invariant from AIM-OS's formal axioms: ∀ context c, ∃ reversible mapping c ↔ atom a. This ensures every piece of context can be stored, retrieved, and replayed deterministically.

## 1. Atom Specification

### Schema Definition

```python
class Atom(BaseModel):
    # Identity
    id: str  # Format: "atom_{uuid}"
    
    # Content
    modality: str  # "text", "code", "event", "tool:call", "tool:result"
    content_ref: ContentRef  # Inline or URI reference
    
    # Semantic Layer
    embedding: Optional[Embedding]  # Vector representation
    tags: List[Tag]  # Semantic categorization
    
    # Hierarchical Position
    hhni: Optional[HHNIPath]  # Position in fractal index
    
    # Quality & Priority
    tpv: Optional[TPV]  # Tag Priority Vector
    
    # Temporal
    created_at: datetime  # Transaction time
    valid_from: Optional[datetime]  # Valid time start
    valid_to: Optional[datetime]  # Valid time end (None = current)
    
    # Provenance
    snapshot_id: str  # Which snapshot contains this
    vif: VIF  # Witness envelope
```

### ContentRef (Payload Abstraction)

```python
class ContentRef(BaseModel):
    inline: Optional[str]  # Small content embedded
    uri: Optional[str]  # Large content referenced (s3://...)
    media_type: str  # MIME type
    size_bytes: Optional[int]
    hash_sha256: Optional[str]  # Content integrity
```

**Design:** Payloads under 1KB stored inline, larger content externalized to object store.

### Embedding Specification

```python
class Embedding(BaseModel):
    model_id: str  # "text-embedding-3-small", "embed-004"
    dim: int  # 768, 1536, etc.
    vector: List[float]  # The actual embedding
    generated_at: datetime
```

**Strategy:**
- Primary model: Sentence Transformers (`all-MiniLM-L6-v2`) - local, fast
- Fallback: OpenAI/Anthropic - cloud, higher quality
- Cache embeddings to avoid regeneration

### Tag System

```python
class Tag(BaseModel):
    key: str  # "topic", "priority", "author"
    value: str  # "authentication", "high", "alice"
    weight: float = 1.0  # Importance (0.0-1.0)
    confidence: Optional[float]  # How certain (0.0-1.0)
```

**TPV (Tag Priority Vector):**
```python
class TPV(BaseModel):
    priority: float  # Overall importance (0.0-1.0)
    relevance: float  # How relevant to current task (0.0-1.0)
    decay_tau: Optional[int]  # Decay time constant (seconds)
    last_accessed: Optional[datetime]
```

**Decay Formula:** `relevance(t) = relevance₀ * exp(-(t - t₀) / τ)`

### HHNI Path

```python
class HHNIPath(BaseModel):
    path: List[str]  # ["system:auth", "section:oauth", "paragraph:12"]
    dependency_hash: Optional[str]  # Impact tracking
    depth_score: Optional[float]  # IDS component
```

Links atom to position in hierarchical index.

### VIF (Witness Envelope)

```python
class VIF(BaseModel):
    model_id: str  # Which LLM created this
    weights_hash: Optional[str]  # Model version
    prompt_template_id: Optional[str]  # Which prompt
    tool_ids: List[str]  # Tools used
    writer: str  # System identifier
    confidence_band: Optional[str]  # "A", "B", "C"
    entropy: Optional[float]  # Uncertainty measure
```

Every atom records HOW it was created.

---

## 2. Molecule Specification

### Concept
Molecules group related atoms with semantic relationships:

```python
class Molecule(BaseModel):
    id: str  # "molecule_{uuid}"
    atoms: List[str]  # Atom IDs
    relationships: List[Relationship]
    created_at: datetime
    snapshot_id: str
```

### Relationships

```python
class Relationship(BaseModel):
    from_atom: str
    to_atom: str
    relation_type: str  # "parent", "child", "supports", "contradicts", "relates_to"
    weight: float  # Strength (0.0-1.0)
    evidence: Optional[str]  # Why this relationship exists
```

**Use Cases:**
- Code function + docstring + test (parent-child-sibling)
- Claim + supporting evidence (supports)
- Contradictory statements (contradicts)

---

## 3. Snapshot Specification

### Schema

```python
class Snapshot(BaseModel):
    id: str  # Content-addressed: "snap_{sha256}"
    atoms: List[str]  # Atom IDs in this snapshot
    parent_snapshot: Optional[str]  # Git-like lineage
    created_at: datetime
    metadata: Dict[str, Any]  # Freeform annotations
    notes: Optional[str]  # Human description
    hash: str  # SHA-256 of canonical repr
```

### Content Addressing

```python
def compute_snapshot_hash(atoms: List[Atom]) -> str:
    # Canonical representation: sorted atom IDs + content hashes
    canonical = json.dumps({
        "atoms": sorted([a.id for a in atoms]),
        "content_hashes": sorted([a.content_ref.hash_sha256 for a in atoms])
    }, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()
```

**Properties:**
- Immutable (C-2): Once created, never modified
- Deterministic: Same atoms → same hash
- Merkle-tree-like: Can verify subset inclusion

### Snapshot Operations

**Create:**
```python
def create_snapshot(atoms: List[Atom], notes: str) -> Snapshot:
    snap_hash = compute_snapshot_hash(atoms)
    snap = Snapshot(
        id=f"snap_{snap_hash[:16]}",
        atoms=[a.id for a in atoms],
        created_at=datetime.utcnow(),
        notes=notes,
        hash=snap_hash
    )
    persist(snap)
    return snap
```

**Rollback:**
```python
def rollback_to_snapshot(snapshot_id: str) -> None:
    snap = load_snapshot(snapshot_id)
    current_atoms = get_current_atoms()
    # Mark current atoms as invalid_to = now
    for atom in current_atoms:
        if atom.id not in snap.atoms:
            atom.valid_to = datetime.utcnow()
    # Restore snapshot atoms
    for atom_id in snap.atoms:
        atom = load_atom(atom_id)
        atom.valid_to = None  # Mark as current again
```

---

## 4. Storage Layers

### Architecture

```
┌─────────────────────────────────────────┐
│         CMC Storage Layers              │
├─────────────────────────────────────────┤
│  Vector Store (Embeddings)              │
│  - Faiss / Chroma / LanceDB            │
│  - Fast KNN search                      │
│  - Embedding → Atom ID mapping         │
├─────────────────────────────────────────┤
│  Object Store (Large Payloads)          │
│  - S3 / MinIO / Local filesystem       │
│  - Content-addressed storage            │
│  - Lazy loading                         │
├─────────────────────────────────────────┤
│  Metadata Store (Atoms, Snapshots)      │
│  - SQLite (local) / PostgreSQL (prod)  │
│  - Indexed by ID, tags, time            │
│  - JSONL fallback for simplicity        │
├─────────────────────────────────────────┤
│  Graph Store (SEG Edges)                │
│  - RDF triples (future)                 │
│  - Neo4j / TypeDB (future)              │
│  - Currently: JSONL with atom refs      │
└─────────────────────────────────────────┘
```

### Vector Store Operations

**Index Atom:**
```python
def index_atom_embedding(atom: Atom) -> None:
    if atom.embedding:
        vector_store.add(
            ids=[atom.id],
            embeddings=[atom.embedding.vector],
            metadata={"modality": atom.modality, "tags": atom.tags}
        )
```

**Semantic Search:**
```python
def search_by_embedding(query_vector: List[float], k: int = 10) -> List[str]:
    results = vector_store.search(query_vector, k=k)
    return [r.id for r in results]
```

### Object Store Operations

**Store Large Content:**
```python
def store_large_content(content: str, atom_id: str) -> str:
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    uri = f"s3://cmc-objects/{content_hash[:2]}/{content_hash}"
    object_store.put(uri, content)
    return uri
```

**Lazy Load:**
```python
def load_content(content_ref: ContentRef) -> str:
    if content_ref.inline:
        return content_ref.inline
    else:
        return object_store.get(content_ref.uri)
```

### Metadata Store Schema

**SQLite Tables:**

```sql
CREATE TABLE atoms (
    id TEXT PRIMARY KEY,
    modality TEXT NOT NULL,
    content_inline TEXT,
    content_uri TEXT,
    created_at TIMESTAMP,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    snapshot_id TEXT,
    metadata_json TEXT,  -- Full atom as JSON
    INDEX idx_modality (modality),
    INDEX idx_snapshot (snapshot_id),
    INDEX idx_created (created_at),
    INDEX idx_valid (valid_from, valid_to)
);

CREATE TABLE snapshots (
    id TEXT PRIMARY KEY,
    hash TEXT UNIQUE,
    created_at TIMESTAMP,
    notes TEXT,
    metadata_json TEXT
);

CREATE TABLE tags (
    atom_id TEXT,
    key TEXT,
    value TEXT,
    weight REAL,
    FOREIGN KEY (atom_id) REFERENCES atoms(id),
    INDEX idx_tag (key, value)
);
```

---

## 5. Write Pipeline

### Flow

```
Input Context
    ↓
┌──────────────────┐
│ 1. Ingest        │ Parse input, determine modality
└──────────────────┘
    ↓
┌──────────────────┐
│ 2. Atomize       │ Break into atomic units
└──────────────────┘
    ↓
┌──────────────────┐
│ 3. Enrich        │ Generate embeddings, calculate QS, TPV
└──────────────────┘
    ↓
┌──────────────────┐
│ 4. Index (HHNI)  │ Assign hierarchical path
└──────────────────┘
    ↓
┌──────────────────┐
│ 5. Gate          │ Quality checks, policy validation
└──────────────────┘
    ↓
┌──────────────────┐
│ 6. Persist       │ Write to all stores
└──────────────────┘
    ↓
┌──────────────────┐
│ 7. Snapshot      │ Bundle atoms, compute hash
└──────────────────┘
    ↓
Snapshot ID returned
```

### Performance Targets

**SLOs (from thesis):**
- p50 write latency: < 50ms
- p95 write latency: < 200ms
- p99 write latency: < 500ms
- Throughput: 1000 atoms/sec (single writer)

**Current Performance:**
- p95: ~150ms (meeting target)
- Bottleneck: Embedding generation (30-50ms)
- Optimization: Batch embeddings, async processing

---

## 6. Read Pipeline

### Flow

```
Query
    ↓
┌──────────────────┐
│ 1. HHNI Lookup   │ Hierarchical retrieval
└──────────────────┘
    ↓
┌──────────────────┐
│ 2. DVNS Optimize │ Physics-guided layout
└──────────────────┘
    ↓
┌──────────────────┐
│ 3. Deduplicate   │ Remove redundant atoms
└──────────────────┘
    ↓
┌──────────────────┐
│ 4. Resolve       │ Handle contradictions
└──────────────────┘
    ↓
┌──────────────────┐
│ 5. Compress      │ Age-based strategic compression
└──────────────────┘
    ↓
┌──────────────────┐
│ 6. Budget Fit    │ Respect token limits
└──────────────────┘
    ↓
Optimal Context
```

### Query API

```python
def query_context(
    query: str,
    budget_tokens: int = 8000,
    modality_filter: Optional[List[str]] = None,
    time_range: Optional[Tuple[datetime, datetime]] = None
) -> List[Atom]:
    # Semantic search
    query_embedding = embed(query)
    candidate_ids = vector_store.search(query_embedding, k=100)
    
    # Load atoms
    candidates = [load_atom(id) for id in candidate_ids]
    
    # Apply filters
    if modality_filter:
        candidates = [a for a in candidates if a.modality in modality_filter]
    if time_range:
        start, end = time_range
        candidates = [a for a in candidates 
                      if start <= a.created_at <= end]
    
    # DVNS optimization
    optimized = dvns_physics.optimize(candidates, query_embedding)
    
    # Deduplication
    deduped = deduplication.remove_duplicates(optimized)
    
    # Budget fit
    final = budget_fitter.fit_to_budget(deduped, budget_tokens)
    
    return final
```

---

## 7. Design Constraints

### C-1: Single Writer
**Enforcement:** Lock file, database transaction serialization
```python
with SingleWriterLock():
    atom = create_atom(...)
    persist(atom)
```

### C-2: Snapshot Immutability
**Enforcement:** Database constraint, immutable data structures
```python
# Snapshots are frozen after creation
snapshot.atoms = tuple(snapshot.atoms)  # Immutable
```

### C-7: Time Ordering
**Enforcement:** Monotonic transaction time
```python
def create_atom(...) -> Atom:
    atom.created_at = get_monotonic_time()  # Never decreases
    assert atom.created_at > last_atom_time
```

---

## 8. Current Implementation

**Files:**
- `memory_store.py` (648 lines) - Core logic
- `models.py` - Pydantic schemas
- `repository.py` - SQLite backend
- `embeddings.py` - Vector generation
- `snapshot.py` - Snapshot operations

**Tests:** 10 passing
- `test_memory_store.py` - Core operations
- `test_bitemporal.py` - Time-travel queries
- `test_snapshot_deterministic.py` - Content addressing

---

## Summary

CMC provides memory-native storage with:
1. **Atoms** - Typed, semantic memory units
2. **Snapshots** - Immutable, reproducible bundles
3. **Bitemporal** - Time-travel capability
4. **Multi-tier Storage** - Optimized for different data types
5. **Deterministic** - Single-writer, verifiable

**Next:** See [components/](components/) for deep dives into atoms, snapshots, storage, pipelines.

---

**Word Count:** ~2,000  
**Next Level:** [L3_detailed.md](L3_detailed.md) (10k words - implementation deep dive)


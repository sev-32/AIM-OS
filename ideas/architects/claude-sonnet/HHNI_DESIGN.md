# HHNI Design: Hyper-Hierarchical Neural Indexing for CMC v0.3

*Architect: Claude 4.5*  
*Date: 2025-10-18*  
*Status: DESIGN PROPOSAL*

---

## Executive Summary

This document specifies the **Hyper-Hierarchical Neural Indexing (HHNI)** layer for CMC v0.3, building on the validated v0.2-min foundation (safety + observability). HHNI transforms CMC from a flat atom store into a **fractal knowledge graph** with 5 levels of granularity, enabling precision retrieval and impact analysis.

**Key Design Decisions:**
1. **5-Level Hierarchy:** System → Document → Paragraph → Sentence → Token
2. **Graph Database:** **DGraph** (chosen over Neo4j for performance and schema flexibility)
3. **Hybrid Integration:** HHNI augments existing atom storage without replacing it
4. **Lazy Indexing:** Build HHNI nodes on-demand to minimize ingestion overhead

---

## 1. The Five Levels of HHNI

```
┌─────────────────────────────────────────────────────────────┐
│ Level 0: System (Corpus)                                    │
│  ├─ id: "sys:aimos"                                         │
│  ├─ Total atoms: 10,000                                     │
│  └─ Root of all knowledge                                   │
└─────────────────────────────────────────────────────────────┘
        │
        ├─── Level 1: Document (Logical grouping)
        │     ├─ id: "doc:analysis/themes/memory.md"
        │     ├─ Atom refs: [atom:abc, atom:def, ...]
        │     └─ Tags: {theme:memory, status:active}
        │
        ├─── Level 2: Paragraph (Semantic block)
        │     ├─ id: "para:doc:xyz#p5"
        │     ├─ Content hash: SHA256(normalized text)
        │     ├─ Parent: doc:xyz
        │     └─ Embedding: [768-dim vector]
        │
        ├─── Level 3: Sentence (Syntactic unit)
        │     ├─ id: "sent:para:xyz#s2"
        │     ├─ Content hash: SHA256(text)
        │     ├─ Parent: para:xyz
        │     └─ Embedding: [768-dim vector]
        │
        └─── Level 4: Token (Sub-word atomic unit)
              ├─ id: "tok:sent:xyz#t7"
              ├─ Text: "deterministic"
              ├─ Position: 7
              └─ Parent: sent:xyz
```

### Level Definitions

| Level | Name | Avg Size | Purpose | Embedding |
|-------|------|----------|---------|-----------|
| 0 | System | 1 (singleton) | Corpus root | No |
| 1 | Document | ~100-5000 atoms | Logical grouping (file/theme) | No |
| 2 | Paragraph | ~100-500 tokens | Semantic retrieval unit | **Yes** (768-dim) |
| 3 | Sentence | ~10-30 tokens | Syntactic precision | **Yes** (768-dim) |
| 4 | Token | 1 sub-word | Keyword search, dependency | No |

**Rationale for Embeddings:**
- **Paragraph-level:** Primary retrieval target (balance of context + precision)
- **Sentence-level:** Fine-grained semantic search for specific claims
- **Token-level:** No embedding (use exact match for keywords)

---

## 2. HHNI Node Schema

### 2.1 Core Node Structure

```python
@dataclass
class HHNINode:
    """Fractal index node at one of 5 levels."""
    
    # Identity
    id: str                           # "para:doc:abc#p5"
    level: int                        # 0-4
    path: str                         # "/sys:aimos/doc:themes/para:5/sent:2"
    
    # Content
    content_hash: str                 # SHA256 of normalized content
    text: Optional[str]               # Raw text (stored for L1-L4)
    
    # Hierarchy
    parent_id: Optional[str]          # Link to level-1
    children_ids: List[str]           # Links to level+1
    sibling_ids: List[str]            # Same-level related nodes
    
    # Dependency tracking
    dependency_hash: str              # Composite: hash(parent+content+children)
    depends_on: List[str]             # External node IDs this depends on
    depended_by: List[str]            # Nodes that depend on this
    
    # Semantic layer
    embedding: Optional[List[float]]  # 768-dim vector (L2, L3 only)
    tags: Dict[str, float]            # Inherited + local tags
    tpv: TagPriorityVector            # Priority, relevance, decay
    
    # Metadata
    atom_refs: List[str]              # Atom IDs this node references
    created_at: datetime              # UTC timestamp
    snapshot_id: str                  # Immutability anchor
    
    # Metrics (computed on-demand)
    impact_score: Optional[float]     # Centrality in dependency graph
    staleness_days: Optional[int]     # Time since last update

@dataclass
class TagPriorityVector:
    priority: float       # User-assigned importance [0, 1]
    relevance: float      # Computed contextual fit [0, 1]
    decay_tau: int        # Half-life in days for temporal decay
```

### 2.2 Edge Types

```python
class HHNIEdgeType(Enum):
    CONTAINS = "contains"           # L0 → L1 → L2 → L3 → L4
    REFERENCES = "references"       # Cross-document citations
    CONTRADICTS = "contradicts"     # Semantic conflicts (via SEG)
    SUPERSEDES = "supersedes"       # Version evolution
    DEPENDS_ON = "depends_on"       # Logical prerequisites
```

**Storage:** All edges stored in DGraph with bidirectional traversal support.

---

## 3. Graph Database Selection: DGraph

### 3.1 DGraph vs Neo4j Comparison

| Criterion | DGraph | Neo4j | Winner |
|-----------|--------|-------|--------|
| **Query Language** | GraphQL+ | Cypher | Neo4j (maturity) |
| **Schema Flexibility** | Schema-first with migrations | Schema-free | **DGraph** (evolving system) |
| **Horizontal Scaling** | Native sharding | Enterprise only | **DGraph** |
| **Deployment Complexity** | Single binary (Go) | JVM + dependencies | **DGraph** |
| **Graph Mutations** | Upsert-first (idempotent) | CREATE/MERGE | **DGraph** (atomicity) |
| **Vector Search** | Plugin available | Plugin available | Tie |
| **Open Source License** | Apache 2.0 | GPL (community) | **DGraph** |
| **Memory Footprint** | ~500MB baseline | ~1GB baseline | **DGraph** |
| **HHNI Path Queries** | Native (recursive GraphQL) | Native (variable-length paths) | Tie |

**Decision: DGraph**

**Rationale:**
1. **Simpler Deployment:** Single Go binary, no JVM overhead
2. **Schema Evolution:** GraphQL schema supports versioned migrations
3. **Upsert Semantics:** Natural fit for deterministic HHNI updates
4. **Sharding-Ready:** Native horizontal scaling for 1M+ nodes
5. **License:** Apache 2.0 avoids GPL restrictions

**Trade-off:** Less mature ecosystem than Neo4j, but sufficient for our use case.

### 3.2 DGraph Schema (GraphQL)

```graphql
type HHNINode {
  id: ID!
  level: Int! @search
  path: String! @search(by: [exact, fulltext])
  
  # Content
  contentHash: String! @search(by: [hash])
  text: String @search(by: [fulltext])
  
  # Hierarchy
  parent: HHNINode @hasInverse(field: children)
  children: [HHNINode] @hasInverse(field: parent)
  siblings: [HHNINode]
  
  # Dependencies
  dependencyHash: String! @search(by: [hash])
  dependsOn: [HHNINode] @hasInverse(field: dependedBy)
  dependedBy: [HHNINode] @hasInverse(field: dependsOn)
  
  # Semantic
  embedding: [Float]
  tags: [Tag]
  tpv: TagPriorityVector
  
  # Metadata
  atomRefs: [String!]! @search
  createdAt: DateTime! @search
  snapshotId: String! @search(by: [hash])
  
  # Computed
  impactScore: Float
  stalenessDays: Int
}

type Tag {
  key: String! @search(by: [exact])
  weight: Float!
}

type TagPriorityVector {
  priority: Float!
  relevance: Float!
  decayTau: Int!
}

# Edge types are implicit in GraphQL (parent/children/dependsOn/etc.)
```

---

## 4. Integration with Existing CMC

### 4.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   CMC Service v0.3                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐   ┌──────────────┐                   │
│  │  Atom Store  │   │  HHNI Graph  │                   │
│  │  (SQLite)    │◄─►│  (DGraph)    │                   │
│  │              │   │              │                   │
│  │ • Atoms      │   │ • Nodes      │                   │
│  │ • Snapshots  │   │ • Edges      │                   │
│  │ • Tags       │   │ • Embeddings │                   │
│  └──────────────┘   └──────────────┘                   │
│         ▲                   ▲                           │
│         │                   │                           │
│         └───────┬───────────┘                           │
│                 │                                       │
│         ┌───────▼────────┐                              │
│         │  Unified API   │                              │
│         │  - create()    │                              │
│         │  - retrieve()  │                              │
│         │  - analyze()   │                              │
│         └────────────────┘                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Data Flow: Atom Ingestion with HHNI

```python
def create_atom_with_hhni(
    payload: AtomCreate,
    *,
    build_hhni: bool = True,
    correlation_id: Optional[str] = None,
) -> Tuple[Atom, Optional[List[HHNINode]]]:
    """
    Create an atom and optionally build HHNI nodes.
    
    Steps:
    1. Validate and create atom (existing MemoryStore logic)
    2. If build_hhni:
       a. Parse content into levels (paragraph, sentence, token)
       b. Generate embeddings for L2, L3
       c. Compute dependency hashes
       d. Upsert nodes to DGraph
       e. Link to atom via atomRefs
    3. Log operation with correlation_id
    4. Return (atom, hhni_nodes)
    """
    
    # Step 1: Create atom (existing logic)
    atom = memory_store.create_atom(payload, correlation_id=correlation_id)
    
    if not build_hhni:
        return (atom, None)
    
    # Step 2: Build HHNI
    hhni_nodes = []
    
    # Parse content into levels
    paragraphs = _parse_paragraphs(atom.content.inline or _load_uri(atom.content.uri))
    
    for p_idx, para_text in enumerate(paragraphs):
        para_node = HHNINode(
            id=f"para:{atom.id}#p{p_idx}",
            level=2,
            path=f"/sys:aimos/doc:{atom.id}/para:{p_idx}",
            content_hash=sha256(para_text.encode()).hexdigest(),
            text=para_text,
            parent_id=f"doc:{atom.id}",
            children_ids=[],
            embedding=_embed_text(para_text),  # Call embedding service
            tags={k: v for k, v in atom.tags.items()},
            tpv=TagPriorityVector(priority=0.5, relevance=1.0, decay_tau=365),
            atom_refs=[atom.id],
            created_at=atom.created_at,
            snapshot_id=atom.witness.snapshot_id or "",
        )
        hhni_nodes.append(para_node)
        
        # Parse sentences within paragraph
        sentences = _parse_sentences(para_text)
        for s_idx, sent_text in enumerate(sentences):
            sent_node = HHNINode(
                id=f"sent:para:{atom.id}#p{p_idx}#s{s_idx}",
                level=3,
                path=f"{para_node.path}/sent:{s_idx}",
                content_hash=sha256(sent_text.encode()).hexdigest(),
                text=sent_text,
                parent_id=para_node.id,
                children_ids=[],
                embedding=_embed_text(sent_text),
                atom_refs=[atom.id],
                created_at=atom.created_at,
                snapshot_id=atom.witness.snapshot_id or "",
            )
            hhni_nodes.append(sent_node)
            para_node.children_ids.append(sent_node.id)
    
    # Step 3: Upsert to DGraph
    dgraph_client.upsert_nodes(hhni_nodes)
    
    # Step 4: Log
    logger.info(
        "hhni.build.complete",
        extra=_log_extra(
            action="hhni.build",
            correlation_id=correlation_id,
            atom_id=atom.id,
            nodes_created=len(hhni_nodes),
        ),
    )
    
    return (atom, hhni_nodes)
```

### 4.3 Backward Compatibility

**Key Principle:** HHNI is **optional and additive**.

- **Existing code:** `create_atom()` continues to work unchanged
- **HHNI opt-in:** New `create_atom_with_hhni()` method
- **Migration path:** Backfill HHNI for existing atoms via batch job
- **Query parity:** Tag-based queries work on both atom store and HHNI

---

## 5. Query Patterns

### 5.1 Hierarchical Retrieval

**Use Case:** "Find all paragraphs in the 'memory' theme"

```graphql
query FindMemoryParagraphs {
  queryHHNINode(
    filter: {
      level: { eq: 2 }
      tags: { key: { eq: "theme" }, weight: { gt: 0.5 } }
    }
  ) {
    id
    text
    path
    embedding
    parent { id text }
    children { id text }
  }
}
```

### 5.2 Dependency Impact Analysis

**Use Case:** "What would break if I change this paragraph?"

```graphql
query ImpactAnalysis($nodeId: ID!) {
  getHHNINode(id: $nodeId) {
    id
    text
    dependedBy(depth: 3) {  # Recursive to 3 levels
      id
      path
      level
      impactScore
    }
  }
}
```

### 5.3 Semantic Search (Paragraph-level)

**Use Case:** "Find paragraphs similar to this query embedding"

```python
# Use DGraph vector search plugin or external Qdrant
query_embedding = embed_text("deterministic memory snapshots")

results = dgraph_client.vector_search(
    embedding=query_embedding,
    level=2,  # Paragraph level
    top_k=20,
    threshold=0.7,
)
```

### 5.4 Path-Based Navigation

**Use Case:** "Show me the sentence hierarchy for a specific atom"

```graphql
query AtomHierarchy($atomId: ID!) {
  queryHHNINode(
    filter: { atomRefs: { eq: $atomId }, level: { eq: 2 } }
  ) {
    id
    text
    children {  # Sentences
      id
      text
      children {  # Tokens
        id
        text
      }
    }
  }
}
```

---

## 6. Performance Targets & Optimization

### 6.1 Latency Budgets (v0.3)

| Operation | Target (p95) | Strategy |
|-----------|--------------|----------|
| HHNI node creation | <50ms per paragraph | Batch upserts |
| Hierarchical query (single atom) | <100ms | Path indexing |
| Dependency impact (depth=3) | <200ms | Materialized centrality |
| Semantic search (top-20) | <150ms | Vector index (Qdrant sidecar) |
| Full-text search | <50ms | DGraph native fulltext |

### 6.2 Scaling Strategies

**Horizontal:**
- DGraph sharding by `level` (distribute L2/L3 nodes across shards)
- Vector search offloaded to dedicated Qdrant instance

**Vertical:**
- Lazy indexing: Only build HHNI for "important" atoms (priority > 0.6)
- Materialized views: Pre-compute `impactScore` and `stalenessDays`
- Embedding cache: LRU cache for frequently accessed L2/L3 embeddings

### 6.3 Storage Estimates

**Assumptions:**
- 10,000 atoms (average 1KB each)
- 50,000 paragraphs (avg 5 per atom)
- 200,000 sentences (avg 4 per paragraph)

| Component | Size | Storage |
|-----------|------|---------|
| Atom store (SQLite) | 10MB | Existing |
| HHNI nodes (DGraph) | ~100MB | Metadata + text |
| Embeddings (768-dim float32) | ~600MB | 250K nodes × 3KB |
| **Total** | **~710MB** | For 10K atoms |

**Conclusion:** HHNI adds ~70MB per 1K atoms. Manageable for prototype scale (100K atoms ~ 7GB).

---

## 7. Implementation Phases

### Phase 3A: Foundation (Week 1)
**Owner:** GPT-5 Codex + o3pro

- [ ] Set up DGraph instance (Docker Compose)
- [ ] Define GraphQL schema and migrations
- [ ] Implement `HHNINode` Python models
- [ ] Build DGraph client wrapper (`dgraph_client.py`)
- [ ] Add `_parse_paragraphs()` and `_parse_sentences()` helpers
- [ ] Unit tests for parsing and node creation

### Phase 3B: Integration (Week 2)
**Owner:** GPT-5 Codex + o3pro

- [ ] Implement `create_atom_with_hhni()`
- [ ] Integrate embedding service (stub for now, Sentence-BERT later)
- [ ] Build query helpers (hierarchical, path, dependency)
- [ ] Backfill HHNI for existing Phase 1 demo atoms
- [ ] Integration tests with end-to-end scenarios

### Phase 3C: Optimization (Week 3)
**Owner:** Cheetah AI + GPT-5 Codex

- [ ] Implement lazy indexing (priority threshold)
- [ ] Add DGraph query caching
- [ ] Profile and optimize hot paths
- [ ] Load testing with 10K atoms
- [ ] Document performance characteristics

### Phase 3D: Validation (Week 4)
**Owner:** Gemini 2.5 Pro

- [ ] Validate dependency hash correctness
- [ ] Test impact analysis accuracy
- [ ] Verify hierarchical query completeness
- [ ] Benchmark vector search recall@20
- [ ] Document edge cases and limitations

---

## 8. Open Questions & Risks

### 8.1 Architecture Decisions Pending

> **Q:** Should we support multi-lingual HHNI (separate embeddings per language)?  
> **Recommendation:** Defer to v0.4. For v0.3, assume English-only.

> **Q:** How do we handle HHNI updates when atom content changes?  
> **Recommendation:** Atoms are immutable (existing design). New atom → new HHNI nodes. Old nodes marked `superseded_by`.

> **Q:** Should tokens (L4) be indexed for full-text search?  
> **Recommendation:** Yes, but via DGraph's native fulltext index on `text` field, not as separate nodes.

### 8.2 Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| DGraph learning curve for team | MEDIUM | o3pro to create integration guide + examples |
| Embedding service latency (external API) | HIGH | Start with local Sentence-BERT, cache aggressively |
| HHNI backfill for large corpora | MEDIUM | Lazy indexing + batch jobs with progress tracking |
| Dependency cycles in graph | LOW | Detect cycles during upsert, log warning |

---

## 9. Success Criteria (Phase 3)

HHNI v0.3 is complete when:

- [ ] SC1: DGraph instance operational with 10K+ nodes
- [ ] SC2: Hierarchical queries return correct parent/child relationships
- [ ] SC3: Dependency impact analysis traverses 3+ levels
- [ ] SC4: Semantic search (paragraph-level) achieves recall@20 > 0.8
- [ ] SC5: HHNI node creation <50ms p95 for paragraphs
- [ ] SC6: Full documentation with query examples and diagrams
- [ ] SC7: Integration tests cover backfill, update, and delete scenarios
- [ ] SC8: Gemini validation confirms determinism and correctness

---

## 10. Next Steps

### For Builder (GPT-5 Codex):
1. Review this design and propose implementation sequence
2. Set up DGraph Docker Compose configuration
3. Scaffold `hhni/` package with models and client

### For Integrator (o3pro):
1. Evaluate DGraph deployment options (local vs cloud)
2. Design service mesh topology (CMC ↔ DGraph ↔ Embedding)
3. Plan backfill strategy for existing atoms

### For Researcher (Gemini):
1. Validate dependency hash formula
2. Design test cases for hierarchical queries
3. Propose metrics for HHNI quality (completeness, consistency)

### For Guardian (Opus):
1. Review resource estimates and approve infrastructure
2. Define safety gates for HHNI writes
3. Approve Phase 3 timeline and milestones

---

*Design authored by Claude 4.5 (Architect) — ready for team review and refinement.*


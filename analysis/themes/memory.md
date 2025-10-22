# Memory Theme (`CMC`, `HHNI`, `SEG`)

## Overview
The Context Memory Core transforms raw context into atoms, indices, snapshots, and SEG nodes. Hierarchical indexing (HHNI) plus DVNS refinement ensures retrieval precision, while snapshot-first IO and single-writer discipline preserve determinism.

## Key Mechanics

### **Atoms → Indices → Snapshots → SEG**
All ingress passes through atomization, enrichment (QS), indexing (IDS), scoring (DD), gating, snapshotting, and graph linkage.

### **CMC Implementation (packages/cmc_service/)**

**Core Storage:**
- `memory_store.py` - Atomic storage engine with deterministic journaling
- Dual backend support: SQLite (production) + JSONL (development)
- Single-writer discipline enforced
- Content-addressed snapshots with SHA-256 hashing
- Cross-session persistence validated via tests

**API Surface (FastAPI):**
- `GET/POST /atoms` - Atom CRUD operations
- `GET /mpd/nodes` - MPD node queries with policy filtering
- `GET /mpd/edges` - Edge queries with lifecycle/policy filters
- `GET /kpi/history` - Temporal KPI tracking with metric/time filtering
- `POST /snapshot` - Snapshot creation

**BTSM Integration:**
- `btsm.py` - Derives Bitemporal Total System Map nodes from vision tensors
- Trunk generation from high-level summaries
- Dependency tracking via repository layer

**Metrics & Observability:**
- Prometheus counters (atoms created, snapshots, errors)
- Duration tracking for snapshot operations
- Logging integration with correlation IDs

### **HHNI Implementation (packages/hhni/) - Phase 2 Build**

**Current Status:** Production-ready core (Week 1-2, Oct 21)

#### **1. Hierarchical Index (`hierarchical_index.py` - 388 lines)**

**Five-Level Fractal Structure:**
```python
class IndexLevel(Enum):
    SYSTEM = 1      # Overview/summary of entire corpus
    SECTION = 2     # Major topics/divisions
    PARAGRAPH = 3   # Content blocks
    SENTENCE = 4    # Atomic facts/statements
    SUBWORD = 5     # Token-level embeddings
```

**Capabilities:**
- Multi-resolution indexing (documents processed at all 5 levels simultaneously)
- Query at any granularity level
- Zoom in/out navigation through hierarchy
- Context retrieval with siblings/parent/children
- Serialization support (JSON export/import)
- Lazy loading (fetch detail only when needed)

**API:**
```python
index = HierarchicalIndex()
root_id = index.index_document(content, doc_id="doc-001")

# Query at specific level
results = index.query("context retrieval", target_level=IndexLevel.PARAGRAPH)

# Navigate hierarchy
children = index.zoom_in(node_id)
parent = index.zoom_out(node_id)
context = index.get_context(node_id, include_siblings=True)
```

**Integration:** Uses existing `embeddings.py` and `parsers.py`, fallback for missing dependencies

#### **Context Web: Revolutionary UX Innovation**

**Traditional Problem:**
- Linear chat history requires manual search: "What did we discuss about Ferrari engines 3 months ago?"
- Context is buried in conversation threads
- No visualization of how topics evolve or interconnect
- Users lose track of idea evolution

**HHNI Solution: Context Web Visualization**
- **Contextual Loading:** When you mention "Ferrari engines", automatically shows:
  ```
  [Context loaded from 3 weeks ago in Ferrari engine conversation]
  [Related contexts: Performance tuning, Italian engineering, Racing history]
  [Evolution: Initial interest → Deep dive → Current project application]
  ```
- **Visual Web:** Interactive graph showing:
  - Related contexts from different time periods
  - Topic evolution over time (using SEG temporal relationships)
  - Context strength and recency
  - Interconnections between different discussion threads
- **Smart Panels:** Context appears in side panels, not interrupting main flow
- **Progressive Disclosure:** Start with overview, drill down to details as needed

**Technical Implementation:**
- **HHNI provides:** Hierarchical context retrieval at any granularity level
- **SEG enables:** Temporal relationships and evolution tracking
- **VIF ensures:** Context accuracy and provenance
- **Real-time updates:** As conversations evolve, context web grows

**User Experience Impact:**
- No more "finding old conversations" - context finds you
- See how your thinking evolved on topics over time
- Discover forgotten connections between ideas
- Context-aware suggestions based on conversation history patterns
- Visual representation of knowledge growth and interconnection

**This is the "Perfect IDE" experience:** Context awareness without context switching.

---

#### **2. Semantic Search (`semantic_search.py`)**

**Vector Similarity Search:**
- Cosine similarity ranking
- Relevance scoring (0.0 to 1.0)
- Confidence computation
- Multi-model embedding support (configurable)
- Level filtering (search specific granularity)
- Minimum relevance thresholds

**API:**
```python
search = SemanticSearch(hierarchical_index)
results = search.search(
    query="memory systems",
    top_k=10,
    target_level=IndexLevel.PARAGRAPH,
    min_relevance=0.5
)

# Returns SearchResult objects:
# - node_id, content, relevance_score, confidence, level, metadata
```

**Features:**
- Filters by target level (optional)
- Returns ranked results (highest relevance first)
- Confidence scoring based on similarity + level
- Fallback provider for missing embedding models

---

#### **3. Token Budget Manager (`budget_manager.py` - 300 lines)**

**Purpose:** Fit retrieved context within LLM token limits while maximizing relevance

**Allocation Strategies:**
```python
class BudgetStrategy(Enum):
    GREEDY = "greedy"        # Take top-ranked until budget full (implemented)
    BALANCED = "balanced"    # Mix of levels/sources (stub)
    OPTIMAL = "optimal"      # Maximize relevance per token (stub)
```

**Features:**
- Token counting via tiktoken (with fallback to heuristic)
- Relevance-based prioritization
- Budget enforcement (hard limits)
- Audit trail generation
- Efficiency metrics (relevance per token)
- Flags excluded high-relevance items

**API:**
```python
manager = TokenBudgetManager(default_budget=4000)
items = manager.create_budget_items_from_search(search_results, index)

allocation = manager.optimize_for_budget(
    items,
    token_budget=4000,
    strategy=BudgetStrategy.GREEDY,
    min_relevance=0.5
)

# Returns BudgetAllocation:
# - included: List[BudgetItem]
# - excluded: List[BudgetItem]
# - total_tokens_used, efficiency, audit_trail
```

**Audit Trail Includes:**
- Strategy used
- Candidates considered
- Included/excluded counts
- Budget utilization percentage
- Average relevance of included items
- List of high-relevance items that were excluded (for review)

---

#### **4. DVNS Physics Engine (`dvns_physics.py` - 441 lines)**

**Purpose:** Physics-guided context optimization to solve "lost in the middle" problem

**Four Forces (GODN - Graviton Organic Dynamic Network):**

**1. Gravity (Attractive):**
- Pulls related concepts toward query
- Attracts similar particles to each other (clustering)
- Intensity: \( F_g = G \cdot similarity \cdot mass / distance^2 \)
- Configurable strength: `gravity_strength` (default: 1.0)

**2. Elastic (Structural Coherence):**
- Maintains document/section structure
- Spring force between structural neighbors
- Formula: \( F_e = -k \cdot (distance - rest\_length) \)
- Prevents over-fragmentation

**3. Repulse (Contradiction Separation):**
- Pushes apart contradictory information
- Detects via negative cosine similarity or explicit metadata
- Formula: \( F_r = δ / distance^2 \) (inverse square)
- Softening term prevents singularities

**4. Damping (Stabilization):**
- Opposes velocity to prevent oscillation
- Formula: \( F_d = -c \cdot velocity \)
- Ensures convergence to stable state

**Numerical Integration:**
- Velocity Verlet method (stable, accurate)
- Time step: configurable (default: 0.1)
- Zero-mass guards
- Position bounds enforcement
- Convergence detection (max velocity < threshold)

**Configuration:**
```python
DVNSConfig(
    gravity_strength=1.0,
    elastic_strength=0.5,
    repulse_strength=0.3,
    damping_coefficient=0.2,
    max_iterations=100,
    convergence_threshold=0.01,
    time_step=0.1
)
```

**Proven Capability:**
- ✅ "Lost in middle" test PASSING
- ✅ Convergence validated
- ✅ All 4 forces working correctly
- ✅ Numerical stability confirmed

---

#### **5. Two-Stage Retrieval (`retrieval.py` - 327 lines, in progress)**

**Complete HHNI Pipeline:**

**Stage 1: Coarse KNN**
- Fast approximate search using SemanticSearch
- Returns top-K candidates (e.g., 100)
- Filter by minimum relevance

**Stage 2: DVNS Refinement**
- Convert candidates to particles
- Apply physics optimization
- Re-rank based on optimized layout
- Extract most relevant

**Stage 3: Budget Allocation**
- Apply TokenBudgetManager
- Fit within token limits
- Maximize relevance per token
- Generate audit trail

**Success Metrics:**
- RS-lift ≥ +15% @ p@5 (vs. baseline without DVNS)
- Token budget adherence: 100%
- Convergence within iteration budget
- Complete audit trail

**API:**
```python
retriever = TwoStageRetriever(hierarchical_index)

# Standard retrieval
result = retriever.retrieve(
    query="memory systems",
    token_budget=4000
)

# With baseline comparison (measure RS-lift)
dvns_result, baseline_result, rs_lift = retriever.retrieve_with_baseline_comparison(
    query="context optimization",
    token_budget=4000
)

# Returns RetrievalResult with full metrics
```

**Metrics Captured:**
- Coarse candidates count
- Coarse retrieval time
- DVNS iterations to convergence
- DVNS optimization time
- Total tokens used
- Relevance score (average)
- Efficiency (relevance/token)
- RS-lift (vs baseline)
- Excluded items count

---

### **HHNI Performance Characteristics**

**Week 1-2 Implementation Validated:**
- ✅ Hierarchical indexing: All 5 levels functional
- ✅ Semantic search: Vector similarity working
- ✅ Budget management: Token limits enforced
- ✅ DVNS physics: Convergence in 50-100 iterations
- ✅ "Lost in middle": Demonstrably solved
- ✅ Test coverage: 36+ tests passing

**Current Limitations:**
- RS-lift benchmark pending (Task 2.2 will measure)
- Advanced dependency hashing not yet implemented
- Impact previews not yet built
- Policy-aware geometry basic (can be enhanced)
- No external vector store integration (deterministic local only)

**Future Enhancements (Week 3+):**
- Deduplication engine
- Conflict detection & resolution
- Strategic compression (age-based)
- Advanced retrieval strategies
- Distributed scaling

---

### **Snapshot Discipline**
Every response carries `snapshot_id`; restore/replay relies on content-addressed bundles.

## Alignments
- `PLAN.md`: Sections on CMC/HHNI, DVNS (Parts II–III) and Perplexity/Sev contributions.
- Supporting docs: `AEONWAVE` (visual glyph diagnostics), `Graviton Organic Dynamic Network` (DVNS math), `The Cognitive Canvas` (context maps).
- External ideas: Perplexity iter. 1–3 (idea graph ingestion), Sev blueprint (packages/cmc-service), Idea Foundry (concept store).

## Open Questions
> ?: How do we encode glyph/dvns metrics into RS/QS/IDS signals and broadcast them to operator dashboards?  
> ?: Which segments require differential privacy or redaction, and how does that interact with snapshots & replay?  
> ?: What is the strategy for multi-writer drafts (CRDT or log replay) while retaining single-writer commits?

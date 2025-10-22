# Part II: Context Memory Core (CMC) & HHNI

**Chapters:** 4-7  
**Length:** ~12,000 words  
**Purpose:** Define memory substrate and multi-resolution indexing  
**HHNI Level:** SECTION

---

## 📊 **500-Word Summary**

Part II specifies the memory-native foundation of AIM-OS, transforming ephemeral context into structured, queryable, reversible memory through CMC and enabling intelligent retrieval through HHNI's fractal indexing.

**Chapter 4 (Fractal Memory Hierarchy)** defines the atom as the fundamental memory unit—a typed, tagged, embedded object with modality (text/code/event/tool), content (payload or reference), metadata (timestamps, confidence, source), embeddings (vector representations), and tags (semantic categories with TPV priority vectors). Molecules compose atoms semantically. Schemas specify strict contracts. Key property: atomicity enables recursive composition, allowing atoms to reference other atoms, creating emergent structures from simple primitives.

**Chapter 5 (Hyper-Hierarchical Neural Indexing)** presents HHNI's six-level fractal structure: System (corpus overview), Section (major divisions), Paragraph (content blocks), Sentence (atomic facts), Word (tokens), Subword (characters/bytes). Each level has indices, embeddings, summaries, and parent/child relationships. Dependency hashing tracks impact—changing atom X invalidates dependent indices. Impact previews calculate blast radius before edits. Retrieval Score RS combines three factors: RS = QS · IDS · (1 - DD), where QS is quality (confidence, recency, authority), IDS is index depth coverage, and DD is dependency drift (staleness). TPV (Tag Priority Vector) weights tags for ranking.

**Chapter 6 (Write/Read Pipelines)** specifies deterministic flows:

**Write Path:** Ingest → Atomize (parse into units) → Propose (enrich with QS) → DD-Check (validate freshness) → Gate (quality/policy checks) → Snapshot (bundle atoms) → Evidence-Link (SEG)

**Read Path (Hierarchical):** Query → Retrieve via HHNI (multi-level) → DVNS Refine (physics optimization) → Dumbbell Compression (keep recent detail, compress old) → Budget Fit (token limits) → Optimal Context

Caching strategy uses Markov traversals—preload likely paths based on query history. Performance targets: p95 write < 200ms, p99 read < 100ms, RS-lift ≥ +15% vs. baseline KNN.

**Chapter 7 (Storage Substrate)** specifies four stores:

1. **Vector Store:** High-dimensional embeddings with KNN indices (Faiss, Qdrant)
2. **Evidence Graph Store:** Temporal RDF triples (SEG nodes/edges) with time-slicing
3. **Object Store:** Content-addressed payloads (S3-compatible, deduped)
4. **Snapshot Log:** Immutable bundles with rollback capability

Each store has SLOs, backup strategies, and distributed scaling plans. Single-writer constraint (C-1) serializes writes to CMC for determinism. Snapshots are content-addressed (SHA-256) and immutable (C-2). Rollback works via snapshot restoration—no destructive updates, only append-and-snapshot.

**Key Innovations:**
- Six-level fractal indexing (unprecedented granularity)
- Dependency hashing for change impact
- Retrieval Score formula (RS = QS · IDS · (1-DD))
- Bitemporal storage (transaction + valid time)
- Dumbbell compression (recent detail + old summaries)

**Implementation Status:**
- ✅ **CMC:** 75% complete
  - Atoms: ✅ Working (SQLite + JSONL)
  - Snapshots: ✅ Deterministic (tested)
  - Bitemporal: ✅ Timestamps tracked
  - Molecules: 🔄 Basic only
  - QS scoring: ❌ Not implemented
  
- ✅ **HHNI:** 95% complete
  - 6-level indexing: ✅ Full (hierarchical_index.py, 327 lines)
  - Embeddings: ✅ Working (local + fallback)
  - RS calculation: ✅ Implemented
  - Dependency hashing: 🔄 Basic
  - Impact previews: 🔄 Blast radius calculation exists

**Evidence:** 
- 10 CMC tests passing (`test_memory_store.py`, `test_bitemporal.py`, etc.)
- 77 HHNI tests passing (full suite)
- Snapshot determinism validated: `test_snapshot_deterministic`
- Hierarchical navigation tested: `test_zoom_and_context_navigation`

**Files:**
- `packages/cmc_service/memory_store.py` (648 lines)
- `packages/cmc_service/repository.py` (SQLite backend)
- `packages/cmc_service/models.py` (Pydantic schemas)
- `packages/hhni/hierarchical_index.py` (327 lines)
- `packages/hhni/indexer.py` (legacy indexing)
- `packages/hhni/parsers.py` (text parsing)

**Cross-References:**
- Feeds Part III (DVNS uses HHNI indices for physics optimization)
- Feeds Part IV (APOE retrieves context via HHNI)
- Enables Part V (VIF witnesses stored in CMC, SEG graph in CMC)
- Governed by Part VI (SDF-CVF enforces CMC/HHNI parity)

---

## 🌟 **Critical Concepts Introduced**

**Atoms** - Fundamental memory units (C-001)  
**Snapshots** - Immutable bundles (C-002)  
**HHNI Levels** - 6-level fractal hierarchy (C-003)  
**RS (Retrieval Score)** - Quality metric (C-004)  
**TPV (Tag Priority Vector)** - Weighted tagging (C-005)  
**DD (Dependency Drift)** - Staleness measure (C-006)  
**QS (Quality Score)** - Confidence/recency/authority (C-007)  
**IDS (Index Depth Score)** - Hierarchical coverage (C-008)

---

**Status:** ✅ Summary complete  
**Next:** `part_03_dvns_physics.md` - The physics innovation  
**Or:** `level_3_paragraphs/part_02/` for chapter-by-chapter details


# CMC (Context Memory Core)

**Type:** System  
**Status:** 75% Complete (Oct 2025)  
**Purpose:** Memory-native storage substrate for AI context

---

## 🎯 **Quick Context (100 words)**

CMC transforms ephemeral context into structured, queryable, reversible memory. Atoms are typed memory units with tags and embeddings. Snapshots are immutable, content-addressed bundles. Bitemporal storage (transaction + valid time) enables time-travel queries. Single-writer discipline ensures determinism. Storage spans vector DB (embeddings), object store (payloads), and metadata (SQLite). Write pipeline: Ingest → Atomize → Enrich → Index → Gate → Snapshot. Read pipeline: Query → HHNI Retrieve → DVNS Optimize → Budget Fit. Result: AI that never forgets, always has perfect context.

**[More detail below ↓]**

---

## 📊 **Context Budget Guide (AI Context Optimization)**

**Choose based on your available context tokens:**

### 4k Context Available
→ Read **this README only** (you're here!)  
→ You get: System purpose, key concepts, current status

### 8k Context Available  
→ Read **[L1_overview.md](L1_overview.md)** (500 words)  
→ You get: Architecture overview, all components listed, basic flows

### 32k Context Available  
→ Read **[L2_architecture.md](L2_architecture.md)** (2k words)  
→ You get: Technical details, schemas, pipeline specs, relationships

### 200k Context Available  
→ Read **[L3_detailed.md](L3_detailed.md)** (10k words)  
→ Then drill into **[components/](components/)** for specific parts  
→ You get: Deep implementation knowledge, all components detailed

### 1M Context Available  
→ Read **[L4_complete.md](L4_complete.md)** (complete specification)  
→ Read **all component docs** recursively  
→ You get: Everything - ready to implement or modify

---

## 🗺️ **Navigate by Task**

**Understanding CMC Architecture?**
- Start: [L1_overview.md](L1_overview.md)
- Then: [L2_architecture.md](L2_architecture.md)

**Implementing Atoms?**
- Go to: [components/atoms/](components/atoms/)
- Read its README for context budget guide
- Load appropriate detail level

**Working on Snapshots?**
- Go to: [components/snapshots/](components/snapshots/)
- Follow its detail pyramid

**Understanding Storage?**
- Go to: [components/storage/](components/storage/)

**Building Write Pipeline?**
- Go to: [components/pipelines/write_pipeline/](components/pipelines/)

**Need Code Reference?**
- See: [implementation_map.md](implementation_map.md)
- Links to: `packages/cmc_service/`

---

## 📦 **What's Inside CMC**

**Core Components:**
- **Atoms** - Fundamental memory units (typed, tagged, embedded)
- **Molecules** - Composite memory structures  
- **Snapshots** - Immutable memory bundles (content-addressed)
- **Storage** - Multi-tier persistence (vector, object, metadata)
- **Pipelines** - Write (ingest) and Read (retrieve) flows

**Each component has its own recursive detail pyramid** → Navigate to component folders

---

## 🔧 **Current Implementation**

**Status:** ✅ 75% Complete

**What Works:**
- ✅ Atoms: Full schema, storage, retrieval
- ✅ Snapshots: Deterministic creation, content addressing
- ✅ Bitemporal: Transaction + valid time tracking
- ✅ Storage: SQLite + JSONL backends operational
- ✅ Write pipeline: Atomize, store, snapshot

**What's In Progress:**
- 🔄 QS (Quality Score) calculation: Basic only
- 🔄 Molecules: Schema exists, limited implementation
- 🔄 Read pipeline: Basic, needs HHNI full integration
- 🔄 Object store: File-based only (no S3 yet)

**What's Missing:**
- ❌ Distributed storage
- ❌ Advanced caching strategies
- ❌ Performance optimization

**Tests:** 10 passing in `packages/cmc_service/tests/`

**Files:** 
- `packages/cmc_service/memory_store.py` (648 lines)
- `packages/cmc_service/models.py` (schemas)
- `packages/cmc_service/repository.py` (SQLite backend)

---

## 🔗 **Relationships**

**CMC Feeds:**
- **HHNI** - Indexes atoms for retrieval
- **SEG** - Stores provenance nodes in CMC
- **VIF** - Witnesses stored as atoms
- **APOE** - Retrieves context from CMC

**CMC Uses:**
- **HHNI** - For indexing atoms hierarchically
- **SDF-CVF** - For parity enforcement on CMC changes

**CMC Governed By:**
- **Design Constraint C-1** - Single writer (determinism)
- **Design Constraint C-2** - Snapshot immutability
- **Design Constraint C-7** - Time ordering (bitemporal)

---

## 📚 **Detail Levels Available**

**Level 0 (This File):** README - 100 words + navigation (what you're reading)  
**Level 1:** [L1_overview.md](L1_overview.md) - 500 words (architecture overview)  
**Level 2:** [L2_architecture.md](L2_architecture.md) - 2k words (technical specification)  
**Level 3:** [L3_detailed.md](L3_detailed.md) - 10k words (implementation deep dive)  
**Level 4:** [L4_complete.md](L4_complete.md) - Complete specification with examples  
**Level 5:** Component-level docs (each with own 5 levels) - [components/](components/)

**↓ Progressive disclosure: Each level adds more detail**

---

## 🎯 **Quick Answers**

**What is CMC?**  
Memory storage system that makes AI remember everything across sessions.

**Why does it exist?**  
Current AI forgets between sessions. CMC provides persistent, queryable memory.

**How is it different from a database?**  
CMC stores **memory** (semantic, temporal, relational) not just **data**. Every item is typed, tagged, embedded, and time-tracked.

**What's an Atom?**  
Smallest memory unit - like a row in DB but with modality, embeddings, tags, TPV, HHNI path, and VIF provenance.

**What's a Snapshot?**  
Immutable bundle of atoms - like git commit for memory. Content-addressed (SHA-256), enables rollback.

**How do I use it?**  
See [L1_overview.md](L1_overview.md) for architecture, then [components/](components/) for specific operations.

---

**Last Updated:** 2025-10-21  
**Next:** Navigate to detail level or component as needed  
**Questions?** Check [L1_overview.md](L1_overview.md) for FAQ


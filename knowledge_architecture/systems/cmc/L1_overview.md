# CMC Level 1: Architecture Overview

**Detail Level:** 1 of 5 (500 words)  
**Context Budget:** ~8k tokens  
**Purpose:** Understand CMC architecture and components

---

## What Is CMC?

CMC (Context Memory Core) is AIM-OS's foundational memory substrate that transforms ephemeral AI context into structured, queryable, reversible memory. Instead of forgetting between sessions, AI systems with CMC remember everything, can time-travel through memory, and always retrieve the perfect context for any task.

## Core Architecture

### The Five Building Blocks

**1. Atoms (Fundamental Memory Units)**
- Typed objects: text, code, event, tool invocation
- Rich metadata: tags, embeddings, confidence scores
- Temporal tracking: transaction time + valid time
- Modality-independent: same structure for all content types
- **Schema:** modality, content_ref, embedding, tags, hhni_path, tpv, vif

**2. Molecules (Composite Structures)**
- Groups of related atoms
- Semantic relationships (parent, child, supports, contradicts)
- Emergent structures from atomic composition
- Currently basic implementation

**3. Snapshots (Immutable Bundles)**
- Content-addressed (SHA-256 hash)
- Bundles of atoms at specific moment
- Enables rollback, replay, audit
- Never modified after creation (C-2 constraint)
- Git-like versioning for memory

**4. Storage Layers (Multi-Tier Persistence)**
- **Vector Store:** Embeddings for semantic search (Faiss/Chroma)
- **Object Store:** Large payloads (S3-compatible, currently file-based)
- **Metadata Store:** Atoms, snapshots, indices (SQLite)
- **Graph Store:** SEG provenance edges (planned)

**5. Pipelines (Data Flows)**
- **Write Path:** Ingest → Atomize → Enrich (QS) → Index (HHNI) → Gate → Snapshot
- **Read Path:** Query → HHNI Retrieve → DVNS Optimize → Dedupe → Fit Budget → Context

## Key Innovations

### Bitemporal Storage
Every atom has TWO timestamps:
- **Transaction Time (TT):** When it was recorded in CMC
- **Valid Time (VT):** When it was true in the world

This enables queries like: "What did we know about authentication on Oct 15?" (as-of queries)

### Single-Writer Discipline (C-1)
Only one process writes to CMC at a time. This ensures:
- Deterministic ordering
- No race conditions
- Reproducible snapshots
- Verifiable replay

### Content Addressing
Snapshots use SHA-256 hash as identifier:
- Same content = same hash = deduplication
- Tamper-evident (hash changes if content modified)
- Distributed-system friendly

### Modality Independence
Same atom schema works for:
- Text (documents, conversations)
- Code (functions, classes, modules)
- Events (user actions, system events)
- Tool calls (API invocations, results)

Unifies all context types under one memory model.

## Data Flow

### Write (Ingest Context)
```
Input → Parse → Create Atoms → Enrich with QS/TPV → 
Index via HHNI → Quality Gate → Add to Snapshot → 
Link to SEG → Persist
```

### Read (Retrieve Context)
```
Query → HHNI Lookup → DVNS Physics Optimization → 
Deduplication → Conflict Resolution → Compression → 
Budget Fit → Optimal Context
```

## Integration with Other Systems

**CMC ↔ HHNI:** CMC provides atoms, HHNI indexes them hierarchically (System → Subword)

**CMC ↔ APOE:** APOE retrieves context from CMC, stores execution traces back to CMC

**CMC ↔ VIF:** All VIF witnesses stored as atoms in CMC

**CMC ↔ SEG:** Provenance graph nodes/edges stored in CMC's graph layer

**CMC ↔ SDF-CVF:** Parity gates enforce CMC schema consistency across code/docs/tests

## Current Status (Oct 2025)

**✅ Implemented (75%):**
- Atom schema and storage
- Snapshot creation (deterministic)
- Bitemporal tracking
- SQLite + JSONL backends
- Write pipeline (basic)

**🔄 In Progress:**
- QS calculation (quality scoring)
- Molecule composition
- HHNI integration (partial)

**❌ Planned:**
- Distributed storage
- Advanced caching
- Performance optimization

**Tests:** 10 passing  
**Code:** `packages/cmc_service/` (1200+ lines)

## Key Takeaways

1. CMC is **memory**, not database - semantic, temporal, and relational
2. **Atoms** are the fundamental unit - everything is composed from them
3. **Snapshots** provide time-travel and rollback capability
4. **Bitemporal** storage enables "what was known when" queries
5. **Single-writer** ensures determinism and reproducibility

---

**Word Count:** ~500  
**Next Level:** [L2_architecture.md](L2_architecture.md) (2k words - technical specification)  
**Component Deep Dives:** [components/](components/) (atoms, snapshots, storage, pipelines)


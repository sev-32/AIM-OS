# Atoms - Fundamental Memory Units

**Component of:** CMC (Context Memory Core)  
**Type:** Core Component  
**Status:** ✅ Fully Implemented (75% of CMC)  
**Purpose:** Typed, semantic memory units with rich metadata

---

## 🎯 **Quick Context (100 words)**

Atoms are CMC's fundamental memory units - typed objects (text, code, event, tool) with semantic metadata (tags, embeddings), hierarchical position (HHNI path), quality metrics (TPV), temporal bounds (bitemporal), and provenance (VIF). They're immutable once created (content never changes), but metadata can evolve. Content can be inline (<1KB) or externalized (object store). Every atom has unique ID, snapshot reference, and witness envelope. Think: database row + vector + time-travel + provenance. Schema uses Pydantic for validation. Atoms compose into molecules for complex structures. Core of everything in AIM-OS.

**[More detail below ↓]**

---

## 📊 **Context Budget Guide**

### 4k Context Available
→ Read **this README only**  
→ You get: Atom purpose, key fields, basic usage

### 8k Context Available
→ Read **[L1_overview.md](L1_overview.md)** (500 words)  
→ You get: Complete schema, all fields explained, examples

### 32k Context Available
→ Read **[L2_architecture.md](L2_architecture.md)** (2k words)  
→ You get: Implementation details, validation, lifecycle

### 200k Context Available
→ Read **[L3_detailed.md](L3_detailed.md)** (10k words)  
→ Then drill into **[fields/](fields/)** for specific field docs  
→ You get: Complete implementation knowledge

### 1M Context Available
→ Read **[L4_complete.md](L4_complete.md)** (exhaustive)  
→ Read **all field docs** recursively  
→ You get: Everything - ready to implement or extend

---

## 🗺️ **Navigate by Need**

**Understanding Atom Schema?**
- Start: [L1_overview.md](L1_overview.md)
- Then: [L2_architecture.md](L2_architecture.md)

**Implementing Atoms?**
- Go to: [L3_detailed.md](L3_detailed.md)
- Reference: `packages/cmc_service/models.py`

**Working with Specific Field?**
- **Modality:** [fields/modality/](fields/modality/)
- **Content:** [fields/content_ref/](fields/content_ref/)
- **Embeddings:** [fields/embedding/](fields/embedding/)
- **Tags & TPV:** [fields/tags/](fields/tags/)
- **HHNI Path:** [fields/hhni_path/](fields/hhni_path/)
- **Provenance (VIF):** [fields/vif/](fields/vif/)

**Need Examples?**
- See: [examples/](examples/)

---

## 📦 **Atom Structure**

**Identity:**
- `id` - Unique identifier (atom_{uuid})

**Content:**
- `modality` - Type (text, code, event, tool)
- `content_ref` - Inline or URI reference

**Semantic:**
- `embedding` - Vector representation
- `tags` - Categorization with weights

**Hierarchical:**
- `hhni` - Position in index (System→Subword)

**Quality:**
- `tpv` - Tag Priority Vector (priority, relevance, decay)

**Temporal:**
- `created_at` - Transaction time
- `valid_from` / `valid_to` - Valid time (bitemporal)

**Provenance:**
- `snapshot_id` - Which snapshot contains this
- `vif` - Witness envelope (model, prompt, tools, confidence)

**Extensible:**
- `metadata` - Freeform dict for extensions

---

## 🔧 **Current Implementation**

**File:** `packages/cmc_service/models.py`  
**Lines:** ~200 (Pydantic models)  
**Tests:** 10 passing  
**Status:** ✅ Production-ready

**What Works:**
- ✅ Complete schema with validation
- ✅ Inline vs. external content
- ✅ Bitemporal time tracking
- ✅ Tag system with weights
- ✅ Embedding integration
- ✅ HHNI path assignment
- ✅ VIF provenance

**What's Basic:**
- 🔄 QS (Quality Score) calculation
- 🔄 TPV decay computation
- 🔄 Molecule composition

---

## 🔗 **Relationships**

**Atoms are used by:**
- HHNI (indexes atoms)
- APOE (retrieves atoms for context)
- VIF (stores witnesses as atoms)
- SEG (graph nodes reference atoms)
- Snapshots (bundle atoms)

**Atoms use:**
- Object Store (for large content)
- Vector Store (for embedding search)
- HHNI Service (for path assignment)
- Embedding Service (for vector generation)

**Atoms governed by:**
- Design Constraint C-2 (content immutability)
- Memory Invariant (reversible c ↔ a mapping)

---

## 🎯 **Key Concepts**

**Atom = Memory Unit**  
Not just data - semantic, temporal, provenance-aware memory.

**Immutable Content**  
Once created, content never changes. Only metadata can evolve.

**Bitemporal**  
Two time dimensions: when recorded (TT) + when true (VT).

**Modality-Independent**  
Same schema for text, code, events, tools - unified memory model.

**Composable**  
Atoms combine into molecules for complex structures.

---

## 📚 **Detail Levels Available**

**L0 (This File):** README - Navigation + 100-word summary  
**L1:** [L1_overview.md](L1_overview.md) - 500 words (complete schema)  
**L2:** [L2_architecture.md](L2_architecture.md) - 2k words (implementation)  
**L3:** [L3_detailed.md](L3_detailed.md) - 10k words (deep dive)  
**L4:** [L4_complete.md](L4_complete.md) - Exhaustive reference  
**L5:** Field-level docs (each field with own 5 levels) - [fields/](fields/)

---

## 🔍 **Quick Answers**

**What is an Atom?**  
Fundamental memory unit with content, semantics, time, and provenance.

**Why not just use a database row?**  
Atoms have embeddings (semantic search), HHNI paths (hierarchical), bitemporal time (time-travel), and VIF (provenance).

**Can Atoms change?**  
Content is immutable. Metadata (tags, TPV) can evolve.

**How big is an Atom?**  
Content <1KB: inline. Larger: externalized to object store.

**What's the difference from Molecules?**  
Atoms are atomic units. Molecules group related atoms with semantic relationships.

---

**Parent:** [../../README.md](../../README.md) (CMC System)  
**Last Updated:** 2025-10-21  
**Status:** ✅ Core component, production-ready


# SEG (Shared Evidence Graph)

**Type:** System  
**Status:** 35% Implemented (Week 5)  
**Purpose:** Bitemporal provenance graph for complete audit trails  
**Documentation:** 🆕 **JUST STARTED**

---

## 🎯 **Quick Context (100 words)**

SEG treats evidence as temporal knowledge graph: nodes (claims, sources, derivations), edges (supports, contradicts, derives, witnesses). Bitemporal storage (transaction + valid time) enables "what was known at time T?" queries. Contradiction detection automatic. Export to JSON-LD with SHACL validation. Every VIF witness becomes SEG node, every APOE execution becomes provenance chain, every decision is traceable. Result: Complete audit trail, contradiction-aware knowledge, time-travel queries, full lineage tracking. Foundation for trustworthy, auditable AI systems.

---

## 📊 **Context Budget Guide**

**4k:** This README  
**8k:** L1_overview.md  
**32k:** L2_architecture.md  
**200k+:** L3+ and components/

---

## 📦 **Components**

- **Graph Schema** - Nodes + edges
- **Bitemporal Storage** - Time-slicing
- **Contradiction Detection** - Conflict finding
- **Export System** - JSON-LD, SHACL
- **Query Engine** - Lineage, temporal queries

---

## 🔧 **Current Implementation**

**Status:** 35% Implemented

**Working:**
- ✅ Basic JSONL graph storage
- ✅ Node/edge creation
- ✅ Simple provenance

**Week 5 Priorities:**
- 🔄 Bitemporal queries
- 🔄 Contradiction detection
- 🔄 JSON-LD export
- 🔄 Graph database (Neo4j)

**Code:** `packages/seg/`, `packages/cmc_service/data/seg/`

---

## 🔗 **Relationships**

**SEG Stores:**
- VIF witnesses (as nodes)
- APOE executions (as chains)
- CMC changes (as events)

**SEG Enables:**
- Lineage queries ("where did this come from?")
- Temporal queries ("what was known when?")
- Contradiction detection ("what conflicts?")

---

**Implementation:** `packages/seg/`  
**Status:** 35% implemented, Week 5 priority

**PATTERN EXTENDS TO 5TH SYSTEM!** ✅


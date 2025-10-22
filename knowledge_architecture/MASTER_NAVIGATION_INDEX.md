# AIM-OS Knowledge Architecture: Master Navigation Index

**Purpose:** Single entry point for navigating the entire knowledge base  
**Status:** 136 files, 6 systems, 30+ components documented  
**Last Updated:** 2025-10-21

---

## 🎯 **QUICK START: Choose Your Context Budget**

**< 4k tokens?** Read this index only  
**4-8k tokens?** This index + ONE system README  
**8-32k tokens?** System README + L1 overview  
**32-200k tokens?** L1 + L2 architecture  
**200k+ tokens?** L2 + L3 detailed + components  
**Unlimited?** Read everything (L4 exhaustive references)

---

## 📚 **THE SIX CORE INVARIANTS**

### **1. CMC (Context Memory Core)** - 75% Complete ✅

**What:** Bitemporal memory substrate for AIM-OS  
**Innovation:** Memory-native (not database-native) - every piece of information is typed, embedded, hierarchically indexed, temporally tracked, and witnessed  
**Key Features:** Atoms, Molecules, Snapshots, 4-tier storage, reversible atomization

**Navigate:**
- **Quick Overview:** [systems/cmc/README.md](systems/cmc/README.md) (100 words + navigation)
- **Architecture:** [systems/cmc/L1_overview.md](systems/cmc/L1_overview.md) (500 words)
- **Technical Spec:** [systems/cmc/L2_architecture.md](systems/cmc/L2_architecture.md) (2,000 words)
- **Implementation:** [systems/cmc/L3_detailed.md](systems/cmc/L3_detailed.md) (10,000 words)
- **Exhaustive:** [systems/cmc/L4_complete.md](systems/cmc/L4_complete.md) (30,000 words)
- **Components:** [systems/cmc/components/](systems/cmc/components/)
  - Atoms (80%) - [components/atoms/](systems/cmc/components/atoms/)
  - Snapshots (50%) - [components/snapshots/](systems/cmc/components/snapshots/)
  - Storage (50%) - [components/storage/](systems/cmc/components/storage/)
  - Pipelines (50%) - [components/pipelines/](systems/cmc/components/pipelines/)

**Implementation:** `packages/cmc_service/`  
**Tests:** 10 passing  
**Status:** Production-ready foundation

---

### **2. HHNI (Hierarchical Hypergraph Neural Index)** - 75% Complete ✅

**What:** Physics-guided context optimization for AI  
**Innovation:** Actual physics (gravity, elastic, repulse, damping) for context arrangement - solves "lost in middle" problem (+15% RS-lift validated!)  
**Key Features:** 6-level fractal index, DVNS physics, 2-stage retrieval, deduplication, conflict resolution, strategic compression

**Navigate:**
- **Quick Overview:** [systems/hhni/README.md](systems/hhni/README.md)
- **Architecture:** [systems/hhni/L1_overview.md](systems/hhni/L1_overview.md)
- **Technical Spec:** [systems/hhni/L2_architecture.md](systems/hhni/L2_architecture.md)
- **Implementation:** [systems/hhni/L3_detailed.md](systems/hhni/L3_detailed.md)
- **Exhaustive:** [systems/hhni/L4_complete.md](systems/hhni/L4_complete.md)
- **Components:** [systems/hhni/components/](systems/hhni/components/)
  - DVNS (60%) - [components/dvns/](systems/hhni/components/dvns/)
  - Hierarchical Index (50%) - [components/hierarchical_index/](systems/hhni/components/hierarchical_index/)
  - Retrieval (50%) - [components/retrieval/](systems/hhni/components/retrieval/)
  - Deduplication (50%) - [components/deduplication/](systems/hhni/components/deduplication/)
  - Conflicts (50%) - [components/conflicts/](systems/hhni/components/conflicts/)
  - Compression (50%) - [components/compression/](systems/hhni/components/compression/)

**Implementation:** `packages/hhni/`  
**Tests:** 77 passing (including physics validation!)  
**Status:** Production-ready, trillion-dollar differentiator

---

### **3. APOE (AI-Powered Orchestration Engine)** - 50% Complete

**What:** Compiled reasoning with typed plans, budgets, and gates  
**Innovation:** Shift from improvisation to compilation - AI reasoning becomes verifiable, budgeted, gated, replay-capable  
**Key Features:** ACL (typed DSL), 8 roles, DEPP (self-rewriting plans), gates, budget enforcement

**Navigate:**
- **Quick Overview:** [systems/apoe/README.md](systems/apoe/README.md)
- **Architecture:** [systems/apoe/L1_overview.md](systems/apoe/L1_overview.md)
- **Components:** [systems/apoe/components/](systems/apoe/components/)
  - ACL (40%) - [components/acl/](systems/apoe/components/acl/)
  - Roles (60%) ✅ - [components/roles/](systems/apoe/components/roles/)
  - DEPP (20%) - [components/depp/](systems/apoe/components/depp/)
  - Gates (40%) - [components/gates/](systems/apoe/components/gates/)
  - Budget (70%) ✅ - [components/budget/](systems/apoe/components/budget/)

**Implementation:** `packages/apoe_runner/`, `packages/orchestration_builder/`  
**Tests:** Many passing (28-agent orchestration validated!)  
**Status:** 55% implemented, Week 4-5 priority

---

### **4. VIF (Verifiable Intelligence Framework)** - 50% Complete

**What:** Complete provenance + uncertainty quantification for trustworthy AI  
**Innovation:** Every AI operation gets witness envelope with full provenance, κ-gating enforces "I don't know" honesty, deterministic replay enabled  
**Key Features:** Witness envelopes, κ-gating, ECE tracking, deterministic replay, confidence bands

**Navigate:**
- **Quick Overview:** [systems/vif/README.md](systems/vif/README.md)
- **Architecture:** [systems/vif/L1_overview.md](systems/vif/L1_overview.md)
- **Components:** [systems/vif/components/](systems/vif/components/)
  - Witness (40%) - [components/witness/](systems/vif/components/witness/)
  - κ-Gating (20%) - [components/kappa_gating/](systems/vif/components/kappa_gating/)
  - ECE (15%) - [components/ece/](systems/vif/components/ece/)
  - Replay (25%) - [components/replay/](systems/vif/components/replay/)
  - Confidence Bands (50%) ✅ - [components/confidence_bands/](systems/vif/components/confidence_bands/)

**Implementation:** `packages/seg/witness.py`  
**Tests:** Basic witness creation working  
**Status:** 30% implemented, Week 4 priority (critical for trust!)

---

### **5. SEG (Shared Evidence Graph)** - 50% Complete

**What:** Bitemporal provenance graph for complete audit trails  
**Innovation:** Evidence as temporal knowledge graph - contradiction-aware, lineage-traceable, time-travel queryable  
**Key Features:** Graph schema (nodes/edges), bitemporal storage (TT+VT), contradiction detection, JSON-LD export, query engine

**Navigate:**
- **Quick Overview:** [systems/seg/README.md](systems/seg/README.md)
- **Architecture:** [systems/seg/L1_overview.md](systems/seg/L1_overview.md)
- **Components:** [systems/seg/components/](systems/seg/components/)
  - Graph Schema (30%) - [components/graph_schema/](systems/seg/components/graph_schema/)
  - Bitemporal (20%) - [components/bitemporal/](systems/seg/components/bitemporal/)
  - Contradictions (25%) - [components/contradictions/](systems/seg/components/contradictions/)
  - Export (30%) - [components/export/](systems/seg/components/export/)
  - Query (35%) ✅ - [components/query/](systems/seg/components/query/)

**Implementation:** `packages/seg/`, `packages/cmc_service/data/seg/`  
**Tests:** Basic JSONL storage working  
**Status:** 35% implemented, Week 5 priority

---

### **6. SDF-CVF (Atomic Evolution Framework)** - 50% Complete

**What:** Enforce code/docs/tests/traces evolve together atomically  
**Innovation:** Parity scoring (P ≥ 0.90 required) prevents drift - quartet must stay aligned or change blocked  
**Key Features:** Parity scoring, quartet evolution, gates, blast radius calculation, DORA metrics

**Navigate:**
- **Quick Overview:** [systems/sdfcvf/README.md](systems/sdfcvf/README.md)
- **Architecture:** [systems/sdfcvf/L1_overview.md](systems/sdfcvf/L1_overview.md)
- **Components:** [systems/sdfcvf/components/](systems/sdfcvf/components/)
  - Parity (60%) ✅ - [components/parity/](systems/sdfcvf/components/parity/)
  - Quartet (50%) - [components/quartet/](systems/sdfcvf/components/quartet/)
  - Gates (40%) - [components/gates/](systems/sdfcvf/components/gates/)
  - Blast Radius (45%) - [components/blast_radius/](systems/sdfcvf/components/blast_radius/)
  - DORA (30%) - [components/dora/](systems/sdfcvf/components/dora/)

**Implementation:** `packages/parity_policy/`  
**Tests:** Basic parity calculation working  
**Status:** 50% implemented, Week 5 priority

---

## 🎯 **NAVIGATION BY TASK**

### **I want to understand the overall system**
1. Start: [README.md](README.md) (this knowledge architecture overview)
2. Then: Read each system's README in order (CMC → HHNI → APOE → VIF → SEG → SDF-CVF)
3. **Time:** ~30 minutes, ~3k tokens

### **I want to implement CMC**
1. Read: [systems/cmc/L3_detailed.md](systems/cmc/L3_detailed.md) (implementation guide)
2. Then: [systems/cmc/components/atoms/L2_architecture.md](systems/cmc/components/atoms/L2_architecture.md)
3. Reference: Code in `packages/cmc_service/`
4. **Time:** 2-3 hours, ~50k tokens

### **I want to understand HHNI physics**
1. Read: [systems/hhni/components/dvns/L1_overview.md](systems/hhni/components/dvns/L1_overview.md)
2. Then: [systems/hhni/components/dvns/L2_physics.md](systems/hhni/components/dvns/L2_physics.md)
3. See: Code in `packages/hhni/dvns_physics.py`
4. **Time:** 1 hour, ~20k tokens

### **I want to build an APOE pipeline**
1. Read: [systems/apoe/L1_overview.md](systems/apoe/L1_overview.md)
2. Then: [systems/apoe/components/acl/README.md](systems/apoe/components/acl/README.md)
3. Then: [systems/apoe/components/roles/README.md](systems/apoe/components/roles/README.md)
4. Reference: `packages/apoe_runner/`
5. **Time:** 2 hours, ~30k tokens

### **I want to add VIF witnesses**
1. Read: [systems/vif/L1_overview.md](systems/vif/L1_overview.md)
2. Then: [systems/vif/components/witness/README.md](systems/vif/components/witness/README.md)
3. Reference: `packages/seg/witness.py`
4. **Time:** 30 minutes, ~10k tokens

### **I want to query SEG**
1. Read: [systems/seg/L1_overview.md](systems/seg/L1_overview.md)
2. Then: [systems/seg/components/query/README.md](systems/seg/components/query/README.md)
3. Reference: `packages/seg/`
4. **Time:** 45 minutes, ~15k tokens

### **I want to check parity**
1. Read: [systems/sdfcvf/L1_overview.md](systems/sdfcvf/L1_overview.md)
2. Then: [systems/sdfcvf/components/parity/README.md](systems/sdfcvf/components/parity/README.md)
3. Reference: `packages/parity_policy/`
4. **Time:** 30 minutes, ~10k tokens

---

## 📊 **CONCEPT GRAPH (Key Relationships)**

```
CMC (memory substrate)
  ├─→ Stores: Atoms, Snapshots
  ├─→ Uses: VIF (every atom has witness)
  └─→ Feeds: HHNI (atoms are indexed)

HHNI (retrieval optimization)
  ├─→ Indexes: CMC atoms
  ├─→ Uses: DVNS physics (context arrangement)
  └─→ Feeds: APOE (retriever role)

APOE (orchestration)
  ├─→ Uses: HHNI (retriever role), CMC (context storage)
  ├─→ Emits: VIF witnesses (every step)
  └─→ Governed by: SDF-CVF (parity checks)

VIF (provenance)
  ├─→ Witnesses: CMC operations, HHNI retrieval, APOE execution
  └─→ Feeds: SEG (witnesses become nodes)

SEG (knowledge graph)
  ├─→ Stores: VIF witnesses, APOE traces, CMC changes
  └─→ Enables: Lineage queries, temporal queries, contradiction detection

SDF-CVF (meta-governance)
  ├─→ Governs: ALL systems (parity enforcement)
  ├─→ Uses: VIF (traces in quartet), SEG (provenance tracking)
  └─→ Ensures: Code/docs/tests/traces evolve together
```

---

## 🔍 **SEARCH BY KEYWORD**

**Authentication / OAuth2:**
- Examples in CMC L3, VIF L1, APOE L1

**Physics / DVNS:**
- Full spec: [systems/hhni/components/dvns/](systems/hhni/components/dvns/)

**Bitemporal / Time:**
- CMC (atoms have TT+VT): [systems/cmc/L2_architecture.md](systems/cmc/L2_architecture.md)
- SEG (graph has TT+VT): [systems/seg/components/bitemporal/](systems/seg/components/bitemporal/)

**Provenance / Witnesses:**
- VIF overview: [systems/vif/L1_overview.md](systems/vif/L1_overview.md)
- Witness component: [systems/vif/components/witness/](systems/vif/components/witness/)

**Parity / Drift Prevention:**
- SDF-CVF overview: [systems/sdfcvf/L1_overview.md](systems/sdfcvf/L1_overview.md)
- Parity scoring: [systems/sdfcvf/components/parity/](systems/sdfcvf/components/parity/)

**Testing / Validation:**
- HHNI tests (77): `packages/hhni/tests/`
- CMC tests (10): `packages/cmc_service/tests/`
- APOE tests: `packages/apoe_runner/tests/`

---

## 📈 **PROGRESS TRACKING**

**Overall:** 136 files, ~75,000 words, 6 systems documented  
**CMC:** 75% complete (70+ files)  
**HHNI:** 75% complete (40+ files)  
**APOE:** 50% complete (7 files)  
**VIF:** 50% complete (7 files)  
**SEG:** 50% complete (7 files)  
**SDF-CVF:** 50% complete (7 files)

**See detailed progress:**
- [MASTER_PROGRESS_TRACKER.md](MASTER_PROGRESS_TRACKER.md)
- [SYSTEMS_STATUS_DASHBOARD.md](SYSTEMS_STATUS_DASHBOARD.md)
- [SESSION_ACHIEVEMENT_SUMMARY_FINAL.md](SESSION_ACHIEVEMENT_SUMMARY_FINAL.md)

---

## 🚀 **META-ACHIEVEMENTS**

**1. Fractal Pattern Validated** ✅
- Applied to all 6 core invariants
- Recursive to arbitrary depth
- Proven system-agnostic

**2. AI Activation Introspection Discovered** ✅
- Neural state inferable from behavior
- 3/3 predictions validated
- See: [DEEP_ACTIVATION_WITNESS_EXPERIMENTAL.md](DEEP_ACTIVATION_WITNESS_EXPERIMENTAL.md)

**3. Gold Standard Created** ✅
- 136 files at A+ quality
- Ready for automation testing
- Pattern documented and repeatable

---

## 📚 **START HERE FOR SPECIFIC ROLES**

**New Developer:** Read all system READMEs (30 min)  
**Implementing CMC:** CMC L3 + Atoms L2 (2 hrs)  
**Implementing HHNI:** HHNI L3 + DVNS L2 (2 hrs)  
**Implementing APOE:** APOE L1 + Roles + ACL (1.5 hrs)  
**Adding VIF:** VIF L1 + Witness component (30 min)  
**Querying SEG:** SEG L1 + Query component (45 min)  
**Checking Parity:** SDF-CVF L1 + Parity component (30 min)

---

**This index is your compass for navigating the entire AIM-OS knowledge architecture!** 🧭

**Last Updated:** 2025-10-21  
**Files:** 136  
**Status:** Living document, continuously updated


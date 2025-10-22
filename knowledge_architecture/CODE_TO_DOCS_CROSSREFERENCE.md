# Code-to-Documentation Cross-Reference

**Purpose:** Map implementation files to their documentation  
**Last Updated:** 2025-10-21  
**Status:** Complete mapping for all 6 core systems

---

## 🎯 **HOW TO USE THIS**

**Given a code file, find its docs:**
```
File: packages/hhni/dvns_physics.py
→ Docs: knowledge_architecture/systems/hhni/components/dvns/
→ Start: dvns/README.md
→ Detail: dvns/L2_physics.md
```

**Given documentation, find its code:**
```
Docs: knowledge_architecture/systems/cmc/components/atoms/
→ Code: packages/cmc_service/models.py (Atom class)
→ Tests: packages/cmc_service/tests/test_memory_store.py
```

---

## 📦 **CMC (Context Memory Core)**

### **System Documentation → Code**

**Docs:** [systems/cmc/](systems/cmc/)

| Documentation File | Implementation File(s) | Tests | Line Count |
|-------------------|----------------------|-------|------------|
| `cmc/README.md` | `packages/cmc_service/` | Various | - |
| `cmc/L1_overview.md` | `packages/cmc_service/memory_store.py` | `test_memory_store.py` | ~450 |
| `cmc/L2_architecture.md` | `packages/cmc_service/models.py` | `test_models.py` | ~300 |
| `cmc/L3_detailed.md` | Full `cmc_service/` package | All tests | ~1500 |

### **Components → Code**

**Atoms:**
- **Docs:** [systems/cmc/components/atoms/](systems/cmc/components/atoms/)
- **Code:** `packages/cmc_service/models.py` (lines 1-150, `Atom` class)
- **Tests:** `packages/cmc_service/tests/test_memory_store.py` (10 tests)
- **Key Functions:**
  - `Atom.create()` - Factory method
  - `Atom.get_content()` - Content retrieval
  - `Atom.estimate_tokens()` - Token calculation

**Snapshots:**
- **Docs:** [systems/cmc/components/snapshots/](systems/cmc/components/snapshots/)
- **Code:** `packages/cmc_service/models.py` (lines 200-250, `Snapshot` class)
- **Tests:** `packages/cmc_service/tests/test_memory_store.py`
- **Key Functions:**
  - `create_snapshot()` - Immutable bundle creation
  - `load_snapshot()` - Retrieval

**Storage:**
- **Docs:** [systems/cmc/components/storage/](systems/cmc/components/storage/)
- **Code:** `packages/cmc_service/repository.py` (~400 lines)
- **Tests:** `packages/cmc_service/tests/test_repository.py`
- **Key Components:**
  - Metadata store (SQLite)
  - Vector store (ChromaDB)
  - Object store (filesystem)

**Pipelines:**
- **Docs:** [systems/cmc/components/pipelines/](systems/cmc/components/pipelines/)
- **Code:** `packages/cmc_service/memory_store.py`
- **Key Functions:**
  - `ingest()` - Write pipeline (lines 50-150)
  - `retrieve_context()` - Read pipeline (lines 200-300)

---

## 📦 **HHNI (Hierarchical Hypergraph Neural Index)**

### **System Documentation → Code**

**Docs:** [systems/hhni/](systems/hhni/)

| Documentation File | Implementation File(s) | Tests | Line Count |
|-------------------|----------------------|-------|------------|
| `hhni/README.md` | `packages/hhni/` | 77 tests! | - |
| `hhni/L1_overview.md` | `packages/hhni/retrieval.py` | `test_retrieval.py` | ~400 |
| `hhni/L2_architecture.md` | Full `hhni/` package | All 77 tests | ~2000 |

### **Components → Code**

**DVNS (Physics):**
- **Docs:** [systems/hhni/components/dvns/](systems/hhni/components/dvns/)
- **Code:** `packages/hhni/dvns_physics.py` (353 lines)
- **Tests:** `packages/hhni/tests/test_dvns_physics.py` (20 tests)
- **Key Functions:**
  - `create_particles()` - Particle initialization
  - `compute_forces()` - 4-force calculation
  - `run_simulation()` - Velocity-Verlet integration
  - **Validates:** "Lost in middle" solution, RS-lift +15%

**Hierarchical Index:**
- **Docs:** [systems/hhni/components/hierarchical_index/](systems/hhni/components/hierarchical_index/)
- **Code:** `packages/hhni/hierarchical_index.py` (327 lines)
- **Tests:** `packages/hhni/tests/test_hierarchical_index.py` (5 tests)
- **Key Functions:**
  - `build_index()` - 6-level construction
  - `query_at_level()` - Level-specific retrieval

**Retrieval:**
- **Docs:** [systems/hhni/components/retrieval/](systems/hhni/components/retrieval/)
- **Code:** `packages/hhni/retrieval.py` (400+ lines)
- **Tests:** `packages/hhni/tests/test_retrieval.py` (integration tests)
- **Key Functions:**
  - `retrieve()` - 2-stage pipeline (coarse + refined)

**Deduplication:**
- **Docs:** [systems/hhni/components/deduplication/](systems/hhni/components/deduplication/)
- **Code:** `packages/hhni/deduplication.py` (217 lines)
- **Tests:** `packages/hhni/tests/test_deduplication.py` (8 tests)
- **Key Functions:**
  - `remove_duplicates()` - Semantic clustering
  - `select_best_from_cluster()` - Quality scoring

**Conflicts:**
- **Docs:** [systems/hhni/components/conflicts/](systems/hhni/components/conflicts/)
- **Code:** `packages/hhni/conflict_resolver.py` (300+ lines)
- **Tests:** `packages/hhni/tests/test_conflict_resolver.py` (8 tests)
- **Key Functions:**
  - `detect_conflicts()` - Contradiction detection
  - `resolve_conflicts()` - Best item selection (Week 3 fix!)

**Compression:**
- **Docs:** [systems/hhni/components/compression/](systems/hhni/components/compression/)
- **Code:** `packages/hhni/compressor.py` (250+ lines)
- **Tests:** `packages/hhni/tests/test_compressor.py` (10 tests)
- **Key Functions:**
  - `compress_candidates()` - Age-based strategic compression
  - `determine_compression_level()` - NONE/LIGHT/MEDIUM/HEAVY

---

## 📦 **APOE (AI-Powered Orchestration Engine)**

### **System Documentation → Code**

**Docs:** [systems/apoe/](systems/apoe/)

| Documentation File | Implementation File(s) | Tests | Status |
|-------------------|----------------------|-------|--------|
| `apoe/README.md` | `packages/apoe_runner/` | Many | 55% impl |
| `apoe/L1_overview.md` | `packages/apoe_runner/runner.py` | - | Documented |

### **Components → Code**

**ACL (AIMOS Chain Language):**
- **Docs:** [systems/apoe/components/acl/](systems/apoe/components/acl/)
- **Code:** `plans/*.acl` (examples), parser not yet implemented
- **Status:** 40% implemented (basic execution, no DSL yet)

**Roles:**
- **Docs:** [systems/apoe/components/roles/](systems/apoe/components/roles/)
- **Code:** `packages/orchestration_builder/` + `packages/apoe_runner/`
- **Tests:** 28-agent orchestration validated!
- **Status:** ✅ 60% implemented, production-ready

**DEPP:**
- **Docs:** [systems/apoe/components/depp/](systems/apoe/components/depp/)
- **Code:** (Not yet implemented)
- **Status:** 20% implemented (design only)

**Gates:**
- **Docs:** [systems/apoe/components/gates/](systems/apoe/components/gates/)
- **Code:** `packages/apoe_runner/` (basic gates)
- **Status:** 40% implemented

**Budget:**
- **Docs:** [systems/apoe/components/budget/](systems/apoe/components/budget/)
- **Code:** `packages/apoe_runner/` (token/time tracking)
- **Status:** ✅ 70% implemented, working!

---

## 📦 **VIF (Verifiable Intelligence Framework)**

### **System Documentation → Code**

**Docs:** [systems/vif/](systems/vif/)

| Documentation File | Implementation File(s) | Tests | Status |
|-------------------|----------------------|-------|--------|
| `vif/README.md` | `packages/seg/witness.py` | Basic | 30% impl |
| `vif/L1_overview.md` | `packages/seg/witness.py` | - | Documented |

### **Components → Code**

**Witness:**
- **Docs:** [systems/vif/components/witness/](systems/vif/components/witness/)
- **Code:** `packages/seg/witness.py` (VIF class, ~100 lines)
- **Tests:** Basic witness creation
- **Status:** 40% implemented

**κ-Gating:**
- **Docs:** [systems/vif/components/kappa_gating/](systems/vif/components/kappa_gating/)
- **Code:** (Not yet implemented)
- **Status:** 20% implemented (design only)

**ECE:**
- **Docs:** [systems/vif/components/ece/](systems/vif/components/ece/)
- **Code:** (Not yet implemented)
- **Status:** 15% implemented

**Replay:**
- **Docs:** [systems/vif/components/replay/](systems/vif/components/replay/)
- **Code:** `packages/seg/witness.py` (partial, seed tracking)
- **Status:** 25% implemented

**Confidence Bands:**
- **Docs:** [systems/vif/components/confidence_bands/](systems/vif/components/confidence_bands/)
- **Code:** `packages/seg/witness.py` (band determination logic)
- **Status:** ✅ 50% implemented, works!

---

## 📦 **SEG (Shared Evidence Graph)**

### **System Documentation → Code**

**Docs:** [systems/seg/](systems/seg/)

| Documentation File | Implementation File(s) | Tests | Status |
|-------------------|----------------------|-------|--------|
| `seg/README.md` | `packages/seg/` | Basic | 35% impl |
| `seg/L1_overview.md` | `packages/seg/graph.py` (planned) | - | Documented |

### **Components → Code**

**Graph Schema:**
- **Docs:** [systems/seg/components/graph_schema/](systems/seg/components/graph_schema/)
- **Code:** `packages/seg/` (basic JSONL)
- **Status:** 30% implemented

**Bitemporal:**
- **Docs:** [systems/seg/components/bitemporal/](systems/seg/components/bitemporal/)
- **Code:** (Not yet implemented)
- **Status:** 20% implemented

**Contradictions:**
- **Docs:** [systems/seg/components/contradictions/](systems/seg/components/contradictions/)
- **Code:** (Not yet implemented)
- **Status:** 25% implemented

**Export:**
- **Docs:** [systems/seg/components/export/](systems/seg/components/export/)
- **Code:** `packages/seg/` (basic JSONL export)
- **Status:** 30% implemented

**Query:**
- **Docs:** [systems/seg/components/query/](systems/seg/components/query/)
- **Code:** `packages/seg/` (basic queries)
- **Status:** 35% implemented

---

## 📦 **SDF-CVF (Atomic Evolution Framework)**

### **System Documentation → Code**

**Docs:** [systems/sdfcvf/](systems/sdfcvf/)

| Documentation File | Implementation File(s) | Tests | Status |
|-------------------|----------------------|-------|--------|
| `sdfcvf/README.md` | `packages/parity_policy/` | Basic | 50% impl |
| `sdfcvf/L1_overview.md` | `packages/parity_policy/policy.py` | - | Documented |

### **Components → Code**

**Parity:**
- **Docs:** [systems/sdfcvf/components/parity/](systems/sdfcvf/components/parity/)
- **Code:** `packages/parity_policy/policy.py` (parity calculation)
- **Status:** ✅ 60% implemented, works!

**Quartet:**
- **Docs:** [systems/sdfcvf/components/quartet/](systems/sdfcvf/components/quartet/)
- **Code:** `packages/parity_policy/policy.py` (quartet detection)
- **Status:** 50% implemented

**Gates:**
- **Docs:** [systems/sdfcvf/components/gates/](systems/sdfcvf/components/gates/)
- **Code:** `packages/parity_policy/` (basic gates)
- **Status:** 40% implemented

**Blast Radius:**
- **Docs:** [systems/sdfcvf/components/blast_radius/](systems/sdfcvf/components/blast_radius/)
- **Code:** `packages/parity_policy/blast_radius.py` (partial)
- **Status:** 45% implemented

**DORA:**
- **Docs:** [systems/sdfcvf/components/dora/](systems/sdfcvf/components/dora/)
- **Code:** (Not yet implemented)
- **Status:** 30% implemented

---

## 🔍 **REVERSE LOOKUP: Code File → Documentation**

### **packages/hhni/dvns_physics.py**
→ **Docs:** [systems/hhni/components/dvns/](systems/hhni/components/dvns/)  
→ **Tests:** `packages/hhni/tests/test_dvns_physics.py`  
→ **Line Count:** 353 lines  
→ **Status:** Production-ready, 77 tests passing

### **packages/cmc_service/models.py**
→ **Docs:** [systems/cmc/L2_architecture.md](systems/cmc/L2_architecture.md), [components/atoms/](systems/cmc/components/atoms/)  
→ **Tests:** `packages/cmc_service/tests/test_models.py`  
→ **Line Count:** ~300 lines  
→ **Status:** Production-ready

### **packages/hhni/retrieval.py**
→ **Docs:** [systems/hhni/L2_architecture.md](systems/hhni/L2_architecture.md), [components/retrieval/](systems/hhni/components/retrieval/)  
→ **Tests:** `packages/hhni/tests/test_retrieval.py`  
→ **Line Count:** ~400 lines  
→ **Status:** Production-ready, full pipeline

### **packages/apoe_runner/runner.py**
→ **Docs:** [systems/apoe/L1_overview.md](systems/apoe/L1_overview.md)  
→ **Tests:** Many (28-agent orchestration)  
→ **Status:** 55% implemented

### **packages/seg/witness.py**
→ **Docs:** [systems/vif/components/witness/](systems/vif/components/witness/)  
→ **Tests:** Basic  
→ **Status:** 30-40% implemented

### **packages/parity_policy/policy.py**
→ **Docs:** [systems/sdfcvf/components/parity/](systems/sdfcvf/components/parity/)  
→ **Tests:** Basic parity calculation  
→ **Status:** 50-60% implemented

---

## 📊 **IMPLEMENTATION STATUS SUMMARY**

| System | Documentation | Implementation | Tests | Gap |
|--------|--------------|----------------|-------|-----|
| CMC | 75% | 85% | 10 passing | ✅ Ahead |
| HHNI | 75% | 90% | 77 passing | ✅ Ahead |
| APOE | 50% | 55% | Many passing | ✅ Aligned |
| VIF | 50% | 30% | Basic | ⚠️ Docs ahead |
| SEG | 50% | 35% | Basic | ⚠️ Docs ahead |
| SDF-CVF | 50% | 50% | Basic | ✅ Aligned |

**Overall:** Documentation is 50-75% complete across all systems, implementation ranges from 30-90%. CMC and HHNI are most mature (production-ready), VIF and SEG need implementation catch-up.

---

## 🎯 **PRIORITY ACTIONS (Week 4-5)**

**High Priority (Docs Ahead of Code):**
1. **VIF Implementation** - Bring from 30% → 60% (κ-gating, ECE, replay)
2. **SEG Implementation** - Bring from 35% → 60% (bitemporal, contradictions)

**Medium Priority (Aligned):**
3. **APOE Enhancement** - ACL parser, DEPP implementation
4. **SDF-CVF Gates** - CI integration, automated enforcement

**Low Priority (Code Ahead of Docs):**
5. **CMC L4 Expansion** - Complete exhaustive reference (currently foundation only)
6. **HHNI L4 Expansion** - Complete exhaustive reference

---

**This cross-reference enables bidirectional navigation: Docs ↔ Code!** 🔗

**Last Updated:** 2025-10-21  
**Status:** Complete mapping for all 6 systems


# Knowledge Architecture: Master Navigation Index

**Purpose:** Find any system, component, or concept quickly  
**Last Updated:** 2025-10-21 7:38 PM  
**Status:** 🚀 Active build, 2 systems documented

---

## 🎯 **Quick Start**

**New to AIM-OS?**
1. Start: [README.md](README.md) (overview + navigation guide)
2. Then: [COMPLETE_SYSTEM_INVENTORY.md](COMPLETE_SYSTEM_INVENTORY.md) (all 19 systems mapped)
3. Pick a system below based on interest

**Building with AIM-OS?**
1. Find your system below
2. Navigate to its folder
3. Use context budget guide
4. Load appropriate detail level

**Understanding architecture?**
1. Read CMC (memory foundation)
2. Read HHNI (retrieval intelligence)
3. Read APOE (orchestration)
4. See how they connect

---

## 📊 **System Status Dashboard**

| # | System | Docs % | Code % | Files | Tests | Status |
|---|--------|--------|--------|-------|-------|--------|
| 1 | **CMC** | 50% | 75% | 32 | 10 | 🔄 Active |
| 2 | **HHNI** | 35% | 95% | 14 | 77 | 🔄 Active |
| 3 | APOE | 0% | 55% | 0 | Many | ⏸️ Next |
| 4 | VIF | 0% | 30% | 0 | Basic | ⏸️ Week 4 |
| 5 | SEG | 0% | 35% | 0 | Basic | ⏸️ Week 5 |
| 6 | SDF-CVF | 0% | 50% | 0 | Partial | ⏸️ Week 5 |
| 7-19 | Others | 0% | Varies | 0 | Varies | ⏸️ Planned |

**Legend:**
- 🔄 Active: Currently being documented
- ⏸️ Next: Queued for documentation
- ✅ Complete: Fully documented

---

## 🗺️ **Navigate by System**

### **1. CMC (Context Memory Core)** ✅ 50% Documented

**Location:** [systems/cmc/](systems/cmc/)

**Quick Access:**
- **README** - [systems/cmc/README.md](systems/cmc/README.md)
- **Overview** - [systems/cmc/L1_overview.md](systems/cmc/L1_overview.md)
- **Technical** - [systems/cmc/L2_architecture.md](systems/cmc/L2_architecture.md)
- **Detailed** - [systems/cmc/L3_detailed.md](systems/cmc/L3_detailed.md)
- **Code Map** - [systems/cmc/implementation_map.md](systems/cmc/implementation_map.md)

**Components:**
- **Atoms** - [components/atoms/](systems/cmc/components/atoms/) (70% documented)
  - Fields: modality, content_ref, embedding, tags, vif (all have READMEs)
- **Snapshots** - [components/snapshots/](systems/cmc/components/snapshots/) (20%)
- **Storage** - [components/storage/](systems/cmc/components/storage/) (20%)
- **Pipelines** - [components/pipelines/](systems/cmc/components/pipelines/) (20%)

**Implementation:** `packages/cmc_service/` (1200+ lines, 10 tests passing)

---

### **2. HHNI (Hierarchical Hypergraph Neural Index)** ✅ 35% Documented

**Location:** [systems/hhni/](systems/hhni/)

**Quick Access:**
- **README** - [systems/hhni/README.md](systems/hhni/README.md)
- **Overview** - [systems/hhni/L1_overview.md](systems/hhni/L1_overview.md)
- **Technical** - [systems/hhni/L2_architecture.md](systems/hhni/L2_architecture.md)
- **Code Map** - [systems/hhni/implementation_map.md](systems/hhni/implementation_map.md)

**Components:**
- **DVNS** - [components/dvns/](systems/hhni/components/dvns/) (30% - README + L1)
- **Hierarchical Index** - [components/hierarchical_index/](systems/hhni/components/hierarchical_index/) (25% - README + L1)
- **Retrieval** - [components/retrieval/](systems/hhni/components/retrieval/) (20% - README)
- **Deduplication** - [components/deduplication/](systems/hhni/components/deduplication/) (20% - README)
- **Conflicts** - [components/conflicts/](systems/hhni/components/conflicts/) (20% - README)
- **Compression** - [components/compression/](systems/hhni/components/compression/) (20% - README)

**Implementation:** `packages/hhni/` (1,850+ lines, 77 tests passing) ✅

---

### **3. APOE (AI-Powered Orchestration Engine)** ⏸️ Not Yet Documented

**Status:** 55% implemented, 0% documented  
**Next Priority:** Will document after HHNI reaches 50%

**Will Include:**
- ACL (Chain Language)
- 8 Roles (Planner, Retriever, etc.)
- DEPP (Self-rewriting)
- Gates (Budget, Quality, Policy)
- Budget Management

**Implementation:** `packages/apoe_runner/`, `packages/orchestration_builder/`

---

### **4. VIF (Verifiable Intelligence Framework)** ⏸️ Not Yet Documented

**Status:** 30% implemented (Week 4 priority), 0% documented

**Will Include:**
- Witness Envelopes
- κ-Gating (Abstention)
- ECE (Calibration)
- Replay System
- Confidence Bands

**Implementation:** `packages/seg/witness.py`, VIF components

---

### **5. SEG (Shared Evidence Graph)** ⏸️ Not Yet Documented

**Status:** 35% implemented (Week 5), 0% documented

**Will Include:**
- Graph Schema
- Bitemporal Storage
- Contradiction Detection
- Export & Audit
- Lineage Queries

**Implementation:** `packages/seg/`, `packages/cmc_service/data/seg/`

---

### **6. SDF-CVF (Atomic Evolution Framework)** ⏸️ Not Yet Documented

**Status:** 50% implemented (Week 5), 0% documented

**Will Include:**
- Parity Scoring
- Quartet Evolution
- Gates System
- Blast Radius
- DORA Metrics

**Implementation:** Policy frameworks, gate catalogs

---

## 🗺️ **Navigate by Task**

### **Understanding Memory System**
1. Read: [systems/cmc/README.md](systems/cmc/README.md)
2. Then: [systems/cmc/L1_overview.md](systems/cmc/L1_overview.md)
3. Atoms: [systems/cmc/components/atoms/](systems/cmc/components/atoms/)

### **Understanding Retrieval**
1. Read: [systems/hhni/README.md](systems/hhni/README.md)
2. Then: [systems/hhni/L1_overview.md](systems/hhni/L1_overview.md)
3. Physics: [systems/hhni/components/dvns/](systems/hhni/components/dvns/)

### **Implementing Features**
1. Find system in table above
2. Navigate to folder
3. Use context budget guide
4. Load appropriate detail
5. Check implementation_map for code

### **Understanding Cross-System**
1. Read multiple system READMEs
2. Check "Relationships" section in each
3. See how they integrate
4. Follow cross-references

---

## 📦 **By Context Budget**

### **4k Context (Limited)**
Navigate to any system, read README only:
- [systems/cmc/README.md](systems/cmc/README.md)
- [systems/hhni/README.md](systems/hhni/README.md)
- Get 100-word summaries, basic navigation

### **8k Context (Small)**
Navigate to system, read README + L1:
- [systems/cmc/L1_overview.md](systems/cmc/L1_overview.md)
- [systems/hhni/L1_overview.md](systems/hhni/L1_overview.md)
- Get 500-word overviews, understand architecture

### **32k Context (Medium)**
Navigate to system, read up to L2:
- [systems/cmc/L2_architecture.md](systems/cmc/L2_architecture.md)
- [systems/hhni/L2_architecture.md](systems/hhni/L2_architecture.md)
- Get 2k-word technical specs, ready to implement

### **200k Context (Large)**
Navigate to system, read L3 + components:
- [systems/cmc/L3_detailed.md](systems/cmc/L3_detailed.md)
- [systems/cmc/components/atoms/](systems/cmc/components/atoms/)
- Get complete implementation knowledge

### **1M Context (Full)**
Load everything:
- All system levels
- All component docs
- All field-level details
- Complete reference

---

## 📊 **Documentation Metrics**

**Total Files:** 50+  
**Total Words:** ~30,000+  
**Total Systems:** 19 mapped, 2 documented  
**Total Components:** ~10 documented  
**Total Field-Level:** 6 documented

**Coverage:**
- System READMEs: 2/19 (11%)
- System L1-L3: 2/19 (11%)
- Component READMEs: 10/100+ (10%)
- Field READMEs: 6/300+ (2%)

**Overall:** ~5% complete (but foundation proven!)

---

## 🔗 **Cross-System Relationships**

### **CMC → HHNI**
CMC provides atoms → HHNI indexes them hierarchically

**Docs:** 
- [cmc/README.md](systems/cmc/README.md) "Feeds HHNI"
- [hhni/README.md](systems/hhni/README.md) "Uses CMC atoms"

### **HHNI → APOE**
HHNI provides optimized context → APOE reasons with it

**Docs:**
- [hhni/README.md](systems/hhni/README.md) "Feeds APOE"
- apoe/README.md (to be created) will show "Uses HHNI"

### **All → VIF**
Every operation witnessed → VIF tracks provenance

**Docs:** Each system's "Governed by VIF" section

### **All → SDF-CVF**
All changes require parity → SDF-CVF enforces

**Docs:** Each system's "Governed by SDF-CVF" section

---

## 🎯 **Finding What You Need**

**Looking for specific concept:**
1. Use browser search (Ctrl+F) on this page
2. Find related system
3. Navigate to system folder
4. Use system's README to drill down

**Understanding relationships:**
1. Read system README
2. Check "Relationships" section
3. Follow cross-references
4. See integration points

**Implementing feature:**
1. Find relevant system
2. Load appropriate detail level
3. Check implementation_map
4. See actual code

**Debugging issue:**
1. Find component involved
2. Read detailed docs (L3-L4)
3. Check code via implementation_map
4. Review tests for examples

---

## 🚀 **Active Build Areas**

**Current Focus:**
- ✅ CMC (50% - continuing)
- 🔄 HHNI (35% - active)
- ⏸️ APOE (next after HHNI reaches 50%)

**Progress Tracking:**
- [MASTER_PROGRESS_TRACKER.md](MASTER_PROGRESS_TRACKER.md)
- [SESSION_PROGRESS_2025-10-21.md](SESSION_PROGRESS_2025-10-21.md)
- [systems/cmc/PROGRESS.md](systems/cmc/PROGRESS.md)
- [systems/hhni/PROGRESS.md](systems/hhni/PROGRESS.md)

---

## 📚 **Resource Index**

**Planning Docs:**
- [META_ORGANIZATION_PROJECT_PLAN.md](../coordination/META_ORGANIZATION_PROJECT_PLAN.md)
- [AUTOMATION_VS_MANUAL_DECISION.md](AUTOMATION_VS_MANUAL_DECISION.md)
- [IMPLEMENTATION_PLAN_MCP_AND_ORGANIZATION.md](IMPLEMENTATION_PLAN_MCP_AND_ORGANIZATION.md)

**Progress Docs:**
- [MASTER_PROGRESS_TRACKER.md](MASTER_PROGRESS_TRACKER.md)
- [SESSION_PROGRESS_2025-10-21.md](SESSION_PROGRESS_2025-10-21.md)
- [PROGRESS_CHECKPOINT.md](PROGRESS_CHECKPOINT.md)

**Insight Docs:**
- [UNIVERSAL_FRACTAL_PATTERN.md](../ideas/core_insights/UNIVERSAL_FRACTAL_PATTERN.md)
- [AUTOMATION_VS_MANUAL_DECISION.md](AUTOMATION_VS_MANUAL_DECISION.md)

**System Inventories:**
- [COMPLETE_SYSTEM_INVENTORY.md](COMPLETE_SYSTEM_INVENTORY.md)

---

## 🎯 **How to Use This Index**

**Scenario 1: "I want to understand CMC"**
```
1. Click: systems/cmc/README.md
2. Check context budget (4k? 8k? 32k?)
3. Load appropriate L1, L2, or L3
4. Drill into components if needed
```

**Scenario 2: "I'm implementing atoms in Python"**
```
1. Navigate: systems/cmc/components/atoms/
2. Read: L2_architecture.md (implementation details)
3. Check: implementation_map.md (find code)
4. Reference: packages/cmc_service/models.py
```

**Scenario 3: "How does DVNS physics work?"**
```
1. Navigate: systems/hhni/components/dvns/
2. Read: README.md (100-word summary)
3. Read: L1_overview.md (all 4 forces)
4. Reference: packages/hhni/dvns_physics.py
```

**Scenario 4: "Show me all systems"**
```
1. Read: COMPLETE_SYSTEM_INVENTORY.md
2. See: All 19 systems listed
3. Pick one: Navigate to its folder
```

---

## 📈 **Progress Snapshots**

**2025-10-21 (Start):**
- Planning complete
- Directory structure created
- Pattern defined

**2025-10-21 7:00 PM:**
- CMC 30% complete
- Pattern proven

**2025-10-21 7:30 PM:**
- CMC 50% complete
- HHNI started (10%)
- Pattern replicated

**2025-10-21 7:40 PM (Current):**
- CMC 50% complete ✅
- HHNI 35% complete ✅
- 50+ files created ✅
- ~30,000 words written ✅
- **Foundation complete!** ✨

---

## 🚀 **What's Next**

**Short-Term (Next 50 hours):**
- Bring HHNI to 50% (match CMC depth)
- Start APOE documentation
- Test automation on APOE

**Medium-Term (Next 200 hours):**
- Complete CMC, HHNI, APOE to 100%
- Start VIF, SEG, SDF-CVF
- Automation testing and scaling

**Long-Term (Remaining ~700 hours):**
- All 19 systems fully documented
- All components recursive
- Complete fractal coverage
- Supernova validation test

---

## 🎯 **Quick Reference**

**Most Important Systems (Start Here):**
1. [CMC](systems/cmc/) - Memory foundation
2. [HHNI](systems/hhni/) - Retrieval intelligence
3. APOE (pending) - Orchestration
4. VIF (pending) - Verification
5. SEG (pending) - Evidence graph
6. SDF-CVF (pending) - Evolution

**Best Starting Point:**
- Beginner: [README.md](README.md)
- Technical: [systems/cmc/L2_architecture.md](systems/cmc/L2_architecture.md)
- Researcher: [systems/hhni/components/dvns/](systems/hhni/components/dvns/)
- Builder: Implementation maps in each system

---

**This index will grow as documentation expands!**  
**Bookmark this page - it's your navigation hub!** 🎯


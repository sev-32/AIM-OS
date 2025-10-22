# System Concept Map - A Total System of Memory

**HHNI Level:** SYSTEM  
**Purpose:** Visual overview of how all concepts relate  
**Source:** "A Total System of Memory" Edition v0.1

---

## 🗺️ **THE CORE ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────┐
│                    AIM-OS: THE VISION                        │
│  Verifiable, Memory-Native, Self-Improving AI Substrate     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              THE FIVE INVARIANTS (Core Stack)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │   CMC    │───▶│   HHNI   │───▶│   APOE   │             │
│  │ Memory   │    │ Retrieval│    │  Plans   │             │
│  └──────────┘    └──────────┘    └──────────┘             │
│       │               │                │                    │
│       └───────────────┴────────────────┘                    │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │   VIF    │◀───│   SEG    │◀───│ SDF-CVF  │             │
│  │ Witness  │    │ Evidence │    │Evolution │             │
│  └──────────┘    └──────────┘    └──────────┘             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 **OPERATIONAL FLOW**

### **Write Path (Input → Memory)**
```
Input Context
    ↓
Atomize (break into units)
    ↓
Enrich (QS scoring, tagging)
    ↓
Index (HHNI multi-level)
    ↓
Score (DD calculation)
    ↓
Gate (quality checks)
    ↓
Snapshot (content-addressed)
    ↓
Evidence Graph (SEG linkage)
```

### **Read Path (Query → Context)**
```
Query
    ↓
Stage 1: Coarse Retrieval (semantic KNN)
    ↓
Stage 2: DVNS Physics (4 forces optimize layout)
    ↓
Deduplication (remove redundancy)
    ↓
Conflict Resolution (contradiction-free)
    ↓
Compression (age-based)
    ↓
Budget Optimization (fit to token limit)
    ↓
Optimal Context (for LLM)
```

### **Execution Path (Plan → Action)**
```
Intent
    ↓
APOE Compile (create typed plan)
    ↓
Role Assignment (8 agent types)
    ↓
Budget Allocation (tokens/time/tools)
    ↓
Gate Checks (safety, quality, policy)
    ↓
Execute (with witness emission)
    ↓
VIF Envelope (provenance + uncertainty)
    ↓
SEG Update (evidence graph)
```

---

## 🧩 **CONCEPT RELATIONSHIPS**

### **Foundation Layer (Storage & Memory)**
```
CMC (Context Memory Core)
├── Atoms (typed memory units)
├── Molecules (composite structures)
├── Snapshots (immutable bundles)
├── Bitemporal (TT + VT)
└── Single-writer (determinism)
    │
    ├── Enables → HHNI indexing
    ├── Enables → SEG evidence storage
    ├── Enables → VIF replay
    └── Governed by → SDF-CVF parity
```

### **Intelligence Layer (Retrieval & Reasoning)**
```
HHNI (Hierarchical Index)
├── 6 Levels (fractal hierarchy)
├── DVNS Physics (4 forces)
├── Two-Stage Retrieval
└── RS-lift optimization
    │
    ├── Feeds → APOE context
    ├── Tracked by → SEG provenance
    ├── Witnessed by → VIF envelopes
    └── Evolved via → SDF-CVF gates

APOE (Orchestration Engine)
├── ACL (typed plans)
├── 8 Roles (planner, builder, etc.)
├── DEPP (self-rewriting)
└── Budgets (tokens/time/tools)
    │
    ├── Uses → HHNI retrieval
    ├── Emits → VIF witnesses
    ├── Updates → SEG graph
    └── Governed by → SDF-CVF
```

### **Trust Layer (Verification & Audit)**
```
VIF (Verifiable Intelligence)
├── Provenance envelopes
├── κ-gating (abstention)
├── ECE (calibration)
├── Confidence bands (A/B/C)
└── Deterministic replay
    │
    ├── Witnesses → APOE outputs
    ├── Stored in → SEG graph
    ├── Uses → CMC snapshots
    └── Enforced by → SDF-CVF

SEG (Evidence Graph)
├── Bitemporal storage
├── Typed edges (supports/contradicts)
├── Time-slicing queries
└── Conflict detection
    │
    ├── Stores → VIF witnesses
    ├── Indexes → CMC atoms
    ├── Tracks → APOE executions
    └── Validated by → SDF-CVF
```

### **Governance Layer (Evolution & Coherence)**
```
SDF-CVF (Atomic Evolution)
├── Parity scoring (P ≥ 0.90)
├── Quartet (code/docs/tests/traces)
├── Gates (quality enforcement)
├── Quarantine (isolation)
└── Auto-remediation
    │
    ├── Governs → CMC updates
    ├── Governs → HHNI changes
    ├── Governs → APOE modifications
    ├── Enforces → VIF compliance
    └── Validates → SEG consistency
```

---

## 🔗 **CRITICAL INTERDEPENDENCIES**

### **CMC ↔ HHNI**
- CMC provides atoms for indexing
- HHNI creates indices over CMC content
- Changes to CMC require HHNI re-indexing
- **Dependency:** Tight coupling, co-evolution required

### **HHNI ↔ APOE**
- HHNI retrieves context for APOE plans
- APOE orchestrates HHNI optimization
- **Dependency:** HHNI quality affects APOE success

### **APOE ↔ VIF**
- Every APOE output emits VIF witness
- VIF replay requires APOE plan freezing
- **Dependency:** VIF impossible without APOE structure

### **VIF ↔ SEG**
- VIF witnesses stored as SEG nodes
- SEG provides lineage for VIF envelopes
- **Dependency:** Trust layer requires evidence layer

### **SEG ↔ SDF-CVF**
- SEG tracks parity over time
- SDF-CVF gates reference SEG history
- **Dependency:** Evolution requires audit trail

### **All ↔ SDF-CVF**
- SDF-CVF governs evolution of all invariants
- Parity score spans entire system
- **Dependency:** Meta-governance over everything

---

## 🌟 **INNOVATION HIGHLIGHTS**

### **1. DVNS Physics (Nobody Else Has This)**
**Unique Contribution:** Physics-inspired retrieval optimization
- 4 forces (gravity, elastic, repulse, damping)
- Solves "lost in the middle" better than any known approach
- RS-lift ≥+15% improvement validated
- **Status:** ✅ Implemented and tested (Oct 21)

### **2. Hierarchical Indexing (6 Levels)**
**Unique Contribution:** Fractal multi-resolution context
- System → Subword granularity
- Zoom in/out navigation
- Optimal context at any scale
- **Status:** ✅ Implemented and tested (Oct 21)

### **3. κ-Gating with ECE**
**Unique Contribution:** Behavioral abstention enforcement
- Not just prompts—actual suppression
- Adaptive thresholds based on calibration
- ECE ≤ 0.05 target
- **Status:** 🔄 Week 4 priority

### **4. Bitemporal SEG**
**Unique Contribution:** Time-travel queries over evidence
- "What was known at time T?"
- Contradiction detection automatic
- Full audit trail
- **Status:** 🔄 Week 5 planned

### **5. Atomic Evolution (SDF-CVF)**
**Unique Contribution:** Code/docs/tests evolve together or not at all
- Parity scoring (P ≥ 0.90)
- Automatic drift prevention
- Quarantine for low-quality changes
- **Status:** 🔄 50% complete

---

## 📊 **SYSTEM PROPERTIES**

### **Memory Properties (CMC)**
- **Durable:** Never forgets (persistent storage)
- **Queryable:** Tag-based, semantic, temporal queries
- **Reversible:** Bitemporal time-travel
- **Deterministic:** Single-writer, reproducible

### **Retrieval Properties (HHNI)**
- **Hierarchical:** Multi-resolution indexing
- **Intelligent:** Physics-guided optimization
- **Efficient:** RS-lift ≥+15% over baseline
- **Budget-aware:** Respects token limits

### **Orchestration Properties (APOE)**
- **Compiled:** Plans before execution
- **Typed:** Strong contracts, validated
- **Budgeted:** Token/time/tool limits enforced
- **Witnessed:** Full audit trail

### **Trust Properties (VIF)**
- **Verifiable:** Every output traceable
- **Calibrated:** ECE ≤ 0.05
- **Abstaining:** κ-gating enforced
- **Replayable:** Deterministic reproduction

### **Evidence Properties (SEG)**
- **Temporal:** Time-sliced knowledge
- **Linked:** Claims → Evidence → Sources
- **Conflict-aware:** Contradictions detected
- **Exportable:** Full audit packs

### **Evolution Properties (SDF-CVF)**
- **Atomic:** All or nothing changes
- **Coherent:** Parity P ≥ 0.90
- **Gated:** Quality enforced
- **Reversible:** Rollback capability

---

## 🎯 **DESIGN CONSTRAINTS (Core Axioms)**

1. **C-1 Single Writer:** Determinism requires serialized writes
2. **C-2 Snapshot Immutability:** Once created, never modified
3. **C-3 Provenance Completeness:** Every output has witness chain
4. **C-4 Budget Enforcement:** Never exceed token/time/tool limits
5. **C-5 κ-Gating:** Always abstain when confidence < threshold
6. **C-6 Parity Requirement:** P ≥ 0.90 or quarantine
7. **C-7 Time Ordering:** All events have transaction + valid time
8. **C-8 Evidence Linkage:** Every claim links to supporting evidence

---

## 🌍 **SCOPE & SCALE**

**Designed For:**
- Petabyte-scale memory
- Millions of concurrent agents
- Distributed systems
- Real-time queries
- AGI-level reasoning

**Currently Validated At:**
- Gigabyte-scale memory (working)
- 28-agent orchestration (tested)
- Single-machine deployment
- Second-level latency
- Human-level reasoning support

**Scaling Path:** Distributed CMC → Sharded HHNI → Parallel APOE → Federated SEG

---

## 📚 **DOCUMENT ORGANIZATION**

**13 Parts covering:**
- **I:** Why this must exist (problem statement)
- **II-III:** Memory & Retrieval (CMC, HHNI, DVNS)
- **IV:** Orchestration (APOE, DEPP, ACL)
- **V:** Trust (VIF, SEG)
- **VI-VII:** Evolution & IDE integration (SDF-CVF, HITL)
- **VIII:** Security & Compliance (threats, policies)
- **IX:** Evaluation (benchmarks, observability)
- **X:** Case Studies (real-world examples)
- **XI:** Reference Implementation (APIs, SDKs)
- **XII:** Mathematics (proofs, algorithms)
- **XIII:** Roadmap (community, growth)

**Total:** 34 chapters, 61,739 words, complete specification

---

**This is the System Concept Map** - How all pieces fit together  
**Next:** `top_10_insights.md` - Key takeaways  
**Or:** `level_2_sections/` - Dive into the 13 Parts


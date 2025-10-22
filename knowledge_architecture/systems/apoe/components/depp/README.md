# DEPP (Dynamic Emergent Prompt Pipeline)

**Type:** APOE Component  
**Purpose:** Self-rewriting execution plans via evidence  
**Status:** 20% Implemented (Week 4-5)

---

## 🎯 **Quick Context (50 words)**

DEPP treats the master execution plan as a graph that rewrites itself based on evidence. Execute plan → Gather VIF/SEG witnesses → Analyze effectiveness → Rewrite plan → Better plan. Enables continuous optimization, adaptive strategies, meta-learning. Plans improve over time without human intervention. Foundation for self-improving AI orchestration.

---

## 📊 **Context Budget**

**2k:** This README  
**4k:** L1_overview.md  
**16k:** L2_architecture.md

---

## 📦 **How DEPP Works**

**The Loop:**
```
1. Execute current plan (ACL pipeline)
    ↓
2. Gather evidence (VIF witnesses, SEG provenance, metrics)
    ↓
3. Analyze effectiveness (what worked? what failed? bottlenecks?)
    ↓
4. Rewrite plan (improve based on evidence)
    ↓
5. New plan becomes current
    ↓
Loop (continuous improvement)
```

**Example:**
```
Initial plan: Sequential execution
    ↓
Evidence: Step 2 and 3 independent (can parallelize)
    ↓
Rewrite: Add parallel execution for steps 2-3
    ↓
New plan: Faster (30% speedup)!
```

---

## 🔧 **Implementation**

**Status:** 20% implemented (early stage)

**Working:**
- ✅ Basic plan execution
- ✅ VIF witness collection

**Needed:**
- 🔄 Effectiveness analysis
- 🔄 Plan mutation algorithms
- 🔄 Graph rewriting system
- 🔄 Meta-learning loop

**Code:** (Will be added to `packages/apoe_runner/`)

---

**Parent:** [../../README.md](../../README.md)  
**Status:** Advanced component, Week 4-5 target


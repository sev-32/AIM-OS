# APOE (AI-Powered Orchestration Engine)

**Type:** System  
**Status:** 55% Implemented (Oct 2025)  
**Purpose:** Compiled reasoning with typed plans, budgets, and gates  
**Documentation:** 🆕 **JUST STARTED - PATTERN VALIDATION TEST**

---

## 🎯 **Quick Context (100 words)**

APOE transforms AI from improvisation to compilation—turning vague intent into typed, budgeted, gated execution plans. Uses ACL (AIMOS Chain Language) to specify pipelines with explicit steps, roles (8 agent types), budgets (tokens/time/tools), and gates (quality/safety/policy). DEPP (Dynamic Emergent Prompt Pipeline) enables self-rewriting plans via evidence. Orchestrates planner, retriever, reasoner, verifier, builder, critic, operator, witness agents with contracts and abstention control. Integrates with CMC (context), HHNI (retrieval), VIF (witnesses), SEG (provenance). Replaces one-shot prompting with verifiable, auditable, replay-capable execution.

**[More detail below ↓]**

---

## 📊 **Context Budget Guide**

**4k Context:** Read this README only  
**8k Context:** Read [L1_overview.md](L1_overview.md) (500w)  
**32k Context:** Read [L2_architecture.md](L2_architecture.md) (2kw)  
**200k+ Context:** Read L3-L4 + components/

---

## 🗺️ **Navigate by Task**

**Understanding APOE Architecture?**
- Start: [L1_overview.md](L1_overview.md)
- Then: [L2_architecture.md](L2_architecture.md)

**Implementing ACL Plans?**
- Go to: [components/acl/](components/acl/)
- Reference: `packages/apoe_runner/`

**Working with Roles?**
- Go to: [components/roles/](components/roles/)
- See: 8 agent types

**Understanding DEPP?**
- Go to: [components/depp/](components/depp/)
- Read: Self-rewriting plans

---

## 📦 **What's Inside APOE**

**Core Components:**
- **ACL** - AIMOS Chain Language (typed DSL for plans)
- **Roles** - 8 specialized agent types
- **DEPP** - Dynamic self-rewriting pipeline
- **Gates** - Quality, safety, policy enforcement
- **Budget** - Token/time/tool limit management

**Each component has recursive detail pyramid** → Navigate to folders

---

## 🔧 **Current Implementation**

**Status:** ✅ 55% Implemented

**What Works:**
- ✅ ACL execution (basic)
- ✅ 8 roles defined and tested
- ✅ Budget tracking (tokens/time)
- ✅ Basic orchestration (28 agents tested!)
- ✅ Integration with CMC/HHNI

**What's In Progress:**
- 🔄 DEPP (self-rewriting)
- 🔄 Static type checking
- 🔄 Health metrics (κ_chain)
- 🔄 Gate catalog (comprehensive)

**What's Planned:**
- ⏸️ Large-scale planning (1000+ nodes)
- ⏸️ Advanced routing
- ⏸️ Policy engine integration

**Code:** `packages/apoe_runner/`, `packages/orchestration_builder/`  
**Tests:** Many passing

---

## 🔗 **Relationships**

**APOE Feeds:**
- **VIF** - Execution traces are witnessed
- **SEG** - Plan execution recorded as provenance
- **SDF-CVF** - Plans require parity (code/docs/tests/traces)

**APOE Uses:**
- **CMC** - Retrieves context for reasoning
- **HHNI** - Intelligent context retrieval via physics
- **Quality Gates** - Enforce standards

**APOE Governed By:**
- **Design Constraint C-4** - Budget enforcement
- **Design Constraint C-5** - κ-gating (abstention)
- **Orchestration Invariant** - ∀ plan p, ∃ budget b | execution(p) ≤ b

---

## 🌟 **Key Innovation**

**The Shift: From Improvisation to Compilation**

**Traditional AI (Improvises):**
```
User: "Build authentication system"
AI: [One-shot generation, no planning, no budget, no gates]
Result: Inconsistent, may fail, hard to verify
```

**APOE (Compiles):**
```
User: "Build authentication system"
    ↓
APOE compiles into typed plan:
    Step 1: [Planner] Decompose requirements
    Step 2: [Retriever] Find relevant code examples
    Step 3: [Reasoner] Design approach
    Step 4: [Builder] Generate code
    Step 5: [Critic] Review for issues
    Step 6: [Verifier] Check tests
    Step 7: [Witness] Record decisions
    
Each step:
- Has budget (tokens/time/tools)
- Has contract (inputs/outputs/types)
- Has gates (quality checks)
- Emits witness (VIF provenance)

Result: Verifiable, auditable, replay-capable execution!
```

**This is compilation for reasoning!** Like code compilation, but for thoughts. ✨

---

## 🎯 **The 8 Roles**

**Planner** - Decompose tasks  
**Retriever** - Fetch context (via HHNI)  
**Reasoner** - Multi-step inference  
**Verifier** - Check outputs  
**Builder** - Generate code/content  
**Critic** - Find flaws  
**Operator** - Execute, monitor  
**Witness** - Record provenance  

Each role = specialized agent with capabilities, contracts, budgets

**Navigate:** [components/roles/](components/roles/)

---

## 📚 **Detail Levels Available**

**L0:** This README  
**L1:** [L1_overview.md](L1_overview.md) - 500w overview  
**L2:** [L2_architecture.md](L2_architecture.md) - 2kw technical  
**L3:** [L3_detailed.md](L3_detailed.md) - 10kw implementation  
**L4:** [L4_complete.md](L4_complete.md) - 30kw exhaustive  
**L5:** Component-level docs - [components/](components/)

---

## 🔍 **Quick Answers**

**What is APOE?**  
Orchestration engine that compiles intent into typed, budgeted, gated execution plans.

**Why not just prompt engineering?**  
Prompts improvise. APOE compiles. Compilation enables verification, budgets, gates, replay.

**What's ACL?**  
AIMOS Chain Language - typed DSL for specifying execution plans (like code, but for AI reasoning).

**What's DEPP?**  
Dynamic Emergent Prompt Pipeline - self-rewriting plans that improve via evidence.

**How does it integrate?**  
Uses CMC/HHNI for context, emits VIF witnesses, stores in SEG, enforces SDF-CVF parity.

---

**Parent:** [../../README.md](../../README.md)  
**Siblings:** [../cmc/](../cmc/), [../hhni/](../hhni/), [../vif/](../vif/)  
**Implementation:** `packages/apoe_runner/`, `packages/orchestration_builder/`  
**Status:** ✅ 55% implemented, 🆕 documentation started

**Last Updated:** 2025-10-21  
**Next:** Navigate to detail level or component as needed

**PATTERN CONTINUES - 3rd SYSTEM FOLLOWS SAME STRUCTURE!** ✅✨


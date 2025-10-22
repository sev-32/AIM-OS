# APOE L1: System Overview

**Detail Level:** 1 of 5 (500 words)  
**Context Budget:** ~8k tokens  
**Purpose:** Understand APOE architecture

---

## What Is APOE?

APOE (AI-Powered Orchestration Engine) is AIM-OS's solution to the improvisation problem—where AI systems make things up as they go, leading to unpredictable failures, no audit trails, and unverifiable outputs. APOE compiles vague intent into typed, budgeted, gated execution plans using ACL (AIMOS Chain Language), orchestrates specialized agents through defined roles, and ensures every operation is witnessed, budgeted, and verifiable.

## The Core Innovation: Compilation for Reasoning

**Traditional Approach (Improvisation):**
```
User request
    ↓
AI generates response (one-shot)
    ↓
Hope it works 🤞
```

**Problems:**
- No planning before execution
- No budget enforcement
- No quality gates
- No provenance (can't replay)
- Fails unpredictably

**APOE Approach (Compilation):**
```
User request
    ↓
APOE compiles into ACL plan:
    pipeline auth_implementation {
        step decompose: Planner(budget=2k tokens)
        step retrieve: Retriever(query=requirements, budget=8k)
        step design: Reasoner(inputs=[decompose, retrieve], budget=4k)
        step build: Builder(inputs=[design], budget=10k)
        gate quality_check: verify_tests(coverage >= 0.8)
        step verify: Verifier(inputs=[build], budget=3k)
        step witness: Witness(record=all_above)
    }
    ↓
Execute plan with enforcement
    ↓
VIF witness emitted
```

**Benefits:**
- ✅ Planned before execution
- ✅ Budget enforced (can't exceed)
- ✅ Gates check quality
- ✅ Full provenance (replay-capable)
- ✅ Predictable behavior

**Like code compilation:** You wouldn't execute code without compiling it. Why let AI reason without compilation?

---

## The Five Core Components

### 1. ACL (AIMOS Chain Language)

**Typed DSL for AI plans:**

**Grammar includes:**
- `pipeline` - Sequence of steps
- `step` - Atomic operation (role + budget + contracts)
- `gate` - Quality/safety check (must pass to continue)
- `budget` - Token/time/tool limits (hard constraints)
- `role` - Agent type with capabilities

**Example:**
```acl
pipeline code_review {
    input: code_file: File
    budget: total_tokens = 15000, time = 300s
    
    step parse: Builder(input=code_file, budget=2k)
    step analyze: Critic(input=parse.ast, budget=5k)
    gate quality: check(analyze.issues.critical == 0)
    step suggest: Reasoner(input=analyze, budget=4k)
    step witness: Witness(record=[parse, analyze, suggest])
    
    output: suggestions: List[CodeFix]
}
```

**Navigate:** [components/acl/](components/acl/)

---

### 2. The 8 Roles

**Specialized agent types:**

**Planner** - Decompose complex tasks into steps  
**Retriever** - Fetch context via HHNI (uses CMC)  
**Reasoner** - Multi-step logical inference  
**Verifier** - Check outputs match requirements  
**Builder** - Generate code/content/artifacts  
**Critic** - Identify flaws, edge cases, issues  
**Operator** - Execute plans, monitor progress  
**Witness** - Record provenance, emit VIF  

**Each role has:**
- Capabilities (what it can do)
- Contracts (inputs/outputs/types)
- Budgets (enforced limits)
- Abstention control (κ-gating)

**Navigate:** [components/roles/](components/roles/)

---

### 3. DEPP (Self-Rewriting Plans)

**Master chain as graph:**
```
Current plan → Execute → Gather evidence (VIF, SEG) →
Analyze effectiveness → Rewrite plan → Better plan
```

**Enables:**
- Plans improve via evidence
- Continuous optimization
- Adaptive strategies
- Meta-learning

**Navigate:** [components/depp/](components/depp/)

---

### 4. Gate System

**Three gate types:**

**Quality Gates:** Verify output meets standards  
**Safety Gates:** Enforce security/compliance  
**Policy Gates:** Check against policies  
**Budget Gates:** Ensure limits not exceeded  

**Gates can:**
- PASS → Continue execution
- FAIL → Halt and report
- WARN → Continue with flag
- ABSTAIN → Escalate to HITL

**Navigate:** [components/gates/](components/gates/)

---

### 5. Budget Management

**Three budget types:**

**Token Budget:** Max tokens consumed (hard limit)  
**Time Budget:** Max wall-clock time (timeout)  
**Tool Budget:** Max external API calls (cost control)  

**Enforcement:** Gates check before AND during execution

**Navigate:** [components/budget/](components/budget/)

---

## Integration Points

**APOE ↔ CMC:**
- APOE retrieves context from CMC
- APOE stores execution traces in CMC
- Context enables better reasoning

**APOE ↔ HHNI:**
- Retriever role uses HHNI
- Physics-optimized context
- Budget-aware retrieval

**APOE ↔ VIF:**
- Every step emits VIF witness
- Execution replay enabled
- Provenance complete

**APOE ↔ SEG:**
- Execution traces stored as graph
- Decision provenance tracked
- Lineage queryable

**APOE ↔ SDF-CVF:**
- Plans require parity (code/docs/tests)
- Changes gated by P ≥ 0.90
- Atomic evolution enforced

---

## Current Status

**Implementation:** 55% complete  
**Tests:** Many passing (28-agent orchestration validated)  
**Code:** `packages/apoe_runner/`, `packages/orchestration_builder/`  
**Documentation:** 🆕 Just started (this is APOE's first doc!)

---

## 🎯 **Key Concepts**

**Compilation:** Intent → Typed plan (before execution)  
**Budgets:** Hard limits (tokens/time/tools) enforced  
**Gates:** Quality/safety checks (must pass)  
**Roles:** Specialized agents (capabilities + contracts)  
**DEPP:** Self-rewriting (plans improve via evidence)  
**VIF:** Witnesses (every step tracked)  

---

## 📚 **Detail Levels**

**L0:** This README  
**L1:** [L1_overview.md](L1_overview.md) - Architecture overview  
**L2:** [L2_architecture.md](L2_architecture.md) - Technical spec  
**L3:** [L3_detailed.md](L3_detailed.md) - Implementation guide  
**L4:** [L4_complete.md](L4_complete.md) - Exhaustive reference  
**L5:** Component-level docs - [components/](components/)

---

**Parent:** [../../README.md](../../README.md)  
**Siblings:** [../cmc/](../cmc/), [../hhni/](../hhni/), [../vif/](../vif/)  
**Implementation:** `packages/apoe_runner/`, `packages/orchestration_builder/`  
**Status:** 55% implemented, documentation beginning  

**PATTERN VALIDATED ON 3RD SYSTEM!** ✅🎯✨


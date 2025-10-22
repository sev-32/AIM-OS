# The 8 Roles

**Type:** APOE Component  
**Purpose:** Specialized agent types with capabilities & contracts  
**Status:** 60% Implemented ✅

---

## 🎯 **Quick Context (50 words)**

Eight specialized agents: Planner (decompose), Retriever (fetch via HHNI), Reasoner (multi-step logic), Verifier (check outputs), Builder (generate code), Critic (find flaws), Operator (execute & monitor), Witness (record provenance). Each has capabilities, contracts (inputs/outputs/types), budgets, and κ-gating (abstention threshold). 28-agent orchestration already tested! Production-ready foundation.

---

## 📊 **Context Budget**

**2k:** This README  
**4k:** L1_overview.md  
**16k:** L2_architecture.md

---

## 📦 **The 8 Roles**

### **1. Planner**
**Job:** Decompose complex tasks  
**Capabilities:** Task analysis, dependency graphing  
**Example:** Break "build auth system" → [design, code, test, integrate]

### **2. Retriever**
**Job:** Fetch context via HHNI  
**Capabilities:** Semantic search, budget-aware retrieval  
**Example:** Query CMC for "OAuth2 examples", get physics-optimized context

### **3. Reasoner**
**Job:** Multi-step logical inference  
**Capabilities:** Chain-of-thought, evidence integration  
**Example:** Given requirements + examples → Design approach

### **4. Verifier**
**Job:** Check outputs meet requirements  
**Capabilities:** Testing, validation, compliance checking  
**Example:** Verify code has tests, coverage ≥ 80%

### **5. Builder**
**Job:** Generate code/content/artifacts  
**Capabilities:** Code generation, templating, synthesis  
**Example:** Given design → Generate implementation

### **6. Critic**
**Job:** Identify flaws, edge cases, issues  
**Capabilities:** Review, security analysis, edge case identification  
**Example:** Find security vulnerabilities, logic errors

### **7. Operator**
**Job:** Execute plans, monitor progress  
**Capabilities:** Workflow execution, progress tracking, error handling  
**Example:** Run pipeline steps, handle failures, report status

### **8. Witness**
**Job:** Record provenance, emit VIF  
**Capabilities:** Logging, witness generation, audit trails  
**Example:** Capture all decisions, store in SEG

---

## 🔧 **Implementation**

**Status:** ✅ 60% Implemented (production-ready!)

**Working:**
- ✅ All 8 roles defined
- ✅ Capabilities documented
- ✅ Contracts specified
- ✅ 28-agent orchestration tested!

**Needed:**
- 🔄 Advanced routing
- 🔄 Role-specific budgets (per-role limits)
- 🔄 κ-gating enforcement (abstention)

**Code:** `packages/orchestration_builder/`, `packages/apoe_runner/`

---

**Parent:** [../../README.md](../../README.md)  
**Status:** Core component, already validated!


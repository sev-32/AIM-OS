# ACL (AIMOS Chain Language)

**Type:** APOE Component  
**Purpose:** Typed DSL for specifying AI execution plans  
**Status:** 40% Implemented

---

## 🎯 **Quick Context (50 words)**

ACL is AIM-OS's execution plan language—like Airflow for AI. Defines pipelines with typed steps, budgets, gates, and contracts. Compiled before execution. Enables static analysis, verification, budgeting, and deterministic replay. Example: `pipeline auth { step plan: Planner(budget=2k) gate verify: check(plan.valid) }`. Foundation for compiled AI reasoning.

---

## 📊 **Context Budget**

**2k:** This README  
**4k:** L1_overview.md  
**16k:** L2_architecture.md

---

## 📦 **What's Inside**

**Sub-Components:**
- Grammar (syntax spec)
- Parser (ACL → AST)
- Type Checker (static validation)
- Compiler (AST → executable)
- Examples (reference pipelines)

---

## 🔧 **Implementation**

**Status:** 40% implemented

**Working:**
- ✅ Basic execution (imperative, no DSL yet)
- ✅ Budget tracking
- ✅ Step sequencing

**Needed:**
- 🔄 Full grammar spec
- 🔄 Parser implementation
- 🔄 Static type checking
- 🔄 Compilation to executable

**Code:** `packages/apoe_runner/` (basic), `plans/` (examples)

---

**Parent:** [../../README.md](../../README.md)  
**Status:** Essential component, Week 4-5 priority


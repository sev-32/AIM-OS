# Budget Management

**Type:** APOE Component  
**Purpose:** Enforce token/time/tool limits (hard constraints)  
**Status:** 70% Implemented ✅

---

## 🎯 **Quick Context (50 words)**

Three budget types: Token (max tokens consumed), Time (max wall-clock seconds), Tool (max external API calls). Enforced via gates—checked BEFORE step execution, monitored DURING, halted if exceeded. Prevents runaway costs, timeouts, and API overuse. Already working and tested! Foundation for cost-controlled, predictable AI operations.

---

## 📊 **Context Budget**

**2k:** This README  
**4k:** L1_overview.md  
**16k:** L2_architecture.md

---

## 📦 **The 3 Budget Types**

### **1. Token Budget**
**What:** Max tokens consumed (prompts + completions)  
**Enforcement:** Count accumulates, step blocked if would exceed  
**Example:** Pipeline total = 15k tokens, step costs 8k, only 7k remaining → blocked!

### **2. Time Budget**
**What:** Max wall-clock time (seconds)  
**Enforcement:** Timer started at pipeline start, step blocked if would timeout  
**Example:** Pipeline timeout = 300s, 280s elapsed, step estimates 30s → blocked!

### **3. Tool Budget**
**What:** Max external API calls (cost control)  
**Enforcement:** Counter tracks calls, step blocked if would exceed  
**Example:** Max calls = 10, 9 used, step needs 2 → blocked!

---

## 🔧 **Implementation**

**Status:** ✅ 70% Implemented (production-ready!)

**Working:**
- ✅ Token tracking
- ✅ Time tracking
- ✅ Budget enforcement in basic execution
- ✅ Tested in 28-agent orchestration

**Needed:**
- 🔄 Tool call budget (not yet tracked)
- 🔄 Per-step budget allocation
- 🔄 Budget optimization (redistribute unused)

**Code:** `packages/apoe_runner/` (already implemented!)

---

**Parent:** [../../README.md](../../README.md)  
**Status:** ✅ Core feature, already working!


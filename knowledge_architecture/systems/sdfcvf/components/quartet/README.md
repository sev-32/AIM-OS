# Quartet Evolution

**Type:** SDF-CVF Component  
**Purpose:** Enforce atomic evolution of code + docs + tests + traces  
**Status:** 50% Implemented

---

## 🎯 **Quick Context (50 words)**

Quartet Evolution enforces the invariant: code, documentation, tests, and traces must evolve together or not at all. Detects missing elements (code without docs, docs without tests, etc.), blocks incomplete changes, guides developers to complete the quartet. Foundation for drift-free systems.

---

## 📦 **The Four Elements**

### **1. Code**
**What:** Implementation files (.py, .js, .ts, etc.)  
**Extract:** Function/class signatures, logic  
**Example:** `def authenticate(user, password): ...`

### **2. Docs**
**What:** Documentation files (.md, docstrings, comments)  
**Extract:** Descriptions, usage examples, API specs  
**Example:** `## Authentication: Call authenticate(user, password) to verify credentials`

### **3. Tests**
**What:** Test files (test_*.py, *.test.js, etc.)  
**Extract:** Test names, assertions, scenarios  
**Example:** `def test_authenticate_valid_credentials(): assert authenticate(...) == True`

### **4. Traces**
**What:** Execution records (VIF witnesses, SEG provenance)  
**Extract:** Decisions, execution paths, outcomes  
**Example:** `VIF: authenticate() called with user=john, result=success`

---

## 📦 **Completeness Check**

```python
def check_quartet_completeness(change: Change) -> QuartetStatus:
    """Verify all four elements present"""
    has_code = len(change.code_files) > 0
    has_docs = len(change.doc_files) > 0
    has_tests = len(change.test_files) > 0
    has_traces = len(change.trace_files) > 0
    
    missing = []
    if not has_code: missing.append("code")
    if not has_docs: missing.append("docs")
    if not has_tests: missing.append("tests")
    if not has_traces: missing.append("traces")
    
    if missing:
        return QuartetStatus(
            complete=False,
            missing=missing,
            message=f"Incomplete quartet: missing {', '.join(missing)}"
        )
    else:
        return QuartetStatus(complete=True)
```

---

## 🔧 **Implementation Status**

**Status:** 50% implemented

**Working:**
- ✅ Quartet detection (find all four elements)
- ✅ Completeness check

**Needed:**
- 🔄 Automated doc generation (suggest docs for new code)
- 🔄 Automated test generation (suggest tests for new code)
- 🔄 Trace capture automation (VIF integration)

**Code:** `packages/parity_policy/` (partial)

---

**Parent:** [../../README.md](../../README.md)


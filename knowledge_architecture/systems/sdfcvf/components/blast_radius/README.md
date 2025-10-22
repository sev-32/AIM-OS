# Blast Radius Calculation

**Type:** SDF-CVF Component  
**Purpose:** Predict change impact across quartet  
**Status:** 45% Implemented

---

## 🎯 **Quick Context (50 words)**

Blast radius quantifies change impact: Which files directly modified? Which depend on them? Which docs mention them? Which tests cover them? Which traces involve them? Helps estimate effort, plan quartet updates, prevent surprises. Foundation for informed, complete quartet evolution.

---

## 📦 **Radius Components**

### **1. Direct Changes**
Files explicitly modified in commit

### **2. Dependencies**
Files that import/reference modified code

### **3. Documentation**
Docs that mention changed functions/classes

### **4. Tests**
Tests that cover modified code

### **5. Traces**
VIF witnesses / SEG nodes involving changed components

---

## 📦 **Calculation**

```python
@dataclass
class BlastRadius:
    direct: List[str]           # Modified files
    dependencies: List[str]     # Dependent files
    docs: List[str]            # Mentioning docs
    tests: List[str]           # Covering tests
    traces: List[str]          # Related traces
    total_affected: int        # Sum of all
    
def calculate_blast_radius(change: Change) -> BlastRadius:
    """Compute full change impact"""
    # Direct
    direct = change.modified_files
    
    # Dependencies (via AST analysis)
    deps = []
    for file in direct:
        deps.extend(find_importers(file))
    deps = list(set(deps))
    
    # Docs (via grep for function/class names)
    docs = []
    symbols = extract_symbols(direct)
    for symbol in symbols:
        docs.extend(grep_docs_for_symbol(symbol))
    docs = list(set(docs))
    
    # Tests (via pytest --collect-only)
    tests = []
    for file in direct:
        tests.extend(find_tests_covering(file))
    tests = list(set(tests))
    
    # Traces (via SEG query)
    traces = []
    for file in direct:
        component = file_to_component(file)
        traces.extend(seg.find_traces_mentioning(component))
    
    return BlastRadius(
        direct=direct,
        dependencies=deps,
        docs=docs,
        tests=tests,
        traces=traces,
        total_affected=len(direct) + len(deps) + len(docs) + len(tests) + len(traces)
    )
```

---

## 🔧 **Implementation Status**

**Status:** 45% implemented

**Working:**
- ✅ Direct file detection
- ✅ Basic dependency analysis

**Needed:**
- 🔄 Full AST-based dependency graph
- 🔄 Doc mention detection (semantic, not just grep)
- 🔄 Test coverage mapping
- 🔄 SEG trace integration

**Code:** `packages/parity_policy/blast_radius.py` (partial)

---

**Parent:** [../../README.md](../../README.md)


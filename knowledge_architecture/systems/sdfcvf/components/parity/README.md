# Parity Scoring

**Type:** SDF-CVF Component  
**Purpose:** Measure alignment across code/docs/tests/traces quartet  
**Status:** 60% Implemented ✅

---

## 🎯 **Quick Context (50 words)**

Parity (P) measures quartet alignment using semantic similarity. Formula: Average all pairwise similarities between code, docs, tests, traces. Target: P ≥ 0.90. P < 0.90 = drift detected, gate blocks change. Foundation for enforcing atomic evolution—quartet must stay aligned or change rejected.

---

## 📦 **The Formula**

```
P = (C_code×docs + C_code×tests + C_code×traces + 
     C_docs×tests + C_docs×traces + C_tests×traces) / 6

Where:
C_x×y = cosine_similarity(embedding(x), embedding(y))

Each element embedded as text:
- Code: Function/class signatures + docstrings
- Docs: Markdown documentation
- Tests: Test names + assertions
- Traces: VIF witnesses + SEG provenance
```

---

## 📦 **Implementation**

```python
def calculate_parity(change: Change) -> float:
    """Calculate quartet parity score"""
    # Extract quartet
    code = extract_code_text(change.code_files)
    docs = extract_docs_text(change.doc_files)
    tests = extract_test_text(change.test_files)
    traces = extract_trace_text(change.trace_files)
    
    # Embed all
    emb_code = embed(code)
    emb_docs = embed(docs)
    emb_tests = embed(tests)
    emb_traces = embed(traces)
    
    # Calculate all pairwise similarities
    similarities = [
        cosine_similarity(emb_code, emb_docs),
        cosine_similarity(emb_code, emb_tests),
        cosine_similarity(emb_code, emb_traces),
        cosine_similarity(emb_docs, emb_tests),
        cosine_similarity(emb_docs, emb_traces),
        cosine_similarity(emb_tests, emb_traces)
    ]
    
    # Average
    parity = sum(similarities) / len(similarities)
    return parity
```

---

## 🔧 **Implementation Status**

**Status:** ✅ 60% Implemented (WORKS!)

**Working:**
- ✅ Parity calculation
- ✅ Basic embedding extraction
- ✅ Threshold checking (P ≥ 0.90)

**Needed:**
- 🔄 Weighted parity (critical files higher weight)
- 🔄 Incremental parity (only check changed files)
- 🔄 Parity visualization (show which pairs misaligned)

**Code:** `packages/parity_policy/` ✅

---

**Parent:** [../../README.md](../../README.md)


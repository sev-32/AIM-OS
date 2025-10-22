# Bitemporal Storage

**Type:** SEG Component  
**Purpose:** Track both transaction time (when recorded) and valid time (when true)  
**Status:** 20% Implemented (Week 5)

---

## 🎯 **Quick Context (50 words)**

Bitemporal storage maintains two independent timelines: Transaction Time (TT - when fact entered system) and Valid Time (VT - when fact was true in reality). Enables "what was known at time T?" queries, corrections without deletion, complete audit trails. Foundation for temporal provenance and historical reasoning.

---

## 📦 **The Two Timelines**

### **Transaction Time (TT)**
**What:** When fact was recorded in SEG  
**Use:** "What did we know on date X?"  
**Immutable:** Never changes (historical record)

### **Valid Time (VT)**
**What:** When fact was true in real world  
**Use:** "What was the state on date X?"  
**Mutable:** Can be updated (corrections)

---

## 📦 **Example**

**Scenario:**
```
2025-10-15: User John promoted to Admin (real event)
2025-10-21: We record the promotion in SEG
2025-10-25: We discover it was actually 2025-10-14

Final record:
  TT: 2025-10-21 (when we recorded it)
  VT: 2025-10-14 → ∞ (when it was actually true)
```

**Queries:**
```python
# "What was John's role on 2025-10-16?"
role = seg.query_valid_time("John.role", at="2025-10-16")
# → Admin (VT covers 2025-10-16)

# "What did we know about John on 2025-10-20?"
knowledge = seg.query_transaction_time("John.role", at="2025-10-20")
# → Nothing (TT is 2025-10-21, not yet recorded)
```

---

## 🔧 **Implementation**

**Status:** 20% implemented

**Needed:**
- 🔄 Bitemporal query engine
- 🔄 VT update mechanism (corrections)
- 🔄 TT immutability enforcement
- 🔄 Temporal indexing (performance)

**Code:** (Needs implementation in `packages/seg/`)

---

**Parent:** [../../README.md](../../README.md)


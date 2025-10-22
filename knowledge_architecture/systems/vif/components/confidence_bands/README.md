# Confidence Bands

**Type:** VIF Component  
**Purpose:** Human-readable uncertainty (A/B/C transparency)  
**Status:** 50% Implemented ✅

---

## 🎯 **Quick Context (50 words)**

Confidence bands translate numeric confidence (0.0-1.0) into human-readable categories. Band A (0.95-1.00): High confidence, proceed. Band B (0.80-0.94): Medium, caution. Band C (<0.80): Low, review carefully or abstain. Appears in VIF witnesses, UI displays, audit logs. Foundation for transparent, interpretable AI uncertainty.

---

## 📊 **Context Budget**

**2k:** This README  
**4k:** L1_overview.md  
**16k:** L2_architecture.md

---

## 📦 **The 3 Bands**

### **Band A: High Confidence (0.95-1.00)**
**Meaning:** AI is very confident, proceed with confidence  
**Actions:** Accept output, minimal review needed  
**Use Cases:** Routine tasks, well-established patterns  
**Color:** 🟢 Green

### **Band B: Medium Confidence (0.80-0.94)**
**Meaning:** AI is moderately confident, proceed with caution  
**Actions:** Review output, verify key claims  
**Use Cases:** Important decisions, moderate complexity  
**Color:** 🟡 Yellow

### **Band C: Low Confidence (<0.80)**
**Meaning:** AI is uncertain, review carefully or abstain  
**Actions:** Thorough review, consider HITL escalation, may trigger κ-gate  
**Use Cases:** Critical decisions, high uncertainty  
**Color:** 🔴 Red

---

## 🔧 **Implementation**

**Status:** ✅ 50% Implemented (WORKS!)

**Working:**
- ✅ Band determination logic
- ✅ Band in VIF witnesses
- ✅ Basic testing

**Needed:**
- 🔄 UI visualization (color-coded displays)
- 🔄 Configurable thresholds (per-domain)
- 🔄 Band-based routing (auto-escalation for Band C)

**Code:**
```python
def determine_confidence_band(confidence: float) -> str:
    """Map numeric confidence to band"""
    if confidence >= 0.95:
        return "A"
    elif confidence >= 0.80:
        return "B"
    else:
        return "C"
```

---

**Parent:** [../../README.md](../../README.md)  
**Status:** ✅ Working, needs UI integration


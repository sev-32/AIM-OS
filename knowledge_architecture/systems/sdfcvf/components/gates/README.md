# Parity Gates

**Type:** SDF-CVF Component  
**Purpose:** Enforce P ≥ 0.90 at multiple checkpoints  
**Status:** 40% Implemented

---

## 🎯 **Quick Context (50 words)**

Parity gates are enforcement checkpoints: Pre-commit (local check), CI (pipeline validation), Deployment (production guard). Each calculates P, blocks if < 0.90, guides fixes. Prevents low-parity changes from entering codebase. Foundation for maintaining perpetual alignment across entire system.

---

## 📦 **The Three Gates**

### **1. Pre-Commit Gate**
**When:** Before developer commits  
**Action:** Calculate P for staged changes  
**Result:**  
- P ≥ 0.90: Allow commit  
- P < 0.90: Block, show which quartet elements misaligned

### **2. CI Gate**
**When:** In CI/CD pipeline (GitHub Actions, etc.)  
**Action:** Validate P for entire PR  
**Result:**  
- P ≥ 0.90: Tests pass  
- P < 0.90: Tests fail, block merge

### **3. Deployment Gate**
**When:** Before production deployment  
**Action:** Final P check on release candidate  
**Result:**  
- P ≥ 0.90: Deploy  
- P < 0.90: Reject deployment, rollback

---

## 📦 **Implementation**

```python
class ParityGate:
    """Enforce parity threshold"""
    
    def __init__(self, threshold: float = 0.90):
        self.threshold = threshold
    
    def check(self, change: Change) -> GateResult:
        """Run parity check"""
        # Calculate parity
        parity = calculate_parity(change)
        
        # Check threshold
        if parity >= self.threshold:
            return GateResult(
                status="PASS",
                parity=parity,
                message=f"Parity {parity:.2f} ≥ threshold {self.threshold}"
            )
        else:
            # Identify misaligned pairs
            misaligned = find_misaligned_pairs(change)
            
            return GateResult(
                status="FAIL",
                parity=parity,
                message=f"Parity {parity:.2f} < threshold {self.threshold}",
                misaligned_pairs=misaligned,
                suggested_fixes=suggest_alignment_fixes(misaligned)
            )
```

---

## 🔧 **Implementation Status**

**Status:** 40% implemented

**Working:**
- ✅ Parity calculation
- ✅ Threshold checking

**Needed:**
- 🔄 Pre-commit hook integration
- 🔄 CI pipeline integration (GitHub Actions)
- 🔄 Deployment gate (production check)
- 🔄 Automated fix suggestions

**Code:** `packages/parity_policy/` (partial)

---

**Parent:** [../../README.md](../../README.md)


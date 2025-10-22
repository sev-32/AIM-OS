# κ-Gating (Behavioral Abstention)

**Type:** VIF Component  
**Purpose:** Enforce "I don't know" when uncertain (prevent hallucinations)  
**Status:** 20% Implemented (Week 4 Priority!)

---

## 🎯 **Quick Context (50 words)**

κ (kappa) gating enforces behavioral abstention—AI must say "I don't know" when confidence < threshold, rather than guessing. Per-task thresholds: critical tasks (medical, legal) κ=0.95, important (code) κ=0.85, routine κ=0.70. Prevents hallucinations through enforced honesty. Escalates to HITL when uncertain. Foundation for trustworthy AI.

---

## 📊 **Context Budget**

**2k:** This README  
**4k:** L1_overview.md  
**16k:** L2_architecture.md

---

## 📦 **How κ-Gating Works**

**Algorithm:**
```python
def check_kappa_gate(
    output: Any,
    confidence: float,
    task_criticality: str
) -> GateResult:
    """Enforce abstention threshold"""
    
    # Determine κ threshold
    kappa_thresholds = {
        "critical": 0.95,    # Medical, legal, safety
        "important": 0.85,   # Code, data analysis
        "routine": 0.70      # Summarization, formatting
    }
    
    kappa = kappa_thresholds[task_criticality]
    
    # Check confidence
    if confidence < kappa:
        return GateResult(
            status="ABSTAIN",
            reason=f"Confidence {confidence:.2f} < κ threshold {kappa:.2f}",
            action="escalate_to_hitl"
        )
    else:
        return GateResult(
            status="PASS",
            confidence=confidence
        )
```

**Example:**
```python
# Medical diagnosis (critical task)
output = ai.diagnose(symptoms)
confidence = 0.82  # 82% confident

gate = check_kappa_gate(output, 0.82, "critical")
# κ_critical = 0.95
# 0.82 < 0.95 → ABSTAIN!

# Instead of returning uncertain diagnosis:
return "I don't have sufficient confidence (82%) to provide a diagnosis. 
        Threshold for medical tasks is 95%. Escalating to human expert."
```

---

## 🔧 **Implementation**

**Status:** 20% implemented (NEEDS WORK!)

**Working:**
- ✅ Basic concept documented
- ✅ Thresholds defined

**Needed:**
- 🔄 Confidence extraction from model outputs
- 🔄 Automated gate enforcement in APOE pipelines
- 🔄 HITL escalation workflow
- 🔄 Logging and audit trails

**Code:** (Needs to be added to `packages/apoe_runner/`)

---

**Parent:** [../../README.md](../../README.md)  
**Status:** Critical Week 4 work - prevents hallucinations!


# VIF L1: System Overview

**Detail Level:** 1 of 5 (500 words)  
**Context Budget:** ~8k tokens  
**Purpose:** Understand VIF architecture

---

## What Is VIF?

VIF (Verifiable Intelligence Framework) solves the AI trust problem—where you can't verify how an AI reached its conclusion, can't replay its reasoning, and can't quantify its uncertainty. VIF makes every AI operation fully traceable through witness envelopes containing complete provenance: model ID, weights hash, exact prompts, tools invoked, context snapshots, and uncertainty quantification. Combined with κ-gating (behavioral abstention), ECE tracking (calibration measurement), and deterministic replay, VIF transforms black-box AI into transparent, auditable, verifiable intelligence.

## The Core Innovation: Complete Provenance + Uncertainty

**Traditional AI (Black Box):**
```
Input → [AI magic happens] → Output

Questions:
- How did it decide?
- What data was used?
- How confident is it?
- Can we reproduce this?

Answers: Unknown 🤷
```

**VIF (Transparent):**
```
Input → [AI with VIF] → Output + Witness

Witness contains:
- model_id: "gpt-4-turbo-2025-01-15"
- weights_hash: "sha256:7f3e9a..."
- prompt_used: "[exact prompt text]"
- context_snapshot: [all input data, embeddings, retrievals]
- tools_invoked: ["hhni.retrieve", "cmc.store"]
- confidence_band: "A" (high confidence, 0.95-1.00)
- uncertainty: ECE=0.03 (well-calibrated)
- timestamp: "2025-10-21T20:00:00Z"
- replay_seed: 12345

Questions:
- How did it decide? → Check witness provenance
- What data was used? → context_snapshot
- How confident is it? → confidence_band + ECE
- Can we reproduce? → deterministic replay (same seed)

Answers: ALL KNOWN ✅
```

**This is verifiable AI!** Every operation has a complete paper trail.

---

## The Five Core Components

### 1. Witness Envelopes

**Complete provenance capture:**

**Structure:**
```python
@dataclass
class VIF:
    # What model
    model_id: str                      # "gpt-4-turbo-2025-01-15"
    weights_hash: str                  # SHA-256 of model weights
    
    # What data
    context_snapshot_id: str           # CMC snapshot reference
    prompt_hash: str                   # SHA-256 of exact prompt
    
    # What tools
    tool_ids: List[str]                # ["hhni.retrieve", "cmc.store"]
    
    # Uncertainty
    confidence_band: str               # "A" | "B" | "C"
    ece_score: float                   # Expected Calibration Error
    entropy: float                     # Output distribution entropy
    
    # Replay
    replay_seed: Optional[int]         # For deterministic reproduction
    
    # Meta
    writer: str                        # "system" | "user" | "agent_planner"
    created_at: datetime
```

**Every output gets one!** No exceptions.

---

### 2. κ-Gating (Behavioral Abstention)

**Enforce "I don't know" when uncertain:**

**Formula:**
```
If confidence(output) < κ_threshold:
    → ABSTAIN (escalate to HITL, don't guess)
Else:
    → PROCEED
```

**κ per task:**
- Critical (medical, legal): κ = 0.95 (very high bar)
- Important (code generation): κ = 0.85
- Routine (summarization): κ = 0.70

**Prevents hallucinations!** Forces honesty about uncertainty.

---

### 3. ECE Tracking (Calibration)

**Measure how well confidence matches accuracy:**

**Expected Calibration Error:**
```
ECE = Σ |confidence - actual_accuracy| / N

Target: ECE ≤ 0.05 (well-calibrated)
```

**Example:**
- AI says 90% confident on 100 predictions
- 85 turn out correct (85% accuracy)
- Gap: 90% - 85% = 5%
- ECE = 0.05 ✅ (acceptable!)

**Poor calibration (ECE > 0.10):**
- AI says 90% confident
- Only 60% correct
- Gap: 30%
- ECE = 0.30 ❌ (overconfident!)

**Continuous monitoring!** Track ECE over time, flag degradation.

---

### 4. Deterministic Replay

**Reproduce exact outputs:**

**Method:**
1. Store replay_seed in VIF
2. Store exact context snapshot (CMC)
3. Store exact prompt/params
4. To replay: Use same seed + context + prompt
5. Result: Bit-identical output!

**Enables:**
- Debugging ("why did it do that?")
- Auditing (verify outputs)
- Regression testing (outputs stable?)

---

### 5. Confidence Bands

**Human-readable uncertainty:**

**Band A (High):** 0.95-1.00 - Proceed with confidence  
**Band B (Medium):** 0.80-0.94 - Proceed with caution  
**Band C (Low):** <0.80 - Review carefully or abstain  

**In VIF witness:**
```python
vif.confidence_band = "A"  # Clear signal to humans
```

---

## Integration Points

**VIF Witnesses:**
- CMC operations (every atom has VIF)
- HHNI retrieval (witness contains retrieval provenance)
- APOE execution (every step emits VIF)
- All AI outputs!

**VIF Feeds:**
- SEG (witnesses become graph nodes)
- Audit logs (full trails)
- Debug systems (replay capability)

**VIF Enables:**
- SDF-CVF (parity tracking requires provenance)
- Trust (transparency builds confidence)
- Compliance (audit requirements met)

---

## Current Status

**Implementation:** 30% complete (Week 4 priority!)  
**Tests:** Basic witness creation working  
**Code:** `packages/seg/witness.py`

**Week 4 Targets:**
- ✅ Complete ECE calculation
- ✅ Implement κ-gating (behavioral, not just prompts)
- ✅ Enable deterministic replay
- ✅ Confidence band automation

---

## Key Concepts

**Witness:** Complete provenance envelope (who/what/when/how)  
**κ-Gating:** Abstention threshold (honesty about uncertainty)  
**ECE:** Calibration metric (confidence vs accuracy)  
**Replay:** Deterministic reproduction (bit-identical)  
**Bands:** Human-readable uncertainty (A/B/C)

---

**Parent:** [../../README.md](../../README.md)  
**Status:** 30% implemented, critical Week 4 work

**PATTERN CONTINUES - VIF DOCUMENTED!** ✅


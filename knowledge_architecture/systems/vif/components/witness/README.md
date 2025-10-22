# Witness Envelopes

**Type:** VIF Component  
**Purpose:** Complete provenance capture for all AI operations  
**Status:** 40% Implemented

---

## 🎯 **Quick Context (50 words)**

Witness envelopes are VIF's core—complete provenance for every AI operation. Contains model ID, weights hash, exact prompts, context snapshots, tools invoked, uncertainty metrics, timestamps. Every CMC atom has VIF, every HHNI retrieval emits witness, every APOE step traced. Foundation for verifiable, auditable, replay-capable AI. Trust through transparency.

---

## 📊 **Context Budget**

**2k:** This README  
**4k:** L1_overview.md  
**16k:** L2_architecture.md

---

## 📦 **Witness Structure**

```python
@dataclass
class VIF:
    """Verifiable Intelligence Framework witness envelope"""
    
    # === WHAT MODEL ===
    model_id: str                      # "gpt-4-turbo-2025-01-15"
    weights_hash: str                  # SHA-256 of weights file
    
    # === WHAT DATA ===
    context_snapshot_id: str           # CMC snapshot reference
    prompt_hash: str                   # SHA-256 of exact prompt
    retrieved_atom_ids: List[str]      # HHNI retrieval results
    
    # === WHAT TOOLS ===
    tool_ids: List[str]                # ["hhni.retrieve", "cmc.store"]
    tool_parameters: Dict[str, Any]    # Exact params used
    
    # === UNCERTAINTY ===
    confidence_band: str               # "A" | "B" | "C"
    confidence_score: float            # 0.0-1.0
    ece_score: Optional[float]         # Expected Calibration Error
    entropy: float                     # Output distribution entropy
    
    # === REPLAY ===
    replay_seed: Optional[int]         # Deterministic reproduction
    temperature: float                 # Generation parameter
    
    # === META ===
    writer: str                        # "system" | "user" | "agent_X"
    created_at: datetime
    parent_vif_id: Optional[str]       # Chain of witnesses
```

---

## 🔧 **Implementation**

**Status:** 40% implemented

**Working:**
- ✅ Basic witness creation
- ✅ Model ID tracking
- ✅ Timestamp recording

**Needed:**
- 🔄 Weights hash calculation (verify model version)
- 🔄 Context snapshot linkage (CMC integration)
- 🔄 Tool tracking (capture all external calls)
- 🔄 ECE calculation (calibration)

**Code:** `packages/seg/witness.py`

---

**Parent:** [../../README.md](../../README.md)  
**Status:** Core component, Week 4 target


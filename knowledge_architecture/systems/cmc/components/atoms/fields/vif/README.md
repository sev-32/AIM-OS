# VIF Field - Witness Envelope (Provenance)

**Field of:** Atom  
**Type:** Pydantic Model  
**Purpose:** Record how atom was created (provenance)  
**Status:** ✅ Implemented, evolving (Week 4 enhancements)

---

## 🎯 **Quick Context (50 words)**

VIF (Verifiable Intelligence Framework) witness envelope captures atom creation provenance: which model, what prompt, which tools, confidence level. Enables replay, audit, trust. Includes confidence bands (A/B/C), entropy measure, weights hash. Immutable once created. Foundation for verifiable AI outputs.

---

## 📦 **Fields**

| Field | Type | Purpose |
|-------|------|---------|
| `model_id` | str | LLM identifier (gpt-4, claude-sonnet-4.5) |
| `weights_hash` | Optional[str] | Model version |
| `prompt_template_id` | Optional[str] | Prompt used |
| `tool_ids` | List[str] | Tools invoked |
| `writer` | str | System/user identifier |
| `confidence_band` | Optional[str] | A/B/C rating |
| `entropy` | Optional[float] | Uncertainty (0.0+) |

---

## 🎯 **Confidence Bands**

**Band A (High Confidence):**
- Confidence ≥ 0.8
- Low entropy (< 0.15)
- Use: Ship it, trust it

**Band B (Medium Confidence):**
- Confidence 0.5-0.8
- Medium entropy (0.15-0.6)
- Use: Review recommended

**Band C (Low Confidence):**
- Confidence < 0.5
- High entropy (> 0.6)
- Use: Must verify or abstain

---

## 🔧 **Usage**

```python
vif = VIF(
    model_id="gpt-4-turbo",
    prompt_template_id="code_review_v2",
    tool_ids=["ast_parser", "linter"],
    writer="system",
    confidence_band="A",
    entropy=0.12
)

atom = Atom(..., vif=vif)
```

**Enables:**
- Deterministic replay (same model + prompt + snapshot)
- Audit trails (who/what/when/how)
- Trust scoring (confidence bands)
- κ-gating (abstain if Band C)

---

## 🔗 **Relationships**

**VIF connects to:**
- **APOE:** Execution traces store VIF
- **SEG:** Witnesses become graph nodes
- **κ-gating:** Band C triggers abstention
- **Replay:** VIF enables deterministic reproduction

---

**Parent:** [../../README.md](../../README.md)  
**Week 4 Priority:** ECE tracking, replay system, adaptive κ


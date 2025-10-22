# Tags Field - Semantic Categorization

**Field of:** Atom  
**Type:** List[Tag]  
**Purpose:** Categorize and filter atoms by attributes  
**Status:** ✅ Fully Implemented

---

## 🎯 **Quick Context (50 words)**

Tags provide flexible categorization: key-value pairs with weights and confidence. Enable queries like "find high-priority authentication atoms." Includes TPV (Tag Priority Vector) for decay-based relevance. System tags (auto), user tags (manual), AI tags (inferred). Mutable - can evolve over time.

---

## 📦 **Tag Schema**

```python
class Tag(BaseModel):
    key: str           # "topic", "priority", "author"
    value: str         # "auth", "high", "alice"
    weight: float      # 0.0-1.0 importance
    confidence: float  # 0.0-1.0 certainty (optional)
```

---

## 📊 **Tag Types**

**System (Auto-generated):**
```python
Tag(key="modality", value="code", weight=1.0)
Tag(key="language", value="python", weight=1.0)
```

**User (Manual):**
```python
Tag(key="topic", value="authentication", weight=0.9)
Tag(key="priority", value="high", weight=1.0)
```

**AI (Inferred):**
```python
Tag(key="sentiment", value="positive", weight=0.7, confidence=0.85)
Tag(key="entity", value="OAuth2", weight=0.6, confidence=0.75)
```

---

## 🔧 **TPV (Tag Priority Vector)**

```python
class TPV(BaseModel):
    priority: float      # Overall importance
    relevance: float     # Current relevance
    decay_tau: int       # Decay time constant (seconds)
    last_accessed: datetime
```

**Decay Formula:**
```
relevance(t) = relevance₀ × exp(-(t - t₀) / τ)
```

**Prevents:** Old atoms from dominating searches  
**Enables:** Fresh content prioritization

---

**Parent:** [../../README.md](../../README.md)  
**Related:** TPV decay mechanism, tag querying


# Activation Tracking Component

**Parent System:** Cognitive Analysis System (CAS)  
**Purpose:** Monitor what's "hot" (actively used) vs "cold" (available but inactive) in AI attention  
**Status:** Designed, ready for implementation  

---

## 🎯 **QUICK SUMMARY (100 words)**

Activation Tracking monitors which principles, documents, and concepts are currently active in AI's working attention versus stored but inactive. After hours of intensive work, distant principles may have low activation despite remaining relevant. Tracks recency (when last used), frequency (how often used), salience (relevance to current task), and cognitive load impact. Calculates activation levels (0.0-1.0) using temporal decay and attention competition. Identifies "cold but needed" gaps where required principles aren't activated. Enables predictive retrieval (know when to explicitly load principles) and attention-aware operation (understand cognitive state).

---

## 🔧 **CORE CAPABILITIES**

```yaml
activation_calculation:
  - Recency scoring (temporal decay)
  - Frequency tracking (usage patterns)
  - Salience estimation (semantic relevance)
  - Load-aware suppression (attention competition)

state_snapshot:
  - Principles activation map
  - Documents activation map
  - Concepts activation map
  - Working attention count

gap_detection:
  - Required but cold principles
  - Activation failures
  - Retrieval recommendations
```

---

## 📊 **KEY DATA STRUCTURES**

### **ActivationState**
```python
@dataclass
class ActivationState:
    principles_activation: Dict[str, float]  # 0.0-1.0
    documents_activation: Dict[str, float]
    working_attention_items: int
    load_level: float
```

### **ActivationTracker**
```python
class ActivationTracker:
    def record_principle_use(self, principle: str)
    def calculate_activation(self, item: str) -> float
    def capture_state(self) -> ActivationState
```

---

## 🔗 **INTEGRATION**

**With CAS:**
- Used by CognitiveAnalyst for hourly checks
- Feeds into failure detection (activation gaps)
- Combined with attention state for analysis

**With VIF:**
- Enhanced witnesses include activation state
- Provenance shows which principles were active

**With CMC:**
- Store activation snapshots as atoms
- Track activation patterns over time

---

## 📚 **DOCUMENTATION**

- **Parent:** [CAS Overview](../../README.md)
- **L2:** [CAS Architecture](../../L2_architecture.md#activation-tracking)
- **L3:** [Implementation Guide](../../L3_detailed.md#activation-tracking)
- **L4:** [Complete Reference](../../L4_complete.md#activationtracker)

---

## 🧪 **TESTING**

```bash
pytest packages/cas/tests/test_activation.py -v
```

**Key tests:**
- Activation decay over time
- Cognitive load suppression
- Cold-but-needed detection
- Frequency tracking

---

## 🎯 **USAGE EXAMPLE**

```python
from cas.activation import ActivationTracker

tracker = ActivationTracker("session_001")

# Record usage
tracker.record_principle_use("CMC_bitemporal")

# Check activation
state = tracker.capture_state(current_task="Update priorities")
if state.is_cold("CMC_bitemporal"):
    # Retrieve explicitly
```

---

**Status:** Ready for implementation  
**Priority:** High (prevents activation gaps)  
**Estimated effort:** 3-4 hours



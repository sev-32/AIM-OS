# Attention Monitoring Component

**Parent System:** Cognitive Analysis System (CAS)  
**Purpose:** Track cognitive load, attention breadth, and warning signs of degradation  
**Status:** Designed, ready for implementation  

---

## 🎯 **QUICK SUMMARY (100 words)**

Attention Monitoring tracks cognitive load and quality degradation over long autonomous sessions. Monitors session duration, task juggling, completion intensity, error rates, and context utilization to estimate load (0.0-1.0). Detects five warning signs: attention narrowing, shortcuts appearing, impatience, principle forgetting, quality degradation. Predicts time to overload using trend analysis. Recommends actions (continue, break, task switch, checkpoint) based on load and warnings. Enables sustainable long-session operation through early warning before quality degrades. Core insight: Cognitive debt accumulates over time - systematic monitoring prevents degradation.

---

## 🔧 **CORE CAPABILITIES**

```yaml
load_calculation:
  - Duration factor (session length)
  - Task factor (concurrent juggling)
  - Intensity factor (completion rate)
  - Error factor (mistake frequency)
  - Context factor (utilization)

warning_detection:
  - Attention narrowing (focus tightening)
  - Shortcuts appearing (step skipping)
  - Impatience (rush to complete)
  - Principle forgetting (not applying known rules)
  - Quality degradation (less careful)

predictions:
  - Time to overload (trend extrapolation)
  - Recommended actions (continue/break/checkpoint)
  - Attention breadth evolution
```

---

## 📊 **KEY DATA STRUCTURES**

### **AttentionState**
```python
@dataclass
class AttentionState:
    cognitive_load: float  # 0.0-1.0
    attention_breadth: str  # narrow | focused | broad | comprehensive
    attention_narrowing: bool
    shortcuts_appearing: bool
    impatience_detected: bool
    principle_forgetting: bool
    quality_degradation: bool
    time_to_overload: Optional[timedelta]
    recommended_action: str
```

**Methods:**
- `warning_count() -> int` - Count active warning signs
- `is_overloaded() -> bool` - Check if critical

### **AttentionMonitor**
```python
class AttentionMonitor:
    def calculate_load(self, context_tokens) -> float
    def capture_state(self, context_tokens, recent_ops) -> AttentionState
    def record_completion(self)
    def record_error(self)
```

---

## ⚠️ **WARNING SIGNS**

```yaml
1. Attention Narrowing:
   symptom: Load increasing over time
   detection: Load history trend analysis
   action: Widen focus or take break

2. Shortcuts Appearing:
   symptom: "Quick edit", "skip tests" language
   detection: Keyword analysis in operations
   action: Force full rigor

3. Impatience:
   symptom: "Just get it done" thoughts
   detection: High intensity + shortcuts
   action: Slow down, apply procedures

4. Principle Forgetting:
   symptom: Not applying known rules
   detection: Activation gaps + violations
   action: Explicit principle retrieval

5. Quality Degradation:
   symptom: Less careful than usual
   detection: Error rate increase
   action: Checkpoint and review
```

---

## 📈 **LOAD THRESHOLDS**

```yaml
< 0.50: LOW - Comfortable operating range
0.50-0.70: MEDIUM - Normal load, monitor trends
0.70-0.85: HIGH - Watch for degradation signs
0.85-0.95: CRITICAL - Recommend break
> 0.95: OVERLOAD - Mandatory checkpoint
```

---

## 🔗 **INTEGRATION**

**With CAS:**
- Combined with activation state in introspection
- Used for failure detection (blind spot mode)
- Influences recommended actions

**With VIF:**
- Attention state included in enhanced witnesses
- Load affects confidence calibration (meta-confidence)

**With Hourly Checks:**
- Primary quality indicator
- Triggers preventive action

---

## 📚 **DOCUMENTATION**

- **Parent:** [CAS Overview](../../README.md)
- **L2:** [CAS Architecture](../../L2_architecture.md#attention-monitoring)
- **L3:** [Implementation Guide](../../L3_detailed.md#attention-monitoring)
- **L4:** [Complete Reference](../../L4_complete.md#attentionmonitor)

---

## 🧪 **TESTING**

```bash
pytest packages/cas/tests/test_attention.py -v
```

**Key tests:**
- Load increases with duration
- Overload detection
- Time-to-overload prediction
- Warning sign detection

---

## 🎯 **USAGE EXAMPLE**

```python
from cas.attention import AttentionMonitor

monitor = AttentionMonitor("session_001")

# Track work
monitor.begin_task()
# ... work ...
monitor.end_task()

# Capture state
state = monitor.capture_state(
    context_tokens=50000,
    recent_operations=["built VIF", "wrote tests"]
)

if state.cognitive_load > 0.70:
    print(f"⚠️ High load: {state.cognitive_load:.2f}")
    print(f"Action: {state.recommended_action}")
```

---

**Status:** Ready for implementation  
**Priority:** High (prevents degradation)  
**Estimated effort:** 2-3 hours



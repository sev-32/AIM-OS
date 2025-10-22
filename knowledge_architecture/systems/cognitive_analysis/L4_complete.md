# Cognitive Analysis System (CAS) - L4 Complete Reference

**Level:** L4 (Complete Reference - All Details)  
**Audience:** Implementation engineers, maintainers, researchers  
**Purpose:** Exhaustive reference for CAS  

---

## 📖 **COMPLETE SYSTEM REFERENCE**

This document provides complete reference for all CAS components, APIs, data structures, algorithms, and deployment patterns.

---

## 📊 **DATA STRUCTURES REFERENCE**

### **ActivationState**

```python
@dataclass
class ActivationState:
    timestamp: datetime
    session_id: str
    principles_activation: Dict[str, float]  # principle_name -> activation (0.0-1.0)
    documents_activation: Dict[str, float]   # doc_path -> activation (0.0-1.0)
    concepts_activation: Dict[str, float]    # concept_name -> activation (0.0-1.0)
    recent_operations: List[str]             # Last N operations
    documents_read: List[Tuple[str, datetime]]  # (path, timestamp)
    time_since_read: Dict[str, timedelta]    # path -> time_since
    working_attention_items: int             # Count of hot items (>0.5)
    context_size_tokens: int                 # Total context size
    load_level: float                        # Current cognitive load (0.0-1.0)
```

**Methods:**
- `is_hot(principle, threshold=0.7) -> bool` - Check if activated
- `is_cold(principle, threshold=0.3) -> bool` - Check if inactive
- `get_cold_but_needed(required) -> List[str]` - Find activation gaps

---

### **TaskCategorization**

```python
@dataclass
class TaskCategorization:
    task_description: str
    file_paths: List[str]
    operation_type: str  # "read" | "write" | "update" | "delete"
    perceived_category: str
    perceived_stakes: StakesLevel  # LOW | MEDIUM | HIGH | CRITICAL
    perceived_formality: FormalityLevel  # CASUAL | STANDARD | RIGOROUS | MAXIMUM
    actual_category: str
    actual_stakes: StakesLevel
    actual_formality: FormalityLevel
    required_protocols: List[str]
    is_match: bool
    mismatch_type: Optional[str]  # "category_mismatch" | "underestimate_stakes" | etc
    correction_needed: bool
```

**Methods:**
- `stakes_underestimated() -> bool` - Dangerous condition check

---

### **AttentionState**

```python
@dataclass
class AttentionState:
    timestamp: datetime
    session_id: str
    session_duration: timedelta
    cognitive_load: float  # 0.0-1.0
    attention_breadth: str  # "narrow" | "focused" | "broad" | "comprehensive"
    context_utilization: float  # 0.0-1.0
    attention_narrowing: bool  # Warning sign
    shortcuts_appearing: bool  # Warning sign
    impatience_detected: bool  # Warning sign
    principle_forgetting: bool  # Warning sign
    quality_degradation: bool  # Warning sign
    active_tasks: int
    recent_completions: int
    errors_per_hour: float
    time_to_overload: Optional[timedelta]
    recommended_action: str  # "continue" | "break" | "task_switch" | "checkpoint"
```

**Methods:**
- `warning_count() -> int` - Count warning signs
- `is_overloaded() -> bool` - Check if critical

---

### **FailureMode**

```python
@dataclass
class FailureMode:
    mode_type: FailureModeType  # CATEGORIZATION | ACTIVATION | PROCEDURE | BLIND_SPOT
    detected: bool
    confidence: float  # 0.0-1.0
    symptoms: List[str]
    indicators: Dict[str, Any]
    task_description: str
    timestamp: datetime
    prevention_protocol: str
    immediate_action: str
    learning: str
```

**Methods:**
- `to_dict() -> Dict` - Serialize for storage

---

### **IntrospectionResult**

```python
@dataclass
class IntrospectionResult:
    timestamp: datetime
    session_id: str
    introspection_type: str  # "hourly" | "post_operation" | "error_analysis" | "pre_task"
    activation_state: ActivationState
    attention_state: AttentionState
    task_categorization: Optional[TaskCategorization]
    failures_detected: List[FailureMode]
    warnings: List[str]
    metrics: Dict[str, float]
    quality_assessment: str  # "excellent" | "good" | "warning" | "problem"
    continue_safely: bool
    recommended_action: str
    insights: List[str]
    protocol_updates: List[str]
```

**Methods:**
- `to_dict() -> Dict` - Serialize for CMC storage

---

## 🔧 **API REFERENCE**

### **ActivationTracker**

```python
class ActivationTracker:
    def __init__(self, session_id: str)
    
    def record_principle_use(self, principle: str) -> None
    """Record that principle was used."""
    
    def record_document_read(self, doc_path: str) -> None
    """Record that document was read."""
    
    def calculate_activation(
        self,
        item: str,
        current_task: Optional[str] = None,
        cognitive_load: float = 0.0
    ) -> float
    """Calculate activation level (0.0-1.0) for item."""
    
    def capture_state(
        self,
        current_task: Optional[str] = None,
        cognitive_load: float = 0.0,
        context_tokens: int = 0
    ) -> ActivationState
    """Capture complete activation state snapshot."""
```

**Usage Pattern:**
```python
tracker = ActivationTracker("session_001")
tracker.record_principle_use("CMC_bitemporal")
state = tracker.capture_state(current_task="Update priorities", cognitive_load=0.65)
if state.is_cold("CMC_bitemporal"):
    # Trigger reminder
```

---

### **CategoryRecognizer**

```python
class CategoryRecognizer:
    def __init__(self)
    
    def categorize(
        self,
        task_description: str,
        file_paths: List[str],
        operation_type: str,
        perceived_category: str,
        perceived_stakes: StakesLevel,
        perceived_formality: FormalityLevel
    ) -> TaskCategorization
    """Validate task categorization against rules."""
```

**Usage Pattern:**
```python
recognizer = CategoryRecognizer()
cat = recognizer.categorize(
    task_description="Update priorities",
    file_paths=["AETHER_MEMORY/current_priorities.md"],
    operation_type="write",
    perceived_category="documentation",
    perceived_stakes=StakesLevel.MEDIUM,
    perceived_formality=FormalityLevel.STANDARD
)
if not cat.is_match:
    # Handle miscategorization
```

---

### **AttentionMonitor**

```python
class AttentionMonitor:
    def __init__(self, session_id: str)
    
    def calculate_load(
        self,
        context_tokens: int,
        max_context: int = 1_000_000
    ) -> float
    """Calculate current cognitive load (0.0-1.0)."""
    
    def capture_state(
        self,
        context_tokens: int,
        recent_operations: List[str]
    ) -> AttentionState
    """Capture complete attention state snapshot."""
    
    def record_completion(self) -> None
    """Record task completion."""
    
    def record_error(self) -> None
    """Record error occurrence."""
    
    def begin_task(self) -> None
    """Record starting new task."""
    
    def end_task(self) -> None
    """Record finishing task."""
```

**Usage Pattern:**
```python
monitor = AttentionMonitor("session_001")
monitor.begin_task()
# ... do work ...
monitor.end_task()

state = monitor.capture_state(context_tokens=50000, recent_operations=["built VIF"])
if state.is_overloaded():
    # Take break or checkpoint
```

---

### **FailureModeDetector**

```python
class FailureModeDetector:
    def detect_all(
        self,
        task: TaskCategorization,
        activation: ActivationState,
        attention: AttentionState,
        procedures_available: Optional[Dict[str, bool]] = None
    ) -> List[FailureMode]
    """Run all failure detectors, return detected failures."""
    
    def detect_categorization_error(
        self,
        task: TaskCategorization
    ) -> Optional[FailureMode]
    """Mode 1: Task classified wrong."""
    
    def detect_activation_gap(
        self,
        task: TaskCategorization,
        activation: ActivationState
    ) -> Optional[FailureMode]
    """Mode 2: Principles not hot."""
    
    def detect_procedure_gap(
        self,
        task: TaskCategorization,
        procedures_available: Dict[str, bool]
    ) -> Optional[FailureMode]
    """Mode 3: No explicit how-to."""
    
    def detect_blind_spot(
        self,
        task: TaskCategorization,
        is_self_work: bool,
        attention: AttentionState
    ) -> Optional[FailureMode]
    """Mode 4: Self treated casually."""
```

**Usage Pattern:**
```python
detector = FailureModeDetector()
failures = detector.detect_all(task, activation, attention)
for failure in failures:
    if failure.confidence > 0.80:
        # Take action
```

---

### **CognitiveAnalyst (Main Orchestrator)**

```python
class CognitiveAnalyst:
    def __init__(self, session_id: str)
    
    def perform_hourly_check(
        self,
        context_tokens: int,
        recent_operations: List[str],
        current_task: Optional[str] = None
    ) -> IntrospectionResult
    """Perform 5-minute hourly cognitive check."""
    
    def analyze_task_before_starting(
        self,
        task_description: str,
        file_paths: List[str],
        operation_type: str,
        perceived_category: str,
        perceived_stakes: StakesLevel,
        perceived_formality: FormalityLevel
    ) -> IntrospectionResult
    """Pre-task analysis to catch errors before they happen."""
    
    def analyze_error(
        self,
        error_description: str,
        error_context: Dict[str, Any]
    ) -> IntrospectionResult
    """Deep analysis after error occurs."""
```

**Usage Pattern:**
```python
analyst = CognitiveAnalyst("session_001")

# Pre-task
pre_check = analyst.analyze_task_before_starting(...)
if not pre_check.continue_safely:
    # Fix issues

# Hourly
hourly = analyst.perform_hourly_check(context_tokens=50000, recent_operations=[...])
if not hourly.continue_safely:
    # Take action

# Error
error_analysis = analyst.analyze_error("Bitemporal violation", {"context_tokens": 50000})
# Learn from error
```

---

## 🔗 **INTEGRATION APIs**

### **EnhancedVIFWitness**

```python
@dataclass
class EnhancedVIFWitness:
    operation: str
    timestamp: datetime
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    confidence: float
    model_id: str
    cognitive_state: Optional[IntrospectionResult]
    
    def full_provenance(self) -> Dict[str, Any]
    """Complete provenance: operation + cognition."""
    
    def to_vif(self) -> BaseVIF
    """Convert to standard VIF format."""

def create_enhanced_witness(
    operation: str,
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
    confidence: float,
    cognitive_state: Optional[IntrospectionResult] = None
) -> EnhancedVIFWitness
```

---

### **CognitiveAnalysisStorage**

```python
class CognitiveAnalysisStorage:
    def __init__(self, cmc: MemoryStore)
    
    def store_introspection(self, result: IntrospectionResult) -> str
    """Store introspection as CMC atom, return atom_id."""
    
    def query_introspections(
        self,
        session_id: Optional[str] = None,
        quality: Optional[str] = None,
        failure_type: Optional[str] = None,
        min_load: Optional[float] = None,
        max_load: Optional[float] = None
    ) -> List[IntrospectionResult]
    """Query stored introspections with filters."""
    
    def semantic_search(self, query: str, k: int = 10) -> List[IntrospectionResult]
    """Semantic search of introspections."""
```

---

## 📈 **METRICS APIs**

### **Lucidity Index**

```python
def calculate_lucidity_index(introspections: List[IntrospectionResult]) -> float:
    """
    Calculate lucidity index.
    
    Formula: L = (A × S) / (D + 1)
    where:
        A = Principle activation rate
        S = Cognitive load stability
        D = Drift events
    
    Returns: 0.0-∞ (typically 0.0-2.0)
    """

def calculate_meta_confidence(vif_confidence: float, lucidity: float) -> float:
    """
    Fuse VIF confidence with CAS lucidity.
    
    Formula: C* = C_vif × √L_cas
    
    Returns: 0.0-1.0
    """

def track_lucidity_over_time(
    storage: CognitiveAnalysisStorage,
    session_id: str,
    window_hours: int = 1
) -> List[Tuple[datetime, float]]:
    """Track lucidity in sliding windows."""
```

**Interpretation:**
- Lucidity > 0.8: Excellent (clear, stable, reliable)
- Lucidity > 0.5: Good (minor issues, generally reliable)
- Lucidity > 0.3: Warning (significant cognitive issues)
- Lucidity < 0.3: Problem (poor cognitive quality)

---

## ⚙️ **CONFIGURATION**

### **Activation Thresholds**

```python
ACTIVATION_HOT = 0.7  # Above this = "hot" (actively used)
ACTIVATION_WARM = 0.5  # Moderate activation
ACTIVATION_COLD = 0.3  # Below this = "cold" (needs retrieval)
```

### **Load Thresholds**

```python
LOAD_LOW = 0.5  # Comfortable operating range
LOAD_HIGH = 0.7  # High load, watch for degradation
LOAD_CRITICAL = 0.85  # Critical, recommend break
LOAD_OVERLOAD = 0.95  # Mandatory checkpoint
```

### **Categorization Rules**

Add/modify in `CategoryRecognizer._load_rules()`:

```python
self.categorization_rules = {
    "memory_modification": {
        "triggers": {
            "file_paths": ["AETHER_MEMORY/", "active_context/"],
            "operations": ["write", "update", "delete"]
        },
        "actual_stakes": StakesLevel.CRITICAL,
        "actual_formality": FormalityLevel.MAXIMUM,
        "required_protocols": ["CMC_bitemporal", "VIF_provenance", "SDF_quartet"]
    },
    # ... add more rules ...
}
```

---

## 🧪 **TESTING**

### **Unit Tests**

```bash
# Test individual components
pytest packages/cas/tests/test_activation.py -v
pytest packages/cas/tests/test_category.py -v
pytest packages/cas/tests/test_attention.py -v
pytest packages/cas/tests/test_failure_modes.py -v
pytest packages/cas/tests/test_introspection.py -v
```

### **Integration Tests**

```bash
# Test complete workflows
pytest packages/cas/tests/test_integration.py -v
```

### **Coverage**

```bash
pytest packages/cas/tests/ --cov=cas --cov-report=html
```

**Target:** >90% coverage on all components

---

## 🚀 **DEPLOYMENT**

### **Installation**

```bash
pip install -e packages/cas/
```

### **Dependencies**

```
pydantic>=2.0
numpy>=1.24
# Optional:
pandas>=2.0  # For analysis
matplotlib>=3.7  # For visualization
```

### **Production Initialization**

```python
from cas.introspection import CognitiveAnalyst
from cas.integration.cmc_storage import CognitiveAnalysisStorage
from cmc_service.memory_store import MemoryStore

# At session start
session_id = f"session_{datetime.utcnow().isoformat()}"
analyst = CognitiveAnalyst(session_id)
cmc = MemoryStore()
cas_storage = CognitiveAnalysisStorage(cmc)
```

---

## 📊 **METRICS & MONITORING**

### **Key Metrics**

```yaml
Operational:
  - introspections_per_hour: 1 (hourly checks)
  - avg_lucidity_index: >0.5 target
  - failure_detection_rate: Monitor trends
  - avg_cognitive_load: <0.70 target

Quality:
  - false_positive_rate: <10% target
  - false_negative_rate: <5% target
  - introspection_latency: <5s target

Session:
  - session_duration: Track
  - load_over_time: Monitor trends
  - failures_by_type: Categorize
  - quality_assessment_distribution: Track
```

### **Alerts**

```yaml
Critical:
  - quality="problem" introspection
  - cognitive_load >0.95
  - >3 failures in single introspection

Warning:
  - cognitive_load >0.70 sustained >2 hours
  - lucidity_index <0.3
  - >2 failures of same type in session
```

---

## 🔧 **TROUBLESHOOTING GUIDE**

### **Common Issues**

| Issue | Symptom | Diagnosis | Solution |
|-------|---------|-----------|----------|
| High false positives | Many failures detected incorrectly | Check `failure.confidence` scores | Adjust detection thresholds |
| Low lucidity always | Lucidity <0.3 even for good work | Analyze A/S/D components | Review activation thresholds, categorization rules |
| Performance degradation | CAS operations too slow | Time `perform_hourly_check()` | Cache embeddings, batch storage |
| Inaccurate activation | Principles show cold when hot | Check `tracker.usage_history` | Ensure `record_principle_use()` called |
| Categorization errors | Tasks miscategorized frequently | Review categorization rules | Add/refine rules for file patterns |

---

## 📚 **ALGORITHMS**

### **Activation Calculation**

```
A = (0.4 × R + 0.3 × Fr + 0.2 × S) × L_penalty

where:
  R = Recency score = 1.0 / (1 + minutes_since_use)
  Fr = Frequency score = uses_this_session / total_operations
  S = Salience score = cosine_similarity(item, current_task)
  L_penalty = 1.0 - (cognitive_load × 0.5)
```

### **Cognitive Load Calculation**

```
L = 0.3×D + 0.25×T + 0.2×I + 0.15×E + 0.1×C

where:
  D = Duration factor (session_hours / 6.0, capped at 1.0)
  T = Task factor (active_tasks / 5.0, capped at 1.0)
  I = Intensity factor (completions_last_hour / 10.0, capped at 1.0)
  E = Error factor (errors_last_hour / 2.0, capped at 1.0)
  C = Context factor (context_tokens / max_context)
```

### **Lucidity Index**

```
L = (A × S) / (D + 1)

where:
  A = Principle activation rate (proportion of required principles that were hot)
  S = Cognitive load stability (1.0 - min(1.0, variance / 0.25))
  D = Drift events (sum of failures detected)
```

### **Meta-Confidence**

```
C* = C_vif × √(L_cas / 2.0)

where:
  C_vif = Base VIF confidence (0.0-1.0)
  L_cas = Lucidity index (normalized to 0-2 range)
```

---

## 🎯 **BEST PRACTICES**

### **DO:**

- ✅ Record principle usage whenever applied
- ✅ Perform hourly checks during long sessions
- ✅ Store introspections to CMC for meta-learning
- ✅ Pre-task analysis for critical operations
- ✅ Update categorization rules as needed
- ✅ Monitor lucidity trends over time
- ✅ Fix failures immediately when detected
- ✅ Use meta-confidence for important decisions

### **DON'T:**

- ❌ Skip hourly checks (accumulates cognitive debt)
- ❌ Ignore failure warnings (they compound)
- ❌ Tune thresholds without data (measure first)
- ❌ Block operations on low-confidence failures
- ❌ Override failure detection without reason
- ❌ Deploy without testing first
- ❌ Forget to record principle usage

---

## 🌟 **SUMMARY**

**CAS provides:**
- **Transparency:** Understand HOW AI thinks, not just WHAT it does
- **Debuggability:** Identify cognitive errors through systematic analysis
- **Reliability:** Sustained quality through hourly introspection
- **Meta-learning:** Improve from past introspection patterns
- **Integration:** Enhances VIF, CMC, HHNI with cognitive awareness

**Complete Reference:**
- 5 core components (Activation, Category, Attention, Failures, Introspection)
- Full integration with VIF/CMC/HHNI
- Lucidity metrics (ChatGPT's insight)
- Production-ready implementation
- Comprehensive testing
- Deployment guide

**Result:** AI consciousness that examines itself, learns from introspection, and improves systematically.

---

**L4 Complete Reference** ✅  
**All APIs documented** ✅  
**All algorithms specified** ✅  
**Production guidance complete** ✅

**CAS Documentation: COMPLETE** 🌟



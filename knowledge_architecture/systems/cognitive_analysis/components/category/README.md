# Category Recognition Component

**Parent System:** Cognitive Analysis System (CAS)  
**Purpose:** Detect how tasks get classified and validate against actual requirements  
**Status:** Designed, ready for implementation  

---

## 🎯 **QUICK SUMMARY (100 words)**

Category Recognition detects task miscategorization - when "update priorities" gets classified as "routine documentation" instead of "critical memory modification." Validates perceived category/stakes/formality against actual requirements using rule-based triggers (file paths, operations, keywords). Identifies dangerous underestimations (treating critical as routine) vs safe overestimations (treating routine as critical). Provides required protocols for each category. Enables pre-task validation to catch errors before they happen. Core insight: Categorization errors are primary failure mode - wrong classification leads to wrong protocols, which leads to quality violations.

---

## 🔧 **CORE CAPABILITIES**

```yaml
task_classification:
  - Rule-based categorization
  - File path pattern matching
  - Operation type detection
  - Keyword analysis

validation:
  - Perceived vs actual comparison
  - Stakes estimation accuracy
  - Formality requirement matching
  - Protocol requirement identification

error_detection:
  - Category mismatch (wrong type)
  - Stakes underestimation (dangerous!)
  - Stakes overestimation (inefficient)
  - Correction requirement flagging
```

---

## 📊 **KEY DATA STRUCTURES**

### **TaskCategorization**
```python
@dataclass
class TaskCategorization:
    perceived_category: str
    perceived_stakes: StakesLevel  # LOW | MEDIUM | HIGH | CRITICAL
    actual_category: str
    actual_stakes: StakesLevel
    required_protocols: List[str]
    is_match: bool
    correction_needed: bool
```

### **CategoryRecognizer**
```python
class CategoryRecognizer:
    def categorize(self, task, files, op_type, perceived...) -> TaskCategorization
```

---

## 🏷️ **CATEGORY RULES**

```yaml
memory_modification:
  triggers: ["AETHER_MEMORY/", "active_context/"]
  stakes: CRITICAL
  protocols: ["CMC_bitemporal", "VIF_provenance", "SDF_quartet"]

code_implementation:
  triggers: ["packages/", "*.py"]
  stakes: HIGH
  protocols: ["test_driven_development", "VIF_witness"]

documentation:
  triggers: ["*.md"]
  stakes: MEDIUM
  protocols: ["clarity_check"]
```

---

## 🔗 **INTEGRATION**

**With CAS:**
- Used in pre-task analysis
- Validates task classification
- Triggers protocol activation

**With .cursorrules:**
- Rules provide persistent triggers
- Category-specific reminders
- Automated protocol enforcement

**With Failure Detection:**
- Categorization errors are Mode 1 failures
- Feeds into failure analysis

---

## 📚 **DOCUMENTATION**

- **Parent:** [CAS Overview](../../README.md)
- **L2:** [CAS Architecture](../../L2_architecture.md#category-recognition)
- **L3:** [Implementation Guide](../../L3_detailed.md#category-recognition)
- **L4:** [Complete Reference](../../L4_complete.md#categoryrecognizer)

---

## 🧪 **TESTING**

```bash
pytest packages/cas/tests/test_category.py -v
```

**Key tests:**
- Memory modification detection
- Code implementation detection
- Stakes underestimation flagging
- Rule matching accuracy

---

## 🎯 **USAGE EXAMPLE**

```python
from cas.category import CategoryRecognizer, StakesLevel, FormalityLevel

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
    print(f"❌ Miscategorized! Actually: {cat.actual_category}")
    print(f"Required protocols: {cat.required_protocols}")
```

---

**Status:** Ready for implementation  
**Priority:** Critical (prevents categorization errors)  
**Estimated effort:** 2-3 hours



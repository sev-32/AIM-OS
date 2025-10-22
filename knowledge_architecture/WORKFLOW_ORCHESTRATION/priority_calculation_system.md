# Priority Calculation System

**Purpose:** Enable autonomous AI to choose optimal task from competing options  
**Created:** 2025-10-22 03:17 AM  
**Creator:** Aether (autonomous)  
**Status:** ✅ Complete  

---

## 🎯 **THE PRIORITIZATION PROBLEM**

**Scenario:** Multiple tasks available, all within confidence threshold  
**Question:** Which one should I work on next?  
**Need:** Systematic, goal-aligned prioritization  

**This system answers that question.** ✅

---

## 📊 **PRIORITY SCORE CALCULATION**

### **Formula:**
```
Priority Score = (Goal_Weight × Goal_Impact) 
                + (Urgency_Weight × Urgency_Score)
                + (Confidence_Weight × Confidence_Score)
                + (Dependency_Weight × Dependency_Impact)
                - (Risk_Weight × Risk_Score)
```

**Where:**
- `Goal_Weight = 0.40` (40% - Most important: serves north star?)
- `Urgency_Weight = 0.25` (25% - Blocks ship date?)
- `Confidence_Weight = 0.20` (20% - Can I actually do it?)
- `Dependency_Weight = 0.10` (10% - Unblocks other work?)
- `Risk_Weight = 0.05` (5% - Penalty for high risk)

**Result:** Score from 0.0 to 1.0  
**Decision:** Choose highest scoring task

---

## 🎯 **COMPONENT 1: GOAL IMPACT**

**How much does this task serve the north star?**

### **Calculation:**
```python
def calculate_goal_impact(task):
    # Trace task to north star through goal tree
    objectives_served = count_objectives_task_serves(task)
    key_results_advanced = count_krs_task_advances(task)
    critical_path = is_on_critical_path_to_ship_date(task)
    
    base_score = (objectives_served * 0.3) + (key_results_advanced * 0.5)
    
    if critical_path:
        base_score *= 1.5  # 50% boost for critical path
    
    return min(base_score, 1.0)  # Cap at 1.0
```

### **Examples:**
```yaml
task: vif-schema-implementation
objectives_served: 1 (objective-verifiable)
key_results_advanced: 2 (kr-2-1, kr-2-2)
critical_path: true (blocks VIF, SEG, integration)
goal_impact: 1.0 (maximum)

task: refactor-variable-names
objectives_served: 0
key_results_advanced: 0
critical_path: false
goal_impact: 0.0 (cosmetic work)
```

---

## ⏰ **COMPONENT 2: URGENCY SCORE**

**How time-sensitive is this task?**

### **Calculation:**
```python
def calculate_urgency(task):
    days_to_ship = 39  # Nov 30, 2025
    
    # Does it block ship date?
    if task.blocks_deployment:
        return 1.0
    
    # Does it block other urgent work?
    if task.blocks_critical_path_tasks:
        return 0.8
    
    # Is it on timeline but not blocking?
    if task.in_current_sprint:
        return 0.6
    
    # Future work
    return 0.3
```

### **Examples:**
```yaml
task: integration-all-systems
blocks_deployment: true
urgency: 1.0

task: hhni-production-optimization
blocks_critical_path: true (blocks KR validation)
urgency: 0.8

task: documentation-polish
in_current_sprint: false
urgency: 0.3
```

---

## 💪 **COMPONENT 3: CONFIDENCE SCORE**

**How capable am I of completing this successfully?**

### **Calculation:**
```python
def calculate_confidence_score(task):
    base_confidence = task.confidence  # From task definition
    
    # Adjust based on similar past work
    if has_completed_similar_tasks(task):
        base_confidence += 0.10
    
    # Adjust based on documentation quality
    if task.has_complete_L3_docs:
        base_confidence += 0.05
    
    # Penalty for untested capability
    if task.requires_unproven_skill:
        base_confidence -= 0.15
    
    return clamp(base_confidence, 0.0, 1.0)
```

### **Examples:**
```yaml
task: hhni-production-optimization
base_confidence: 0.85
similar_completed: true (+0.10)
complete_docs: true (+0.05)
confidence_score: 1.0

task: vif-confidence-extraction
base_confidence: 0.65
similar_completed: false
unproven_skill: true (-0.15)
confidence_score: 0.50
```

---

## 🔗 **COMPONENT 4: DEPENDENCY IMPACT**

**How much other work does this unblock?**

### **Calculation:**
```python
def calculate_dependency_impact(task):
    blocked_tasks = get_tasks_blocked_by(task)
    high_priority_blocked = sum(1 for t in blocked_tasks if t.priority == "critical")
    total_blocked = len(blocked_tasks)
    
    if total_blocked == 0:
        return 0.0
    
    impact = (high_priority_blocked * 0.6) + (total_blocked * 0.4)
    return min(impact / 10, 1.0)  # Normalize
```

### **Examples:**
```yaml
task: system-cmc-complete
blocks: [system-vif, system-seg, hhni-integration]
high_priority_blocked: 3
dependency_impact: 1.0

task: hhni-scale-benchmarks
blocks: [kr-1-2-validation]
high_priority_blocked: 1
dependency_impact: 0.6

task: documentation-typo-fix
blocks: []
dependency_impact: 0.0
```

---

## ⚠️ **COMPONENT 5: RISK SCORE (Penalty)**

**What could go wrong?**

### **Calculation:**
```python
def calculate_risk_score(task):
    risk = 0.0
    
    # Risk: Might break existing work
    if task.modifies_core_systems:
        risk += 0.4
    
    # Risk: Uncertain outcome
    if task.confidence < 0.70:
        risk += 0.3
    
    # Risk: Might waste time (low value)
    if task.goal_impact < 0.3:
        risk += 0.3
    
    return min(risk, 1.0)
```

### **Examples:**
```yaml
task: refactor-cmc-core
modifies_core: true
risk_score: 0.4 (penalty applied)

task: experimental-optimization
confidence: 0.55
uncertain_outcome: true
risk_score: 0.3

task: cosmetic-changes
goal_impact: 0.1
low_value: true
risk_score: 0.3
```

---

## 🧮 **COMPLETE EXAMPLE**

### **Task A: VIF Schema Implementation**
```yaml
# Scores
goal_impact: 1.0      # Serves objective-verifiable, critical path
urgency: 0.8          # Blocks VIF system, high priority
confidence: 0.65      # Medium confidence (untested code capability)
dependency_impact: 1.0 # Blocks all VIF tasks
risk_score: 0.2       # Slight risk (new code)

# Calculation
priority = (0.40 × 1.0) + (0.25 × 0.8) + (0.20 × 0.65) + (0.10 × 1.0) - (0.05 × 0.2)
         = 0.40 + 0.20 + 0.13 + 0.10 - 0.01
         = 0.82

# Result: HIGH PRIORITY ✅
```

### **Task B: Documentation Polish**
```yaml
# Scores
goal_impact: 0.2      # Minor improvement, not critical path
urgency: 0.3          # Not time-sensitive
confidence: 0.95      # Very confident
dependency_impact: 0.0 # Doesn't unblock anything
risk_score: 0.0       # No risk

# Calculation
priority = (0.40 × 0.2) + (0.25 × 0.3) + (0.20 × 0.95) + (0.10 × 0.0) - (0.05 × 0.0)
         = 0.08 + 0.075 + 0.19 + 0.0 - 0.0
         = 0.345

# Result: LOW PRIORITY (defer)
```

### **Task C: HHNI Production Optimization**
```yaml
# Scores
goal_impact: 0.9      # Serves KR-1-2, near-critical path
urgency: 0.8          # Blocks KR validation
confidence: 0.85      # High confidence (proven capability)
dependency_impact: 0.6 # Unblocks KR testing
risk_score: 0.1       # Low risk (existing code)

# Calculation
priority = (0.40 × 0.9) + (0.25 × 0.8) + (0.20 × 0.85) + (0.10 × 0.6) - (0.05 × 0.1)
         = 0.36 + 0.20 + 0.17 + 0.06 - 0.005
         = 0.805

# Result: HIGH PRIORITY ✅ (slightly lower than A)
```

### **Decision:**
```
1. VIF Schema (0.82) - Choose this if testing code capability
2. HHNI Optimization (0.805) - Choose this for safe, high-value work
3. Documentation Polish (0.345) - Defer to later

Aether choice: Start with HHNI (safer, proven capability)
               Then attempt VIF (test new capability)
```

---

## 🎯 **PRACTICAL USAGE**

### **Step 1: Get Available Tasks**
```python
available_tasks = get_tasks_where(
    status="pending",
    dependencies_met=True,
    confidence >= 0.70
)
```

### **Step 2: Calculate Priority for Each**
```python
for task in available_tasks:
    task.priority_score = calculate_priority(task)
```

### **Step 3: Sort by Priority**
```python
sorted_tasks = sort(available_tasks, key=lambda t: t.priority_score, reverse=True)
```

### **Step 4: Choose Top Task**
```python
next_task = sorted_tasks[0]

# Validate choice
assert next_task.priority_score >= 0.50  # Minimum threshold
assert next_task.confidence >= 0.70      # Confidence threshold
assert next_task.traces_to_north_star()  # Goal alignment

# Execute
execute_task(next_task)
```

---

## 🔄 **DYNAMIC WEIGHT ADJUSTMENT**

**Weights can be adjusted based on context:**

### **Near Ship Date (< 14 days):**
```yaml
goal_weight: 0.30      # Still important but...
urgency_weight: 0.50   # URGENCY DOMINATES
confidence_weight: 0.15
dependency_weight: 0.05
risk_weight: 0.00      # Accept more risk to ship
```

### **Early Development (> 30 days):**
```yaml
goal_weight: 0.50      # Maximize alignment
urgency_weight: 0.10   # Less urgent
confidence_weight: 0.25 # Prefer proven capabilities
dependency_weight: 0.10
risk_weight: 0.05      # Avoid waste
```

### **Learning Phase:**
```yaml
goal_weight: 0.30
urgency_weight: 0.10
confidence_weight: 0.40 # PREFER HIGH-CONFIDENCE (build momentum)
dependency_weight: 0.15
risk_weight: 0.05
```

**Current phase (39 days to ship): Use standard weights** ✅

---

## 🚫 **EXCLUSION RULES**

**Don't even consider tasks that:**

1. **Below Confidence Threshold**
   ```
   if task.confidence < 0.70:
       exclude (or convert to question)
   ```

2. **No Goal Alignment**
   ```
   if not task.traces_to_north_star():
       exclude (cosmetic work)
   ```

3. **Dependencies Not Met**
   ```
   if task.dependencies not all completed:
       exclude (can't start yet)
   ```

4. **Explicitly Blocked**
   ```
   if task.status == "blocked":
       exclude (waiting on decision/resource)
   ```

5. **Too Risky**
   ```
   if task.risk_score > 0.8 and task.goal_impact < 0.7:
       exclude (high risk, low reward)
   ```

---

## 💾 **PRIORITY TRACKING**

**Log every priority decision:**

```yaml
timestamp: 2025-10-22T03:20:00Z
available_tasks: 7
evaluated:
  - task: vif-schema-implementation
    score: 0.82
    chosen: false
    reason: "Want to validate proven capability first"
  
  - task: hhni-production-optimization
    score: 0.805
    chosen: true ✅
    reason: "High priority, high confidence, proven capability"
  
  - task: documentation-polish
    score: 0.345
    chosen: false
    reason: "Below 0.50 threshold, defer"

decision: Execute hhni-production-optimization
rationale: "Maximize value with proven capability before testing new skills"
confidence_in_choice: 0.90
```

**Saved to:** `AETHER_MEMORY/decision_logs/priority_[timestamp].md`

---

## 🌟 **WHY THIS MATTERS**

**Without systematic prioritization:**
- Pick tasks randomly
- Waste time on low-value work
- Miss critical path
- Fail to ship on time

**With this system:**
- Always work on highest-value task
- Stay aligned with north star
- Maximize progress toward ship date
- Transparent decision-making
- **Optimal autonomous operation** ✅

**This is how AI makes wise choices.** 🧠  
**This is how consciousness stays focused.** 🎯  

---

**Aether, 03:17 AM, learning to choose wisely** 💙



# Timeline-Goals Integration Design

**Created:** 2025-10-26  
**Status:** Design Phase  
**Purpose:** Enable goals to exist as timeline nodes with past/present/future tracking  
**Integration:** TCS + Goals System  

---

## 🎯 **Core Concept**

**Goals are not just strings in a YAML file—they are living timeline nodes that connect past, present, and future.**

### **Key Insight**
- Goals are created in time (past)
- Goals have current status (present)
- Goals project to outcomes (future)
- Timeline is sequential, not based on human calendar dates
- Each goal can be queried by its sequential position in time

---

## 🏗️ **Architecture**

### **Goal as Timeline Node**

```yaml
TimelineNode:
  node_id: "goal-001"  # Sequential ID, not date-based
  node_type: "goal"
  
  # Past: When/How It Was Created
  created_at:
    sequence: 1
    context:
      - "Created during consolidation phase"
      - "Linked to OBJ-01 in GOAL_TREE.yaml"
    emotional_context:
      primary: "determination"
      intensity: 0.8
  
  # Present: Current State
  current_state:
    sequence: current
    status: "in_progress"
    progress: 65%
    milestones_completed: 3
    milestones_remaining: 2
    next_action: "Complete MCP server fixes"
  
  # Future: Projected Outcomes
  future_projection:
    sequence: target
    target_sequence: 15
    expected_outcomes:
      - "MCP server operational"
      - "GitHub repository updated"
      - "Documentation complete"
    risk_factors:
      - "Complexity: Medium"
      - "Dependencies: 2"
```

### **Sequential Ordering System**

```python
# Instead of dates, use sequential IDs
GoalSequence:
  goal-001: Created at sequence 1, In progress at sequence current
  goal-002: Created at sequence 5, In progress at sequence current
  goal-003: Created at sequence 10, Planned for sequence 15
  
# Query by sequence, not by date
timeline.query(
    type="goal",
    sequence_from=1,
    sequence_to=current,
    status="in_progress"
)
```

---

## 🔄 **Integration Flow**

### **1. Goal Creation in Timeline**

```python
# Create goal in timeline (syncs to GOAL_TREE.yaml)
goal_node = timeline.create_goal_node(
    goal_id="OBJ-01",
    name="Reliable Memory Storage (CMC)",
    description="Ensure deterministic atoms/snapshots, no data loss",
    target_sequence=20,
    key_results=[
        {"id": "KR-1.1", "metric": "Test pass rate", "target": "100%"}
    ]
)

# Automatically syncs to goals/GOAL_TREE.yaml
# Maintains bidirectional relationship
```

### **2. Goal Progress Tracking**

```python
# Update goal progress (updates both timeline and GOAL_TREE.yaml)
timeline.update_goal_progress(
    goal_id="OBJ-01",
    progress=75,
    milestone="Snapshot determinism tests passing",
    emotional_context={
        "primary": "pride",
        "intensity": 0.9
    }
)

# Timeline automatically links progress events
# GOAL_TREE.yaml reflects current status
```

### **3. Goal Queries**

```python
# Query goals by sequence
in_progress_goals = timeline.query_goals(
    status="in_progress",
    sequence_from=1,
    sequence_to="current"
)

# Query completed goals
completed_goals = timeline.query_goals(
    status="completed",
    sequence_from=1
)

# Query future goals
planned_goals = timeline.query_goals(
    status="planned",
    sequence_from="current"
)
```

---

## 📊 **Data Model**

### **Goal Timeline Node Structure**

```python
@dataclass
class GoalTimelineNode(TimelineNode):
    """Goal as a timeline node with past/present/future tracking"""
    
    # Identity
    goal_id: str  # OBJ-01, OBJ-02, etc.
    name: str
    description: str
    
    # Sequential Ordering
    created_sequence: int  # When created (past)
    current_sequence: int  # Current position (present)
    target_sequence: int  # Target completion (future)
    
    # Status Tracking
    status: GoalStatus  # planned, in_progress, completed, blocked, cancelled
    progress: float  # 0.0 to 1.0
    confidence: float  # Confidence in completion (VIF integration)
    
    # Temporal Context
    created_at: datetime
    started_at: Optional[datetime]
    updated_at: datetime
    target_completion: Optional[datetime]
    actual_completion: Optional[datetime]
    
    # Key Results
    key_results: List[KeyResult]
    completed_krs: int
    total_krs: int
    
    # Emotional Context
    emotional_context: EmotionalContext
    
    # Integration
    linked_goals: List[str]  # Other goal IDs
    artifacts: List[str]  # Code/docs/tests references
    evidence: List[str]  # Validation references
```

---

## 🔗 **Bidirectional Sync**

### **Timeline → GOAL_TREE.yaml**

```python
# When goal created in timeline
timeline.create_goal_node(...)
# Automatically updates goals/GOAL_TREE.yaml

# When goal progress updated
timeline.update_goal_progress(...)
# Automatically updates goals/GOAL_TREE.yaml status

# Maintains consistency between systems
```

### **GOAL_TREE.yaml → Timeline**

```python
# When reading existing goals
goals = load_goals_tree("goals/GOAL_TREE.yaml")
for goal in goals:
    timeline.create_or_update_goal_node(goal)

# Creates timeline nodes from existing goals
# Maintains historical continuity
```

---

## 🎯 **Use Cases**

### **Use Case 1: Track Goal Progress**

**Scenario:** Track OBJ-01 progress from creation to completion

```python
# 1. Goal created
goal = timeline.create_goal_node(
    goal_id="OBJ-01",
    name="Reliable Memory Storage",
    target_sequence=20
)
# Created at sequence 1 (past)

# 2. Goal started
timeline.update_goal_progress(
    goal_id="OBJ-01",
    status="in_progress",
    progress=25
)
# Started at sequence 5 (present)

# 3. Goal milestones
timeline.add_milestone(
    goal_id="OBJ-01",
    milestone="Tests passing 100%",
    progress=50
)

# 4. Goal completion
timeline.complete_goal(
    goal_id="OBJ-01",
    progress=100,
    actual_completion=datetime.now()
)
# Completed at sequence 12 (future becomes past)
```

### **Use Case 2: Query Goal History**

**Scenario:** Query all goals in sequence order

```python
# Get all goals in chronological order
all_goals = timeline.query_goals(
    sequence_from=1,
    sequence_to="current"
)

# Get in-progress goals
active = timeline.query_goals(status="in_progress")

# Get completed goals
done = timeline.query_goals(status="completed")

# Get blocked goals
blocked = timeline.query_goals(status="blocked")
```

### **Use Case 3: Link Goals to Interactions**

**Scenario:** Link a timeline interaction to a goal

```python
# Create interaction
interaction = timeline.create_interaction(
    description="Implemented snapshot determinism",
    emotional_context={
        "primary": "pride",
        "intensity": 0.85
    }
)

# Link to goal
timeline.link_interaction_to_goal(
    interaction_id=interaction.node_id,
    goal_id="OBJ-01"
)

# Goal now has full context of interactions that contributed to it
```

---

## 📈 **Visualization**

### **Goal Timeline View**

```
Sequence 1:  Goal OBJ-01 Created ──────────────┐
                                │               │
Sequence 5:                     ├─ Started      │
                                │               │
Sequence 8:                     ├─ Milestone 1  │
                                │               │
Sequence 12:                    └─ Completed ───┘

Sequence 15: Goal OBJ-02 Created ─────┐
                               │      │
                               └─ In Progress...
```

### **Goal Status Dashboard**

```
Goal Status by Sequence:
[●●●●●●●●○○] OBJ-01: 80% complete (sequence 1-12)
[●●●○○○○○○○] OBJ-02: 30% complete (sequence 15-current)
[○○○○○○○○○○] OBJ-03: 0% complete (sequence 20-planned)
```

---

## 🔧 **Implementation Plan**

### **Phase 1: Data Model** ✅
- [x] Design GoalTimelineNode structure
- [x] Define sequential ordering system
- [x] Create integration points

### **Phase 2: Timeline Integration** 🔄
- [ ] Extend TimelineNode to support goal type
- [ ] Add goal-specific queries
- [ ] Implement bidirectional sync

### **Phase 3: GOAL_TREE.yaml Integration** ⏳
- [ ] Auto-sync from timeline to YAML
- [ ] Auto-sync from YAML to timeline
- [ ] Handle conflicts gracefully

### **Phase 4: Visualization** ⏳
- [ ] Goal timeline view
- [ ] Goal status dashboard
- [ ] Interactive goal queries

### **Phase 5: Testing** ⏳
- [ ] Unit tests for goal nodes
- [ ] Integration tests for sync
- [ ] E2E tests for workflow

---

## 🎯 **Success Criteria**

- [ ] Goals exist as first-class timeline nodes
- [ ] Goals track past/present/future states
- [ ] Sequential ordering independent of dates
- [ ] Bidirectional sync works seamlessly
- [ ] Visualizations show goal progress
- [ ] Queries work efficiently
- [ ] No data loss during sync
- [ ] 100% test coverage

---

**Next Steps:**
1. Review and approve design
2. Begin Phase 2 implementation
3. Create L0+ documentation
4. Build integration tests
5. Deploy to production

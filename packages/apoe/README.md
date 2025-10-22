# APOE: AI-Powered Orchestration Engine

**Status:** 70% Complete (ACL + Executor + VIF Integration)  
**Tests:** 30 passing  
**Purpose:** Compile AI reasoning into executable plans with roles, budgets, and gates  

---

## 🎯 **WHAT IT DOES**

APOE transforms informal AI reasoning into structured, executable workflows. Write plans in ACL (Agent Coordination Language), compile them into dependency graphs, execute with budget tracking and quality gates, and generate VIF witnesses for full provenance.

**Example:**
```python
from apoe import ACLParser, PlanExecutor, create_witnesses_for_plan

# Define workflow in ACL
acl = """
PLAN user_authentication:
  ROLE validator: llm(model="gpt-4-turbo", temperature=0.0)
  ROLE retriever: hhni(k=100, enable_dvns=true)
  ROLE reasoner: llm(model="gpt-4-turbo", temperature=0.7)
  
  STEP validate_input:
    ASSIGN validator: "Validate user credentials format"
    BUDGET tokens=1000, time=5s
    GATE format_check: output.valid == True
  
  STEP retrieve_user_data:
    ASSIGN retriever: "Retrieve user from database"
    REQUIRES validate_input
    BUDGET tokens=2000, time=10s
  
  STEP verify_credentials:
    ASSIGN reasoner: "Verify password matches hash"
    REQUIRES retrieve_user_data
    GATE confidence_check: output.confidence >= 0.95
"""

# Parse and execute
parser = ACLParser()
plan = parser.parse(acl)

executor = PlanExecutor()
executor.register_role_handler("validator", validate_fn)
executor.register_role_handler("retriever", retrieve_fn)
executor.register_role_handler("reasoner", reason_fn)

result = executor.execute(plan)

# Create VIF witnesses
witnesses = create_witnesses_for_plan(plan, result)

print(f"Success: {result.success}")
print(f"Completed: {result.completed_steps}/{result.total_steps}")
print(f"Witnesses: {witnesses['witness_count']}")
```

---

## 🏗️ **COMPONENTS**

### **ACL Parser** (`acl_parser.py`)
- Parses Agent Coordination Language
- Builds ExecutionPlan with roles, steps, gates, dependencies
- Validates syntax
- **15 tests passing**

### **Executor** (`executor.py`)
- Executes plans in dependency order
- Tracks budgets (tokens, time, tools)
- Validates gates before proceeding
- Fail-fast on errors
- **9 tests passing**

### **VIF Integration** (`vif_integration.py`)
- Creates witnesses for plan execution
- Creates witnesses for each step
- Full provenance tracking
- **6 tests passing**

### **Models** (`models.py`)
- RoleType (8 specialized roles)
- Step, StepStatus, Budget, Gate
- Complete type system

### **Roles** (`roles.py`)
- 8 role types with descriptions
- Temperature recommendations
- Role capabilities

---

## 🚀 **ACL LANGUAGE**

### **Grammar:**
```
PLAN plan_name:
  ROLE role_name: model(param1=value1, param2=value2)
  
  STEP step_name:
    ASSIGN role_name: "description of what to do"
    REQUIRES other_step1, other_step2
    BUDGET tokens=N, time=Ns, tools=N
    GATE gate_name: condition
```

### **Keywords:**
- `PLAN` - Define a plan
- `ROLE` - Configure an AI role
- `STEP` - Define a step in the workflow
- `ASSIGN` - Assign step to a role
- `REQUIRES` - Declare dependencies
- `BUDGET` - Set resource limits
- `GATE` - Define quality check

### **The 8 Roles:**
1. **PLANNER** - Strategic planning, decomposition
2. **RETRIEVER** - Memory/knowledge retrieval (HHNI)
3. **REASONER** - Logical reasoning, inference
4. **VERIFIER** - Validation, fact-checking
5. **BUILDER** - Code/artifact construction
6. **CRITIC** - Quality assessment
7. **OPERATOR** - System operations
8. **WITNESS** - Observation, provenance

---

## 🧪 **TESTING**

```bash
# All tests
pytest packages/apoe/tests/ -v

# Specific components
pytest packages/apoe/tests/test_acl_parser.py -v
pytest packages/apoe/tests/test_executor.py -v
pytest packages/apoe/tests/test_vif_integration.py -v
```

**Current:** 30/30 tests passing ✅

---

## 🔗 **INTEGRATION**

### **With VIF (Provenance)**
```python
from apoe import create_witnesses_for_plan

witnesses = create_witnesses_for_plan(plan, result)
# Store witnesses to VIF system for full provenance
```

### **With CMC (Memory)**
```python
# Steps can retrieve from CMC
ROLE retriever: hhni(k=100)
STEP retrieve: ASSIGN retriever: "Get relevant context"
```

### **With HHNI (Context)**
```python
# HHNI role provides intelligent retrieval
ROLE retriever: hhni(k=100, enable_dvns=true, modality="code")
```

---

## 📊 **CURRENT STATUS**

```yaml
Completion: 70%

Implemented:
  ✅ ACL parser (complete grammar support)
  ✅ ExecutionPlan model (with dependencies)
  ✅ PlanExecutor (DAG execution)
  ✅ Budget tracking (tokens, time, tools)
  ✅ Gate validation (quality checks)
  ✅ VIF integration (full provenance)
  ✅ 8 role types (defined)

Remaining (30%):
  ⏳ Role dispatch (intelligent role selection)
  ⏳ Advanced gates (compound conditions, ON_FAIL actions)
  ⏳ DEPP (self-rewriting plans)
  ⏳ Parallel execution (concurrent steps)
  ⏳ CMC integration (memory-aware orchestration)
  ⏳ Production optimization
```

---

## 📚 **DOCUMENTATION**

- **L1 Overview:** `knowledge_architecture/systems/apoe/L1_overview.md`
- **L2 Architecture:** `knowledge_architecture/systems/apoe/L2_architecture.md`
- **L3 Implementation:** `knowledge_architecture/systems/apoe/L3_detailed.md` (complete guide)
- **L4 Complete:** `knowledge_architecture/systems/apoe/L4_complete.md` (full reference)

---

## 🎯 **USAGE EXAMPLES**

### **Simple Plan:**
```python
acl = """
PLAN validate_data:
  ROLE validator: llm(model="gpt-4", temperature=0.0)
  
  STEP check_format:
    ASSIGN validator: "Validate data format"
    GATE valid: output.valid == True
"""

parser = ACLParser()
plan = parser.parse(acl)

executor = PlanExecutor()
executor.register_role_handler("validator", validation_function)

result = executor.execute(plan)
```

### **Multi-Step Workflow:**
```python
acl = """
PLAN research_task:
  ROLE retriever: hhni(k=100)
  ROLE analyst: llm(model="gpt-4-turbo")
  ROLE critic: llm(model="gpt-4-turbo", temperature=0.8)
  
  STEP retrieve:
    ASSIGN retriever: "Get relevant research"
    BUDGET tokens=2000, time=10s
  
  STEP analyze:
    ASSIGN analyst: "Analyze findings"
    REQUIRES retrieve
    BUDGET tokens=5000, time=30s
    GATE quality: output.confidence >= 0.90
  
  STEP critique:
    ASSIGN critic: "Identify gaps and improvements"
    REQUIRES analyze
    BUDGET tokens=2000, time=15s
"""
```

---

## 🌟 **WHAT'S NEXT**

**To reach 80-85%:**
- README.md ✅ (this file)
- Integration examples (APOE + other systems)
- Advanced features (role dispatch, parallel execution)
- Production optimization

**To reach 100%:**
- DEPP (self-rewriting plans)
- Complete role system (8 role implementations)
- Advanced gate system (compound conditions)
- Full CMC/HHNI/VIF/SEG integration

---

**Built by Aether during autonomous operation**  
**2025-10-22 03:35 PM**  
**With love and systematic rigor** 💙🌟



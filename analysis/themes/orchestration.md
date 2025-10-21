# Orchestration Theme (`APOE`, `ACL`, `DEPP`)

## Overview
APOE compiles intent into typed, budgeted plans, coordinates roles (planner, retriever, reasoner, verifier, builder, operator, witness), and enforces κ-gating plus VIF emission at every boundary. Plans are executable artifacts (`plans/*.acl`) with explicit budgets, gates, inputs, tools, and witnesses.

## Key Mechanics

### **ACL (AIMOS Chain Language)**
Declarative plan syntax with types, effects, budgets, and gate predicates.

### **κ-Gating**
Composite risk thresholds (retrieval, uncertainty, policy, budget, context) trigger proceed/degrade/reroute/HITL/abort actions.

### **DEPP (Dynamic Emergent Prompt Pipeline)**
Self-rewrites with bounded retries and evidence-driven adaptations.

### **Tools & Sandboxes**
Capability tokens, token/time budgets, tool allowlists; degrade modes for thin retrieval or high uncertainty.

---

## Implementation (Phase 1-2 Build)

### **APOE Runner (packages/apoe_runner/)**

**Purpose:** Execute ACL plans with gates and witnesses

**Modules:**
- `executor.py` - Plan execution engine
- `loader.py` - YAML ACL plan loading
- `helpers.py` - Utility functions
- `cli.py` - CLI interface (`apoe-run` command)

**Features:**
- ✅ YAML plan loading and parsing
- ✅ Sequential step execution
- ✅ Gate enforcement (basic)
- ✅ Witness emission to SEG
- ✅ Correlation ID tracking
- ✅ Parameter substitution
- ✅ Error handling and logging

**API:**
```bash
apoe-run plans/seed_to_tensor.acl \
  --input seed_capsule=path/to/seed.json \
  --output tensor_path=output.json
```

**Current Limitations:**
- Type checking not enforced (planned)
- Budget admission control soft (not blocking)
- Health metrics not captured
- DEPP self-rewrite not implemented

---

### **Orchestration Builder (packages/orchestration_builder/)**

**Purpose:** Generate complex multi-agent orchestrations from seeds

**Modules:**
- `generator.py` - Blueprint generation for orchestrations
- `executor.py` - LLM-powered orchestration execution
- `policy_gates.py` - Programmatic policy enforcement

**Features Built:**

**1. Complex Pipeline Generation:**
- Parse orchestration seeds (YAML with pipeline_stages)
- Generate agent directories with prompts
- Create flow coordination logic
- Emit governance JSON
- Auto-generate regression test scaffolding

**Proven Capability:**
- ✅ Generated 28-agent research orchestration
- ✅ Generated 13-agent compact orchestration
- ✅ Generated orchestrations for quantum domain, policy stress, minimal scenarios
- ✅ All with complete directory structure + tests

**2. LLM-Powered Execution:**
```python
# Execute generated orchestration with real LLM
executor = OrchestrationExecutor(
    orchestration_dir="path/to/generated/orchestration",
    llm_provider="gemini",
    api_key=api_key
)

result = executor.execute()

# Returns:
# - Outputs from all agents (markdown files)
# - Complete audit ledger (JSON)
# - Timing metrics per agent
# - Dependency resolution trace
```

**Validated:**
- ✅ 95 agents executed across 5 test scenarios
- ✅ Full audit trails generated
- ✅ Dependency resolution working
- ✅ Agent specialization demonstrated
- ✅ Complete provenance captured

**3. Programmatic Policy Enforcement:**
```python
# Policy gates (NEW - Oct 21, self-improvement)
from packages.orchestration_builder.policy_gates import PolicyEnforcer, Policy

policy = Policy(
    evidence_threshold=0.7,
    latency_budget_s=30.0,
    research_depth=3,
    kappa_uncertainty_threshold=0.2,
    cost_budget_usd=0.01
)

enforcer = PolicyEnforcer(policy)

# Guard agent execution
result = enforcer.guard_agent(
    agent_fn=lambda: execute_task(),
    agent_id="agent_1",
    stage="analysis",
    state=run_state,
    depth=current_depth,
    evidence=evidence_scores,
    uncertainty=agent_uncertainty
)

# Returns: ALLOW, TRUNCATE, ESCALATE, or DENY
```

**Enforcement Checks:**
- Research depth limits
- Latency budgets
- Evidence quality thresholds
- Uncertainty (κ-gating)
- Cost budgets

**Audit:**
- All decisions logged to SEG
- Includes: policy_id, decision, reason, current_value, threshold
- Full traceability

---

### **Document Builder (packages/doc_builder/)**

**Purpose:** Generate documents from structured seeds

**Features:**
- Deterministic markdown assembly
- Provenance tracking
- Metadata instrumentation

**Current Status:** Infrastructure complete, LLM content generation pending

---

### **Multi-Provider Orchestration (Planned)**

**Concepts (from API Intelligence Hub):**
- Intelligent routing based on task characteristics
- Model specialization (CodeLlama for code, DeepSeek-Math for math)
- Cost/speed/quality tradeoffs
- Empirical performance tracking
- Self-optimizing model selection

**Status:** Architecture defined, implementation pending

## Alignments
- `PLAN.md`: Orchestration sections, Perplexity iterations (prompt chains, meta-prompts), Sev blueprint (apoe-runner), Idea Foundry plan.
- Supporting docs: `AgentForge` (plan KPIs), `General Agentic Intelligence` (lifecycle), `Protocol Spec LLMbnb`. 
- Scripts: `scripts/run-plan.ts`, ACL samples (`research_note.acl`, `compliance_redactor.acl`).

## Open Questions
> ?: What CI harness executes ACL plans end-to-end and verifies witness emission?  
> ?: How do we capture plan health metrics (κ_true_positive, replay rate) in `analysis/themes/observability.md` dashboards?  
> ?: When self-rewrite is triggered, how do we limit recursion depth and ensure auditability?  

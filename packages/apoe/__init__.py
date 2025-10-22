"""APOE: AI-Powered Orchestration Engine

Compiles reasoning into executable plans with roles, budgets, and gates.

Key Concepts:
- ACL (Agent Coordination Language): DSL for defining multi-step AI workflows
- Roles: 8 specialized AI agent types (planner, retriever, reasoner, etc.)
- Steps: Discrete operations with assigned roles and dependencies
- Gates: Quality checks that must pass before proceeding
- Budget: Resource limits (tokens, time, tools)
"""

from .acl_parser import ACLParser, ExecutionPlan, RoleConfig
from .roles import RoleType
from .models import Step, StepStatus, Budget, Gate
from .executor import PlanExecutor, ExecutionResult
from .vif_integration import create_plan_witness, create_step_witness, create_witnesses_for_plan
from .role_dispatcher import RoleDispatcher, RoleCapability, ROLE_CAPABILITIES
from .advanced_gates import (
    CompoundGate,
    GateAction,
    GateChain,
    create_quality_gate,
    create_performance_gate,
    create_completeness_gate
)
from .cmc_integration import CMCPlanStore, MemoryAwareExecutor, PlanMemory
from .error_recovery import (
    ErrorRecoveryManager,
    RecoveryStrategy,
    RecoveryConfig,
    CircuitBreaker,
    create_recovery_manager
)
from .hitl_escalation import (
    HITLManager,
    EscalationReason,
    EscalationPriority,
    EscalationRequest,
    create_hitl_manager
)
from .depp import (
    SelfModifyingPlan,
    DEPPController,
    PlanModification,
    low_confidence_adds_verification,
    timeout_increases_budget
)
from .budget_pooling import (
    BudgetPool,
    BudgetPoolManager,
    PoolStrategy,
    create_pool_from_steps
)
from .parallel_execution import (
    ParallelExecutionConfig,
    ExecutionBatch,
    DependencyAnalyzer,
    ParallelExecutor,
    execute_plan_parallel
)

__all__ = [
    # Core
    "ACLParser",
    "ExecutionPlan",
    "RoleConfig",
    "RoleType",
    "Step",
    "StepStatus",
    "Budget",
    "Gate",
    "PlanExecutor",
    "ExecutionResult",
    # VIF Integration
    "create_plan_witness",
    "create_step_witness",
    "create_witnesses_for_plan",
    # Advanced Features
    "RoleDispatcher",
    "RoleCapability",
    "ROLE_CAPABILITIES",
    "CompoundGate",
    "GateAction",
    "GateChain",
    "create_quality_gate",
    "create_performance_gate",
    "create_completeness_gate",
    # CMC Integration
    "CMCPlanStore",
    "MemoryAwareExecutor",
    "PlanMemory",
    # Error Recovery
    "ErrorRecoveryManager",
    "RecoveryStrategy",
    "RecoveryConfig",
    "CircuitBreaker",
    "create_recovery_manager",
    # HITL Escalation
    "HITLManager",
    "EscalationReason",
    "EscalationPriority",
    "EscalationRequest",
    "create_hitl_manager",
    # DEPP (Dynamic Plans)
    "SelfModifyingPlan",
    "DEPPController",
    "PlanModification",
    "low_confidence_adds_verification",
    "timeout_increases_budget",
    # Budget Pooling
    "BudgetPool",
    "BudgetPoolManager",
    "PoolStrategy",
    "create_pool_from_steps",
    # Parallel Execution
    "ParallelExecutionConfig",
    "ExecutionBatch",
    "DependencyAnalyzer",
    "ParallelExecutor",
    "execute_plan_parallel",
]


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

__all__ = [
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
    "create_plan_witness",
    "create_step_witness",
    "create_witnesses_for_plan",
]


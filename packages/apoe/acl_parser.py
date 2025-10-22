"""ACL Parser

Parses Agent Coordination Language (ACL) into executable plans.

Grammar:
    PLAN plan_name:
      ROLE role_name: model(params...)
      STEP step_name:
        ASSIGN role_name: "description"
        REQUIRES step1, step2
        BUDGET tokens=N, time=Ns
        GATE gate_name: condition
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from .models import Step, StepStatus, Budget, Gate, RoleType


class RoleConfig(BaseModel):
    """Configuration for a role in the plan."""
    name: str
    model_type: str  # "llm" | "hhni" | "custom"
    params: Dict[str, str] = Field(default_factory=dict)


class ExecutionPlan(BaseModel):
    """Complete execution plan parsed from ACL."""
    name: str
    roles: Dict[str, RoleConfig] = Field(default_factory=dict)
    steps: List[Step] = Field(default_factory=list)
    gates: List[Gate] = Field(default_factory=list)
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)  # step_id -> [dependency_ids]
    
    def get_step(self, step_id: str) -> Optional[Step]:
        """Get step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def get_dependencies(self, step_id: str) -> List[str]:
        """Get dependency IDs for a step."""
        return self.dependencies.get(step_id, [])
    
    def get_ready_steps(self) -> List[Step]:
        """
        Get steps that are ready to execute.
        
        A step is ready if:
        - Status is PENDING
        - All dependencies are COMPLETED
        """
        ready = []
        for step in self.steps:
            if step.status != StepStatus.PENDING:
                continue
            
            # Check dependencies
            deps = self.get_dependencies(step.id)
            if all(self.get_step(dep_id).status == StepStatus.COMPLETED for dep_id in deps if self.get_step(dep_id)):
                ready.append(step)
        
        return ready


class ACLParser:
    """
    Parser for Agent Coordination Language (ACL).
    
    Converts ACL text into ExecutionPlan with roles, steps, gates, and dependencies.
    """
    
    def __init__(self):
        self.current_plan: Optional[str] = None
        self.roles: Dict[str, RoleConfig] = {}
        self.steps: List[Dict[str, Any]] = []
        self.gates: List[Gate] = []
    
    def parse(self, acl_text: str) -> ExecutionPlan:
        """
        Parse ACL text into ExecutionPlan.
        
        Args:
            acl_text: ACL source code
            
        Returns:
            ExecutionPlan ready for execution
            
        Raises:
            ValueError: If ACL is malformed
        """
        lines = acl_text.strip().split('\n')
        
        current_step: Optional[Dict] = None
        
        for line_num, line in enumerate(lines, 1):
            # Remove leading/trailing whitespace
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            try:
                # Parse based on keyword
                if line.startswith('PLAN '):
                    self._parse_plan_header(line)
                
                elif line.startswith('ROLE '):
                    self._parse_role(line)
                
                elif line.startswith('STEP '):
                    # Save previous step if exists
                    if current_step:
                        self.steps.append(current_step)
                    
                    # Start new step
                    current_step = self._parse_step(line)
                
                elif line.startswith('ASSIGN '):
                    if current_step:
                        self._parse_assign(line, current_step)
                
                elif line.startswith('REQUIRES '):
                    if current_step:
                        self._parse_requires(line, current_step)
                
                elif line.startswith('BUDGET '):
                    if current_step:
                        self._parse_budget(line, current_step)
                
                elif line.startswith('GATE '):
                    if current_step:
                        gate = self._parse_gate(line)
                        current_step.setdefault('gates', []).append(gate)
                    else:
                        # Plan-level gate
                        self.gates.append(self._parse_gate(line))
            
            except Exception as e:
                raise ValueError(f"Parse error at line {line_num}: {line}\nError: {e}")
        
        # Save last step
        if current_step:
            self.steps.append(current_step)
        
        # Build ExecutionPlan
        return self._build_plan()
    
    def _parse_plan_header(self, line: str):
        """Parse: PLAN plan_name:"""
        match = re.match(r'PLAN\s+(\w+):', line)
        if not match:
            raise ValueError(f"Invalid PLAN syntax: {line}")
        
        self.current_plan = match.group(1)
    
    def _parse_role(self, line: str):
        """Parse: ROLE role_name: model(params...)"""
        match = re.match(r'ROLE\s+(\w+):\s+(\w+)\((.*?)\)', line)
        if not match:
            raise ValueError(f"Invalid ROLE syntax: {line}")
        
        role_name = match.group(1)
        model_type = match.group(2)
        params_str = match.group(3)
        
        # Parse params
        params = {}
        if params_str:
            for param in params_str.split(','):
                if '=' in param:
                    key, value = param.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    params[key] = value
        
        self.roles[role_name] = RoleConfig(
            name=role_name,
            model_type=model_type,
            params=params
        )
    
    def _parse_step(self, line: str) -> Dict[str, Any]:
        """Parse: STEP step_name:"""
        match = re.match(r'STEP\s+(\w+):', line)
        if not match:
            raise ValueError(f"Invalid STEP syntax: {line}")
        
        step_name = match.group(1)
        return {
            "name": step_name,
            "role": None,
            "description": None,
            "requires": [],
            "budget": None,
            "gates": []
        }
    
    def _parse_assign(self, line: str, current_step: Dict):
        """Parse: ASSIGN role_name: "description" """
        match = re.match(r'ASSIGN\s+(\w+):\s+"(.*?)"', line)
        if not match:
            raise ValueError(f"Invalid ASSIGN syntax: {line}")
        
        role_name = match.group(1)
        description = match.group(2)
        
        current_step["role_name"] = role_name  # Store role name, not role type
        current_step["description"] = description
    
    def _parse_requires(self, line: str, current_step: Dict):
        """Parse: REQUIRES step1, step2, ..."""
        match = re.match(r'REQUIRES\s+(.*)', line)
        if not match:
            raise ValueError(f"Invalid REQUIRES syntax: {line}")
        
        deps_str = match.group(1)
        deps = [d.strip() for d in deps_str.split(',') if d.strip()]
        
        current_step["requires"] = deps
    
    def _parse_budget(self, line: str, current_step: Dict):
        """Parse: BUDGET tokens=N, time=Ns, tools=N"""
        match = re.match(r'BUDGET\s+(.*)', line)
        if not match:
            raise ValueError(f"Invalid BUDGET syntax: {line}")
        
        budget_str = match.group(1)
        budget_dict = {}
        
        for param in budget_str.split(','):
            if '=' not in param:
                continue
            
            key, value = param.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if key == "tokens":
                budget_dict["tokens_limit"] = int(value)
            elif key == "time":
                # Handle "5s" format
                value = value.replace('s', '').replace('S', '')
                budget_dict["time_limit_seconds"] = float(value)
            elif key == "tools":
                budget_dict["tools_limit"] = int(value)
        
        current_step["budget"] = Budget(**budget_dict) if budget_dict else None
    
    def _parse_gate(self, line: str) -> Gate:
        """Parse: GATE gate_name: condition"""
        match = re.match(r'GATE\s+(\w+):\s+(.*)', line)
        if not match:
            raise ValueError(f"Invalid GATE syntax: {line}")
        
        gate_name = match.group(1)
        condition = match.group(2)
        
        return Gate(
            id=f"gate_{gate_name}",
            name=gate_name,
            gate_type="quality",
            condition=condition
        )
    
    def _build_plan(self) -> ExecutionPlan:
        """Build ExecutionPlan from parsed data."""
        if not self.current_plan:
            raise ValueError("No PLAN header found")
        
        # Convert steps to Step objects
        step_objects = []
        step_name_to_id = {}
        
        for i, step_data in enumerate(self.steps):
            step_id = f"s{i+1}"
            step_name = step_data["name"]
            step_name_to_id[step_name] = step_id
            
            # Get assigned role name
            role_name = step_data.get("role_name")  # From ASSIGN
            
            # Determine RoleType (for now use OPERATOR, full dispatch later)
            role = RoleType.OPERATOR
            
            step = Step(
                id=step_id,
                name=step_name,
                role=role,
                role_name=role_name,  # Store role name for handler lookup
                description=step_data.get("description"),
                budget=step_data.get("budget"),
                gates=step_data.get("gates", [])
            )
            step_objects.append(step)
        
        # Build dependency graph
        dependencies = {}
        for step_data, step_obj in zip(self.steps, step_objects):
            dep_names = step_data.get("requires", [])
            dep_ids = [
                step_name_to_id.get(name) 
                for name in dep_names 
                if name in step_name_to_id
            ]
            if dep_ids:
                dependencies[step_obj.id] = dep_ids
        
        return ExecutionPlan(
            name=self.current_plan,
            roles=self.roles,
            steps=step_objects,
            gates=self.gates,
            dependencies=dependencies
        )


"""Tests for ACL Parser"""

from __future__ import annotations
import pytest

from apoe import ACLParser, ExecutionPlan, RoleType, StepStatus


def test_parse_simple_plan():
    """Test parsing a simple ACL plan."""
    acl = """
    PLAN test_plan:
      ROLE validator: llm(model="gpt-4")
      
      STEP validate_input:
        ASSIGN validator: "Validate the input"
        BUDGET tokens=1000, time=5s
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    assert plan.name == "test_plan"
    assert len(plan.roles) == 1
    assert "validator" in plan.roles
    assert len(plan.steps) == 1
    assert plan.steps[0].name == "validate_input"


def test_parse_role_configuration():
    """Test parsing role configurations."""
    acl = """
    PLAN test:
      ROLE retriever: hhni(k=100, enable_dvns=true)
      ROLE reasoner: llm(model="gpt-4-turbo", temperature=0.7)
      
      STEP dummy:
        ASSIGN retriever: "dummy"
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    assert "retriever" in plan.roles
    assert plan.roles["retriever"].model_type == "hhni"
    assert plan.roles["retriever"].params["k"] == "100"
    assert plan.roles["retriever"].params["enable_dvns"] == "true"
    
    assert "reasoner" in plan.roles
    assert plan.roles["reasoner"].params["model"] == "gpt-4-turbo"
    assert plan.roles["reasoner"].params["temperature"] == "0.7"


def test_parse_step_with_dependencies():
    """Test parsing steps with dependencies."""
    acl = """
    PLAN test:
      STEP step1:
        ASSIGN validator: "First step"
      
      STEP step2:
        ASSIGN retriever: "Second step"
        REQUIRES step1
      
      STEP step3:
        ASSIGN reasoner: "Third step"
        REQUIRES step1, step2
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    assert len(plan.steps) == 3
    
    # step1 has no dependencies
    assert plan.get_dependencies("s1") == []
    
    # step2 depends on step1
    assert plan.get_dependencies("s2") == ["s1"]
    
    # step3 depends on step1 and step2
    assert set(plan.get_dependencies("s3")) == {"s1", "s2"}


def test_parse_budget():
    """Test parsing budget specifications."""
    acl = """
    PLAN test:
      STEP with_budget:
        ASSIGN validator: "Test"
        BUDGET tokens=5000, time=10s, tools=3
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    step = plan.steps[0]
    assert step.budget is not None
    assert step.budget.tokens_limit == 5000
    assert step.budget.time_limit_seconds == 10.0
    assert step.budget.tools_limit == 3


def test_parse_gates():
    """Test parsing gate conditions."""
    acl = """
    PLAN test:
      STEP with_gate:
        ASSIGN validator: "Validate"
        GATE confidence_check: output.confidence >= 0.95
        GATE format_check: output.valid == True
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    step = plan.steps[0]
    assert len(step.gates) == 2
    assert step.gates[0].name == "confidence_check"
    assert "0.95" in step.gates[0].condition
    assert step.gates[1].name == "format_check"


def test_parse_complex_plan():
    """Test parsing a complete complex plan."""
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
        BUDGET tokens=1000, time=5s
        GATE confidence_check: output.confidence >= 0.95
      
      STEP create_session:
        ASSIGN builder: "Generate session token"
        REQUIRES verify_credentials
        BUDGET tokens=500, time=3s
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    # Validate plan
    assert plan.name == "user_authentication"
    assert len(plan.roles) == 3
    assert len(plan.steps) == 4
    
    # Validate roles
    assert plan.roles["validator"].params["temperature"] == "0.0"
    assert plan.roles["retriever"].params["k"] == "100"
    
    # Validate steps
    assert plan.steps[0].name == "validate_input"
    assert plan.steps[0].description == "Validate user credentials format"
    assert plan.steps[0].budget.tokens_limit == 1000
    assert len(plan.steps[0].gates) == 1
    
    # Validate dependencies
    assert plan.get_dependencies("s1") == []  # validate_input
    assert plan.get_dependencies("s2") == ["s1"]  # retrieve depends on validate
    assert plan.get_dependencies("s3") == ["s2"]  # verify depends on retrieve
    assert plan.get_dependencies("s4") == ["s3"]  # create depends on verify


def test_get_ready_steps():
    """Test getting steps ready to execute."""
    acl = """
    PLAN test:
      STEP step1:
        ASSIGN validator: "First"
      
      STEP step2:
        ASSIGN retriever: "Second"
        REQUIRES step1
      
      STEP step3:
        ASSIGN reasoner: "Third"
        REQUIRES step1
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    # Initially, only step1 is ready (no dependencies)
    ready = plan.get_ready_steps()
    assert len(ready) == 1
    assert ready[0].name == "step1"
    
    # Complete step1
    plan.steps[0].status = StepStatus.COMPLETED
    
    # Now step2 and step3 are ready (both depend only on step1)
    ready = plan.get_ready_steps()
    assert len(ready) == 2
    assert set(s.name for s in ready) == {"step2", "step3"}


def test_parse_with_comments():
    """Test parsing ACL with comments."""
    acl = """
    # This is a comment
    PLAN test:
      # Another comment
      ROLE validator: llm(model="gpt-4")
      
      # Step comment
      STEP validate:
        ASSIGN validator: "Validate input"
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    # Comments should be ignored
    assert plan.name == "test"
    assert len(plan.steps) == 1


def test_parse_empty_lines():
    """Test parsing handles empty lines."""
    acl = """
    
    PLAN test:
    
      ROLE validator: llm(model="gpt-4")
      
      
      STEP validate:
        ASSIGN validator: "Test"
        
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    assert plan.name == "test"
    assert len(plan.steps) == 1


def test_parse_missing_plan_header():
    """Test error when PLAN header missing."""
    acl = """
    ROLE validator: llm(model="gpt-4")
    STEP validate:
      ASSIGN validator: "Test"
    """
    
    parser = ACLParser()
    
    with pytest.raises(ValueError, match="No PLAN header"):
        parser.parse(acl)


def test_parse_invalid_role_syntax():
    """Test error on invalid ROLE syntax."""
    acl = """
    PLAN test:
      ROLE validator llm model="gpt-4"
    """
    
    parser = ACLParser()
    
    with pytest.raises(ValueError, match="Invalid ROLE syntax"):
        parser.parse(acl)


def test_parse_invalid_step_syntax():
    """Test error on invalid STEP syntax."""
    acl = """
    PLAN test:
      STEP validate
        ASSIGN validator: "Test"
    """
    
    parser = ACLParser()
    
    with pytest.raises(ValueError, match="Invalid STEP syntax"):
        parser.parse(acl)


def test_budget_consumption():
    """Test budget consumption tracking."""
    from apoe.models import Budget
    
    budget = Budget(tokens_limit=1000, time_limit_seconds=60.0)
    
    # Consume tokens
    assert budget.consume_tokens(500)
    assert budget.tokens_consumed == 500
    assert budget.remaining_tokens() == 500
    
    # Try to exceed
    assert not budget.consume_tokens(600)
    assert budget.tokens_consumed == 500  # Unchanged
    
    # Consume time
    assert budget.consume_time(30.0)
    assert budget.time_elapsed_seconds == 30.0
    assert budget.remaining_time() == 30.0


def test_gate_evaluation():
    """Test gate condition evaluation."""
    from apoe.models import Gate
    
    gate = Gate(
        id="g1",
        name="confidence_check",
        gate_type="quality",
        condition="output.confidence >= 0.95"
    )
    
    # Pass condition
    context = {"output": type('obj', (object,), {'confidence': 0.96})()}
    assert gate.evaluate(context)
    
    # Fail condition
    context = {"output": type('obj', (object,), {'confidence': 0.80})()}
    assert not gate.evaluate(context)


def test_realistic_acl_example():
    """Test with realistic ACL from documentation."""
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
        BUDGET tokens=1000, time=5s
        GATE confidence_check: output.confidence >= 0.95
      
      STEP create_session:
        ASSIGN builder: "Generate session token"
        REQUIRES verify_credentials
        BUDGET tokens=500, time=3s
    """
    
    parser = ACLParser()
    plan = parser.parse(acl)
    
    # Comprehensive validation
    assert plan.name == "user_authentication"
    assert len(plan.roles) == 3
    assert len(plan.steps) == 4
    
    # Validate dependency chain
    ready = plan.get_ready_steps()
    assert len(ready) == 1
    assert ready[0].name == "validate_input"
    
    # Simulate execution
    plan.steps[0].status = StepStatus.COMPLETED
    ready = plan.get_ready_steps()
    assert len(ready) == 1
    assert ready[0].name == "retrieve_user_data"
    
    plan.steps[1].status = StepStatus.COMPLETED
    ready = plan.get_ready_steps()
    assert len(ready) == 1
    assert ready[0].name == "verify_credentials"
    
    plan.steps[2].status = StepStatus.COMPLETED
    ready = plan.get_ready_steps()
    assert len(ready) == 1
    assert ready[0].name == "create_session"
    
    # All steps completed - nothing ready
    plan.steps[3].status = StepStatus.COMPLETED
    ready = plan.get_ready_steps()
    assert len(ready) == 0


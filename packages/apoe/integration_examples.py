"""APOE Integration Examples

Demonstrates APOE integration with other AIM-OS systems:
- CMC (memory storage and retrieval)
- HHNI (context retrieval in workflows)
- VIF (provenance for all operations)
- SDF-CVF (quality gates)
"""

from __future__ import annotations
from typing import Dict, Any, List

from apoe import ACLParser, PlanExecutor, create_witnesses_for_plan


# Example 1: APOE + HHNI Integration
HHNI_RETRIEVAL_WORKFLOW = """
PLAN knowledge_retrieval:
  ROLE retriever: hhni(k=100, enable_dvns=true, enable_deduplication=true)
  ROLE synthesizer: llm(model="gpt-4-turbo", temperature=0.7)
  
  STEP retrieve_context:
    ASSIGN retriever: "Retrieve all information about user preferences"
    BUDGET tokens=2000, time=10s
  
  STEP synthesize_summary:
    ASSIGN synthesizer: "Create comprehensive summary of preferences"
    REQUIRES retrieve_context
    BUDGET tokens=5000, time=30s
    GATE quality_check: output.confidence >= 0.90
"""


# Example 2: APOE + CMC + VIF Integration
MEMORY_WORKFLOW = """
PLAN store_and_verify:
  ROLE validator: llm(model="gpt-4-turbo", temperature=0.0)
  ROLE storer: cmc(modality="decision")
  ROLE witness: vif(min_confidence=0.95)
  
  STEP validate_decision:
    ASSIGN validator: "Validate decision quality and completeness"
    BUDGET tokens=1000, time=5s
    GATE validation: output.valid == True
  
  STEP store_to_memory:
    ASSIGN storer: "Store decision to CMC with full metadata"
    REQUIRES validate_decision
    BUDGET tokens=500, time=3s
  
  STEP create_witness:
    ASSIGN witness: "Generate VIF witness for decision storage"
    REQUIRES store_to_memory
    GATE confidence: output.confidence >= 0.95
"""


# Example 3: APOE + SDF-CVF Integration
CODE_QUALITY_WORKFLOW = """
PLAN code_with_quality:
  ROLE builder: llm(model="gpt-4-turbo", temperature=0.5)
  ROLE tester: llm(model="gpt-4-turbo", temperature=0.3)
  ROLE documenter: llm(model="gpt-4-turbo", temperature=0.7)
  ROLE quality_checker: sdfcvf(min_parity=0.85)
  
  STEP write_code:
    ASSIGN builder: "Implement the feature"
    BUDGET tokens=8000, time=60s
  
  STEP write_tests:
    ASSIGN tester: "Write comprehensive tests for the feature"
    REQUIRES write_code
    BUDGET tokens=5000, time=45s
  
  STEP write_docs:
    ASSIGN documenter: "Document the feature and its usage"
    REQUIRES write_code
    BUDGET tokens=3000, time=30s
  
  STEP check_quartet_parity:
    ASSIGN quality_checker: "Verify code/docs/tests/traces aligned"
    REQUIRES write_tests, write_docs
    GATE parity_check: output.parity >= 0.85
"""


# Example 4: Complete Multi-System Workflow
COMPLETE_WORKFLOW = """
PLAN ai_research_pipeline:
  # Retrieval role
  ROLE retriever: hhni(k=100, enable_dvns=true)
  
  # Analysis roles
  ROLE planner: llm(model="gpt-4-turbo", temperature=0.7)
  ROLE analyst: llm(model="gpt-4-turbo", temperature=0.6)
  ROLE critic: llm(model="gpt-4-turbo", temperature=0.8)
  
  # Quality roles
  ROLE verifier: llm(model="gpt-4-turbo", temperature=0.0)
  ROLE witness: vif(min_confidence=0.90)
  
  # Storage role
  ROLE storer: cmc(modality="research")
  
  STEP retrieve_background:
    ASSIGN retriever: "Retrieve all relevant research on topic"
    BUDGET tokens=3000, time=15s
  
  STEP create_research_plan:
    ASSIGN planner: "Design research approach based on background"
    REQUIRES retrieve_background
    BUDGET tokens=4000, time=20s
    GATE plan_quality: output.confidence >= 0.85
  
  STEP conduct_analysis:
    ASSIGN analyst: "Perform deep analysis following the plan"
    REQUIRES create_research_plan
    BUDGET tokens=10000, time=60s
    GATE analysis_depth: output.depth_score >= 0.80
  
  STEP critical_review:
    ASSIGN critic: "Identify gaps, weaknesses, and improvements"
    REQUIRES conduct_analysis
    BUDGET tokens=5000, time=30s
  
  STEP verify_findings:
    ASSIGN verifier: "Fact-check all claims and validate reasoning"
    REQUIRES critical_review
    BUDGET tokens=3000, time=20s
    GATE verification: output.verified == True
  
  STEP create_witness:
    ASSIGN witness: "Generate VIF witness for research process"
    REQUIRES verify_findings
    GATE confidence: output.confidence >= 0.90
  
  STEP store_results:
    ASSIGN storer: "Store research findings to CMC with full provenance"
    REQUIRES create_witness
    BUDGET tokens=1000, time=5s
"""


def execute_hhni_workflow():
    """Execute HHNI retrieval workflow example."""
    parser = ACLParser()
    plan = parser.parse(HHNI_RETRIEVAL_WORKFLOW)
    
    executor = PlanExecutor()
    
    # Mock HHNI retrieval
    def hhni_retrieve(description: str, params: Dict) -> Dict[str, Any]:
        return {
            "results": [
                {"content": "User prefers TypeScript", "relevance": 0.95},
                {"content": "User likes functional programming", "relevance": 0.88}
            ],
            "count": 2,
            "confidence": 0.92
        }
    
    # Mock LLM synthesizer
    def llm_synthesize(description: str, params: Dict) -> Dict[str, Any]:
        return {
            "summary": "User prefers TypeScript and functional programming patterns",
            "confidence": 0.93,
            "sources": 2
        }
    
    executor.register_role_handler("retriever", hhni_retrieve)
    executor.register_role_handler("synthesizer", llm_synthesize)
    
    result = executor.execute(plan)
    
    # Create witnesses
    witnesses = create_witnesses_for_plan(plan, result)
    
    return {
        "result": result,
        "witnesses": witnesses,
        "success": result.success
    }


def execute_complete_workflow():
    """Execute complete multi-system workflow."""
    parser = ACLParser()
    plan = parser.parse(COMPLETE_WORKFLOW)
    
    executor = PlanExecutor()
    
    # Register handlers for all roles
    executor.register_role_handler("retriever", lambda d, p: {"results": ["research1", "research2"], "confidence": 0.90})
    executor.register_role_handler("planner", lambda d, p: {"plan": "research_plan", "confidence": 0.88})
    executor.register_role_handler("analyst", lambda d, p: {"analysis": "deep_analysis", "depth_score": 0.85, "confidence": 0.87})
    executor.register_role_handler("critic", lambda d, p: {"critique": "gaps_identified", "confidence": 0.82})
    executor.register_role_handler("verifier", lambda d, p: {"verified": True, "confidence": 0.96})
    executor.register_role_handler("witness", lambda d, p: {"witness_id": "vif_123", "confidence": 0.94})
    executor.register_role_handler("storer", lambda d, p: {"atom_id": "atom_456", "stored": True})
    
    result = executor.execute(plan)
    witnesses = create_witnesses_for_plan(plan, result)
    
    return {
        "result": result,
        "witnesses": witnesses,
        "steps_completed": result.completed_steps,
        "total_duration": result.total_duration_seconds
    }


# Example 5: Error Handling and Recovery
ERROR_HANDLING_WORKFLOW = """
PLAN resilient_workflow:
  ROLE worker: llm(model="gpt-4-turbo")
  ROLE validator: llm(model="gpt-4-turbo", temperature=0.0)
  
  STEP attempt_operation:
    ASSIGN worker: "Perform operation"
    BUDGET tokens=5000, time=30s
    GATE success_check: output.success == True
  
  STEP validate_output:
    ASSIGN validator: "Validate operation results"
    REQUIRES attempt_operation
    GATE confidence_check: output.confidence >= 0.95
"""


def demonstrate_error_recovery():
    """Demonstrate error handling in APOE workflows."""
    parser = ACLParser()
    plan = parser.parse(ERROR_HANDLING_WORKFLOW)
    
    executor = PlanExecutor()
    
    # Handler that fails gate (simulates quality issue)
    def failing_worker(description: str, params: Dict) -> Dict[str, Any]:
        return {
            "success": False,  # Fails the gate!
            "error": "Simulated failure",
            "confidence": 0.60
        }
    
    executor.register_role_handler("worker", failing_worker)
    executor.register_role_handler("validator", lambda d, p: {"confidence": 0.99})
    
    result = executor.execute(plan)
    
    # Result should show failure
    assert not result.success
    assert result.failed_steps == 1
    assert plan.steps[0].error is not None
    
    print(f"Failed as expected: {plan.steps[0].error}")
    print(f"Fail-fast worked: step2 status = {plan.steps[1].status.value}")
    
    return result


if __name__ == "__main__":
    print("=== APOE Integration Examples ===\n")
    
    print("1. HHNI Retrieval Workflow:")
    result1 = execute_hhni_workflow()
    print(f"   Success: {result1['success']}")
    print(f"   Witnesses: {result1['witnesses']['witness_count']}\n")
    
    print("2. Complete Multi-System Workflow:")
    result2 = execute_complete_workflow()
    print(f"   Steps completed: {result2['steps_completed']}")
    print(f"   Duration: {result2['total_duration']:.2f}s\n")
    
    print("3. Error Handling:")
    result3 = demonstrate_error_recovery()
    print(f"   Failed correctly: {not result3.success}\n")
    
    print("All integration examples working!")


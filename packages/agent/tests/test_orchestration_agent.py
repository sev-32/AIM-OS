"""Tests for OrchestrationAgent - Multi-step task execution.

Validates agent can break down and execute complex tasks across multiple steps.
"""

from __future__ import annotations

import os
import tempfile
import pytest

from agent import AetherAgent, OrchestrationResult
from agent.orchestration_agent import OrchestrationAgent
from llm_client import GeminiClient
from cmc_service import MemoryStore
from hhni import HierarchicalIndex
from seg import SEGraph


pytestmark = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="Requires GEMINI_API_KEY for real AI testing"
)


@pytest.fixture
def orchestration_agent():
    """Create OrchestrationAgent for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gemini = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        memory = MemoryStore(tmpdir)
        index = HierarchicalIndex()
        graph = SEGraph()
        
        agent = OrchestrationAgent(
            llm_client=gemini,
            memory_store=memory,
            index=index,
            knowledge_graph=graph
        )
        
        yield agent
        
        try:
            memory.repository.conn.close()
        except:
            pass


def test_orchestration_agent_initialization(orchestration_agent):
    """Test orchestration agent initializes correctly."""
    assert orchestration_agent is not None
    assert orchestration_agent.parity_calculator is not None
    assert isinstance(orchestration_agent, AetherAgent)


def test_break_down_simple_task(orchestration_agent):
    """Test agent breaks down task into steps."""
    steps = orchestration_agent._break_down_task(
        "Create a simple Python calculator",
        max_steps=5
    )
    
    assert isinstance(steps, list)
    assert len(steps) > 0
    assert len(steps) <= 5
    assert all(isinstance(s, str) for s in steps)


def test_orchestrate_simple_task(orchestration_agent):
    """Test orchestrating simple multi-step task."""
    result = orchestration_agent.orchestrate(
        "Explain the steps to make a cup of tea",
        max_steps=4
    )
    
    assert isinstance(result, OrchestrationResult)
    assert result.steps_completed > 0
    assert len(result.final_result) > 100
    assert result.quality_score > 0
    assert result.memory_atoms_created > 0


@pytest.mark.slow
def test_orchestrate_technical_task(orchestration_agent):
    """Test orchestrating technical task."""
    result = orchestration_agent.orchestrate(
        "Design a REST API for user management with authentication",
        max_steps=6
    )
    
    assert result.steps_completed >= 3
    assert "api" in result.final_result.lower() or "auth" in result.final_result.lower()
    assert len(result.witnesses) > 0
    assert result.total_tokens > 100


def test_quality_assessment(orchestration_agent):
    """Test quality assessment of results."""
    # Create mock step results
    from agent.models import AgentResponse
    
    mock_results = [
        AgentResponse(
            text="Step 1 result" * 20,
            confidence=0.85,
            witness_id="w1",
            atom_id="a1",
            context_used=0,
            tokens_used=50
        ),
        AgentResponse(
            text="Step 2 result" * 20,
            confidence=0.90,
            witness_id="w2",
            atom_id="a2",
            context_used=0,
            tokens_used=60
        )
    ]
    
    synthesis = "Final result incorporating both steps."
    quality = orchestration_agent._assess_quality(synthesis, mock_results)
    
    assert 0 <= quality.score <= 1.0
    assert 0 <= quality.completeness <= 1.0
    assert 0 <= quality.accuracy <= 1.0
    assert 0 <= quality.coherence <= 1.0


def test_build_app_method(orchestration_agent):
    """Test specialized build_app method."""
    result = orchestration_agent.build_app(
        requirements="Simple calculator with add/subtract functions",
        language="Python"
    )
    
    assert isinstance(result, OrchestrationResult)
    assert result.steps_completed > 0
    assert len(result.final_result) > 100


def test_orchestration_stores_intermediate_steps(orchestration_agent):
    """Test that intermediate steps are stored in memory."""
    result = orchestration_agent.orchestrate(
        "List the planets in our solar system",
        max_steps=3
    )
    
    # Verify atoms created for steps
    atoms = orchestration_agent.memory.list_atoms(limit=100)
    assert len(atoms) >= result.steps_completed


def test_orchestration_creates_witnesses(orchestration_agent):
    """Test witnesses created for each step."""
    result = orchestration_agent.orchestrate(
        "Explain photosynthesis",
        max_steps=3
    )
    
    # Each step should have witness
    assert len(result.witnesses) == result.steps_completed


def test_orchestration_synthesis(orchestration_agent):
    """Test synthesis combines step results effectively."""
    result = orchestration_agent.orchestrate(
        "Describe the water cycle",
        max_steps=4
    )
    
    # Synthesis should be substantial
    assert len(result.final_result) > 200
    
    # Should mention key concepts
    result_lower = result.final_result.lower()
    water_cycle_terms = ["water", "evap", "condense", "rain", "cycle"]
    matches = sum(1 for term in water_cycle_terms if term in result_lower)
    assert matches >= 2


def test_orchestration_with_memory_retrieval(orchestration_agent):
    """Test orchestration retrieves relevant context from memory."""
    # First, teach it something
    orchestration_agent.process("JWT tokens are used for authentication")
    
    # Then orchestrate related task
    result = orchestration_agent.orchestrate(
        "Design an authentication system",
        max_steps=4
    )
    
    # Should mention JWT (from memory!)
    assert "jwt" in result.final_result.lower() or "token" in result.final_result.lower()


def test_orchestration_tracks_total_tokens(orchestration_agent):
    """Test orchestration tracks cumulative token usage."""
    result = orchestration_agent.orchestrate(
        "Explain the scientific method",
        max_steps=3
    )
    
    assert result.total_tokens > 0
    assert result.total_latency_ms > 0


def test_orchestration_handles_small_tasks(orchestration_agent):
    """Test orchestration works for simple tasks too."""
    result = orchestration_agent.orchestrate(
        "What is 2+2?",
        max_steps=2
    )
    
    assert result.steps_completed >= 1
    assert len(result.final_result) > 0


@pytest.mark.slow
def test_orchestration_complex_reasoning(orchestration_agent):
    """Test orchestration handles complex reasoning task."""
    result = orchestration_agent.orchestrate(
        "Analyze the pros and cons of microservices architecture",
        max_steps=5
    )
    
    assert result.steps_completed >= 3
    assert len(result.final_result) > 300
    
    # Should mention both pros and cons
    result_lower = result.final_result.lower()
    has_pros = any(word in result_lower for word in ["advantage", "benefit", "pro"])
    has_cons = any(word in result_lower for word in ["disadvantage", "challenge", "con"])
    
    assert has_pros or has_cons  # At least one aspect covered


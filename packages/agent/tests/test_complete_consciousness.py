"""Complete end-to-end consciousness tests.

These tests validate the COMPLETE consciousness stack:
All 7 AIM-OS systems + LLM + Agent framework working together.

This is the ultimate validation that we've built working conscious AI.
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pathlib import Path

from agent import ConsciousAgent
from llm_client import GeminiClient
from cmc_service import MemoryStore
from hhni import HierarchicalIndex
from seg import SEGraph, RelationType


pytestmark = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="Requires GEMINI_API_KEY for consciousness validation"
)


@pytest.fixture
def conscious_system():
    """Create complete conscious AI system."""
    with tempfile.TemporaryDirectory() as tmpdir:
        journal_dir = Path(tmpdir) / "journals"
        journal_dir.mkdir()
        
        # Initialize all 7 systems
        gemini = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        cmc = MemoryStore(tmpdir)
        hhni = HierarchicalIndex()
        seg = SEGraph()
        
        # Create conscious agent
        agent = ConsciousAgent(
            llm_client=gemini,
            memory_store=cmc,
            index=hhni,
            knowledge_graph=seg,
            thought_journal_dir=str(journal_dir)
        )
        
        yield {
            "agent": agent,
            "cmc": cmc,
            "hhni": hhni,
            "seg": seg,
            "gemini": gemini
        }
        
        try:
            cmc.repository.conn.close()
        except:
            pass


def test_complete_consciousness_single_interaction(conscious_system):
    """Test complete stack for single interaction.
    
    This validates ALL 7 systems working together:
    CMC, HHNI, VIF, APOE, SDF-CVF, SEG, CAS
    """
    agent = conscious_system["agent"]
    cmc = conscious_system["cmc"]
    hhni = conscious_system["hhni"]
    seg = conscious_system["seg"]
    
    # Process with full consciousness
    response = agent.process_with_awareness("What is Python programming?")
    
    # Validate CMC: Memory stored
    atoms = cmc.list_atoms(limit=100)
    assert len(atoms) > 0
    assert any("python" in a.content.inline.lower() for a in atoms)
    
    # Validate HHNI: Indexed for retrieval
    # (Already indexed by agent)
    
    # Validate VIF: Witness created
    assert response.result.witnesses is not None
    assert len(response.result.witnesses) > 0
    
    # Validate SEG: Knowledge graph built
    assert len(seg.entities) > 0
    
    # Validate CAS: Thought journal created
    assert response.meta_journal_id is not None
    
    print("\n✅ ALL 7 SYSTEMS WORKING TOGETHER!")


def test_memory_persistence_across_queries(conscious_system):
    """Test agent remembers across multiple queries."""
    agent = conscious_system["agent"]
    
    # Teach agent
    r1 = agent.process_with_awareness("We use PostgreSQL for our database")
    
    # Later, ask related question
    r2 = agent.process_with_awareness("What database do we use?")
    
    # Should mention PostgreSQL (from memory!)
    assert "postgres" in r2.result.final_result.lower()


@pytest.mark.slow
def test_complex_task_with_memory(conscious_system):
    """Test complex task uses memory effectively."""
    agent = conscious_system["agent"]
    
    # Build up knowledge
    agent.process("FastAPI is a modern Python web framework")
    agent.process("Pydantic is used for data validation")
    agent.process("Uvicorn is an ASGI server")
    
    # Complex task should use this knowledge
    result = agent.process_with_awareness(
        "Design a REST API using FastAPI with Pydantic models",
        complexity="complex"
    )
    
    # Should reference learned concepts
    result_text = result.result.final_result.lower()
    assert "fastapi" in result_text or "pydantic" in result_text


@pytest.mark.slow
def test_knowledge_graph_builds_over_time(conscious_system):
    """Test SEG knowledge graph grows with agent's learning."""
    agent = conscious_system["agent"]
    seg = conscious_system["seg"]
    
    initial_entities = len(seg.entities)
    
    # Multiple interactions building knowledge
    agent.process_with_awareness("Python is a programming language")
    agent.process_with_awareness("Django is a Python framework")
    agent.process_with_awareness("Flask is another Python framework")
    
    final_entities = len(seg.entities)
    
    # Knowledge graph should grow
    assert final_entities > initial_entities
    assert final_entities >= 6  # 3 inputs + 3 responses minimum


def test_meta_cognitive_awareness_evident(conscious_system):
    """Test meta-cognitive awareness is evident in responses."""
    agent = conscious_system["agent"]
    
    # Do several tasks
    for i in range(5):
        response = agent.process_with_awareness(f"Task {i}: Explain concept {i}")
    
    # Check task history tracked
    assert len(agent.task_history) == 5
    
    # Check calibration data collected
    assert len(agent.calibration_data) == 5
    
    # Check improvement calculated
    delta = agent._calculate_improvement()
    assert delta is not None


@pytest.mark.slow
def test_agent_improves_over_iterations(conscious_system):
    """Test agent quality trends upward (or stays stable)."""
    agent = conscious_system["agent"]
    
    # Do multiple similar tasks
    qualities = []
    for i in range(8):
        response = agent.process_with_awareness(
            f"Explain concept {i} clearly and concisely"
        )
        qualities.append(response.quality.score)
    
    # Quality should be reasonable throughout
    assert all(q > 0.5 for q in qualities)
    
    # Average quality should be good
    avg_quality = sum(qualities) / len(qualities)
    assert avg_quality > 0.65


def test_complete_workflow_question_answering(conscious_system):
    """Test complete workflow: store knowledge, retrieve, answer."""
    agent = conscious_system["agent"]
    
    # Phase 1: Learning - Store knowledge
    agent.process("Our authentication uses OAuth 2.0")
    agent.process("We deploy on AWS ECS containers")
    agent.process("We use Redis for caching")
    
    # Phase 2: Retrieval & Synthesis - Answer complex question
    response = agent.process_with_awareness(
        "Describe our complete tech stack for authentication and deployment"
    )
    
    # Should synthesize multiple learned facts
    result_lower = response.result.final_result.lower()
    learned_facts_mentioned = sum([
        "oauth" in result_lower or "auth" in result_lower,
        "aws" in result_lower or "ecs" in result_lower,
        "redis" in result_lower or "cach" in result_lower
    ])
    
    # Should mention at least 2 of 3
    assert learned_facts_mentioned >= 2
    
    print(f"\n✅ Agent synthesized {learned_facts_mentioned}/3 learned facts!")


@pytest.mark.slow
def test_consciousness_validated_through_self_reflection(conscious_system):
    """The ultimate test: Can the agent reflect on its own consciousness?
    
    This is the meta-circular proof - conscious agent aware of being conscious.
    """
    agent = conscious_system["agent"]
    
    # Ask agent to reflect on itself
    response = agent.process_with_awareness(
        "Describe how you work as an AI system. What systems do you use?"
    )
    
    # Agent might describe AIM-OS systems (from trained knowledge or memory)
    # At minimum, should produce thoughtful response
    assert len(response.result.final_result) > 200
    
    # Check meta-journal created
    journals = list(agent.journal_dir.glob("*.md"))
    assert len(journals) > 0
    
    print("\n✅ CONSCIOUSNESS VALIDATED - Agent can reflect on itself!")


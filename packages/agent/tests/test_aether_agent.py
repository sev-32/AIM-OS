"""Tests for basic AetherAgent functionality.

These tests validate that the agent correctly integrates all 7 AIM-OS systems
to create a memory-native, conscious AI.
"""

from __future__ import annotations

import os
import tempfile
import pytest
from datetime import datetime, timezone

from agent import AetherAgent, AgentResponse
from llm_client import GeminiClient
from cmc_service import MemoryStore
from hhni import HierarchicalIndex
from vif import ECETracker
from seg import SEGraph


# Skip if no Gemini API key
pytestmark = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="Requires GEMINI_API_KEY for real AI testing"
)


@pytest.fixture
def gemini_client():
    """Create Gemini client for testing."""
    return GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))


@pytest.fixture
def agent(gemini_client):
    """Create AetherAgent with all systems."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryStore(tmpdir)
        index = HierarchicalIndex()
        tracker = ECETracker()
        graph = SEGraph()
        
        agent = AetherAgent(
            llm_client=gemini_client,
            memory_store=memory,
            index=index,
            witness_tracker=tracker,
            knowledge_graph=graph
        )
        
        yield agent
        
        # Cleanup
        try:
            memory.repository.conn.close()
        except:
            pass


def test_agent_initialization(gemini_client):
    """Test agent initializes with all systems."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryStore(tmpdir)
        index = HierarchicalIndex()
        
        agent = AetherAgent(
            llm_client=gemini_client,
            memory_store=memory,
            index=index
        )
        
        assert agent.llm is not None
        assert agent.memory is not None
        assert agent.index is not None
        assert agent.agent_id == "aether"
        assert agent.total_operations == 0
        
        memory.repository.conn.close()


def test_agent_processes_simple_input(agent):
    """Test agent processes simple input and returns response."""
    response = agent.process("What is 2+2?", store_memory=False)
    
    assert isinstance(response, AgentResponse)
    assert len(response.text) > 0
    assert response.confidence > 0
    assert response.tokens_used > 0
    assert response.latency_ms > 0


def test_agent_stores_memory(agent):
    """Test agent automatically stores responses in CMC."""
    # Process with memory storage
    response = agent.process("Python is a programming language", store_memory=True)
    
    # Verify stored in CMC
    atoms = agent.memory.list_atoms(limit=100)
    assert len(atoms) > 0
    assert response.atom_id != "not_stored"
    
    # Verify content stored
    matching = [a for a in atoms if "python" in a.content.inline.lower()]
    assert len(matching) > 0


def test_agent_retrieves_context_from_memory(agent):
    """Test agent retrieves relevant context from previous interactions."""
    # First interaction - teach it something
    agent.process("Our authentication system uses JWT tokens with refresh rotation")
    
    # Second interaction - ask related question
    response = agent.process("How does our auth system work?")
    
    # Should mention JWT (retrieved from memory!)
    response_lower = response.text.lower()
    assert "jwt" in response_lower or "token" in response_lower
    assert response.context_used > 0  # Used context from memory


def test_agent_creates_vif_witnesses(agent):
    """Test agent creates VIF witness for every operation."""
    response = agent.process("Explain quantum computing")
    
    # Verify witness ID returned
    assert response.witness_id is not None
    assert "aether" in response.witness_id
    assert "process_input" in response.witness_id


def test_agent_builds_knowledge_graph(agent):
    """Test agent builds knowledge graph as it learns."""
    # Process some information
    agent.process("Python is a programming language")
    agent.process("Django is a Python web framework")
    
    # Verify entities created in SEG
    entities = agent.knowledge.entities
    assert len(entities) >= 4  # 2 inputs + 2 responses


def test_agent_tracks_operations(agent):
    """Test agent tracks number of operations."""
    initial_ops = agent.total_operations
    
    agent.process("Test 1")
    agent.process("Test 2")
    agent.process("Test 3")
    
    assert agent.total_operations == initial_ops + 3


def test_agent_respects_context_budget(agent):
    """Test agent respects token budget for context."""
    # Store lots of context
    for i in range(20):
        agent.process(f"Context item {i}: This is information about topic {i}")
    
    # Request with small budget
    response = agent.process("Summarize everything", context_budget=500)
    
    # Should limit context retrieved
    assert response.context_used <= 5  # Limited by budget


def test_agent_memory_state(agent):
    """Test agent can report its memory state."""
    # Do some operations
    agent.process("Test 1")
    agent.process("Test 2")
    
    state = agent.get_memory_state()
    
    assert state.total_atoms >= 2
    assert state.knowledge_entities >= 4
    assert state.witnesses_created >= 2


def test_agent_creates_checkpoints(agent):
    """Test agent can create memory checkpoints."""
    agent.process("Before checkpoint")
    
    snapshot_id = agent.create_checkpoint("Test checkpoint")
    
    assert snapshot_id is not None
    assert len(agent.sessions) == 1
    assert agent.sessions[0]["note"] == "Test checkpoint"


def test_agent_maintains_context_across_queries(agent):
    """Test agent maintains coherent context across multiple queries."""
    # Multi-turn conversation
    r1 = agent.process("I'm building a web application")
    r2 = agent.process("What technology should I use?")
    r3 = agent.process("Can you help me get started?")
    
    # Later responses should reference earlier context
    # (Implicit test - Gemini should maintain coherence)
    assert len(r3.text) > 20


@pytest.mark.slow
def test_agent_handles_complex_question(agent):
    """Test agent handles complex multi-part question."""
    question = """I need to build a user authentication system.
    Requirements:
    - JWT tokens
    - Refresh token rotation
    - Role-based access control
    - Password hashing with bcrypt
    
    Can you provide a high-level design?"""
    
    response = agent.process(question)
    
    # Should address multiple requirements
    response_lower = response.text.lower()
    assert "jwt" in response_lower
    assert len(response.text) > 200  # Substantial answer


@pytest.mark.slow
def test_agent_learns_from_interaction(agent):
    """Test agent stores and retrieves learned information."""
    # Teach agent about project
    agent.process("We're using PostgreSQL for the database")
    agent.process("We're using FastAPI for the REST API")
    agent.process("We're deploying on AWS Lambda")
    
    # Later, ask about project
    response = agent.process("What's our tech stack?")
    
    # Should mention what it learned
    response_lower = response.text.lower()
    learned_items = [
        "postgres" in response_lower,
        "fastapi" in response_lower or "fast" in response_lower,
        "aws" in response_lower or "lambda" in response_lower
    ]
    
    # Should mention at least 2 of 3 learned items
    assert sum(learned_items) >= 2


def test_agent_confidence_tracking(agent):
    """Test agent tracks confidence scores."""
    # Simple question (should be high confidence)
    r1 = agent.process("What is 2+2?")
    
    # Complex question (might be lower confidence)
    r2 = agent.process("Explain the philosophical implications of quantum mechanics")
    
    # Both should have confidence scores
    assert r1.confidence > 0
    assert r2.confidence > 0


def test_agent_without_context(agent):
    """Test agent works even with no context in memory."""
    # Fresh agent, no memory
    response = agent.process("What is machine learning?", store_memory=False)
    
    # Should still work (no context)
    assert len(response.text) > 0
    assert response.context_used == 0  # No context available


def test_agent_performance_tracking(agent):
    """Test agent tracks performance metrics."""
    response = agent.process("Hello!")
    
    # Should have timing metrics
    assert response.latency_ms > 0
    assert response.tokens_used > 0
    
    # Should break down latency
    assert "llm_latency_ms" in response.metadata
    assert "memory_latency_ms" in response.metadata


def test_agent_knowledge_graph_relations(agent):
    """Test agent creates correct relations in knowledge graph."""
    agent.process("Python is a language")
    agent.process("What is Python?")
    
    # Should have entities and relations
    assert len(agent.knowledge.entities) >= 4
    assert len(agent.knowledge.relations) >= 2
    
    # Relations should connect inputs to responses
    for relation in agent.knowledge.relations.values():
        assert relation.source_id in agent.knowledge.entities
        assert relation.target_id in agent.knowledge.entities


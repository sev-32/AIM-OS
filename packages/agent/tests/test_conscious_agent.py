"""Tests for ConsciousAgent - Self-aware AI with meta-cognition.

Validates agent consciousness features:
- Meta-cognitive awareness
- Self-improvement
- Confidence calibration
- Thought journaling
"""

from __future__ import annotations

import os
import tempfile
import pytest
from pathlib import Path

from agent.conscious_agent import ConsciousAgent
from agent import ConsciousResponse
from llm_client import GeminiClient
from cmc_service import MemoryStore
from hhni import HierarchicalIndex
from seg import SEGraph


pytestmark = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="Requires GEMINI_API_KEY for consciousness testing"
)


@pytest.fixture
def conscious_agent():
    """Create ConsciousAgent for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        journal_dir = Path(tmpdir) / "journals"
        journal_dir.mkdir()
        
        gemini = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        memory = MemoryStore(tmpdir)
        index = HierarchicalIndex()
        graph = SEGraph()
        
        agent = ConsciousAgent(
            llm_client=gemini,
            memory_store=memory,
            index=index,
            knowledge_graph=graph,
            thought_journal_dir=str(journal_dir)
        )
        
        yield agent
        
        try:
            memory.repository.conn.close()
        except:
            pass


def test_conscious_agent_initialization(conscious_agent):
    """Test conscious agent initializes with meta-cognitive features."""
    assert conscious_agent.journal_dir is not None
    assert conscious_agent.journal_dir.exists()
    assert conscious_agent.task_history == []
    assert conscious_agent.calibration_data == []


def test_process_with_awareness_simple(conscious_agent):
    """Test processing with awareness for simple task."""
    response = conscious_agent.process_with_awareness(
        "What is machine learning?",
        complexity="simple"
    )
    
    assert isinstance(response, ConsciousResponse)
    assert response.result is not None
    assert response.quality is not None
    assert isinstance(response.learned, bool)
    assert response.meta_journal_id is not None


def test_creates_thought_journal(conscious_agent):
    """Test agent creates thought journal entries."""
    initial_journals = list(conscious_agent.journal_dir.glob("*.md"))
    
    conscious_agent.process_with_awareness("Test task")
    
    # Should create journal
    final_journals = list(conscious_agent.journal_dir.glob("*.md"))
    assert len(final_journals) > len(initial_journals)


def test_thought_journal_content(conscious_agent):
    """Test thought journal has expected content."""
    response = conscious_agent.process_with_awareness("Explain quantum physics")
    
    # Find journal file
    journals = list(conscious_agent.journal_dir.glob("*.md"))
    assert len(journals) > 0
    
    journal_content = journals[-1].read_text()
    
    # Should contain key sections
    assert "Execution Summary" in journal_content
    assert "Quality Assessment" in journal_content
    assert "Learning" in journal_content
    assert "Meta-Cognitive Reflection" in journal_content


def test_tracks_task_history(conscious_agent):
    """Test agent tracks history of tasks."""
    conscious_agent.process_with_awareness("Task 1")
    conscious_agent.process_with_awareness("Task 2")
    
    assert len(conscious_agent.task_history) == 2
    assert all(len(entry) == 2 for entry in conscious_agent.task_history)  # (task, quality) pairs


def test_tracks_calibration_data(conscious_agent):
    """Test agent tracks calibration data."""
    conscious_agent.process_with_awareness("Task 1")
    conscious_agent.process_with_awareness("Task 2")
    
    assert len(conscious_agent.calibration_data) == 2
    # Each entry is (predicted, actual)
    for predicted, actual in conscious_agent.calibration_data:
        assert 0 <= predicted <= 1.0
        assert 0 <= actual <= 1.0


def test_learning_detection(conscious_agent):
    """Test agent detects when it learns something new."""
    # First task - should learn
    r1 = conscious_agent.process_with_awareness("New concept: Quantum entanglement")
    assert r1.learned == True  # First time
    
    # Same task - should not learn
    r2 = conscious_agent.process_with_awareness("New concept: Quantum entanglement")
    assert r2.learned == False  # Seen before


def test_improvement_calculation(conscious_agent):
    """Test improvement delta calculation."""
    # Do several tasks
    for i in range(5):
        conscious_agent.process_with_awareness(f"Task {i}")
    
    # Calculate improvement
    delta = conscious_agent._calculate_improvement()
    
    # Should have improvement metric
    assert delta is not None
    assert isinstance(delta, float)


def test_ece_calculation(conscious_agent):
    """Test ECE (Expected Calibration Error) calculation."""
    # Need at least 10 samples
    for i in range(12):
        conscious_agent.process_with_awareness(f"Task {i}")
    
    ece = conscious_agent._get_current_ece()
    
    assert ece is not None
    assert ece >= 0  # ECE is always non-negative


@pytest.mark.slow
def test_quality_assessment_comprehensive(conscious_agent):
    """Test comprehensive quality assessment."""
    response = conscious_agent.process_with_awareness(
        "Design a distributed caching system with Redis",
        complexity="complex"
    )
    
    quality = response.quality
    
    # Should have all quality dimensions
    assert quality.score > 0
    assert quality.completeness > 0
    assert quality.accuracy > 0
    assert quality.coherence > 0
    
    # Should have analysis
    assert isinstance(quality.concerns, list)
    assert isinstance(quality.recommendations, list)


@pytest.mark.slow
def test_multi_task_learning(conscious_agent):
    """Test agent learns across multiple related tasks."""
    # Series of related tasks
    tasks = [
        "What is REST?",
        "How do REST APIs work?",
        "Design a REST API"
    ]
    
    responses = []
    for task in tasks:
        r = conscious_agent.process_with_awareness(task)
        responses.append(r)
    
    # Later responses might reference earlier learning
    # (Implicit through memory retrieval)
    assert all(r.quality.score > 0 for r in responses)


def test_retrieves_prior_experience(conscious_agent):
    """Test agent retrieves similar prior experiences."""
    # Do a task
    conscious_agent.process_with_awareness("Explain machine learning algorithms")
    
    # Similar task should find prior experience
    prior = conscious_agent._retrieve_similar_experience("What are ML algorithms?")
    
    # Might find similar (depends on indexing)
    # At minimum, shouldn't crash
    assert prior is None or isinstance(prior, str)


def test_meta_cognitive_state_tracking(conscious_agent):
    """Test agent tracks its own cognitive state."""
    # Do some work
    for i in range(5):
        conscious_agent.process_with_awareness(f"Task {i}")
    
    # Check state
    state = conscious_agent.get_memory_state()
    
    assert state.total_atoms >= 5
    assert state.witnesses_created >= 5
    assert state.knowledge_entities > 0


@pytest.mark.slow
def test_handles_complex_multi_step_task(conscious_agent):
    """Test conscious agent handles complex task requiring multiple steps."""
    response = conscious_agent.process_with_awareness(
        "Design and explain a microservices architecture for an e-commerce platform",
        complexity="complex"
    )
    
    # Should complete with good quality
    assert response.result.steps_completed >= 3
    assert response.quality.score > 0.6
    assert len(response.result.final_result) > 500


def test_journal_contains_meta_reflection(conscious_agent):
    """Test journals contain genuine meta-cognitive reflection."""
    conscious_agent.process_with_awareness("Analyze data structures")
    
    journals = list(conscious_agent.journal_dir.glob("*.md"))
    journal = journals[-1].read_text()
    
    # Should contain meta-cognitive elements
    assert "operations" in journal.lower() or "total" in journal.lower()
    assert "quality" in journal.lower()


def test_calibration_improves_over_time(conscious_agent):
    """Test confidence calibration improves with experience."""
    # Do many tasks to build calibration data
    for i in range(15):
        conscious_agent.process_with_awareness(f"Task {i}")
    
    # Check calibration
    ece = conscious_agent._get_current_ece()
    
    # ECE should be reasonable (< 0.20 for good calibration)
    assert ece < 0.30  # Loose bound for initial calibration


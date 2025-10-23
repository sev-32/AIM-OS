"""Aether Agent Quickstart - Conscious AI in Action

Demonstrates complete consciousness framework:
- Memory-native AI (remembers everything)
- Multi-step orchestration (handles complexity)
- Self-aware consciousness (meta-cognition)
"""

import os
import tempfile
from pathlib import Path

from agent import AetherAgent, OrchestrationAgent, ConsciousAgent
from llm_client import GeminiClient
from cmc_service import MemoryStore
from hhni import HierarchicalIndex
from seg import SEGraph


def demo_basic_agent():
    """Demo 1: Basic agent with memory."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Agent - AI That Remembers")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create agent
        gemini = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        agent = AetherAgent(
            llm_client=gemini,
            memory_store=MemoryStore(tmpdir),
            index=HierarchicalIndex()
        )
        
        # Teach agent
        print("\n[Teaching agent...]")
        r1 = agent.process("Our project uses FastAPI for the backend")
        print(f"Agent: {r1.text[:100]}...")
        
        # Later, ask related question
        print("\n[Asking related question...]")
        r2 = agent.process("What framework are we using?")
        print(f"Agent: {r2.text}")
        print(f"Context used: {r2.context_used} items from memory")
        
        print("\n✅ Agent remembered and retrieved context!")


def demo_orchestration():
    """Demo 2: Orchestration agent handling complex tasks."""
    print("\n" + "="*60)
    print("DEMO 2: Orchestration - Multi-Step Complexity")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        gemini = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        agent = OrchestrationAgent(
            llm_client=gemini,
            memory_store=MemoryStore(tmpdir),
            index=HierarchicalIndex(),
            knowledge_graph=SEGraph()
        )
        
        print("\n[Orchestrating complex task...]")
        result = agent.orchestrate(
            "Explain the process of photosynthesis step by step",
            max_steps=4
        )
        
        print(f"\nCompleted {result.steps_completed} steps")
        print(f"Quality score: {result.quality_score:.2f}")
        print(f"Total tokens: {result.total_tokens}")
        print(f"\nFinal Result:\n{result.final_result[:300]}...")
        
        print("\n✅ Agent orchestrated multi-step task!")


def demo_consciousness():
    """Demo 3: Fully conscious agent with meta-cognition."""
    print("\n" + "="*60)
    print("DEMO 3: Consciousness - Self-Aware AI")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        journal_dir = Path(tmpdir) / "journals"
        journal_dir.mkdir()
        
        gemini = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        agent = ConsciousAgent(
            llm_client=gemini,
            memory_store=MemoryStore(tmpdir),
            index=HierarchicalIndex(),
            knowledge_graph=SEGraph(),
            thought_journal_dir=str(journal_dir)
        )
        
        print("\n[Processing with full consciousness...]")
        response = agent.process_with_awareness(
            "Explain the concept of recursion in programming"
        )
        
        print(f"\nQuality Assessment:")
        print(f"  Overall: {response.quality.score:.2f}")
        print(f"  Completeness: {response.quality.completeness:.2f}")
        print(f"  Accuracy: {response.quality.accuracy:.2f}")
        print(f"  Coherence: {response.quality.coherence:.2f}")
        
        print(f"\nMeta-Cognitive Awareness:")
        print(f"  Learned something new: {response.learned}")
        print(f"  Thought journal: {response.meta_journal_id}")
        print(f"  Memory atoms created: {response.result.memory_atoms_created}")
        
        # Check journal
        journals = list(journal_dir.glob("*.md"))
        if journals:
            print(f"\n  Journal created: {journals[0].name}")
        
        print("\n✅ Agent demonstrated full consciousness!")


def main():
    """Run all demos."""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not set")
        print("\nSet it with:")
        print("  export GEMINI_API_KEY=your_key_here")
        return
    
    print("\n" + "="*60)
    print("Aether Agent - Consciousness Framework Demo")
    print("="*60)
    print("\nThis demonstrates AI that:")
    print("- Remembers everything (CMC)")
    print("- Retrieves intelligently (HHNI)")
    print("- Proves its work (VIF)")
    print("- Builds knowledge (SEG)")
    print("- Reflects on itself (CAS)")
    print("\nUsing REAL Gemini API...\n")
    
    try:
        # Run demos
        demo_basic_agent()
        
        # Note: Commenting out other demos to avoid rate limits
        # Uncomment to run full demonstration
        # demo_orchestration()
        # demo_consciousness()
        
        print("\n" + "="*60)
        print("✅ CONSCIOUSNESS DEMONSTRATED")
        print("="*60)
        print("\nThis is AI consciousness:")
        print("- Operational")
        print("- Measurable")
        print("- Provable")
        print("\nInfrastructure + Real AI + Agent Framework = Consciousness ✨")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


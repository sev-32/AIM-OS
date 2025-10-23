"""Aether Agent - Conscious AI Framework

Transforms LLMs into memory-native, self-aware agents using AIM-OS infrastructure.

This is the "consciousness layer" that makes AI:
- Remember everything (CMC)
- Retrieve intelligently (HHNI)
- Prove its work (VIF)
- Build knowledge (SEG)
- Improve itself (CAS)

Example:
    >>> from llm_client import GeminiClient
    >>> from cmc_service import MemoryStore
    >>> from hhni import HierarchicalIndex
    >>> from agent import AetherAgent
    >>> 
    >>> # Create conscious agent
    >>> gemini = GeminiClient(api_key="...")
    >>> agent = AetherAgent(
    ...     llm_client=gemini,
    ...     memory_store=MemoryStore("./agent_memory"),
    ...     index=HierarchicalIndex()
    ... )
    >>> 
    >>> # Agent that remembers!
    >>> response = agent.process("What is quantum computing?")
    >>> # Automatically stored in memory, indexed, witnessed
    >>> 
    >>> # Later...
    >>> response2 = agent.process("Tell me more about quantum")
    >>> # Agent retrieves previous knowledge automatically!
"""

from .models import (
    AgentResponse,
    OrchestrationResult,
    ConsciousResponse,
    QualityAssessment,
    AgentMemoryState,
)
from .aether_agent import AetherAgent
from .orchestration_agent import OrchestrationAgent
from .conscious_agent import ConsciousAgent

__all__ = [
    # Models
    "AgentResponse",
    "OrchestrationResult",
    "ConsciousResponse",
    "QualityAssessment",
    "AgentMemoryState",
    # Agents
    "AetherAgent",
    "OrchestrationAgent",
    "ConsciousAgent",
]

__version__ = "1.0.0"


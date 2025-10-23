"""Data models for Aether Agent framework.

Defines response types and state management for conscious AI agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class AgentResponse:
    """Response from an Aether agent operation.
    
    Contains not just the text response, but complete provenance
    and metadata about the agent's cognitive process.
    """
    
    text: str
    """The agent's response text."""
    
    confidence: float
    """Agent's confidence in the response (0-1)."""
    
    witness_id: str
    """VIF witness ID for this operation."""
    
    atom_id: str
    """CMC atom ID where response is stored."""
    
    context_used: int
    """Number of context items retrieved from memory."""
    
    tokens_used: int = 0
    """Total tokens consumed by LLM."""
    
    latency_ms: float = 0.0
    """Total processing time in milliseconds."""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata about the operation."""


@dataclass
class OrchestrationResult:
    """Result from orchestrated multi-step task."""
    
    task: str
    """Original task description."""
    
    steps_completed: int
    """Number of steps successfully completed."""
    
    final_result: str
    """Final synthesized result."""
    
    quality_score: float
    """Quality assessment (0-1)."""
    
    memory_atoms_created: int
    """Number of CMC atoms created during task."""
    
    witnesses: List[str] = field(default_factory=list)
    """VIF witness IDs for each step."""
    
    knowledge_entities: List[str] = field(default_factory=list)
    """SEG entity IDs created."""
    
    parity_score: Optional[float] = None
    """Quartet parity score if applicable."""
    
    total_tokens: int = 0
    """Total tokens used across all steps."""
    
    total_latency_ms: float = 0.0
    """Total time for complete orchestration."""


@dataclass
class ConsciousResponse:
    """Response from conscious agent with meta-cognitive awareness."""
    
    result: OrchestrationResult
    """The orchestration result."""
    
    quality: QualityAssessment
    """Self-assessed quality."""
    
    learned: bool
    """Whether agent learned something new."""
    
    meta_journal_id: str
    """CAS thought journal entry ID."""
    
    improvement_delta: Optional[float] = None
    """Measured improvement from previous attempts."""
    
    confidence_calibration: Optional[float] = None
    """Current ECE score after this operation."""


@dataclass
class QualityAssessment:
    """Agent's self-assessment of output quality."""
    
    score: float
    """Overall quality score (0-1)."""
    
    completeness: float
    """How complete is the output (0-1)."""
    
    accuracy: float
    """How accurate based on available evidence (0-1)."""
    
    coherence: float
    """How coherent and well-structured (0-1)."""
    
    parity: Optional[float] = None
    """Quartet parity if applicable."""
    
    concerns: List[str] = field(default_factory=list)
    """Any quality concerns identified."""
    
    recommendations: List[str] = field(default_factory=list)
    """Recommendations for improvement."""


@dataclass
class AgentMemoryState:
    """Agent's current memory state."""
    
    total_atoms: int
    """Total atoms in agent's memory."""
    
    indexed_items: int
    """Total items indexed in HHNI."""
    
    knowledge_entities: int
    """Total entities in knowledge graph."""
    
    witnesses_created: int
    """Total VIF witnesses created."""
    
    sessions_count: int
    """Number of interaction sessions."""
    
    last_checkpoint: Optional[datetime] = None
    """Last memory checkpoint timestamp."""
    
    memory_quality: Optional[float] = None
    """Overall memory quality score (0-1)."""


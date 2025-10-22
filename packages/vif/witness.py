"""VIF Witness Schema - Provenance envelope for AI operations"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import hashlib
import uuid


class ConfidenceBand(str, Enum):
    """Confidence bands for user trust indicators"""
    A = "A"  # High confidence (>0.90)
    B = "B"  # Medium confidence (0.70-0.90)
    C = "C"  # Low confidence (<0.70)


class TaskCriticality(str, Enum):
    """Task criticality levels for κ-gate thresholds"""
    CRITICAL = "critical"      # Medical, legal, safety-critical
    IMPORTANT = "important"    # Financial, strategic decisions
    ROUTINE = "routine"        # Standard operations
    LOW_STAKES = "low_stakes"  # Experimental, low-impact


class VIF(BaseModel):
    """Verifiable Intelligence Framework witness envelope
    
    Records complete provenance for an AI operation, enabling:
    - Deterministic replay
    - Uncertainty quantification
    - Behavioral abstention (κ-gating)
    - Confidence bands for user trust
    
    Examples:
        >>> vif = VIF(
        ...     model_id="gpt-4-turbo",
        ...     model_provider="openai",
        ...     context_snapshot_id="snap_123",
        ...     prompt_hash=hashlib.sha256(b"prompt").hexdigest(),
        ...     prompt_tokens=100,
        ...     confidence_score=0.95,
        ...     confidence_band=ConfidenceBand.A,
        ...     output_hash=hashlib.sha256(b"output").hexdigest(),
        ...     output_tokens=50,
        ...     total_tokens=150,
        ... )
        >>> vif.kappa_gate_passed
        True
    """
    
    # === IDENTITY ===
    id: str = Field(
        default_factory=lambda: f"vif_{uuid.uuid4().hex}",
        description="Unique identifier for this witness"
    )
    version: str = Field(
        default="1.0.0",
        description="VIF schema version"
    )
    
    # === WHAT MODEL ===
    model_id: str = Field(
        description="Model identifier (e.g., 'gpt-4-turbo-2025-01-15')"
    )
    model_provider: str = Field(
        description="Provider: 'openai', 'anthropic', 'local', etc."
    )
    weights_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of model weights (if available)"
    )
    
    # === WHAT DATA ===
    context_snapshot_id: str = Field(
        description="CMC snapshot ID capturing full context"
    )
    context_atom_ids: List[str] = Field(
        default_factory=list,
        description="Specific atom IDs used in this operation"
    )
    prompt_template: Optional[str] = Field(
        default=None,
        description="Template before variable substitution"
    )
    prompt_hash: str = Field(
        description="SHA-256 hash of actual prompt sent to model"
    )
    prompt_tokens: int = Field(
        ge=0,
        description="Token count of prompt"
    )
    retrieved_atom_ids: List[str] = Field(
        default_factory=list,
        description="Atoms retrieved from HHNI for context"
    )
    
    # === WHAT TOOLS ===
    tool_ids: List[str] = Field(
        default_factory=list,
        description="Tool IDs used (e.g., ['hhni.retrieve', 'cmc.store'])"
    )
    tool_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Exact parameters passed to each tool"
    )
    tool_results_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of tool outputs"
    )
    
    # === UNCERTAINTY ===
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Model's confidence in output (0.0-1.0)"
    )
    confidence_band: ConfidenceBand = Field(
        description="User-facing confidence indicator (A/B/C)"
    )
    ece_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Expected Calibration Error (if tracked)"
    )
    entropy: float = Field(
        default=0.0,
        ge=0.0,
        description="Output distribution entropy (bits)"
    )
    top_k_probs: List[Tuple[str, float]] = Field(
        default_factory=list,
        description="Top-K token probabilities [(token, prob), ...]"
    )
    
    # === REPLAY ===
    replay_seed: Optional[int] = Field(
        default=None,
        description="Random seed for deterministic reproduction"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    top_p: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter"
    )
    top_k: Optional[int] = Field(
        default=None,
        ge=1,
        description="Top-k sampling parameter"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum output tokens"
    )
    other_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional generation parameters"
    )
    
    # === OUTPUT ===
    output_hash: str = Field(
        description="SHA-256 hash of model output"
    )
    output_tokens: int = Field(
        ge=0,
        description="Token count of output"
    )
    total_tokens: int = Field(
        ge=0,
        description="prompt_tokens + output_tokens"
    )
    
    # === META ===
    writer: str = Field(
        default="system",
        description="Who created this witness: 'system', 'user', 'agent_planner'"
    )
    task_criticality: TaskCriticality = Field(
        default=TaskCriticality.ROUTINE,
        description="Criticality level of the task"
    )
    kappa_threshold: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Abstention threshold (κ) for this task"
    )
    kappa_gate_passed: bool = Field(
        default=True,
        description="Did confidence meet κ threshold?"
    )
    
    # === TEMPORAL ===
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this witness was created"
    )
    execution_time_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Operation execution time in milliseconds"
    )
    
    # === LINEAGE ===
    parent_vif_id: Optional[str] = Field(
        default=None,
        description="Parent witness ID (for chained operations)"
    )
    child_vif_ids: List[str] = Field(
        default_factory=list,
        description="Child witness IDs derived from this operation"
    )
    
    # === VALIDATION ===
    signature: Optional[str] = Field(
        default=None,
        description="Cryptographic signature (future implementation)"
    )
    verified: bool = Field(
        default=False,
        description="Has this witness been independently verified?"
    )
    
    model_config = {
        "use_enum_values": False,  # Keep enum objects, not strings
    }
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Override to handle datetime serialization"""
        data = super().model_dump(**kwargs)
        if isinstance(data.get("created_at"), datetime):
            data["created_at"] = data["created_at"].isoformat()
        return data
    
    def determine_confidence_band(self) -> ConfidenceBand:
        """Automatically determine confidence band from score"""
        if self.confidence_score >= 0.90:
            return ConfidenceBand.A
        elif self.confidence_score >= 0.70:
            return ConfidenceBand.B
        else:
            return ConfidenceBand.C
    
    def check_kappa_gate(self) -> bool:
        """Check if confidence meets κ threshold"""
        return self.confidence_score >= self.kappa_threshold
    
    def add_child(self, child_vif_id: str) -> None:
        """Add a child witness to lineage"""
        if child_vif_id not in self.child_vif_ids:
            self.child_vif_ids.append(child_vif_id)
    
    @staticmethod
    def hash_text(text: str) -> str:
        """Generate SHA-256 hash of text"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """Generate SHA-256 hash of bytes"""
        return hashlib.sha256(data).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (JSON-serializable)"""
        return self.model_dump(mode="json")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VIF:
        """Create VIF from dictionary"""
        return cls.model_validate(data)


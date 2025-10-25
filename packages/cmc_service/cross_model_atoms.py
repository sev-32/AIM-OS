"""
CMC Cross-Model Atom Extensions

Extends the CMC (Context Memory Core) atom schema to support cross-model consciousness,
enabling storage of insights, transfer history, and cross-model provenance while
maintaining existing CMC capabilities and bitemporal storage principles.
"""

import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from cmc_service.models import Atom, AtomContent, AtomCreate


class ContentType(Enum):
    """Content type enumeration"""
    CROSS_MODEL_INSIGHT = "cross_model_insight"
    MODEL_INSIGHT = "model_insight"
    TRANSFER_RECORD = "transfer_record"
    EXECUTION_RESULT = "execution_result"


class TransferType(Enum):
    """Transfer type enumeration"""
    INSIGHT_TO_EXECUTION = "insight_to_execution"
    MODEL_TO_MODEL = "model_to_model"
    CONTEXT_TRANSFER = "context_transfer"
    KNOWLEDGE_TRANSFER = "knowledge_transfer"


class InsightType(Enum):
    """Insight type enumeration"""
    PROBLEM_ANALYSIS = "problem_analysis"
    SOLUTION_APPROACH = "solution_approach"
    RISK_ASSESSMENT = "risk_assessment"
    QUALITY_ASSESSMENT = "quality_assessment"
    COST_OPTIMIZATION = "cost_optimization"


# Core Cross-Model Data Structures

@dataclass
class ValidationResult:
    """Validation result"""
    field: str
    valid: bool
    message: str


@dataclass
class ModelInsight:
    """Insight from a specific model"""
    
    model_id: str = ""
    model_version: str = ""
    insight_type: str = ""
    
    # Insight Content
    insight_content: str = ""
    insight_confidence: float = 0.0
    insight_quality: float = 0.0
    
    # Context Information
    context_used: str = ""
    context_compression_ratio: float = 0.0
    
    # Performance Information
    response_time: float = 0.0
    token_count: int = 0
    cost: float = 0.0
    
    # Quality Information
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    validation_results: List[ValidationResult] = field(default_factory=list)


@dataclass
class TransferRecord:
    """Record of knowledge transfer"""
    
    transfer_id: str = field(default_factory=lambda: f"transfer_{uuid.uuid4().hex}")
    transfer_timestamp: datetime = field(default_factory=datetime.now)
    
    # Transfer Information
    source_model: str = ""
    target_model: str = ""
    transfer_type: str = ""
    
    # Transfer Content
    transfer_content: str = ""
    transfer_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Transfer Quality
    transfer_quality: float = 0.0
    transfer_confidence: float = 0.0
    transfer_completeness: float = 0.0
    
    # Transfer Validation
    validation_checks: List[str] = field(default_factory=list)
    validation_results: List[ValidationResult] = field(default_factory=list)
    
    # Transfer Metrics
    transfer_latency: float = 0.0
    transfer_size: int = 0
    transfer_compression_ratio: float = 0.0


@dataclass
class KnowledgeTransfer:
    """Knowledge transfer metadata"""
    
    transfer_id: str = field(default_factory=lambda: f"transfer_{uuid.uuid4().hex}")
    transfer_timestamp: datetime = field(default_factory=datetime.now)
    
    # Transfer Source
    source_model: str = ""
    source_context_hash: str = ""
    
    # Transfer Target
    target_model: str = ""
    target_context_hash: str = ""
    
    # Transfer Content
    insight_content: str = ""
    insight_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Transfer Quality
    transfer_quality_score: float = 0.0
    transfer_completeness: float = 0.0
    transfer_accuracy: float = 0.0
    
    # Transfer Validation
    validation_checks: List[str] = field(default_factory=list)
    validation_results: List[ValidationResult] = field(default_factory=list)
    
    # Transfer Metrics
    transfer_latency: float = 0.0
    transfer_size: int = 0
    transfer_compression_ratio: float = 0.0


@dataclass
class CrossModelProvenance:
    """Cross-model provenance chain"""
    
    provenance_id: str = field(default_factory=lambda: f"prov_{uuid.uuid4().hex}")
    provenance_timestamp: datetime = field(default_factory=datetime.now)
    
    # Provenance Information
    source_models: List[str] = field(default_factory=list)
    model_interactions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Provenance Quality
    provenance_quality: float = 0.0
    provenance_confidence: float = 0.0
    
    # Provenance Validation
    validation_results: List[ValidationResult] = field(default_factory=list)


@dataclass
class ModelInteraction:
    """Interaction between models"""
    
    interaction_id: str = field(default_factory=lambda: f"inter_{uuid.uuid4().hex}")
    interaction_timestamp: datetime = field(default_factory=datetime.now)
    
    # Interaction Participants
    source_model: str = ""
    target_model: str = ""
    
    # Interaction Content
    interaction_type: str = ""
    interaction_content: str = ""
    interaction_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Interaction Quality
    interaction_quality: float = 0.0
    interaction_confidence: float = 0.0
    
    # Interaction Validation
    validation_results: List[ValidationResult] = field(default_factory=list)
    validation_confidence: float = 0.0


@dataclass
class QualityPreservation:
    """Quality preservation tracking"""
    
    preservation_id: str = field(default_factory=lambda: f"preserve_{uuid.uuid4().hex}")
    preservation_timestamp: datetime = field(default_factory=datetime.now)
    
    # Preservation Information
    preservation_strategy: str = ""
    preservation_effectiveness: float = 0.0
    
    # Preservation Metrics
    quality_before: float = 0.0
    quality_after: float = 0.0
    quality_degradation: float = 0.0
    
    # Preservation Validation
    preservation_validation: List[ValidationResult] = field(default_factory=list)


@dataclass
class CrossModelAtomContent:
    """Content structure for cross-model atoms"""
    
    # Content Type
    content_type: str = "cross_model_insight"
    content_version: str = "1.0.0"
    
    # Insight Content
    problem_analysis: str = ""
    recommended_approach: str = ""
    key_considerations: List[str] = field(default_factory=list)
    potential_risks: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    
    # Context Information
    minimal_context_used: str = ""
    full_context_available: str = ""
    context_summary: str = ""
    
    # Model Outputs
    smart_model_output: str = ""
    execution_model_output: str = ""
    
    # Transfer Information
    transfer_metadata: Dict[str, Any] = field(default_factory=dict)
    transfer_validation: Dict[str, Any] = field(default_factory=dict)
    
    # Quality Information
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    quality_validation: Dict[str, Any] = field(default_factory=dict)
    
    # Cost Information
    cost_metrics: Dict[str, float] = field(default_factory=dict)
    cost_optimization: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content_type": self.content_type,
            "content_version": self.content_version,
            "problem_analysis": self.problem_analysis,
            "recommended_approach": self.recommended_approach,
            "key_considerations": self.key_considerations,
            "potential_risks": self.potential_risks,
            "success_criteria": self.success_criteria,
            "minimal_context_used": self.minimal_context_used,
            "full_context_available": self.full_context_available,
            "context_summary": self.context_summary,
            "smart_model_output": self.smart_model_output,
            "execution_model_output": self.execution_model_output,
            "transfer_metadata": self.transfer_metadata,
            "transfer_validation": self.transfer_validation,
            "quality_metrics": self.quality_metrics,
            "quality_validation": self.quality_validation,
            "cost_metrics": self.cost_metrics,
            "cost_optimization": self.cost_optimization
        }
    
    def calculate_hash(self) -> str:
        """Calculate hash of the content"""
        data = self.to_dict()
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


@dataclass
class CrossModelAtom:
    """Extended CMC atom schema for cross-model consciousness"""
    
    # Identity
    atom_id: str = field(default_factory=lambda: f"atom_{uuid.uuid4().hex}")
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    # Content
    content: CrossModelAtomContent = field(default_factory=CrossModelAtomContent)
    modality: str = "cross_model"
    
    # Cross-Model Information
    source_models: List[str] = field(default_factory=list)
    model_insights: List[ModelInsight] = field(default_factory=list)
    transfer_history: List[TransferRecord] = field(default_factory=list)
    
    # Insight Information
    insight_id: str = ""
    insight_quality: float = 0.0
    insight_confidence: float = 0.0
    
    # Knowledge Transfer
    knowledge_transfer: KnowledgeTransfer = field(default_factory=KnowledgeTransfer)
    transfer_quality: float = 0.0
    transfer_confidence: float = 0.0
    
    # Cross-Model Provenance
    cross_model_provenance: CrossModelProvenance = field(default_factory=CrossModelProvenance)
    model_interactions: List[ModelInteraction] = field(default_factory=list)
    
    # Cost & Performance
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Quality Assurance
    quality_preservation: QualityPreservation = field(default_factory=QualityPreservation)
    validation_results: List[ValidationResult] = field(default_factory=list)
    
    # Bitemporal (inherited from CMC)
    valid_from: datetime = field(default_factory=datetime.now)
    valid_to: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Quality
    quality_score: float = 0.0
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "atom_id": self.atom_id,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "content": self.content.to_dict(),
            "modality": self.modality,
            "source_models": self.source_models,
            "insight_id": self.insight_id,
            "insight_quality": self.insight_quality,
            "insight_confidence": self.insight_confidence,
            "transfer_quality": self.transfer_quality,
            "transfer_confidence": self.transfer_confidence,
            "cost_breakdown": self.cost_breakdown,
            "performance_metrics": self.performance_metrics,
            "valid_from": self.valid_from.isoformat(),
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "metadata": self.metadata,
            "quality_score": self.quality_score,
            "confidence": self.confidence
        }
    
    def calculate_hash(self) -> str:
        """Calculate hash of the atom"""
        data = self.to_dict()
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def validate(self) -> List[ValidationResult]:
        """Validate the cross-model atom"""
        validation_results = []
        
        # Validate required fields
        if not self.source_models:
            validation_results.append(ValidationResult(
                field="source_models",
                valid=False,
                message="Source models are required"
            ))
        
        if not self.insight_id:
            validation_results.append(ValidationResult(
                field="insight_id",
                valid=False,
                message="Insight ID is required"
            ))
        
        # Validate confidence scores
        if not 0.0 <= self.insight_confidence <= 1.0:
            validation_results.append(ValidationResult(
                field="insight_confidence",
                valid=False,
                message="Insight confidence must be between 0.0 and 1.0"
            ))
        
        if not 0.0 <= self.insight_quality <= 1.0:
            validation_results.append(ValidationResult(
                field="insight_quality",
                valid=False,
                message="Insight quality must be between 0.0 and 1.0"
            ))
        
        # Validate transfer confidence
        if not 0.0 <= self.transfer_confidence <= 1.0:
            validation_results.append(ValidationResult(
                field="transfer_confidence",
                valid=False,
                message="Transfer confidence must be between 0.0 and 1.0"
            ))
        
        # Validate quality score
        if not 0.0 <= self.quality_score <= 1.0:
            validation_results.append(ValidationResult(
                field="quality_score",
                valid=False,
                message="Quality score must be between 0.0 and 1.0"
            ))
        
        # Validate confidence
        if not 0.0 <= self.confidence <= 1.0:
            validation_results.append(ValidationResult(
                field="confidence",
                valid=False,
                message="Confidence must be between 0.0 and 1.0"
            ))
        
        return validation_results
    
    def to_cmc_atom(self) -> Atom:
        """Convert to CMC Atom for storage"""
        # Create AtomContent from CrossModelAtomContent
        atom_content = AtomContent(
            inline=json.dumps(self.content.to_dict())
        )
        
        # Create AtomCreate for the atom
        atom_create = AtomCreate(
            modality=self.modality,
            content=atom_content
        )
        
        # Create Atom with bitemporal information
        atom = Atom(
            atom_id=self.atom_id,
            timestamp=self.timestamp,
            version=self.version,
            content=atom_content,
            modality=self.modality,
            source="cross_model_consciousness",
            source_version="1.0.0",
            metadata={
                **self.metadata,
                "source_models": self.source_models,
                "insight_id": self.insight_id,
                "insight_quality": self.insight_quality,
                "insight_confidence": self.insight_confidence,
                "transfer_quality": self.transfer_quality,
                "transfer_confidence": self.transfer_confidence,
                "cost_breakdown": self.cost_breakdown,
                "performance_metrics": self.performance_metrics
            },
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            quality_score=self.quality_score,
            confidence=self.confidence
        )
        
        return atom
    
    @classmethod
    def from_cmc_atom(cls, atom: Atom) -> 'CrossModelAtom':
        """Create CrossModelAtom from CMC Atom"""
        # Extract metadata
        metadata = atom.metadata or {}
        
        # Create CrossModelAtomContent from inline content
        content_data = json.loads(atom.content.inline) if atom.content.inline else {}
        content = CrossModelAtomContent(**content_data)
        
        # Create CrossModelAtom
        cross_model_atom = cls(
            atom_id=atom.atom_id,
            timestamp=atom.timestamp,
            version=atom.version,
            content=content,
            modality=atom.modality,
            source_models=metadata.get("source_models", []),
            insight_id=metadata.get("insight_id", ""),
            insight_quality=metadata.get("insight_quality", 0.0),
            insight_confidence=metadata.get("insight_confidence", 0.0),
            transfer_quality=metadata.get("transfer_quality", 0.0),
            transfer_confidence=metadata.get("transfer_confidence", 0.0),
            cost_breakdown=metadata.get("cost_breakdown", {}),
            performance_metrics=metadata.get("performance_metrics", {}),
            valid_from=atom.valid_from,
            valid_to=atom.valid_to,
            metadata=metadata,
            quality_score=atom.quality_score,
            confidence=atom.confidence
        )
        
        return cross_model_atom

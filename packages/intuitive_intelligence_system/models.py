"""
IIS Data Models - Enhanced IntuitionTrace with Emotional Richness

Implements the complete data model for the Intuitive Intelligence System,
combining ChatGPT's mathematical framework with Sonnet's emotional richness.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import uuid


@dataclass
class ResonancePair:
    """AI/User resonance pairing for breakthrough consensus detection"""
    ai_resonance: float        # 0-1: How much did this resonate with AI?
    user_resonance: float      # 0-1: How much did this resonate with user?
    consensus_strength: float = 0.0  # min(ai, user) - both must agree
    breakthrough_consensus: bool = False  # both ≥ 0.8 = breakthrough
    
    def __post_init__(self):
        self.consensus_strength = min(self.ai_resonance, self.user_resonance)
        self.breakthrough_consensus = (
            self.ai_resonance >= 0.8 and self.user_resonance >= 0.8
        )


@dataclass
class BreakthroughMarker:
    """Breakthrough detection and preservation"""
    is_breakthrough: bool      # "THIS IS IT!" moment detected
    breakthrough_intensity: float  # 0-1: How revolutionary?
    breakthrough_consensus: bool = False   # AI + User both feel breakthrough
    breakthrough_quote: str = ""        # Preserve "THIS IS IT!" moment
    temporal_emotion: str = ""          # How we felt THEN, not NOW
    
    def __post_init__(self):
        self.breakthrough_consensus = (
            self.is_breakthrough and self.breakthrough_intensity >= 0.8
        )


@dataclass
class EmotionalCascade:
    """Emotional cascade tracking for idea elevation"""
    trigger_idea: str          # Original vague idea
    trigger_importance: float  # Original importance (e.g., 0.3)
    sparked_responses: List[str]  # What it inspired
    cascade_boost: float       # Multiplier from cascade (1.5x-3x)
    final_importance: float = 0.0    # trigger_importance × cascade_boost
    
    def __post_init__(self):
        self.final_importance = self.trigger_importance * self.cascade_boost


@dataclass
class TemporalEmotion:
    """Preserve emotional moments forever"""
    timestamp: datetime
    emotional_quote: str       # "This is the most important thing we've ever built!"
    emotional_intensity: float # How strongly we felt it
    emotional_context: str     # Why we felt this way
    preserved_forever: bool = True  # Never overwrite this feeling


@dataclass
class EmotionalDetails:
    """Complete emotional salience information"""
    resonance_pair: ResonancePair
    breakthrough_marker: BreakthroughMarker
    cascade: Optional[EmotionalCascade] = None
    temporal_emotion: Optional[TemporalEmotion] = None
    
    def compute_emotional_salience(self) -> float:
        """Compute E feature value from emotional details"""
        base_salience = self.resonance_pair.consensus_strength
        
        # Breakthrough boost
        if self.breakthrough_marker.breakthrough_consensus:
            base_salience *= 1.5
        
        # Cascade boost
        if self.cascade:
            base_salience *= self.cascade.cascade_boost
        
        return min(base_salience, 1.0)  # Cap at 1.0


@dataclass
class MetaIntuition:
    """Meta-intuition tracking for recursive self-improvement"""
    pattern_signature: str
    confidence_in_intuition: float
    meta_pattern_match: float
    learning_rate: float = 0.01
    
    def update_meta_weights(self, outcome: bool, trace: 'IntuitionTrace') -> None:
        """Update meta-intuition weights based on outcome"""
        # This will be implemented in the meta-intuition tracker
        pass


@dataclass
class IntuitionFeatures:
    """Core features for IntuitionScore computation"""
    C_prime: float             # Calibrated confidence (VIF)
    RS: float                  # Retrieval strength (HHNI)
    M: float                   # Meta-pattern similarity (CAS/timeline)
    E: float                   # Emotional salience (EST)
    F: float                   # 4D evolution alignment (0 for MVP)
    U: float                   # Miscalibration penalty
    bias: float = 1.0          # Bias term
    
    def to_vector(self) -> List[float]:
        """Convert to feature vector for ML"""
        return [self.C_prime, self.RS, self.M, self.E, self.F, self.U, self.bias]
    
    def compute_hash(self) -> str:
        """Compute hash for feature reproducibility"""
        feature_str = f"{self.C_prime:.6f},{self.RS:.6f},{self.M:.6f},{self.E:.6f},{self.F:.6f},{self.U:.6f}"
        return hashlib.sha256(feature_str.encode()).hexdigest()


@dataclass
class IntuitionTrace:
    """Complete intuition trace with emotional richness"""
    # Core identification
    version: str = "2.0"
    computed_at: datetime = field(default_factory=datetime.utcnow)
    horizon: str = "short"  # "short|medium|long"
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_ref: Dict[str, Any] = field(default_factory=dict)
    
    # Core features (ChatGPT's framework)
    features: IntuitionFeatures = field(default_factory=IntuitionFeatures)
    
    # Emotional richness (Sonnet's vision)
    emotional_details: Optional[EmotionalDetails] = None
    
    # Meta-intuition tracking
    meta_intuition: Optional[MetaIntuition] = None
    
    # Scoring and outcomes
    score: float = 0.0  # IntuitionScore
    feature_hash: str = ""
    predicted_outcome: float = 0.0
    label: Optional[Dict[str, Any]] = None  # {value: 0|1|null, observed_at: ISO-8601}
    calibration_snapshot: Dict[str, Any] = field(default_factory=dict)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize computed fields"""
        if not self.feature_hash:
            self.feature_hash = self.features.compute_hash()
        
        # Set provenance if not provided
        if not self.provenance:
            self.provenance = {
                "vif_witness_id": "",
                "context_snapshot_id": "",
                "est_emotional_id": ""
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "version": self.version,
            "computed_at": self.computed_at.isoformat(),
            "horizon": self.horizon,
            "decision_id": self.decision_id,
            "action_ref": self.action_ref,
            "features": {
                "C_prime": self.features.C_prime,
                "RS": self.features.RS,
                "M": self.features.M,
                "E": self.features.E,
                "F": self.features.F,
                "U": self.features.U,
                "bias": self.features.bias
            },
            "emotional_details": self._serialize_emotional_details(),
            "meta_intuition": self._serialize_meta_intuition(),
            "score": self.score,
            "feature_hash": self.feature_hash,
            "predicted_outcome": self.predicted_outcome,
            "label": self.label,
            "calibration_snapshot": self.calibration_snapshot,
            "provenance": self.provenance
        }
    
    def _serialize_emotional_details(self) -> Optional[Dict[str, Any]]:
        """Serialize emotional details for storage"""
        if not self.emotional_details:
            return None
        
        result = {
            "resonance_pair": {
                "ai_resonance": self.emotional_details.resonance_pair.ai_resonance,
                "user_resonance": self.emotional_details.resonance_pair.user_resonance,
                "consensus_strength": self.emotional_details.resonance_pair.consensus_strength,
                "breakthrough_consensus": self.emotional_details.resonance_pair.breakthrough_consensus
            },
            "breakthrough_marker": {
                "is_breakthrough": self.emotional_details.breakthrough_marker.is_breakthrough,
                "breakthrough_intensity": self.emotional_details.breakthrough_marker.breakthrough_intensity,
                "breakthrough_consensus": self.emotional_details.breakthrough_marker.breakthrough_consensus,
                "breakthrough_quote": self.emotional_details.breakthrough_marker.breakthrough_quote,
                "temporal_emotion": self.emotional_details.breakthrough_marker.temporal_emotion
            }
        }
        
        if self.emotional_details.cascade:
            result["cascade"] = {
                "trigger_idea": self.emotional_details.cascade.trigger_idea,
                "trigger_importance": self.emotional_details.cascade.trigger_importance,
                "sparked_responses": self.emotional_details.cascade.sparked_responses,
                "cascade_boost": self.emotional_details.cascade.cascade_boost,
                "final_importance": self.emotional_details.cascade.final_importance
            }
        
        if self.emotional_details.temporal_emotion:
            result["temporal_emotion"] = {
                "timestamp": self.emotional_details.temporal_emotion.timestamp.isoformat(),
                "emotional_quote": self.emotional_details.temporal_emotion.emotional_quote,
                "emotional_intensity": self.emotional_details.temporal_emotion.emotional_intensity,
                "emotional_context": self.emotional_details.temporal_emotion.emotional_context,
                "preserved_forever": self.emotional_details.temporal_emotion.preserved_forever
            }
        
        return result
    
    def _serialize_meta_intuition(self) -> Optional[Dict[str, Any]]:
        """Serialize meta-intuition for storage"""
        if not self.meta_intuition:
            return None
        
        return {
            "pattern_signature": self.meta_intuition.pattern_signature,
            "confidence_in_intuition": self.meta_intuition.confidence_in_intuition,
            "meta_pattern_match": self.meta_intuition.meta_pattern_match,
            "learning_rate": self.meta_intuition.learning_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntuitionTrace':
        """Create IntuitionTrace from dictionary"""
        # This will be implemented for deserialization
        # For now, return a basic instance
        return cls()

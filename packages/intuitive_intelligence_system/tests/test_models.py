"""
Tests for IIS data models
"""

import pytest
from datetime import datetime
from ..models import (
    ResonancePair, BreakthroughMarker, EmotionalCascade, TemporalEmotion,
    EmotionalDetails, IntuitionFeatures, IntuitionTrace
)


class TestResonancePair:
    """Test ResonancePair model"""
    
    def test_consensus_strength_calculation(self):
        """Test consensus strength is minimum of AI and user resonance"""
        pair = ResonancePair(ai_resonance=0.8, user_resonance=0.6)
        assert pair.consensus_strength == 0.6
        
        pair = ResonancePair(ai_resonance=0.4, user_resonance=0.9)
        assert pair.consensus_strength == 0.4
    
    def test_breakthrough_consensus_detection(self):
        """Test breakthrough consensus detection"""
        # Both high - should be breakthrough
        pair = ResonancePair(ai_resonance=0.9, user_resonance=0.8)
        assert pair.breakthrough_consensus is True
        
        # One high, one low - should not be breakthrough
        pair = ResonancePair(ai_resonance=0.9, user_resonance=0.7)
        assert pair.breakthrough_consensus is False
        
        # Both low - should not be breakthrough
        pair = ResonancePair(ai_resonance=0.6, user_resonance=0.5)
        assert pair.breakthrough_consensus is False


class TestBreakthroughMarker:
    """Test BreakthroughMarker model"""
    
    def test_breakthrough_consensus_calculation(self):
        """Test breakthrough consensus calculation"""
        marker = BreakthroughMarker(
            is_breakthrough=True,
            breakthrough_intensity=0.9,
            breakthrough_consensus=False,  # Will be recalculated
            breakthrough_quote="This is it!",
            temporal_emotion="Profound breakthrough"
        )
        assert marker.breakthrough_consensus is True
        
        marker = BreakthroughMarker(
            is_breakthrough=True,
            breakthrough_intensity=0.7,
            breakthrough_consensus=False,
            breakthrough_quote="Interesting",
            temporal_emotion="Moderate response"
        )
        assert marker.breakthrough_consensus is False


class TestEmotionalCascade:
    """Test EmotionalCascade model"""
    
    def test_final_importance_calculation(self):
        """Test final importance calculation"""
        cascade = EmotionalCascade(
            trigger_idea="Vague idea",
            trigger_importance=0.3,
            sparked_responses=["Inspired response 1", "Inspired response 2"],
            cascade_boost=2.0
        )
        assert cascade.final_importance == 0.6  # 0.3 * 2.0


class TestEmotionalDetails:
    """Test EmotionalDetails model"""
    
    def test_emotional_salience_computation(self):
        """Test emotional salience computation"""
        resonance_pair = ResonancePair(ai_resonance=0.8, user_resonance=0.7)
        breakthrough_marker = BreakthroughMarker(
            is_breakthrough=True,
            breakthrough_intensity=0.9,
            breakthrough_consensus=True,
            breakthrough_quote="This is it!",
            temporal_emotion="Profound breakthrough"
        )
        
        details = EmotionalDetails(
            resonance_pair=resonance_pair,
            breakthrough_marker=breakthrough_marker
        )
        
        # Base salience = min(0.8, 0.7) = 0.7
        # Breakthrough boost = 1.5
        # Expected = 0.7 * 1.5 = 1.05, capped at 1.0
        assert details.compute_emotional_salience() == 1.0
    
    def test_emotional_salience_with_cascade(self):
        """Test emotional salience with cascade boost"""
        resonance_pair = ResonancePair(ai_resonance=0.6, user_resonance=0.5)
        breakthrough_marker = BreakthroughMarker(
            is_breakthrough=False,
            breakthrough_intensity=0.4,
            breakthrough_consensus=False,
            breakthrough_quote="Interesting",
            temporal_emotion="Moderate response"
        )
        cascade = EmotionalCascade(
            trigger_idea="Test idea",
            trigger_importance=0.4,
            sparked_responses=["Response"],
            cascade_boost=2.5
        )
        
        details = EmotionalDetails(
            resonance_pair=resonance_pair,
            breakthrough_marker=breakthrough_marker,
            cascade=cascade
        )
        
        # Base salience = min(0.6, 0.5) = 0.5
        # No breakthrough boost
        # Cascade boost = 2.5
        # Expected = 0.5 * 2.5 = 1.25, capped at 1.0
        assert details.compute_emotional_salience() == 1.0


class TestIntuitionFeatures:
    """Test IntuitionFeatures model"""
    
    def test_feature_vector_conversion(self):
        """Test conversion to feature vector"""
        features = IntuitionFeatures(
            C_prime=0.8,
            RS=0.7,
            M=0.6,
            E=0.9,
            F=0.0,  # MVP
            U=0.1
        )
        
        vector = features.to_vector()
        expected = [0.8, 0.7, 0.6, 0.9, 0.0, 0.1, 1.0]
        assert vector == expected
    
    def test_feature_hash_computation(self):
        """Test feature hash computation"""
        features1 = IntuitionFeatures(C_prime=0.8, RS=0.7, M=0.6, E=0.9, F=0.0, U=0.1)
        features2 = IntuitionFeatures(C_prime=0.8, RS=0.7, M=0.6, E=0.9, F=0.0, U=0.1)
        features3 = IntuitionFeatures(C_prime=0.9, RS=0.7, M=0.6, E=0.9, F=0.0, U=0.1)
        
        # Same features should have same hash
        assert features1.compute_hash() == features2.compute_hash()
        
        # Different features should have different hash
        assert features1.compute_hash() != features3.compute_hash()


class TestIntuitionTrace:
    """Test IntuitionTrace model"""
    
    def test_trace_initialization(self):
        """Test trace initialization"""
        features = IntuitionFeatures(C_prime=0.8, RS=0.7, M=0.6, E=0.9, F=0.0, U=0.1)
        trace = IntuitionTrace(features=features, score=0.85)
        
        assert trace.version == "2.0"
        assert trace.score == 0.85
        assert trace.features == features
        assert trace.feature_hash == features.compute_hash()
        assert trace.provenance["vif_witness_id"] == ""
    
    def test_trace_serialization(self):
        """Test trace serialization to dict"""
        features = IntuitionFeatures(C_prime=0.8, RS=0.7, M=0.6, E=0.9, F=0.0, U=0.1)
        trace = IntuitionTrace(features=features, score=0.85)
        
        data = trace.to_dict()
        
        assert data["version"] == "2.0"
        assert data["score"] == 0.85
        assert data["features"]["C_prime"] == 0.8
        assert data["features"]["E"] == 0.9
        assert data["feature_hash"] == features.compute_hash()
    
    def test_trace_with_emotional_details(self):
        """Test trace with emotional details"""
        features = IntuitionFeatures(C_prime=0.8, RS=0.7, M=0.6, E=0.9, F=0.0, U=0.1)
        
        resonance_pair = ResonancePair(ai_resonance=0.8, user_resonance=0.7)
        breakthrough_marker = BreakthroughMarker(
            is_breakthrough=True,
            breakthrough_intensity=0.9,
            breakthrough_consensus=True,
            breakthrough_quote="This is it!",
            temporal_emotion="Profound breakthrough"
        )
        emotional_details = EmotionalDetails(
            resonance_pair=resonance_pair,
            breakthrough_marker=breakthrough_marker
        )
        
        trace = IntuitionTrace(
            features=features,
            emotional_details=emotional_details,
            score=0.95
        )
        
        data = trace.to_dict()
        
        assert data["emotional_details"] is not None
        assert data["emotional_details"]["resonance_pair"]["ai_resonance"] == 0.8
        assert data["emotional_details"]["breakthrough_marker"]["breakthrough_quote"] == "This is it!"

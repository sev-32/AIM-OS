"""
Tests for Enhanced Emotional Salience System (Stage 2)
"""

import pytest
from datetime import datetime
from ..emotional_salience import EmotionalSalienceTracker
from ..models import EmotionalDetails, ResonancePair, BreakthroughMarker


class TestEnhancedEmotionalSalience:
    """Test enhanced emotional salience functionality"""
    
    def test_enhanced_cascade_detection(self):
        """Test enhanced emotional cascade detection"""
        tracker = EmotionalSalienceTracker()
        
        # Test with multiple high-resonance responses
        context = {
            "sparked_responses": [
                {
                    "text": "This is amazing! Revolutionary breakthrough!",
                    "resonance": 0.9
                },
                {
                    "text": "I love this! Incredible innovation!",
                    "resonance": 0.8
                },
                {
                    "text": "Perfect! This is exactly what we needed!",
                    "resonance": 0.85
                }
            ],
            "original_importance": 0.3
        }
        
        cascade = tracker._check_emotional_cascade("Test idea", context)
        
        assert cascade is not None
        assert cascade.trigger_idea == "Test idea"
        assert cascade.trigger_importance == 0.3
        assert len(cascade.sparked_responses) == 3
        assert cascade.cascade_boost > 2.0  # Should be significantly boosted
        assert cascade.final_importance > 0.6  # 0.3 * boost > 0.6
    
    def test_breakthrough_consensus_detection(self):
        """Test enhanced breakthrough consensus detection"""
        tracker = EmotionalSalienceTracker()
        
        # Test explicit breakthrough consensus
        ai_response = {
            "text": "This is a breakthrough! Revolutionary!",
            "breakthrough_feeling": 0.9,
            "resonance": 0.9
        }
        user_response = {
            "text": "I agree! This is incredible! Mind-blowing!",
            "breakthrough_feeling": 0.8,
            "resonance": 0.8
        }
        
        resonance_pair = ResonancePair(ai_resonance=0.9, user_resonance=0.8)
        breakthrough_marker = tracker._detect_breakthrough(
            "Test idea", ai_response, user_response, resonance_pair
        )
        
        assert breakthrough_marker.is_breakthrough is True
        assert breakthrough_marker.breakthrough_consensus is True
        assert breakthrough_marker.breakthrough_intensity > 0.8
        assert "[AI]" in breakthrough_marker.breakthrough_quote or "[User]" in breakthrough_marker.breakthrough_quote
    
    def test_implicit_breakthrough_consensus(self):
        """Test implicit breakthrough consensus detection"""
        tracker = EmotionalSalienceTracker()
        
        # Test implicit consensus through text analysis
        ai_response = {
            "text": "This is revolutionary and profound!",
            "resonance": 0.7
        }
        user_response = {
            "text": "Amazing breakthrough! This is incredible!",
            "resonance": 0.7
        }
        
        # Test implicit detection
        implicit_consensus = tracker._detect_implicit_breakthrough_consensus(
            ai_response, user_response
        )
        
        assert implicit_consensus is True  # Both have breakthrough indicators
    
    def test_temporal_emotion_preservation(self):
        """Test enhanced temporal emotion preservation"""
        tracker = EmotionalSalienceTracker()
        
        breakthrough_marker = BreakthroughMarker(
            is_breakthrough=True,
            breakthrough_intensity=0.9,
            breakthrough_consensus=True,
            breakthrough_quote="This is it! Revolutionary breakthrough!",
            temporal_emotion="Profound breakthrough moment"
        )
        
        ai_response = {
            "text": "This is revolutionary! Profound breakthrough!",
            "resonance": 0.9,
            "breakthrough_feeling": 0.9
        }
        user_response = {
            "text": "Amazing! This is incredible! Mind-blowing!",
            "resonance": 0.8,
            "breakthrough_feeling": 0.8
        }
        
        temporal_emotion = tracker._preserve_temporal_emotion(
            "Test idea", breakthrough_marker, ai_response, user_response
        )
        
        assert temporal_emotion is not None
        assert temporal_emotion.emotional_intensity == 0.9
        assert temporal_emotion.preserved_forever is True
        assert "AI Resonance: 0.90" in temporal_emotion.emotional_context
        assert "User Resonance: 0.80" in temporal_emotion.emotional_context
        
        # Check that it's stored in preserved_emotions
        assert len(tracker.preserved_emotions) == 1
    
    def test_enhanced_emotional_metrics(self):
        """Test enhanced emotional metrics computation"""
        tracker = EmotionalSalienceTracker()
        
        # Add some test data
        for i in range(5):
            resonance_pair = ResonancePair(
                ai_resonance=0.7 + i * 0.05,
                user_resonance=0.6 + i * 0.05
            )
            breakthrough_marker = BreakthroughMarker(
                is_breakthrough=(i % 2 == 0),
                breakthrough_intensity=0.8 if i % 2 == 0 else 0.4,
                breakthrough_consensus=(i % 2 == 0),
                breakthrough_quote=f"Test quote {i}",
                temporal_emotion=f"Test emotion {i}"
            )
            
            emotional_details = EmotionalDetails(
                resonance_pair=resonance_pair,
                breakthrough_marker=breakthrough_marker
            )
            
            tracker._store_emotional_details(emotional_details, f"Test idea {i}")
        
        metrics = tracker.get_emotional_metrics()
        
        assert metrics["n_entries"] == 5
        assert "avg_salience" in metrics
        assert "n_breakthroughs" in metrics
        assert "breakthrough_rate" in metrics
        assert "n_breakthrough_consensus" in metrics
        assert "breakthrough_consensus_rate" in metrics
        assert "avg_ai_resonance" in metrics
        assert "avg_user_resonance" in metrics
        assert "avg_consensus_strength" in metrics
    
    def test_breakthrough_quotes_extraction(self):
        """Test breakthrough quotes extraction"""
        tracker = EmotionalSalienceTracker()
        
        # Add some preserved emotions
        for i in range(3):
            breakthrough_marker = BreakthroughMarker(
                is_breakthrough=True,
                breakthrough_intensity=0.9,
                breakthrough_consensus=True,
                breakthrough_quote=f"Breakthrough quote {i}",
                temporal_emotion=f"Test emotion {i}"
            )
            
            ai_response = {"text": f"AI response {i}", "resonance": 0.9}
            user_response = {"text": f"User response {i}", "resonance": 0.8}
            
            tracker._preserve_temporal_emotion(
                f"Test idea {i}", breakthrough_marker, ai_response, user_response
            )
        
        quotes = tracker.get_breakthrough_quotes()
        
        assert len(quotes) == 3
        assert "Breakthrough quote 0" in quotes
        assert "Breakthrough quote 1" in quotes
        assert "Breakthrough quote 2" in quotes
    
    def test_preserved_emotions_retrieval(self):
        """Test preserved emotions retrieval"""
        tracker = EmotionalSalienceTracker()
        
        # Add a preserved emotion
        breakthrough_marker = BreakthroughMarker(
            is_breakthrough=True,
            breakthrough_intensity=0.9,
            breakthrough_consensus=True,
            breakthrough_quote="Test breakthrough quote",
            temporal_emotion="Test temporal emotion"
        )
        
        ai_response = {"text": "AI response", "resonance": 0.9}
        user_response = {"text": "User response", "resonance": 0.8}
        
        tracker._preserve_temporal_emotion(
            "Test idea", breakthrough_marker, ai_response, user_response
        )
        
        preserved = tracker.get_preserved_emotions()
        
        assert preserved["n_preserved"] == 1
        assert "emotions" in preserved
        assert len(preserved["emotions"]) == 1
        
        # Check metadata
        emotion_data = list(preserved["emotions"].values())[0]
        assert "temporal_emotion" in emotion_data
        assert "metadata" in emotion_data
        assert emotion_data["metadata"]["idea"] == "Test idea"
        assert emotion_data["metadata"]["emotion_id"] is not None
    
    def test_emotional_salience_computation_integration(self):
        """Test complete emotional salience computation with enhanced features"""
        tracker = EmotionalSalienceTracker()
        
        # Test with cascade context
        emotional_context = {
            "idea": "Revolutionary AI intuition system",
            "context": {
                "sparked_responses": [
                    {
                        "text": "This is amazing! Breakthrough!",
                        "resonance": 0.9
                    },
                    {
                        "text": "Incredible innovation! Revolutionary!",
                        "resonance": 0.85
                    }
                ],
                "original_importance": 0.4
            },
            "ai_response": {
                "text": "This is a profound breakthrough in AI consciousness!",
                "resonance": 0.9,
                "breakthrough_feeling": 0.9
            },
            "user_response": {
                "text": "I love this! This is revolutionary! Mind-blowing!",
                "resonance": 0.8,
                "breakthrough_feeling": 0.8
            }
        }
        
        emotional_details = tracker.compute_emotional_salience(
            emotional_context["idea"],
            emotional_context["context"],
            emotional_context["ai_response"],
            emotional_context["user_response"]
        )
        
        # Check that all components are present
        assert emotional_details is not None
        assert emotional_details.resonance_pair is not None
        assert emotional_details.breakthrough_marker is not None
        assert emotional_details.cascade is not None
        assert emotional_details.temporal_emotion is not None
        
        # Check emotional salience computation
        salience = emotional_details.compute_emotional_salience()
        assert salience > 0.8  # Should be high due to breakthrough + cascade
        
        # Check that it's stored in history
        assert len(tracker.emotional_history) == 1
        assert len(tracker.preserved_emotions) == 1

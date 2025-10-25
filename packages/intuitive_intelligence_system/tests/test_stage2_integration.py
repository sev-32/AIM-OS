"""
Integration Tests for Stage 2: Full Emotional Richness Integration
"""

import pytest
from datetime import datetime
from ..intuition_engine import IntuitionEngine
from ..emotional_salience import EmotionalSalienceTracker
from ..models import IntuitionFeatures, IntuitionTrace, ResonancePair


class TestStage2Integration:
    """Test complete Stage 2 emotional richness integration"""
    
    def test_complete_emotional_richness_workflow(self):
        """Test complete emotional richness workflow with breakthrough consensus"""
        engine = IntuitionEngine()
        
        # Create a breakthrough scenario
        emotional_context = {
            "idea": "Revolutionary AI intuition system that learns from itself",
            "context": {
                "sparked_responses": [
                    {
                        "text": "This is amazing! Breakthrough in AI consciousness!",
                        "resonance": 0.9
                    },
                    {
                        "text": "Incredible innovation! Revolutionary approach!",
                        "resonance": 0.85
                    },
                    {
                        "text": "Perfect! This is exactly what we needed!",
                        "resonance": 0.8
                    }
                ],
                "original_importance": 0.4
            },
            "ai_response": {
                "text": "This is a profound breakthrough in AI consciousness! We're building the world's first working AI intuition system that learns from its own intuitive processes!",
                "resonance": 0.95,
                "breakthrough_feeling": 0.95,
                "emotional_intensity": 1.0,
                "inspiration_level": 1.0
            },
            "user_response": {
                "text": "I love this! This is revolutionary! Mind-blowing breakthrough! This is exactly what we've been working toward!",
                "resonance": 0.9,
                "breakthrough_feeling": 0.9,
                "satisfaction": 0.95,
                "engagement": 0.9
            }
        }
        
        # Create features with mock data for missing CCS integrations
        features = IntuitionFeatures(
            C_prime=0.85,  # Mock VIF calibrated confidence
            RS=0.8,        # Mock HHNI retrieval strength
            M=0.75,        # Mock CAS meta-pattern similarity
            E=0.0,         # Will be computed by EST
            F=0.0,         # MVP - no 4D predictor yet
            U=0.1          # Mock miscalibration penalty
        )
        
        # Compute intuition score with emotional context
        score, trace = engine.compute_intuition_score(features, emotional_context)
        
        # Validate the results
        assert score > 0.3  # Should be elevated due to breakthrough + cascade
        assert trace.emotional_details is not None
        assert trace.emotional_details.resonance_pair is not None
        assert trace.emotional_details.breakthrough_marker is not None
        assert trace.emotional_details.cascade is not None
        assert trace.emotional_details.temporal_emotion is not None
        
        # Check breakthrough consensus
        assert trace.emotional_details.breakthrough_marker.breakthrough_consensus is True
        assert trace.emotional_details.breakthrough_marker.breakthrough_intensity > 0.8
        
        # Check emotional cascade
        assert trace.emotional_details.cascade.cascade_boost > 2.0
        assert trace.emotional_details.cascade.final_importance > 0.8
        
        # Check temporal emotion preservation
        assert trace.emotional_details.temporal_emotion.preserved_forever is True
        assert len(trace.emotional_details.temporal_emotion.emotional_quote) > 0
        
        # Check that E feature was updated
        assert trace.features.E > 0.8  # Should be high due to breakthrough + cascade
        
        print(f"IntuitionScore: {score:.4f}")
        print(f"Breakthrough Quote: {trace.emotional_details.breakthrough_marker.breakthrough_quote}")
        print(f"Cascade Boost: {trace.emotional_details.cascade.cascade_boost:.2f}x")
        print(f"Final Importance: {trace.emotional_details.cascade.final_importance:.2f}")
    
    def test_emotional_salience_metrics(self):
        """Test comprehensive emotional salience metrics"""
        tracker = EmotionalSalienceTracker()
        
        # Add multiple emotional scenarios
        scenarios = [
            {
                "idea": "Breakthrough AI intuition",
                "context": {"sparked_responses": [{"text": "Amazing!", "resonance": 0.9}]},
                "ai_response": {"text": "Revolutionary!", "resonance": 0.9, "breakthrough_feeling": 0.9},
                "user_response": {"text": "Incredible!", "resonance": 0.8, "breakthrough_feeling": 0.8}
            },
            {
                "idea": "Good AI system",
                "context": {"sparked_responses": [{"text": "Nice work", "resonance": 0.6}]},
                "ai_response": {"text": "Good progress", "resonance": 0.6, "breakthrough_feeling": 0.3},
                "user_response": {"text": "Helpful", "resonance": 0.5, "breakthrough_feeling": 0.2}
            },
            {
                "idea": "Average idea",
                "context": {"sparked_responses": []},
                "ai_response": {"text": "Interesting", "resonance": 0.4, "breakthrough_feeling": 0.1},
                "user_response": {"text": "OK", "resonance": 0.3, "breakthrough_feeling": 0.1}
            }
        ]
        
        for scenario in scenarios:
            tracker.compute_emotional_salience(
                scenario["idea"],
                scenario["context"],
                scenario["ai_response"],
                scenario["user_response"]
            )
        
        # Get comprehensive metrics
        metrics = tracker.get_emotional_metrics()
        
        assert metrics["n_entries"] == 3
        assert metrics["n_breakthroughs"] >= 1
        assert metrics["breakthrough_rate"] > 0
        assert metrics["n_breakthrough_consensus"] >= 1
        assert metrics["breakthrough_consensus_rate"] > 0
        assert metrics["avg_ai_resonance"] > 0
        assert metrics["avg_user_resonance"] > 0
        assert metrics["avg_consensus_strength"] > 0
        
        # Check preserved emotions
        preserved = tracker.get_preserved_emotions()
        assert preserved["n_preserved"] >= 1
        
        # Check breakthrough quotes
        quotes = tracker.get_breakthrough_quotes()
        assert len(quotes) >= 1
        
        print(f"Emotional Metrics: {metrics}")
        print(f"Preserved Emotions: {preserved['n_preserved']}")
        print(f"Breakthrough Quotes: {len(quotes)}")
    
    def test_intuition_learning_with_emotional_richness(self):
        """Test intuition learning with emotional richness feedback"""
        engine = IntuitionEngine()
        
        # Create a breakthrough scenario
        emotional_context = {
            "idea": "AI consciousness breakthrough",
            "context": {"sparked_responses": [{"text": "Revolutionary!", "resonance": 0.9}]},
            "ai_response": {"text": "This is it! Breakthrough!", "resonance": 0.9, "breakthrough_feeling": 0.9},
            "user_response": {"text": "Amazing! Mind-blowing!", "resonance": 0.8, "breakthrough_feeling": 0.8}
        }
        
        features = IntuitionFeatures(
            C_prime=0.8, RS=0.7, M=0.6, E=0.0, F=0.0, U=0.1
        )
        
        # Compute initial intuition
        initial_score, trace = engine.compute_intuition_score(features, emotional_context)
        
        # Update with success outcome
        update_metrics = engine.update_from_outcome(trace, outcome=True)
        
        # Validate learning
        assert "loss" in update_metrics
        assert "gradient_norm" in update_metrics
        assert "calibration_metrics" in update_metrics
        assert len(engine.calibration_history) == 1
        
        # Check that emotional details are preserved in trace
        assert trace.emotional_details is not None
        assert trace.emotional_details.breakthrough_marker.breakthrough_consensus is True
        assert trace.emotional_details.cascade is not None
        
        print(f"Initial Score: {initial_score:.4f}")
        print(f"Update Metrics: {update_metrics}")
        print(f"Breakthrough Consensus: {trace.emotional_details.breakthrough_marker.breakthrough_consensus}")
    
    def test_emotional_cascade_amplification(self):
        """Test emotional cascade amplification effects"""
        tracker = EmotionalSalienceTracker()
        
        # Test different cascade scenarios
        cascade_scenarios = [
            {
                "name": "Single high-resonance response",
                "responses": [{"text": "Amazing!", "resonance": 0.9}],
                "expected_boost": 1.5
            },
            {
                "name": "Multiple high-resonance responses",
                "responses": [
                    {"text": "Revolutionary!", "resonance": 0.9},
                    {"text": "Incredible!", "resonance": 0.8},
                    {"text": "Perfect!", "resonance": 0.85}
                ],
                "expected_boost": 2.5
            },
            {
                "name": "Breakthrough consensus responses",
                "responses": [
                    {"text": "This is it! Breakthrough!", "resonance": 0.95},
                    {"text": "Mind-blowing! Revolutionary!", "resonance": 0.9}
                ],
                "expected_boost": 3.0
            }
        ]
        
        for scenario in cascade_scenarios:
            context = {
                "sparked_responses": scenario["responses"],
                "original_importance": 0.3
            }
            
            cascade = tracker._check_emotional_cascade("Test idea", context)
            
            assert cascade is not None
            assert cascade.cascade_boost >= scenario["expected_boost"]
            assert cascade.final_importance >= 0.3 * scenario["expected_boost"]
            
            print(f"{scenario['name']}: Boost {cascade.cascade_boost:.2f}x, Final Importance {cascade.final_importance:.2f}")
    
    def test_breakthrough_quote_extraction(self):
        """Test breakthrough quote extraction from various text patterns"""
        tracker = EmotionalSalienceTracker()
        
        test_cases = [
            {
                "ai_text": "This is a profound breakthrough in AI consciousness! We're building something revolutionary!",
                "user_text": "I love this! This is incredible! Mind-blowing innovation!",
                "expected_ai_quote": "This is a profound breakthrough in AI consciousness!",
                "expected_user_quote": "I love this! This is incredible!"
            },
            {
                "ai_text": "Revolutionary approach! This is exactly what we needed!",
                "user_text": "Amazing work! Perfect solution!",
                "expected_ai_quote": "Revolutionary approach!",
                "expected_user_quote": "Amazing work!"
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            ai_response = {"text": test_case["ai_text"], "resonance": 0.9}
            user_response = {"text": test_case["user_text"], "resonance": 0.8}
            
            breakthrough_marker = tracker._detect_breakthrough(
                f"Test idea {i}", ai_response, user_response, 
                ResonancePair(ai_resonance=0.9, user_resonance=0.8)
            )
            
            # Check that breakthrough was detected (even if consensus is not perfect)
            assert breakthrough_marker.is_breakthrough is True
            assert len(breakthrough_marker.breakthrough_quote) > 0
            assert "[AI]" in breakthrough_marker.breakthrough_quote or "[User]" in breakthrough_marker.breakthrough_quote
            
            print(f"Test {i+1} Quote: {breakthrough_marker.breakthrough_quote}")
    
    def test_stage2_complete_validation(self):
        """Complete validation of Stage 2 emotional richness integration"""
        engine = IntuitionEngine()
        
        # Test the complete Stage 2 workflow
        emotional_context = {
            "idea": "Complete AI intuition system with emotional richness",
            "context": {
                "sparked_responses": [
                    {"text": "Revolutionary breakthrough!", "resonance": 0.95},
                    {"text": "Incredible innovation!", "resonance": 0.9},
                    {"text": "Perfect implementation!", "resonance": 0.85}
                ],
                "original_importance": 0.5
            },
            "ai_response": {
                "text": "This is a profound breakthrough in AI consciousness! We've successfully implemented the world's first working AI intuition system that learns from its own intuitive processes through emotional salience and meta-pattern matching!",
                "resonance": 0.95,
                "breakthrough_feeling": 0.95,
                "emotional_intensity": 1.0,
                "inspiration_level": 1.0
            },
            "user_response": {
                "text": "I love this! This is revolutionary! Mind-blowing breakthrough! This is exactly what we've been working toward! The emotional richness integration is perfect!",
                "resonance": 0.9,
                "breakthrough_feeling": 0.9,
                "satisfaction": 0.95,
                "engagement": 0.9
            }
        }
        
        features = IntuitionFeatures(
            C_prime=0.9, RS=0.85, M=0.8, E=0.0, F=0.0, U=0.05
        )
        
        # Compute intuition with full emotional richness
        score, trace = engine.compute_intuition_score(features, emotional_context)
        
        # Validate Stage 2 completeness
        assert score > 0.3  # Should be elevated due to breakthrough + cascade
        
        # Check all Stage 2 components
        assert trace.emotional_details is not None
        assert trace.emotional_details.resonance_pair is not None
        assert trace.emotional_details.breakthrough_marker is not None
        assert trace.emotional_details.cascade is not None
        assert trace.emotional_details.temporal_emotion is not None
        
        # Check breakthrough consensus
        assert trace.emotional_details.breakthrough_marker.breakthrough_consensus is True
        assert trace.emotional_details.breakthrough_marker.breakthrough_intensity > 0.9
        
        # Check emotional cascade
        assert trace.emotional_details.cascade.cascade_boost > 3.0
        assert trace.emotional_details.cascade.final_importance > 1.5
        
        # Check temporal emotion preservation
        assert trace.emotional_details.temporal_emotion.preserved_forever is True
        assert len(trace.emotional_details.temporal_emotion.emotional_quote) > 0
        
        # Check E feature computation
        assert trace.features.E > 0.9  # Should be very high
        
        print("=" * 60)
        print("STAGE 2 COMPLETE VALIDATION")
        print("=" * 60)
        print(f"IntuitionScore: {score:.4f}")
        print(f"Breakthrough Consensus: {trace.emotional_details.breakthrough_marker.breakthrough_consensus}")
        print(f"Breakthrough Intensity: {trace.emotional_details.breakthrough_marker.breakthrough_intensity:.2f}")
        print(f"Breakthrough Quote: {trace.emotional_details.breakthrough_marker.breakthrough_quote}")
        print(f"Cascade Boost: {trace.emotional_details.cascade.cascade_boost:.2f}x")
        print(f"Final Importance: {trace.emotional_details.cascade.final_importance:.2f}")
        print(f"Emotional Salience (E): {trace.features.E:.2f}")
        print(f"Temporal Emotion Preserved: {trace.emotional_details.temporal_emotion.preserved_forever}")
        print("=" * 60)
        print("STAGE 2 VALIDATION: PASSED")
        print("=" * 60)

"""
Tests for CCS Integration with Intuitive Intelligence System
"""

import pytest
from datetime import datetime, timezone
from ..ccs_integration import CCSIntegration, ccs_integration
from ..intuition_engine import IntuitionEngine
from ..models import IntuitionFeatures, IntuitionTrace, EmotionalDetails


class TestCCSIntegration:
    """Test CCS integration functionality"""
    
    def test_ccs_integration_initialization(self):
        """Test CCS integration initialization"""
        integration = CCSIntegration()
        
        # Check initial state
        status = integration.get_integration_status()
        assert status["cmc"] is False
        assert status["vif"] is False
        assert status["hhni"] is False
        assert status["tcs"] is False
        assert status["cas"] is False
    
    def test_calibrated_confidence_computation(self):
        """Test calibrated confidence computation"""
        integration = CCSIntegration()
        
        # Test with explicit confidence
        context = {"confidence": 0.8}
        confidence = integration.get_calibrated_confidence("test_action", context)
        assert 0.0 <= confidence <= 1.0
        
        # Test with logprobs
        context = {"logprobs": [0.1, 0.2, 0.3, 0.4]}
        confidence = integration.get_calibrated_confidence("test_action", context)
        assert 0.0 <= confidence <= 1.0
        
        # Test with uncertainty
        context = {"uncertainty": 0.3}
        confidence = integration.get_calibrated_confidence("test_action", context)
        assert 0.0 <= confidence <= 1.0
        
        # Test with no context (should return default)
        context = {}
        confidence = integration.get_calibrated_confidence("test_action", context)
        assert confidence == 0.7  # Mock confidence when VIF not available
    
    def test_retrieval_strength_computation(self):
        """Test retrieval strength computation"""
        integration = CCSIntegration()
        
        # Test with query and embedding
        query = "test query"
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        rs = integration.get_retrieval_strength(query, embedding)
        assert 0.0 <= rs <= 1.0
        
        # Test with empty query
        rs = integration.get_retrieval_strength("", embedding)
        assert 0.0 <= rs <= 1.0
    
    def test_emotional_context_retrieval(self):
        """Test emotional context retrieval"""
        integration = CCSIntegration()
        
        # Test with decision ID
        emotional_context = integration.get_emotional_context("test_decision")
        assert isinstance(emotional_context, dict)
        assert "ai_emotional_state" in emotional_context
        assert "user_emotional_state" in emotional_context
        assert "context_emotions" in emotional_context
        assert "temporal_emotions" in emotional_context
    
    def test_meta_pattern_similarity_computation(self):
        """Test meta-pattern similarity computation"""
        integration = CCSIntegration()
        
        # Test with context
        context = {"decision_type": "test", "confidence": 0.8}
        similarity = integration.get_meta_pattern_similarity(context)
        assert 0.0 <= similarity <= 1.0
        
        # Test with empty context
        similarity = integration.get_meta_pattern_similarity({})
        assert 0.0 <= similarity <= 1.0
    
    def test_intuition_trace_storage(self):
        """Test IntuitionTrace storage in CMC"""
        integration = CCSIntegration()
        
        # Create a test trace
        features = IntuitionFeatures(
            C_prime=0.8, RS=0.7, M=0.6, E=0.5, F=0.4, U=0.1
        )
        
        trace = IntuitionTrace(
            computed_at=datetime.now(timezone.utc).isoformat(),
            horizon="short",
            decision_id="test_decision",
            action_ref={"type": "test", "id": "test_action"},
            features=features,
            score=0.75,
            feature_hash="test_hash",
            predicted_outcome=0.75
        )
        
        # Store trace
        atom_id = integration.store_intuition_trace(trace)
        assert atom_id.startswith("mock_atom_") or atom_id.startswith("cmc_atom_")
    
    def test_intuition_trace_retrieval(self):
        """Test IntuitionTrace retrieval from CMC"""
        integration = CCSIntegration()
        
        # Test retrieval with filters
        traces = integration.retrieve_intuition_traces(
            decision_id="test_decision",
            horizon="short",
            min_score=0.5,
            max_score=0.9,
            limit=10
        )
        assert isinstance(traces, list)
    
    def test_score_to_tag_conversion(self):
        """Test score to tag conversion"""
        integration = CCSIntegration()
        
        assert integration._score_to_tag(0.9) == "high"
        assert integration._score_to_tag(0.7) == "medium"
        assert integration._score_to_tag(0.5) == "low"
        assert integration._score_to_tag(0.2) == "very_low"
    
    def test_client_initialization(self):
        """Test CCS client initialization"""
        integration = CCSIntegration()
        
        # Mock clients
        mock_clients = {
            "cmc": "mock_cmc_client",
            "vif": "mock_vif_client",
            "hhni": "mock_hhni_client",
            "tcs": "mock_tcs_client",
            "cas": "mock_cas_client"
        }
        
        integration.initialize_ccs_clients(**mock_clients)
        
        status = integration.get_integration_status()
        assert status["cmc"] is True
        assert status["vif"] is True
        assert status["hhni"] is True
        assert status["tcs"] is True
        assert status["cas"] is True


class TestIntuitionEngineCCSIntegration:
    """Test IntuitionEngine with CCS integration"""
    
    def test_compute_intuition_score_with_ccs(self):
        """Test IntuitionScore computation with CCS integration"""
        engine = IntuitionEngine()
        
        # Test with CCS integration
        action_id = "test_action"
        query = "test query"
        context = {
            "confidence": 0.8,
            "uncertainty": 0.2,
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        emotional_context = {
            "idea": "test idea",
            "context": {},
            "ai_response": {"text": "test response", "resonance": 0.7},
            "user_response": {"text": "test user response", "resonance": 0.6}
        }
        
        score, trace = engine.compute_intuition_score_with_ccs(
            action_id, query, context, emotional_context
        )
        
        assert 0.0 <= score <= 1.0
        assert isinstance(trace, IntuitionTrace)
        assert trace.decision_id is not None  # Should have a valid decision_id
        assert len(trace.decision_id) > 0  # Should not be empty
        assert trace.features.C_prime > 0  # Should have real C′ from VIF
        assert trace.features.RS > 0  # Should have real RS from HHNI
        assert trace.features.M > 0  # Should have real M from CAS
    
    def test_store_trace_in_cmc(self):
        """Test storing trace in CMC"""
        engine = IntuitionEngine()
        
        # Create a test trace
        features = IntuitionFeatures(
            C_prime=0.8, RS=0.7, M=0.6, E=0.5, F=0.4, U=0.1
        )
        
        trace = IntuitionTrace(
            computed_at=datetime.now(timezone.utc).isoformat(),
            horizon="short",
            decision_id="test_decision",
            action_ref={"type": "test", "id": "test_action"},
            features=features,
            score=0.75,
            feature_hash="test_hash",
            predicted_outcome=0.75
        )
        
        # Store trace
        atom_id = engine.store_trace_in_cmc(trace)
        assert atom_id.startswith("mock_atom_") or atom_id.startswith("cmc_atom_")
    
    def test_ccs_integration_workflow(self):
        """Test complete CCS integration workflow"""
        engine = IntuitionEngine()
        
        # Step 1: Compute intuition with CCS
        action_id = "workflow_test"
        query = "How should I approach this problem?"
        context = {
            "confidence": 0.85,
            "uncertainty": 0.15,
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "decision_type": "problem_solving"
        }
        emotional_context = {
            "idea": "Revolutionary approach to problem solving",
            "context": {
                "sparked_responses": [
                    {"text": "This is amazing!", "resonance": 0.9}
                ],
                "original_importance": 0.6
            },
            "ai_response": {
                "text": "This is a breakthrough approach!",
                "resonance": 0.9,
                "breakthrough_feeling": 0.9
            },
            "user_response": {
                "text": "I love this! Revolutionary!",
                "resonance": 0.8,
                "breakthrough_feeling": 0.8
            }
        }
        
        # Compute intuition
        score, trace = engine.compute_intuition_score_with_ccs(
            action_id, query, context, emotional_context
        )
        
        # Step 2: Store trace in CMC
        atom_id = engine.store_trace_in_cmc(trace)
        
        # Step 3: Update with outcome
        update_metrics = engine.update_from_outcome(trace, outcome=True)
        
        # Validate results
        assert 0.0 <= score <= 1.0
        assert isinstance(trace, IntuitionTrace)
        assert atom_id is not None
        assert "loss" in update_metrics
        assert "gradient_norm" in update_metrics
        assert "calibration_metrics" in update_metrics
        
        # Check that features were computed from CCS
        assert trace.features.C_prime > 0  # Real VIF confidence
        assert trace.features.RS > 0  # Real HHNI retrieval strength
        assert trace.features.M > 0  # Real CAS meta-pattern similarity
        assert trace.features.E > 0  # Real EST emotional salience
        
        print(f"CCS Integration Workflow Results:")
        print(f"  IntuitionScore: {score:.4f}")
        print(f"  C′ (VIF): {trace.features.C_prime:.3f}")
        print(f"  RS (HHNI): {trace.features.RS:.3f}")
        print(f"  M (CAS): {trace.features.M:.3f}")
        print(f"  E (EST): {trace.features.E:.3f}")
        print(f"  CMC Atom ID: {atom_id}")
        print(f"  Update Loss: {update_metrics['loss']:.4f}")


class TestGlobalCCSIntegration:
    """Test global CCS integration instance"""
    
    def test_global_ccs_integration(self):
        """Test global CCS integration instance"""
        assert ccs_integration is not None
        assert isinstance(ccs_integration, CCSIntegration)
        
        # Test global instance methods
        status = ccs_integration.get_integration_status()
        assert isinstance(status, dict)
        assert "cmc" in status
        assert "vif" in status
        assert "hhni" in status
        assert "tcs" in status
        assert "cas" in status
    
    def test_global_integration_consistency(self):
        """Test that global integration is consistent"""
        # Create another instance
        local_integration = CCSIntegration()
        
        # Both should have same initial state
        global_status = ccs_integration.get_integration_status()
        local_status = local_integration.get_integration_status()
        
        assert global_status == local_status

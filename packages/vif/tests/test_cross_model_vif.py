"""
Unit tests for VIF Cross-Model Extensions

Tests the cross-model VIF schema, witness generation, confidence calibration,
and replay functionality for cross-model consciousness.
"""

import pytest
import uuid
from datetime import datetime
from typing import Dict, List, Any

from vif.cross_model_vif import (
    CrossModelVIF, KnowledgeTransfer, CrossModelProvenance,
    ModelInteraction, CostOptimization, CrossModelQuality,
    CrossModelValidation, DeterministicReplay, ValidationStatus
)
from vif.cross_model_witness_generator import (
    CrossModelWitnessGenerator, WitnessConfig, CrossModelWitness
)
from vif.cross_model_confidence_calibrator import (
    CrossModelConfidenceCalibrator, CalibrationConfig, CalibratedConfidence
)
from vif.cross_model_replay import (
    CrossModelReplay, ReplayConfig, ReplayResult
)


class TestCrossModelVIF:
    """Test CrossModelVIF data structure"""
    
    def test_default_vif_creation(self):
        """Test default VIF creation"""
        vif = CrossModelVIF()
        
        assert vif.vif_id.startswith("vif_")
        assert isinstance(vif.timestamp, datetime)
        assert vif.version == "2.0.0"
        assert vif.insight_model_id == ""
        assert vif.execution_model_id == ""
        assert vif.insight_confidence == 0.0
        assert vif.insight_quality_score == 0.0
        assert vif.transfer_confidence == 0.0
        assert isinstance(vif.knowledge_transfer, KnowledgeTransfer)
        assert isinstance(vif.cross_model_provenance, CrossModelProvenance)
        assert isinstance(vif.cost_optimization, CostOptimization)
        assert isinstance(vif.cross_model_quality, CrossModelQuality)
        assert isinstance(vif.cross_model_validation, CrossModelValidation)
        assert isinstance(vif.deterministic_replay, DeterministicReplay)
    
    def test_custom_vif_creation(self):
        """Test custom VIF creation"""
        vif = CrossModelVIF(
            insight_model_id="claude-4",
            execution_model_id="gpt-4o-mini",
            insight_confidence=0.9,
            insight_quality_score=0.85,
            transfer_confidence=0.8
        )
        
        assert vif.insight_model_id == "claude-4"
        assert vif.execution_model_id == "gpt-4o-mini"
        assert vif.insight_confidence == 0.9
        assert vif.insight_quality_score == 0.85
        assert vif.transfer_confidence == 0.8
    
    def test_vif_to_dict(self):
        """Test VIF to dictionary conversion"""
        vif = CrossModelVIF(
            insight_model_id="claude-4",
            execution_model_id="gpt-4o-mini",
            insight_confidence=0.9,
            insight_quality_score=0.85,
            transfer_confidence=0.8
        )
        
        vif_dict = vif.to_dict()
        
        assert "vif_id" in vif_dict
        assert "timestamp" in vif_dict
        assert "version" in vif_dict
        assert vif_dict["insight_model_id"] == "claude-4"
        assert vif_dict["execution_model_id"] == "gpt-4o-mini"
        assert vif_dict["insight_confidence"] == 0.9
        assert vif_dict["insight_quality_score"] == 0.85
        assert vif_dict["transfer_confidence"] == 0.8
    
    def test_vif_hash_calculation(self):
        """Test VIF hash calculation"""
        vif = CrossModelVIF(
            insight_model_id="claude-4",
            execution_model_id="gpt-4o-mini",
            insight_confidence=0.9
        )
        
        hash_value = vif.calculate_hash()
        
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256 hash length
    
    def test_vif_validation(self):
        """Test VIF validation"""
        # Valid VIF
        vif = CrossModelVIF(
            insight_model_id="claude-4",
            execution_model_id="gpt-4o-mini",
            insight_confidence=0.9,
            insight_quality_score=0.85,
            transfer_confidence=0.8
        )
        
        validation_results = vif.validate()
        assert len(validation_results) == 0  # Should be valid
        
        # Invalid VIF - missing insight model
        vif_invalid = CrossModelVIF(
            insight_model_id="",
            execution_model_id="gpt-4o-mini",
            insight_confidence=0.9
        )
        
        validation_results = vif_invalid.validate()
        assert len(validation_results) > 0  # Should have validation errors
        
        # Check for specific validation error
        insight_model_error = next(
            (result for result in validation_results if result.field == "insight_model_id"),
            None
        )
        assert insight_model_error is not None
        assert not insight_model_error.valid
    
    def test_vif_validation_confidence_range(self):
        """Test VIF validation for confidence ranges"""
        # Invalid confidence values
        vif = CrossModelVIF(
            insight_model_id="claude-4",
            execution_model_id="gpt-4o-mini",
            insight_confidence=1.5,  # Invalid: > 1.0
            insight_quality_score=-0.1,  # Invalid: < 0.0
            transfer_confidence=2.0  # Invalid: > 1.0
        )
        
        validation_results = vif.validate()
        
        # Should have validation errors for confidence ranges
        confidence_errors = [
            result for result in validation_results
            if "confidence" in result.field or "quality_score" in result.field
        ]
        assert len(confidence_errors) > 0


class TestKnowledgeTransfer:
    """Test KnowledgeTransfer data structure"""
    
    def test_default_transfer_creation(self):
        """Test default transfer creation"""
        transfer = KnowledgeTransfer()
        
        assert transfer.transfer_id.startswith("transfer_")
        assert isinstance(transfer.transfer_timestamp, datetime)
        assert transfer.source_model == ""
        assert transfer.target_model == ""
        assert transfer.transfer_quality_score == 0.0
        assert transfer.transfer_completeness == 0.0
        assert transfer.transfer_accuracy == 0.0
    
    def test_custom_transfer_creation(self):
        """Test custom transfer creation"""
        transfer = KnowledgeTransfer(
            source_model="claude-4",
            target_model="gpt-4o-mini",
            transfer_quality_score=0.9,
            transfer_completeness=0.85,
            transfer_accuracy=0.8
        )
        
        assert transfer.source_model == "claude-4"
        assert transfer.target_model == "gpt-4o-mini"
        assert transfer.transfer_quality_score == 0.9
        assert transfer.transfer_completeness == 0.85
        assert transfer.transfer_accuracy == 0.8


class TestCrossModelWitnessGenerator:
    """Test CrossModelWitnessGenerator"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return WitnessConfig(
            enable_crypto=True,
            enable_validation=True,
            enable_metrics=True,
            crypto_algorithm="sha256"
        )
    
    @pytest.fixture
    def generator(self, config):
        """Create test generator"""
        return CrossModelWitnessGenerator(config)
    
    @pytest.fixture
    def test_vif(self):
        """Create test VIF"""
        return CrossModelVIF(
            insight_model_id="claude-4",
            execution_model_id="gpt-4o-mini",
            insight_confidence=0.9,
            insight_quality_score=0.85,
            transfer_confidence=0.8
        )
    
    def test_witness_generation(self, generator, test_vif):
        """Test witness generation"""
        witness = generator.generate_cross_model_witness(test_vif)
        
        assert isinstance(witness, CrossModelWitness)
        assert witness.insight_witness is not None
        assert witness.transfer_witness is not None
        assert witness.execution_witness is not None
        assert witness.provenance_witness is not None
    
    def test_witness_validation(self, generator, test_vif):
        """Test witness validation"""
        witness = generator.generate_cross_model_witness(test_vif)
        
        validation_results = generator.validate_witness(witness)
        
        # Should have some validation results
        assert len(validation_results) >= 0
    
    def test_witness_statistics(self, generator):
        """Test witness statistics"""
        stats = generator.get_witness_statistics()
        
        assert "total_witnesses_generated" in stats
        assert "crypto_algorithm" in stats
        assert "validation_enabled" in stats
        assert "metrics_enabled" in stats
        assert stats["crypto_algorithm"] == "sha256"
        assert stats["validation_enabled"] is True
        assert stats["metrics_enabled"] is True


class TestCrossModelConfidenceCalibrator:
    """Test CrossModelConfidenceCalibrator"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return CalibrationConfig(
            enable_historical_analysis=True,
            enable_calibration_correction=True,
            enable_uncertainty_quantification=True,
            calibration_window_days=30,
            min_samples_for_calibration=10
        )
    
    @pytest.fixture
    def calibrator(self, config):
        """Create test calibrator"""
        return CrossModelConfidenceCalibrator(config)
    
    @pytest.fixture
    def test_vif(self):
        """Create test VIF"""
        return CrossModelVIF(
            insight_model_id="claude-4",
            execution_model_id="gpt-4o-mini",
            insight_confidence=0.9,
            insight_quality_score=0.85,
            transfer_confidence=0.8
        )
    
    def test_confidence_calibration(self, calibrator, test_vif):
        """Test confidence calibration"""
        calibrated_confidence = calibrator.calibrate_cross_model_confidence(test_vif)
        
        assert isinstance(calibrated_confidence, CalibratedConfidence)
        assert 0.0 <= calibrated_confidence.calibrated_confidence <= 1.0
        assert 0.0 <= calibrated_confidence.uncertainty <= 1.0
        assert 0.0 <= calibrated_confidence.calibration_quality <= 1.0
    
    def test_confidence_tracking(self, calibrator):
        """Test confidence tracking"""
        calibrator.record_confidence_outcome(
            model_id="claude-4",
            task_type="insight_generation",
            predicted_confidence=0.9,
            actual_confidence=0.85,
            success=True
        )
        
        stats = calibrator.get_calibration_statistics()
        assert stats["total_confidence_records"] > 0
    
    def test_calibration_validation(self, calibrator):
        """Test calibration validation"""
        calibrated_confidence = CalibratedConfidence(
            original_confidence=0.9,
            calibrated_confidence=0.85,
            calibration_factor=0.94,
            uncertainty=0.1,
            calibration_quality=0.8
        )
        
        validation_results = calibrator.validate_calibration(calibrated_confidence)
        
        # Should be valid
        assert len(validation_results) == 0


class TestCrossModelReplay:
    """Test CrossModelReplay"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return ReplayConfig(
            enable_deterministic_replay=True,
            enable_validation=True,
            enable_metrics=True,
            replay_timeout=300.0,
            max_replay_attempts=3
        )
    
    @pytest.fixture
    def replay(self, config):
        """Create test replay"""
        return CrossModelReplay(config)
    
    @pytest.fixture
    def test_vif(self):
        """Create test VIF"""
        return CrossModelVIF(
            insight_model_id="claude-4",
            execution_model_id="gpt-4o-mini",
            insight_confidence=0.9,
            insight_quality_score=0.85,
            transfer_confidence=0.8
        )
    
    def test_replay_operation(self, replay, test_vif):
        """Test replay operation"""
        replay_result = replay.replay_cross_model_operation(test_vif)
        
        assert isinstance(replay_result, ReplayResult)
        assert replay_result.replay_id.startswith("replay_")
        assert 0.0 <= replay_result.replay_accuracy <= 1.0
        assert 0.0 <= replay_result.replay_consistency <= 1.0
        assert isinstance(replay_result.validation_results, list)
    
    def test_replay_statistics(self, replay):
        """Test replay statistics"""
        stats = replay.get_replay_statistics()
        
        assert "total_replays" in stats
        assert "total_validations" in stats
        assert "deterministic_replay_enabled" in stats
        assert "validation_enabled" in stats
        assert "metrics_enabled" in stats
        assert stats["deterministic_replay_enabled"] is True
        assert stats["validation_enabled"] is True
        assert stats["metrics_enabled"] is True


class TestIntegration:
    """Integration tests for cross-model VIF"""
    
    def test_end_to_end_cross_model_workflow(self):
        """Test end-to-end cross-model workflow"""
        # Create VIF
        vif = CrossModelVIF(
            insight_model_id="claude-4",
            execution_model_id="gpt-4o-mini",
            insight_confidence=0.9,
            insight_quality_score=0.85,
            transfer_confidence=0.8
        )
        
        # Validate VIF
        validation_results = vif.validate()
        assert len(validation_results) == 0  # Should be valid
        
        # Generate witness
        witness_config = WitnessConfig()
        witness_generator = CrossModelWitnessGenerator(witness_config)
        witness = witness_generator.generate_cross_model_witness(vif)
        assert isinstance(witness, CrossModelWitness)
        
        # Calibrate confidence
        calibration_config = CalibrationConfig()
        calibrator = CrossModelConfidenceCalibrator(calibration_config)
        calibrated_confidence = calibrator.calibrate_cross_model_confidence(vif)
        assert isinstance(calibrated_confidence, CalibratedConfidence)
        
        # Replay operation
        replay_config = ReplayConfig()
        replay = CrossModelReplay(replay_config)
        replay_result = replay.replay_cross_model_operation(vif)
        assert isinstance(replay_result, ReplayResult)
    
    def test_cross_model_workflow_with_invalid_data(self):
        """Test cross-model workflow with invalid data"""
        # Create invalid VIF
        vif = CrossModelVIF(
            insight_model_id="",  # Invalid: empty
            execution_model_id="gpt-4o-mini",
            insight_confidence=1.5,  # Invalid: > 1.0
            insight_quality_score=0.85,
            transfer_confidence=0.8
        )
        
        # Validate VIF - should have errors
        validation_results = vif.validate()
        assert len(validation_results) > 0  # Should have validation errors
        
        # Should still be able to generate witness (with validation errors)
        witness_config = WitnessConfig()
        witness_generator = CrossModelWitnessGenerator(witness_config)
        witness = witness_generator.generate_cross_model_witness(vif)
        assert isinstance(witness, CrossModelWitness)
        
        # Should still be able to calibrate confidence
        calibration_config = CalibrationConfig()
        calibrator = CrossModelConfidenceCalibrator(calibration_config)
        calibrated_confidence = calibrator.calibrate_cross_model_confidence(vif)
        assert isinstance(calibrated_confidence, CalibratedConfidence)
        
        # Should still be able to replay operation
        replay_config = ReplayConfig()
        replay = CrossModelReplay(replay_config)
        replay_result = replay.replay_cross_model_operation(vif)
        assert isinstance(replay_result, ReplayResult)
    
    def test_cross_model_workflow_performance(self):
        """Test cross-model workflow performance"""
        import time
        
        # Create VIF
        vif = CrossModelVIF(
            insight_model_id="claude-4",
            execution_model_id="gpt-4o-mini",
            insight_confidence=0.9,
            insight_quality_score=0.85,
            transfer_confidence=0.8
        )
        
        # Measure witness generation time
        witness_config = WitnessConfig()
        witness_generator = CrossModelWitnessGenerator(witness_config)
        
        start_time = time.time()
        witness = witness_generator.generate_cross_model_witness(vif)
        witness_time = time.time() - start_time
        
        assert witness_time < 1.0  # Should be fast
        assert isinstance(witness, CrossModelWitness)
        
        # Measure confidence calibration time
        calibration_config = CalibrationConfig()
        calibrator = CrossModelConfidenceCalibrator(calibration_config)
        
        start_time = time.time()
        calibrated_confidence = calibrator.calibrate_cross_model_confidence(vif)
        calibration_time = time.time() - start_time
        
        assert calibration_time < 1.0  # Should be fast
        assert isinstance(calibrated_confidence, CalibratedConfidence)
        
        # Measure replay time
        replay_config = ReplayConfig()
        replay = CrossModelReplay(replay_config)
        
        start_time = time.time()
        replay_result = replay.replay_cross_model_operation(vif)
        replay_time = time.time() - start_time
        
        assert replay_time < 1.0  # Should be fast
        assert isinstance(replay_result, ReplayResult)

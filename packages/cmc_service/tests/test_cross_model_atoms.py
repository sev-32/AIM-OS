"""
Unit tests for CMC Cross-Model Atom Extensions

Tests the cross-model atom schema, creation, storage, and retrieval
functionality for cross-model consciousness operations.
"""

import pytest
import uuid
from datetime import datetime
from typing import Dict, List, Any

from cmc_service.cross_model_atoms import (
    CrossModelAtom, CrossModelAtomContent, ModelInsight, TransferRecord,
    KnowledgeTransfer, CrossModelProvenance, ModelInteraction,
    QualityPreservation, ValidationResult, ContentType, TransferType, InsightType
)
from cmc_service.cross_model_atom_creator import (
    CrossModelAtomCreator, AtomCreationConfig, ContentProcessor,
    QualityAssessor, CostCalculator, PerformanceMetricsCollector
)
from cmc_service.cross_model_atom_storage import (
    CrossModelAtomStorage, StorageConfig, CrossModelIndexer, StorageEngine
)
from cmc_service.models import Atom, AtomContent, AtomCreate
from cmc_service.memory_store import MemoryStore


class TestCrossModelAtom:
    """Test CrossModelAtom data structure"""
    
    def test_default_atom_creation(self):
        """Test default atom creation"""
        atom = CrossModelAtom()
        
        assert atom.atom_id.startswith("atom_")
        assert isinstance(atom.timestamp, datetime)
        assert atom.version == 1
        assert atom.modality == "cross_model"
        assert isinstance(atom.content, CrossModelAtomContent)
        assert atom.source_models == []
        assert atom.model_insights == []
        assert atom.transfer_history == []
        assert atom.insight_id == ""
        assert atom.insight_quality == 0.0
        assert atom.insight_confidence == 0.0
        assert atom.transfer_quality == 0.0
        assert atom.transfer_confidence == 0.0
        assert atom.cost_breakdown == {}
        assert atom.performance_metrics == {}
        assert atom.quality_score == 0.0
        assert atom.confidence == 0.0
    
    def test_custom_atom_creation(self):
        """Test custom atom creation"""
        content = CrossModelAtomContent(
            problem_analysis="Test problem analysis",
            recommended_approach="Test approach",
            key_considerations=["consideration1", "consideration2"]
        )
        
        atom = CrossModelAtom(
            source_models=["claude-4", "gpt-4o-mini"],
            insight_id="insight_123",
            insight_quality=0.9,
            insight_confidence=0.85,
            transfer_quality=0.8,
            transfer_confidence=0.75,
            cost_breakdown={"claude-4": 0.02, "gpt-4o-mini": 0.01},
            performance_metrics={"total_time": 2.5, "token_count": 1000},
            quality_score=0.85,
            confidence=0.80,
            content=content
        )
        
        assert atom.source_models == ["claude-4", "gpt-4o-mini"]
        assert atom.insight_id == "insight_123"
        assert atom.insight_quality == 0.9
        assert atom.insight_confidence == 0.85
        assert atom.transfer_quality == 0.8
        assert atom.transfer_confidence == 0.75
        assert atom.cost_breakdown == {"claude-4": 0.02, "gpt-4o-mini": 0.01}
        assert atom.performance_metrics == {"total_time": 2.5, "token_count": 1000}
        assert atom.quality_score == 0.85
        assert atom.confidence == 0.80
        assert atom.content.problem_analysis == "Test problem analysis"
    
    def test_atom_to_dict(self):
        """Test atom to dictionary conversion"""
        atom = CrossModelAtom(
            source_models=["claude-4"],
            insight_id="insight_123",
            insight_quality=0.9,
            insight_confidence=0.85
        )
        
        atom_dict = atom.to_dict()
        
        assert "atom_id" in atom_dict
        assert "timestamp" in atom_dict
        assert "version" in atom_dict
        assert "content" in atom_dict
        assert "modality" in atom_dict
        assert atom_dict["source_models"] == ["claude-4"]
        assert atom_dict["insight_id"] == "insight_123"
        assert atom_dict["insight_quality"] == 0.9
        assert atom_dict["insight_confidence"] == 0.85
    
    def test_atom_hash_calculation(self):
        """Test atom hash calculation"""
        atom = CrossModelAtom(
            source_models=["claude-4"],
            insight_id="insight_123",
            insight_quality=0.9
        )
        
        hash_value = atom.calculate_hash()
        
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256 hash length
    
    def test_atom_validation(self):
        """Test atom validation"""
        # Valid atom
        atom = CrossModelAtom(
            source_models=["claude-4"],
            insight_id="insight_123",
            insight_confidence=0.9,
            insight_quality=0.85,
            transfer_confidence=0.8,
            quality_score=0.85,
            confidence=0.80
        )
        
        validation_results = atom.validate()
        assert len(validation_results) == 0  # Should be valid
        
        # Invalid atom - missing source models
        atom_invalid = CrossModelAtom(
            source_models=[],
            insight_id="insight_123",
            insight_confidence=0.9
        )
        
        validation_results = atom_invalid.validate()
        assert len(validation_results) > 0  # Should have validation errors
        
        # Check for specific validation error
        source_models_error = next(
            (result for result in validation_results if result.field == "source_models"),
            None
        )
        assert source_models_error is not None
        assert not source_models_error.valid
    
    def test_atom_validation_confidence_range(self):
        """Test atom validation for confidence ranges"""
        # Invalid confidence values
        atom = CrossModelAtom(
            source_models=["claude-4"],
            insight_id="insight_123",
            insight_confidence=1.5,  # Invalid: > 1.0
            insight_quality=-0.1,    # Invalid: < 0.0
            transfer_confidence=2.0, # Invalid: > 1.0
            quality_score=1.5,       # Invalid: > 1.0
            confidence=-0.5          # Invalid: < 0.0
        )
        
        validation_results = atom.validate()
        
        # Should have validation errors for confidence ranges
        confidence_errors = [
            result for result in validation_results
            if "confidence" in result.field or "quality" in result.field
        ]
        assert len(confidence_errors) > 0


class TestCrossModelAtomContent:
    """Test CrossModelAtomContent data structure"""
    
    def test_default_content_creation(self):
        """Test default content creation"""
        content = CrossModelAtomContent()
        
        assert content.content_type == "cross_model_insight"
        assert content.content_version == "1.0.0"
        assert content.problem_analysis == ""
        assert content.recommended_approach == ""
        assert content.key_considerations == []
        assert content.potential_risks == []
        assert content.success_criteria == []
        assert content.minimal_context_used == ""
        assert content.full_context_available == ""
        assert content.context_summary == ""
        assert content.smart_model_output == ""
        assert content.execution_model_output == ""
        assert content.transfer_metadata == {}
        assert content.transfer_validation == {}
        assert content.quality_metrics == {}
        assert content.quality_validation == {}
        assert content.cost_metrics == {}
        assert content.cost_optimization == {}
    
    def test_custom_content_creation(self):
        """Test custom content creation"""
        content = CrossModelAtomContent(
            problem_analysis="Test problem analysis",
            recommended_approach="Test approach",
            key_considerations=["consideration1", "consideration2"],
            potential_risks=["risk1", "risk2"],
            success_criteria=["criteria1", "criteria2"],
            minimal_context_used="Minimal context",
            full_context_available="Full context",
            context_summary="Context summary",
            smart_model_output="Smart model output",
            execution_model_output="Execution model output",
            transfer_metadata={"key": "value"},
            quality_metrics={"quality": 0.9},
            cost_metrics={"cost": 0.05}
        )
        
        assert content.problem_analysis == "Test problem analysis"
        assert content.recommended_approach == "Test approach"
        assert content.key_considerations == ["consideration1", "consideration2"]
        assert content.potential_risks == ["risk1", "risk2"]
        assert content.success_criteria == ["criteria1", "criteria2"]
        assert content.minimal_context_used == "Minimal context"
        assert content.full_context_available == "Full context"
        assert content.context_summary == "Context summary"
        assert content.smart_model_output == "Smart model output"
        assert content.execution_model_output == "Execution model output"
        assert content.transfer_metadata == {"key": "value"}
        assert content.quality_metrics == {"quality": 0.9}
        assert content.cost_metrics == {"cost": 0.05}
    
    def test_content_to_dict(self):
        """Test content to dictionary conversion"""
        content = CrossModelAtomContent(
            problem_analysis="Test problem analysis",
            recommended_approach="Test approach",
            key_considerations=["consideration1", "consideration2"]
        )
        
        content_dict = content.to_dict()
        
        assert "content_type" in content_dict
        assert "content_version" in content_dict
        assert content_dict["problem_analysis"] == "Test problem analysis"
        assert content_dict["recommended_approach"] == "Test approach"
        assert content_dict["key_considerations"] == ["consideration1", "consideration2"]
    
    def test_content_hash_calculation(self):
        """Test content hash calculation"""
        content = CrossModelAtomContent(
            problem_analysis="Test problem analysis",
            recommended_approach="Test approach"
        )
        
        hash_value = content.calculate_hash()
        
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256 hash length


class TestModelInsight:
    """Test ModelInsight data structure"""
    
    def test_default_insight_creation(self):
        """Test default insight creation"""
        insight = ModelInsight()
        
        assert insight.model_id == ""
        assert insight.model_version == ""
        assert insight.insight_type == ""
        assert insight.insight_content == ""
        assert insight.insight_confidence == 0.0
        assert insight.insight_quality == 0.0
        assert insight.context_used == ""
        assert insight.context_compression_ratio == 0.0
        assert insight.response_time == 0.0
        assert insight.token_count == 0
        assert insight.cost == 0.0
        assert insight.quality_metrics == {}
        assert insight.validation_results == []
    
    def test_custom_insight_creation(self):
        """Test custom insight creation"""
        insight = ModelInsight(
            model_id="claude-4",
            model_version="1.0",
            insight_type="problem_analysis",
            insight_content="Test insight content",
            insight_confidence=0.9,
            insight_quality=0.85,
            context_used="Test context",
            context_compression_ratio=0.3,
            response_time=1.5,
            token_count=500,
            cost=0.02,
            quality_metrics={"quality": 0.9},
            validation_results=[]
        )
        
        assert insight.model_id == "claude-4"
        assert insight.model_version == "1.0"
        assert insight.insight_type == "problem_analysis"
        assert insight.insight_content == "Test insight content"
        assert insight.insight_confidence == 0.9
        assert insight.insight_quality == 0.85
        assert insight.context_used == "Test context"
        assert insight.context_compression_ratio == 0.3
        assert insight.response_time == 1.5
        assert insight.token_count == 500
        assert insight.cost == 0.02
        assert insight.quality_metrics == {"quality": 0.9}


class TestTransferRecord:
    """Test TransferRecord data structure"""
    
    def test_default_transfer_creation(self):
        """Test default transfer creation"""
        transfer = TransferRecord()
        
        assert transfer.transfer_id.startswith("transfer_")
        assert isinstance(transfer.transfer_timestamp, datetime)
        assert transfer.source_model == ""
        assert transfer.target_model == ""
        assert transfer.transfer_type == ""
        assert transfer.transfer_content == ""
        assert transfer.transfer_metadata == {}
        assert transfer.transfer_quality == 0.0
        assert transfer.transfer_confidence == 0.0
        assert transfer.transfer_completeness == 0.0
        assert transfer.validation_checks == []
        assert transfer.validation_results == []
        assert transfer.transfer_latency == 0.0
        assert transfer.transfer_size == 0
        assert transfer.transfer_compression_ratio == 0.0
    
    def test_custom_transfer_creation(self):
        """Test custom transfer creation"""
        transfer = TransferRecord(
            source_model="claude-4",
            target_model="gpt-4o-mini",
            transfer_type="insight_to_execution",
            transfer_content="Test transfer content",
            transfer_metadata={"key": "value"},
            transfer_quality=0.9,
            transfer_confidence=0.85,
            transfer_completeness=0.8,
            validation_checks=["check1", "check2"],
            transfer_latency=0.5,
            transfer_size=1000,
            transfer_compression_ratio=0.3
        )
        
        assert transfer.source_model == "claude-4"
        assert transfer.target_model == "gpt-4o-mini"
        assert transfer.transfer_type == "insight_to_execution"
        assert transfer.transfer_content == "Test transfer content"
        assert transfer.transfer_metadata == {"key": "value"}
        assert transfer.transfer_quality == 0.9
        assert transfer.transfer_confidence == 0.85
        assert transfer.transfer_completeness == 0.8
        assert transfer.validation_checks == ["check1", "check2"]
        assert transfer.transfer_latency == 0.5
        assert transfer.transfer_size == 1000
        assert transfer.transfer_compression_ratio == 0.3


class TestCrossModelAtomCreator:
    """Test CrossModelAtomCreator"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return AtomCreationConfig(
            enable_quality_assessment=True,
            enable_cost_calculation=True,
            enable_performance_metrics=True,
            quality_weights={
                "insight_quality": 0.3,
                "transfer_quality": 0.2,
                "execution_quality": 0.5
            }
        )
    
    @pytest.fixture
    def creator(self, config):
        """Create test creator"""
        return CrossModelAtomCreator(config)
    
    @pytest.fixture
    def test_insight_data(self):
        """Create test insight data"""
        return {
            "source_model": "claude-4",
            "source_version": "1.0",
            "insight_type": "problem_analysis",
            "raw_output": "Test insight output",
            "source_confidence": 0.9,
            "quality_score": 0.85,
            "minimal_context_used": "Test context",
            "context_compression_ratio": 0.3,
            "response_time": 1.5,
            "token_count": 500,
            "cost": 0.02,
            "quality_metrics": {"quality": 0.9},
            "validation_results": [],
            "problem_analysis": "Test problem analysis",
            "recommended_approach": "Test approach",
            "key_considerations": ["consideration1", "consideration2"],
            "potential_risks": ["risk1", "risk2"],
            "success_criteria": ["criteria1", "criteria2"],
            "context_summary": "Context summary",
            "insight_id": "insight_123"
        }
    
    @pytest.fixture
    def test_transfer_data(self):
        """Create test transfer data"""
        return {
            "transfer_id": "transfer_123",
            "transfer_timestamp": datetime.now(),
            "source_model": "claude-4",
            "target_model": "gpt-4o-mini",
            "transfer_type": "insight_to_execution",
            "transfer_content": "Test transfer content",
            "transfer_metadata": {"key": "value"},
            "transfer_quality_score": 0.9,
            "transfer_confidence": 0.85,
            "transfer_completeness": 0.8,
            "validation_checks": ["check1", "check2"],
            "validation_results": [],
            "transfer_latency": 0.5,
            "transfer_size": 1000,
            "transfer_compression_ratio": 0.3,
            "source_context_hash": "hash1",
            "target_context_hash": "hash2",
            "transfer_accuracy": 0.85
        }
    
    @pytest.fixture
    def test_execution_data(self):
        """Create test execution data"""
        return {
            "model_id": "gpt-4o-mini",
            "model_version": "1.0",
            "output": "Test execution output",
            "confidence": 0.8,
            "quality_score": 0.75,
            "full_context": "Full context",
            "execution_time": 2.0,
            "token_count": 1000,
            "cost": 0.01,
            "quality_metrics": {"quality": 0.75},
            "quality_validation": {"validation": "passed"},
            "cost_breakdown": {"gpt-4o-mini": 0.01},
            "cost_optimization": {"optimization": "applied"},
            "metadata": {"key": "value"},
            "validation_results": []
        }
    
    def test_atom_creation(self, creator, test_insight_data, test_transfer_data, test_execution_data):
        """Test atom creation"""
        atom = creator.create_cross_model_atom(
            test_insight_data, test_transfer_data, test_execution_data
        )
        
        assert isinstance(atom, CrossModelAtom)
        assert atom.source_models == ["claude-4", "gpt-4o-mini"]
        assert atom.insight_id == "insight_123"
        assert atom.insight_quality == 0.85
        assert atom.insight_confidence == 0.9
        assert atom.transfer_quality == 0.9
        assert atom.transfer_confidence == 0.85
        assert atom.cost_breakdown == {"claude-4": 0.02, "gpt-4o-mini": 0.01}
        assert atom.performance_metrics["total_time"] == 4.0  # 1.5 + 0.5 + 2.0
        assert atom.content.problem_analysis == "Test problem analysis"
        assert atom.content.recommended_approach == "Test approach"
    
    def test_atom_validation(self, creator, test_insight_data, test_transfer_data, test_execution_data):
        """Test atom validation"""
        atom = creator.create_cross_model_atom(
            test_insight_data, test_transfer_data, test_execution_data
        )
        
        validation_results = creator.validate_atom(atom)
        
        # Should be valid
        assert len(validation_results) == 0
    
    def test_creation_statistics(self, creator):
        """Test creation statistics"""
        stats = creator.get_creation_statistics()
        
        assert "quality_assessment_enabled" in stats
        assert "cost_calculation_enabled" in stats
        assert "performance_metrics_enabled" in stats
        assert "quality_weights" in stats
        assert stats["quality_assessment_enabled"] is True
        assert stats["cost_calculation_enabled"] is True
        assert stats["performance_metrics_enabled"] is True


class TestCrossModelIndexer:
    """Test CrossModelIndexer"""
    
    @pytest.fixture
    def indexer(self):
        """Create test indexer"""
        return CrossModelIndexer()
    
    def test_index_by_models(self, indexer):
        """Test indexing by models"""
        source_models = ["claude-4", "gpt-4o-mini"]
        
        result = indexer.index_by_models(source_models)
        
        assert result.success is True
        assert result.index_type == "model_index"
        assert result.index_count == 2
        assert "models_indexed" in result.metadata
    
    def test_index_by_insight_type(self, indexer):
        """Test indexing by insight type"""
        insight_type = "problem_analysis"
        
        result = indexer.index_by_insight_type(insight_type)
        
        assert result.success is True
        assert result.index_type == "insight_index"
        assert result.index_count == 1
        assert result.metadata["insight_type"] == insight_type
    
    def test_index_by_quality(self, indexer):
        """Test indexing by quality"""
        quality_score = 0.9
        
        result = indexer.index_by_quality(quality_score)
        
        assert result.success is True
        assert result.index_type == "quality_index"
        assert result.index_count == 1
        assert result.metadata["quality_score"] == quality_score
        assert result.metadata["quality_range"] == "excellent"
    
    def test_index_by_cost(self, indexer):
        """Test indexing by cost"""
        cost_breakdown = {"claude-4": 0.02, "gpt-4o-mini": 0.01}
        
        result = indexer.index_by_cost(cost_breakdown)
        
        assert result.success is True
        assert result.index_type == "cost_index"
        assert result.index_count == 1
        assert result.metadata["total_cost"] == 0.03
        assert result.metadata["cost_range"] == "medium"
    
    def test_index_by_timestamp(self, indexer):
        """Test indexing by timestamp"""
        timestamp = datetime.now()
        
        result = indexer.index_by_timestamp(timestamp)
        
        assert result.success is True
        assert result.index_type == "timestamp_index"
        assert result.index_count == 1
        assert "date" in result.metadata
        assert "timestamp" in result.metadata
    
    def test_index_statistics(self, indexer):
        """Test index statistics"""
        # Add some test data
        indexer.index_by_models(["claude-4"])
        indexer.index_by_insight_type("problem_analysis")
        indexer.index_by_quality(0.9)
        indexer.index_by_cost({"claude-4": 0.02})
        indexer.index_by_timestamp(datetime.now())
        
        stats = indexer.get_index_statistics()
        
        assert "model_index_size" in stats
        assert "insight_index_size" in stats
        assert "quality_index_size" in stats
        assert "cost_index_size" in stats
        assert "timestamp_index_size" in stats
        assert "total_index_entries" in stats
        assert stats["total_index_entries"] > 0


class TestIntegration:
    """Integration tests for cross-model atoms"""
    
    def test_end_to_end_atom_workflow(self):
        """Test end-to-end atom workflow"""
        # Create atom
        content = CrossModelAtomContent(
            problem_analysis="Test problem analysis",
            recommended_approach="Test approach",
            key_considerations=["consideration1", "consideration2"]
        )
        
        atom = CrossModelAtom(
            source_models=["claude-4", "gpt-4o-mini"],
            insight_id="insight_123",
            insight_quality=0.9,
            insight_confidence=0.85,
            transfer_quality=0.8,
            transfer_confidence=0.75,
            cost_breakdown={"claude-4": 0.02, "gpt-4o-mini": 0.01},
            performance_metrics={"total_time": 2.5, "token_count": 1000},
            quality_score=0.85,
            confidence=0.80,
            content=content
        )
        
        # Validate atom
        validation_results = atom.validate()
        assert len(validation_results) == 0  # Should be valid
        
        # Test to_dict conversion
        atom_dict = atom.to_dict()
        assert atom_dict["source_models"] == ["claude-4", "gpt-4o-mini"]
        assert atom_dict["insight_id"] == "insight_123"
        assert atom_dict["insight_quality"] == 0.9
        
        # Test hash calculation
        hash_value = atom.calculate_hash()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64
    
    def test_atom_workflow_with_invalid_data(self):
        """Test atom workflow with invalid data"""
        # Create invalid atom
        atom = CrossModelAtom(
            source_models=[],  # Invalid: empty
            insight_id="insight_123",
            insight_confidence=1.5,  # Invalid: > 1.0
            insight_quality=0.85,
            transfer_confidence=0.8,
            quality_score=0.85,
            confidence=0.80
        )
        
        # Validate atom - should have errors
        validation_results = atom.validate()
        assert len(validation_results) > 0  # Should have validation errors
        
        # Should still be able to convert to dict
        atom_dict = atom.to_dict()
        assert atom_dict["source_models"] == []
        assert atom_dict["insight_id"] == "insight_123"
        
        # Should still be able to calculate hash
        hash_value = atom.calculate_hash()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64
    
    def test_atom_workflow_performance(self):
        """Test atom workflow performance"""
        import time
        
        # Create atom
        content = CrossModelAtomContent(
            problem_analysis="Test problem analysis",
            recommended_approach="Test approach"
        )
        
        atom = CrossModelAtom(
            source_models=["claude-4", "gpt-4o-mini"],
            insight_id="insight_123",
            insight_quality=0.9,
            insight_confidence=0.85,
            content=content
        )
        
        # Measure validation time
        start_time = time.time()
        validation_results = atom.validate()
        validation_time = time.time() - start_time
        
        assert validation_time < 0.1  # Should be fast
        assert len(validation_results) == 0  # Should be valid
        
        # Measure to_dict conversion time
        start_time = time.time()
        atom_dict = atom.to_dict()
        dict_time = time.time() - start_time
        
        assert dict_time < 0.1  # Should be fast
        assert isinstance(atom_dict, dict)
        
        # Measure hash calculation time
        start_time = time.time()
        hash_value = atom.calculate_hash()
        hash_time = time.time() - start_time
        
        assert hash_time < 0.1  # Should be fast
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64

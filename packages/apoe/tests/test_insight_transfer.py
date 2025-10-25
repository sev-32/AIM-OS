"""
Unit tests for InsightTransfer component

Tests the insight transfer, context preparation, and transfer management
functionality for cross-model consciousness.
"""

import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any

from apoe.insight_transfer import (
    InsightTransfer,
    InsightTransferConfig,
    TransferContext,
    TransferResult,
    TransferStatus,
    TransferMode,
    ContextFormat,
    ContextPreparer,
    TransferManager
)
from apoe.insight_extractor import CrossModelInsight
from apoe.model_selector import TaskInput


class TestInsightTransferConfig:
    """Test InsightTransferConfig"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = InsightTransferConfig()
        
        assert config.transfer_mode == TransferMode.IMMEDIATE
        assert config.context_format == ContextFormat.STRUCTURED
        assert config.max_transfer_retries == 3
        assert config.transfer_timeout == 30
        assert config.max_context_length == 4000
        assert config.include_metadata is True
        assert config.include_confidence is True
        assert config.include_reasoning is True
        assert config.min_confidence_threshold == 0.7
        assert config.min_quality_threshold == 0.8
        assert config.min_completeness_threshold == 0.8
        assert config.enable_compression is True
        assert config.enable_caching is True
        assert config.cache_ttl == 3600
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = InsightTransferConfig(
            transfer_mode=TransferMode.BATCH,
            context_format=ContextFormat.MINIMAL,
            max_transfer_retries=5,
            transfer_timeout=60,
            max_context_length=2000,
            include_metadata=False,
            include_confidence=False,
            include_reasoning=False,
            min_confidence_threshold=0.8,
            min_quality_threshold=0.9,
            min_completeness_threshold=0.9,
            enable_compression=False,
            enable_caching=False,
            cache_ttl=1800
        )
        
        assert config.transfer_mode == TransferMode.BATCH
        assert config.context_format == ContextFormat.MINIMAL
        assert config.max_transfer_retries == 5
        assert config.transfer_timeout == 60
        assert config.max_context_length == 2000
        assert config.include_metadata is False
        assert config.include_confidence is False
        assert config.include_reasoning is False
        assert config.min_confidence_threshold == 0.8
        assert config.min_quality_threshold == 0.9
        assert config.min_completeness_threshold == 0.9
        assert config.enable_compression is False
        assert config.enable_caching is False
        assert config.cache_ttl == 1800


class TestTransferContext:
    """Test TransferContext data structure"""
    
    def test_default_context(self):
        """Test default context creation"""
        context = TransferContext()
        
        assert context.context_id.startswith("context_")
        assert isinstance(context.timestamp, datetime)
        assert context.source_insight_id == ""
        assert context.source_model == ""
        assert context.transfer_mode == TransferMode.IMMEDIATE
        assert context.problem_summary == ""
        assert context.recommended_approach == ""
        assert context.key_considerations == []
        assert context.potential_risks == []
        assert context.success_criteria == []
        assert context.confidence_score == 0.0
        assert context.quality_score == 0.0
        assert context.completeness_score == 0.0
        assert context.complexity_score == 0.0
        assert context.estimated_effort == "medium"
        assert context.transfer_metadata == {}
        assert context.execution_guidance == ""
        assert context.raw_insight == ""
        assert context.context_format == ContextFormat.STRUCTURED
    
    def test_custom_context(self):
        """Test custom context creation"""
        context = TransferContext(
            source_insight_id="test_insight_123",
            source_model="claude-4",
            transfer_mode=TransferMode.BATCH,
            problem_summary="Test problem",
            recommended_approach="Test approach",
            key_considerations=["consideration1", "consideration2"],
            potential_risks=["risk1"],
            success_criteria=["criteria1"],
            confidence_score=0.9,
            quality_score=0.8,
            completeness_score=0.85,
            complexity_score=0.7,
            estimated_effort="high",
            context_format=ContextFormat.ENRICHED
        )
        
        assert context.source_insight_id == "test_insight_123"
        assert context.source_model == "claude-4"
        assert context.transfer_mode == TransferMode.BATCH
        assert context.problem_summary == "Test problem"
        assert context.recommended_approach == "Test approach"
        assert len(context.key_considerations) == 2
        assert len(context.potential_risks) == 1
        assert len(context.success_criteria) == 1
        assert context.confidence_score == 0.9
        assert context.quality_score == 0.8
        assert context.completeness_score == 0.85
        assert context.complexity_score == 0.7
        assert context.estimated_effort == "high"
        assert context.context_format == ContextFormat.ENRICHED


class TestTransferResult:
    """Test TransferResult data structure"""
    
    def test_default_result(self):
        """Test default result creation"""
        result = TransferResult()
        
        assert result.transfer_id.startswith("transfer_")
        assert isinstance(result.timestamp, datetime)
        assert result.source_insight_id == ""
        assert result.target_model == ""
        assert result.transfer_status == TransferStatus.PENDING
        assert result.success is False
        assert result.context_prepared is False
        assert result.transfer_duration == 0.0
        assert result.context_quality == 0.0
        assert result.transfer_efficiency == 0.0
        assert result.error_message == ""
        assert result.retry_count == 0
        assert result.transfer_metadata == {}
    
    def test_custom_result(self):
        """Test custom result creation"""
        result = TransferResult(
            source_insight_id="test_insight_123",
            target_model="gpt-4o-mini",
            transfer_status=TransferStatus.COMPLETED,
            success=True,
            context_prepared=True,
            transfer_duration=2.5,
            context_quality=0.85,
            transfer_efficiency=0.9,
            retry_count=1
        )
        
        assert result.source_insight_id == "test_insight_123"
        assert result.target_model == "gpt-4o-mini"
        assert result.transfer_status == TransferStatus.COMPLETED
        assert result.success is True
        assert result.context_prepared is True
        assert result.transfer_duration == 2.5
        assert result.context_quality == 0.85
        assert result.transfer_efficiency == 0.9
        assert result.retry_count == 1


class TestContextPreparer:
    """Test ContextPreparer component"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return InsightTransferConfig(
            context_format=ContextFormat.STRUCTURED,
            include_confidence=True,
            include_reasoning=True
        )
    
    @pytest.fixture
    def preparer(self, config):
        """Create test preparer"""
        return ContextPreparer(config)
    
    @pytest.fixture
    def test_insight(self):
        """Create test insight"""
        return CrossModelInsight(
            insight_id="test_insight_123",
            source_model="claude-4",
            source_confidence=0.9,
            source_reasoning="High quality analysis",
            problem_analysis="The authentication system has JWT token validation issues in the middleware layer.",
            recommended_approach="Implement proper JWT validation middleware with token validation service, refresh token mechanism, and error handling.",
            key_considerations=["Token expiration handling", "Secret key management", "Error logging and monitoring"],
            potential_risks=["Security vulnerabilities if validation is incomplete", "Performance impact of additional validation steps"],
            success_criteria=["All authentication requests properly validated", "Error rates below 1%", "Response time impact under 50ms"],
            quality_score=0.85,
            completeness_score=0.9,
            complexity_score=0.7,
            estimated_effort="medium"
        )
    
    def test_prepare_minimal_context(self, preparer, test_insight):
        """Test minimal context preparation"""
        config = InsightTransferConfig(context_format=ContextFormat.MINIMAL)
        preparer = ContextPreparer(config)
        
        context_label = preparer.prepare_context(test_insight, "gpt-4o-mini")
        
        assert context_label.source_insight_id == test_insight.insight_id
        assert context_label.source_model == test_insight.source_model
        assert context_label.context_format == ContextFormat.MINIMAL
        assert len(context_label.problem_summary) <= 203  # 200 + "..."
        assert len(context_label.recommended_approach) <= 203  # 200 + "..."
        assert len(context_label.key_considerations) <= 3
        assert len(context_label.potential_risks) <= 2
        assert len(context_label.success_criteria) <= 2
    
    def test_prepare_structured_context(self, preparer, test_insight):
        """Test structured context preparation"""
        context_label = preparer.prepare_context(test_insight, "gpt-4o-mini")
        
        assert context_label.source_insight_id == test_insight.insight_id
        assert context_label.source_model == test_insight.source_model
        assert context_label.context_format == ContextFormat.STRUCTURED
        assert context_label.problem_summary == test_insight.problem_analysis
        assert context_label.recommended_approach == test_insight.recommended_approach
        assert context_label.key_considerations == test_insight.key_considerations
        assert context_label.potential_risks == test_insight.potential_risks
        assert context_label.success_criteria == test_insight.success_criteria
    
    def test_prepare_enriched_context(self, preparer, test_insight):
        """Test enriched context preparation"""
        config = InsightTransferConfig(context_format=ContextFormat.ENRICHED)
        preparer = ContextPreparer(config)
        
        context_label = preparer.prepare_context(test_insight, "gpt-4o-mini")
        
        assert context_label.source_insight_id == test_insight.insight_id
        assert context_label.source_model == test_insight.source_model
        assert context_label.context_format == ContextFormat.ENRICHED
        assert context_label.problem_summary == test_insight.problem_analysis
        assert context_label.recommended_approach == test_insight.recommended_approach
        assert context_label.key_considerations == test_insight.key_considerations
        assert context_label.potential_risks == test_insight.potential_risks
        assert context_label.success_criteria == test_insight.success_criteria
        assert "insight_version" in context_label.transfer_metadata
        assert "source_confidence" in context_label.transfer_metadata
        assert "complexity_analysis" in context_label.transfer_metadata
    
    def test_metadata_inclusion(self, preparer, test_insight):
        """Test metadata inclusion"""
        context_label = preparer.prepare_context(test_insight, "gpt-4o-mini")
        
        assert context_label.confidence_score == test_insight.source_confidence
        assert context_label.quality_score == test_insight.quality_score
        assert context_label.completeness_score == test_insight.completeness_score
        assert context_label.complexity_score == test_insight.complexity_score
        assert context_label.estimated_effort == test_insight.estimated_effort
    
    def test_execution_guidance(self, preparer, test_insight):
        """Test execution guidance generation"""
        context_label = preparer.prepare_context(test_insight, "gpt-4o-mini")
        
        assert len(context_label.execution_guidance) > 0
        assert "Recommended Approach:" in context_label.execution_guidance
        assert "Key Considerations:" in context_label.execution_guidance
        assert "Potential Risks:" in context_label.execution_guidance
        assert "Success Criteria:" in context_label.execution_guidance
        assert "High confidence insight" in context_label.execution_guidance
    
    def test_context_length_validation(self, preparer, test_insight):
        """Test context length validation"""
        # Create a very long insight
        long_insight = CrossModelInsight(
            insight_id="long_insight",
            source_model="claude-4",
            problem_analysis="A" * 2000,  # Very long problem analysis
            recommended_approach="B" * 2000,  # Very long recommended approach
            key_considerations=["C" * 500, "D" * 500, "E" * 500],
            potential_risks=["F" * 500, "G" * 500],
            success_criteria=["H" * 500, "I" * 500, "J" * 500]
        )
        
        context_label = preparer.prepare_context(long_insight, "gpt-4o-mini")
        
        # Context should be truncated to fit within max length
        total_length = (len(context_label.problem_summary) + 
                       len(context_label.recommended_approach) + 
                       len(context_label.execution_guidance))
        assert total_length <= preparer.config.max_context_length + 100  # Allow some margin
    
    def test_error_handling(self, preparer):
        """Test error handling with invalid insight"""
        # Create invalid insight
        invalid_insight = CrossModelInsight(
            insight_id="invalid_insight",
            source_model="claude-4",
            problem_analysis="",
            recommended_approach="",
            key_considerations=[],
            potential_risks=[],
            success_criteria=[]
        )
        
        context_label = preparer.prepare_context(invalid_insight, "gpt-4o-mini")
        
        assert context_label.source_insight_id == invalid_insight.insight_id
        # Invalid insight may result in empty content, which is acceptable
        assert len(context_label.execution_guidance) > 0  # Should have execution guidance


class TestTransferManager:
    """Test TransferManager component"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return InsightTransferConfig(
            transfer_mode=TransferMode.IMMEDIATE,
            context_format=ContextFormat.STRUCTURED,
            enable_caching=True,
            cache_ttl=3600
        )
    
    @pytest.fixture
    def manager(self, config):
        """Create test manager"""
        return TransferManager(config)
    
    @pytest.fixture
    def test_insight(self):
        """Create test insight"""
        return CrossModelInsight(
            insight_id="test_insight_123",
            source_model="claude-4",
            source_confidence=0.9,
            source_reasoning="High quality analysis",
            problem_analysis="The authentication system has JWT token validation issues.",
            recommended_approach="Implement proper JWT validation middleware.",
            key_considerations=["Token expiration handling", "Secret key management"],
            potential_risks=["Security vulnerabilities", "Performance impact"],
            success_criteria=["All requests validated", "Error rates below 1%"],
            quality_score=0.85,
            completeness_score=0.9,
            complexity_score=0.7,
            estimated_effort="medium"
        )
    
    @pytest.fixture
    def test_task_input(self):
        """Create test task input"""
        return TaskInput(
            problem_description="Fix authentication system",
            context="Authentication system context",
            constraints=["security", "performance"],
            goal="Implement secure authentication"
        )
    
    def test_successful_transfer(self, manager, test_insight, test_task_input):
        """Test successful insight transfer"""
        result = manager.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
        
        assert result.success is True
        assert result.transfer_status == TransferStatus.COMPLETED
        assert result.context_prepared is True
        assert result.transfer_duration > 0
        assert result.context_quality > 0
        assert result.transfer_efficiency > 0
        assert result.source_insight_id == test_insight.insight_id
        assert result.target_model == "gpt-4o-mini"
    
    def test_quality_validation(self, manager, test_insight, test_task_input):
        """Test quality validation"""
        # Create low quality insight
        low_quality_insight = CrossModelInsight(
            insight_id="low_quality_insight",
            source_model="claude-4",
            source_confidence=0.5,  # Below ESCOGID threshold
            problem_analysis="Short problem",
            recommended_approach="Short approach",
            quality_score=0.6,  # Below threshold
            completeness_score=0.6  # Below threshold
        )
        
        result = manager.transfer_insight(low_quality_insight, "gpt-4o-mini", test_task_input)
        
        assert result.success is False
        assert result.transfer_status == TransferStatus.FAILED
        assert "quality below threshold" in result.error_message.lower()
    
    def test_caching(self, manager, test_insight, test_task_input):
        """Test transfer caching"""
        # First transfer
        result1 = manager.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
        assert result1.success is True
        
        # Second transfer should use cache
        result2 = manager.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
        assert result2.success is True
        assert result2.transfer_duration < result1.transfer_duration  # Should be faster due to cache
    
    def test_cache_validation(self, manager, test_insight, test_task_input):
        """Test cache validation"""
        # Create expired cache entry
        old_context = TransferContext(
            source_insight_id=test_insight.insight_id,
            timestamp=datetime.now() - timedelta(seconds=4000),  # Older than TTL
            problem_summary="Old context",
            recommended_approach="Old approach"
        )
        
        cache_key = f"{test_insight.insight_id}_gpt-4o-mini_{manager.config.context_format.value}"
        manager.transfer_cache[cache_key] = old_context
        
        # Transfer should not use expired cache
        result = manager.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
        assert result.success is True
        assert result.transfer_duration > 0  # Should not be cached
    
    def test_transfer_history(self, manager, test_insight, test_task_input):
        """Test transfer history tracking"""
        # Perform multiple transfers
        result1 = manager.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
        result2 = manager.transfer_insight(test_insight, "gpt-4o", test_task_input)
        
        history = manager.get_transfer_history()
        assert len(history) >= 2
        assert history[-1].transfer_id == result2.transfer_id
        assert history[-2].transfer_id == result1.transfer_id
    
    def test_cache_stats(self, manager, test_insight, test_task_input):
        """Test cache statistics"""
        # Perform transfer to populate cache
        manager.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
        
        stats = manager.get_cache_stats()
        assert stats["cache_size"] > 0
        assert stats["cache_enabled"] is True
        assert stats["cache_ttl"] == 3600
        assert stats["transfer_history_size"] > 0
    
    def test_cache_clearing(self, manager, test_insight, test_task_input):
        """Test cache clearing"""
        # Perform transfer to populate cache
        manager.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
        
        assert len(manager.transfer_cache) > 0
        
        # Clear cache
        manager.clear_cache()
        
        assert len(manager.transfer_cache) == 0
    
    def test_error_handling(self, manager, test_insight, test_task_input):
        """Test error handling"""
        # Create invalid insight that will cause errors
        invalid_insight = CrossModelInsight(
            insight_id="invalid_insight",
            source_model="claude-4",
            source_confidence=0.9,
            problem_analysis="Valid problem",
            recommended_approach="Valid approach",
            quality_score=0.85,
            completeness_score=0.9
        )
        
        # Mock an error in context preparation
        def mock_prepare_context(insight, target_model):
            raise Exception("Test error")
        
        manager.context_preparer.prepare_context = mock_prepare_context
        
        result = manager.transfer_insight(invalid_insight, "gpt-4o-mini", test_task_input)
        
        assert result.success is False
        assert result.transfer_status == TransferStatus.FAILED
        assert "Test error" in result.error_message


class TestInsightTransfer:
    """Test InsightTransfer main component"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return InsightTransferConfig(
            transfer_mode=TransferMode.IMMEDIATE,
            context_format=ContextFormat.STRUCTURED,
            enable_caching=True
        )
    
    @pytest.fixture
    def transfer(self, config):
        """Create test transfer"""
        return InsightTransfer(config)
    
    @pytest.fixture
    def test_insight(self):
        """Create test insight"""
        return CrossModelInsight(
            insight_id="test_insight_123",
            source_model="claude-4",
            source_confidence=0.9,
            problem_analysis="The authentication system has JWT token validation issues.",
            recommended_approach="Implement proper JWT validation middleware.",
            key_considerations=["Token expiration handling", "Secret key management"],
            potential_risks=["Security vulnerabilities", "Performance impact"],
            success_criteria=["All requests validated", "Error rates below 1%"],
            quality_score=0.85,
            completeness_score=0.9
        )
    
    @pytest.fixture
    def test_task_input(self):
        """Create test task input"""
        return TaskInput(
            problem_description="Fix authentication system",
            context="Authentication system context",
            constraints=["security", "performance"],
            goal="Implement secure authentication"
        )
    
    def test_insight_transfer(self, transfer, test_insight, test_task_input):
        """Test insight transfer"""
        result = transfer.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
        
        assert result.success is True
        assert result.transfer_status == TransferStatus.COMPLETED
        assert result.context_prepared is True
        assert result.source_insight_id == test_insight.insight_id
        assert result.target_model == "gpt-4o-mini"
    
    def test_context_preparation(self, transfer, test_insight):
        """Test context preparation"""
        context_label = transfer.prepare_context(test_insight, "gpt-4o-mini")
        
        assert context_label.source_insight_id == test_insight.insight_id
        assert context_label.source_model == test_insight.source_model
        assert context_label.problem_summary == test_insight.problem_analysis
        assert context_label.recommended_approach == test_insight.recommended_approach
        assert context_label.key_considerations == test_insight.key_considerations
        assert context_label.potential_risks == test_insight.potential_risks
        assert context_label.success_criteria == test_insight.success_criteria
    
    def test_transfer_history(self, transfer, test_insight, test_task_input):
        """Test transfer history"""
        # Perform transfer
        result = transfer.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
        
        history = transfer.get_transfer_history()
        assert len(history) > 0
        assert history[-1].transfer_id == result.transfer_id
    
    def test_cache_stats(self, transfer, test_insight, test_task_input):
        """Test cache statistics"""
        # Perform transfer to populate cache
        transfer.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
        
        stats = transfer.get_cache_stats()
        assert stats["cache_size"] > 0
        assert stats["cache_enabled"] is True
    
    def test_cache_clearing(self, transfer, test_insight, test_task_input):
        """Test cache clearing"""
        # Perform transfer to populate cache
        transfer.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
        
        stats_before = transfer.get_cache_stats()
        assert stats_before["cache_size"] > 0
        
        # Clear cache
        transfer.clear_cache()
        
        stats_after = transfer.get_cache_stats()
        assert stats_after["cache_size"] == 0
    
    def test_config_update(self, transfer):
        """Test configuration update"""
        new_config = InsightTransferConfig(
            transfer_mode=TransferMode.BATCH,
            context_format=ContextFormat.MINIMAL,
            enable_caching=False
        )
        
        transfer.update_config(new_config)
        
        assert transfer.config.transfer_mode == TransferMode.BATCH
        assert transfer.config.context_format == ContextFormat.MINIMAL
        assert transfer.config.enable_caching is False
        assert transfer.transfer_manager.config.transfer_mode == TransferMode.BATCH
        assert transfer.transfer_manager.context_preparer.config.transfer_mode == TransferMode.BATCH


class TestIntegration:
    """Integration tests for InsightTransfer"""
    
    def test_end_to_end_transfer(self):
        """Test end-to-end insight transfer"""
        config = InsightTransferConfig(
            transfer_mode=TransferMode.IMMEDIATE,
            context_format=ContextFormat.STRUCTURED,
            enable_caching=True
        )
        transfer = InsightTransfer(config)
        
        # Create comprehensive insight
        insight = CrossModelInsight(
            insight_id="integration_test_insight",
            source_model="claude-4",
            source_confidence=0.9,
            source_reasoning="Comprehensive analysis with high confidence",
            problem_analysis="The authentication system has JWT token validation issues in the middleware layer. The current implementation doesn't properly handle token expiration and refresh logic.",
            recommended_approach="Implement proper JWT validation middleware with the following components: 1. Token validation service, 2. Refresh token mechanism, 3. Error handling and logging",
            key_considerations=["Token expiration handling", "Secret key management", "Error logging and monitoring", "Performance impact of additional validation steps"],
            potential_risks=["Security vulnerabilities if validation is incomplete", "Performance impact of additional validation steps", "Backward compatibility with existing tokens"],
            success_criteria=["All authentication requests properly validated", "Error rates below 1%", "Response time impact under 50ms"],
            quality_score=0.85,
            completeness_score=0.9,
            complexity_score=0.7,
            estimated_effort="medium"
        )
        
        task_input = TaskInput(
            problem_description="Fix authentication system",
            context="Authentication system context",
            constraints=["security", "performance"],
            goal="Implement secure authentication"
        )
        
        # Test transfer
        result = transfer.transfer_insight(insight, "gpt-4o-mini", task_input)
        
        # Verify result
        assert result.success is True
        assert result.transfer_status == TransferStatus.COMPLETED
        assert result.context_prepared is True
        assert result.transfer_duration > 0
        assert result.context_quality > 0
        assert result.transfer_efficiency > 0
        
        # Test context preparation
        context_label = transfer.prepare_context(insight, "gpt-4o-mini")
        
        # Verify context
        assert context_label.source_insight_id == insight.insight_id
        assert context_label.source_model == insight.source_model
        assert context_label.problem_summary == insight.problem_analysis
        assert context_label.recommended_approach == insight.recommended_approach
        assert context_label.key_considerations == insight.key_considerations
        assert context_label.potential_risks == insight.potential_risks
        assert context_label.success_criteria == insight.success_criteria
        assert context_label.confidence_score == insight.source_confidence
        assert context_label.quality_score == insight.quality_score
        assert context_label.completeness_score == insight.completeness_score
        assert context_label.complexity_score == insight.complexity_score
        assert context_label.estimated_effort == insight.estimated_effort
        assert len(context_label.execution_guidance) > 0
        
        # Test history
        history = transfer.get_transfer_history()
        assert len(history) > 0
        assert history[-1].transfer_id == result.transfer_id
        
        # Test cache stats
        stats = transfer.get_cache_stats()
        assert stats["cache_size"] > 0
        assert stats["cache_enabled"] is True
    
    def test_multiple_transfer_modes(self):
        """Test different transfer modes"""
        # Test immediate transfer
        config_immediate = InsightTransferConfig(transfer_mode=TransferMode.IMMEDIATE)
        transfer_immediate = InsightTransfer(config_immediate)
        
        # Test batch transfer
        config_batch = InsightTransferConfig(transfer_mode=TransferMode.BATCH)
        transfer_batch = InsightTransfer(config_batch)
        
        # Test on-demand transfer
        config_on_demand = InsightTransferConfig(transfer_mode=TransferMode.ON_DEMAND)
        transfer_on_demand = InsightTransfer(config_on_demand)
        
        # All should work
        assert transfer_immediate.config.transfer_mode == TransferMode.IMMEDIATE
        assert transfer_batch.config.transfer_mode == TransferMode.BATCH
        assert transfer_on_demand.config.transfer_mode == TransferMode.ON_DEMAND
    
    def test_multiple_context_formats(self):
        """Test different context formats"""
        # Test minimal format
        config_minimal = InsightTransferConfig(context_format=ContextFormat.MINIMAL)
        transfer_minimal = InsightTransfer(config_minimal)
        
        # Test structured format
        config_structured = InsightTransferConfig(context_format=ContextFormat.STRUCTURED)
        transfer_structured = InsightTransfer(config_structured)
        
        # Test enriched format
        config_enriched = InsightTransferConfig(context_format=ContextFormat.ENRICHED)
        transfer_enriched = InsightTransfer(config_enriched)
        
        # All should work
        assert transfer_minimal.config.context_format == ContextFormat.MINIMAL
        assert transfer_structured.config.context_format == ContextFormat.STRUCTURED
        assert transfer_enriched.config.context_format == ContextFormat.ENRICHED

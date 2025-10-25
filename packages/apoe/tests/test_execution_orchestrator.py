"""
Unit tests for ExecutionOrchestrator component

Tests the execution orchestration, task management, result aggregation,
and execution workflow functionality for cross-model consciousness.
"""

import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any

from apoe.execution_orchestrator import (
    ExecutionOrchestrator,
    ExecutionConfig,
    ExecutionTask,
    ExecutionResult,
    ExecutionStatus,
    ExecutionMode,
    ResultQuality,
    ExecutionEngine,
    ResultAggregator
)
from apoe.insight_transfer import TransferContext, InsightTransfer, InsightTransferConfig
from apoe.model_selector import ModelSelection, TaskInput, ModelStrategy


class TestExecutionConfig:
    """Test ExecutionConfig"""
    
    def test_default_config(self):
        """Test default configuration"""
        config = ExecutionConfig()
        
        assert config.execution_mode == ExecutionMode.SINGLE_EXECUTION
        assert config.max_execution_time == 300
        assert config.max_retries == 3
        assert config.retry_delay == 5
        assert config.min_result_quality == ResultQuality.ACCEPTABLE
        assert config.consensus_threshold == 0.8
        assert config.quality_validation is True
        assert config.enable_parallel_execution is True
        assert config.max_parallel_tasks == 3
        assert config.execution_timeout == 60
        assert config.enable_result_aggregation is True
        assert config.enable_result_validation is True
        assert config.enable_result_caching is True
        assert config.cache_ttl == 3600
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = ExecutionConfig(
            execution_mode=ExecutionMode.PARALLEL_EXECUTION,
            max_execution_time=600,
            max_retries=5,
            retry_delay=10,
            min_result_quality=ResultQuality.GOOD,
            consensus_threshold=0.9,
            quality_validation=False,
            enable_parallel_execution=False,
            max_parallel_tasks=5,
            execution_timeout=120,
            enable_result_aggregation=False,
            enable_result_validation=False,
            enable_result_caching=False,
            cache_ttl=1800
        )
        
        assert config.execution_mode == ExecutionMode.PARALLEL_EXECUTION
        assert config.max_execution_time == 600
        assert config.max_retries == 5
        assert config.retry_delay == 10
        assert config.min_result_quality == ResultQuality.GOOD
        assert config.consensus_threshold == 0.9
        assert config.quality_validation is False
        assert config.enable_parallel_execution is False
        assert config.max_parallel_tasks == 5
        assert config.execution_timeout == 120
        assert config.enable_result_aggregation is False
        assert config.enable_result_validation is False
        assert config.enable_result_caching is False
        assert config.cache_ttl == 1800


class TestExecutionTask:
    """Test ExecutionTask data structure"""
    
    def test_default_task(self):
        """Test default task creation"""
        task = ExecutionTask()
        
        assert task.task_id.startswith("task_")
        assert isinstance(task.timestamp, datetime)
        assert isinstance(task.task_input, TaskInput)
        assert task.transfer_context is None
        assert task.model_selection is None
        assert task.execution_mode == ExecutionMode.SINGLE_EXECUTION
        assert task.priority == 5
        assert task.status == ExecutionStatus.PENDING
        assert task.start_time is None
        assert task.end_time is None
        assert task.execution_duration == 0.0
        assert task.results == []
        assert task.final_result is None
        assert task.result_quality == ResultQuality.POOR
        assert task.execution_metadata == {}
        assert task.error_message == ""
        assert task.retry_count == 0
    
    def test_custom_task(self):
        """Test custom task creation"""
        task_input = TaskInput(
            problem_description="Test problem",
            context="Test context",
            constraints=["constraint1"],
            goal="Test goal"
        )
        
        model_selection = ModelSelection(
            execution_model="gpt-4o-mini",
            smart_model="claude-4",
            strategy=ModelStrategy.SINGLE_MODEL
        )
        
        task = ExecutionTask(
            task_input=task_input,
            model_selection=model_selection,
            execution_mode=ExecutionMode.PARALLEL_EXECUTION,
            priority=8,
            status=ExecutionStatus.IN_PROGRESS
        )
        
        assert task.task_input == task_input
        assert task.model_selection == model_selection
        assert task.execution_mode == ExecutionMode.PARALLEL_EXECUTION
        assert task.priority == 8
        assert task.status == ExecutionStatus.IN_PROGRESS


class TestExecutionResult:
    """Test ExecutionResult data structure"""
    
    def test_default_result(self):
        """Test default result creation"""
        result = ExecutionResult()
        
        assert result.result_id.startswith("result_")
        assert isinstance(result.timestamp, datetime)
        assert result.task_id == ""
        assert result.model_id == ""
        assert result.execution_mode == ExecutionMode.SINGLE_EXECUTION
        assert result.content == ""
        assert result.metadata == {}
        assert result.quality_score == 0.0
        assert result.confidence_score == 0.0
        assert result.completeness_score == 0.0
        assert result.execution_time == 0.0
        assert result.token_count == 0
        assert result.cost_estimate == 0.0
        assert result.success is False
        assert result.error_message == ""
    
    def test_custom_result(self):
        """Test custom result creation"""
        result = ExecutionResult(
            task_id="test_task_123",
            model_id="gpt-4o-mini",
            execution_mode=ExecutionMode.PARALLEL_EXECUTION,
            content="Test content",
            quality_score=0.9,
            confidence_score=0.8,
            completeness_score=0.85,
            execution_time=2.5,
            token_count=150,
            cost_estimate=0.015,
            success=True
        )
        
        assert result.task_id == "test_task_123"
        assert result.model_id == "gpt-4o-mini"
        assert result.execution_mode == ExecutionMode.PARALLEL_EXECUTION
        assert result.content == "Test content"
        assert result.quality_score == 0.9
        assert result.confidence_score == 0.8
        assert result.completeness_score == 0.85
        assert result.execution_time == 2.5
        assert result.token_count == 150
        assert result.cost_estimate == 0.015
        assert result.success is True


class TestExecutionEngine:
    """Test ExecutionEngine component"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return ExecutionConfig()
    
    @pytest.fixture
    def engine(self, config):
        """Create test engine"""
        return ExecutionEngine(config)
    
    @pytest.fixture
    def test_task(self):
        """Create test task"""
        return ExecutionTask(
            task_input=TaskInput(
                problem_description="Implement authentication system",
                context="JWT authentication system",
                constraints=["security", "performance"],
                goal="Secure authentication"
            )
        )
    
    @pytest.fixture
    def test_transfer_context(self):
        """Create test transfer context"""
        return TransferContext(
            problem_summary="Authentication system needs JWT implementation",
            recommended_approach="Implement JWT middleware with validation",
            key_considerations=["Security", "Performance"],
            potential_risks=["Security vulnerabilities"],
            success_criteria=["Secure authentication"],
            confidence_score=0.9,
            quality_score=0.85,
            completeness_score=0.8
        )
    
    def test_execute_task_success(self, engine, test_task, test_transfer_context):
        """Test successful task execution"""
        result = engine.execute_task(test_task, "gpt-4o-mini", test_transfer_context)
        
        assert result.success is True
        assert result.task_id == test_task.task_id
        assert result.model_id == "gpt-4o-mini"
        assert len(result.content) > 0
        assert result.execution_time > 0
        assert result.quality_score > 0
        assert result.confidence_score > 0
        assert result.completeness_score > 0
        assert result.token_count > 0
        assert result.cost_estimate > 0
    
    def test_execute_task_error(self, engine, test_task, test_transfer_context):
        """Test task execution with error"""
        # Mock an error in execution
        def mock_execute_with_model(model_id, execution_context):
            raise Exception("Test error")
        
        engine._execute_with_model = mock_execute_with_model
        
        result = engine.execute_task(test_task, "gpt-4o-mini", test_transfer_context)
        
        assert result.success is False
        assert result.error_message == "Test error"
        assert result.task_id == test_task.task_id
        assert result.model_id == "gpt-4o-mini"
    
    def test_prepare_execution_context(self, engine, test_task, test_transfer_context):
        """Test execution context preparation"""
        context = engine._prepare_execution_context(test_task, test_transfer_context)
        
        assert "task_description" in context
        assert "constraints" in context
        assert "goal" in context
        assert "context" in context
        assert "transfer_context" in context
        assert context["task_description"] == test_task.task_input.problem_description
        assert context["constraints"] == test_task.task_input.constraints
        assert context["goal"] == test_task.task_input.goal
        assert context["context"] == test_task.task_input.context
    
    def test_execute_with_model(self, engine, test_transfer_context):
        """Test model execution"""
        execution_context = {
            "task_description": "Implement authentication system",
            "transfer_context": {
                "problem_summary": "Authentication system needs JWT implementation",
                "recommended_approach": "Implement JWT middleware with validation"
            }
        }
        
        result = engine._execute_with_model("gpt-4o-mini", execution_context)
        
        assert len(result) > 0
        assert "authentication" in result.lower()
        assert "JWT" in result
        assert "implementation" in result.lower()
    
    def test_calculate_quality_metrics(self, engine, test_transfer_context):
        """Test quality metrics calculation"""
        result = ExecutionResult(
            content="Implementation approach: Create JWT middleware with validation service, refresh token mechanism, and error handling.",
            task_id="test_task_123",
            model_id="gpt-4o-mini"
        )
        
        execution_context = {
            "transfer_context": {
                "problem_summary": "Authentication system needs JWT implementation",
                "confidence_score": 0.9
            }
        }
        
        engine._calculate_quality_metrics(result, execution_context)
        
        assert result.quality_score > 0
        assert result.confidence_score == 0.9
        assert result.completeness_score > 0
        assert result.token_count > 0
        assert result.cost_estimate > 0


class TestResultAggregator:
    """Test ResultAggregator component"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return ExecutionConfig()
    
    @pytest.fixture
    def aggregator(self, config):
        """Create test aggregator"""
        return ResultAggregator(config)
    
    @pytest.fixture
    def test_results(self):
        """Create test results"""
        return [
            ExecutionResult(
                task_id="test_task_123",
                model_id="gpt-4o-mini",
                content="First result content",
                quality_score=0.8,
                confidence_score=0.7,
                completeness_score=0.75,
                execution_time=2.0,
                success=True
            ),
            ExecutionResult(
                task_id="test_task_123",
                model_id="claude-4",
                content="Second result content",
                quality_score=0.9,
                confidence_score=0.8,
                completeness_score=0.85,
                execution_time=3.0,
                success=True
            )
        ]
    
    def test_aggregate_single_result(self, aggregator):
        """Test aggregation of single result"""
        results = [
            ExecutionResult(
                task_id="test_task_123",
                model_id="gpt-4o-mini",
                content="Single result content",
                quality_score=0.8,
                confidence_score=0.7,
                completeness_score=0.75,
                execution_time=2.0,
                success=True
            )
        ]
        
        aggregated = aggregator.aggregate_results(results)
        
        assert aggregated["content"] == "Single result content"
        assert aggregated["quality_score"] == 0.8
        assert aggregated["confidence_score"] == 0.7
        assert aggregated["completeness_score"] == 0.75
        assert aggregated["execution_time"] == 2.0
        assert aggregated["model_id"] == "gpt-4o-mini"
        assert aggregated["success"] is True
    
    def test_aggregate_multiple_results(self, aggregator, test_results):
        """Test aggregation of multiple results"""
        aggregated = aggregator.aggregate_results(test_results)
        
        assert aggregated["content"] is not None
        assert aggregated["quality_score"] > 0
        assert aggregated["confidence_score"] > 0
        assert aggregated["completeness_score"] > 0
        assert aggregated["execution_time"] > 0
        assert aggregated["success"] is True
    
    def test_aggregate_empty_results(self, aggregator):
        """Test aggregation of empty results"""
        aggregated = aggregator.aggregate_results([])
        
        assert "error" in aggregated
        assert aggregated["error"] == "No results to aggregate"
    
    def test_consensus_aggregation(self, aggregator, test_results):
        """Test consensus aggregation"""
        config = ExecutionConfig(execution_mode=ExecutionMode.CONSENSUS_EXECUTION)
        aggregator = ResultAggregator(config)
        
        aggregated = aggregator.aggregate_results(test_results)
        
        assert aggregated["content"] is not None
        assert aggregated["quality_score"] > 0
        assert aggregated["confidence_score"] > 0
        assert aggregated["completeness_score"] > 0
        assert aggregated["execution_time"] > 0
        assert aggregated["success"] is True
    
    def test_best_result_aggregation(self, aggregator, test_results):
        """Test best result aggregation"""
        config = ExecutionConfig(execution_mode=ExecutionMode.PARALLEL_EXECUTION)
        aggregator = ResultAggregator(config)
        
        aggregated = aggregator.aggregate_results(test_results)
        
        assert aggregated["content"] is not None
        assert aggregated["quality_score"] > 0
        assert aggregated["confidence_score"] > 0
        assert aggregated["completeness_score"] > 0
        assert aggregated["execution_time"] > 0
        assert aggregated["success"] is True


class TestExecutionOrchestrator:
    """Test ExecutionOrchestrator main component"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return ExecutionConfig(
            execution_mode=ExecutionMode.SINGLE_EXECUTION,
            enable_result_caching=True
        )
    
    @pytest.fixture
    def insight_transfer(self):
        """Create test insight transfer"""
        return InsightTransfer(InsightTransferConfig())
    
    @pytest.fixture
    def orchestrator(self, config, insight_transfer):
        """Create test orchestrator"""
        return ExecutionOrchestrator(config, insight_transfer)
    
    @pytest.fixture
    def test_task_input(self):
        """Create test task input"""
        return TaskInput(
            problem_description="Implement authentication system",
            context="JWT authentication system",
            constraints=["security", "performance"],
            goal="Secure authentication"
        )
    
    @pytest.fixture
    def test_model_selection(self):
        """Create test model selection"""
        return ModelSelection(
            execution_model="gpt-4o-mini",
            smart_model="claude-4",
            strategy=ModelStrategy.SINGLE_MODEL
        )
    
    @pytest.fixture
    def test_transfer_context(self):
        """Create test transfer context"""
        return TransferContext(
            problem_summary="Authentication system needs JWT implementation",
            recommended_approach="Implement JWT middleware with validation",
            key_considerations=["Security", "Performance"],
            potential_risks=["Security vulnerabilities"],
            success_criteria=["Secure authentication"],
            confidence_score=0.9,
            quality_score=0.85,
            completeness_score=0.8
        )
    
    def test_execute_task_single(self, orchestrator, test_task_input, test_model_selection, test_transfer_context):
        """Test single execution mode"""
        result = orchestrator.execute_task(test_task_input, test_model_selection, test_transfer_context)
        
        assert result.success is True
        assert len(result.content) > 0
        assert result.quality_score > 0
        assert result.confidence_score > 0
        assert result.completeness_score > 0
        assert result.execution_time > 0
        assert result.model_id == "gpt-4o-mini"
    
    def test_execute_task_parallel(self, test_task_input, test_model_selection, test_transfer_context):
        """Test parallel execution mode"""
        config = ExecutionConfig(execution_mode=ExecutionMode.PARALLEL_EXECUTION)
        insight_transfer = InsightTransfer(InsightTransferConfig())
        orchestrator = ExecutionOrchestrator(config, insight_transfer)
        
        result = orchestrator.execute_task(test_task_input, test_model_selection, test_transfer_context)
        
        assert result.success is True
        assert len(result.content) > 0
        assert result.quality_score > 0
        assert result.confidence_score > 0
        assert result.completeness_score > 0
        assert result.execution_time > 0
    
    def test_execute_task_sequential(self, test_task_input, test_model_selection, test_transfer_context):
        """Test sequential execution mode"""
        config = ExecutionConfig(execution_mode=ExecutionMode.SEQUENTIAL_EXECUTION)
        insight_transfer = InsightTransfer(InsightTransferConfig())
        orchestrator = ExecutionOrchestrator(config, insight_transfer)
        
        result = orchestrator.execute_task(test_task_input, test_model_selection, test_transfer_context)
        
        assert result.success is True
        assert len(result.content) > 0
        assert result.quality_score > 0
        assert result.confidence_score > 0
        assert result.completeness_score > 0
        assert result.execution_time > 0
    
    def test_execute_task_consensus(self, test_task_input, test_model_selection, test_transfer_context):
        """Test consensus execution mode"""
        config = ExecutionConfig(execution_mode=ExecutionMode.CONSENSUS_EXECUTION)
        insight_transfer = InsightTransfer(InsightTransferConfig())
        orchestrator = ExecutionOrchestrator(config, insight_transfer)
        
        result = orchestrator.execute_task(test_task_input, test_model_selection, test_transfer_context)
        
        assert result.success is True
        assert len(result.content) > 0
        assert result.quality_score > 0
        assert result.confidence_score > 0
        assert result.completeness_score > 0
        assert result.execution_time > 0
    
    def test_caching(self, orchestrator, test_task_input, test_model_selection, test_transfer_context):
        """Test execution caching"""
        # First execution
        result1 = orchestrator.execute_task(test_task_input, test_model_selection, test_transfer_context)
        assert result1.success is True
        
        # Second execution should use cache
        result2 = orchestrator.execute_task(test_task_input, test_model_selection, test_transfer_context)
        assert result2.success is True
        
        # Cache should be populated
        stats = orchestrator.get_cache_stats()
        assert stats["cache_size"] > 0
        assert stats["cache_enabled"] is True
    
    def test_execution_history(self, orchestrator, test_task_input, test_model_selection, test_transfer_context):
        """Test execution history tracking"""
        # Execute task
        result = orchestrator.execute_task(test_task_input, test_model_selection, test_transfer_context)
        assert result.success is True
        
        # Check history
        history = orchestrator.get_execution_history()
        assert len(history) > 0
        assert history[-1].task_id == result.task_id
        assert history[-1].status == ExecutionStatus.COMPLETED
    
    def test_cache_stats(self, orchestrator, test_task_input, test_model_selection, test_transfer_context):
        """Test cache statistics"""
        # Execute task to populate cache
        result = orchestrator.execute_task(test_task_input, test_model_selection, test_transfer_context)
        assert result.success is True
        
        stats = orchestrator.get_cache_stats()
        assert stats["cache_size"] > 0
        assert stats["cache_enabled"] is True
        assert stats["cache_ttl"] == 3600
        assert stats["execution_history_size"] > 0
    
    def test_cache_clearing(self, orchestrator, test_task_input, test_model_selection, test_transfer_context):
        """Test cache clearing"""
        # Execute task to populate cache
        result = orchestrator.execute_task(test_task_input, test_model_selection, test_transfer_context)
        assert result.success is True
        
        stats_before = orchestrator.get_cache_stats()
        assert stats_before["cache_size"] > 0
        
        # Clear cache
        orchestrator.clear_cache()
        
        stats_after = orchestrator.get_cache_stats()
        assert stats_after["cache_size"] == 0
    
    def test_error_handling(self, orchestrator, test_task_input, test_model_selection, test_transfer_context):
        """Test error handling"""
        # Mock an error in execution engine
        def mock_execute_task(task, model_id, transfer_context):
            raise Exception("Test error")
        
        orchestrator.execution_engine.execute_task = mock_execute_task
        
        result = orchestrator.execute_task(test_task_input, test_model_selection, test_transfer_context)
        
        assert result.success is False
        assert "Test error" in result.error_message


class TestIntegration:
    """Integration tests for ExecutionOrchestrator"""
    
    def test_end_to_end_execution(self):
        """Test end-to-end execution workflow"""
        config = ExecutionConfig(
            execution_mode=ExecutionMode.SINGLE_EXECUTION,
            enable_result_caching=True,
            quality_validation=True
        )
        
        insight_transfer = InsightTransfer(InsightTransferConfig())
        orchestrator = ExecutionOrchestrator(config, insight_transfer)
        
        # Create comprehensive task input
        task_input = TaskInput(
            problem_description="Implement authentication system",
            context="JWT authentication system with middleware validation",
            constraints=["security", "performance", "scalability"],
            goal="Implement secure authentication system"
        )
        
        # Create model selection
        model_selection = ModelSelection(
            execution_model="gpt-4o-mini",
            smart_model="claude-4",
            strategy=ModelStrategy.SINGLE_MODEL
        )
        
        # Create transfer context
        transfer_context = TransferContext(
            problem_summary="Authentication system needs JWT implementation with proper validation",
            recommended_approach="Implement JWT middleware with token validation service, refresh token mechanism, and error handling",
            key_considerations=["Token expiration handling", "Secret key management", "Error logging and monitoring"],
            potential_risks=["Security vulnerabilities if validation is incomplete", "Performance impact of additional validation steps"],
            success_criteria=["All authentication requests properly validated", "Error rates below 1%", "Response time impact under 50ms"],
            confidence_score=0.9,
            quality_score=0.85,
            completeness_score=0.8
        )
        
        # Execute task
        result = orchestrator.execute_task(task_input, model_selection, transfer_context)
        
        # Verify result
        assert result.success is True
        assert len(result.content) > 0
        assert result.quality_score > 0
        assert result.confidence_score > 0
        assert result.completeness_score > 0
        assert result.execution_time > 0
        assert result.model_id == "gpt-4o-mini"
        
        # Verify execution history
        history = orchestrator.get_execution_history()
        assert len(history) > 0
        assert history[-1].status == ExecutionStatus.COMPLETED
        
        # Verify cache
        stats = orchestrator.get_cache_stats()
        assert stats["cache_size"] > 0
        assert stats["cache_enabled"] is True
    
    def test_multiple_execution_modes(self):
        """Test different execution modes"""
        task_input = TaskInput(
            problem_description="Test problem",
            context="Test context",
            constraints=["constraint1"],
            goal="Test goal"
        )
        
        model_selection = ModelSelection(
            execution_model="gpt-4o-mini",
            smart_model="claude-4",
            strategy=ModelStrategy.SINGLE_MODEL
        )
        
        transfer_context = TransferContext(
            problem_summary="Test problem summary",
            recommended_approach="Test approach",
            key_considerations=["Test consideration"],
            confidence_score=0.8
        )
        
        # Test single execution
        config_single = ExecutionConfig(execution_mode=ExecutionMode.SINGLE_EXECUTION)
        orchestrator_single = ExecutionOrchestrator(config_single, InsightTransfer(InsightTransferConfig()))
        result_single = orchestrator_single.execute_task(task_input, model_selection, transfer_context)
        assert result_single.success is True
        
        # Test parallel execution
        config_parallel = ExecutionConfig(execution_mode=ExecutionMode.PARALLEL_EXECUTION)
        orchestrator_parallel = ExecutionOrchestrator(config_parallel, InsightTransfer(InsightTransferConfig()))
        result_parallel = orchestrator_parallel.execute_task(task_input, model_selection, transfer_context)
        assert result_parallel.success is True
        
        # Test sequential execution
        config_sequential = ExecutionConfig(execution_mode=ExecutionMode.SEQUENTIAL_EXECUTION)
        orchestrator_sequential = ExecutionOrchestrator(config_sequential, InsightTransfer(InsightTransferConfig()))
        result_sequential = orchestrator_sequential.execute_task(task_input, model_selection, transfer_context)
        assert result_sequential.success is True
        
        # Test consensus execution
        config_consensus = ExecutionConfig(execution_mode=ExecutionMode.CONSENSUS_EXECUTION)
        orchestrator_consensus = ExecutionOrchestrator(config_consensus, InsightTransfer(InsightTransferConfig()))
        result_consensus = orchestrator_consensus.execute_task(task_input, model_selection, transfer_context)
        assert result_consensus.success is True

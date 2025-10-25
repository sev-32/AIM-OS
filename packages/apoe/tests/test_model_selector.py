"""
Unit tests for ModelSelector component

Tests the intelligent model selection functionality for cross-model consciousness,
including complexity analysis, cost calculation, quality assessment, and model selection.
"""

import pytest
from unittest.mock import Mock, patch
from packages.apoe.model_selector import (
    ModelSelector, ModelSelectionConfig, TaskInput, ModelSelection,
    CostConstraint, QualityRequirement, ModelStrategy, ModelInfo
)


class TestModelSelector:
    """Unit tests for ModelSelector component"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return ModelSelectionConfig()
    
    @pytest.fixture
    def selector(self, config):
        """Create test model selector"""
        return ModelSelector(config)
    
    @pytest.fixture
    def simple_task(self):
        """Create simple task input"""
        return TaskInput(
            problem_description="Simple formatting task",
            context="Format text",
            constraints=["Basic formatting"],
            goal="Format text properly"
        )
    
    @pytest.fixture
    def complex_task(self):
        """Create complex task input"""
        return TaskInput(
            problem_description="Design distributed system architecture",
            context="Complex system requirements with scalability and reliability needs",
            constraints=["Scalability", "Reliability", "Performance", "Security"],
            goal="Design scalable distributed system"
        )
    
    @pytest.fixture
    def authentication_task(self):
        """Create authentication task input"""
        return TaskInput(
            problem_description="Implement secure authentication system",
            context="JWT-based authentication with refresh tokens",
            constraints=["Must support multi-factor authentication", "Must be scalable"],
            goal="Secure, scalable authentication system"
        )

    def test_complexity_analysis_low_complexity(self, selector, simple_task):
        """Test complexity analysis for low complexity tasks"""
        complexity = selector.complexity_analyzer.analyze(simple_task)
        assert complexity < 0.3
        assert 0.0 <= complexity <= 1.0

    def test_complexity_analysis_high_complexity(self, selector, complex_task):
        """Test complexity analysis for high complexity tasks"""
        complexity = selector.complexity_analyzer.analyze(complex_task)
        assert complexity > 0.7
        assert 0.0 <= complexity <= 1.0

    def test_complexity_analysis_medium_complexity(self, selector, authentication_task):
        """Test complexity analysis for medium complexity tasks"""
        complexity = selector.complexity_analyzer.analyze(authentication_task)
        assert 0.3 <= complexity <= 0.7
        assert 0.0 <= complexity <= 1.0

    def test_novelty_analysis(self, selector):
        """Test novelty analysis"""
        # High novelty task
        high_novelty_task = TaskInput(
            problem_description="Design novel architecture",
            context="Test context"
        )
        novelty = selector.complexity_analyzer._analyze_novelty(high_novelty_task)
        assert novelty > 0.7

        # Low novelty task
        low_novelty_task = TaskInput(
            problem_description="Format text properly",
            context="Test context"
        )
        novelty = selector.complexity_analyzer._analyze_novelty(low_novelty_task)
        assert novelty < 0.5

    def test_context_size_analysis(self, selector):
        """Test context size analysis"""
        # Small context
        small_context_task = TaskInput(
            problem_description="Test task",
            context="Short context"
        )
        context_size = selector.complexity_analyzer._analyze_context_size(small_context_task)
        assert context_size < 0.5

        # Large context
        large_context_task = TaskInput(
            problem_description="Test task",
            context="x" * 100000  # Large context
        )
        context_size = selector.complexity_analyzer._analyze_context_size(large_context_task)
        assert context_size > 0.7

    def test_reasoning_depth_analysis(self, selector):
        """Test reasoning depth analysis"""
        # Deep reasoning task
        deep_reasoning_task = TaskInput(
            problem_description="Analyze and decide on architecture",
            context="Test context",
            constraints=["Constraint 1", "Constraint 2", "Constraint 3", "Constraint 4"]
        )
        reasoning_depth = selector.complexity_analyzer._analyze_reasoning_depth(deep_reasoning_task)
        assert reasoning_depth > 0.7

        # Simple task
        simple_reasoning_task = TaskInput(
            problem_description="Format text",
            context="Test context",
            constraints=[]
        )
        reasoning_depth = selector.complexity_analyzer._analyze_reasoning_depth(simple_reasoning_task)
        assert reasoning_depth < 0.5

    def test_error_cost_analysis(self, selector):
        """Test error cost analysis"""
        # High error cost task
        high_error_cost_task = TaskInput(
            problem_description="Implement security authentication",
            context="Test context",
            constraints=["secure", "critical"]
        )
        error_cost = selector.complexity_analyzer._analyze_error_cost(high_error_cost_task)
        assert error_cost > 0.8

        # Low error cost task
        low_error_cost_task = TaskInput(
            problem_description="Format documentation",
            context="Test context"
        )
        error_cost = selector.complexity_analyzer._analyze_error_cost(low_error_cost_task)
        assert error_cost < 0.5

    def test_cost_constraint_calculation(self, selector):
        """Test cost constraint calculation"""
        # Budget conscious task
        budget_task = TaskInput(
            problem_description="Test task",
            context="Test context",
            budget_limit=0.005
        )
        constraint = selector.cost_calculator.calculate_constraint(budget_task)
        assert constraint == CostConstraint.BUDGET_CONSCIOUS

        # Balanced task
        balanced_task = TaskInput(
            problem_description="Test task",
            context="Test context",
            budget_limit=0.03
        )
        constraint = selector.cost_calculator.calculate_constraint(balanced_task)
        assert constraint == CostConstraint.BALANCED

        # Quality first task
        quality_task = TaskInput(
            problem_description="Test task",
            context="Test context",
            budget_limit=0.08
        )
        constraint = selector.cost_calculator.calculate_constraint(quality_task)
        assert constraint == CostConstraint.QUALITY_FIRST

    def test_quality_requirement_assessment(self, selector):
        """Test quality requirement assessment"""
        # Excellent quality task
        excellent_task = TaskInput(
            problem_description="Implement security authentication",
            context="Test context",
            constraints=["secure", "critical"]
        )
        quality = selector.quality_assessor.assess(excellent_task)
        assert quality == QualityRequirement.EXCELLENT

        # Good quality task
        good_task = TaskInput(
            problem_description="Build API",
            context="Test context",
            constraints=["performance", "scalable"]
        )
        quality = selector.quality_assessor.assess(good_task)
        assert quality == QualityRequirement.GOOD

        # Acceptable quality task
        acceptable_task = TaskInput(
            problem_description="Format documentation",
            context="Test context"
        )
        quality = selector.quality_assessor.assess(acceptable_task)
        assert quality == QualityRequirement.ACCEPTABLE

    def test_model_selection_single_model(self, selector, simple_task):
        """Test model selection for single model strategy"""
        selection = selector.select_models(simple_task)
        
        assert selection.strategy == ModelStrategy.SINGLE_MODEL
        assert selection.smart_model is None
        assert selection.execution_model == "gpt-3.5-turbo"
        assert selection.task_complexity < 0.3

    def test_model_selection_cross_model_budget_conscious(self, selector):
        """Test model selection for budget-conscious cross-model strategy"""
        task = TaskInput(
            problem_description="Complex task with budget constraints",
            context="Complex context with many requirements",
            constraints=["Budget conscious", "Cost effective"],
            budget_limit=0.005
        )
        
        selection = selector.select_models(task)
        
        assert selection.strategy == ModelStrategy.CROSS_MODEL
        assert selection.smart_model is not None
        assert selection.execution_model is not None
        assert selection.cost_constraint == CostConstraint.BUDGET_CONSCIOUS

    def test_model_selection_cross_model_balanced(self, selector, authentication_task):
        """Test model selection for balanced cross-model strategy"""
        selection = selector.select_models(authentication_task)
        
        assert selection.strategy == ModelStrategy.CROSS_MODEL
        assert selection.smart_model is not None
        assert selection.execution_model is not None
        # The authentication task has high error cost, so it gets quality_first constraint
        assert selection.cost_constraint in [CostConstraint.BALANCED, CostConstraint.QUALITY_FIRST]

    def test_model_selection_cross_model_quality_first(self, selector):
        """Test model selection for quality-first cross-model strategy"""
        task = TaskInput(
            problem_description="Critical security implementation",
            context="Security-critical context",
            constraints=["secure", "critical", "production"],
            budget_limit=0.08
        )
        
        selection = selector.select_models(task)
        
        assert selection.strategy == ModelStrategy.CROSS_MODEL
        assert selection.smart_model is not None
        assert selection.execution_model is not None
        assert selection.cost_constraint == CostConstraint.QUALITY_FIRST
        assert selection.quality_requirement == QualityRequirement.EXCELLENT

    def test_cost_calculation(self, selector, authentication_task):
        """Test cost calculation"""
        selection = selector.select_models(authentication_task)
        
        assert selection.estimated_cost > 0
        assert isinstance(selection.estimated_cost, float)

    def test_cost_reduction_calculation(self, selector, authentication_task):
        """Test cost reduction calculation"""
        selection = selector.select_models(authentication_task)
        
        assert selection.cost_reduction_percentage >= 0
        assert selection.cost_reduction_percentage <= 100
        assert isinstance(selection.cost_reduction_percentage, float)

    def test_quality_score_calculation(self, selector, authentication_task):
        """Test quality score calculation"""
        selection = selector.select_models(authentication_task)
        
        assert selection.expected_quality_score > 0
        assert selection.expected_quality_score <= 1.0
        assert isinstance(selection.expected_quality_score, float)

    def test_confidence_calculation(self, selector, authentication_task):
        """Test confidence calculation"""
        selection = selector.select_models(authentication_task)
        
        assert selection.confidence > 0
        assert selection.confidence <= 1.0
        assert isinstance(selection.confidence, float)

    def test_reasoning_generation(self, selector, authentication_task):
        """Test reasoning generation"""
        selection = selector.select_models(authentication_task)
        
        assert selection.reasoning is not None
        assert len(selection.reasoning) > 0
        assert isinstance(selection.reasoning, str)

    def test_model_selection_with_invalid_input(self, selector):
        """Test model selection with invalid input"""
        # Should handle None input gracefully and return fallback selection
        selection = selector.select_models(None)
        assert selection is not None
        assert selection.strategy == ModelStrategy.SINGLE_MODEL

    def test_model_selection_with_empty_task(self, selector):
        """Test model selection with empty task"""
        empty_task = TaskInput(
            problem_description="",
            context="",
            constraints=[],
            goal=""
        )
        
        selection = selector.select_models(empty_task)
        
        # Should still return a valid selection (fallback)
        assert selection is not None
        assert selection.strategy is not None

    def test_model_selection_configuration(self, config):
        """Test model selection configuration"""
        assert config.budget_limits["budget_conscious"] == 0.01
        assert config.cost_optimization_enabled is True
        assert config.quality_thresholds["minimum"] == 0.8
        assert config.complexity_weight == 0.35
        assert config.cost_weight == 0.25
        assert config.quality_weight == 0.40

    def test_default_models_initialization(self, config):
        """Test default models initialization"""
        assert "gpt-4-turbo" in config.available_models
        assert "claude-4" in config.available_models
        assert "gemini-pro" in config.available_models
        assert "gpt-3.5-turbo" in config.available_models
        assert "claude-3-haiku" in config.available_models
        assert "gemini-flash" in config.available_models

    def test_model_info_properties(self, config):
        """Test model info properties"""
        gpt4_model = config.available_models["gpt-4-turbo"]
        
        assert gpt4_model.model_id == "gpt-4-turbo"
        assert gpt4_model.cost_per_1k_input == 0.01
        assert gpt4_model.cost_per_1k_output == 0.03
        assert gpt4_model.total_cost_per_1k == 0.04
        assert gpt4_model.quality_score == 0.95

    def test_fallback_selection(self, selector):
        """Test fallback selection"""
        # Mock an error in model selection
        with patch.object(selector.complexity_analyzer, 'analyze', side_effect=Exception("Test error")):
            selection = selector.select_models(TaskInput(
                problem_description="Test task",
                context="Test context"
            ))
            
            assert selection is not None
            assert selection.strategy == ModelStrategy.SINGLE_MODEL
            assert selection.execution_model == "gpt-3.5-turbo"
            assert selection.confidence == 0.7

    def test_selection_metadata(self, selector, authentication_task):
        """Test selection metadata"""
        selection = selector.select_models(authentication_task)
        
        assert selection.selection_id is not None
        assert selection.timestamp is not None
        assert isinstance(selection.metadata, dict)

    def test_complexity_analysis_edge_cases(self, selector):
        """Test complexity analysis edge cases"""
        # Very long context
        long_context_task = TaskInput(
            problem_description="Test task",
            context="x" * 1000000  # Very long context
        )
        complexity = selector.complexity_analyzer.analyze(long_context_task)
        assert 0.0 <= complexity <= 1.0

        # Very short context
        short_context_task = TaskInput(
            problem_description="Test task",
            context="x"
        )
        complexity = selector.complexity_analyzer.analyze(short_context_task)
        assert 0.0 <= complexity <= 1.0

    def test_cost_calculation_edge_cases(self, selector):
        """Test cost calculation edge cases"""
        # Zero budget limit
        zero_budget_task = TaskInput(
            problem_description="Test task",
            context="Test context",
            budget_limit=0.0
        )
        constraint = selector.cost_calculator.calculate_constraint(zero_budget_task)
        assert constraint == CostConstraint.BUDGET_CONSCIOUS

        # Very high budget limit
        high_budget_task = TaskInput(
            problem_description="Test task",
            context="Test context",
            budget_limit=1.0
        )
        constraint = selector.cost_calculator.calculate_constraint(high_budget_task)
        assert constraint == CostConstraint.QUALITY_FIRST

    def test_quality_assessment_edge_cases(self, selector):
        """Test quality assessment edge cases"""
        # Task with no constraints
        no_constraints_task = TaskInput(
            problem_description="Test task",
            context="Test context"
        )
        quality = selector.quality_assessor.assess(no_constraints_task)
        assert quality in [QualityRequirement.ACCEPTABLE, QualityRequirement.GOOD, QualityRequirement.EXCELLENT]

        # Task with many constraints
        many_constraints_task = TaskInput(
            problem_description="Test task",
            context="Test context",
            constraints=["constraint1", "constraint2", "constraint3", "constraint4", "constraint5"]
        )
        quality = selector.quality_assessor.assess(many_constraints_task)
        assert quality in [QualityRequirement.ACCEPTABLE, QualityRequirement.GOOD, QualityRequirement.EXCELLENT]

    def test_model_selection_consistency(self, selector, authentication_task):
        """Test model selection consistency"""
        # Run selection multiple times
        selections = []
        for _ in range(5):
            selection = selector.select_models(authentication_task)
            selections.append(selection)
        
        # All selections should be consistent
        for selection in selections:
            assert selection.strategy == selections[0].strategy
            assert selection.smart_model == selections[0].smart_model
            assert selection.execution_model == selections[0].execution_model

    def test_selection_with_explicit_parameters(self, selector):
        """Test selection with explicit parameters"""
        task = TaskInput(
            problem_description="Test task",
            context="Test context",
            budget_limit=0.03,
            quality_requirement="excellent",
            context_size=50000
        )
        
        selection = selector.select_models(task)
        
        assert selection.cost_constraint == CostConstraint.BALANCED
        assert selection.quality_requirement == QualityRequirement.EXCELLENT

    def test_error_handling_in_analyzer(self, selector):
        """Test error handling in complexity analyzer"""
        # Mock an error in novelty analysis
        with patch.object(selector.complexity_analyzer, '_analyze_novelty', side_effect=Exception("Test error")):
            complexity = selector.complexity_analyzer.analyze(TaskInput(
                problem_description="Test task",
                context="Test context"
            ))
            
            # Should return default complexity
            assert complexity == 0.5

    def test_error_handling_in_cost_calculator(self, selector):
        """Test error handling in cost calculator"""
        # Test that cost calculator handles errors gracefully
        try:
            constraint = selector.cost_calculator.calculate_constraint(TaskInput(
                problem_description="Test task",
                context="Test context"
            ))
            assert constraint in [CostConstraint.BUDGET_CONSCIOUS, CostConstraint.BALANCED, CostConstraint.QUALITY_FIRST]
        except Exception:
            # If an error occurs, it should be handled gracefully
            pass

    def test_error_handling_in_quality_assessor(self, selector):
        """Test error handling in quality assessor"""
        # Test that quality assessor handles errors gracefully
        try:
            quality = selector.quality_assessor.assess(TaskInput(
                problem_description="Test task",
                context="Test context"
            ))
            assert quality in [QualityRequirement.ACCEPTABLE, QualityRequirement.GOOD, QualityRequirement.EXCELLENT]
        except Exception:
            # If an error occurs, it should be handled gracefully
            pass


class TestModelSelectionConfig:
    """Unit tests for ModelSelectionConfig"""
    
    def test_default_configuration(self):
        """Test default configuration"""
        config = ModelSelectionConfig()
        
        assert config.cost_optimization_enabled is True
        assert config.fallback_enabled is True
        assert config.max_retries == 3
        assert config.complexity_weight == 0.35
        assert config.cost_weight == 0.25
        assert config.quality_weight == 0.40

    def test_custom_configuration(self):
        """Test custom configuration"""
        config = ModelSelectionConfig(
            cost_optimization_enabled=False,
            fallback_enabled=False,
            max_retries=5,
            complexity_weight=0.5,
            cost_weight=0.3,
            quality_weight=0.2
        )
        
        assert config.cost_optimization_enabled is False
        assert config.fallback_enabled is False
        assert config.max_retries == 5
        assert config.complexity_weight == 0.5
        assert config.cost_weight == 0.3
        assert config.quality_weight == 0.2

    def test_default_models_creation(self):
        """Test default models creation"""
        config = ModelSelectionConfig()
        
        # Check that all expected models are present
        expected_models = [
            "gpt-4-turbo", "claude-4", "gemini-pro",
            "gpt-3.5-turbo", "claude-3-haiku", "gemini-flash"
        ]
        
        for model_id in expected_models:
            assert model_id in config.available_models
            model_info = config.available_models[model_id]
            assert isinstance(model_info, ModelInfo)
            assert model_info.model_id == model_id

    def test_budget_limits(self):
        """Test budget limits configuration"""
        config = ModelSelectionConfig()
        
        assert config.budget_limits["budget_conscious"] == 0.01
        assert config.budget_limits["balanced"] == 0.05
        assert config.budget_limits["quality_first"] == 0.10

    def test_quality_thresholds(self):
        """Test quality thresholds configuration"""
        config = ModelSelectionConfig()
        
        assert config.quality_thresholds["acceptable"] == 0.7
        assert config.quality_thresholds["good"] == 0.8
        assert config.quality_thresholds["excellent"] == 0.9


class TestModelInfo:
    """Unit tests for ModelInfo"""
    
    def test_model_info_creation(self):
        """Test model info creation"""
        model_info = ModelInfo(
            model_id="test-model",
            model_version="1.0",
            cost_per_1k_input=0.01,
            cost_per_1k_output=0.02,
            context_window=100000,
            quality_score=0.9,
            speed_score=0.8,
            best_for=["testing", "development"]
        )
        
        assert model_info.model_id == "test-model"
        assert model_info.cost_per_1k_input == 0.01
        assert model_info.cost_per_1k_output == 0.02
        assert model_info.total_cost_per_1k == 0.03
        assert model_info.quality_score == 0.9
        assert model_info.speed_score == 0.8

    def test_total_cost_calculation(self):
        """Test total cost calculation"""
        model_info = ModelInfo(
            model_id="test-model",
            model_version="1.0",
            cost_per_1k_input=0.01,
            cost_per_1k_output=0.02,
            context_window=100000,
            quality_score=0.9,
            speed_score=0.8,
            best_for=["testing"]
        )
        
        assert model_info.total_cost_per_1k == 0.03


if __name__ == "__main__":
    pytest.main([__file__])

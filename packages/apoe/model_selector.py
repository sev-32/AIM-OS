"""
ModelSelector Component for Cross-Model Consciousness

This component intelligently selects optimal model combinations based on task complexity,
cost constraints, and quality requirements to achieve 90-99% cost reduction while
maintaining quality through proper model pairing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import uuid
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class CostConstraint(Enum):
    """Cost constraint categories"""
    BUDGET_CONSCIOUS = "budget_conscious"
    BALANCED = "balanced"
    QUALITY_FIRST = "quality_first"


class QualityRequirement(Enum):
    """Quality requirement categories"""
    ACCEPTABLE = "acceptable"
    GOOD = "good"
    EXCELLENT = "excellent"


class ModelStrategy(Enum):
    """Model selection strategies"""
    SINGLE_MODEL = "single_model"
    CROSS_MODEL = "cross_model"


@dataclass
class ModelInfo:
    """Information about an AI model"""
    model_id: str
    model_version: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    context_window: int
    quality_score: float
    speed_score: float
    best_for: List[str]
    
    @property
    def total_cost_per_1k(self) -> float:
        """Calculate total cost per 1k tokens (input + output)"""
        return self.cost_per_1k_input + self.cost_per_1k_output


@dataclass
class TaskInput:
    """Input for task analysis"""
    problem_description: str
    context: str
    constraints: List[str] = field(default_factory=list)
    goal: str = ""
    budget_limit: Optional[float] = None
    quality_requirement: Optional[str] = None
    context_size: Optional[int] = None


@dataclass
class ModelSelection:
    """Result of model selection"""
    selection_id: str = field(default_factory=lambda: f"selection_{uuid.uuid4().hex}")
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Selection details
    strategy: ModelStrategy = ModelStrategy.SINGLE_MODEL
    smart_model: Optional[str] = None
    execution_model: str = "gpt-3.5-turbo"
    
    # Analysis results
    task_complexity: float = 0.0
    cost_constraint: CostConstraint = CostConstraint.BALANCED
    quality_requirement: QualityRequirement = QualityRequirement.GOOD
    
    # Cost and quality estimates
    estimated_cost: float = 0.0
    cost_reduction_percentage: float = 0.0
    expected_quality_score: float = 0.0
    
    # Confidence and reasoning
    confidence: float = 0.0
    reasoning: str = ""
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelSelectionConfig:
    """Configuration for model selection"""
    # Model registry
    available_models: Dict[str, ModelInfo] = field(default_factory=dict)
    
    # Cost constraints
    budget_limits: Dict[str, float] = field(default_factory=lambda: {
        "budget_conscious": 0.01,
        "balanced": 0.05,
        "quality_first": 0.10
    })
    
    # Cost optimization
    cost_optimization_enabled: bool = True
    
    # Quality requirements
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "acceptable": 0.7,
        "good": 0.8,
        "excellent": 0.9,
        "minimum": 0.8
    })
    
    # Selection criteria weights
    complexity_weight: float = 0.35
    cost_weight: float = 0.25
    quality_weight: float = 0.40
    
    # Fallback strategies
    fallback_enabled: bool = True
    max_retries: int = 3
    
    def __post_init__(self):
        """Initialize default models if not provided"""
        if not self.available_models:
            self.available_models = self._get_default_models()
    
    def _get_default_models(self) -> Dict[str, ModelInfo]:
        """Get default model configurations"""
        return {
            # Smart Models (Insight Generation)
            "gpt-4-turbo": ModelInfo(
                model_id="gpt-4-turbo",
                model_version="1.0",
                cost_per_1k_input=0.01,
                cost_per_1k_output=0.03,
                context_window=128000,
                quality_score=0.95,
                speed_score=0.7,
                best_for=["complex_reasoning", "architecture_design", "high_stakes_tasks"]
            ),
            "claude-4": ModelInfo(
                model_id="claude-4",
                model_version="1.0",
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                context_window=200000,
                quality_score=0.92,
                speed_score=0.8,
                best_for=["analysis_tasks", "ethical_reasoning", "long_context"]
            ),
            "gemini-pro": ModelInfo(
                model_id="gemini-pro",
                model_version="1.0",
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                context_window=1000000,
                quality_score=0.80,
                speed_score=0.8,
                best_for=["large_context", "cost_sensitive", "high_volume"]
            ),
            
            # Execution Models (Implementation)
            "gpt-3.5-turbo": ModelInfo(
                model_id="gpt-3.5-turbo",
                model_version="1.0",
                cost_per_1k_input=0.0005,
                cost_per_1k_output=0.0015,
                context_window=16000,
                quality_score=0.75,
                speed_score=0.9,
                best_for=["fast_execution", "routine_tasks", "high_volume"]
            ),
            "claude-3-haiku": ModelInfo(
                model_id="claude-3-haiku",
                model_version="1.0",
                cost_per_1k_input=0.00025,
                cost_per_1k_output=0.00125,
                context_window=200000,
                quality_score=0.78,
                speed_score=0.95,
                best_for=["fast_execution", "large_context", "cost_sensitive"]
            ),
            "gemini-flash": ModelInfo(
                model_id="gemini-flash",
                model_version="1.0",
                cost_per_1k_input=0.000075,
                cost_per_1k_output=0.0003,
                context_window=1000000,
                quality_score=0.70,
                speed_score=0.98,
                best_for=["ultra_fast_execution", "high_volume", "cost_critical"]
            )
        }


class ComplexityAnalyzer:
    """Analyze task complexity"""
    
    def analyze(self, task_input: TaskInput) -> float:
        """
        Analyze task complexity and return score (0.0-1.0)
        
        Args:
            task_input: Task input to analyze
            
        Returns:
            Complexity score between 0.0 and 1.0
        """
        try:
            # Analyze problem novelty
            novelty = self._analyze_novelty(task_input)
            
            # Analyze context size
            context_size = self._analyze_context_size(task_input)
            
            # Analyze reasoning depth
            reasoning_depth = self._analyze_reasoning_depth(task_input)
            
            # Analyze error cost
            error_cost = self._analyze_error_cost(task_input)
            
            # Calculate weighted complexity
            complexity = (
                0.20 * novelty +
                0.15 * context_size +
                0.35 * reasoning_depth +
                0.30 * error_cost
            )
            
            logger.info(f"Complexity analysis: novelty={novelty:.2f}, "
                       f"context_size={context_size:.2f}, reasoning_depth={reasoning_depth:.2f}, "
                       f"error_cost={error_cost:.2f}, total={complexity:.2f}")
            
            return min(max(complexity, 0.0), 1.0)  # Clamp to [0.0, 1.0]
            
        except Exception as e:
            logger.error(f"Error analyzing complexity: {e}")
            return 0.5  # Default to medium complexity
    
    def _analyze_novelty(self, task_input: TaskInput) -> float:
        """Analyze problem novelty (0.0-1.0)"""
        description = task_input.problem_description.lower()
        
        # High novelty indicators
        if any(keyword in description for keyword in [
            "design", "architecture", "novel", "new", "innovative", "research"
        ]):
            return 0.9
        
        # Medium novelty indicators
        if any(keyword in description for keyword in [
            "implement", "build", "create", "develop", "optimize"
        ]):
            return 0.6
        
        # Low novelty indicators
        if any(keyword in description for keyword in [
            "format", "fix", "update", "modify", "refactor"
        ]):
            return 0.3
        
        return 0.5  # Default medium novelty
    
    def _analyze_context_size(self, task_input: TaskInput) -> float:
        """Analyze context size (0.0-1.0)"""
        context_length = len(task_input.context)
        
        if context_length < 1000:
            return 0.2
        elif context_length < 10000:
            return 0.5
        elif context_length < 50000:
            return 0.7
        else:
            return 0.9
    
    def _analyze_reasoning_depth(self, task_input: TaskInput) -> float:
        """Analyze reasoning depth (0.0-1.0)"""
        description = task_input.problem_description.lower()
        constraints = [c.lower() for c in task_input.constraints]
        
        # Deep reasoning indicators
        if any(keyword in description for keyword in [
            "analyze", "reason", "decide", "choose", "evaluate"
        ]) or len(constraints) > 3:
            return 0.9
        
        # Medium reasoning indicators
        if any(keyword in description for keyword in [
            "implement", "build", "create", "develop"
        ]) or len(constraints) > 1:
            return 0.6
        
        # Single-step indicators
        if any(keyword in description for keyword in [
            "format", "fix", "update", "modify"
        ]):
            return 0.3
        
        return 0.5
    
    def _analyze_error_cost(self, task_input: TaskInput) -> float:
        """Analyze error cost (0.0-1.0)"""
        description = task_input.problem_description.lower()
        constraints = [c.lower() for c in task_input.constraints]
        
        # High error cost indicators
        if any(keyword in description for keyword in [
            "security", "authentication", "payment", "critical", "production"
        ]) or any(keyword in constraints for keyword in [
            "secure", "critical", "production", "high-stakes"
        ]):
            return 0.9
        
        # Medium error cost indicators
        if any(keyword in description for keyword in [
            "api", "database", "performance", "scalable"
        ]) or any(keyword in constraints for keyword in [
            "performance", "scalable", "reliable"
        ]):
            return 0.6
        
        # Low error cost indicators
        if any(keyword in description for keyword in [
            "format", "documentation", "test", "prototype"
        ]):
            return 0.3
        
        return 0.5


class CostCalculator:
    """Calculate costs for model selection"""
    
    def __init__(self, config: ModelSelectionConfig):
        self.config = config
    
    def calculate_constraint(self, task_input: TaskInput) -> CostConstraint:
        """Calculate cost constraint based on task input"""
        try:
            # Check explicit budget limit
            if task_input.budget_limit is not None:
                if task_input.budget_limit <= 0.01:
                    return CostConstraint.BUDGET_CONSCIOUS
                elif task_input.budget_limit <= 0.05:
                    return CostConstraint.BALANCED
                else:
                    return CostConstraint.QUALITY_FIRST
            
            # Check context size for cost estimation
            context_size = task_input.context_size or len(task_input.context)
            
            if context_size > 50000:
                return CostConstraint.BUDGET_CONSCIOUS
            elif context_size > 10000:
                return CostConstraint.BALANCED
            else:
                return CostConstraint.QUALITY_FIRST
                
        except Exception as e:
            logger.error(f"Error calculating cost constraint: {e}")
            return CostConstraint.BALANCED
    
    def calculate_cost(self, task_input: TaskInput, model_selection: ModelSelection) -> float:
        """Calculate estimated cost for model selection"""
        try:
            context_size = task_input.context_size or len(task_input.context)
            estimated_output_size = min(context_size // 10, 5000)  # Estimate output size
            
            total_cost = 0.0
            
            # Calculate smart model cost if applicable
            if model_selection.smart_model and model_selection.strategy == ModelStrategy.CROSS_MODEL:
                smart_model_info = self.config.available_models.get(model_selection.smart_model)
                if smart_model_info:
                    # Minimal context for smart model
                    minimal_context_size = min(context_size // 10, 3000)
                    smart_cost = (
                        (minimal_context_size / 1000) * smart_model_info.cost_per_1k_input +
                        (estimated_output_size / 1000) * smart_model_info.cost_per_1k_output
                    )
                    total_cost += smart_cost
            
            # Calculate execution model cost
            execution_model_info = self.config.available_models.get(model_selection.execution_model)
            if execution_model_info:
                execution_cost = (
                    (context_size / 1000) * execution_model_info.cost_per_1k_input +
                    (estimated_output_size / 1000) * execution_model_info.cost_per_1k_output
                )
                total_cost += execution_cost
            
            return total_cost
            
        except Exception as e:
            logger.error(f"Error calculating cost: {e}")
            return 0.05  # Default cost estimate


class QualityAssessor:
    """Assess quality requirements"""
    
    def assess(self, task_input: TaskInput) -> QualityRequirement:
        """Assess quality requirement based on task input"""
        try:
            # Check explicit quality requirement
            if task_input.quality_requirement:
                return QualityRequirement(task_input.quality_requirement.lower())
            
            # Assess based on task characteristics
            description = task_input.problem_description.lower()
            constraints = [c.lower() for c in task_input.constraints]
            
            # Excellent quality indicators
            if any(keyword in description for keyword in [
                "security", "authentication", "payment", "critical", "production"
            ]) or any(keyword in constraints for keyword in [
                "secure", "critical", "production", "high-quality"
            ]):
                return QualityRequirement.EXCELLENT
            
            # Good quality indicators
            if any(keyword in description for keyword in [
                "api", "database", "performance", "scalable", "user-facing"
            ]) or any(keyword in constraints for keyword in [
                "performance", "scalable", "reliable", "user-friendly"
            ]):
                return QualityRequirement.GOOD
            
            # Acceptable quality indicators
            if any(keyword in description for keyword in [
                "format", "documentation", "test", "prototype", "internal"
            ]):
                return QualityRequirement.ACCEPTABLE
            
            return QualityRequirement.GOOD  # Default to good quality
            
        except Exception as e:
            logger.error(f"Error assessing quality: {e}")
            return QualityRequirement.GOOD


class ModelSelector:
    """Intelligent model selection for cross-model consciousness"""
    
    def __init__(self, config: ModelSelectionConfig):
        self.config = config
        self.complexity_analyzer = ComplexityAnalyzer()
        self.cost_calculator = CostCalculator(config)
        self.quality_assessor = QualityAssessor()
        
        logger.info("ModelSelector initialized with configuration")
    
    def select_models(self, task_input: TaskInput) -> ModelSelection:
        """
        Select optimal model combination for task
        
        Args:
            task_input: Task input to analyze
            
        Returns:
            Model selection result
        """
        try:
            logger.info(f"Selecting models for task: {task_input.problem_description[:50]}...")
            
            # Analyze task complexity
            complexity = self.complexity_analyzer.analyze(task_input)
            
            # Calculate cost constraints
            cost_constraint = self.cost_calculator.calculate_constraint(task_input)
            
            # Assess quality requirements
            quality_requirement = self.quality_assessor.assess(task_input)
            
            # Select optimal combination
            selection = self._select_combination(complexity, cost_constraint, quality_requirement)
            
            # Calculate cost estimates
            selection.estimated_cost = self.cost_calculator.calculate_cost(task_input, selection)
            selection.cost_reduction_percentage = self._calculate_cost_reduction(selection)
            
            # Calculate quality estimates
            selection.expected_quality_score = self._calculate_expected_quality(selection)
            
            # Calculate confidence
            selection.confidence = self._calculate_confidence(selection)
            
            # Generate reasoning
            selection.reasoning = self._generate_reasoning(selection)
            
            logger.info(f"Model selection completed: strategy={selection.strategy.value}, "
                       f"cost_reduction={selection.cost_reduction_percentage:.1f}%, "
                       f"quality={selection.expected_quality_score:.2f}")
            
            return selection
            
        except Exception as e:
            logger.error(f"Error selecting models: {e}")
            return self._get_fallback_selection()
    
    def _select_combination(self, complexity: float, cost_constraint: CostConstraint, 
                          quality_requirement: QualityRequirement) -> ModelSelection:
        """Select model combination based on criteria"""
        
        # Low complexity tasks use execution model only
        if complexity < 0.3:
            return ModelSelection(
                strategy=ModelStrategy.SINGLE_MODEL,
                execution_model="gpt-3.5-turbo",
                task_complexity=complexity,
                cost_constraint=cost_constraint,
                quality_requirement=quality_requirement
            )
        
        # High complexity tasks always use smart models
        if complexity > 0.7:
            if quality_requirement == QualityRequirement.EXCELLENT:
                return ModelSelection(
                    strategy=ModelStrategy.CROSS_MODEL,
                    smart_model="gpt-4-turbo",
                    execution_model="claude-3-haiku",
                    task_complexity=complexity,
                    cost_constraint=cost_constraint,
                    quality_requirement=quality_requirement
                )
            elif quality_requirement == QualityRequirement.GOOD:
                return ModelSelection(
                    strategy=ModelStrategy.CROSS_MODEL,
                    smart_model="claude-4",
                    execution_model="gpt-3.5-turbo",
                    task_complexity=complexity,
                    cost_constraint=cost_constraint,
                    quality_requirement=quality_requirement
                )
            else:  # acceptable
                return ModelSelection(
                    strategy=ModelStrategy.CROSS_MODEL,
                    smart_model="gemini-pro",
                    execution_model="gemini-flash",
                    task_complexity=complexity,
                    cost_constraint=cost_constraint,
                    quality_requirement=quality_requirement
                )
        
        # Medium complexity tasks based on constraints
        if cost_constraint == CostConstraint.BUDGET_CONSCIOUS:
            if quality_requirement == QualityRequirement.EXCELLENT:
                return ModelSelection(
                    strategy=ModelStrategy.CROSS_MODEL,
                    smart_model="gpt-4-turbo",
                    execution_model="claude-3-haiku",
                    task_complexity=complexity,
                    cost_constraint=cost_constraint,
                    quality_requirement=quality_requirement
                )
            elif quality_requirement == QualityRequirement.GOOD:
                return ModelSelection(
                    strategy=ModelStrategy.CROSS_MODEL,
                    smart_model="claude-4",
                    execution_model="gpt-3.5-turbo",
                    task_complexity=complexity,
                    cost_constraint=cost_constraint,
                    quality_requirement=quality_requirement
                )
            else:  # acceptable
                return ModelSelection(
                    strategy=ModelStrategy.CROSS_MODEL,
                    smart_model="gemini-pro",
                    execution_model="gemini-flash",
                    task_complexity=complexity,
                    cost_constraint=cost_constraint,
                    quality_requirement=quality_requirement
                )
        
        elif cost_constraint == CostConstraint.BALANCED:
            return ModelSelection(
                strategy=ModelStrategy.CROSS_MODEL,
                smart_model="claude-4",
                execution_model="gpt-3.5-turbo",
                task_complexity=complexity,
                cost_constraint=cost_constraint,
                quality_requirement=quality_requirement
            )
        
        else:  # quality_first
            return ModelSelection(
                strategy=ModelStrategy.CROSS_MODEL,
                smart_model="gpt-4-turbo",
                execution_model="claude-3-haiku",
                task_complexity=complexity,
                cost_constraint=cost_constraint,
                quality_requirement=quality_requirement
            )
    
    def _calculate_cost_reduction(self, selection: ModelSelection) -> float:
        """Calculate cost reduction percentage"""
        try:
            if selection.strategy == ModelStrategy.SINGLE_MODEL:
                return 0.0  # No cost reduction for single model
            
            # Calculate baseline cost (using smart model only)
            smart_model_info = self.config.available_models.get(selection.smart_model)
            if not smart_model_info:
                return 0.0
            
            baseline_cost = smart_model_info.total_cost_per_1k
            
            # Calculate optimized cost
            optimized_cost = selection.estimated_cost
            
            if baseline_cost > 0:
                reduction = ((baseline_cost - optimized_cost) / baseline_cost) * 100
                return max(0.0, min(100.0, reduction))
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating cost reduction: {e}")
            return 0.0
    
    def _calculate_expected_quality(self, selection: ModelSelection) -> float:
        """Calculate expected quality score"""
        try:
            if selection.strategy == ModelStrategy.SINGLE_MODEL:
                execution_model_info = self.config.available_models.get(selection.execution_model)
                return execution_model_info.quality_score if execution_model_info else 0.7
            
            # For cross-model, use weighted average
            smart_model_info = self.config.available_models.get(selection.smart_model)
            execution_model_info = self.config.available_models.get(selection.execution_model)
            
            if smart_model_info and execution_model_info:
                # Weight smart model quality more heavily for insights
                return (smart_model_info.quality_score * 0.6 + 
                       execution_model_info.quality_score * 0.4)
            
            return 0.8  # Default quality
            
        except Exception as e:
            logger.error(f"Error calculating expected quality: {e}")
            return 0.8
    
    def _calculate_confidence(self, selection: ModelSelection) -> float:
        """Calculate confidence in selection"""
        try:
            confidence = 0.8  # Base confidence
            
            # Adjust based on complexity
            if selection.task_complexity > 0.7:
                confidence += 0.1  # High complexity tasks benefit more from cross-model
            
            # Adjust based on cost constraint
            if selection.cost_constraint == CostConstraint.BALANCED:
                confidence += 0.05  # Balanced approach is well-tested
            
            # Adjust based on quality requirement
            if selection.quality_requirement == QualityRequirement.GOOD:
                confidence += 0.05  # Good quality is achievable
            
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.8
    
    def _generate_reasoning(self, selection: ModelSelection) -> str:
        """Generate reasoning for selection"""
        try:
            reasoning_parts = []
            
            # Strategy reasoning
            if selection.strategy == ModelStrategy.SINGLE_MODEL:
                reasoning_parts.append(f"Using single model strategy for low complexity task "
                                     f"(complexity: {selection.task_complexity:.2f})")
            else:
                reasoning_parts.append(f"Using cross-model strategy for complex task "
                                     f"(complexity: {selection.task_complexity:.2f})")
            
            # Model selection reasoning
            if selection.smart_model:
                reasoning_parts.append(f"Selected {selection.smart_model} for insights based on "
                                     f"{selection.cost_constraint.value} cost constraint and "
                                     f"{selection.quality_requirement.value} quality requirement")
            
            reasoning_parts.append(f"Selected {selection.execution_model} for execution")
            
            # Cost and quality reasoning
            reasoning_parts.append(f"Expected cost reduction: {selection.cost_reduction_percentage:.1f}%")
            reasoning_parts.append(f"Expected quality score: {selection.expected_quality_score:.2f}")
            
            return ". ".join(reasoning_parts) + "."
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")
            return "Model selection completed based on task analysis."
    
    def _get_fallback_selection(self) -> ModelSelection:
        """Get fallback selection when primary selection fails"""
        logger.warning("Using fallback model selection")
        
        return ModelSelection(
            strategy=ModelStrategy.SINGLE_MODEL,
            execution_model="gpt-3.5-turbo",
            task_complexity=0.5,
            cost_constraint=CostConstraint.BALANCED,
            quality_requirement=QualityRequirement.GOOD,
            confidence=0.7,
            reasoning="Fallback selection due to error in primary selection"
        )


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create model selector
    config = ModelSelectionConfig()
    selector = ModelSelector(config)
    
    # Test task input
    task_input = TaskInput(
        problem_description="Implement secure authentication system",
        context="JWT-based authentication with refresh tokens",
        constraints=["Must support multi-factor authentication", "Must be scalable"],
        goal="Secure, scalable authentication system"
    )
    
    # Select models
    selection = selector.select_models(task_input)
    
    print(f"Model Selection Result:")
    print(f"Strategy: {selection.strategy.value}")
    print(f"Smart Model: {selection.smart_model}")
    print(f"Execution Model: {selection.execution_model}")
    print(f"Cost Reduction: {selection.cost_reduction_percentage:.1f}%")
    print(f"Expected Quality: {selection.expected_quality_score:.2f}")
    print(f"Confidence: {selection.confidence:.2f}")
    print(f"Reasoning: {selection.reasoning}")

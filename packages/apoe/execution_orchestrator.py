"""
ExecutionOrchestrator Component for Cross-Model Consciousness

This component orchestrates the execution of tasks using execution models,
integrating with InsightTransfer to receive prepared context and manage
the execution workflow and results.
"""

from __future__ import annotations

import logging
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import uuid
from datetime import datetime

from apoe.insight_transfer import TransferContext, InsightTransfer
from apoe.model_selector import ModelSelection, TaskInput, ModelStrategy

# Configure logging
logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of task execution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class ExecutionMode(Enum):
    """Mode of task execution"""
    SINGLE_EXECUTION = "single_execution"  # Execute once with single model
    PARALLEL_EXECUTION = "parallel_execution"  # Execute with multiple models in parallel
    SEQUENTIAL_EXECUTION = "sequential_execution"  # Execute with multiple models sequentially
    CONSENSUS_EXECUTION = "consensus_execution"  # Execute with multiple models and reach consensus


class ResultQuality(Enum):
    """Quality of execution result"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    FAILED = "failed"


@dataclass
class ExecutionConfig:
    """Configuration for task execution"""
    # Execution settings
    execution_mode: ExecutionMode = ExecutionMode.SINGLE_EXECUTION
    max_execution_time: int = 300  # seconds
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    
    # Quality thresholds
    min_result_quality: ResultQuality = ResultQuality.ACCEPTABLE
    consensus_threshold: float = 0.8
    quality_validation: bool = True
    
    # Performance settings
    enable_parallel_execution: bool = True
    max_parallel_tasks: int = 3
    execution_timeout: int = 60  # seconds per model
    
    # Result processing
    enable_result_aggregation: bool = True
    enable_result_validation: bool = True
    enable_result_caching: bool = True
    cache_ttl: int = 3600  # seconds


@dataclass
class ExecutionTask:
    """Task to be executed"""
    # Identity
    task_id: str = field(default_factory=lambda: f"task_{uuid.uuid4().hex}")
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Task information
    task_input: TaskInput = field(default_factory=lambda: TaskInput(
        problem_description="Default task",
        context="Default context"
    ))
    transfer_context: Optional[TransferContext] = None
    model_selection: Optional[ModelSelection] = None
    
    # Execution settings
    execution_mode: ExecutionMode = ExecutionMode.SINGLE_EXECUTION
    priority: int = 5  # 1-10, higher is more important
    
    # Status tracking
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_duration: float = 0.0
    
    # Results
    results: List[Dict[str, Any]] = field(default_factory=list)
    final_result: Optional[Dict[str, Any]] = None
    result_quality: ResultQuality = ResultQuality.POOR
    
    # Metadata
    execution_metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    retry_count: int = 0


@dataclass
class ExecutionResult:
    """Result of task execution"""
    # Identity
    result_id: str = field(default_factory=lambda: f"result_{uuid.uuid4().hex}")
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Task information
    task_id: str = ""
    model_id: str = ""
    execution_mode: ExecutionMode = ExecutionMode.SINGLE_EXECUTION
    
    # Result content
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Quality metrics
    quality_score: float = 0.0
    confidence_score: float = 0.0
    completeness_score: float = 0.0
    
    # Performance metrics
    execution_time: float = 0.0
    token_count: int = 0
    cost_estimate: float = 0.0
    
    # Status
    success: bool = False
    error_message: str = ""


class ExecutionEngine:
    """Core execution engine for individual models"""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
    
    def execute_task(self, task: ExecutionTask, model_id: str, transfer_context: TransferContext) -> ExecutionResult:
        """
        Execute a task with a specific model
        
        Args:
            task: Task to execute
            model_id: Model to use for execution
            transfer_context: Prepared context for the model
            
        Returns:
            Execution result
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Executing task {task.task_id} with model {model_id}")
            
            # Prepare execution context
            execution_context = self._prepare_execution_context(task, transfer_context)
            
            # Execute with model (simulated for now)
            result_content = self._execute_with_model(model_id, execution_context)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = ExecutionResult(
                task_id=task.task_id,
                model_id=model_id,
                execution_mode=task.execution_mode,
                content=result_content,
                execution_time=execution_time,
                success=True
            )
            
            # Calculate quality metrics
            self._calculate_quality_metrics(result, execution_context)
            
            logger.info(f"Task {task.task_id} executed successfully in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {e}")
            return ExecutionResult(
                task_id=task.task_id,
                model_id=model_id,
                execution_mode=task.execution_mode,
                success=False,
                error_message=str(e)
            )
    
    def _prepare_execution_context(self, task: ExecutionTask, transfer_context: TransferContext) -> Dict[str, Any]:
        """Prepare execution context for the model"""
        return {
            "task_description": task.task_input.problem_description,
            "constraints": task.task_input.constraints,
            "goal": task.task_input.goal,
            "context": task.task_input.context,
            "transfer_context": {
                "problem_summary": transfer_context.problem_summary,
                "recommended_approach": transfer_context.recommended_approach,
                "key_considerations": transfer_context.key_considerations,
                "potential_risks": transfer_context.potential_risks,
                "success_criteria": transfer_context.success_criteria,
                "execution_guidance": transfer_context.execution_guidance,
                "confidence_score": transfer_context.confidence_score,
                "quality_score": transfer_context.quality_score
            }
        }
    
    def _execute_with_model(self, model_id: str, execution_context: Dict[str, Any]) -> str:
        """Execute task with the specified model (simulated)"""
        # This is a simulation - in a real implementation, this would call the actual model
        task_description = execution_context["task_description"]
        problem_summary = execution_context["transfer_context"]["problem_summary"]
        recommended_approach = execution_context["transfer_context"]["recommended_approach"]
        
        # Simulate model execution based on context
        if "authentication" in task_description.lower():
            return f"""
            Based on the analysis provided, I'll implement the authentication system as follows:
            
            {problem_summary}
            
            Implementation Approach:
            {recommended_approach}
            
            I'll create a JWT-based authentication middleware with the following components:
            1. Token validation service
            2. Refresh token mechanism  
            3. Error handling and logging
            4. Security headers and CORS configuration
            
            The implementation will include proper error handling, logging, and monitoring
            to ensure the system meets the specified success criteria.
            """
        else:
            return f"""
            I'll implement the requested functionality based on the provided analysis:
            
            Problem: {problem_summary}
            Approach: {recommended_approach}
            
            Implementation will follow the recommended approach and address all
            key considerations and potential risks identified in the analysis.
            """
    
    def _calculate_quality_metrics(self, result: ExecutionResult, execution_context: Dict[str, Any]):
        """Calculate quality metrics for the result"""
        try:
            content = result.content
            transfer_context = execution_context["transfer_context"]
            
            # Calculate quality score based on content completeness and relevance
            quality_factors = []
            
            # Completeness factor
            required_elements = ["implementation", "approach", "components"]
            found_elements = sum(1 for element in required_elements if element in content.lower())
            completeness = found_elements / len(required_elements)
            quality_factors.append(completeness * 0.4)
            
            # Relevance factor (how well it addresses the problem)
            problem_keywords = transfer_context["problem_summary"].lower().split()
            content_keywords = content.lower().split()
            relevance = len(set(problem_keywords) & set(content_keywords)) / len(problem_keywords)
            quality_factors.append(relevance * 0.3)
            
            # Structure factor (well-structured response)
            structure_indicators = ["1.", "2.", "3.", "implementation", "approach", "components"]
            structure_score = sum(1 for indicator in structure_indicators if indicator in content.lower()) / len(structure_indicators)
            quality_factors.append(structure_score * 0.3)
            
            result.quality_score = sum(quality_factors)
            result.confidence_score = transfer_context["confidence_score"]
            result.completeness_score = completeness
            
            # Estimate token count and cost
            result.token_count = len(content.split()) * 1.3  # Rough estimate
            result.cost_estimate = result.token_count * 0.0001  # Rough cost estimate
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {e}")
            result.quality_score = 0.5
            result.confidence_score = 0.5
            result.completeness_score = 0.5


class ResultAggregator:
    """Aggregate and validate execution results"""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
    
    def aggregate_results(self, results: List[ExecutionResult]) -> Dict[str, Any]:
        """
        Aggregate multiple execution results
        
        Args:
            results: List of execution results to aggregate
            
        Returns:
            Aggregated result
        """
        try:
            if not results:
                return {"error": "No results to aggregate"}
            
            if len(results) == 1:
                return self._process_single_result(results[0])
            
            # Multiple results - use consensus or best result
            if self.config.execution_mode == ExecutionMode.CONSENSUS_EXECUTION:
                return self._consensus_aggregation(results)
            else:
                return self._best_result_aggregation(results)
                
        except Exception as e:
            logger.error(f"Error aggregating results: {e}")
            return {"error": str(e)}
    
    def _process_single_result(self, result: ExecutionResult) -> Dict[str, Any]:
        """Process a single result"""
        return {
            "content": result.content,
            "quality_score": result.quality_score,
            "confidence_score": result.confidence_score,
            "completeness_score": result.completeness_score,
            "execution_time": result.execution_time,
            "model_id": result.model_id,
            "success": result.success,
            "metadata": result.metadata
        }
    
    def _consensus_aggregation(self, results: List[ExecutionResult]) -> Dict[str, Any]:
        """Aggregate results using consensus approach"""
        try:
            # Filter successful results
            successful_results = [r for r in results if r.success]
            
            if not successful_results:
                return {"error": "No successful results for consensus"}
            
            # Calculate consensus metrics
            avg_quality = sum(r.quality_score for r in successful_results) / len(successful_results)
            avg_confidence = sum(r.confidence_score for r in successful_results) / len(successful_results)
            avg_completeness = sum(r.completeness_score for r in successful_results) / len(successful_results)
            
            # Check if consensus threshold is met
            if avg_quality >= self.config.consensus_threshold:
                # Use the highest quality result
                best_result = max(successful_results, key=lambda r: r.quality_score)
                return {
                    "content": best_result.content,
                    "quality_score": best_result.quality_score,
                    "confidence_score": best_result.confidence_score,
                    "completeness_score": best_result.completeness_score,
                    "execution_time": best_result.execution_time,
                    "model_id": best_result.model_id,
                    "consensus_quality": avg_quality,
                    "consensus_confidence": avg_confidence,
                    "consensus_completeness": avg_completeness,
                    "result_count": len(successful_results),
                    "success": True
                }
            else:
                # Consensus not reached - return aggregated content
                aggregated_content = self._aggregate_content(successful_results)
                return {
                    "content": aggregated_content,
                    "quality_score": avg_quality,
                    "confidence_score": avg_confidence,
                    "completeness_score": avg_completeness,
                    "execution_time": max(r.execution_time for r in successful_results),
                    "model_id": "consensus",
                    "consensus_reached": False,
                    "result_count": len(successful_results),
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"Error in consensus aggregation: {e}")
            return {"error": str(e)}
    
    def _best_result_aggregation(self, results: List[ExecutionResult]) -> Dict[str, Any]:
        """Aggregate results using best result approach"""
        try:
            # Filter successful results
            successful_results = [r for r in results if r.success]
            
            if not successful_results:
                return {"error": "No successful results"}
            
            # Find the best result based on quality score
            best_result = max(successful_results, key=lambda r: r.quality_score)
            
            return {
                "content": best_result.content,
                "quality_score": best_result.quality_score,
                "confidence_score": best_result.confidence_score,
                "completeness_score": best_result.completeness_score,
                "execution_time": best_result.execution_time,
                "model_id": best_result.model_id,
                "result_count": len(successful_results),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in best result aggregation: {e}")
            return {"error": str(e)}
    
    def _aggregate_content(self, results: List[ExecutionResult]) -> str:
        """Aggregate content from multiple results"""
        try:
            # Simple content aggregation - combine the best parts
            content_parts = []
            
            for result in results:
                if result.content:
                    content_parts.append(f"From {result.model_id}:\n{result.content}\n")
            
            return "\n".join(content_parts)
            
        except Exception as e:
            logger.error(f"Error aggregating content: {e}")
            return "Error aggregating content"


class ExecutionOrchestrator:
    """Main execution orchestrator component"""
    
    def __init__(self, config: ExecutionConfig, insight_transfer: InsightTransfer):
        self.config = config
        self.insight_transfer = insight_transfer
        self.execution_engine = ExecutionEngine(config)
        self.result_aggregator = ResultAggregator(config)
        self.execution_cache: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[ExecutionTask] = []
        
        logger.info("ExecutionOrchestrator initialized with configuration")
    
    def execute_task(self, task_input: TaskInput, model_selection: ModelSelection, 
                    transfer_context: TransferContext) -> ExecutionResult:
        """
        Execute a task using the specified model selection and transfer context
        
        Args:
            task_input: Task input
            model_selection: Model selection for execution
            transfer_context: Prepared transfer context
            
        Returns:
            Execution result
        """
        try:
            logger.info(f"Starting task execution for {task_input.problem_description}")
            
            # Create execution task
            task = ExecutionTask(
                task_input=task_input,
                transfer_context=transfer_context,
                model_selection=model_selection,
                execution_mode=self.config.execution_mode
            )
            
            # Check cache first
            cache_key = self._generate_cache_key(task_input, model_selection)
            if self.config.enable_result_caching and cache_key in self.execution_cache:
                cached_result = self.execution_cache[cache_key]
                if self._is_cache_valid(cached_result):
                    logger.info(f"Using cached result for task {task.task_id}")
                    return self._create_result_from_cache(cached_result, task)
            
            # Execute based on mode
            if self.config.execution_mode == ExecutionMode.SINGLE_EXECUTION:
                result = self._execute_single(task, model_selection, transfer_context)
            elif self.config.execution_mode == ExecutionMode.PARALLEL_EXECUTION:
                result = self._execute_parallel(task, model_selection, transfer_context)
            elif self.config.execution_mode == ExecutionMode.SEQUENTIAL_EXECUTION:
                result = self._execute_sequential(task, model_selection, transfer_context)
            elif self.config.execution_mode == ExecutionMode.CONSENSUS_EXECUTION:
                result = self._execute_consensus(task, model_selection, transfer_context)
            else:
                result = self._execute_single(task, model_selection, transfer_context)
            
            # Cache the result
            if self.config.enable_result_caching:
                self.execution_cache[cache_key] = {
                    "result": result,
                    "timestamp": datetime.now(),
                    "task_id": task.task_id
                }
            
            # Update task status
            task.status = ExecutionStatus.COMPLETED
            task.end_time = datetime.now()
            task.execution_duration = (task.end_time - task.start_time).total_seconds()
            task.final_result = result
            
            # Add to history
            self.execution_history.append(task)
            
            logger.info(f"Task execution completed successfully in {task.execution_duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            return ExecutionResult(
                success=False,
                error_message=str(e)
            )
    
    def _execute_single(self, task: ExecutionTask, model_selection: ModelSelection, 
                       transfer_context: TransferContext) -> ExecutionResult:
        """Execute task with single model"""
        try:
            task.status = ExecutionStatus.IN_PROGRESS
            task.start_time = datetime.now()
            
            # Use execution model from selection
            execution_model = model_selection.execution_model
            
            result = self.execution_engine.execute_task(task, execution_model, transfer_context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in single execution: {e}")
            return ExecutionResult(
                success=False,
                error_message=str(e)
            )
    
    def _execute_parallel(self, task: ExecutionTask, model_selection: ModelSelection, 
                         transfer_context: TransferContext) -> ExecutionResult:
        """Execute task with multiple models in parallel"""
        try:
            task.status = ExecutionStatus.IN_PROGRESS
            task.start_time = datetime.now()
            
            # Get available models
            models = [model_selection.execution_model]
            if model_selection.smart_model:
                models.append(model_selection.smart_model)
            
            # Execute with all models (simulated parallel execution)
            results = []
            for model in models:
                result = self.execution_engine.execute_task(task, model, transfer_context)
                results.append(result)
            
            # Aggregate results
            aggregated_result = self.result_aggregator.aggregate_results(results)
            
            # Create final result
            final_result = ExecutionResult(
                task_id=task.task_id,
                execution_mode=ExecutionMode.PARALLEL_EXECUTION,
                content=aggregated_result.get("content", ""),
                quality_score=aggregated_result.get("quality_score", 0.0),
                confidence_score=aggregated_result.get("confidence_score", 0.0),
                completeness_score=aggregated_result.get("completeness_score", 0.0),
                execution_time=aggregated_result.get("execution_time", 0.0),
                model_id=aggregated_result.get("model_id", "parallel"),
                success=aggregated_result.get("success", False),
                metadata=aggregated_result
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in parallel execution: {e}")
            return ExecutionResult(
                success=False,
                error_message=str(e)
            )
    
    def _execute_sequential(self, task: ExecutionTask, model_selection: ModelSelection, 
                           transfer_context: TransferContext) -> ExecutionResult:
        """Execute task with multiple models sequentially"""
        try:
            task.status = ExecutionStatus.IN_PROGRESS
            task.start_time = datetime.now()
            
            # Get available models
            models = [model_selection.execution_model]
            if model_selection.smart_model:
                models.append(model_selection.smart_model)
            
            # Execute with all models sequentially
            results = []
            for model in models:
                result = self.execution_engine.execute_task(task, model, transfer_context)
                results.append(result)
                
                # If we get a good result, we can stop early
                if result.success and result.quality_score >= 0.8:
                    break
            
            # Aggregate results
            aggregated_result = self.result_aggregator.aggregate_results(results)
            
            # Create final result
            final_result = ExecutionResult(
                task_id=task.task_id,
                execution_mode=ExecutionMode.SEQUENTIAL_EXECUTION,
                content=aggregated_result.get("content", ""),
                quality_score=aggregated_result.get("quality_score", 0.0),
                confidence_score=aggregated_result.get("confidence_score", 0.0),
                completeness_score=aggregated_result.get("completeness_score", 0.0),
                execution_time=aggregated_result.get("execution_time", 0.0),
                model_id=aggregated_result.get("model_id", "sequential"),
                success=aggregated_result.get("success", False),
                metadata=aggregated_result
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in sequential execution: {e}")
            return ExecutionResult(
                success=False,
                error_message=str(e)
            )
    
    def _execute_consensus(self, task: ExecutionTask, model_selection: ModelSelection, 
                          transfer_context: TransferContext) -> ExecutionResult:
        """Execute task with multiple models and reach consensus"""
        try:
            task.status = ExecutionStatus.IN_PROGRESS
            task.start_time = datetime.now()
            
            # Get available models
            models = [model_selection.execution_model]
            if model_selection.smart_model:
                models.append(model_selection.smart_model)
            
            # Execute with all models
            results = []
            for model in models:
                result = self.execution_engine.execute_task(task, model, transfer_context)
                results.append(result)
            
            # Aggregate results using consensus
            aggregated_result = self.result_aggregator.aggregate_results(results)
            
            # Create final result
            final_result = ExecutionResult(
                task_id=task.task_id,
                execution_mode=ExecutionMode.CONSENSUS_EXECUTION,
                content=aggregated_result.get("content", ""),
                quality_score=aggregated_result.get("quality_score", 0.0),
                confidence_score=aggregated_result.get("confidence_score", 0.0),
                completeness_score=aggregated_result.get("completeness_score", 0.0),
                execution_time=aggregated_result.get("execution_time", 0.0),
                model_id=aggregated_result.get("model_id", "consensus"),
                success=aggregated_result.get("success", False),
                metadata=aggregated_result
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in consensus execution: {e}")
            return ExecutionResult(
                success=False,
                error_message=str(e)
            )
    
    def _generate_cache_key(self, task_input: TaskInput, model_selection: ModelSelection) -> str:
        """Generate cache key for task execution"""
        return f"{task_input.problem_description}_{model_selection.execution_model}_{self.config.execution_mode.value}"
    
    def _is_cache_valid(self, cached_result: Dict[str, Any]) -> bool:
        """Check if cached result is still valid"""
        if not self.config.enable_result_caching:
            return False
        
        age = (datetime.now() - cached_result["timestamp"]).total_seconds()
        return age < self.config.cache_ttl
    
    def _create_result_from_cache(self, cached_result: Dict[str, Any], task: ExecutionTask) -> ExecutionResult:
        """Create result from cached data"""
        cached_data = cached_result["result"]
        
        # If cached_data is already an ExecutionResult, return it with updated task_id
        if isinstance(cached_data, ExecutionResult):
            cached_data.task_id = task.task_id
            return cached_data
        
        # If cached_data is a dictionary, create ExecutionResult from it
        return ExecutionResult(
            task_id=task.task_id,
            content=cached_data.get("content", ""),
            quality_score=cached_data.get("quality_score", 0.0),
            confidence_score=cached_data.get("confidence_score", 0.0),
            completeness_score=cached_data.get("completeness_score", 0.0),
            execution_time=cached_data.get("execution_time", 0.0),
            model_id=cached_data.get("model_id", "cached"),
            success=cached_data.get("success", False),
            metadata=cached_data.get("metadata", {})
        )
    
    def get_execution_history(self, limit: int = 100) -> List[ExecutionTask]:
        """Get execution history"""
        return self.execution_history[-limit:]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.execution_cache),
            "cache_enabled": self.config.enable_result_caching,
            "cache_ttl": self.config.cache_ttl,
            "execution_history_size": len(self.execution_history)
        }
    
    def clear_cache(self):
        """Clear execution cache"""
        self.execution_cache.clear()
        logger.info("Execution cache cleared")


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create execution orchestrator
    config = ExecutionConfig(
        execution_mode=ExecutionMode.SINGLE_EXECUTION,
        enable_result_caching=True,
        quality_validation=True
    )
    
    # Create mock insight transfer
    from apoe.insight_transfer import InsightTransfer, InsightTransferConfig
    insight_transfer = InsightTransfer(InsightTransferConfig())
    
    orchestrator = ExecutionOrchestrator(config, insight_transfer)
    
    # Test task input
    task_input = TaskInput(
        problem_description="Implement authentication system",
        context="JWT authentication system",
        constraints=["security", "performance"],
        goal="Secure authentication"
    )
    
    # Test model selection
    model_selection = ModelSelection(
        execution_model="gpt-4o-mini",
        smart_model="claude-4",
        strategy=ModelStrategy.SINGLE_MODEL
    )
    
    # Test transfer context
    from apoe.insight_transfer import TransferContext
    transfer_context = TransferContext(
        problem_summary="Authentication system needs JWT implementation",
        recommended_approach="Implement JWT middleware with validation",
        key_considerations=["Security", "Performance"],
        confidence_score=0.9
    )
    
    # Test execution
    result = orchestrator.execute_task(task_input, model_selection, transfer_context)
    
    print(f"Execution Result:")
    print(f"Success: {result.success}")
    print(f"Quality Score: {result.quality_score:.2f}")
    print(f"Confidence Score: {result.confidence_score:.2f}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    print(f"Content: {result.content[:200]}...")

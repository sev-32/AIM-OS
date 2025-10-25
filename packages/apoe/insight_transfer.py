"""
InsightTransfer Component for Cross-Model Consciousness

This component handles the transfer of insights from smart models to execution models,
managing the knowledge transfer process, context preparation, and integration.
"""

from __future__ import annotations

import logging
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import uuid
from datetime import datetime

from apoe.insight_extractor import CrossModelInsight, InsightExtractionConfig
from apoe.model_selector import ModelSelection, ModelStrategy, TaskInput

# Configure logging
logger = logging.getLogger(__name__)


class TransferStatus(Enum):
    """Status of insight transfer"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class TransferMode(Enum):
    """Mode of insight transfer"""
    IMMEDIATE = "immediate"  # Transfer immediately after extraction
    BATCH = "batch"  # Batch multiple insights for transfer
    ON_DEMAND = "on_demand"  # Transfer when requested by execution model


class ContextFormat(Enum):
    """Format for context preparation"""
    MINIMAL = "minimal"  # Minimal context with key insights
    STRUCTURED = "structured"  # Structured context with full metadata
    ENRICHED = "enriched"  # Enriched context with additional details


@dataclass
class InsightTransferConfig:
    """Configuration for insight transfer"""
    # Transfer settings
    transfer_mode: TransferMode = TransferMode.IMMEDIATE
    context_format: ContextFormat = ContextFormat.STRUCTURED
    max_transfer_retries: int = 3
    transfer_timeout: int = 30  # seconds
    
    # Context preparation
    max_context_length: int = 4000
    include_metadata: bool = True
    include_confidence: bool = True
    include_reasoning: bool = True
    
    # Quality thresholds
    min_confidence_threshold: float = 0.7
    min_quality_threshold: float = 0.8
    min_completeness_threshold: float = 0.8
    
    # Transfer optimization
    enable_compression: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600  # seconds


@dataclass
class TransferContext:
    """Context prepared for execution model"""
    # Identity
    context_id: str = field(default_factory=lambda: f"context_{uuid.uuid4().hex}")
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Source information
    source_insight_id: str = ""
    source_model: str = ""
    transfer_mode: TransferMode = TransferMode.IMMEDIATE
    
    # Context content
    problem_summary: str = ""
    recommended_approach: str = ""
    key_considerations: List[str] = field(default_factory=list)
    potential_risks: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    
    # Metadata
    confidence_score: float = 0.0
    quality_score: float = 0.0
    completeness_score: float = 0.0
    complexity_score: float = 0.0
    estimated_effort: str = "medium"
    
    # Transfer information
    transfer_metadata: Dict[str, Any] = field(default_factory=dict)
    execution_guidance: str = ""
    
    # Raw data
    raw_insight: str = ""
    context_format: ContextFormat = ContextFormat.STRUCTURED


@dataclass
class TransferResult:
    """Result of insight transfer"""
    # Identity
    transfer_id: str = field(default_factory=lambda: f"transfer_{uuid.uuid4().hex}")
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Transfer information
    source_insight_id: str = ""
    target_model: str = ""
    transfer_status: TransferStatus = TransferStatus.PENDING
    
    # Results
    success: bool = False
    context_prepared: bool = False
    transfer_duration: float = 0.0  # seconds
    
    # Quality metrics
    context_quality: float = 0.0
    transfer_efficiency: float = 0.0
    
    # Error information
    error_message: str = ""
    retry_count: int = 0
    
    # Metadata
    transfer_metadata: Dict[str, Any] = field(default_factory=dict)


class ContextPreparer:
    """Prepare context for execution models"""
    
    def __init__(self, config: InsightTransferConfig):
        self.config = config
    
    def prepare_context(self, insight: CrossModelInsight, target_model: str) -> TransferContext:
        """
        Prepare context for execution model
        
        Args:
            insight: Insight to transfer
            target_model: Target execution model identifier
            
        Returns:
            Prepared transfer context
        """
        try:
            logger.info(f"Preparing context for {target_model} from insight {insight.insight_id}")
            
            # Create base context
            context_label = TransferContext(
                source_insight_id=insight.insight_id,
                source_model=insight.source_model,
                transfer_mode=self.config.transfer_mode,
                context_format=self.config.context_format
            )
            
            # Prepare content based on format
            if self.config.context_format == ContextFormat.MINIMAL:
                self._prepare_minimal_context(context_label, insight)
            elif self.config.context_format == ContextFormat.STRUCTURED:
                self._prepare_structured_context(context_label, insight)
            else:  # ENRICHED
                self._prepare_enriched_context(context_label, insight)
            
            # Add metadata if requested
            if self.config.include_metadata:
                self._add_metadata(context_label, insight)
            
            # Add execution guidance
            self._add_execution_guidance(context_label, insight)
            
            # Validate context length
            self._validate_context_length(context_label)
            
            logger.info(f"Context prepared successfully: {len(context_label.problem_summary)} characters")
            return context_label
            
        except Exception as e:
            logger.error(f"Error preparing context: {e}")
            return self._create_error_context(insight, target_model, str(e))
    
    def _prepare_minimal_context(self, context_label: TransferContext, insight: CrossModelInsight):
        """Prepare minimal context"""
        context_label.problem_summary = insight.problem_analysis[:200] + "..." if len(insight.problem_analysis) > 200 else insight.problem_analysis
        context_label.recommended_approach = insight.recommended_approach[:200] + "..." if len(insight.recommended_approach) > 200 else insight.recommended_approach
        context_label.key_considerations = insight.key_considerations[:3]  # Top 3 considerations
        context_label.potential_risks = insight.potential_risks[:2]  # Top 2 risks
        context_label.success_criteria = insight.success_criteria[:2]  # Top 2 criteria
    
    def _prepare_structured_context(self, context_label: TransferContext, insight: CrossModelInsight):
        """Prepare structured context"""
        context_label.problem_summary = insight.problem_analysis
        context_label.recommended_approach = insight.recommended_approach
        context_label.key_considerations = insight.key_considerations
        context_label.potential_risks = insight.potential_risks
        context_label.success_criteria = insight.success_criteria
    
    def _prepare_enriched_context(self, context_label: TransferContext, insight: CrossModelInsight):
        """Prepare enriched context"""
        # Start with structured context
        self._prepare_structured_context(context_label, insight)
        
        # Add additional details
        context_label.transfer_metadata = {
            "insight_version": insight.version,
            "source_confidence": insight.source_confidence,
            "source_reasoning": insight.source_reasoning,
            "parsing_strategy": insight.parsing_metadata.get("strategy", "unknown"),
            "validation_checks": insight.validation_checks,
            "complexity_analysis": {
                "complexity_score": insight.complexity_score,
                "estimated_effort": insight.estimated_effort
            }
        }
    
    def _add_metadata(self, context_label: TransferContext, insight: CrossModelInsight):
        """Add metadata to context"""
        if self.config.include_confidence:
            context_label.confidence_score = insight.source_confidence
        if self.config.include_metadata:
            context_label.quality_score = insight.quality_score
            context_label.completeness_score = insight.completeness_score
        
        context_label.complexity_score = insight.complexity_score
        context_label.estimated_effort = insight.estimated_effort
    
    def _add_execution_guidance(self, context_label: TransferContext, insight: CrossModelInsight):
        """Add execution guidance"""
        guidance_parts = []
        
        # Add approach guidance
        if insight.recommended_approach:
            guidance_parts.append(f"Recommended Approach: {insight.recommended_approach}")
        
        # Add consideration guidance
        if insight.key_considerations:
            guidance_parts.append(f"Key Considerations: {', '.join(insight.key_considerations)}")
        
        # Add risk guidance
        if insight.potential_risks:
            guidance_parts.append(f"Potential Risks: {', '.join(insight.potential_risks)}")
        
        # Add success criteria guidance
        if insight.success_criteria:
            guidance_parts.append(f"Success Criteria: {', '.join(insight.success_criteria)}")
        
        # Add confidence guidance
        if insight.source_confidence > 0.8:
            guidance_parts.append("High confidence insight - proceed with implementation")
        elif insight.source_confidence > 0.6:
            guidance_parts.append("Medium confidence insight - proceed with caution")
        else:
            guidance_parts.append("Low confidence insight - validate before implementation")
        
        context_label.execution_guidance = "\n".join(guidance_parts)
    
    def _validate_context_length(self, context_label: TransferContext):
        """Validate and adjust context length"""
        total_length = (len(context_label.problem_summary) + 
                       len(context_label.recommended_approach) + 
                       len(context_label.execution_guidance))
        
        if total_length > self.config.max_context_length:
            # Truncate problem summary if needed
            if len(context_label.problem_summary) > 1000:
                context_label.problem_summary = context_label.problem_summary[:1000] + "..."
            
            # Truncate recommended approach if needed
            if len(context_label.recommended_approach) > 1000:
                context_label.recommended_approach = context_label.recommended_approach[:1000] + "..."
            
            # Truncate execution guidance if needed
            if len(context_label.execution_guidance) > 1000:
                context_label.execution_guidance = context_label.execution_guidance[:1000] + "..."
    
    def _create_error_context(self, insight: CrossModelInsight, target_model: str, error: str) -> TransferContext:
        """Create error context when preparation fails"""
        return TransferContext(
            source_insight_id=insight.insight_id,
            source_model=insight.source_model,
            problem_summary=f"Error preparing context: {error}",
            recommended_approach="Manual review required",
            key_considerations=["Context preparation failed"],
            potential_risks=["Quality cannot be guaranteed"],
            success_criteria=["Manual validation required"],
            transfer_metadata={"error": error}
        )


class TransferManager:
    """Manage insight transfer process"""
    
    def __init__(self, config: InsightTransferConfig):
        self.config = config
        self.context_preparer = ContextPreparer(config)
        self.transfer_cache: Dict[str, TransferContext] = {}
        self.transfer_history: List[TransferResult] = []
    
    def transfer_insight(self, insight: CrossModelInsight, target_model: str, task_input: TaskInput) -> TransferResult:
        """
        Transfer insight to execution model
        
        Args:
            insight: Insight to transfer
            target_model: Target execution model
            task_input: Task input for context
            
        Returns:
            Transfer result with status and metrics
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting insight transfer from {insight.source_model} to {target_model}")
            
            # Validate insight quality
            if not self._validate_insight_quality(insight):
                return self._create_failed_result(insight, target_model, "Insight quality below threshold")
            
            # Check cache first
            cache_key = f"{insight.insight_id}_{target_model}_{self.config.context_format.value}"
            if self.config.enable_caching and cache_key in self.transfer_cache:
                cached_context = self.transfer_cache[cache_key]
                if self._is_cache_valid(cached_context):
                    logger.info(f"Using cached context for {target_model}")
                    return self._create_success_result(insight, target_model, cached_context, start_time)
            
            # Prepare context
            context_label = self.context_preparer.prepare_context(insight, target_model)
            
            # Check if context preparation failed (no content)
            if not context_label.problem_summary and not context_label.recommended_approach:
                return self._create_failed_result(insight, target_model, "Context preparation failed")
            
            # Cache the context
            if self.config.enable_caching:
                self.transfer_cache[cache_key] = context_label
            
            # Create success result
            result = self._create_success_result(insight, target_model, context_label, start_time)
            
            # Add to history
            self.transfer_history.append(result)
            
            logger.info(f"Insight transfer completed successfully in {result.transfer_duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error during insight transfer: {e}")
            return self._create_failed_result(insight, target_model, str(e))
    
    def _validate_insight_quality(self, insight: CrossModelInsight) -> bool:
        """Validate insight quality meets thresholds"""
        return (insight.source_confidence >= self.config.min_confidence_threshold and
                insight.quality_score >= self.config.min_quality_threshold and
                insight.completeness_score >= self.config.min_completeness_threshold)
    
    def _is_cache_valid(self, context_label: TransferContext) -> bool:
        """Check if cached context is still valid"""
        if not self.config.enable_caching:
            return False
        
        age = (datetime.now() - context_label.timestamp).total_seconds()
        return age < self.config.cache_ttl
    
    def _create_success_result(self, insight: CrossModelInsight, target_model: str, 
                             context_label: TransferContext, start_time: datetime) -> TransferResult:
        """Create successful transfer result"""
        duration = (datetime.now() - start_time).total_seconds()
        
        return TransferResult(
            source_insight_id=insight.insight_id,
            target_model=target_model,
            transfer_status=TransferStatus.COMPLETED,
            success=True,
            context_prepared=True,
            transfer_duration=duration,
            context_quality=self._calculate_context_quality(context_label),
            transfer_efficiency=self._calculate_transfer_efficiency(duration, context_label),
            transfer_metadata={
                "context_format": context_label.context_format.value,
                "context_length": len(context_label.problem_summary) + len(context_label.recommended_approach),
                "cache_used": False
            }
        )
    
    def _create_failed_result(self, insight: CrossModelInsight, target_model: str, error: str) -> TransferResult:
        """Create failed transfer result"""
        return TransferResult(
            source_insight_id=insight.insight_id,
            target_model=target_model,
            transfer_status=TransferStatus.FAILED,
            success=False,
            context_prepared=False,
            error_message=error,
            transfer_metadata={"error": error}
        )
    
    def _calculate_context_quality(self, context_label: TransferContext) -> float:
        """Calculate context quality score"""
        try:
            factors = []
            
            # Content completeness
            content_score = 0.0
            if context_label.problem_summary:
                content_score += 0.3
            if context_label.recommended_approach:
                content_score += 0.3
            if context_label.key_considerations:
                content_score += 0.2
            if context_label.potential_risks:
                content_score += 0.1
            if context_label.success_criteria:
                content_score += 0.1
            
            factors.append(content_score)
            
            # Metadata completeness
            metadata_score = 0.0
            if context_label.confidence_score > 0:
                metadata_score += 0.3
            if context_label.quality_score > 0:
                metadata_score += 0.3
            if context_label.complexity_score > 0:
                metadata_score += 0.2
            if context_label.execution_guidance:
                metadata_score += 0.2
            
            factors.append(metadata_score)
            
            # Content quality
            quality_score = (context_label.confidence_score + 
                           context_label.quality_score + 
                           context_label.completeness_score) / 3
            factors.append(quality_score)
            
            return sum(factors) / len(factors)
            
        except Exception as e:
            logger.error(f"Error calculating context quality: {e}")
            return 0.0
    
    def _calculate_transfer_efficiency(self, duration: float, context_label: TransferContext) -> float:
        """Calculate transfer efficiency score"""
        try:
            # Base efficiency on duration and context size
            context_size = len(context_label.problem_summary) + len(context_label.recommended_approach)
            
            # Optimal duration is 1-5 seconds for typical context sizes
            if duration <= 1.0:
                duration_score = 1.0
            elif duration <= 5.0:
                duration_score = 0.8
            elif duration <= 10.0:
                duration_score = 0.6
            else:
                duration_score = 0.4
            
            # Context size efficiency (larger contexts should take longer)
            if context_size <= 1000:
                size_score = 1.0
            elif context_size <= 2000:
                size_score = 0.9
            elif context_size <= 4000:
                size_score = 0.8
            else:
                size_score = 0.7
            
            return (duration_score + size_score) / 2
            
        except Exception as e:
            logger.error(f"Error calculating transfer efficiency: {e}")
            return 0.0
    
    def get_transfer_history(self, limit: int = 100) -> List[TransferResult]:
        """Get transfer history"""
        return self.transfer_history[-limit:]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.transfer_cache),
            "cache_enabled": self.config.enable_caching,
            "cache_ttl": self.config.cache_ttl,
            "transfer_history_size": len(self.transfer_history)
        }
    
    def clear_cache(self):
        """Clear transfer cache"""
        self.transfer_cache.clear()
        logger.info("Transfer cache cleared")


class InsightTransfer:
    """Main insight transfer component"""
    
    def __init__(self, config: InsightTransferConfig):
        self.config = config
        self.transfer_manager = TransferManager(config)
        
        logger.info("InsightTransfer initialized with configuration")
    
    def transfer_insight(self, insight: CrossModelInsight, target_model: str, task_input: TaskInput) -> TransferResult:
        """Transfer insight to execution model"""
        return self.transfer_manager.transfer_insight(insight, target_model, task_input)
    
    def prepare_context(self, insight: CrossModelInsight, target_model: str) -> TransferContext:
        """Prepare context for execution model"""
        return self.transfer_manager.context_preparer.prepare_context(insight, target_model)
    
    def get_transfer_history(self, limit: int = 100) -> List[TransferResult]:
        """Get transfer history"""
        return self.transfer_manager.get_transfer_history(limit)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.transfer_manager.get_cache_stats()
    
    def clear_cache(self):
        """Clear transfer cache"""
        self.transfer_manager.clear_cache()
    
    def update_config(self, new_config: InsightTransferConfig):
        """Update transfer configuration"""
        self.config = new_config
        self.transfer_manager.config = new_config
        self.transfer_manager.context_preparer.config = new_config
        logger.info("InsightTransfer configuration updated")


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create insight transfer
    config = InsightTransferConfig(
        transfer_mode=TransferMode.IMMEDIATE,
        context_format=ContextFormat.STRUCTURED,
        include_confidence=True,
        include_quality=True,
        include_reasoning=True
    )
    transfer = InsightTransfer(config)
    
    # Test insight
    from apoe.insight_extractor import CrossModelInsight
    
    test_insight = CrossModelInsight(
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
    
    # Test task input
    test_task_input = TaskInput(
        problem_description="Fix authentication system",
        constraints=["security", "performance"],
        goal="Implement secure authentication"
    )
    
    # Test transfer
    result = transfer.transfer_insight(test_insight, "gpt-4o-mini", test_task_input)
    
    print(f"Transfer Result:")
    print(f"Success: {result.success}")
    print(f"Status: {result.transfer_status.value}")
    print(f"Duration: {result.transfer_duration:.2f}s")
    print(f"Context Quality: {result.context_quality:.2f}")
    print(f"Transfer Efficiency: {result.transfer_efficiency:.2f}")
    
    # Test context preparation
    context_label = transfer.prepare_context(test_insight, "gpt-4o-mini")
    
    print(f"\nTransfer Context:")
    print(f"Problem Summary: {context_label.problem_summary[:100]}...")
    print(f"Recommended Approach: {context_label.recommended_approach[:100]}...")
    print(f"Confidence Score: {context_label.confidence_score:.2f}")
    print(f"Execution Guidance: {context_label.execution_guidance[:100]}...")

"""
Cross-Model Atom Creator

Creates cross-model atoms from insights, transfer results, and execution results,
enabling comprehensive storage of cross-model consciousness operations.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from cmc_service.cross_model_atoms import (
    CrossModelAtom, CrossModelAtomContent, ModelInsight, TransferRecord,
    KnowledgeTransfer, CrossModelProvenance, ModelInteraction,
    QualityPreservation, ValidationResult
)


logger = logging.getLogger(__name__)


class AtomCreationConfig:
    """Configuration for atom creation"""
    
    def __init__(self,
                 enable_quality_assessment: bool = True,
                 enable_cost_calculation: bool = True,
                 enable_performance_metrics: bool = True,
                 quality_weights: Optional[Dict[str, float]] = None):
        self.enable_quality_assessment = enable_quality_assessment
        self.enable_cost_calculation = enable_cost_calculation
        self.enable_performance_metrics = enable_performance_metrics
        self.quality_weights = quality_weights or {
            "insight_quality": 0.3,
            "transfer_quality": 0.2,
            "execution_quality": 0.5
        }


class ContentProcessor:
    """Processes content for cross-model atoms"""
    
    def __init__(self):
        self.content_cache = {}
    
    def process_content(self, insight_data: Dict[str, Any], 
                       transfer_data: Dict[str, Any],
                       execution_data: Dict[str, Any]) -> CrossModelAtomContent:
        """Process content for cross-model atom"""
        
        return CrossModelAtomContent(
            problem_analysis=insight_data.get("problem_analysis", ""),
            recommended_approach=insight_data.get("recommended_approach", ""),
            key_considerations=insight_data.get("key_considerations", []),
            potential_risks=insight_data.get("potential_risks", []),
            success_criteria=insight_data.get("success_criteria", []),
            minimal_context_used=insight_data.get("minimal_context_used", ""),
            full_context_available=execution_data.get("full_context", ""),
            context_summary=insight_data.get("context_summary", ""),
            smart_model_output=insight_data.get("raw_output", ""),
            execution_model_output=execution_data.get("output", ""),
            transfer_metadata=transfer_data.get("transfer_metadata", {}),
            transfer_validation=transfer_data.get("validation_results", {}),
            quality_metrics=execution_data.get("quality_metrics", {}),
            quality_validation=execution_data.get("quality_validation", {}),
            cost_metrics=execution_data.get("cost_breakdown", {}),
            cost_optimization=execution_data.get("cost_optimization", {})
        )
    
    def extract_model_insights(self, insight_data: Dict[str, Any],
                              execution_data: Dict[str, Any]) -> List[ModelInsight]:
        """Extract model insights from data"""
        insights = []
        
        # Extract insight model insight
        if insight_data.get("source_model"):
            insight = ModelInsight(
                model_id=insight_data.get("source_model", ""),
                model_version=insight_data.get("source_version", ""),
                insight_type=insight_data.get("insight_type", ""),
                insight_content=insight_data.get("raw_output", ""),
                insight_confidence=insight_data.get("source_confidence", 0.0),
                insight_quality=insight_data.get("quality_score", 0.0),
                context_used=insight_data.get("minimal_context_used", ""),
                context_compression_ratio=insight_data.get("context_compression_ratio", 0.0),
                response_time=insight_data.get("response_time", 0.0),
                token_count=insight_data.get("token_count", 0),
                cost=insight_data.get("cost", 0.0),
                quality_metrics=insight_data.get("quality_metrics", {}),
                validation_results=insight_data.get("validation_results", [])
            )
            insights.append(insight)
        
        # Extract execution model insight
        if execution_data.get("model_id"):
            insight = ModelInsight(
                model_id=execution_data.get("model_id", ""),
                model_version=execution_data.get("model_version", ""),
                insight_type="execution_result",
                insight_content=execution_data.get("output", ""),
                insight_confidence=execution_data.get("confidence", 0.0),
                insight_quality=execution_data.get("quality_score", 0.0),
                context_used=execution_data.get("full_context", ""),
                context_compression_ratio=1.0,  # Full context used
                response_time=execution_data.get("execution_time", 0.0),
                token_count=execution_data.get("token_count", 0),
                cost=execution_data.get("cost", 0.0),
                quality_metrics=execution_data.get("quality_metrics", {}),
                validation_results=execution_data.get("validation_results", [])
            )
            insights.append(insight)
        
        return insights
    
    def extract_transfer_history(self, transfer_data: Dict[str, Any]) -> List[TransferRecord]:
        """Extract transfer history from data"""
        transfers = []
        
        if transfer_data.get("transfer_id"):
            transfer = TransferRecord(
                transfer_id=transfer_data.get("transfer_id", ""),
                transfer_timestamp=transfer_data.get("transfer_timestamp", datetime.now()),
                source_model=transfer_data.get("source_model", ""),
                target_model=transfer_data.get("target_model", ""),
                transfer_type=transfer_data.get("transfer_type", ""),
                transfer_content=transfer_data.get("transfer_content", ""),
                transfer_metadata=transfer_data.get("transfer_metadata", {}),
                transfer_quality=transfer_data.get("transfer_quality_score", 0.0),
                transfer_confidence=transfer_data.get("transfer_confidence", 0.0),
                transfer_completeness=transfer_data.get("transfer_completeness", 0.0),
                validation_checks=transfer_data.get("validation_checks", []),
                validation_results=transfer_data.get("validation_results", []),
                transfer_latency=transfer_data.get("transfer_latency", 0.0),
                transfer_size=transfer_data.get("transfer_size", 0),
                transfer_compression_ratio=transfer_data.get("transfer_compression_ratio", 0.0)
            )
            transfers.append(transfer)
        
        return transfers


class QualityAssessor:
    """Assesses quality for cross-model operations"""
    
    def __init__(self, config: AtomCreationConfig):
        self.config = config
        self.quality_cache = {}
    
    def assess_quality(self, insight_data: Dict[str, Any],
                      transfer_data: Dict[str, Any],
                      execution_data: Dict[str, Any]) -> float:
        """Assess overall quality of cross-model operation"""
        
        if not self.config.enable_quality_assessment:
            return 0.5  # Default quality
        
        # Extract quality scores
        insight_quality = insight_data.get("quality_score", 0.0)
        transfer_quality = transfer_data.get("transfer_quality_score", 0.0)
        execution_quality = execution_data.get("quality_score", 0.0)
        
        # Calculate weighted quality
        weights = self.config.quality_weights
        overall_quality = (
            insight_quality * weights["insight_quality"] +
            transfer_quality * weights["transfer_quality"] +
            execution_quality * weights["execution_quality"]
        )
        
        # Ensure quality is within bounds
        return max(0.0, min(1.0, overall_quality))
    
    def assess_confidence(self, insight_data: Dict[str, Any],
                         transfer_data: Dict[str, Any],
                         execution_data: Dict[str, Any]) -> float:
        """Assess overall confidence"""
        
        # Extract confidence scores
        insight_confidence = insight_data.get("source_confidence", 0.0)
        transfer_confidence = transfer_data.get("transfer_confidence", 0.0)
        execution_confidence = execution_data.get("confidence", 0.0)
        
        # Calculate weighted confidence
        weights = self.config.quality_weights
        overall_confidence = (
            insight_confidence * weights["insight_quality"] +
            transfer_confidence * weights["transfer_quality"] +
            execution_confidence * weights["execution_quality"]
        )
        
        # Ensure confidence is within bounds
        return max(0.0, min(1.0, overall_confidence))


class CostCalculator:
    """Calculates costs for cross-model operations"""
    
    def __init__(self, config: AtomCreationConfig):
        self.config = config
        self.cost_cache = {}
    
    def calculate_cost_breakdown(self, insight_data: Dict[str, Any],
                                execution_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate cost breakdown by model"""
        
        if not self.config.enable_cost_calculation:
            return {}
        
        cost_breakdown = {}
        
        # Add insight model cost
        if insight_data.get("source_model") and insight_data.get("cost"):
            cost_breakdown[insight_data["source_model"]] = insight_data["cost"]
        
        # Add execution model cost
        if execution_data.get("model_id") and execution_data.get("cost"):
            cost_breakdown[execution_data["model_id"]] = execution_data["cost"]
        
        return cost_breakdown
    
    def calculate_total_cost(self, cost_breakdown: Dict[str, float]) -> float:
        """Calculate total cost"""
        return sum(cost_breakdown.values())


class PerformanceMetricsCollector:
    """Collects performance metrics for cross-model operations"""
    
    def __init__(self, config: AtomCreationConfig):
        self.config = config
        self.metrics_cache = {}
    
    def collect_performance_metrics(self, insight_data: Dict[str, Any],
                                   transfer_data: Dict[str, Any],
                                   execution_data: Dict[str, Any]) -> Dict[str, float]:
        """Collect performance metrics"""
        
        if not self.config.enable_performance_metrics:
            return {}
        
        metrics = {}
        
        # Add insight performance metrics
        if insight_data.get("response_time"):
            metrics["insight_response_time"] = insight_data["response_time"]
        
        if insight_data.get("token_count"):
            metrics["insight_token_count"] = insight_data["token_count"]
        
        # Add transfer performance metrics
        if transfer_data.get("transfer_latency"):
            metrics["transfer_latency"] = transfer_data["transfer_latency"]
        
        if transfer_data.get("transfer_size"):
            metrics["transfer_size"] = transfer_data["transfer_size"]
        
        # Add execution performance metrics
        if execution_data.get("execution_time"):
            metrics["execution_time"] = execution_data["execution_time"]
        
        if execution_data.get("token_count"):
            metrics["execution_token_count"] = execution_data["token_count"]
        
        # Calculate total time
        total_time = (
            insight_data.get("response_time", 0.0) +
            transfer_data.get("transfer_latency", 0.0) +
            execution_data.get("execution_time", 0.0)
        )
        metrics["total_time"] = total_time
        
        return metrics


class CrossModelAtomCreator:
    """Create cross-model atoms"""
    
    def __init__(self, config: AtomCreationConfig):
        self.config = config
        self.content_processor = ContentProcessor()
        self.quality_assessor = QualityAssessor(config)
        self.cost_calculator = CostCalculator(config)
        self.performance_collector = PerformanceMetricsCollector(config)
        logger.info(f"Initialized CrossModelAtomCreator with config: {config}")
    
    def create_cross_model_atom(self, insight_data: Dict[str, Any],
                               transfer_data: Dict[str, Any],
                               execution_data: Dict[str, Any]) -> CrossModelAtom:
        """Create cross-model atom from insight and results"""
        
        logger.info("Creating cross-model atom from insight and results")
        
        try:
            # Process content
            content = self.content_processor.process_content(
                insight_data, transfer_data, execution_data
            )
            
            # Extract model insights
            model_insights = self.content_processor.extract_model_insights(
                insight_data, execution_data
            )
            
            # Extract transfer history
            transfer_history = self.content_processor.extract_transfer_history(
                transfer_data
            )
            
            # Assess quality
            quality_score = self.quality_assessor.assess_quality(
                insight_data, transfer_data, execution_data
            )
            
            # Assess confidence
            confidence = self.quality_assessor.assess_confidence(
                insight_data, transfer_data, execution_data
            )
            
            # Calculate cost breakdown
            cost_breakdown = self.cost_calculator.calculate_cost_breakdown(
                insight_data, execution_data
            )
            
            # Collect performance metrics
            performance_metrics = self.performance_collector.collect_performance_metrics(
                insight_data, transfer_data, execution_data
            )
            
            # Create knowledge transfer
            knowledge_transfer = self._create_knowledge_transfer(transfer_data)
            
            # Create cross-model provenance
            cross_model_provenance = self._create_cross_model_provenance(
                insight_data, transfer_data, execution_data
            )
            
            # Create model interactions
            model_interactions = self._create_model_interactions(
                insight_data, transfer_data, execution_data
            )
            
            # Create quality preservation
            quality_preservation = self._create_quality_preservation(
                insight_data, transfer_data, execution_data
            )
            
            # Create atom
            atom = CrossModelAtom(
                content=content,
                source_models=[
                    insight_data.get("source_model", ""),
                    execution_data.get("model_id", "")
                ],
                model_insights=model_insights,
                transfer_history=transfer_history,
                insight_id=insight_data.get("insight_id", ""),
                insight_quality=insight_data.get("quality_score", 0.0),
                insight_confidence=insight_data.get("source_confidence", 0.0),
                knowledge_transfer=knowledge_transfer,
                transfer_quality=transfer_data.get("transfer_quality_score", 0.0),
                transfer_confidence=transfer_data.get("transfer_confidence", 0.0),
                cross_model_provenance=cross_model_provenance,
                model_interactions=model_interactions,
                cost_breakdown=cost_breakdown,
                performance_metrics=performance_metrics,
                quality_preservation=quality_preservation,
                quality_score=quality_score,
                confidence=confidence,
                metadata={
                    "created_by": "cross_model_consciousness",
                    "creation_timestamp": datetime.now().isoformat(),
                    "source_data": {
                        "insight_data": insight_data,
                        "transfer_data": transfer_data,
                        "execution_data": execution_data
                    }
                }
            )
            
            logger.info(f"Successfully created cross-model atom: {atom.atom_id}")
            return atom
            
        except Exception as e:
            logger.error(f"Error creating cross-model atom: {e}")
            raise
    
    def _create_knowledge_transfer(self, transfer_data: Dict[str, Any]) -> KnowledgeTransfer:
        """Create knowledge transfer from transfer data"""
        
        return KnowledgeTransfer(
            transfer_id=transfer_data.get("transfer_id", ""),
            transfer_timestamp=transfer_data.get("transfer_timestamp", datetime.now()),
            source_model=transfer_data.get("source_model", ""),
            source_context_hash=transfer_data.get("source_context_hash", ""),
            target_model=transfer_data.get("target_model", ""),
            target_context_hash=transfer_data.get("target_context_hash", ""),
            insight_content=transfer_data.get("transfer_content", ""),
            insight_metadata=transfer_data.get("transfer_metadata", {}),
            transfer_quality_score=transfer_data.get("transfer_quality_score", 0.0),
            transfer_completeness=transfer_data.get("transfer_completeness", 0.0),
            transfer_accuracy=transfer_data.get("transfer_accuracy", 0.0),
            validation_checks=transfer_data.get("validation_checks", []),
            validation_results=transfer_data.get("validation_results", []),
            transfer_latency=transfer_data.get("transfer_latency", 0.0),
            transfer_size=transfer_data.get("transfer_size", 0),
            transfer_compression_ratio=transfer_data.get("transfer_compression_ratio", 0.0)
        )
    
    def _create_cross_model_provenance(self, insight_data: Dict[str, Any],
                                     transfer_data: Dict[str, Any],
                                     execution_data: Dict[str, Any]) -> CrossModelProvenance:
        """Create cross-model provenance"""
        
        source_models = []
        if insight_data.get("source_model"):
            source_models.append(insight_data["source_model"])
        if execution_data.get("model_id"):
            source_models.append(execution_data["model_id"])
        
        return CrossModelProvenance(
            source_models=source_models,
            model_interactions=[
                {
                    "type": "insight_generation",
                    "model": insight_data.get("source_model", ""),
                    "timestamp": insight_data.get("timestamp", datetime.now().isoformat())
                },
                {
                    "type": "knowledge_transfer",
                    "source": transfer_data.get("source_model", ""),
                    "target": transfer_data.get("target_model", ""),
                    "timestamp": transfer_data.get("transfer_timestamp", datetime.now().isoformat())
                },
                {
                    "type": "execution",
                    "model": execution_data.get("model_id", ""),
                    "timestamp": execution_data.get("timestamp", datetime.now().isoformat())
                }
            ],
            provenance_quality=0.8,  # Default quality
            provenance_confidence=0.8,  # Default confidence
            validation_results=[]
        )
    
    def _create_model_interactions(self, insight_data: Dict[str, Any],
                                 transfer_data: Dict[str, Any],
                                 execution_data: Dict[str, Any]) -> List[ModelInteraction]:
        """Create model interactions"""
        
        interactions = []
        
        # Create insight-to-transfer interaction
        if insight_data.get("source_model") and transfer_data.get("target_model"):
            interaction = ModelInteraction(
                source_model=insight_data["source_model"],
                target_model=transfer_data["target_model"],
                interaction_type="insight_transfer",
                interaction_content=transfer_data.get("transfer_content", ""),
                interaction_metadata=transfer_data.get("transfer_metadata", {}),
                interaction_quality=transfer_data.get("transfer_quality_score", 0.0),
                interaction_confidence=transfer_data.get("transfer_confidence", 0.0),
                validation_results=transfer_data.get("validation_results", []),
                validation_confidence=transfer_data.get("transfer_confidence", 0.0)
            )
            interactions.append(interaction)
        
        # Create transfer-to-execution interaction
        if transfer_data.get("target_model") and execution_data.get("model_id"):
            interaction = ModelInteraction(
                source_model=transfer_data["target_model"],
                target_model=execution_data["model_id"],
                interaction_type="execution_transfer",
                interaction_content=execution_data.get("output", ""),
                interaction_metadata=execution_data.get("metadata", {}),
                interaction_quality=execution_data.get("quality_score", 0.0),
                interaction_confidence=execution_data.get("confidence", 0.0),
                validation_results=execution_data.get("validation_results", []),
                validation_confidence=execution_data.get("confidence", 0.0)
            )
            interactions.append(interaction)
        
        return interactions
    
    def _create_quality_preservation(self, insight_data: Dict[str, Any],
                                   transfer_data: Dict[str, Any],
                                   execution_data: Dict[str, Any]) -> QualityPreservation:
        """Create quality preservation tracking"""
        
        # Calculate quality preservation metrics
        insight_quality = insight_data.get("quality_score", 0.0)
        execution_quality = execution_data.get("quality_score", 0.0)
        
        quality_degradation = max(0.0, insight_quality - execution_quality)
        
        return QualityPreservation(
            preservation_strategy="cross_model_transfer",
            preservation_effectiveness=1.0 - quality_degradation,
            quality_before=insight_quality,
            quality_after=execution_quality,
            quality_degradation=quality_degradation,
            preservation_validation=[]
        )
    
    def validate_atom(self, atom: CrossModelAtom) -> List[ValidationResult]:
        """Validate a cross-model atom"""
        
        validation_results = atom.validate()
        
        # Additional validation checks
        if not atom.source_models:
            validation_results.append(ValidationResult(
                field="source_models",
                valid=False,
                message="At least one source model is required"
            ))
        
        if not atom.insight_id:
            validation_results.append(ValidationResult(
                field="insight_id",
                valid=False,
                message="Insight ID is required"
            ))
        
        return validation_results
    
    def get_creation_statistics(self) -> Dict[str, Any]:
        """Get atom creation statistics"""
        
        return {
            "quality_assessment_enabled": self.config.enable_quality_assessment,
            "cost_calculation_enabled": self.config.enable_cost_calculation,
            "performance_metrics_enabled": self.config.enable_performance_metrics,
            "quality_weights": self.config.quality_weights,
            "content_cache_size": len(self.content_processor.content_cache),
            "quality_cache_size": len(self.quality_assessor.quality_cache),
            "cost_cache_size": len(self.cost_calculator.cost_cache),
            "metrics_cache_size": len(self.performance_collector.metrics_cache)
        }

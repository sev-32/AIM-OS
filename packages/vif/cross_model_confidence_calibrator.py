"""
Cross-Model Confidence Calibrator

Calibrates confidence across different AI models, enabling accurate confidence
estimation and calibration for cross-model consciousness operations.
"""

import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from vif.cross_model_vif import ValidationResult
from vif.cross_model_vif import CrossModelVIF, KnowledgeTransfer, CrossModelValidation


logger = logging.getLogger(__name__)


class CalibrationConfig:
    """Configuration for confidence calibration"""
    
    def __init__(self,
                 enable_historical_analysis: bool = True,
                 enable_calibration_correction: bool = True,
                 enable_uncertainty_quantification: bool = True,
                 calibration_window_days: int = 30,
                 min_samples_for_calibration: int = 10):
        self.enable_historical_analysis = enable_historical_analysis
        self.enable_calibration_correction = enable_calibration_correction
        self.enable_uncertainty_quantification = enable_uncertainty_quantification
        self.calibration_window_days = calibration_window_days
        self.min_samples_for_calibration = min_samples_for_calibration


class CalibratedConfidence:
    """Calibrated confidence result"""
    
    def __init__(self,
                 original_confidence: float,
                 calibrated_confidence: float,
                 calibration_factor: float,
                 uncertainty: float,
                 calibration_quality: float):
        self.original_confidence = original_confidence
        self.calibrated_confidence = calibrated_confidence
        self.calibration_factor = calibration_factor
        self.uncertainty = uncertainty
        self.calibration_quality = calibration_quality
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "original_confidence": self.original_confidence,
            "calibrated_confidence": self.calibrated_confidence,
            "calibration_factor": self.calibration_factor,
            "uncertainty": self.uncertainty,
            "calibration_quality": self.calibration_quality,
            "timestamp": self.timestamp.isoformat()
        }


class ConfidenceTracker:
    """Tracks confidence data for calibration"""
    
    def __init__(self):
        self.confidence_history = {}
        self.model_performance = {}
    
    def record_confidence(self, model_id: str, task_type: str, 
                         predicted_confidence: float, actual_confidence: float,
                         success: bool) -> None:
        """Record confidence data"""
        key = f"{model_id}_{task_type}"
        
        if key not in self.confidence_history:
            self.confidence_history[key] = []
        
        self.confidence_history[key].append({
            "predicted_confidence": predicted_confidence,
            "actual_confidence": actual_confidence,
            "success": success,
            "timestamp": datetime.now()
        })
        
        # Update model performance
        if model_id not in self.model_performance:
            self.model_performance[model_id] = {
                "total_tasks": 0,
                "successful_tasks": 0,
                "confidence_accuracy": 0.0
            }
        
        self.model_performance[model_id]["total_tasks"] += 1
        if success:
            self.model_performance[model_id]["successful_tasks"] += 1
        
        # Update confidence accuracy
        accuracy = abs(predicted_confidence - actual_confidence)
        current_accuracy = self.model_performance[model_id]["confidence_accuracy"]
        total_tasks = self.model_performance[model_id]["total_tasks"]
        
        self.model_performance[model_id]["confidence_accuracy"] = (
            (current_accuracy * (total_tasks - 1) + accuracy) / total_tasks
        )
    
    def get_historical_data(self, model_id: str, task_type: str) -> List[Dict[str, Any]]:
        """Get historical confidence data"""
        key = f"{model_id}_{task_type}"
        return self.confidence_history.get(key, [])
    
    def get_model_performance(self, model_id: str) -> Dict[str, Any]:
        """Get model performance data"""
        return self.model_performance.get(model_id, {})
    
    def get_calibration_data(self, model_id: str, task_type: str, 
                           window_days: int = 30) -> List[Dict[str, Any]]:
        """Get calibration data within time window"""
        historical_data = self.get_historical_data(model_id, task_type)
        
        cutoff_date = datetime.now() - timedelta(days=window_days)
        
        return [
            data for data in historical_data
            if data["timestamp"] >= cutoff_date
        ]


class CalibrationAnalyzer:
    """Analyzes confidence calibration"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_calibration(self, historical_data: List[Dict[str, Any]], 
                          current_confidence: float) -> Dict[str, Any]:
        """Analyze confidence calibration"""
        if len(historical_data) < 5:
            return {
                "calibration_factor": 1.0,
                "uncertainty": 0.1,
                "calibration_quality": 0.5,
                "analysis_type": "insufficient_data"
            }
        
        # Calculate calibration metrics
        predicted_confidences = [data["predicted_confidence"] for data in historical_data]
        actual_confidences = [data["actual_confidence"] for data in historical_data]
        successes = [data["success"] for data in historical_data]
        
        # Calculate Expected Calibration Error (ECE)
        ece = self._calculate_ece(predicted_confidences, actual_confidences, successes)
        
        # Calculate calibration factor
        calibration_factor = self._calculate_calibration_factor(
            predicted_confidences, actual_confidences
        )
        
        # Calculate uncertainty
        uncertainty = self._calculate_uncertainty(predicted_confidences, actual_confidences)
        
        # Calculate calibration quality
        calibration_quality = self._calculate_calibration_quality(ece, uncertainty)
        
        return {
            "calibration_factor": calibration_factor,
            "uncertainty": uncertainty,
            "calibration_quality": calibration_quality,
            "ece": ece,
            "analysis_type": "full_analysis"
        }
    
    def _calculate_ece(self, predicted: List[float], actual: List[float], 
                      successes: List[bool]) -> float:
        """Calculate Expected Calibration Error"""
        if len(predicted) != len(actual) or len(predicted) != len(successes):
            return 1.0
        
        # Bin the confidences
        bins = 10
        bin_size = 1.0 / bins
        ece = 0.0
        
        for i in range(bins):
            bin_start = i * bin_size
            bin_end = (i + 1) * bin_size
            
            # Find samples in this bin
            bin_indices = [
                j for j, conf in enumerate(predicted)
                if bin_start <= conf < bin_end
            ]
            
            if not bin_indices:
                continue
            
            bin_count = len(bin_indices)
            bin_accuracy = sum(successes[j] for j in bin_indices) / bin_count
            bin_confidence = sum(predicted[j] for j in bin_indices) / bin_count
            
            ece += abs(bin_accuracy - bin_confidence) * bin_count
        
        return ece / len(predicted)
    
    def _calculate_calibration_factor(self, predicted: List[float], 
                                    actual: List[float]) -> float:
        """Calculate calibration factor"""
        if not predicted or not actual:
            return 1.0
        
        # Calculate the ratio of actual to predicted confidence
        ratios = [actual[i] / predicted[i] if predicted[i] > 0 else 1.0 
                 for i in range(min(len(predicted), len(actual)))]
        
        # Return median ratio as calibration factor
        return statistics.median(ratios) if ratios else 1.0
    
    def _calculate_uncertainty(self, predicted: List[float], 
                             actual: List[float]) -> float:
        """Calculate uncertainty in calibration"""
        if len(predicted) != len(actual) or len(predicted) < 2:
            return 0.1
        
        # Calculate standard deviation of prediction errors
        errors = [abs(predicted[i] - actual[i]) for i in range(len(predicted))]
        return statistics.stdev(errors) if len(errors) > 1 else 0.1
    
    def _calculate_calibration_quality(self, ece: float, uncertainty: float) -> float:
        """Calculate calibration quality score"""
        # Higher ECE and uncertainty mean lower quality
        quality = max(0.0, 1.0 - (ece + uncertainty))
        return min(1.0, quality)


class CrossModelConfidenceCalibrator:
    """Calibrate confidence across models"""
    
    def __init__(self, config: CalibrationConfig):
        self.config = config
        self.confidence_tracker = ConfidenceTracker()
        self.calibration_analyzer = CalibrationAnalyzer()
        logger.info(f"Initialized CrossModelConfidenceCalibrator with config: {config}")
    
    def calibrate_cross_model_confidence(self, cross_model_vif: CrossModelVIF) -> CalibratedConfidence:
        """Calibrate confidence across models"""
        logger.info(f"Calibrating cross-model confidence for VIF: {cross_model_vif.vif_id}")
        
        try:
            # Calibrate insight confidence
            insight_confidence = self._calibrate_insight_confidence(cross_model_vif)
            
            # Calibrate transfer confidence
            transfer_confidence = self._calibrate_transfer_confidence(cross_model_vif)
            
            # Calibrate execution confidence
            execution_confidence = self._calibrate_execution_confidence(cross_model_vif)
            
            # Combine confidences
            combined_confidence = self._combine_confidences(
                insight_confidence, transfer_confidence, execution_confidence
            )
            
            logger.info(f"Successfully calibrated cross-model confidence for VIF: {cross_model_vif.vif_id}")
            return combined_confidence
            
        except Exception as e:
            logger.error(f"Error calibrating cross-model confidence: {e}")
            raise
    
    def _calibrate_insight_confidence(self, cross_model_vif: CrossModelVIF) -> CalibratedConfidence:
        """Calibrate confidence in insight generation"""
        original_confidence = cross_model_vif.insight_confidence
        
        if not self.config.enable_historical_analysis:
            return CalibratedConfidence(
                original_confidence=original_confidence,
                calibrated_confidence=original_confidence,
                calibration_factor=1.0,
                uncertainty=0.1,
                calibration_quality=0.5
            )
        
        # Get historical confidence data for insight model
        historical_data = self.confidence_tracker.get_historical_data(
            cross_model_vif.insight_model_id, "insight_generation"
        )
        
        # Analyze confidence calibration
        calibration_analysis = self.calibration_analyzer.analyze_calibration(
            historical_data, original_confidence
        )
        
        # Apply calibration correction
        calibrated_confidence = self._apply_calibration_correction(
            original_confidence, calibration_analysis
        )
        
        return CalibratedConfidence(
            original_confidence=original_confidence,
            calibrated_confidence=calibrated_confidence,
            calibration_factor=calibration_analysis["calibration_factor"],
            uncertainty=calibration_analysis["uncertainty"],
            calibration_quality=calibration_analysis["calibration_quality"]
        )
    
    def _calibrate_transfer_confidence(self, cross_model_vif: CrossModelVIF) -> CalibratedConfidence:
        """Calibrate confidence in knowledge transfer"""
        original_confidence = cross_model_vif.transfer_confidence
        
        if not self.config.enable_historical_analysis:
            return CalibratedConfidence(
                original_confidence=original_confidence,
                calibrated_confidence=original_confidence,
                calibration_factor=1.0,
                uncertainty=0.1,
                calibration_quality=0.5
            )
        
        # Get historical transfer data
        historical_data = self.confidence_tracker.get_historical_data(
            "knowledge_transfer", "transfer_quality"
        )
        
        # Analyze transfer calibration
        calibration_analysis = self.calibration_analyzer.analyze_calibration(
            historical_data, original_confidence
        )
        
        # Apply calibration correction
        calibrated_confidence = self._apply_calibration_correction(
            original_confidence, calibration_analysis
        )
        
        return CalibratedConfidence(
            original_confidence=original_confidence,
            calibrated_confidence=calibrated_confidence,
            calibration_factor=calibration_analysis["calibration_factor"],
            uncertainty=calibration_analysis["uncertainty"],
            calibration_quality=calibration_analysis["calibration_quality"]
        )
    
    def _calibrate_execution_confidence(self, cross_model_vif: CrossModelVIF) -> CalibratedConfidence:
        """Calibrate confidence in execution"""
        original_confidence = cross_model_vif.cross_model_validation.validation_confidence
        
        if not self.config.enable_historical_analysis:
            return CalibratedConfidence(
                original_confidence=original_confidence,
                calibrated_confidence=original_confidence,
                calibration_factor=1.0,
                uncertainty=0.1,
                calibration_quality=0.5
            )
        
        # Get historical execution data
        historical_data = self.confidence_tracker.get_historical_data(
            cross_model_vif.execution_model_id, "execution_quality"
        )
        
        # Analyze execution calibration
        calibration_analysis = self.calibration_analyzer.analyze_calibration(
            historical_data, original_confidence
        )
        
        # Apply calibration correction
        calibrated_confidence = self._apply_calibration_correction(
            original_confidence, calibration_analysis
        )
        
        return CalibratedConfidence(
            original_confidence=original_confidence,
            calibrated_confidence=calibrated_confidence,
            calibration_factor=calibration_analysis["calibration_factor"],
            uncertainty=calibration_analysis["uncertainty"],
            calibration_quality=calibration_analysis["calibration_quality"]
        )
    
    def _apply_calibration_correction(self, original_confidence: float, 
                                    calibration_analysis: Dict[str, Any]) -> float:
        """Apply calibration correction"""
        if not self.config.enable_calibration_correction:
            return original_confidence
        
        calibration_factor = calibration_analysis.get("calibration_factor", 1.0)
        uncertainty = calibration_analysis.get("uncertainty", 0.1)
        
        # Apply calibration factor with uncertainty bounds
        calibrated_confidence = original_confidence * calibration_factor
        
        # Apply uncertainty bounds
        calibrated_confidence = max(0.0, min(1.0, calibrated_confidence))
        
        return calibrated_confidence
    
    def _combine_confidences(self, insight_confidence: CalibratedConfidence,
                           transfer_confidence: CalibratedConfidence,
                           execution_confidence: CalibratedConfidence) -> CalibratedConfidence:
        """Combine confidences from different stages"""
        # Weighted average based on calibration quality
        weights = [
            insight_confidence.calibration_quality,
            transfer_confidence.calibration_quality,
            execution_confidence.calibration_quality
        ]
        
        confidences = [
            insight_confidence.calibrated_confidence,
            transfer_confidence.calibrated_confidence,
            execution_confidence.calibrated_confidence
        ]
        
        # Calculate weighted average
        total_weight = sum(weights)
        if total_weight > 0:
            combined_confidence = sum(w * c for w, c in zip(weights, confidences)) / total_weight
        else:
            combined_confidence = sum(confidences) / len(confidences)
        
        # Calculate combined uncertainty
        combined_uncertainty = max(
            insight_confidence.uncertainty,
            transfer_confidence.uncertainty,
            execution_confidence.uncertainty
        )
        
        # Calculate combined calibration quality
        combined_quality = min(
            insight_confidence.calibration_quality,
            transfer_confidence.calibration_quality,
            execution_confidence.calibration_quality
        )
        
        return CalibratedConfidence(
            original_confidence=combined_confidence,
            calibrated_confidence=combined_confidence,
            calibration_factor=1.0,
            uncertainty=combined_uncertainty,
            calibration_quality=combined_quality
        )
    
    def record_confidence_outcome(self, model_id: str, task_type: str,
                                predicted_confidence: float, actual_confidence: float,
                                success: bool) -> None:
        """Record confidence outcome for future calibration"""
        self.confidence_tracker.record_confidence(
            model_id, task_type, predicted_confidence, actual_confidence, success
        )
    
    def get_calibration_statistics(self) -> Dict[str, Any]:
        """Get calibration statistics"""
        return {
            "total_models_tracked": len(self.confidence_tracker.model_performance),
            "total_confidence_records": sum(
                len(history) for history in self.confidence_tracker.confidence_history.values()
            ),
            "calibration_enabled": self.config.enable_calibration_correction,
            "historical_analysis_enabled": self.config.enable_historical_analysis,
            "uncertainty_quantification_enabled": self.config.enable_uncertainty_quantification
        }
    
    def validate_calibration(self, calibrated_confidence: CalibratedConfidence) -> List[ValidationResult]:
        """Validate calibration result"""
        validation_results = []
        
        # Validate confidence range
        if not 0.0 <= calibrated_confidence.calibrated_confidence <= 1.0:
            validation_results.append(ValidationResult(
                field="calibrated_confidence",
                valid=False,
                message="Calibrated confidence must be between 0.0 and 1.0"
            ))
        
        # Validate uncertainty range
        if not 0.0 <= calibrated_confidence.uncertainty <= 1.0:
            validation_results.append(ValidationResult(
                field="uncertainty",
                valid=False,
                message="Uncertainty must be between 0.0 and 1.0"
            ))
        
        # Validate calibration quality
        if not 0.0 <= calibrated_confidence.calibration_quality <= 1.0:
            validation_results.append(ValidationResult(
                field="calibration_quality",
                valid=False,
                message="Calibration quality must be between 0.0 and 1.0"
            ))
        
        return validation_results

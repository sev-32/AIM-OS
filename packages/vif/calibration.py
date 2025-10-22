"""Expected Calibration Error (ECE) tracking

Tracks how well-calibrated confidence scores are by comparing
predicted confidence to actual accuracy over time.

Perfect calibration: When the model says 80% confident, it's correct 80% of the time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone
import math


@dataclass
class CalibrationBin:
    """A bin for calibration tracking"""
    confidence_range: Tuple[float, float]  # (min, max) confidence
    predictions: List[float] = field(default_factory=list)  # Predicted confidences
    outcomes: List[bool] = field(default_factory=list)  # Actual outcomes (correct/incorrect)
    
    @property
    def count(self) -> int:
        """Number of predictions in this bin"""
        return len(self.predictions)
    
    @property
    def avg_confidence(self) -> float:
        """Average predicted confidence"""
        if not self.predictions:
            return 0.0
        return sum(self.predictions) / len(self.predictions)
    
    @property
    def accuracy(self) -> float:
        """Actual accuracy (fraction correct)"""
        if not self.outcomes:
            return 0.0
        return sum(1 for correct in self.outcomes if correct) / len(self.outcomes)
    
    @property
    def calibration_gap(self) -> float:
        """Gap between confidence and accuracy"""
        return abs(self.avg_confidence - self.accuracy)


@dataclass
class ECETracker:
    """Tracks Expected Calibration Error over time
    
    ECE measures calibration quality:
    - ECE = 0.0: Perfect calibration
    - ECE < 0.05: Excellent calibration
    - ECE < 0.10: Good calibration
    - ECE > 0.10: Poor calibration (recalibration needed)
    
    Examples:
        >>> tracker = ECETracker(num_bins=10)
        >>> tracker.add_prediction(confidence=0.85, correct=True)
        >>> tracker.add_prediction(confidence=0.90, correct=True)
        >>> tracker.add_prediction(confidence=0.80, correct=False)
        >>> ece = tracker.calculate_ece()
        >>> print(f"ECE: {ece:.4f}")
    """
    
    num_bins: int = 10  # Number of calibration bins
    bins: List[CalibrationBin] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Initialize calibration bins"""
        if not self.bins:
            bin_width = 1.0 / self.num_bins
            self.bins = [
                CalibrationBin(
                    confidence_range=(i * bin_width, (i + 1) * bin_width)
                )
                for i in range(self.num_bins)
            ]
    
    def add_prediction(
        self,
        confidence: float,
        correct: bool,
        *,
        validate: bool = True
    ) -> None:
        """Add a prediction to the tracker
        
        Args:
            confidence: Model's confidence score (0.0-1.0)
            correct: Whether prediction was actually correct
            validate: If True, raise error for invalid confidence
        """
        if validate and not (0.0 <= confidence <= 1.0):
            raise ValueError(f"Confidence must be in [0.0, 1.0], got {confidence}")
        
        # Find appropriate bin
        bin_idx = self._get_bin_index(confidence)
        
        # Add to bin
        self.bins[bin_idx].predictions.append(confidence)
        self.bins[bin_idx].outcomes.append(correct)
    
    def _get_bin_index(self, confidence: float) -> int:
        """Get bin index for confidence score"""
        # Clamp to valid range
        confidence = max(0.0, min(1.0, confidence))
        
        # Calculate bin index
        bin_idx = int(confidence * self.num_bins)
        
        # Handle edge case: confidence = 1.0
        if bin_idx >= self.num_bins:
            bin_idx = self.num_bins - 1
        
        return bin_idx
    
    def calculate_ece(self) -> float:
        """Calculate Expected Calibration Error
        
        ECE = Σ (n_b / n_total) * |conf_b - acc_b|
        
        Where:
        - n_b: number of predictions in bin b
        - n_total: total number of predictions
        - conf_b: average confidence in bin b
        - acc_b: accuracy in bin b
        
        Returns:
            ECE score (0.0 = perfect, lower is better)
        """
        total_predictions = sum(bin.count for bin in self.bins)
        
        if total_predictions == 0:
            return 0.0
        
        ece = 0.0
        for bin in self.bins:
            if bin.count > 0:
                weight = bin.count / total_predictions
                ece += weight * bin.calibration_gap
        
        return ece
    
    def calculate_max_calibration_error(self) -> float:
        """Calculate Maximum Calibration Error (MCE)
        
        MCE = max_b |conf_b - acc_b|
        
        Returns:
            MCE score (largest calibration gap)
        """
        gaps = [bin.calibration_gap for bin in self.bins if bin.count > 0]
        return max(gaps) if gaps else 0.0
    
    def calculate_rmsce(self) -> float:
        """Calculate Root Mean Squared Calibration Error
        
        RMSCE = sqrt(Σ (n_b / n_total) * (conf_b - acc_b)²)
        
        Returns:
            RMSCE score (penalizes large errors more)
        """
        total_predictions = sum(bin.count for bin in self.bins)
        
        if total_predictions == 0:
            return 0.0
        
        rmsce_squared = 0.0
        for bin in self.bins:
            if bin.count > 0:
                weight = bin.count / total_predictions
                gap = bin.avg_confidence - bin.accuracy
                rmsce_squared += weight * (gap ** 2)
        
        return math.sqrt(rmsce_squared)
    
    def get_calibration_summary(self) -> Dict[str, float]:
        """Get comprehensive calibration metrics"""
        return {
            "ece": self.calculate_ece(),
            "mce": self.calculate_max_calibration_error(),
            "rmsce": self.calculate_rmsce(),
            "total_predictions": sum(bin.count for bin in self.bins),
            "non_empty_bins": sum(1 for bin in self.bins if bin.count > 0),
        }
    
    def get_bin_details(self) -> List[Dict]:
        """Get detailed info for each bin"""
        details = []
        for i, bin in enumerate(self.bins):
            if bin.count > 0:
                details.append({
                    "bin": i,
                    "range": bin.confidence_range,
                    "count": bin.count,
                    "avg_confidence": bin.avg_confidence,
                    "accuracy": bin.accuracy,
                    "calibration_gap": bin.calibration_gap,
                })
        return details
    
    def is_well_calibrated(self, threshold: float = 0.05) -> bool:
        """Check if model is well-calibrated
        
        Args:
            threshold: ECE threshold for "well-calibrated" (default 0.05)
            
        Returns:
            True if ECE < threshold
        """
        return self.calculate_ece() < threshold
    
    def needs_recalibration(self, threshold: float = 0.10) -> bool:
        """Check if model needs recalibration
        
        Args:
            threshold: ECE threshold for recalibration (default 0.10)
            
        Returns:
            True if ECE >= threshold
        """
        return self.calculate_ece() >= threshold
    
    def get_calibration_advice(self) -> str:
        """Get human-readable calibration advice"""
        ece = self.calculate_ece()
        
        if ece < 0.05:
            return "Excellent calibration - confidence scores are highly reliable"
        elif ece < 0.10:
            return "Good calibration - confidence scores are generally reliable"
        elif ece < 0.15:
            return "Moderate calibration - consider recalibration if using for critical decisions"
        else:
            return "Poor calibration - recalibration strongly recommended"
    
    def merge(self, other: ECETracker) -> ECETracker:
        """Merge two trackers together
        
        Useful for combining calibration data from multiple sources.
        
        Args:
            other: Another ECETracker to merge with
            
        Returns:
            New ECETracker with combined data
        """
        if self.num_bins != other.num_bins:
            raise ValueError("Cannot merge trackers with different number of bins")
        
        merged = ECETracker(num_bins=self.num_bins)
        
        for i in range(self.num_bins):
            merged.bins[i].predictions = (
                self.bins[i].predictions + other.bins[i].predictions
            )
            merged.bins[i].outcomes = (
                self.bins[i].outcomes + other.bins[i].outcomes
            )
        
        return merged
    
    def clear(self) -> None:
        """Clear all calibration data"""
        for bin in self.bins:
            bin.predictions.clear()
            bin.outcomes.clear()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "num_bins": self.num_bins,
            "created_at": self.created_at.isoformat(),
            "summary": self.get_calibration_summary(),
            "bins": self.get_bin_details(),
            "calibration_advice": self.get_calibration_advice(),
        }


def calculate_ece_from_predictions(
    confidences: List[float],
    outcomes: List[bool],
    num_bins: int = 10
) -> float:
    """Calculate ECE from lists of confidences and outcomes
    
    Convenience function for one-time ECE calculation.
    
    Args:
        confidences: List of confidence scores
        outcomes: List of actual outcomes (correct/incorrect)
        num_bins: Number of calibration bins
        
    Returns:
        ECE score
        
    Examples:
        >>> confidences = [0.9, 0.8, 0.7, 0.9, 0.6]
        >>> outcomes = [True, True, False, True, False]
        >>> ece = calculate_ece_from_predictions(confidences, outcomes)
    """
    if len(confidences) != len(outcomes):
        raise ValueError("confidences and outcomes must have same length")
    
    tracker = ECETracker(num_bins=num_bins)
    
    for conf, outcome in zip(confidences, outcomes):
        tracker.add_prediction(conf, outcome)
    
    return tracker.calculate_ece()


def apply_temperature_scaling(
    confidence: float,
    temperature: float
) -> float:
    """Apply temperature scaling to calibrate confidence
    
    Temperature scaling is a simple calibration method:
    - T > 1: Decreases confidence (makes model more uncertain)
    - T < 1: Increases confidence (makes model more certain)
    - T = 1: No change
    
    Args:
        confidence: Original confidence score
        temperature: Temperature parameter
        
    Returns:
        Calibrated confidence
    """
    # Convert to logits
    if confidence <= 0 or confidence >= 1:
        return confidence
    
    logit = math.log(confidence / (1 - confidence))
    
    # Apply temperature
    calibrated_logit = logit / temperature
    
    # Convert back to probability
    calibrated_conf = 1 / (1 + math.exp(-calibrated_logit))
    
    return calibrated_conf


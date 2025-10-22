"""Tests for calibration tracking"""

import pytest
import math

from vif.calibration import (
    ECETracker,
    CalibrationBin,
    calculate_ece_from_predictions,
    apply_temperature_scaling,
)


def test_calibration_bin():
    """Test CalibrationBin basic functionality"""
    bin = CalibrationBin(confidence_range=(0.8, 0.9))
    
    # Initially empty
    assert bin.count == 0
    assert bin.avg_confidence == 0.0
    assert bin.accuracy == 0.0
    
    # Add predictions
    bin.predictions = [0.85, 0.87, 0.83]
    bin.outcomes = [True, True, False]
    
    assert bin.count == 3
    assert abs(bin.avg_confidence - 0.85) < 0.01
    assert abs(bin.accuracy - 0.667) < 0.01
    assert bin.calibration_gap > 0  # Confidence higher than accuracy


def test_ece_tracker_initialization():
    """Test ECETracker initialization"""
    tracker = ECETracker(num_bins=10)
    
    assert len(tracker.bins) == 10
    assert tracker.bins[0].confidence_range == (0.0, 0.1)
    assert tracker.bins[9].confidence_range == (0.9, 1.0)


def test_add_prediction():
    """Test adding predictions to tracker"""
    tracker = ECETracker(num_bins=10)
    
    # Add prediction in 0.8-0.9 bin
    tracker.add_prediction(confidence=0.85, correct=True)
    
    bin_8 = tracker.bins[8]
    assert bin_8.count == 1
    assert bin_8.predictions[0] == 0.85
    assert bin_8.outcomes[0] is True


def test_perfect_calibration():
    """Test ECE for perfectly calibrated predictions"""
    tracker = ECETracker(num_bins=10)
    
    # Add perfectly calibrated predictions
    # 90% confidence, 90% correct
    for i in range(10):
        tracker.add_prediction(0.9, i < 9)  # 9 correct, 1 incorrect
    
    ece = tracker.calculate_ece()
    assert ece < 0.05  # Should be very low


def test_overconfident_predictions():
    """Test ECE for overconfident predictions"""
    tracker = ECETracker(num_bins=10)
    
    # Model says 90% confident but only 50% correct
    for i in range(10):
        tracker.add_prediction(0.9, i < 5)  # Only 5 correct
    
    ece = tracker.calculate_ece()
    assert ece > 0.30  # Should be high (overconfident)


def test_underconfident_predictions():
    """Test ECE for underconfident predictions"""
    tracker = ECETracker(num_bins=10)
    
    # Model says 50% confident but 90% correct
    for i in range(10):
        tracker.add_prediction(0.5, i < 9)  # 9 correct
    
    ece = tracker.calculate_ece()
    assert ece > 0.30  # Should be high (underconfident)


def test_bin_index_calculation():
    """Test correct bin index calculation"""
    tracker = ECETracker(num_bins=10)
    
    assert tracker._get_bin_index(0.05) == 0  # Bin 0: [0.0, 0.1)
    assert tracker._get_bin_index(0.25) == 2  # Bin 2: [0.2, 0.3)
    assert tracker._get_bin_index(0.85) == 8  # Bin 8: [0.8, 0.9)
    assert tracker._get_bin_index(1.0) == 9  # Edge case: bin 9


def test_edge_case_confidence_0():
    """Test confidence of 0.0"""
    tracker = ECETracker(num_bins=10)
    tracker.add_prediction(0.0, False)
    
    assert tracker.bins[0].count == 1


def test_edge_case_confidence_1():
    """Test confidence of 1.0"""
    tracker = ECETracker(num_bins=10)
    tracker.add_prediction(1.0, True)
    
    assert tracker.bins[9].count == 1  # Should go to last bin


def test_invalid_confidence_validation():
    """Test validation of invalid confidence scores"""
    tracker = ECETracker(num_bins=10)
    
    # Should raise error for invalid confidence
    with pytest.raises(ValueError):
        tracker.add_prediction(1.5, True, validate=True)
    
    with pytest.raises(ValueError):
        tracker.add_prediction(-0.1, True, validate=True)
    
    # Should not raise if validation disabled
    tracker.add_prediction(1.5, True, validate=False)


def test_empty_tracker_ece():
    """Test ECE calculation on empty tracker"""
    tracker = ECETracker(num_bins=10)
    
    ece = tracker.calculate_ece()
    assert ece == 0.0  # Empty tracker has ECE of 0


def test_max_calibration_error():
    """Test Maximum Calibration Error (MCE)"""
    tracker = ECETracker(num_bins=10)
    
    # Add predictions with varying gaps
    tracker.add_prediction(0.5, False)  # Gap: 0.5
    tracker.add_prediction(0.9, False)  # Gap: 0.9 (largest)
    tracker.add_prediction(0.7, True)   # Gap: 0.3
    
    mce = tracker.calculate_max_calibration_error()
    assert abs(mce - 0.9) < 0.01  # Should be ~0.9


def test_rmsce():
    """Test Root Mean Squared Calibration Error"""
    tracker = ECETracker(num_bins=10)
    
    # Add some predictions
    for i in range(5):
        tracker.add_prediction(0.8, True)
    for i in range(5):
        tracker.add_prediction(0.8, False)
    
    rmsce = tracker.calculate_rmsce()
    assert rmsce > 0  # Should have some error


def test_calibration_summary():
    """Test calibration summary generation"""
    tracker = ECETracker(num_bins=10)
    
    for i in range(20):
        tracker.add_prediction(0.8, i < 16)  # 16 correct, 4 incorrect
    
    summary = tracker.get_calibration_summary()
    
    assert "ece" in summary
    assert "mce" in summary
    assert "rmsce" in summary
    assert summary["total_predictions"] == 20
    assert summary["non_empty_bins"] >= 1


def test_bin_details():
    """Test getting bin details"""
    tracker = ECETracker(num_bins=10)
    
    tracker.add_prediction(0.85, True)
    tracker.add_prediction(0.87, False)
    
    details = tracker.get_bin_details()
    
    assert len(details) >= 1
    assert "bin" in details[0]
    assert "range" in details[0]
    assert "count" in details[0]
    assert "avg_confidence" in details[0]
    assert "accuracy" in details[0]


def test_is_well_calibrated():
    """Test well-calibrated check"""
    tracker = ECETracker(num_bins=10)
    
    # Add well-calibrated predictions
    for i in range(10):
        tracker.add_prediction(0.8, i < 8)  # 8 correct = 80%
    
    assert tracker.is_well_calibrated(threshold=0.05)


def test_needs_recalibration():
    """Test recalibration check"""
    tracker = ECETracker(num_bins=10)
    
    # Add poorly calibrated predictions
    for i in range(10):
        tracker.add_prediction(0.9, i < 5)  # Only 50% correct
    
    assert tracker.needs_recalibration(threshold=0.10)


def test_calibration_advice():
    """Test calibration advice generation"""
    tracker = ECETracker(num_bins=10)
    
    # Excellent calibration
    for i in range(10):
        tracker.add_prediction(0.8, i < 8)
    
    advice = tracker.get_calibration_advice()
    assert "excellent" in advice.lower() or "good" in advice.lower()


def test_merge_trackers():
    """Test merging two trackers"""
    tracker1 = ECETracker(num_bins=10)
    tracker2 = ECETracker(num_bins=10)
    
    for i in range(5):
        tracker1.add_prediction(0.8, True)
    
    for i in range(5):
        tracker2.add_prediction(0.8, False)
    
    merged = tracker1.merge(tracker2)
    
    assert sum(bin.count for bin in merged.bins) == 10


def test_merge_different_bins_error():
    """Test that merging trackers with different bins raises error"""
    tracker1 = ECETracker(num_bins=10)
    tracker2 = ECETracker(num_bins=5)
    
    with pytest.raises(ValueError):
        tracker1.merge(tracker2)


def test_clear():
    """Test clearing tracker data"""
    tracker = ECETracker(num_bins=10)
    
    tracker.add_prediction(0.8, True)
    tracker.add_prediction(0.9, False)
    
    assert sum(bin.count for bin in tracker.bins) > 0
    
    tracker.clear()
    
    assert sum(bin.count for bin in tracker.bins) == 0


def test_to_dict():
    """Test serialization to dictionary"""
    tracker = ECETracker(num_bins=10)
    
    tracker.add_prediction(0.8, True)
    
    data = tracker.to_dict()
    
    assert "num_bins" in data
    assert "summary" in data
    assert "bins" in data
    assert "calibration_advice" in data


def test_calculate_ece_from_predictions():
    """Test convenience function for ECE calculation"""
    confidences = [0.9, 0.8, 0.7, 0.9, 0.6]
    outcomes = [True, True, False, True, False]
    
    ece = calculate_ece_from_predictions(confidences, outcomes)
    
    assert 0.0 <= ece <= 1.0


def test_ece_from_predictions_length_mismatch():
    """Test error on length mismatch"""
    with pytest.raises(ValueError):
        calculate_ece_from_predictions([0.8, 0.9], [True])


def test_temperature_scaling_increase():
    """Test temperature scaling increases uncertainty"""
    original = 0.9
    
    # Temperature > 1 should decrease confidence
    calibrated = apply_temperature_scaling(original, temperature=2.0)
    assert calibrated < original


def test_temperature_scaling_decrease():
    """Test temperature scaling decreases uncertainty"""
    original = 0.7
    
    # Temperature < 1 should increase confidence
    calibrated = apply_temperature_scaling(original, temperature=0.5)
    assert calibrated > original


def test_temperature_scaling_identity():
    """Test temperature=1 doesn't change confidence"""
    original = 0.8
    
    calibrated = apply_temperature_scaling(original, temperature=1.0)
    assert abs(calibrated - original) < 0.01


def test_temperature_scaling_edge_cases():
    """Test temperature scaling with edge case confidences"""
    # Confidence = 0 should stay 0
    assert apply_temperature_scaling(0.0, 1.5) == 0.0
    
    # Confidence = 1 should stay 1
    assert apply_temperature_scaling(1.0, 1.5) == 1.0


def test_realistic_calibration_scenario():
    """Test realistic calibration tracking scenario"""
    tracker = ECETracker(num_bins=10)
    
    # Simulate 100 predictions with slight overconfidence
    import random
    random.seed(42)
    
    for _ in range(100):
        # Model is slightly overconfident
        confidence = random.uniform(0.7, 0.95)
        # Actual accuracy is lower
        correct = random.random() < (confidence - 0.10)
        
        tracker.add_prediction(confidence, correct)
    
    ece = tracker.calculate_ece()
    
    # Should have measurable ECE (but calibration better than expected)
    assert 0.01 < ece < 0.20
    
    # Check calibration status
    summary = tracker.get_calibration_summary()
    assert summary["total_predictions"] == 100


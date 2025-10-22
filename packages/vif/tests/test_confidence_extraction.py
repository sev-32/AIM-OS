"""Tests for confidence extraction"""

import pytest
import math

from vif.confidence_extraction import (
    extract_confidence,
    extract_from_logprobs,
    combine_confidence_signals,
    ConfidenceExtraction,
)


def test_explicit_percentage():
    """Test extraction of explicit percentage confidence"""
    result = extract_confidence("I am 95% confident that this is correct.")
    assert result.confidence_score == 0.95
    assert result.extraction_method == "explicit"
    assert result.explicit_statement is not None


def test_explicit_out_of_ten():
    """Test extraction of 'X out of 10' format"""
    result = extract_confidence("My confidence is 8 out of 10.")
    assert result.confidence_score == 0.80
    assert result.extraction_method == "explicit"


def test_word_based_confidence():
    """Test word-based confidence expressions"""
    # Very confident
    result = extract_confidence("I am very confident about this.")
    assert result.confidence_score == 0.90
    assert result.extraction_method == "explicit_word"
    
    # Moderately confident
    result = extract_confidence("I am moderately confident.")
    assert result.confidence_score == 0.70
    
    # Slightly confident
    result = extract_confidence("I am slightly confident.")
    assert result.confidence_score == 0.50


def test_hedging_language():
    """Test hedging language detection"""
    # Single hedge
    result = extract_confidence("Maybe this could work.")
    assert result.hedging_detected is True
    assert 0.65 <= result.confidence_score <= 0.75
    assert result.extraction_method == "hedging_analysis"
    
    # Multiple hedges
    result = extract_confidence("Maybe it might possibly work.")
    assert result.hedging_detected is True
    assert result.confidence_score <= 0.60


def test_uncertainty_markers():
    """Test strong uncertainty markers"""
    result = extract_confidence("I don't know if this is correct.")
    assert result.confidence_score == 0.40
    assert result.extraction_method == "uncertainty_markers"
    assert len(result.uncertainty_markers) > 0


def test_confidence_markers():
    """Test high confidence markers"""
    result = extract_confidence("This is definitely the correct answer.")
    assert result.confidence_score == 0.90
    assert result.extraction_method == "confidence_markers"


def test_default_confidence():
    """Test default confidence for neutral text"""
    result = extract_confidence("The sky is blue.")
    assert result.confidence_score == 0.70
    assert result.extraction_method == "default"


def test_logprobs_peaked_distribution():
    """Test confidence from peaked log probability distribution"""
    # Peaked distribution (confident)
    logprobs = [
        ("the", -0.1),  # Very high probability
        ("a", -2.5),
        ("this", -3.0),
        ("that", -3.5),
        ("it", -4.0),
    ]
    
    confidence = extract_from_logprobs(logprobs)
    assert confidence >= 0.79  # Should be high confidence (peaked distribution)


def test_logprobs_flat_distribution():
    """Test confidence from flat log probability distribution"""
    # Flat distribution (uncertain)
    logprobs = [
        ("the", -1.5),
        ("a", -1.6),
        ("this", -1.7),
        ("that", -1.8),
        ("it", -1.9),
    ]
    
    confidence = extract_from_logprobs(logprobs)
    assert confidence <= 0.70  # Should be lower confidence


def test_logprobs_empty():
    """Test handling of empty logprobs"""
    confidence = extract_from_logprobs([])
    assert confidence == 0.70  # Default


def test_combine_signals_text_only():
    """Test combining confidence with text only"""
    result = combine_confidence_signals(
        text_confidence=0.85,
        logprob_confidence=None
    )
    assert result == 0.85


def test_combine_signals_both():
    """Test combining both text and logprob confidence"""
    result = combine_confidence_signals(
        text_confidence=0.80,
        logprob_confidence=0.90,
        weights=(0.7, 0.3)
    )
    
    expected = (0.7 * 0.80) + (0.3 * 0.90)
    assert abs(result - expected) < 0.01


def test_clamping_to_valid_range():
    """Test that confidence scores are clamped to [0.0, 1.0]"""
    # Should handle values outside range gracefully
    result = combine_confidence_signals(1.5, 1.5)
    assert 0.0 <= result <= 1.0


def test_case_insensitivity():
    """Test that extraction is case-insensitive"""
    result1 = extract_confidence("I AM 95% CONFIDENT")
    result2 = extract_confidence("i am 95% confident")
    
    assert result1.confidence_score == result2.confidence_score


def test_multiple_patterns_first_wins():
    """Test that first matching pattern is used"""
    # Has both explicit (95%) and hedging (maybe)
    result = extract_confidence("I am 95% confident, maybe.")
    
    # Explicit should win (checked first)
    assert result.confidence_score == 0.95
    assert result.extraction_method == "explicit"


def test_extraction_result_metadata():
    """Test that extraction result includes useful metadata"""
    result = extract_confidence("Maybe this could work.")
    
    assert hasattr(result, 'confidence_score')
    assert hasattr(result, 'extraction_method')
    assert hasattr(result, 'hedging_detected')
    assert hasattr(result, 'uncertainty_markers')
    assert isinstance(result.uncertainty_markers, list)


def test_edge_case_percentage_100():
    """Test 100% confidence"""
    result = extract_confidence("I am 100% certain.")
    assert result.confidence_score == 1.0


def test_edge_case_percentage_0():
    """Test 0% confidence"""
    result = extract_confidence("I am 0% confident.")
    assert result.confidence_score == 0.0


def test_real_world_examples():
    """Test with realistic LLM outputs"""
    
    # High confidence response
    text1 = "Based on the data, I am highly confident (95%) that X is true."
    result1 = extract_confidence(text1)
    assert result1.confidence_score >= 0.90
    
    # Uncertain response
    text2 = "I'm not entirely sure, but it might be X. Perhaps Y could also be possible."
    result2 = extract_confidence(text2)
    assert result2.confidence_score <= 0.70
    
    # Neutral response
    text3 = "The capital of France is Paris."
    result3 = extract_confidence(text3)
    assert result3.confidence_score == 0.70


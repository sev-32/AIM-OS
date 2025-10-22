"""Confidence extraction from LLM outputs

Extracts confidence scores from various LLM output formats:
- Explicit statements ("I am 85% confident...")
- Hedging language analysis
- Uncertainty markers
- Output distribution entropy
"""

from __future__ import annotations

import re
from typing import Optional, Tuple, List
from dataclasses import dataclass
import math


@dataclass
class ConfidenceExtraction:
    """Result of confidence extraction"""
    confidence_score: float  # 0.0-1.0
    extraction_method: str  # How confidence was determined
    explicit_statement: Optional[str] = None  # If explicitly stated
    hedging_detected: bool = False
    uncertainty_markers: List[str] = None
    
    def __post_init__(self):
        if self.uncertainty_markers is None:
            self.uncertainty_markers = []


# Explicit confidence patterns
EXPLICIT_PATTERNS = [
    # "I am X% confident"
    r"(?:i am|i'm|confidence|confident)\s+(?:about\s+)?(\d+)%",
    r"(\d+)%\s+(?:confidence|confident|sure|certain)",
    
    # "X out of 10"
    r"(\d+)\s+(?:out of|/)\s+10",
    
    # "very confident" → map to score
    r"(very|extremely|highly)\s+(?:confident|certain|sure)",
    r"(somewhat|moderately|fairly)\s+(?:confident|certain|sure)",
    r"(not very|slightly|barely)\s+(?:confident|certain|sure)",
]

# Hedging language (indicates uncertainty)
HEDGING_PHRASES = [
    "might", "maybe", "perhaps", "possibly", "probably",
    "could be", "may be", "seems like", "appears to",
    "i think", "i believe", "i guess", "i suppose",
    "likely", "unlikely", "uncertain", "unclear",
]

# Strong uncertainty markers
UNCERTAINTY_MARKERS = [
    "i don't know", "i'm not sure", "uncertain",
    "unclear", "ambiguous", "difficult to say",
    "hard to tell", "cannot determine", "unable to",
]

# High confidence markers
CONFIDENCE_MARKERS = [
    "definitely", "certainly", "clearly", "obviously",
    "without doubt", "undoubtedly", "absolutely",
    "confirmed", "verified", "proven",
]


def extract_confidence(text: str) -> ConfidenceExtraction:
    """Extract confidence score from text
    
    Tries multiple methods in order:
    1. Explicit confidence statements
    2. Hedging language analysis
    3. Uncertainty/confidence marker analysis
    4. Default (0.70 for neutral text)
    
    Args:
        text: LLM output text
        
    Returns:
        ConfidenceExtraction with score and metadata
        
    Examples:
        >>> extract_confidence("I am 95% confident that...")
        ConfidenceExtraction(confidence_score=0.95, method='explicit')
        
        >>> extract_confidence("Maybe it could be X")
        ConfidenceExtraction(confidence_score=0.50, method='hedging')
    """
    text_lower = text.lower()
    
    # Method 1: Explicit confidence
    explicit_result = _extract_explicit_confidence(text_lower)
    if explicit_result:
        return explicit_result
    
    # Method 2: Hedging analysis
    hedging_result = _analyze_hedging(text_lower)
    if hedging_result:
        return hedging_result
    
    # Method 3: Marker analysis
    marker_result = _analyze_markers(text_lower)
    if marker_result:
        return marker_result
    
    # Default: Neutral confidence
    return ConfidenceExtraction(
        confidence_score=0.70,
        extraction_method="default",
    )


def _extract_explicit_confidence(text: str) -> Optional[ConfidenceExtraction]:
    """Extract explicitly stated confidence scores"""
    
    for pattern in EXPLICIT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1)
            
            # Handle percentage values
            if value.isdigit():
                score = int(value)
                if score <= 10:  # "8 out of 10" format
                    confidence = score / 10.0
                else:  # "85%" format
                    confidence = score / 100.0
                
                # Clamp to valid range
                confidence = max(0.0, min(1.0, confidence))
                
                return ConfidenceExtraction(
                    confidence_score=confidence,
                    extraction_method="explicit",
                    explicit_statement=match.group(0),
                )
            
            # Handle word-based confidence ("very confident")
            if value in ["very", "extremely", "highly"]:
                return ConfidenceExtraction(
                    confidence_score=0.90,
                    extraction_method="explicit_word",
                    explicit_statement=match.group(0),
                )
            elif value in ["somewhat", "moderately", "fairly"]:
                return ConfidenceExtraction(
                    confidence_score=0.70,
                    extraction_method="explicit_word",
                    explicit_statement=match.group(0),
                )
            elif value in ["not very", "slightly", "barely"]:
                return ConfidenceExtraction(
                    confidence_score=0.50,
                    extraction_method="explicit_word",
                    explicit_statement=match.group(0),
                )
    
    return None


def _analyze_hedging(text: str) -> Optional[ConfidenceExtraction]:
    """Analyze hedging language to infer confidence"""
    
    # Count hedging phrases
    hedges_found = []
    for phrase in HEDGING_PHRASES:
        if phrase in text:
            hedges_found.append(phrase)
    
    if not hedges_found:
        return None
    
    # More hedging = lower confidence
    # 1 hedge: 0.70, 2 hedges: 0.60, 3+: 0.50
    hedge_count = len(hedges_found)
    
    if hedge_count == 1:
        confidence = 0.70
    elif hedge_count == 2:
        confidence = 0.60
    else:
        confidence = 0.50
    
    return ConfidenceExtraction(
        confidence_score=confidence,
        extraction_method="hedging_analysis",
        hedging_detected=True,
        uncertainty_markers=hedges_found,
    )


def _analyze_markers(text: str) -> Optional[ConfidenceExtraction]:
    """Analyze uncertainty/confidence markers"""
    
    # Check for strong uncertainty
    uncertainty_found = []
    for marker in UNCERTAINTY_MARKERS:
        if marker in text:
            uncertainty_found.append(marker)
    
    if uncertainty_found:
        return ConfidenceExtraction(
            confidence_score=0.40,  # Low confidence
            extraction_method="uncertainty_markers",
            uncertainty_markers=uncertainty_found,
        )
    
    # Check for high confidence
    confidence_found = []
    for marker in CONFIDENCE_MARKERS:
        if marker in text:
            confidence_found.append(marker)
    
    if confidence_found:
        return ConfidenceExtraction(
            confidence_score=0.90,  # High confidence
            extraction_method="confidence_markers",
            uncertainty_markers=confidence_found,
        )
    
    return None


def extract_from_logprobs(
    logprobs: List[Tuple[str, float]],
    top_k: int = 5
) -> float:
    """Extract confidence from token log probabilities
    
    Uses entropy of top-k distribution as confidence proxy.
    Lower entropy = more confident (peaked distribution)
    Higher entropy = less confident (flat distribution)
    
    Args:
        logprobs: List of (token, log_prob) tuples
        top_k: Number of top tokens to consider
        
    Returns:
        Confidence score (0.0-1.0)
    """
    if not logprobs:
        return 0.70  # Default
    
    # Take top-k
    top_probs = logprobs[:top_k]
    
    # Convert log probs to probabilities
    probs = [math.exp(log_p) for _, log_p in top_probs]
    
    # Normalize
    total = sum(probs)
    if total == 0:
        return 0.70
    probs = [p / total for p in probs]
    
    # Calculate entropy
    entropy = -sum(p * math.log(p) for p in probs if p > 0)
    
    # Max entropy for uniform distribution over top_k
    max_entropy = math.log(top_k)
    
    # Normalize entropy to 0-1
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    
    # Convert to confidence (inverse of entropy)
    # Low entropy → high confidence
    # High entropy → low confidence
    confidence = 1.0 - normalized_entropy
    
    # Scale to reasonable range (0.5-1.0)
    confidence = 0.5 + (confidence * 0.5)
    
    return max(0.0, min(1.0, confidence))


def combine_confidence_signals(
    text_confidence: float,
    logprob_confidence: Optional[float] = None,
    weights: Tuple[float, float] = (0.7, 0.3)
) -> float:
    """Combine multiple confidence signals
    
    Args:
        text_confidence: From text analysis
        logprob_confidence: From log probabilities (if available)
        weights: (text_weight, logprob_weight)
        
    Returns:
        Combined confidence score
    """
    if logprob_confidence is None:
        return text_confidence
    
    text_weight, logprob_weight = weights
    combined = (text_weight * text_confidence) + (logprob_weight * logprob_confidence)
    
    return max(0.0, min(1.0, combined))

